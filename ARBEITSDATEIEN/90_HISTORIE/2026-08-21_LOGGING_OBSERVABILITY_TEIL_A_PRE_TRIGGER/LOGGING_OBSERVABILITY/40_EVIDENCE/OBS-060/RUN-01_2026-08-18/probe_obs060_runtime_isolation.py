"""OBS-060 - The runtime isolation proof R-1 .. R-7, in the binding form.

``WP-OBS-060`` prescribes a PROTOCOL COMPARISON, not a list of single
assertions:

    R-1  reference run WITHOUT observability: one complete dictation cycle over
         the REAL STTController with a scripted session. Recorded are ALL
         observable effects: frames sent, CommandResult, FeedbackDecision
         sequence, snapshot sequence, FinalProcessingResult.
    R-2  the same run WITH working observability          -> protocol IDENTICAL
    R-3  ... with an ingress that throws on EVERY submit  -> identical
    R-4  ... with a store that throws on EVERY write_batch-> identical
    R-5  ... with a full queue from the start             -> identical
    R-6  ... with a worker that never starts              -> identical
    R-7  ... with an on_observation that throws on every call
             -> identical AND the cursor file holds the same end state as R-1

    Condition: REAL STTController, REAL FeedbackEngine, REAL
    DualSessionCoordinator, REAL EventProtocolProcessor. Only the WebSocket
    and the output devices (LED, sound, injection) are doubles.

Why a protocol comparison and not single assertions: it also catches effects
nobody thought of when writing the test, and it notices a regression if an
observation call later slips into a place where it changes the flow.

Run:  python <this file>
Exit: 0 when every protocol is identical to R-1, 1 otherwise.
"""

from __future__ import annotations

import asyncio
import json
import os
import queue
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "core" / "observability").is_dir():
        PROJECT_ROOT = parent
        sys.path.insert(0, str(parent))
        break

from core.config import AppConfig, EventStreamConfig, ServerConfig
from core.controller import STTController
from core.event_cursor_store import EventCursorStore
from core.event_models import EventConnectionState
from core.event_protocol import EventProtocolProcessor
from core.event_stream import EventStreamTransport
from core.history import TranscriptHistoryManager
from core.observability.ingress import NULL_INGRESS, ObservabilityIngress
from core.observability.adapters.server_live import ServerLiveAdapter
from core.observability.storage.sqlite import SQLiteLogStore
from core.observability.worker import LoggingWorker
from core.session_coordinator import DualSessionCoordinator, SessionContext

from tests.test_controller import FakeAudioCapture, FakeInjectionQueue, FakeSTTSession
from tests.test_obs040_server_live_adapter import (
    access,
    event_frame,
    hello_frame,
    replay_completed_frame,
    subscribed_frame,
)

FAILURES = []


def check(name, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + name + ((" - " + detail) if detail else ""))
    if not ok:
        FAILURES.append(name)
    return ok


# ---------------------------------------------------------------------------
# The doubles that the work package explicitly allows: WebSocket + outputs
# ---------------------------------------------------------------------------

class _ExplodingIngress(ObservabilityIngress):
    """R-3: every submit throws. The producer call sites must survive it."""

    def __init__(self):
        super().__init__(instance_id="exploding", queue_size=64)

    def submit(self, record):
        raise RuntimeError("ingress.submit exploded")

    def event(self, type, **kwargs):  # noqa: A002
        raise RuntimeError("ingress.event exploded")

    def observe_server_result(self, context, result):
        raise RuntimeError("ingress.observe_server_result exploded")

    def drain(self, max_items, timeout):
        raise RuntimeError("ingress.drain exploded")

    def register_aggregate_source(self, type, source, *, component=None):  # noqa: A002
        raise RuntimeError("ingress.register_aggregate_source exploded")

    def collect_aggregates(self):
        raise RuntimeError("ingress.collect_aggregates exploded")

    def apply_config(self, config):
        raise RuntimeError("ingress.apply_config exploded")


class _ExplodingStore:
    """R-4: every write_batch throws."""

    def open(self):
        from core.observability.storage.sqlite import OpenResult
        return OpenResult(True, False, "")

    def write_batch(self, records):
        raise sqlite3.OperationalError("store.write_batch exploded")

    def probe_write(self):
        return False

    def run_retention(self, **kwargs):
        raise sqlite3.OperationalError("store.run_retention exploded")

    def measure_db_bytes(self):
        return None

    def clear(self):
        return 0

    def close(self):
        return None


