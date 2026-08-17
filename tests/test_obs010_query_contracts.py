"""
Contract tests for ``core.observability.query`` (OBS-010).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §8.
"""

from __future__ import annotations

import unittest

from core.observability.query.base import (
    LogProvider,
    LogRecordView,
    ProviderState,
    ProviderStatus,
    QueryFilter,
    QueryPage,
)


class TestProviderState(unittest.TestCase):
    def test_state_values_match_contract(self):
        self.assertEqual(ProviderState.AVAILABLE.value, "available")
        self.assertEqual(ProviderState.AUTH_REQUIRED.value, "auth_required")
        self.assertEqual(ProviderState.UNAVAILABLE.value, "unavailable")
        self.assertEqual(ProviderState.ERROR.value, "error")


class TestProviderStatus(unittest.TestCase):
    def test_status_fields_and_defaults(self):
        status = ProviderStatus(
            provider_id="local", display_name="Lokal", state=ProviderState.AVAILABLE
        )
        self.assertEqual(status.detail, "")
        self.assertEqual(status.provider_id, "local")

    def test_status_is_frozen(self):
        status = ProviderStatus(
            provider_id="local", display_name="Lokal",
            state=ProviderState.AVAILABLE,
        )
        with self.assertRaises(AttributeError):
            status.state = ProviderState.ERROR


class TestQueryFilter(unittest.TestCase):
    def test_defaults_are_declarative_and_open(self):
        filter = QueryFilter()
        self.assertEqual(filter.channels, ())
        self.assertEqual(filter.levels, ())
        self.assertIsNone(filter.session_id)
        self.assertTrue(filter.include_replayed)
        self.assertTrue(filter.newest_first)

    def test_filter_is_frozen_and_never_mutated(self):
        filter = QueryFilter(channels=("audit",), levels=("INFO",))
        with self.assertRaises(AttributeError):
            filter.channels = ("system",)
        self.assertEqual(tuple(filter.channels), ("audit",))


class TestLogRecordView(unittest.TestCase):
    def test_required_fields_and_defaults(self):
        view = LogRecordView(
            provider_id="local",
            record_id="r" * 32,
            received_at="2026-08-17T00:00:00.000Z",
            source_timestamp=None,
            producer_kind="client",
            producer_id="voice-stt-client",
            instance_id="i" * 32,
            scope="instance",
            channel="system",
            level="INFO",
            type=None,
            component=None,
            session_id=None,
            generation=None,
            activation_id=None,
            segment_id=None,
            transcription_id=None,
            command_id=None,
            event_id=None,
            correlation_id=None,
            server_cursor=None,
            replayed=False,
            message=None,
        )
        self.assertEqual(view.details, {})
        self.assertIsNone(view.raw)
        self.assertEqual(view.cursor, "")
        with self.assertRaises(AttributeError):
            view.message = "changed"


class TestQueryPageAndProvider(unittest.TestCase):
    def test_page_defaults_and_frozen(self):
        status = ProviderStatus(
            provider_id="local", display_name="Lokal",
            state=ProviderState.AVAILABLE,
        )
        page = QueryPage(
            provider_id="local", records=(), next_cursor=None,
            complete=True, status=status,
        )
        self.assertIsNone(page.next_cursor)
        self.assertTrue(page.complete)

    def test_log_provider_protocol_members(self):
        members = {name for name in LogProvider.__dict__ if not name.startswith("_")}
        # runtime protocol exposes the abstract members
        required = {"query", "fetch_raw", "status", "provider_id"}
        self.assertTrue(required.issubset(members))


if __name__ == "__main__":
    unittest.main()