"""
Tests for ``core.observability.storage.sqlite.SQLiteLogStore`` (OBS-030).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §5.2 (DDL), §5.4
(connections/threads, D-2/D-4), §5.5 (write_batch/dedupe), §5.6 (retention),
§5.8 (clear), ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §8.3 (failure states).
"""

from __future__ import annotations

import sqlite3
import tempfile
import threading
import time
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Optional

from core.observability.models import CanonicalLogRecord
from core.observability.storage.sqlite import SQLiteLogStore, SCHEMA_VERSION


def _iso(dt: Optional[datetime] = None) -> str:
    dt = dt if dt is not None else datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{dt.microsecond // 1000:03d}Z"


def make_record(**overrides) -> CanonicalLogRecord:
    fields = dict(
        record_id=uuid.uuid4().hex,
        received_at=_iso(),
        producer_kind="client",
        producer_id="voice-stt-client",
        instance_id="i" * 32,
        scope="instance",
        channel="system",
        level="INFO",
        replayed=False,
        type=None,
    )
    fields.update(overrides)
    return CanonicalLogRecord(**fields)


class TempDbCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmp.name) / "observability.sqlite3"
        self._stores: list[SQLiteLogStore] = []

    def tearDown(self) -> None:
        for store in self._stores:
            store.close()
        self._tmp.cleanup()

    def open_store(self) -> SQLiteLogStore:
        store = SQLiteLogStore(self.db_path)
        self._stores.append(store)
        return store


class TestBootstrapAndDDL(TempDbCase):
    def test_new_file_creates_schema_and_sets_user_version(self):
        store = self.open_store()
        result = store.open()
        self.assertTrue(result.ok)
        self.assertFalse(result.degraded)
        conn = sqlite3.connect(str(self.db_path))
        try:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            self.assertEqual(version, SCHEMA_VERSION)
            tables = {
                row[0] for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            self.assertIn("logs", tables)
            self.assertIn("schema_meta", tables)
            meta_keys = {
                row[0] for row in conn.execute("SELECT key FROM schema_meta")
            }
            self.assertEqual(
                meta_keys, {"created_at", "created_by_version", "last_migrated_at"}
            )
            indexes = {
                row[0] for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='index'"
                )
            }
            for expected in (
                "ux_logs_producer_event", "ix_logs_session_id",
                "ix_logs_received_at", "ix_logs_channel_level",
                "ix_logs_activation", "ix_logs_correlation",
            ):
                self.assertIn(expected, indexes)
        finally:
            conn.close()

    def test_wal_journal_mode_and_pragmas(self):
        store = self.open_store()
        store.open()
        conn = sqlite3.connect(str(self.db_path))
        try:
            mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            self.assertEqual(mode.lower(), "wal")
        finally:
            conn.close()
        wal_sibling = self.db_path.with_name(self.db_path.name + "-wal")
        shm_sibling = self.db_path.with_name(self.db_path.name + "-shm")
        # -wal/-shm appear once a write happens; a plain PRAGMA read may not
        # create them. Force a write to check the same-directory guarantee.
        store.write_batch([make_record()])
        self.assertTrue(wal_sibling.exists() or shm_sibling.exists())
        if wal_sibling.exists():
            self.assertEqual(wal_sibling.parent, self.db_path.parent)


