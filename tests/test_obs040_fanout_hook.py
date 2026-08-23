"""
OBS-040 — the fan-out hook in ``DualSessionCoordinator`` and the second
observation point in ``EventStreamTransport``.

Frozen sources: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §7.1 (location and form),
§7.2 (why here), §7.3 (error handling is mandatory, ``BaseException`` never
caught), §7.4 (forbidden hook locations), §7.5 / FD-R3 (protocol errors),
§12.1 (``client.eventstream.state_changed``);
``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §1.1 O-01/O-02 (observability only,
fan-out instead of mediation), §8.5 GRENZE 1 and GRENZE 2, §9 (a throwing
observer must not influence cursor commit or connection recycling).

**The key proof of this work package (N-07).** A THROWING observer changes
neither the return value of ``_handle_event`` nor the cursor state — verified
with the REAL ``EventProtocolProcessor`` and the REAL ``EventCursorStore`` on a
temporary file. A double for either would define the very cursor-confirmation
semantics that is under test.
"""

from __future__ import annotations

import asyncio
import inspect
import tempfile
import unittest
from pathlib import Path

from core.config import EventStreamConfig, ServerConfig
from core.event_cursor_store import EventCursorStore
from core.event_models import EventConnectionState
from core.event_protocol import (
    EventProtocolProcessor,
    EventResultKind,
    EventStreamAccess,
)
from core.event_stream import EventStreamTransport
from core.observability.ingress import NULL_INGRESS, ObservabilityIngress
from core.session_coordinator import DualSessionCoordinator, SessionContext
from tests.test_obs040_server_live_adapter import (
    ENDPOINT,
    access,
    build_ingress,
    event_frame,
    hello_frame,
    replay_completed_frame,
    subscribed_frame,
)


def enter_live(processor: EventProtocolProcessor) -> None:
    processor.begin_subscription()
    processor.process_mapping(hello_frame())
    processor.process_mapping(subscribed_frame(0))
    processor.process_mapping(replay_completed_frame(0, 0))