class _AlwaysFullIngress(ObservabilityIngress):
    """R-5: the queue is full from the very first record."""

    def __init__(self):
        super().__init__(instance_id="full", queue_size=1)
        from core.observability.models import CanonicalLogRecord
        filler = CanonicalLogRecord(
            record_id="filler", received_at="2026-08-18T00:00:00.000Z",
            producer_kind="client", producer_id="voice-stt-client",
            instance_id="full", scope="instance", channel="system", level="ERROR",
            type="filler",
        )
        self._queue.put_nowait(filler)


# ---------------------------------------------------------------------------
# The protocol: every observable effect of one dictation cycle
# ---------------------------------------------------------------------------

def _jsonable(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "value"):
        return _jsonable(value.value)
    if hasattr(value, "name"):
        return str(value.name)
    return str(value)


class Protocol:
    """Everything a dictation cycle does that anyone outside it can see."""

    def __init__(self):
        self.frames = []
        self.command_results = []
        self.feedback = []
        self.snapshots = []
        self.finals = []
        self.injections = []
        self.texts = []
        self.transports = []
        self.event_stream_accepted = []
        self.resume_cursor = None
        self.cursor_file = None

    def as_dict(self):
        return {
            "frames": _jsonable(self.frames),
            "command_results": _jsonable(self.command_results),
            "feedback": _jsonable(self.feedback),
            "snapshots": _jsonable(self.snapshots),
            "finals": _jsonable(self.finals),
            "injections": _jsonable(self.injections),
            "texts": _jsonable(self.texts),
            "transports": _jsonable(self.transports),
            "event_stream_accepted": _jsonable(self.event_stream_accepted),
            "resume_cursor": _jsonable(self.resume_cursor),
            "cursor_file": _jsonable(self.cursor_file),
        }

    def digest(self):
        return json.dumps(self.as_dict(), sort_keys=True, indent=None)


# ---------------------------------------------------------------------------
# One complete dictation cycle over the REAL controller
# ---------------------------------------------------------------------------

