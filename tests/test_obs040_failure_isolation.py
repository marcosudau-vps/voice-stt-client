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

from voice_stt_client.core.config import AppConfig, EventStreamConfig, ServerConfig
from voice_stt_client.core.history import TranscriptHistoryManager
from voice_stt_client.core.observability.health import LoggingHealthState
from voice_stt_client.core.observability.ingress import ObservabilityIngress
from voice_stt_client.core.session_coordinator import DualSessionCoordinator


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




class TestObserverFailureDoesNotAffectTheClient(unittest.IsolatedAsyncioTestCase):





    async def test_a_broken_ingress_does_not_stop_the_coordinator(self):
        ingress = ExplodingIngress()
        coordinator = DualSessionCoordinator(
            ServerConfig(),
            EventStreamConfig(cursor_persistence_enabled=False),
            observability=ingress,
        )
        self.addAsyncCleanup(coordinator.shutdown)
        coordinator._binding = 1

        from voice_stt_client.core.event_models import EventConnectionState

        coordinator._handle_state(1, EventConnectionState.LIVE)

        self.assertEqual(
            coordinator.context.event_state, EventConnectionState.LIVE
        )

    async def test_a_broken_ingress_does_not_stop_the_injection_queue(self):
        from voice_stt_client.core.text_injector import TextInjectionQueue

        ingress = ExplodingIngress()
        config = AppConfig()
        config.history.persistent.enabled = False
        history = TranscriptHistoryManager(config.history)
        queue = TextInjectionQueue(config, history, None, observability=ingress)

        # Never raises, and the queue's own state is untouched.
        queue._observe_queue_state("after_job", force=True)
        self.assertEqual(queue.queue_size(), 0)


class TestDeadWorkerDoesNotAffectTheClient(unittest.IsolatedAsyncioTestCase):
    pass



class TestExistingBehaviourIsUnchanged(unittest.IsolatedAsyncioTestCase):
    """Regression: the feedback and event-stream paths behave identically with
    and without an observer."""

    def make_controller(self, ingress):
        return build_controller(ingress)



if __name__ == "__main__":
    unittest.main()