class ThrowingObserver:
    """An observer that violates every rule: it throws on every call."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, context, result) -> None:
        self.calls += 1
        raise RuntimeError("observer exploded")


class TestThrowingObserverChangesNothing(unittest.IsolatedAsyncioTestCase):
    """N-07 — the most important proof of this package."""

    def build(self, tmp: str):
        store = EventCursorStore(Path(tmp) / "cursor.json")
        processor = EventProtocolProcessor(access(), cursor_store=store)
        enter_live(processor)
        coordinator = DualSessionCoordinator(
            ServerConfig(),
            EventStreamConfig(cursor_persistence_enabled=False),
        )
        return store, processor, coordinator

    async def test_throwing_observer_changes_neither_return_value_nor_cursor(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, processor, coordinator = self.build(tmp)
            self.addAsyncCleanup(coordinator.shutdown)
            observer = ThrowingObserver()

            accepted_calls = []

            async def accept(context, result) -> bool:
                accepted_calls.append(result.event.event_id)
                return True

            coordinator.on_event = accept
            # Make the coordinator's own guards pass for this result.
            coordinator._context = SessionContext(
                generation=1,
                session_id="session-1",
                log_access=access(),
                event_state=EventConnectionState.LIVE,
                token_expires_at=_far_future(),
            )
            coordinator._binding = 1
            result = processor.process_mapping(event_frame(5, "evt-5", replay=False))

            # 1. Without an observer.
            without = await coordinator._handle_event(1, result)

            # 2. With a THROWING observer, on a fresh but identical setup.
            store2, processor2, coordinator2 = self.build(tmp + "2" if False else tmp)
            coordinator2.on_event = accept
            coordinator2.on_observation = observer
            coordinator2._context = coordinator._context
            coordinator2._binding = 1
            self.addAsyncCleanup(coordinator2.shutdown)
            result2 = processor2.process_mapping(
                event_frame(5, "evt-5", replay=False)
            )
            with_observer = await coordinator2._handle_event(1, result2)

            self.assertTrue(without)
            self.assertEqual(with_observer, without)
            self.assertEqual(observer.calls, 1)
            # The feedback branch ran in both cases, identically.
            self.assertEqual(accepted_calls, ["evt-5", "evt-5"])

            # The cursor is untouched by the observation: only an explicit
            # confirm_event moves it, and neither run called one.
            self.assertEqual(processor2.resume_cursor, 0)
            self.assertFalse((Path(tmp) / "cursor.json").exists())

            # And confirmation still works afterwards, exactly as it would
            # without any observer.
            processor2.confirm_event(result2)
            self.assertEqual(processor2.resume_cursor, 5)
            self.assertTrue((Path(tmp) / "cursor.json").exists())
            self.assertIs(result2.kind, EventResultKind.EVENT)

    async def test_throwing_observer_does_not_break_control_handling(self):
        coordinator = DualSessionCoordinator(
            ServerConfig(),
            EventStreamConfig(cursor_persistence_enabled=False),
        )
        self.addAsyncCleanup(coordinator.shutdown)
        observer = ThrowingObserver()
        coordinator.on_observation = observer
        processor = EventProtocolProcessor(access())
        processor.begin_subscription()
        processor.process_mapping(hello_frame())
        processor.process_mapping(subscribed_frame(0))
        gap = processor.process_mapping(
            {
                "type": "log.gap",
                "lostFromCursor": 1,
                "lostToCursor": 4,
                "reason": "retention",
                "oldestCursor": 1,
                "latestCursor": 20,
            }
        )
        coordinator._binding = 1

        # Returns None and raises nothing.
        self.assertIsNone(coordinator._handle_control(1, gap))
        self.assertEqual(observer.calls, 1)
        self.assertEqual(
            coordinator.context.unavailable_code, gap.issue.value
        )

    async def test_base_exception_from_the_observer_is_not_swallowed(self):
        """ARCH §7.3/§9: ``BaseException`` is caught NOWHERE.
        ``asyncio.CancelledError`` carries the cancellation of the
        event-stream task and must pass through the observer wrapper."""
        coordinator = DualSessionCoordinator(
            ServerConfig(),
            EventStreamConfig(cursor_persistence_enabled=False),
        )
        self.addAsyncCleanup(coordinator.shutdown)

        def cancelling(context, result) -> None:
            raise asyncio.CancelledError()

        coordinator.on_observation = cancelling
        with self.assertRaises(asyncio.CancelledError):
            coordinator._notify_observer(object())


def _far_future():
    from datetime import datetime, timedelta, timezone

    return datetime.now(timezone.utc) + timedelta(hours=1)


class TestHookLocationAndForm(unittest.TestCase):
    def test_notify_observer_is_the_first_statement_of_both_dispatch_paths(self):
        """CONTRACTS §7.1: *"jeweils als ERSTE Anweisung"*. Checked on the
        source, because the position is the contract: the call has to be before
        the binding, token and session checks, so exactly those events the
        runtime path discards become visible (§7.2, point 3)."""
        for name in ("_handle_event", "_handle_control"):
            with self.subTest(function=name):
                source = inspect.getsource(
                    getattr(DualSessionCoordinator, name)
                )
                body = [
                    line.strip()
                    for line in source.splitlines()
                    if line.strip() and not line.strip().startswith(("#", '"""'))
                ]
                # [0..n] is the signature, which may wrap over several lines.
                first_statement = next(
                    line
                    for line in body
                    if not line.startswith(("def ", "async def ", "self,", "binding:", "result:", ") ->"))
                )
                self.assertEqual(first_statement, "self._notify_observer(result)")

    def test_notify_observer_is_return_value_free(self):
        """O-01: no return value of an observer may steer a business path."""
        signature = inspect.signature(DualSessionCoordinator._notify_observer)
        # ``from __future__ import annotations`` keeps annotations as strings.
        self.assertIn(signature.return_annotation, (None, "None", type(None)))
        source = inspect.getsource(DualSessionCoordinator._notify_observer)
        self.assertNotIn("return observer", source)

    def test_forbidden_hook_locations_carry_no_observation(self):
        """CONTRACTS §7.4 lists five explicitly forbidden hook locations. None
        of them may contain an observation call."""
        import core.event_protocol as event_protocol
        import core.feedback_reducer as feedback_reducer
        import ui.application as ui_application
        from core.controller import STTController

        forbidden = (
            (EventStreamTransport, "_dispatch"),
            (EventStreamTransport, "_call"),
            (event_protocol.EventProtocolProcessor, "process_mapping"),
            (feedback_reducer.FeedbackEngine, "handle_event_stream"),
            # ui/application.py::_on_feedback_decision -- forbidden because it
            # runs AFTER two filters; the P+S record of §12.5 is produced by
            # _log_feedback_decision, which it delegates to.
            (ui_application.DesktopApplication, "_on_feedback_decision"),
            # STTController.on_event_stream_event is free and unused BY LOGGING:
            # its return value decides cursor commit and connection recycling.
            (STTController, "_handle_event_stream_event"),
        )
        for owner, name in forbidden:
            with self.subTest(location=f"{owner.__name__}.{name}"):
                source = inspect.getsource(getattr(owner, name))
                self.assertNotIn("_observe", source)
                self.assertNotIn("observability", source)

    def test_the_controllers_own_event_stream_slot_stays_free_for_the_ui(self):
        """§7.4: ``STTController.on_event_stream_event`` is *"vorhanden und
        frei, ABER sein Rueckgabewert entscheidet ueber Cursor-Commit und
        Verbindungsrecycling"*. Logging must never occupy it."""
        from core.config import AppConfig
        from core.controller import STTController
        from core.history import TranscriptHistoryManager
        from tests.test_controller import (
            FakeAudioCapture,
            FakeInjectionQueue,
            FakeSessionCoordinator,
            FakeSTTSession,
        )

        config = AppConfig()
        config.history.persistent.enabled = False
        controller = STTController(
            config,
            session=FakeSTTSession(),
            audio=FakeAudioCapture(),
            history_manager=TranscriptHistoryManager(config.history),
            injection_queue=FakeInjectionQueue(),
            session_coordinator=FakeSessionCoordinator(),
            observability=ObservabilityIngress(instance_id="slot-test"),
        )
        try:
            self.assertIsNone(controller.on_event_stream_event)
        finally:
            controller.history.cleanup()

    def test_default_coordinator_observes_nothing(self):
        coordinator = DualSessionCoordinator(
            ServerConfig(),
            EventStreamConfig(cursor_persistence_enabled=False),
        )
        self.assertIsNone(coordinator.on_observation)
        self.assertIs(coordinator._observe.ingress, NULL_INGRESS)


