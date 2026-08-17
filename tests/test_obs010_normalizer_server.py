"""
Contract tests for the server-result input of the normalizer (OBS-010).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §3.2 (EVENT- and
CONTROL-Ergebnisse), §4.1/§4.2 (R-5, R-6), CONTTRACTS §5.5 (dedupe
expectation for duplicates). Uses real ``EventProtocolProcessor`` results so
the mapped fields are produced by the valid, frozen protocol path.
"""

from __future__ import annotations

import unittest

from core.event_protocol import (
    EventProtocolProcessor,
    EventProtocolResult,
    EventResultKind,
)
from core.event_models import EventEnvelope, EventOrigin
from core.session_coordinator import SessionContext

from core.observability.normalizer import from_server_result

from test_event_protocol import (
    access,
    envelope,
    event_message,
    hello,
    subscribed,
)

INSTANCE_ID = "client-instance-1"
CONTEXT = SessionContext(session_id="session-1", generation=7)


def processed(processor, message):
    return processor.process_mapping(message)


class TestServerEventMapping(unittest.TestCase):
    def _processor(self):
        processor = EventProtocolProcessor(access())
        processor.begin_subscription()
        processor.process_mapping(hello())
        processor.process_mapping(subscribed(0))
        return processor

    def test_real_log_event_frame_fields(self):
        processor = self._processor()
        result = processed(processor, event_message(3, "evt-3", replay=True))
        record = from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        self.assertIsNotNone(record)
        self.assertEqual(record.producer_kind, "server")
        self.assertEqual(record.producer_id, "voice-stt-server")
        self.assertEqual(record.instance_id, "server-1")
        self.assertEqual(record.channel, "transcription")
        self.assertEqual(record.level, "INFO")
        self.assertEqual(record.type, "transcription.completed")
        self.assertEqual(record.component, "transcription")  # Namensraum-Praefix
        self.assertEqual(record.session_id, "session-1")
        self.assertEqual(record.generation, 7)  # aus SessionContext
        self.assertEqual(record.segment_id, 1)
        self.assertEqual(record.event_id, "evt-3")
        self.assertEqual(record.server_cursor, 3)
        self.assertEqual(record.scope, "session")
        self.assertTrue(record.replayed)  # origin == REPLAY
        self.assertIsNotNone(record.raw)  # store_raw_payload default on

    def _live_processor(self):
        processor = self._processor()
        processor.process_mapping({"type": "log.replay_completed",
                                  "cursor": 20, "count": 0})
        return processor

    def test_live_event_is_not_replayed(self):
        processor = self._live_processor()
        result = processed(processor, event_message(24, "evt-24", replay=False))
        record = from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        self.assertFalse(record.replayed)

    def test_meldung_from_rest_payload_becomes_message(self):
        raw_event = envelope(5, "evt-5")
        raw_event["meldung"] = "fertig geworden"
        processor = self._processor()
        result = processed(processor, {"type": "log.event",
                                      "event": raw_event, "replay": True})
        record = from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        self.assertEqual(record.message, "fertig geworden")

    def test_activation_id_from_data(self):
        raw_event = envelope(6, "evt-6")
        raw_event["data"] = {"activationId": "activation-42"}
        processor = self._processor()
        result = processed(processor, {"type": "log.event",
                                      "event": raw_event, "replay": True})
        record = from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        self.assertEqual(record.activation_id, "activation-42")

    def test_envelope_without_data_has_empty_details(self):
        raw_event = envelope(7, "evt-7")
        del raw_event["data"]
        processor = self._processor()
        result = processed(processor, {"type": "log.event",
                                      "event": raw_event, "replay": True})
        record = from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        self.assertEqual(dict(record.details), {})

    def test_severity_critical_maps_to_critical_level(self):
        raw_event = envelope(8, "evt-8")
        raw_event["severity"] = "critical"
        processor = self._processor()
        result = processed(processor, {"type": "log.event",
                                      "event": raw_event, "replay": True})
        record = from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        self.assertEqual(record.level, "CRITICAL")

    def test_unknown_severity_falls_back_to_info_with_source_severity(self):
        raw_event = envelope(9, "evt-9")
        raw_event["severity"] = "verbose"
        processor = self._processor()
        result = processed(processor, {"type": "log.event",
                                      "event": raw_event, "replay": True})
        record = from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        self.assertEqual(record.level, "INFO")
        self.assertEqual(record.details["source_severity"], "verbose")

    def test_store_raw_payload_false_sets_raw_to_none(self):
        processor = self._processor()
        result = processed(processor, event_message(10, "evt-10", replay=True))
        record = from_server_result(
            CONTEXT, result, client_instance_id=INSTANCE_ID,
            store_raw_payload=False,
        )
        self.assertIsNone(record.raw)

    def test_performance_channel_never_keeps_raw(self):
        raw_event = envelope(11, "evt-11", event="audio.stats")
        raw_event["channel"] = "performance"
        processor2 = EventProtocolProcessor(access(channels=("performance",)))
        processor2.begin_subscription()
        processor2.process_mapping(hello())
        processor2.process_mapping(subscribed(0, channels=["performance"]))
        result = processed(processor2, {"type": "log.event",
                                       "event": raw_event, "replay": True})
        record = from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        self.assertEqual(record.channel, "performance")
        self.assertIsNone(record.raw)

    def test_raw_reference_is_not_copied_eagerly(self):
        """ARCH §8.2: raw is taken as the already frozen reference; the record
        build must not copy it (the worker will unfreeze/serialize later)."""
        from types import MappingProxyType
        processor = self._processor()
        result = processed(processor, event_message(12, "evt-12", replay=True))
        record = from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        self.assertIsInstance(result.payload, MappingProxyType)
        self.assertIs(record.raw, result.payload)

    def test_scope_is_global_for_server_event_without_session(self):
        from core.event_protocol import EventProtocolResult, EventResultKind
        from core.event_models import EventEnvelope, EventOrigin, EventConnectionState
        raw_event = envelope(13, "evt-13")
        raw_event["sessionId"] = None
        env = EventEnvelope.from_mapping(raw_event)
        result = EventProtocolResult(
            kind=EventResultKind.EVENT,
            connection_state=EventConnectionState.LIVE,
            event=env,
            origin=EventOrigin.LIVE,
            cursor=13,
            payload={},
        )
        record = from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        self.assertEqual(record.scope, "global")

    def test_context_with_none_session_does_not_crash(self):
        processor = self._processor()
        result = processed(processor, event_message(14, "evt-14", replay=True))
        context = SessionContext(session_id=None, generation=0)
        record = from_server_result(context, result, client_instance_id=INSTANCE_ID)
        self.assertIsNotNone(record)
        self.assertEqual(record.generation, 0)


