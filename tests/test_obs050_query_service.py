"""
OBS-050 — ``LogQueryService``: the registry the UI talks to.

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §8 (four methods) and
``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §10.3 (*"LogQueryService ist eine
REGISTRY, keine fest verdrahtete Liste"*).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.observability.query.base import (
    ProviderState,
    ProviderStatus,
    QueryFilter,
    QueryPage,
)
from core.observability.query.local import LocalLogProvider
from core.observability.query.service import LogQueryService


class FakeProvider:
    def __init__(self, provider_id="fake", state=ProviderState.AVAILABLE, records=()):
        self._provider_id = provider_id
        self._state = state
        self._records = tuple(records)
        self.calls = []

    @property
    def provider_id(self):
        return self._provider_id

    def status(self):
        return ProviderStatus(self._provider_id, self._provider_id, self._state, "")

    def query(self, filter, cursor=None, limit=200):  # noqa: A002
        self.calls.append((filter, cursor, limit))
        return QueryPage(self._provider_id, self._records, None, True, self.status())

    def fetch_raw(self, record_id):
        return {"record_id": record_id}


class BrokenProvider(FakeProvider):
    """A provider that breaks its own contract in every method."""

    def status(self):
        raise RuntimeError("status exploded")

    def query(self, filter, cursor=None, limit=200):  # noqa: A002
        raise RuntimeError("query exploded")

    def fetch_raw(self, record_id):
        raise RuntimeError("fetch_raw exploded")


class TestRegistry(unittest.TestCase):
    def test_register_and_list_in_registration_order(self):
        service = LogQueryService()
        service.register(FakeProvider("local"))
        service.register(FakeProvider("remote"))
        self.assertEqual(service.provider_ids(), ("local", "remote"))
        self.assertEqual(
            [status.provider_id for status in service.providers()],
            ["local", "remote"],
        )

    def test_re_registering_the_same_id_replaces_it(self):
        service = LogQueryService()
        first, second = FakeProvider("local"), FakeProvider("local")
        service.register(first)
        service.register(second)
        service.query("local", QueryFilter())
        self.assertEqual(len(first.calls), 0)
        self.assertEqual(len(second.calls), 1)

    def test_a_provider_without_an_id_is_rejected(self):
        with self.assertRaises(ValueError):
            LogQueryService().register(FakeProvider(""))

    def test_unregister(self):
        service = LogQueryService()
        service.register(FakeProvider("local"))
        service.unregister("local")
        self.assertEqual(service.provider_ids(), ())

    def test_arguments_reach_the_provider_unchanged(self):
        service = LogQueryService()
        provider = FakeProvider("local")
        service.register(provider)
        query_filter = QueryFilter(channels=("audit",))
        service.query("local", query_filter, "id:5", 42)
        self.assertEqual(provider.calls, [(query_filter, "id:5", 42)])


class TestFailureIsolation(unittest.TestCase):
    def test_unknown_provider_is_an_unavailable_page_not_an_exception(self):
        page = LogQueryService().query("nope", QueryFilter())
        self.assertIs(page.status.state, ProviderState.UNAVAILABLE)
        self.assertEqual(page.records, ())
        self.assertFalse(page.complete)

    def test_unknown_provider_fetch_raw_is_none(self):
        self.assertIsNone(LogQueryService().fetch_raw("nope", "record"))

    def test_a_raising_provider_never_reaches_the_caller(self):
        """O-05: the logging failure domain ends at this boundary — the Qt
        thread is on the other side of it."""
        service = LogQueryService()
        service.register(BrokenProvider("broken"))
        page = service.query("broken", QueryFilter())
        self.assertIs(page.status.state, ProviderState.ERROR)
        self.assertIn("RuntimeError", page.status.detail)
        self.assertIsNone(service.fetch_raw("broken", "record"))
        statuses = service.providers()
        self.assertIs(statuses[0].state, ProviderState.ERROR)

    def test_one_broken_provider_does_not_hide_a_healthy_one(self):
        service = LogQueryService()
        service.register(BrokenProvider("broken"))
        service.register(FakeProvider("local"))
        states = {status.provider_id: status.state for status in service.providers()}
        self.assertIs(states["broken"], ProviderState.ERROR)
        self.assertIs(states["local"], ProviderState.AVAILABLE)


class TestWithTheRealLocalProvider(unittest.TestCase):
    def test_service_answers_through_the_local_provider(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "observability.sqlite3"
            service = LogQueryService()
            service.register(LocalLogProvider(path))
            page = service.query("local", QueryFilter())
            # No file yet: unavailable, not an error, and still no file.
            self.assertIs(page.status.state, ProviderState.UNAVAILABLE)
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