class TestIndependentFanOut(unittest.IsolatedAsyncioTestCase):
    """O-02: *"Ein Ereignis geht PARALLEL an Fachlogik und Observability,
    niemals DURCH die Observability hindurch."*"""

    async def asyncSetUp(self) -> None:
        self.coordinator = DualSessionCoordinator(
            ServerConfig(),
            EventStreamConfig(cursor_persistence_enabled=False),
        )
        self.coordinator._binding = 1
        self.coordinator._context = SessionContext(
            generation=1,
            session_id="session-1",
            log_access=access(),
            event_state=EventConnectionState.LIVE,
            token_expires_at=_far_future(),
        )
        self.processor = EventProtocolProcessor(access())
        enter_live(self.processor)
        self.feedback_calls = []
        self.observations = []

        async def feedback(context, result) -> bool:
            self.feedback_calls.append(result)
            return True

        self.coordinator.on_event = feedback
        self.coordinator.on_observation = lambda ctx, res: self.observations.append(res)

    async def asyncTearDown(self) -> None:
        await self.coordinator.shutdown()

    async def test_both_branches_see_the_same_event(self):
        result = self.processor.process_mapping(event_frame(5, "evt-5", replay=False))
        accepted = await self.coordinator._handle_event(1, result)
        self.assertTrue(accepted)
        self.assertEqual(len(self.feedback_calls), 1)
        self.assertEqual(len(self.observations), 1)
        self.assertIs(self.feedback_calls[0], self.observations[0])

    async def test_logging_neither_owns_nor_filters_the_feedback_branch(self):
        """Logging returns nothing; the feedback branch alone decides."""

        async def refusing(context, result) -> bool:
            return False

        self.coordinator.on_event = refusing
        result = self.processor.process_mapping(event_frame(6, "evt-6", replay=False))
        accepted = await self.coordinator._handle_event(1, result)
        self.assertFalse(accepted)
        # Observed regardless of the feedback decision.
        self.assertEqual(len(self.observations), 1)

    async def test_events_the_runtime_path_discards_are_still_observed(self):
        """§7.2 point 3: the observation runs BEFORE the binding/token/session
        checks -- *"damit werden genau die Events sichtbar, die der Runtimepfad
        verwirft"*."""
        result = self.processor.process_mapping(event_frame(7, "evt-7", replay=False))
        # A stale binding: the runtime path rejects this immediately.
        accepted = await self.coordinator._handle_event(999, result)
        self.assertFalse(accepted)
        self.assertEqual(self.feedback_calls, [])
        self.assertEqual(len(self.observations), 1)

    async def test_a_slow_observer_delays_but_does_not_change_the_outcome(self):
        """ARCH §8.5 GRENZE 2: the observer principle guarantees BEHAVIOURAL
        equality, not LATENCY equality -- it runs on the same thread, before
        the feedback branch. This test documents that limit."""
        import time

        def slow(ctx, res) -> None:
            time.sleep(0.2)
            self.observations.append(res)

        self.coordinator.on_observation = slow
        result = self.processor.process_mapping(event_frame(8, "evt-8", replay=False))
        started = time.monotonic()
        accepted = await self.coordinator._handle_event(1, result)
        elapsed = time.monotonic() - started

        self.assertTrue(accepted)
        # Generous lower bound: the point is the delay's existence, not its
        # size, and the Windows clock granularity is coarse.
        self.assertGreaterEqual(elapsed, 0.1)
        self.assertEqual(len(self.observations), 1)