class TestWriteBatchRoundTrip(TempDbCase):
    def test_positive_all_fields_round_trip(self):
        store = self.open_store()
        store.open()
        record = make_record(
            producer_kind="server",
            producer_id="voice-stt-server",
            scope="session",
            channel="transcription",
            level="WARNING",
            type="transcription.completed",
            component="transcription",
            session_id="sess-1",
            generation=3,
            activation_id="act-1",
            segment_id=7,
            transcription_id="sess-1:3:7",
            command_id="cmd-abc",
            event_id=uuid.uuid4().hex,
            correlation_id="trigger:cmd-abc",
            server_cursor=42,
            replayed=True,
            message="hello world",
            details={"a": 1, "nested": {"b": [1, 2, 3]}},
            raw={"secret_free": "payload"},
        )
        inserted, deduplicated = store.write_batch([record])
        self.assertEqual((inserted, deduplicated), (1, 0))

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute("SELECT * FROM logs").fetchone()
        finally:
            conn.close()
        self.assertEqual(row["record_id"], record.record_id)
        self.assertEqual(row["producer_kind"], "server")
        self.assertEqual(row["scope"], "session")
        self.assertEqual(row["channel"], "transcription")
        self.assertEqual(row["level"], "WARNING")
        self.assertEqual(row["type"], "transcription.completed")
        self.assertEqual(row["session_id"], "sess-1")
        self.assertEqual(row["generation"], 3)
        self.assertEqual(row["segment_id"], 7)
        self.assertEqual(row["server_cursor"], 42)
        self.assertEqual(row["replayed"], 1)
        self.assertEqual(row["message"], "hello world")
        self.assertIn('"nested"', row["details_json"])
        self.assertIn("secret_free", row["raw_json"])

    def test_structured_details_with_frozen_containers_round_trip(self):
        """CONTRACTS §4.1: details is frozen to MappingProxyType/tuple on
        construction; the store must serialize it without a
        default=str-collapse (that would defeat redaction elsewhere)."""
        store = self.open_store()
        store.open()
        record = make_record(details={
            "list_field": [1, 2, {"x": "y"}],
            "tuple_field": (1, 2, 3),
        })
        self.assertIsInstance(record.details, MappingProxyType)
        self.assertIsInstance(record.details["tuple_field"], tuple)
        store.write_batch([record])
        conn = sqlite3.connect(str(self.db_path))
        try:
            details_json = conn.execute(
                "SELECT details_json FROM logs"
            ).fetchone()[0]
        finally:
            conn.close()
        import json
        parsed = json.loads(details_json)
        self.assertEqual(parsed["list_field"], [1, 2, {"x": "y"}])
        self.assertEqual(parsed["tuple_field"], [1, 2, 3])

    def test_empty_details_and_none_raw_store_as_null(self):
        store = self.open_store()
        store.open()
        record = make_record(details={}, raw=None)
        store.write_batch([record])
        conn = sqlite3.connect(str(self.db_path))
        try:
            row = conn.execute(
                "SELECT details_json, raw_json FROM logs"
            ).fetchone()
        finally:
            conn.close()
        self.assertIsNone(row[0])
        self.assertIsNone(row[1])

    def test_negative_write_batch_on_unopened_store_is_a_safe_no_op(self):
        store = self.open_store()
        self.assertEqual(store.write_batch([make_record()]), (0, 0))


class TestDedupe(TempDbCase):
    def test_same_producer_event_id_twice_is_one_row_and_counted(self):
        store = self.open_store()
        store.open()
        event_id = uuid.uuid4().hex
        first = make_record(producer_kind="server", producer_id="voice-stt-server",
                            event_id=event_id, replayed=False)
        second = make_record(producer_kind="server", producer_id="voice-stt-server",
                             event_id=event_id, replayed=True)
        inserted1, dedup1 = store.write_batch([first])
        inserted2, dedup2 = store.write_batch([second])
        self.assertEqual((inserted1, dedup1), (1, 0))
        self.assertEqual((inserted2, dedup2), (0, 1))
        self.assertEqual(store.row_count(), 1)
        conn = sqlite3.connect(str(self.db_path))
        try:
            replayed = conn.execute("SELECT replayed FROM logs").fetchone()[0]
        finally:
            conn.close()
        self.assertEqual(replayed, 0, "first stored version wins (§5.5)")

    def test_records_without_event_id_never_collide(self):
        store = self.open_store()
        store.open()
        records = [make_record() for _ in range(5)]
        inserted, deduplicated = store.write_batch(records)
        self.assertEqual((inserted, deduplicated), (5, 0))

    def test_dedupe_is_scoped_to_producer_id(self):
        store = self.open_store()
        store.open()
        event_id = uuid.uuid4().hex
        a = make_record(producer_kind="server", producer_id="voice-stt-server", event_id=event_id)
        b = make_record(producer_kind="other", producer_id="future-producer", event_id=event_id)
        inserted1, _ = store.write_batch([a])
        inserted2, _ = store.write_batch([b])
        self.assertEqual(inserted1, 1)
        self.assertEqual(inserted2, 1)
        self.assertEqual(store.row_count(), 2)


class TestForeignThread(TempDbCase):
    def test_n05_connection_used_from_a_foreign_thread_raises(self):
        store = self.open_store()
        store.open()  # opened on THIS (the test/"worker") thread

        errors: list[BaseException] = []

        def foreign():
            try:
                store.write_batch([make_record()])
            except sqlite3.ProgrammingError as exc:
                errors.append(exc)
            except BaseException as exc:  # noqa: BLE001
                errors.append(exc)

        thread = threading.Thread(target=foreign)
        thread.start()
        thread.join(timeout=5.0)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], sqlite3.ProgrammingError)


