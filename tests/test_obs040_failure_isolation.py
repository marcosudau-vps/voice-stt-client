"""
OBS-040 — a logging failure never affects the client function.

Frozen sources: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` O-01 (observability only),
O-03 (non-blocking), O-05 (failure isolation), §8.3 (failure table), §8.5
GRENZE 3 (a dead worker loses records, and the RotatingFileHandler is the
fallback that is precisely why it is not replaced), §9 (a throwing observer must
influence neither cursor commit nor connection recycling);
``LOGGING_CONTRACTS_FREEZE_V1.md`` §6 (``submit`` never blocks, never raises),
§7.3.

The pattern of every test here: break the logging domain as badly as possible,
then assert the product path is unchanged.
"""

from __future__ import annotations

import asyncio
import time
import unittest

from core.config import AppConfig, EventStreamConfig, ServerConfig
from core.controller import STTController, TransientEventType
from core.history import TranscriptHistoryManager
from core.observability.health import LoggingHealthState
from core.observability.ingress import ObservabilityIngress
from core.session_coordinator import DualSessionCoordinator
from core.stt_session import STTSession, TransportState
from tests.test_controller import (
    FakeAudioCapture,
    FakeInjectionQueue,
    FakeSessionCoordinator,
    FakeSTTSession,
)


class ExplodingIngress(ObservabilityIngress):
    """Every entry point raises. Nothing an ``Ingress`` offers works."""

    def __init__(self) -> None:
        super().__init__(instance_id="exploding", queue_size=4)
        self.calls = 0

    def event(self, *args, **kwargs):
        self.calls += 1
        raise RuntimeError("event exploded")

    def submit(self, record):
        self.calls += 1
        raise RuntimeError("submit exploded")

    def observe_server_result(self, context, result):
        self.calls += 1
        raise RuntimeError("observe exploded")


def build_controller(ingress):
    config = AppConfig()
    config.history.persistent.enabled = False
    return STTController(
        config,
        session=FakeSTTSession(),
        audio=FakeAudioCapture(),
        history_manager=TranscriptHistoryManager(config.history),
        injection_queue=FakeInjectionQueue(),
        session_coordinator=FakeSessionCoordinator(),
        observability=ingress,
    )


class TestObserverFailureDoesNotAffectTheClient(unittest.IsolatedAsyncioTestCase):
    async def test_a_broken_ingress_does_not_stop_a_dictation_start(self):
        ingress = ExplodingIngress()
        controller = build_controller(ingress)
        self.addAsyncCleanup(controller.shutdown)
        controller._loop = asyncio.get_running_loop()

        immediate, attempt = controller._begin_start_locked()

        self.assertIsNone(immediate)
        self.assertIsNotNone(attempt)
        self.assertGreater(ingress.calls, 0)
        self.assertEqual(controller.audio.start_calls, 1)
        attempt.send_task.cancel()
        await asyncio.gather(attempt.send_task, return_exceptions=True)

    async def test_a_broken_ingress_does_not_stop_feedback_publication(self):
        ingress = ExplodingIngress()
        controller = build_controller(ingress)
        self.addAsyncCleanup(controller.shutdown)
        decisions = []
        controller.on_feedback_decision = decisions.append

        controller._emit_feedback_event(
            TransientEventType.ACTION_BLOCKED, "transport_not_ready", "x"
        )

        self.assertEqual(len(decisions), 1)
        self.assertGreater(ingress.calls, 0)

    async def test_a_broken_ingress_does_not_stop_error_classification(self):
        ingress = ExplodingIngress()
        controller = build_controller(ingress)
        self.addAsyncCleanup(controller.shutdown)

        controller._handle_error_event(
            {"type": "error", "where": "admission", "message": "busy"}
        )

        self.assertEqual(
            controller.availability_state.value, "server_busy"
        )

    async def test_a_broken_ingress_does_not_stop_the_session_transport(self):
        ingress = ExplodingIngress()
        config = AppConfig()
        session = STTSession(config.server, config.session, observability=ingress)
        states = []
        session.on_transport_change = states.append

        session._update_transport(TransportState.CONNECTING)
        session._record_failure("network_timeout")

        self.assertEqual(states, [TransportState.CONNECTING])
        self.assertEqual(session.last_failure_reason, "network_timeout")
        self.assertEqual(session.reconnect_attempt, 1)

    async def test_a_broken_ingress_does_not_stop_a_trigger(self):
        ingress = ExplodingIngress()
        config = AppConfig()
        session = STTSession(config.server, config.session, observability=ingress)
        sent = []

        async def fake_send_json(payload):
            sent.append(payload)

        session._send_json = fake_send_json
        session._ws_is_open = lambda: True

        command_id = await session.send_trigger("activate", "manual")

        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0]["commandId"], command_id)
        self.assertIn(command_id, session.pending_trigger_ids)

    async def test_a_broken_ingress_does_not_stop_the_coordinator(self):
        ingress = ExplodingIngress()
        coordinator = DualSessionCoordinator(
            ServerConfig(),
            EventStreamConfig(cursor_persistence_enabled=False),
            observability=ingress,
        )
        self.addAsyncCleanup(coordinator.shutdown)
        coordinator._binding = 1

        from core.event_models import EventConnectionState

        coordinator._handle_state(1, EventConnectionState.LIVE)

        self.assertEqual(
            coordinator.context.event_state, EventConnectionState.LIVE
        )

    async def test_a_broken_ingress_does_not_stop_the_injection_queue(self):
        from core.text_injector import TextInjectionQueue

        ingress = ExplodingIngress()
        config = AppConfig()
        config.history.persistent.enabled = False
        history = TranscriptHistoryManager(config.history)
        queue = TextInjectionQueue(config, history, None, observability=ingress)

        # Never raises, and the queue's own state is untouched.
        queue._observe_queue_state("after_job", force=True)
        self.assertEqual(queue.queue_size(), 0)


