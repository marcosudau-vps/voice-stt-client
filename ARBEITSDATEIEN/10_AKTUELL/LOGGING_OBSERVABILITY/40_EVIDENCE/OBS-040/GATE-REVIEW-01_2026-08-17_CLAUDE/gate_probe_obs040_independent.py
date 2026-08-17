"""OBS-040 Gate Review — independent probe (written by the reviewing session).

Deliberately NOT the run's own probe. It drives the REAL
``EventStreamTransport._dispatch`` (the code path that owns confirm/reject),
the REAL ``EventProtocolProcessor``, the REAL ``EventCursorStore`` on a
temporary file, the REAL ``ObservabilityIngress``, the REAL
``SQLiteLogStore`` and the REAL ``LoggingWorker``.
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
import tempfile
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from core.config import EventStreamConfig, ServerConfig
from core.event_cursor_store import EventCursorStore
from core.event_models import EventConnectionState, EventOrigin
from core.event_protocol import EventProtocolProcessor, EventResultKind
from core.event_stream import EventStreamTransport
from core.observability.ingress import ObservabilityIngress
from core.observability.storage.sqlite import SQLiteLogStore
from core.observability.worker import LoggingWorker
from core.session_coordinator import DualSessionCoordinator, SessionContext

from tests.test_obs040_server_live_adapter import (
    access,
    event_frame,
    hello_frame,
    replay_completed_frame,
    subscribed_frame,
)
from core.observability.adapters.server_live import ServerLiveAdapter

FAILURES = []


def check(name, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + name + (" — " + detail if detail else ""))
    if not ok:
        FAILURES.append(name)


def far_future():
    return datetime.now(timezone.utc) + timedelta(hours=1)


def live_processor(tmp: Path, name="cursor.json"):
    store = EventCursorStore(tmp / name)
    proc = EventProtocolProcessor(access(), cursor_store=store)
    proc.begin_subscription()
    proc.process_mapping(hello_frame())
    proc.process_mapping(subscribed_frame(0))
    proc.process_mapping(replay_completed_frame(0, 0))
    return store, proc


def build_coordinator():
    c = DualSessionCoordinator(
        ServerConfig(), EventStreamConfig(cursor_persistence_enabled=False)
    )
    c._context = SessionContext(
        generation=3,
        session_id="session-1",
        log_access=access(),
        event_state=EventConnectionState.LIVE,
        token_expires_at=far_future(),
    )
    c._binding = 1
    return c


def make_transport(proc, coordinator):
    binding = coordinator._binding
    t = EventStreamTransport(
        EventStreamConfig(),
        access(),
        proc,
        on_event=lambda r: coordinator._handle_event(binding, r),
        on_control=lambda r: coordinator._handle_control(binding, r),
    )
    return t


# --------------------------------------------------------------------------
# G1/G2  N-07 through the REAL dispatch: a throwing observer must change
#        neither the confirmation nor the cursor, and must not stop feedback.
# --------------------------------------------------------------------------
async def g1_g2():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        tmp = Path(d)

        async def run_case(observer):
            store, proc = live_processor(tmp, f"c{id(observer)}.json")
            coord = build_coordinator()
            seen = []

            async def feedback(ctx, result):
                seen.append(result.event.event_id)
                return True

            coord.on_event = feedback
            coord.on_observation = observer
            t = make_transport(proc, coord)
            result = proc.process_mapping(event_frame(5, "evt-5", replay=False))
            raised = None
            try:
                await t._dispatch(result)
            except BaseException as exc:  # noqa: BLE001
                raised = exc
            out = (proc.resume_cursor, list(seen), raised)
            await coord.shutdown()
            return out

        class Thrower:
            calls = 0

            def __call__(self, ctx, result):
                Thrower.calls += 1
                raise RuntimeError("observer exploded")

        base = await run_case(None)
        thrown = await run_case(Thrower())

        check(
            "G1 throwing observer: dispatch confirms exactly as without one",
            base[0] == thrown[0] == 5 and base[2] is None and thrown[2] is None,
            f"resume_cursor none/throwing={base[0]}/{thrown[0]}, exc={base[2]}/{thrown[2]}",
        )
        check(
            "G2 feedback branch unaffected by the throwing observer",
            base[1] == thrown[1] == ["evt-5"] and Thrower.calls == 1,
            f"on_event calls={thrown[1]}, observer calls={Thrower.calls}",
        )


# --------------------------------------------------------------------------
# G3  asyncio.CancelledError from the observer must NOT be swallowed.
# --------------------------------------------------------------------------
async def g3():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        store, proc = live_processor(Path(d))
        coord = build_coordinator()
        coord.on_event = lambda ctx, r: True

        def canceller(ctx, result):
            raise asyncio.CancelledError()

        coord.on_observation = canceller
        result = proc.process_mapping(event_frame(5, "evt-5", replay=False))
        got = None
        try:
            await coord._handle_event(1, result)
        except BaseException as exc:  # noqa: BLE001
            got = type(exc).__name__
        check(
            "G3 BaseException (CancelledError) passes through the hook",
            got == "CancelledError",
            f"raised={got}",
        )
        await coord.shutdown()


# --------------------------------------------------------------------------
# G4  The observer sees what the runtime path discards: a binding mismatch,
#     a duplicate and every control frame.  (CONTRACTS §7.2)
# --------------------------------------------------------------------------
async def g4():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        tmp = Path(d)
        store, proc = live_processor(tmp)
        coord = build_coordinator()
        feedback_seen = []

        async def feedback(ctx, result):
            feedback_seen.append(result)
            return True

        coord.on_event = feedback
        observed = []
        coord.on_observation = lambda ctx, r: observed.append(r)
        t = make_transport(proc, coord)

        # (a) an event the runtime rejects because the binding no longer matches
        r1 = proc.process_mapping(event_frame(5, "evt-5", replay=False))
        await coord._handle_event(999, r1)
        # (b) a duplicate -> transport routes it to on_control, never on_event
        proc.confirm_event(r1)
        r2 = proc.process_mapping(event_frame(5, "evt-5", replay=False))
        await t._dispatch(r2)
        # (c) a control frame
        r3 = proc.process_mapping(
            {
                "type": "log.gap",
                "lostFromCursor": 6,
                "lostToCursor": 9,
                "reason": "retention",
                "oldestCursor": 6,
                "latestCursor": 20,
            }
        )
        await t._dispatch(r3)

        check(
            "G4a observer sees the event the runtime discards (binding mismatch)",
            len(observed) >= 1 and observed[0] is r1 and feedback_seen == [],
            f"observed={len(observed)}, feedback={len(feedback_seen)}",
        )
        check(
            "G4b observer sees the duplicate that never reaches on_event",
            r2.duplicate is True and r2 in observed and r2 not in feedback_seen,
            f"duplicate={r2.duplicate}",
        )
        check(
            "G4c observer sees the control frame",
            r3 in observed and r3.kind is not EventResultKind.EVENT,
            f"kind={r3.kind}",
        )
        await coord.shutdown()


# --------------------------------------------------------------------------
# G5  Replay identity: replayed flag preserved, event_id/cursor preserved,
#     dedupe by (producer_id, event_id) in the REAL store.
# --------------------------------------------------------------------------
def g5():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        tmp = Path(d)
        store, proc = live_processor(tmp)
        ing = ObservabilityIngress(instance_id="inst-1", queue_size=512)
        adapter = ServerLiveAdapter(ing)
        ctx = SessionContext(
            generation=3, session_id="session-1", log_access=access(),
            event_state=EventConnectionState.LIVE, token_expires_at=far_future(),
        )
        live = proc.process_mapping(event_frame(5, "evt-5", replay=False))
        adapter(ctx, live)
        proc.confirm_event(live)

        proc2 = EventProtocolProcessor(access(), cursor_store=EventCursorStore(tmp / "c2.json"))
        proc2.begin_subscription()
        proc2.process_mapping(hello_frame())
        proc2.process_mapping(subscribed_frame(0))
        replayed = proc2.process_mapping(event_frame(5, "evt-5", replay=True))
        adapter(ctx, replayed)

        drained = ing.drain(50, 0.1)
        by_type = [r for r in drained if r.event_id == "evt-5"]
        check(
            "G5a replay flag and event identity preserved",
            len(by_type) == 2
            and by_type[0].replayed is False
            and by_type[1].replayed is True
            and all(r.server_cursor == 5 for r in by_type)
            and all(r.generation == 3 for r in by_type)
            and all(r.instance_id == "server-1" for r in by_type),
            f"replayed flags={[r.replayed for r in by_type]}, cursor={[r.server_cursor for r in by_type]}",
        )

        db = tmp / "obs.sqlite3"
        st = SQLiteLogStore(db)
        st.open()
        inserted, deduped = st.write_batch(by_type)
        st.close()
        con = sqlite3.connect(db)
        rows = con.execute(
            "SELECT replayed, event_id, server_cursor FROM logs WHERE event_id='evt-5'"
        ).fetchall()
        con.close()
        check(
            "G5b dedupe keeps exactly the first (live) version",
            inserted == 1 and deduped == 1 and rows == [(0, "evt-5", 5)],
            f"inserted={inserted}, deduplicated={deduped}, rows={rows}",
        )


# --------------------------------------------------------------------------
# G6  No session log token anywhere in the persisted history, although the
#     hello payload demonstrably carries two of them.
# --------------------------------------------------------------------------
def g6():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        tmp = Path(d)
        store, proc = live_processor(tmp)
        ing = ObservabilityIngress(
            instance_id="inst-1", queue_size=512, store_raw_payload=True
        )
        adapter = ServerLiveAdapter(ing)
        ctx = SessionContext(
            generation=3, session_id="session-1", log_access=access(),
            event_state=EventConnectionState.LIVE, token_expires_at=far_future(),
        )
        # replay the whole handshake through a fresh processor so the hello
        # CONTROL result actually reaches the adapter
        proc2 = EventProtocolProcessor(access(), cursor_store=EventCursorStore(tmp / "c3.json"))
        proc2.begin_subscription()
        adapter(ctx, proc2.process_mapping(hello_frame()))
        adapter(ctx, proc2.process_mapping(subscribed_frame(0)))
        adapter(ctx, proc2.process_mapping(replay_completed_frame(0, 0)))
        adapter(ctx, proc2.process_mapping(event_frame(5, "evt-5", replay=False)))

        db = tmp / "obs.sqlite3"
        st = SQLiteLogStore(db)
        st.open()
        worker = LoggingWorker(ing, st, batch_size=50, flush_interval_s=0.05)
        worker.start()
        time.sleep(0.6)
        worker.stop(2.0)
        st.close()
        with sqlite3.connect(db) as con:
            blob = "\n".join(
                json.dumps(row, default=str)
                for row in con.execute("SELECT * FROM logs").fetchall()
            )
        tokens = ["session-secret-token", "another-session-secret"]
        hits = [t for t in tokens if t in blob]
        check(
            "G6 no session log token in the persisted history",
            not hits and "sessionConfig" in blob,
            f"rows_chars={len(blob)}, token_hits={hits}",
        )


# --------------------------------------------------------------------------
# G7  Hot path: 1000 audio packets produce no record; the WORKER produces the
#     aggregate from the registered counter source.
# --------------------------------------------------------------------------
def g7():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        tmp = Path(d)
        ing = ObservabilityIngress(instance_id="inst-1", queue_size=4096, level="DEBUG")
        counters = {"chunks_captured": 0, "packets_sent": 0}

        class Producer:
            def hot(self):
                counters["chunks_captured"] += 1
                counters["packets_sent"] += 1

        p = Producer()
        for _ in range(1000):
            p.hot()
        before = len(ing.drain(10000, 0.0))
        ing.register_aggregate_source(
            "client.audio.stream_stats", lambda: dict(counters), component="audio"
        )

        db = tmp / "obs.sqlite3"
        st = SQLiteLogStore(db)
        st.open()
        worker = LoggingWorker(ing, st, batch_size=50, flush_interval_s=0.05)
        worker.start()
        time.sleep(0.6)
        worker.stop(2.0)
        st.close()
        con = sqlite3.connect(db)
        rows = con.execute(
            "SELECT type, channel, level, details_json FROM logs"
        ).fetchall()
        con.close()
        agg = [r for r in rows if r[0] == "client.audio.stream_stats"]
        check(
            "G7 1000 hot-path increments -> 0 records, worker aggregate -> 1",
            before == 0 and len(agg) == 1 and agg[0][1] == "performance"
            and agg[0][2] == "DEBUG"
            and json.loads(agg[0][3])["chunks_captured"] == 1000,
            f"records_from_hot_path={before}, aggregate_rows={len(agg)}, all_rows={len(rows)}",
        )


# --------------------------------------------------------------------------
# G8  A logging failure never reaches the runtime: an ingress whose every
#     method throws must not break a client hook or the fan-out.
# --------------------------------------------------------------------------
async def g8():
    class HostileIngress:
        def event(self, *a, **k):
            raise RuntimeError("ingress exploded")

        def observe_server_result(self, *a, **k):
            raise RuntimeError("ingress exploded")

        def submit(self, *a, **k):
            raise RuntimeError("ingress exploded")

    from core.observability.adapters.client_events import ClientEventEmitter

    hostile = HostileIngress()
    emitter = ClientEventEmitter(hostile, component="x")
    ok = True
    try:
        emitter.system("client.test", details={"a": 1})
        emitter.audit("client.test2")
    except Exception as exc:  # noqa: BLE001
        ok = False
    check("G8a a throwing ingress never escapes ClientEventEmitter", ok)

    adapter = ServerLiveAdapter(hostile)
    ok2 = True
    try:
        adapter(None, None)
    except Exception:  # noqa: BLE001
        ok2 = False
    check("G8b a throwing ingress never escapes ServerLiveAdapter", ok2)

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        store, proc = live_processor(Path(d))
        coord = build_coordinator()
        coord.on_event = lambda ctx, r: True
        coord.on_observation = adapter
        t = make_transport(proc, coord)
        result = proc.process_mapping(event_frame(5, "evt-5", replay=False))
        raised = None
        try:
            await t._dispatch(result)
        except BaseException as exc:  # noqa: BLE001
            raised = exc
        check(
            "G8c hostile ingress does not disturb the real dispatch",
            raised is None and proc.resume_cursor == 5,
            f"exc={raised}, resume_cursor={proc.resume_cursor}",
        )
        await coord.shutdown()


# --------------------------------------------------------------------------
# G9  No observability thread survives a stop().
# --------------------------------------------------------------------------
def g9():
    names = [t.name for t in threading.enumerate() if "Observability" in t.name]
    check("G9 no observability thread left over", names == [], f"{names}")


async def main():
    await g1_g2()
    await g3()
    await g4()
    g5()
    g6()
    g7()
    await g8()
    g9()
    print()
    if FAILURES:
        print("FAILED CHECKS: " + ", ".join(FAILURES))
        return 1
    print("all independent checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