class TestServerControlMapping(unittest.TestCase):
    def _processor(self):
        processor = EventProtocolProcessor(access())
        processor.begin_subscription()
        processor.process_mapping(hello())
        processor.process_mapping(subscribed(0))
        return processor

    def _live_processor(self):
        processor = self._processor()
        processor.process_mapping({"type": "log.replay_completed",
                                  "cursor": 20, "count": 0})
        return processor

    def test_gap_controlframe_maps_to_client_eventstream_gap(self):
        processor = self._processor()
        result = processed(processor, {
            "type": "log.gap",
            "reason": "retention",
            "lostFromCursor": 1,
            "lostToCursor": 8,
            "oldestCursor": 2,
            "latestCursor": 20,
        })
        record = from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        self.assertIsNotNone(record)
        self.assertEqual(record.type, "client.eventstream.gap")
        self.assertEqual(record.component, "eventstream")
        self.assertEqual(record.level, "WARNING")
        self.assertEqual(record.producer_kind, "client")
        self.assertEqual(record.producer_id, "voice-stt-client")
        self.assertEqual(record.instance_id, INSTANCE_ID)
        self.assertEqual(record.details["lostFromCursor"], 1)
        self.assertEqual(record.details["lostToCursor"], 8)
        self.assertEqual(record.scope, "session")
        self.assertEqual(record.generation, 7)

    def test_hello_controlframe_is_whitelist_only_no_token(self):
        payload = {
            "type": "log.hello",
            "schemaVersion": 1,
            "logProtocolVersion": 2,
            "deliveryMode": "sqlite_first",
            "replayAvailable": True,
            "serverInstanceId": "server-1",
            "oldestCursor": 0,
            "latestCursor": 20,
            "retentionCursor": 0,
            "logAccess": {
                "available": True,
                "websocketPath": "/ws/logs",
                "historyPath": "/api/logs/events",
                "accessToken": "TOKEN-ABC",
                "sessionId": "session-1",
                "expiresAt": "2026-08-17T00:00:00Z",
                "logProtocolVersion": 2,
                "deliveryMode": "sqlite_first",
                "replayAvailable": True,
                "serverInstanceId": "server-1",
                "oldestCursor": 0,
                "latestCursor": 20,
            },
            "sessionConfig": {"version": 1, "warnings": []},
            "activationConfig": {"mode": "legacy"},
            "sessionCapabilities": {"version": 1},
        }
        processor = EventProtocolProcessor(access())
        processor.begin_subscription()
        result = processor.process_mapping(payload)
        record = from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        self.assertIsNotNone(record)
        self.assertEqual(record.type, "client.eventstream.hello")
        blob = repr(record.__dict__)
        self.assertNotIn("TOKEN-ABC", blob)
        self.assertNotIn("accessToken", record.details)
        self.assertIsNone(record.raw)
        self.assertEqual(record.details["logAccess"]["available"], True)
        self.assertEqual(record.details["logAccess"]["serverInstanceId"], "server-1")
        self.assertNotIn("websocketPath", record.details["logAccess"])
        self.assertEqual(record.details["sessionConfig"]["version"], 1)

    def test_error_controlframe_is_warning(self):
        processor = self._processor()
        result = processed(processor, {"type": "log.error",
                                      "code": "not_authorized"})
        record = from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        self.assertEqual(record.type, "client.eventstream.error")
        self.assertEqual(record.level, "WARNING")

    def test_subscribed_and_pong_controls_are_info(self):
        processor = self._live_processor()
        result = processed(processor, {"type": "log.pong", "cursor": 20,
                                      "serverTime": 1.5})
        record = from_server_result(CONTEXT, result,
                                    client_instance_id=INSTANCE_ID)
        self.assertEqual(record.type, "client.eventstream.pong")
        self.assertEqual(record.level, "INFO")

    def test_control_scope_is_instance_without_session(self):
        processor = self._processor()
        context = SessionContext(session_id=None, generation=0)
        result = processed(processor, {"type": "log.error",
                                      "code": "not_authorized"})
        record = from_server_result(context, result, client_instance_id=INSTANCE_ID)
        self.assertEqual(record.scope, "instance")

    def test_duplicate_event_is_mapped_as_control(self):
        """CONTRACTS §3.2: duplicate-marked events are CONTROL results."""
        processor = EventProtocolProcessor(access(), dedupe_limit=4)
        processor.begin_subscription()
        processor.process_mapping(hello())
        processor.process_mapping(subscribed(0))
        first = processed(processor, event_message(2, "dup-id", replay=True))
        processor.confirm_event(first)
        duplicate = processed(processor, event_message(2, "dup-id", replay=True))
        self.assertTrue(duplicate.duplicate)
        record = from_server_result(CONTEXT, duplicate,
                                    client_instance_id=INSTANCE_ID)
        self.assertIsNotNone(record)
        self.assertEqual(record.type, "client.eventstream.event")
        self.assertEqual(record.component, "eventstream")
        self.assertEqual(record.producer_kind, "client")


