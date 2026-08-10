"""Contract tests for the strict AP07 log protocol processor."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.event_cursor_store import EventCursorStore
from core.event_models import EventConnectionState, EventOrigin
from core.event_protocol import (
    EventProtocolError,
    EventProtocolIssue,
    EventProtocolProcessor,
    EventResultKind,
    EventStreamAccess,
)


ENDPOINT = "wss://stt.voice.marcosudau.com/ws/logs"


def access(**changes) -> EventStreamAccess:
    values = {
        "endpoint": ENDPOINT,
        "session_id": "session-1",
        "access_token": "session-secret-token",
        "server_instance_id": "server-1",
        "oldest_cursor": 0,
        "latest_cursor": 20,
        "channels": ("transcription",),
    }
    values.update(changes)
    return EventStreamAccess(**values)


def hello(**changes) -> dict:
    values = {
        "type": "log.hello",
        "schemaVersion": 1,
        "logProtocolVersion": 2,
        "deliveryMode": "sqlite_first",
        "replayAvailable": True,
        "serverInstanceId": "server-1",
        "oldestCursor": 0,
        "latestCursor": 20,
        "retentionCursor": 0,
    }
    values.update(changes)
    return values


def subscribed(after_cursor: int = 0, **changes) -> dict:
    values = {
        "type": "log.subscribed",
        "channels": ["transcription"],
        "sessionId": "session-1",
        "afterCursor": after_cursor,
        "authorizationScope": "session",
        "allChannels": False,
        "allSessions": False,
    }
    values.update(changes)
    return values


def envelope(cursor: int, event_id: str, event: str = "transcription.completed"):
    return {
        "schemaVersion": 1,
        "eventId": event_id,
        "cursor": cursor,
        "timestamp": "2026-08-09T12:00:00Z",
        "channel": "transcription",
        "event": event,
        "severity": "info",
        "serverInstanceId": "server-1",
        "sessionId": "session-1",
        "segmentId": 1,
        "data": {"reason": "done"},
    }


def event_message(cursor: int, event_id: str, *, replay: bool) -> dict:
    return {
        "type": "log.event",
        "event": envelope(cursor, event_id),
        "replay": replay,
    }


def enter_replay(processor: EventProtocolProcessor, after_cursor: int = 0) -> None:
    processor.begin_subscription()
    processor.process_mapping(hello())
    processor.process_mapping(subscribed(after_cursor))


class TestEventStreamAccess(unittest.TestCase):
    def test_token_is_only_exposed_in_subscribe_payload_not_repr_or_endpoint(self):
        item = access()
        payload = item.subscribe_payload(4)
        self.assertNotIn("session-secret-token", repr(item))
        self.assertNotIn("session-secret-token", item.endpoint)
        self.assertEqual(payload["accessToken"], "session-secret-token")
        self.assertEqual(payload["afterCursor"], 4)

    def test_access_rejects_admin_channels_and_incompatible_contracts(self):
        for changes in (
            {"channels": ("system",)},
            {"protocol_version": 1},
            {"delivery_mode": "best_effort"},
            {"replay_available": False},
            {"endpoint": "wss://user:secret@example.test/ws/logs"},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                access(**changes)


class TestEventProtocolProcessor(unittest.TestCase):
    def test_normal_replay_live_and_explicit_cursor_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            store = EventCursorStore(Path(directory) / "cursor.json")
            processor = EventProtocolProcessor(access(), cursor_store=store)
            enter_replay(processor)

            replay = processor.process_mapping(event_message(3, "evt-3", replay=True))
            self.assertEqual(replay.kind, EventResultKind.EVENT)
            self.assertEqual(replay.origin, EventOrigin.REPLAY)
            self.assertFalse(store.path.exists())
            processor.confirm_event(replay)
            self.assertTrue(store.path.exists())

            completed = processor.process_mapping(
                {"type": "log.replay_completed", "cursor": 20, "count": 1}
            )
            self.assertEqual(completed.connection_state, EventConnectionState.LIVE)
            live = processor.process_mapping(event_message(24, "evt-24", replay=False))
            self.assertEqual(live.origin, EventOrigin.LIVE)
            processor.confirm_event(live)
            self.assertEqual(processor.resume_cursor, 24)

    def test_persisted_cursor_can_be_newer_than_the_log_access_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            store = EventCursorStore(Path(directory) / "cursor.json")
            store.commit(
                24,
                endpoint=ENDPOINT,
                server_instance_id="server-1",
                protocol_version=2,
            )
            processor = EventProtocolProcessor(access(latest_cursor=20), cursor_store=store)
            self.assertEqual(processor.begin_subscription(), 24)

    def test_new_server_instance_starts_at_zero_without_destroying_old_record(self):
        with tempfile.TemporaryDirectory() as directory:
            store = EventCursorStore(Path(directory) / "cursor.json")
            old_record = store.commit(
                24,
                endpoint=ENDPOINT,
                server_instance_id="server-1",
                protocol_version=2,
            )
            processor = EventProtocolProcessor(
                access(server_instance_id="server-2", latest_cursor=2),
                cursor_store=store,
            )

            self.assertEqual(processor.begin_subscription(), 0)
            self.assertEqual(
                store.load(
                    endpoint=ENDPOINT,
                    server_instance_id="server-1",
                    protocol_version=2,
                ),
                old_record,
            )

    def test_global_filtered_cursor_jumps_are_valid(self):
        processor = EventProtocolProcessor(access())
        enter_replay(processor)
        first = processor.process_mapping(event_message(2, "evt-2", replay=True))
        processor.confirm_event(first)
        second = processor.process_mapping(event_message(17, "evt-17", replay=True))
        processor.confirm_event(second)
        self.assertEqual(processor.resume_cursor, 17)

    def test_duplicate_event_id_is_bounded_and_not_delivered_twice(self):
        processor = EventProtocolProcessor(access(), dedupe_limit=2)
        enter_replay(processor)
        first = processor.process_mapping(event_message(2, "evt-2", replay=True))
        processor.confirm_event(first)
        processor.begin_subscription()
        processor.process_mapping(hello())
        processor.process_mapping(subscribed(2))
        duplicate = processor.process_mapping(event_message(2, "evt-2", replay=True))
        self.assertTrue(duplicate.duplicate)

        for cursor in (3, 4):
            result = processor.process_mapping(
                event_message(cursor, f"evt-{cursor}", replay=True)
            )
            processor.confirm_event(result)
        self.assertEqual(len(processor._confirmed_ids), 2)

    def test_rejected_event_can_be_replayed_and_was_not_persisted(self):
        processor = EventProtocolProcessor(access())
        enter_replay(processor)
        result = processor.process_mapping(event_message(2, "evt-2", replay=True))
        processor.reject_event(result)
        processor.begin_subscription()
        processor.process_mapping(hello())
        processor.process_mapping(subscribed())
        retried = processor.process_mapping(event_message(2, "evt-2", replay=True))
        self.assertFalse(retried.duplicate)
        self.assertEqual(processor.resume_cursor, 0)

    def test_retention_gap_is_typed_without_forcing_a_cursor_jump(self):
        processor = EventProtocolProcessor(access())
        enter_replay(processor)
        result = processor.process_mapping({
            "type": "log.gap",
            "reason": "retention",
            "lostFromCursor": 1,
            "lostToCursor": 8,
            "oldestCursor": 2,
            "latestCursor": 20,
        })
        self.assertEqual(result.issue, EventProtocolIssue.RETENTION_GAP)
        self.assertEqual(processor.resume_cursor, 0)

    def test_documented_errors_are_translated_to_typed_issues(self):
        cases = (
            ({"type": "log.error", "code": "not_authorized"}, EventProtocolIssue.AUTHORIZATION),
            ({"type": "log.error", "code": "event_store_unavailable"}, EventProtocolIssue.STORE_UNAVAILABLE),
            ({"type": "log.error", "code": "log_live_disabled"}, EventProtocolIssue.LIVE_DISABLED),
            ({
                "type": "log.error",
                "code": "cursor_ahead",
                "latestCursor": 4,
                "serverInstanceId": "server-1",
            }, EventProtocolIssue.CURSOR_AHEAD),
        )
        for message, issue in cases:
            with self.subTest(issue=issue):
                processor = EventProtocolProcessor(access())
                processor.begin_subscription()
                result = processor.process_mapping(message)
                self.assertEqual(result.issue, issue)
                self.assertEqual(result.connection_state, EventConnectionState.DEGRADED)

    def test_wrong_handshake_contract_and_session_scope_are_rejected(self):
        invalid_hello = (
            hello(logProtocolVersion=1),
            hello(deliveryMode="best_effort"),
            hello(replayAvailable=False),
            hello(serverInstanceId="server-2"),
        )
        for message in invalid_hello:
            with self.subTest(message=message):
                processor = EventProtocolProcessor(access())
                processor.begin_subscription()
                with self.assertRaises(EventProtocolError):
                    processor.process_mapping(message)

        invalid_subscribed = (
            subscribed(sessionId="other"),
            subscribed(authorizationScope="admin"),
            subscribed(allSessions=True),
            subscribed(channels=["audit"]),
        )
        for message in invalid_subscribed:
            with self.subTest(message=message):
                processor = EventProtocolProcessor(access())
                processor.begin_subscription()
                processor.process_mapping(hello())
                with self.assertRaises(EventProtocolError):
                    processor.process_mapping(message)

    def test_out_of_order_replay_flags_and_backward_cursors_are_rejected(self):
        processor = EventProtocolProcessor(access())
        enter_replay(processor)
        for message in (
            event_message(1, "live-too-early", replay=False),
            {"type": "log.keepalive", "cursor": 0, "eventsSent": 0},
        ):
            with self.subTest(message=message), self.assertRaises(EventProtocolError):
                processor.process_mapping(message)

        first = processor.process_mapping(event_message(10, "evt-10", replay=True))
        processor.confirm_event(first)
        with self.assertRaises(EventProtocolError):
            processor.process_mapping(event_message(9, "evt-9", replay=True))

    def test_invalid_json_binary_and_unknown_message_types_are_rejected(self):
        processor = EventProtocolProcessor(access())
        processor.begin_subscription()
        for frame in (b"binary", "not json", "[]", json.dumps({"type": "log.future"})):
            with self.subTest(frame=frame), self.assertRaises(EventProtocolError):
                processor.process_frame(frame)

    def test_event_scope_and_envelope_fields_are_strict(self):
        processor = EventProtocolProcessor(access())
        enter_replay(processor)
        wrong_session = event_message(2, "evt-2", replay=True)
        wrong_session["event"]["sessionId"] = "other"
        with self.assertRaises(EventProtocolError):
            processor.process_mapping(wrong_session)

        missing_cursor = event_message(2, "evt-3", replay=True)
        del missing_cursor["event"]["cursor"]
        with self.assertRaises(EventProtocolError):
            processor.process_mapping(missing_cursor)

    def test_replay_watermark_and_live_controls_are_validated(self):
        processor = EventProtocolProcessor(access())
        enter_replay(processor)
        completed = processor.process_mapping(
            {"type": "log.replay_completed", "cursor": 20, "count": 0}
        )
        self.assertEqual(completed.kind, EventResultKind.REPLAY_COMPLETED)
        pong = processor.process_mapping(
            {"type": "log.pong", "cursor": 20, "serverTime": 1.5}
        )
        keepalive = processor.process_mapping(
            {"type": "log.keepalive", "cursor": 20, "eventsSent": 0}
        )
        self.assertEqual(pong.kind, EventResultKind.PONG)
        self.assertEqual(keepalive.kind, EventResultKind.KEEPALIVE)


if __name__ == "__main__":
    unittest.main()