async def run_cycle(tmp, *, ingress, observation_hook=None, store=None,
                    start_worker=True, label=""):
    """Drive one dictation cycle and return its Protocol.

    ``ingress``  the observability ingress the controller and the coordinator
                 get (``NULL_INGRESS`` for the reference run R-1).
    ``store``    when given, a real LoggingWorker is wired to it.
    """
    directory = tmp / ("run_" + label)
    directory.mkdir(parents=True, exist_ok=True)

    worker = None
    if store is not None:
        worker = LoggingWorker(ingress, store, batch_size=8, flush_interval_s=0.05)
        if start_worker:
            worker.start()

    config = AppConfig()
    config.history.persistent.db_path = str(directory / "history.db")
    history = TranscriptHistoryManager(
        config.history, db_path=config.history.persistent.db_path
    )
    session = FakeSTTSession()
    # the OBS-040 frame helpers speak about "session-1"; aligning the
    # WebSocket double with them keeps the REAL protocol processor and the
    # REAL coordinator on their normal, validating path.
    session.state.session_id = "session-1"
    audio = FakeAudioCapture()
    injection = FakeInjectionQueue()

    # REAL coordinator, REAL cursor store, REAL protocol processor
    cursor_path = directory / "cursor.json"
    cursor_store = EventCursorStore(cursor_path)
    coordinator = DualSessionCoordinator(
        ServerConfig(),
        EventStreamConfig(cursor_persistence_enabled=True),
        cursor_store=cursor_store,
        observability=ingress,
    )

    controller = STTController(
        config,
        session=session,
        audio=audio,
        history_manager=history,
        injection_queue=injection,
        session_coordinator=coordinator,
        observability=ingress,
    )

    protocol = Protocol()
    controller.on_feedback_decision = lambda decision: protocol.feedback.append(
        (getattr(decision.source, "value", decision.source),
         getattr(decision.impulse, "value", decision.impulse))
    )
    controller.on_snapshot_change = lambda snapshot: protocol.snapshots.append(
        (getattr(snapshot.availability_state, "value", snapshot.availability_state),
         getattr(snapshot.dictation_state, "value", snapshot.dictation_state),
         snapshot.reason_code,
         snapshot.revision,
         getattr(snapshot.dictation_window_phase, "value",
                 snapshot.dictation_window_phase),
         getattr(snapshot.server_status, "value", snapshot.server_status))
    )
    controller.on_text = lambda segment_id, text, is_final: protocol.texts.append(
        (segment_id, text, is_final)
    )
    controller.on_transport_change = lambda state: protocol.transports.append(
        getattr(state, "name", str(state))
    )

    # the observation hook under test (R-7 replaces it with a thrower)
    if observation_hook is not None:
        coordinator.on_observation = observation_hook

    sender_task = None
    try:
        controller._loop = asyncio.get_running_loop()
        controller.start_queue()
        sender_task = asyncio.create_task(controller._audio_sender())

        # --- 1. start the dictation -------------------------------------
        result = await controller.start_dictation()
        protocol.command_results.append(
            (getattr(result.status, "value", str(result.status)), result.message)
        )

        # --- 2. audio flows to the WebSocket double ----------------------
        # ``set_streaming`` belongs to the WebSocket double, which the work
        # package explicitly allows; it is identical in every run. The packets
        # go in through the REAL hot-path entry point.
        session.set_streaming(True)
        for index in range(5):
            controller._on_audio_packet_from_thread(
                bytes([index]) * 640, 16000, 1, 320)
        for _ in range(40):
            await asyncio.sleep(0.01)
            if len(session.audio_packets) >= 5:
                break
        protocol.frames.append(len(session.audio_packets))
        protocol.frames.append([len(packet[0]) for packet in session.audio_packets])
        protocol.frames.append(
            [controller.chunks_dropped_send_queue, controller.max_send_queue_depth])

        # --- 3. server events through the REAL protocol processor --------
        stream_access = access()
        processor = EventProtocolProcessor(stream_access, cursor_store=cursor_store)
        processor.begin_subscription()
        processor.process_mapping(hello_frame())
        processor.process_mapping(subscribed_frame(0))
        processor.process_mapping(replay_completed_frame(0, 0))

        coordinator._context = SessionContext(
            generation=session.generation,
            session_id=session.state.session_id,
            log_access=stream_access,
            event_state=EventConnectionState.LIVE,
            token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        coordinator._binding = 1

        transport = EventStreamTransport(
            EventStreamConfig(),
            stream_access,
            processor,
            on_event=lambda r: coordinator._handle_event(1, r),
            on_control=lambda r: coordinator._handle_control(1, r),
        )
        for cursor, event_id in ((5, "evt-5"), (6, "evt-6"), (7, "evt-7")):
            outcome = processor.process_mapping(
                event_frame(cursor, event_id, replay=False,
                            sessionId=session.state.session_id))
            await transport._dispatch(outcome)
            protocol.event_stream_accepted.append((cursor, event_id))
        protocol.resume_cursor = processor.resume_cursor

        # --- 4. a final transcript through the REAL controller path ------
        final = controller.process_raw_final_event({
            "type": "final",
            "sessionId": session.state.session_id,
            "segmentId": 7,
            "text": "das ist ein diktierter satz",
            "_clientGeneration": session.generation,
        })
        protocol.finals.append(
            (getattr(final.status, "value", str(final.status)),
             final.entry.text if getattr(final, "entry", None) else None)
        )

        # --- 5. stop the dictation ---------------------------------------
        result = await controller.stop_dictation()
        protocol.command_results.append(
            (getattr(result.status, "value", str(result.status)), result.message)
        )
        protocol.injections = [entry.text for entry in injection.enqueue_calls]
    finally:
        if sender_task is not None:
            sender_task.cancel()
            try:
                await sender_task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
        await controller.shutdown()
        if worker is not None:
            worker.stop(2.0)

    if cursor_path.exists():
        try:
            content = json.loads(cursor_path.read_text(encoding="utf-8"))
            # ``updated_at`` is the wall-clock moment of the write. Two runs
            # can never share it, and it says nothing about the END STATE the
            # work package asks about. Every other field stays in.
            if isinstance(content, dict):
                content.pop("updated_at", None)
            protocol.cursor_file = content
        except Exception:  # noqa: BLE001
            protocol.cursor_file = "<unreadable>"
    return protocol


class _ThrowingObserver:
    calls = 0

    def __call__(self, context, result):
        _ThrowingObserver.calls += 1
        raise RuntimeError("on_observation exploded")


async def main_async():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as directory:
        tmp = Path(directory)

        print("--- R-1  reference run WITHOUT observability ---")
        reference = await run_cycle(tmp, ingress=NULL_INGRESS, label="r1")
        print(reference.digest())
        print("")

        cases = []

        print("--- R-2  with working observability ---")
        db = tmp / "r2" / "observability.sqlite3"
        db.parent.mkdir(parents=True, exist_ok=True)
        ingress2 = ObservabilityIngress(instance_id="r2", queue_size=4096)
        cases.append(("R-2 working observability",
                      await run_cycle(tmp, ingress=ingress2,
                                      store=SQLiteLogStore(db), label="r2"),
                      ingress2, db))

        print("--- R-3  ingress throws on EVERY call ---")
        ingress3 = _ExplodingIngress()
        cases.append(("R-3 throwing ingress",
                      await run_cycle(tmp, ingress=ingress3, label="r3"), None, None))

        print("--- R-4  store throws on EVERY write_batch ---")
        ingress4 = ObservabilityIngress(instance_id="r4", queue_size=4096)
        cases.append(("R-4 throwing store",
                      await run_cycle(tmp, ingress=ingress4,
                                      store=_ExplodingStore(), label="r4"),
                      ingress4, None))

        print("--- R-5  queue full from the start ---")
        ingress5 = _AlwaysFullIngress()
        cases.append(("R-5 full queue",
                      await run_cycle(tmp, ingress=ingress5, label="r5"),
                      ingress5, None))

        print("--- R-6  worker never starts ---")
        db6 = tmp / "r6" / "observability.sqlite3"
        db6.parent.mkdir(parents=True, exist_ok=True)
        ingress6 = ObservabilityIngress(instance_id="r6", queue_size=4096)
        cases.append(("R-6 worker never starts",
                      await run_cycle(tmp, ingress=ingress6,
                                      store=SQLiteLogStore(db6),
                                      start_worker=False, label="r6"),
                      ingress6, None))

        print("--- R-7  on_observation throws on every call ---")
        ingress7 = ObservabilityIngress(instance_id="r7", queue_size=4096)
        protocol7 = await run_cycle(tmp, ingress=ingress7,
                                    observation_hook=_ThrowingObserver(), label="r7")
        cases.append(("R-7 throwing on_observation", protocol7, ingress7, None))

        print("")
        print("=" * 70)
        expected = reference.digest()
        for name, protocol, _ingress, _db in cases:
            same = protocol.digest() == expected
            check(name + ": protocol identical to R-1", same)
            if not same:
                print("       expected: " + expected)
                print("       actual  : " + protocol.digest())

        check("R-7 the throwing observer was really called",
              _ThrowingObserver.calls > 0,
              "calls=" + str(_ThrowingObserver.calls))
        check("R-7 the cursor file holds the same end state as R-1",
              protocol7.cursor_file == reference.cursor_file,
              str(protocol7.cursor_file) + " vs " + str(reference.cursor_file))
        check("R-7 the resume cursor is the same as in R-1",
              protocol7.resume_cursor == reference.resume_cursor,
              str(protocol7.resume_cursor) + " vs " + str(reference.resume_cursor))

        # R-2 additionally has to have OBSERVED something: an isolation proof
        # that observes nothing proves nothing.
        r2_db = cases[0][3]
        rows = 0
        if r2_db and Path(r2_db).exists():
            connection = sqlite3.connect(str(r2_db))
            rows = int(connection.execute("SELECT COUNT(*) FROM logs").fetchone()[0])
            connection.close()
        check("R-2 the working observability actually recorded the cycle",
              rows > 0, "rows=" + str(rows))


def main():
    asyncio.run(main_async())
    print("")
    print("=" * 70)
    if FAILURES:
        print("FAILURES: " + str(len(FAILURES)))
        for name in FAILURES:
            print("  - " + name)
        return 1
    print("ALL PROTOCOLS IDENTICAL - runtime isolation holds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