class TestServerNormalizerNeverRaises(unittest.TestCase):
    def test_event_without_envelope_yields_none(self):
        result = EventProtocolResult(
            kind=EventResultKind.EVENT,
            connection_state=None,
            event=None,
            origin=EventOrigin.LIVE,
            payload={},
        )
        self.assertIsNone(
            from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        )

    def test_garbage_result_yields_none(self):
        self.assertIsNone(from_server_result(CONTEXT, None))
        self.assertIsNone(from_server_result(CONTEXT, object()))

    def test_unknown_kind_yields_none(self):
        result = EventProtocolResult(
            kind="future.kind", connection_state=None, event=None,
            payload={"hallo": 1},
        )
        self.assertIsNone(
            from_server_result(CONTEXT, result, client_instance_id=INSTANCE_ID)
        )

    def test_control_without_client_instance_id_yields_none(self):
        processor = EventProtocolProcessor(access())
        processor.begin_subscription()
        result = processed(processor, {"type": "log.error",
                                      "code": "not_authorized"})
        self.assertIsNone(from_server_result(CONTEXT, result))

    def test_hello_without_client_instance_id_yields_none(self):
        """Contributes the requirement from §3.2: CONTROL records need the
        client instance id (injected by the future adapter)."""
        processor = EventProtocolProcessor(access())
        processor.begin_subscription()
        result = processed(processor, hello())
        self.assertIsNone(from_server_result(CONTEXT, result))


if __name__ == "__main__":
    unittest.main()