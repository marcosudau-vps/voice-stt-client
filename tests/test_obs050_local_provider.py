"""
OBS-050 — ``LocalLogProvider``: filters, keyset pagination, ordering,
``fetch_raw`` and the failure states.

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §5.4 (reader connections,
``PRAGMA query_only = ON``), §5.7 (keyset pagination, no ``raw_json`` in the
list query), §8 (``QueryFilter``/``QueryPage``/provider contract) and
``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` O-14 (the query layer never writes).
"""

from __future__ import annotations

import re
import sqlite3
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

from core.observability.models import CanonicalLogRecord
from core.observability.query.base import ProviderState, QueryFilter
from core.observability.query.local import (
    MAX_LIMIT,
    LocalLogProvider,
    decode_cursor,
    encode_cursor,
)
from core.observability.storage.sqlite import SQLiteLogStore


def make_record(**overrides) -> CanonicalLogRecord:
    values = dict(
        record_id=uuid4().hex,
        received_at="2026-08-17T10:00:00.000Z",
        producer_kind="client",
        producer_id="voice-stt-client",
        instance_id="instance-1",
        scope="instance",
        channel="system",
        level="INFO",
    )
    values.update(overrides)
    return CanonicalLogRecord(**values)


class ProviderTestCase(unittest.TestCase):
    """One temporary store per test, written through the real store."""

    def setUp(self) -> None:
        self._directory = tempfile.TemporaryDirectory()
        self.db_path = Path(self._directory.name) / "observability.sqlite3"
        self.store = SQLiteLogStore(self.db_path)
        result = self.store.open()
        self.assertTrue(result.ok, msg=result.detail)
        self.addCleanup(self._directory.cleanup)
        self.addCleanup(self.store.close)

    def write(self, records) -> None:
        self.store.write_batch(list(records))

    def provider(self) -> LocalLogProvider:
        return LocalLogProvider(self.db_path)