class TestEventStreamStateChanged(unittest.IsolatedAsyncioTestCase):
    async def test_state_change_produces_one_record_per_transition(self):
        ingress = build_ingress()
        coordinator = DualSessionCoordinator(
            ServerConfig(),
            EventStreamConfig(cursor_persistence_enabled=False),
            observability=ingress,
        )
        self.addAsyncCleanup(coordinator.shutdown)
        coordinator._binding = 1

        coordinator._handle_state(1, EventConnectionState.CONNECTING)
        coordinator._handle_state(1, EventConnectionState.LIVE)
        # The same state twice must not produce a second record.
        coordinator._handle_state(1, EventConnectionState.LIVE)

        records = [
            record
            for record in ingress.drain(50, 0.0)
            if record.type == "client.eventstream.state_changed"
        ]
        self.assertEqual(len(records), 2)
        self.assertEqual(
            [dict(record.details)["state"] for record in records],
            ["connecting", "live"],
        )
        self.assertEqual(dict(records[1].details)["previous"], "connecting")
        self.assertEqual(records[0].channel, "system")
        self.assertEqual(records[0].component, "eventstream")


class TestProtocolErrorObservationPoint(unittest.IsolatedAsyncioTestCase):
    """FD-R3 / §7.5 / ARCH §8.5 GRENZE 1."""

    def build_transport(self, ingress, connect_factory):
        processor = EventProtocolProcessor(access())
        return EventStreamTransport(
            EventStreamConfig(
                reconnect_min_delay=0.01,
                reconnect_max_delay=0.02,
                reconnect_jitter=0.0,
            ),
            access(),
            processor,
            on_event=lambda result: True,
            connect_factory=connect_factory,
            observability=ingress,
        )

    async def collect_protocol_errors(self, ingress, transport):
        """Run the transport until it has produced at least one record.

        Stopping earlier would prove nothing: ``run()``'s ``except`` branch
        begins with ``if not self._running: break``, so a transport that is
        already stopping deliberately observes nothing — a shutdown is not a
        protocol error.
        """
        task = asyncio.create_task(transport.run())
        records = []
        for _ in range(200):
            await asyncio.sleep(0.01)
            records.extend(
                record
                for record in ingress.drain(200, 0.0)
                if record.type == "client.eventstream.protocol_error"
            )
            if records:
                break
        await transport.stop()
        await asyncio.gather(task, return_exceptions=True)
        return records

    async def test_a_protocol_violation_becomes_a_structured_record(self):
        ingress = build_ingress()

        async def failing_connect(*args, **kwargs):
            raise ValueError("server sent a frame that is not JSON")

        transport = self.build_transport(ingress, failing_connect)
        records = await self.collect_protocol_errors(ingress, transport)

        self.assertGreaterEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.channel, "system")
        self.assertEqual(record.level, "WARNING")
        self.assertEqual(record.component, "eventstream")
        details = dict(record.details)
        self.assertEqual(details["error_type"], "ValueError")
        self.assertIn("not JSON", details["message"])
        self.assertEqual(record.session_id, "session-1")

    async def test_the_record_never_carries_a_raw_frame(self):
        """§7.5: *"OHNE das Rohframe -- es liegt dort nicht mehr vor."*

        The exception is deliberately given frame-shaped text: even then the
        record's ``raw`` stays ``None`` and ``details`` holds exactly the two
        frozen keys. Whatever the exception says travels as ``message``, which
        the normalizer redacts like any other text — it is never a second,
        unredacted payload field.
        """
        ingress = build_ingress()

        async def failing_connect(*args, **kwargs):
            raise ValueError('{"type": "log.event", "secretFrameContent": 1}')

        transport = self.build_transport(ingress, failing_connect)
        records = await self.collect_protocol_errors(ingress, transport)

        self.assertGreaterEqual(len(records), 1)
        for record in records:
            self.assertIsNone(record.raw)
            self.assertEqual(
                set(dict(record.details)), {"error_type", "message"}
            )

    async def test_a_transport_without_observability_still_runs(self):
        """The default is NULL_INGRESS; the second observation point must be
        entirely optional."""
        attempts = {"count": 0}

        async def failing_connect(*args, **kwargs):
            attempts["count"] += 1
            raise ValueError("boom")

        processor = EventProtocolProcessor(access())
        transport = EventStreamTransport(
            EventStreamConfig(
                reconnect_min_delay=0.01,
                reconnect_max_delay=0.02,
                reconnect_jitter=0.0,
            ),
            access(),
            processor,
            on_event=lambda result: True,
            connect_factory=failing_connect,
        )
        task = asyncio.create_task(transport.run())
        await asyncio.sleep(0.02)
        await transport.stop()
        await asyncio.gather(task, return_exceptions=True)
        self.assertGreaterEqual(attempts["count"], 1)


