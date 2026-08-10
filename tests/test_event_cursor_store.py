"""Tests for atomic and binding-aware AP07 cursor persistence."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.event_cursor_store import EventCursorStore, normalize_endpoint


ENDPOINT = "wss://stt.voice.marcosudau.com/ws/logs"


class TestEventCursorStore(unittest.TestCase):
    def test_commit_and_load_are_bound_to_endpoint_instance_and_protocol(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cursor.json"
            store = EventCursorStore(path)
            stored = store.commit(
                42,
                endpoint=ENDPOINT,
                server_instance_id="server-1",
                protocol_version=2,
            )
            loaded = store.load(
                endpoint=ENDPOINT,
                server_instance_id="server-1",
                protocol_version=2,
                latest_cursor=50,
            )
            self.assertEqual(loaded, stored)
            self.assertIsNone(
                store.load(
                    endpoint=ENDPOINT,
                    server_instance_id="server-2",
                    protocol_version=2,
                )
            )
            self.assertIsNone(
                store.load(
                    endpoint=ENDPOINT,
                    server_instance_id="server-1",
                    protocol_version=3,
                )
            )

    def test_corrupt_unknown_negative_and_ahead_cursors_are_ignored(self):
        cases = (
            "not json",
            json.dumps({"schema_version": 99}),
            json.dumps({
                "schema_version": 1,
                "endpoint": ENDPOINT,
                "server_instance_id": "server-1",
                "protocol_version": 2,
                "cursor": -1,
                "updated_at": "now",
            }),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cursor.json"
            store = EventCursorStore(path)
            for content in cases:
                with self.subTest(content=content):
                    path.write_text(content, encoding="utf-8")
                    self.assertIsNone(
                        store.load(
                            endpoint=ENDPOINT,
                            server_instance_id="server-1",
                            protocol_version=2,
                        )
                    )
            store.commit(
                100,
                endpoint=ENDPOINT,
                server_instance_id="server-1",
                protocol_version=2,
            )
            self.assertIsNone(
                store.load(
                    endpoint=ENDPOINT,
                    server_instance_id="server-1",
                    protocol_version=2,
                    latest_cursor=99,
                )
            )

    def test_failed_replace_preserves_previous_cursor_and_cleans_temp_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "cursor.json"
            store = EventCursorStore(path)
            store.commit(
                1,
                endpoint=ENDPOINT,
                server_instance_id="server-1",
                protocol_version=2,
            )
            previous = path.read_text(encoding="utf-8")
            with patch("core.event_cursor_store.os.replace", side_effect=OSError("disk")):
                with self.assertRaises(OSError):
                    store.commit(
                        2,
                        endpoint=ENDPOINT,
                        server_instance_id="server-1",
                        protocol_version=2,
                    )
            self.assertEqual(path.read_text(encoding="utf-8"), previous)
            self.assertFalse(any(root.glob(".cursor.json.*.tmp")))

    def test_endpoint_rejects_credentials_query_and_non_websocket_schemes(self):
        self.assertEqual(normalize_endpoint(ENDPOINT), ENDPOINT)
        for value in (
            "https://example.test/ws/logs",
            "wss://user:secret@example.test/ws/logs",
            "wss://example.test/ws/logs?token=secret",
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_endpoint(value)


if __name__ == "__main__":
    unittest.main()