class TestCursorEncoding(unittest.TestCase):
    def test_cursor_roundtrip(self):
        self.assertEqual(decode_cursor(encode_cursor(42)), 42)

    def test_cursor_is_opaque_not_a_bare_number(self):
        """§8.1: the cursor is an opaque string; a caller must not be able to
        do arithmetic on it and get a meaningful result."""
        self.assertFalse(encode_cursor(7).isdigit())

    def test_foreign_cursor_is_rejected(self):
        for value in ("7", "", "afterCursor:7", "id:abc"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    decode_cursor(value)


class TestFilters(ProviderTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.write([
            make_record(channel="system", level="INFO", type="client.app.started",
                        component="ui.application", message="Anwendung gestartet"),
            make_record(channel="audit", level="WARNING", type="client.hotkey.pressed",
                        component="ui.hotkeys", message="Hotkey", session_id="s-1"),
            make_record(channel="transcription", level="ERROR",
                        type="client.injection.rejected", component="core.controller",
                        message="Injection abgelehnt", session_id="s-1", segment_id=3),
            make_record(channel="performance", level="DEBUG",
                        type="client.audio.stream_stats", component="core.audio_capture",
                        producer_kind="server", producer_id="voice-stt-server",
                        instance_id="server-1", scope="global",
                        activation_id="act-1", correlation_id="trigger:cmd-1"),
        ])

    def query(self, **filter_kwargs):
        return self.provider().query(QueryFilter(**filter_kwargs))

    def test_no_filter_returns_everything(self):
        page = self.query()
        self.assertEqual(len(page.records), 4)
        self.assertIs(page.status.state, ProviderState.AVAILABLE)
        self.assertTrue(page.complete)

    def test_channel_filter(self):
        page = self.query(channels=("audit",))
        self.assertEqual([r.channel for r in page.records], ["audit"])

    def test_level_filter_accepts_a_set_of_levels(self):
        page = self.query(levels=("WARNING", "ERROR", "CRITICAL"))
        self.assertEqual({r.level for r in page.records}, {"WARNING", "ERROR"})

    def test_producer_kind_filter(self):
        page = self.query(producer_kinds=("server",))
        self.assertEqual([r.producer_kind for r in page.records], ["server"])

    def test_scope_filter_expresses_the_admin_query(self):
        """§8.1/ARCH §10.3: ``scopes=("global",)`` *means* the later admin
        query and must already work against the local store."""
        page = self.query(scopes=("global",))
        self.assertEqual([r.scope for r in page.records], ["global"])

    def test_type_prefix_filter(self):
        page = self.query(type_prefix="client.injection")
        self.assertEqual([r.type for r in page.records], ["client.injection.rejected"])

    def test_context_filters_session_segment_activation_correlation(self):
        self.assertEqual(len(self.query(session_id="s-1").records), 2)
        self.assertEqual(len(self.query(segment_id=3).records), 1)
        self.assertEqual(len(self.query(activation_id="act-1").records), 1)
        self.assertEqual(len(self.query(correlation_id="trigger:cmd-1").records), 1)

    def test_text_filter_covers_message_type_and_component(self):
        self.assertEqual(len(self.query(text="abgelehnt").records), 1)   # message
        self.assertEqual(len(self.query(text="hotkey").records), 1)      # type/component
        self.assertEqual(len(self.query(text="ui.").records), 2)         # component

    def test_text_filter_escapes_like_wildcards(self):
        """A ``%`` typed into the free-text box must be a literal percent
        sign, not "match everything"."""
        page = self.query(text="%")
        self.assertEqual(len(page.records), 0)
        self.write([make_record(message="100% erledigt")])
        self.assertEqual(len(self.query(text="100%").records), 1)

    def test_underscore_in_text_is_literal(self):
        self.write([make_record(message="a_b")])
        self.assertEqual(len(self.query(text="a_b").records), 1)
        self.assertEqual(len(self.query(text="axb").records), 0)

    def test_time_range_since_is_inclusive_and_until_exclusive(self):
        self.write([
            make_record(received_at="2026-08-17T12:00:00.000Z", message="mittag"),
            make_record(received_at="2026-08-17T13:00:00.000Z", message="danach"),
        ])
        page = self.query(
            since="2026-08-17T12:00:00.000Z", until="2026-08-17T13:00:00.000Z"
        )
        self.assertEqual([r.message for r in page.records], ["mittag"])

    def test_include_replayed_false_hides_replayed_records(self):
        self.write([make_record(replayed=True, message="replay", event_id="e-1",
                                producer_id="voice-stt-server")])
        self.assertEqual(len(self.query(include_replayed=True).records), 5)
        self.assertEqual(len(self.query(include_replayed=False).records), 4)

    def test_empty_tuple_filters_mean_no_restriction(self):
        page = self.query(channels=(), levels=(), producer_kinds=())
        self.assertEqual(len(page.records), 4)

    def test_blank_values_in_a_tuple_do_not_match_nothing(self):
        """A tuple that only holds blanks must behave like an unset filter,
        not like "no channel is acceptable"."""
        page = self.query(channels=("", None))
        self.assertEqual(len(page.records), 4)

    def test_unknown_filter_values_return_an_empty_but_available_page(self):
        page = self.query(channels=("does-not-exist",))
        self.assertEqual(page.records, ())
        self.assertIs(page.status.state, ProviderState.AVAILABLE)
        self.assertIsNone(page.next_cursor)

    def test_combined_filters_are_conjunctive(self):
        page = self.query(session_id="s-1", levels=("ERROR",))
        self.assertEqual(len(page.records), 1)

    def test_details_are_decoded_but_raw_is_not_loaded(self):
        """§5.7: *"raw_json wird in der LISTENabfrage NICHT geladen"*."""
        self.write([make_record(details={"a": 1}, raw={"b": 2}, event_id="e-raw",
                                producer_id="voice-stt-server")])
        page = self.query(text=None, event_id="e-raw")
        self.assertEqual(len(page.records), 1)
        self.assertEqual(dict(page.records[0].details), {"a": 1})
        self.assertIsNone(page.records[0].raw)


class TestPaginationAndOrdering(ProviderTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.write([make_record(message=f"m{index:03d}") for index in range(25)])

    def test_descending_page_is_newest_first_and_deterministic(self):
        first = self.provider().query(QueryFilter(), limit=10)
        again = self.provider().query(QueryFilter(), limit=10)
        self.assertEqual(
            [r.message for r in first.records], [r.message for r in again.records]
        )
        self.assertEqual(first.records[0].message, "m024")
        self.assertEqual(first.records[-1].message, "m015")

    def test_ascending_order_is_the_live_tail_direction(self):
        page = self.provider().query(QueryFilter(newest_first=False), limit=5)
        self.assertEqual([r.message for r in page.records],
                         ["m000", "m001", "m002", "m003", "m004"])

    def test_keyset_pagination_walks_the_whole_result_without_gaps(self):
        provider = self.provider()
        seen = []
        cursor = None
        for _page_index in range(10):
            page = provider.query(QueryFilter(), cursor=cursor, limit=10)
            seen.extend(record.message for record in page.records)
            cursor = page.next_cursor
            if cursor is None:
                break
        self.assertEqual(len(seen), 25)
        self.assertEqual(len(set(seen)), 25)
        self.assertEqual(seen[0], "m024")
        self.assertEqual(seen[-1], "m000")

    def test_next_cursor_is_none_on_the_last_page(self):
        page = self.provider().query(QueryFilter(), limit=100)
        self.assertIsNone(page.next_cursor)

    def test_next_cursor_is_set_when_a_further_page_exists(self):
        page = self.provider().query(QueryFilter(), limit=10)
        self.assertIsNotNone(page.next_cursor)
        self.assertEqual(page.next_cursor, page.records[-1].cursor)

    def test_a_full_page_that_is_exactly_the_rest_reports_no_next_page(self):
        """The extra probe row is what makes this exact: 25 rows, page size
        25 must not offer an empty next page."""
        page = self.provider().query(QueryFilter(), limit=25)
        self.assertEqual(len(page.records), 25)
        self.assertIsNone(page.next_cursor)

    def test_rows_written_between_pages_do_not_shift_the_sequence(self):
        """§5.7's reason for keyset over OFFSET: *"Zwischen zwei
        Seitenabrufen schreibt der Worker weiter."*"""
        provider = self.provider()
        first = provider.query(QueryFilter(), limit=10)
        self.write([make_record(message=f"neu{index}") for index in range(5)])
        second = provider.query(QueryFilter(), cursor=first.next_cursor, limit=10)
        self.assertEqual([r.message for r in second.records],
                         [f"m{index:03d}" for index in range(14, 4, -1)])

    def test_live_tail_only_returns_rows_after_the_cursor(self):
        provider = self.provider()
        newest = provider.query(QueryFilter(), limit=1)
        cursor = newest.records[0].cursor
        self.assertEqual(provider.query(QueryFilter(newest_first=False),
                                        cursor=cursor, limit=500).records, ())
        self.write([make_record(message="live-1"), make_record(message="live-2")])
        tail = provider.query(QueryFilter(newest_first=False), cursor=cursor, limit=500)
        self.assertEqual([r.message for r in tail.records], ["live-1", "live-2"])

    def test_limit_is_capped_and_the_page_reports_it(self):
        page = self.provider().query(QueryFilter(), limit=MAX_LIMIT + 500)
        self.assertLessEqual(len(page.records), MAX_LIMIT)
        self.assertFalse(page.complete)

    def test_non_positive_limit_falls_back_to_the_default(self):
        page = self.provider().query(QueryFilter(), limit=0)
        self.assertEqual(len(page.records), 25)


class TestRawAndFailureStates(ProviderTestCase):
    def test_fetch_raw_returns_the_stored_payload(self):
        record = make_record(raw={"event": "x", "cursor": 5},
                             event_id="e-1", producer_id="voice-stt-server")
        self.write([record])
        raw = self.provider().fetch_raw(record.record_id)
        self.assertEqual(dict(raw), {"event": "x", "cursor": 5})

    def test_fetch_raw_returns_none_without_a_payload(self):
        record = make_record()
        self.write([record])
        self.assertIsNone(self.provider().fetch_raw(record.record_id))

    def test_fetch_raw_of_an_unknown_record_is_none_not_an_error(self):
        self.assertIsNone(self.provider().fetch_raw("does-not-exist"))

    def test_invalid_cursor_is_an_error_page_not_an_exception(self):
        page = self.provider().query(QueryFilter(), cursor="afterCursor:9")
        self.assertIs(page.status.state, ProviderState.ERROR)
        self.assertEqual(page.records, ())
        self.assertFalse(page.complete)

    def test_missing_database_is_unavailable_and_is_never_created(self):
        """O-14: a store file conjured up by the READER would be a write by
        the query layer."""
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "not-there.sqlite3"
            provider = LocalLogProvider(missing)
            page = provider.query(QueryFilter())
            self.assertIs(page.status.state, ProviderState.UNAVAILABLE)
            self.assertEqual(page.records, ())
            self.assertFalse(missing.exists())
            self.assertIsNone(provider.fetch_raw("x"))
            self.assertFalse(missing.exists())

    def test_no_db_path_means_unavailable(self):
        provider = LocalLogProvider(None)
        self.assertIs(provider.status().state, ProviderState.UNAVAILABLE)
        self.assertEqual(provider.query(QueryFilter()).records, ())

    def test_a_file_without_the_logs_table_is_unavailable_not_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.sqlite3"
            sqlite3.connect(str(path)).close()
            page = LocalLogProvider(path).query(QueryFilter())
            self.assertIs(page.status.state, ProviderState.UNAVAILABLE)

    def test_a_corrupt_file_is_an_error_page_not_an_exception(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corrupt.sqlite3"
            path.write_bytes(b"this is not a database" * 100)
            page = LocalLogProvider(path).query(QueryFilter())
            self.assertIs(page.status.state, ProviderState.ERROR)
            self.assertEqual(page.records, ())

    def test_status_is_cached_and_needs_no_io(self):
        """§8: *"Muss OHNE Netz- oder DB-Zugriff antworten koennen
        (gecacht)"* — proven by deleting the file and asking again."""
        self.write([make_record()])
        provider = self.provider()
        provider.query(QueryFilter())
        self.store.close()
        self.db_path.unlink()
        self.assertIs(provider.status().state, ProviderState.AVAILABLE)


class TestReadOnlyConnection(ProviderTestCase):
    def test_reader_connection_is_query_only(self):
        """§5.4: ``PRAGMA query_only = ON`` instead of ``mode=ro`` (W-13).
        The pragma is verified on the provider's own connection."""
        self.write([make_record()])
        provider = self.provider()
        connection = provider._connect()  # noqa: SLF001 - contract under test
        try:
            self.assertEqual(
                connection.execute("PRAGMA query_only").fetchone()[0], 1
            )
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute("DELETE FROM logs")
        finally:
            connection.close()

    def test_query_does_not_leave_a_connection_open(self):
        """§13's antipattern list names the leaking connection explicitly.
        A leaked handle would keep the file locked on Windows — deleting it
        right after the query is the observable proof that none is left."""
        self.write([make_record()])
        provider = self.provider()
        provider.query(QueryFilter())
        provider.fetch_raw("x")
        self.store.close()
        self.db_path.unlink()
        self.assertFalse(self.db_path.exists())

    def test_no_write_statement_appears_in_the_query_modules(self):
        """O-14 read as source: the query layer contains no write SQL.

        Matched as SQL statements rather than as bare words, so that prose in
        a docstring ("drop empty entries") is not mistaken for a ``DROP``.
        """
        pattern = re.compile(
            r"\b(INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|DROP\s+(TABLE|INDEX)"
            r"|CREATE\s+(TABLE|INDEX|UNIQUE)|PRAGMA\s+\w*VACUUM)",
            re.IGNORECASE,
        )
        root = Path(__file__).resolve().parents[1] / "core" / "observability" / "query"
        for name in ("base.py", "local.py", "service.py"):
            text = (root / name).read_text(encoding="utf-8")
            with self.subTest(module=name):
                self.assertIsNone(pattern.search(text))


if __name__ == "__main__":
    unittest.main()