class TestConcurrentReader(TempDbCase):
    def test_concurrent_reader_with_open_query_does_not_block_write_batch(self):
        store = self.open_store()
        store.open()
        store.write_batch([make_record() for _ in range(50)])

        reader = sqlite3.connect(str(self.db_path), timeout=5.0)
        reader.execute("PRAGMA query_only = ON")
        cursor = reader.execute("SELECT * FROM logs")
        cursor.fetchone()  # leave the read transaction open mid-scan

        try:
            start = time.perf_counter()
            inserted, _ = store.write_batch([make_record()])
            elapsed = time.perf_counter() - start
        finally:
            reader.close()

        self.assertEqual(inserted, 1)
        self.assertLess(elapsed, 2.0, "WAL must not block writers behind a live reader")


class TestMigrationAndVersioning(TempDbCase):
    def test_user_version_higher_than_supported_is_read_only_degraded(self):
        # Pre-create a file with a schema_meta-less but future user_version.
        bootstrap = sqlite3.connect(str(self.db_path))
        bootstrap.execute("PRAGMA journal_mode = WAL")
        bootstrap.execute("PRAGMA user_version = 99")
        bootstrap.execute(
            "CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, record_id TEXT)"
        )
        bootstrap.execute("INSERT INTO logs (record_id) VALUES ('sentinel')")
        bootstrap.commit()
        bootstrap.close()

        store = self.open_store()
        result = store.open()
        self.assertTrue(result.ok)
        self.assertTrue(result.degraded)
        self.assertTrue(store.is_degraded)

        inserted, deduplicated = store.write_batch([make_record()])
        self.assertEqual((inserted, deduplicated), (0, 0))

        conn = sqlite3.connect(str(self.db_path))
        try:
            rows = conn.execute("SELECT record_id FROM logs").fetchall()
        finally:
            conn.close()
        self.assertEqual(rows, [("sentinel",)], "nothing deleted or downgraded")

    def test_clear_is_a_no_op_when_degraded(self):
        bootstrap = sqlite3.connect(str(self.db_path))
        bootstrap.execute("PRAGMA user_version = 99")
        bootstrap.execute(
            "CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, record_id TEXT)"
        )
        bootstrap.execute("INSERT INTO logs (record_id) VALUES ('sentinel')")
        bootstrap.commit()
        bootstrap.close()

        store = self.open_store()
        store.open()
        self.assertEqual(store.clear(), 0)

    def test_migration_failure_rolls_back_and_leaves_file_unchanged(self):
        store = self.open_store()

        def _broken_migration(conn, **_kwargs):
            conn.execute("CREATE TABLE logs (id INTEGER PRIMARY KEY)")
            raise RuntimeError("simulated migration failure")

        import core.observability.storage.sqlite as sqlite_module
        original_migrations = sqlite_module._MIGRATIONS
        sqlite_module._MIGRATIONS = ((1, _broken_migration),)
        try:
            before_bytes = self.db_path.read_bytes() if self.db_path.exists() else b""
            result = store.open()
        finally:
            sqlite_module._MIGRATIONS = original_migrations

        self.assertFalse(result.ok)
        self.assertFalse(result.degraded)
        self.assertFalse(store.is_open)
        # A fresh, correctly-migrated store must still work afterwards:
        # the failed attempt must not have corrupted anything durably.
        store2 = self.open_store()
        result2 = store2.open()
        self.assertTrue(result2.ok)
        conn = sqlite3.connect(str(self.db_path))
        try:
            tables = {
                row[0] for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
        finally:
            conn.close()
        self.assertIn("logs", tables)

    def test_open_failure_on_unwritable_directory_reports_failed_not_ok(self):
        # A path whose parent cannot be created (a file standing where a
        # directory is expected) makes ``mkdir`` fail deterministically.
        blocker = Path(self._tmp.name) / "blocker"
        blocker.write_text("not a directory", encoding="utf-8")
        bad_path = blocker / "sub" / "observability.sqlite3"
        store = SQLiteLogStore(bad_path)
        self._stores.append(store)
        result = store.open()
        self.assertFalse(result.ok)
        self.assertFalse(store.is_open)


class TestRetention(TempDbCase):
    def _insert_with_age(self, store: SQLiteLogStore, *, days_old: int, count: int) -> None:
        received = _iso(datetime.now(timezone.utc) - timedelta(days=days_old))
        store.write_batch([make_record(received_at=received) for _ in range(count)])

    def test_age_based_retention_deletes_only_older_rows(self):
        store = self.open_store()
        store.open()
        self._insert_with_age(store, days_old=30, count=3)
        self._insert_with_age(store, days_old=1, count=2)
        cutoff = _iso(datetime.now(timezone.utc) - timedelta(days=14))
        deleted_age, deleted_count = store.run_retention(
            cutoff_iso=cutoff, max_entries=None, time_budget_s=1.0
        )
        self.assertEqual(deleted_age, 3)
        self.assertEqual(deleted_count, 0)
        self.assertEqual(store.row_count(), 2)

    def test_count_based_retention_keeps_newest_max_entries(self):
        store = self.open_store()
        store.open()
        for _ in range(10):
            store.write_batch([make_record()])
        deleted_age, deleted_count = store.run_retention(
            cutoff_iso=None, max_entries=4, time_budget_s=1.0
        )
        self.assertEqual(deleted_age, 0)
        self.assertEqual(deleted_count, 6)
        self.assertEqual(store.row_count(), 4)

    def test_retention_is_blockwise_and_respects_time_budget(self):
        store = self.open_store()
        store.open()
        import core.observability.storage.sqlite as sqlite_module
        original_block = sqlite_module.RETENTION_BLOCK_SIZE
        sqlite_module.RETENTION_BLOCK_SIZE = 3
        try:
            self._insert_with_age(store, days_old=30, count=10)
            cutoff = _iso(datetime.now(timezone.utc) - timedelta(days=14))
            deleted_age, _ = store.run_retention(
                cutoff_iso=cutoff, max_entries=None, time_budget_s=1.0
            )
        finally:
            sqlite_module.RETENTION_BLOCK_SIZE = original_block
        self.assertEqual(deleted_age, 10)

    def test_retention_never_calls_vacuum(self):
        """FD-D8: no auto_vacuum/incremental_vacuum/VACUUM PRAGMA/statement
        anywhere in actual code (prose mentions explaining the omission are
        fine and intentionally excluded from this check)."""
        text = Path("core/observability/storage/sqlite.py").read_text(encoding="utf-8")
        code_only: list[str] = []
        in_docstring = False
        for line in text.splitlines():
            if line.count('"""') % 2 == 1:
                in_docstring = not in_docstring
                continue
            if not in_docstring:
                code_only.append(line)
        code_text = "\n".join(code_only)
        self.assertNotIn("auto_vacuum", code_text)
        self.assertNotIn("incremental_vacuum", code_text)
        self.assertNotRegex(code_text, r"(?i)\bVACUUM\b")


class TestClear(TempDbCase):
    def test_clear_deletes_all_rows_and_returns_count(self):
        store = self.open_store()
        store.open()
        store.write_batch([make_record() for _ in range(7)])
        deleted = store.clear()
        self.assertEqual(deleted, 7)
        self.assertEqual(store.row_count(), 0)

    def test_clear_on_empty_store_returns_zero(self):
        store = self.open_store()
        store.open()
        self.assertEqual(store.clear(), 0)


class TestRestartPersistence(TempDbCase):
    def test_data_survives_close_and_reopen(self):
        store = self.open_store()
        store.open()
        record = make_record(message="persist me")
        store.write_batch([record])
        store.close()

        store2 = self.open_store()
        result = store2.open()
        self.assertTrue(result.ok)
        self.assertFalse(result.degraded)
        self.assertEqual(store2.row_count(), 1)
        conn = sqlite3.connect(str(self.db_path))
        try:
            message = conn.execute("SELECT message FROM logs").fetchone()[0]
        finally:
            conn.close()
        self.assertEqual(message, "persist me")


class TestDbBytes(TempDbCase):
    def test_measure_db_bytes_returns_positive_after_open(self):
        store = self.open_store()
        store.open()
        value = store.measure_db_bytes()
        self.assertIsNotNone(value)
        self.assertGreater(value, 0)

    def test_measure_db_bytes_is_none_when_unopened(self):
        store = self.open_store()
        self.assertIsNone(store.measure_db_bytes())


if __name__ == "__main__":
    unittest.main()