class TestDeadWorkerDoesNotAffectTheClient(unittest.IsolatedAsyncioTestCase):
    async def test_a_failed_worker_makes_submit_return_false_but_nothing_else(self):
        """ARCH §8.3/§8.5 GRENZE 3: after a worker failure the ingress switches
        to "nur verwerfen und zaehlen" -- and the client keeps working."""
        ingress = ObservabilityIngress(instance_id="dead-worker", queue_size=16)
        ingress.health.set_state(LoggingHealthState.FAILED_WORKER, "test")
        controller = build_controller(ingress)
        self.addAsyncCleanup(controller.shutdown)
        decisions = []
        controller.on_feedback_decision = decisions.append

        controller._emit_feedback_event(
            TransientEventType.DICTATION_INTERRUPTED, "transport_loss", "x"
        )

        self.assertEqual(len(decisions), 1)
        self.assertEqual(ingress.drain(16, 0.0), [])

    async def test_a_full_queue_never_blocks_a_producer(self):
        """O-03: *"Es gibt ausschliesslich put_nowait."* With a queue of one and
        a thousand observations, the producer must never wait."""
        ingress = ObservabilityIngress(instance_id="full", queue_size=1)
        config = AppConfig()
        session = STTSession(config.server, config.session, observability=ingress)

        started = time.monotonic()
        for _ in range(1000):
            session._record_failure("network_timeout")
        elapsed = time.monotonic() - started

        self.assertLess(elapsed, 2.0)
        snapshot = ingress.health.snapshot()
        self.assertGreater(
            snapshot.dropped_watermark + snapshot.dropped_queue_full, 0
        )
        self.assertEqual(session.reconnect_attempt, 1000)


class TestExistingBehaviourIsUnchanged(unittest.IsolatedAsyncioTestCase):
    """Regression: the feedback and event-stream paths behave identically with
    and without an observer."""

    def make_controller(self, ingress):
        return build_controller(ingress)

    async def test_feedback_decisions_are_identical_with_and_without_observer(self):
        without = self.make_controller(ObservabilityIngress(
            instance_id="a", enabled=False
        ))
        with_obs = self.make_controller(ObservabilityIngress(
            instance_id="b", queue_size=256
        ))
        self.addAsyncCleanup(without.shutdown)
        self.addAsyncCleanup(with_obs.shutdown)
        first, second = [], []
        without.on_feedback_decision = first.append
        with_obs.on_feedback_decision = second.append

        for controller in (without, with_obs):
            controller._emit_feedback_event(
                TransientEventType.ACTION_BLOCKED, "transport_not_ready", "x"
            )

        self.assertEqual(len(first), len(second), 1)
        self.assertEqual(first[0].state, second[0].state)
        self.assertEqual(first[0].source, second[0].source)
        self.assertEqual(first[0].rule.led, second[0].rule.led)


if __name__ == "__main__":
    unittest.main()