class TestTransportFactoryInjection(unittest.IsolatedAsyncioTestCase):
    """CONTRACTS §6: the default factory carries the ingress, an externally
    supplied factory stays exactly as narrow as it is today."""

    async def test_an_external_factory_is_still_called_with_six_arguments(self):
        seen = {}

        class OneSignatureTransport:
            def __init__(self, config, access_, processor, *, on_event,
                         on_control, on_state_change) -> None:
                seen["built"] = True
                self._stopped = asyncio.Event()

            async def run(self) -> None:
                await self._stopped.wait()

            async def stop(self) -> None:
                self._stopped.set()

        coordinator = DualSessionCoordinator(
            ServerConfig(),
            EventStreamConfig(cursor_persistence_enabled=False),
            transport_factory=OneSignatureTransport,
            observability=ObservabilityIngress(instance_id="x"),
        )
        self.addAsyncCleanup(coordinator.shutdown)
        await coordinator.begin_generation(1)
        accepted = await coordinator.adopt_hello(1, _stt_hello("session-1"))
        await asyncio.sleep(0)
        self.assertTrue(accepted)
        self.assertTrue(seen.get("built"))

    async def test_the_default_factory_hands_the_ingress_to_the_transport(self):
        ingress = build_ingress()
        coordinator = DualSessionCoordinator(
            ServerConfig(),
            EventStreamConfig(cursor_persistence_enabled=False),
            observability=ingress,
        )
        transport = coordinator._transport_factory(
            EventStreamConfig(),
            access(),
            EventProtocolProcessor(access()),
            on_event=lambda result: True,
            on_control=None,
            on_state_change=None,
        )
        self.assertIsInstance(transport, EventStreamTransport)
        self.assertIs(transport._observe.ingress, ingress)


def _stt_hello(session_id: str) -> dict:
    from datetime import datetime, timedelta, timezone

    expiry = (
        datetime.now(timezone.utc) + timedelta(hours=1)
    ).isoformat().replace("+00:00", "Z")
    return {
        "type": "hello",
        "sessionId": session_id,
        "logAccess": {
            "available": True,
            "websocketPath": "/ws/logs",
            "sessionId": session_id,
            "accessToken": "a-token",
            "logProtocolVersion": 2,
            "deliveryMode": "sqlite_first",
            "replayAvailable": True,
            "serverInstanceId": "server-1",
            "oldestCursor": 1,
            "latestCursor": 10,
            "expiresAt": expiry,
        },
    }


if __name__ == "__main__":
    unittest.main()
