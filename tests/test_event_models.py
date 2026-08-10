"""Unit tests for immutable AP07 event and feedback models."""

import unittest

from core.event_models import (
    CanonicalEventType,
    EventEnvelope,
    EventOrigin,
    FeedbackImpulse,
    FeedbackSource,
    LogControlMessage,
    LogMessageType,
    NormalizedFeedbackEvent,
)


def valid_envelope():
    return {
        "schemaVersion": 1,
        "eventId": "evt-1",
        "cursor": 42,
        "timestamp": "2026-08-09T12:00:00.000Z",
        "channel": "transcription",
        "event": "transcription.completed",
        "severity": "info",
        "serverInstanceId": "server-1",
        "sessionId": "session-1",
        "segmentId": 3,
        "data": {"reason": "done", "nested": [1, {"ok": True}]},
        "futureField": {"kept": True},
    }


class TestEventModels(unittest.TestCase):
    def test_event_envelope_is_defensive_and_keeps_unknown_fields(self):
        raw = valid_envelope()
        envelope = EventEnvelope.from_mapping(raw)
        raw["data"]["reason"] = "changed"
        self.assertEqual(envelope.data["reason"], "done")
        self.assertEqual(envelope.extra["futureField"]["kept"], True)
        self.assertEqual(envelope.data["nested"][1]["ok"], True)
        with self.assertRaises(TypeError):
            envelope.data["new"] = "not allowed"

    def test_invalid_required_envelope_fields_are_rejected(self):
        mutations = (
            ("schemaVersion", 0),
            ("eventId", ""),
            ("cursor", -1),
            ("timestamp", None),
            ("segmentId", True),
            ("data", []),
        )
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                raw = valid_envelope()
                raw[key] = value
                with self.assertRaises(ValueError):
                    EventEnvelope.from_mapping(raw)

    def test_log_control_message_accepts_known_types_only(self):
        message = LogControlMessage.from_mapping(
            {"type": "log.replay_completed", "cursor": 41}
        )
        self.assertEqual(message.message_type, LogMessageType.REPLAY_COMPLETED)
        self.assertEqual(message.payload["cursor"], 41)
        with self.assertRaises(ValueError):
            LogControlMessage.from_mapping({"type": "log.invented"})

    def test_replay_cannot_carry_a_historical_impulse(self):
        with self.assertRaises(ValueError):
            NormalizedFeedbackEvent(
                event_type=CanonicalEventType.SERVER_RECORDING_STARTED,
                origin=EventOrigin.REPLAY,
                source=FeedbackSource.EVENT_STREAM,
                impulse=FeedbackImpulse.RECORDING_STARTED,
            )
        event = NormalizedFeedbackEvent(
            event_type=CanonicalEventType.CLIENT_MICROPHONE_LOST,
            origin=EventOrigin.LOCAL,
            source=FeedbackSource.LOCAL_ONLY,
            impulse=FeedbackImpulse.MICROPHONE_LOST,
            details={"device": {"index": 2}},
        )
        with self.assertRaises(TypeError):
            event.details["device"]["index"] = 4
        with self.assertRaises(TypeError):
            NormalizedFeedbackEvent(
                event_type=CanonicalEventType.CLIENT_MICROPHONE_LOST,
                origin=EventOrigin.LOCAL,
                source=FeedbackSource.LOCAL_ONLY,
                details=[],
            )


if __name__ == "__main__":
    unittest.main()
