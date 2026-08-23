"""
Contract tests for the structured client observation input (OBS-010).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §3.3 and §6
(``Ingress.event`` signature), ARCH §3.4 (activation_id diagnostic only),
CONTRACTS §1.3 (scope derivation).
"""

from __future__ import annotations

import unittest

from core.observability.normalizer import from_client_event

INSTANCE_ID = "client-instance-1"


class TestClientEventMapping(unittest.TestCase):
    def test_full_client_event(self):
        record = from_client_event(
            "client.trigger.sent",
            channel="audit",
            level="INFO",
            component="stt_session",
            message="Trigger gesendet.",
            details={"channels": ["transcription"], "afterCursor": 0},
            instance_id=INSTANCE_ID,
            session_id="session-1",
            generation=2,
            activation_id="activation-7",
            segment_id=3,
            command_id="cmd-123",
            correlation_id="trigger:cmd-123",
            transcription_id="session-1:2:3",
        )
        self.assertIsNotNone(record)
        self.assertEqual(record.producer_kind, "client")
        self.assertEqual(record.producer_id, "voice-stt-client")
        self.assertEqual(record.instance_id, INSTANCE_ID)
        self.assertEqual(record.channel, "audit")
        self.assertEqual(record.level, "INFO")
        self.assertEqual(record.type, "client.trigger.sent")
        self.assertEqual(record.component, "stt_session")
        self.assertEqual(record.session_id, "session-1")
        self.assertEqual(record.generation, 2)
        self.assertEqual(record.activation_id, "activation-7")
        self.assertEqual(record.segment_id, 3)
        self.assertEqual(record.command_id, "cmd-123")
        self.assertEqual(record.correlation_id, "trigger:cmd-123")
        self.assertEqual(record.transcription_id, "session-1:2:3")
        self.assertEqual(record.scope, "session")
        self.assertEqual(record.replayed, False)
        self.assertIsNone(record.event_id)
        self.assertIsNone(record.raw)

    def test_scope_is_instance_without_session(self):
        record = from_client_event(
            "client.app.started", channel="system", level="INFO",
            instance_id=INSTANCE_ID,
        )
        self.assertEqual(record.scope, "instance")

    def test_record_id_generated_and_received_at_set(self):
        record = from_client_event(
            "client.app.started", channel="system", level="INFO",
            instance_id=INSTANCE_ID,
        )
        self.assertEqual(len(record.record_id), 32)
        self.assertIn("Z", record.received_at)

    def test_correlation_ids_default_to_none(self):
        record = from_client_event(
            "client.hotkey.pressed", channel="audit", level="INFO",
            instance_id=INSTANCE_ID,
        )
        for field in ("session_id", "generation", "activation_id",
                      "segment_id", "command_id", "correlation_id",
                      "transcription_id"):
            self.assertIsNone(getattr(record, field))

    def test_message_and_details_are_redacted(self):
        record = from_client_event(
            "client.final.deduplicated",
            channel="transcription",
            level="WARNING",
            message="Final [seg=1]: vertraulich",
            details={"text": "vertraulich", "accessToken": "t"},
            instance_id=INSTANCE_ID,
            store_transcription_content=False,
        )
        self.assertNotIn("vertraulich", record.message)
        self.assertNotIn("vertraulich", dict(record.details))
        self.assertEqual(record.details["accessToken"], "[redacted]")

    def test_details_are_not_mutated(self):
        details = {"lists": [1, 2], "nested": {"b": 2}}
        from_client_event(
            "client.audio.stream_started", channel="system", level="INFO",
            details=details, instance_id=INSTANCE_ID,
        )
        self.assertEqual(details, {"lists": [1, 2], "nested": {"b": 2}})
        self.assertIsInstance(details["lists"], list)


class TestClientEventNegative(unittest.TestCase):
    def test_level_outside_closed_set_yields_none(self):
        record = from_client_event(
            "client.trigger.sent", channel="audit", level="VERBOSE",
            instance_id=INSTANCE_ID,
        )
        self.assertIsNone(record)

    def test_details_not_a_mapping_yields_none(self):
        record = from_client_event(
            "client.trigger.sent", channel="audit", level="INFO",
            details=[1, 2, 3], instance_id=INSTANCE_ID,
        )
        self.assertIsNone(record)

    def test_negative_or_bool_segment_id_yields_none(self):
        for bad in (-1, True):
            with self.subTest(value=bad):
                record = from_client_event(
                    "client.trigger.sent", channel="audit", level="INFO",
                    segment_id=bad, instance_id=INSTANCE_ID,
                )
                self.assertIsNone(record)

    def test_missing_instance_id_yields_none(self):
        record = from_client_event(
            "client.trigger.sent", channel="audit", level="INFO",
            instance_id=" ",
        )
        self.assertIsNone(record)

    def test_channel_unknown_is_stored_not_rejected(self):
        """CONTRACTS §2.1: channel is open — unknown values are stored."""
        record = from_client_event(
            "client.whatever", channel="future_channel", level="INFO",
            instance_id=INSTANCE_ID,
        )
        self.assertIsNotNone(record)
        self.assertEqual(record.channel, "future_channel")


if __name__ == "__main__":
    unittest.main()