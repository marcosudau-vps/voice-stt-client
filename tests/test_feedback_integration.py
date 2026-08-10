from __future__ import annotations

import unittest

from core.config import AppConfig
from core.controller import FinalProcessingStatus, STTController
from core.event_models import (
    CanonicalEventType,
    EventConnectionState,
    EventOrigin,
    FeedbackImpulse,
    FeedbackSource,
)
from core.event_normalizer import EventNormalizationError
from core.history import TranscriptHistoryManager
from core.session_coordinator import SessionContext
from tests.test_controller import (
    FakeAudioCapture,
    FakeInjectionQueue,
    FakeSTTSession,
    FakeSessionCoordinator,
)
from tests.test_event_normalizer import log_result


class ControllerFeedbackIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.config = AppConfig.load()
        self.config.history.persistent.enabled = False
        self.session = FakeSTTSession()
        self.history = TranscriptHistoryManager(self.config.history)
        self.queue = FakeInjectionQueue()
        self.coordinator = FakeSessionCoordinator()
        self.controller = STTController(
            self.config,
            session=self.session,
            audio=FakeAudioCapture(),
            history_manager=self.history,
            injection_queue=self.queue,
            session_coordinator=self.coordinator,
        )
        self.decisions = []
        self.controller.on_feedback_decision = self.decisions.append

    async def asyncTearDown(self) -> None:
        await self.controller.shutdown()

    def set_connection(self, connection: EventConnectionState, stt_ready=True):
        return self.controller.feedback_engine.update_connection(
            connection,
            stt_ready=stt_ready,
            generation=self.session.generation,
            session_id=self.session.state.session_id,
        )

    def test_stt_timeline_drives_feedback_only_in_fallback(self) -> None:
        self.set_connection(EventConnectionState.UNAVAILABLE)

        self.controller.handle_server_event(
            "timeline",
            {
                "type": "timeline",
                "event": "recording_started",
                "sessionId": self.session.state.session_id,
                "segmentId": 1,
                "_clientGeneration": self.session.generation,
            },
        )

        self.assertEqual(len(self.decisions), 1)
        self.assertEqual(self.decisions[0].source, FeedbackSource.STT_FALLBACK)
        self.assertEqual(
            self.decisions[0].impulse,
            FeedbackImpulse.RECORDING_STARTED,
        )
        self.assertIsNotNone(self.decisions[0].rule.led)

        self.decisions.clear()
        self.set_connection(EventConnectionState.LIVE)
        self.controller.handle_server_event(
            "timeline",
            {
                "type": "timeline",
                "event": "recording_started",
                "sessionId": self.session.state.session_id,
                "segmentId": 2,
                "_clientGeneration": self.session.generation,
            },
        )
        self.assertEqual(self.decisions, [])

    async def test_event_stream_is_reduced_before_cursor_confirmation(self) -> None:
        self.set_connection(EventConnectionState.LIVE)
        context = SessionContext(
            generation=self.session.generation,
            session_id=self.session.state.session_id,
            event_state=EventConnectionState.LIVE,
        )

        accepted = await self.controller._handle_event_stream_event(
            context,
            log_result(
                "transcription.recording_started",
                session_id=self.session.state.session_id,
                segment_id=3,
                event_id="durable-start",
                transcription_id="fake-session:1:3",
            ),
        )

        self.assertTrue(accepted)
        self.assertEqual(len(self.decisions), 1)
        self.assertEqual(
            self.decisions[0].event.event_type,
            CanonicalEventType.SERVER_RECORDING_STARTED,
        )

    async def test_replay_updates_state_without_emitting_adapter_decision(self) -> None:
        self.set_connection(EventConnectionState.REPLAYING)
        context = SessionContext(
            generation=self.session.generation,
            session_id=self.session.state.session_id,
            event_state=EventConnectionState.REPLAYING,
        )

        accepted = await self.controller._handle_event_stream_event(
            context,
            log_result(
                "transcription.recording_started",
                origin=EventOrigin.REPLAY,
                session_id=self.session.state.session_id,
                segment_id=4,
                event_id="replay-start",
                transcription_id="fake-session:1:4",
            ),
        )

        self.assertTrue(accepted)
        self.assertEqual(self.decisions, [])

    async def test_invalid_known_event_prevents_cursor_confirmation(self) -> None:
        self.set_connection(EventConnectionState.LIVE)
        context = SessionContext(
            generation=self.session.generation,
            session_id=self.session.state.session_id,
            event_state=EventConnectionState.LIVE,
        )

        with self.assertRaises(EventNormalizationError):
            await self.controller._handle_event_stream_event(
                context,
                log_result(
                    "transcription.completed",
                    session_id=self.session.state.session_id,
                    segment_id=None,
                    transcription_id=None,
                ),
            )
        self.assertEqual(self.decisions, [])

    def test_final_queue_handoff_emits_local_injection_fact_without_text(self) -> None:
        result = self.controller.process_raw_final_event(
            {
                "type": "final",
                "sessionId": "fake-session",
                "segmentId": 7,
                "text": "must not appear in feedback details",
            }
        )

        self.assertEqual(result.status, FinalProcessingStatus.QUEUED)
        injection = [
            item
            for item in self.decisions
            if item.event
            and item.event.event_type
            is CanonicalEventType.CLIENT_INJECTION_ACCEPTED
        ]
        self.assertEqual(len(injection), 1)
        self.assertNotIn("text", injection[0].event.details)

    def test_ui_adapter_failure_reenters_canonical_local_mapping(self) -> None:
        decision = self.controller.report_local_feedback(
            CanonicalEventType.CLIENT_SOUND_FAILED,
            {"category": "backend"},
        )

        self.assertIs(self.decisions[-1], decision)
        self.assertEqual(
            decision.event.event_type,
            CanonicalEventType.CLIENT_SOUND_FAILED,
        )
        self.assertIsNotNone(decision.rule.app)
        self.assertIsNone(decision.rule.sound)

    async def test_adapter_callback_failure_does_not_reject_processed_event(self) -> None:
        self.set_connection(EventConnectionState.LIVE)
        self.controller.on_feedback_decision = lambda decision: (_ for _ in ()).throw(
            RuntimeError("adapter failure")
        )
        context = SessionContext(
            generation=self.session.generation,
            session_id=self.session.state.session_id,
            event_state=EventConnectionState.LIVE,
        )

        accepted = await self.controller._handle_event_stream_event(
            context,
            log_result(
                "transcription.recording_started",
                session_id=self.session.state.session_id,
                segment_id=9,
                event_id="adapter-isolation",
                transcription_id="fake-session:1:9",
            ),
        )

        self.assertTrue(accepted)


if __name__ == "__main__":
    unittest.main()
