from __future__ import annotations

import unittest

from core.event_models import (
    CanonicalEventType,
    EventConnectionState,
    EventEnvelope,
    EventOrigin,
    FeedbackImpulse,
    FeedbackSource,
    FeedbackState,
)
from core.event_normalizer import EventNormalizationError, EventNormalizer
from core.event_protocol import EventProtocolResult, EventResultKind


def log_result(
    name: str,
    *,
    origin: EventOrigin = EventOrigin.LIVE,
    session_id: str = "session-1",
    segment_id: int | None = 4,
    event_id: str = "event-1",
    transcription_id: str | None = "session-1:1:4",
    data: dict | None = None,
    channel: str = "transcription",
) -> EventProtocolResult:
    raw = {
        "schemaVersion": 1,
        "eventId": event_id,
        "cursor": 10,
        "timestamp": "2026-08-09T12:00:00Z",
        "channel": channel,
        "event": name,
        "severity": "info",
        "serverInstanceId": "server-a",
        "sessionId": session_id,
        "data": data or {},
    }
    if segment_id is not None:
        raw["segmentId"] = segment_id
    if transcription_id is not None:
        raw["transcriptionId"] = transcription_id
    return EventProtocolResult(
        kind=EventResultKind.EVENT,
        connection_state=(
            EventConnectionState.REPLAYING
            if origin is EventOrigin.REPLAY
            else EventConnectionState.LIVE
        ),
        event=EventEnvelope.from_mapping(raw),
        origin=origin,
        cursor=10,
    )


class EventNormalizerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.normalizer = EventNormalizer()

    def test_all_documented_feedback_lifecycle_names_are_mapped(self) -> None:
        expected = {
            "wakeword.detected": CanonicalEventType.SERVER_WAKE_WORD_DETECTED,
            "transcription.recording_started": CanonicalEventType.SERVER_RECORDING_STARTED,
            "transcription.recording_ended": CanonicalEventType.SERVER_RECORDING_ENDED,
            "transcription.started": CanonicalEventType.SERVER_TRANSCRIPTION_STARTED,
            "transcription.completed": CanonicalEventType.SERVER_TRANSCRIPTION_COMPLETED,
            "transcription.discarded": CanonicalEventType.SERVER_TRANSCRIPTION_DISCARDED,
            "transcription.failed": CanonicalEventType.SERVER_TRANSCRIPTION_FAILED,
            "transcription.cancelled": CanonicalEventType.SERVER_TRANSCRIPTION_CANCELLED,
            "transcription.rejected": CanonicalEventType.SERVER_TRANSCRIPTION_REJECTED,
        }
        for name, canonical in expected.items():
            with self.subTest(name=name):
                segment_id = None if name == "wakeword.detected" else 4
                data = {"reason": "empty_final"} if name == "transcription.discarded" else {}
                event = self.normalizer.normalize_event_stream(
                    log_result(name, segment_id=segment_id, data=data),
                    generation=1,
                    session_id="session-1",
                )
                self.assertEqual(event.event_type, canonical)
                self.assertEqual(event.source, FeedbackSource.EVENT_STREAM)

    def test_replay_reconstructs_state_without_impulse(self) -> None:
        event = self.normalizer.normalize_event_stream(
            log_result(
                "transcription.recording_started",
                origin=EventOrigin.REPLAY,
            ),
            generation=1,
            session_id="session-1",
        )

        self.assertEqual(event.state, FeedbackState.RECORDING)
        self.assertIsNone(event.impulse)
        self.assertEqual(event.origin, EventOrigin.REPLAY)

    def test_correlation_uses_transcription_then_session_segment_alias(self) -> None:
        event = self.normalizer.normalize_event_stream(
            log_result("transcription.completed"),
            generation=1,
            session_id="session-1",
        )

        self.assertIn("transcription:session-1:1:4", event.correlation_id)
        self.assertIn(
            "server.transcription.completed|session:session-1|segment:4",
            event.details["correlationAliases"],
        )

    def test_fallback_maps_only_predefined_timeline_final_and_error(self) -> None:
        recording = self.normalizer.normalize_stt_fallback(
            "timeline",
            {
                "type": "timeline",
                "event": "recording_started",
                "sessionId": "session-1",
                "segmentId": 8,
            },
            generation=2,
            session_id="session-1",
        )
        final = self.normalizer.normalize_stt_fallback(
            "final",
            {"type": "final", "sessionId": "session-1", "segmentId": 8},
            generation=2,
            session_id="session-1",
        )
        error = self.normalizer.normalize_stt_fallback(
            "error",
            {"type": "error", "sessionId": "session-1", "where": "recorder"},
            generation=2,
            session_id="session-1",
        )

        self.assertEqual(recording.impulse, FeedbackImpulse.RECORDING_STARTED)
        self.assertEqual(final.event_type, CanonicalEventType.SERVER_TRANSCRIPTION_COMPLETED)
        self.assertEqual(error.event_type, CanonicalEventType.SERVER_TRANSCRIPTION_FAILED)
        self.assertIsNone(
            self.normalizer.normalize_stt_fallback(
                "realtime",
                {"sessionId": "session-1", "segmentId": 8, "text": "secret"},
                generation=2,
                session_id="session-1",
            )
        )

    def test_unknown_server_event_is_ignored(self) -> None:
        self.assertIsNone(
            self.normalizer.normalize_event_stream(
                log_result("performance.inference"),
                generation=1,
                session_id="session-1",
            )
        )

    def test_known_invalid_events_fail_without_partial_effect(self) -> None:
        invalid = (
            log_result("transcription.completed", segment_id=None),
            log_result("transcription.completed", session_id="other"),
            log_result("transcription.completed", channel="performance"),
            log_result("transcription.discarded", data={"reason": "other"}),
        )
        for result in invalid:
            with self.subTest(event=result.event.event):
                with self.assertRaises(EventNormalizationError):
                    self.normalizer.normalize_event_stream(
                        result,
                        generation=1,
                        session_id="session-1",
                    )

    def test_local_client_events_use_same_normalized_model(self) -> None:
        event = self.normalizer.normalize_local(
            CanonicalEventType.CLIENT_MICROPHONE_LOST,
            generation=3,
            session_id="session-3",
            correlation_id="microphone:device-1:lost",
        )

        self.assertEqual(event.origin, EventOrigin.LOCAL)
        self.assertEqual(event.source, FeedbackSource.LOCAL_ONLY)
        self.assertEqual(event.state, FeedbackState.FAILED)
        self.assertEqual(event.impulse, FeedbackImpulse.MICROPHONE_LOST)


if __name__ == "__main__":
    unittest.main()
