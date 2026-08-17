"""
Tests for ``core.observability.manager.ObservabilityManager`` (OBS-030).

Frozen source: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §6.2 (lifecycle),
``LOGGING_DECISIONS_FREEZE_V1.md`` FD-R4/OD-22.
"""

from __future__ import annotations

import tempfile
import threading
import time
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path

from core.config import LoggingObservabilityConfig
from core.observability.manager import ObservabilityManager
from core.observability.models import CanonicalLogRecord
from core.observability.storage.sqlite import SQLiteLogStore


def _iso() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond // 1000:03d}Z"


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


class ManagerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._threads_before = {t.ident for t in threading.enumerate()}
        self._managers: list[ObservabilityManager] = []
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        for manager in self._managers:
            manager.stop(2.0)
        self._tmp.cleanup()
        after = {t.ident for t in threading.enumerate()}
        self.assertTrue(after.issubset(self._threads_before), "manager left a thread running")

    def build(self, **overrides) -> ObservabilityManager:
        overrides.setdefault("db_path", str(Path(self._tmp.name) / "obs.sqlite3"))
        overrides.setdefault("batch_size", 10)
        overrides.setdefault("flush_interval_s", 0.05)
        config = LoggingObservabilityConfig(**overrides)
        manager = ObservabilityManager(config, log_dir=self._tmp.name)
        self._managers.append(manager)
        return manager


class TestLifecycle(ManagerTestCase):
    def test_start_and_stop_leave_no_thread_behind(self):
        manager = self.build()
        manager.start()
        time.sleep(0.1)
        stopped = manager.stop(2.0)
        self.assertTrue(stopped)

    def test_submitted_record_ends_up_in_sqlite(self):
        manager = self.build()
        manager.start()
        record = make_record(message="via manager")
        self.assertTrue(manager.ingress.submit(record))
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and manager.health.snapshot().written < 1:
            time.sleep(0.02)
        manager.stop(2.0)

        store = SQLiteLogStore(Path(self._tmp.name) / "obs.sqlite3")
        store.open()
        try:
            self.assertEqual(store.row_count(), 1)
        finally:
            store.close()

    def test_disabled_manager_uses_null_ingress_and_no_worker_thread(self):
        manager = self.build(enabled=False)
        manager.start()  # must be a safe no-op
        self.assertFalse(manager.ingress.submit(make_record()))
        stopped = manager.stop(2.0)
        self.assertTrue(stopped)

    def test_store_disabled_still_runs_worker_for_the_sink(self):
        manager = self.build(store_enabled=False, file_sink_enabled=True)
        manager.start()
        record = make_record(message="sink only")
        self.assertTrue(manager.ingress.submit(record))
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and manager.health.snapshot().written < 1:
            time.sleep(0.02)
        manager.stop(2.0)
        sink_dir = Path(self._tmp.name) / "observability"
        files = list(sink_dir.glob("*.jsonl")) if sink_dir.exists() else []
        self.assertGreaterEqual(len(files), 1)


class TestClearHistory(ManagerTestCase):
    def test_clear_history_removes_persisted_rows(self):
        manager = self.build()
        manager.start()
        for _ in range(5):
            manager.ingress.submit(make_record())
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and manager.health.snapshot().written < 5:
            time.sleep(0.02)
        deleted = manager.clear_history(timeout=2.0)
        manager.stop(2.0)
        self.assertEqual(deleted, 5)

    def test_clear_history_on_disabled_manager_returns_zero_without_raising(self):
        manager = self.build(enabled=False)
        self.assertEqual(manager.clear_history(), 0)


class TestRestartAcrossManagers(ManagerTestCase):
    def test_second_manager_instance_sees_data_from_the_first(self):
        db_path = str(Path(self._tmp.name) / "obs.sqlite3")
        manager1 = self.build(db_path=db_path)
        manager1.start()
        manager1.ingress.submit(make_record(message="from run 1"))
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and manager1.health.snapshot().written < 1:
            time.sleep(0.02)
        manager1.stop(2.0)

        manager2 = self.build(db_path=db_path)
        manager2.start()
        manager2.ingress.submit(make_record(message="from run 2"))
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and manager2.health.snapshot().written < 1:
            time.sleep(0.02)
        manager2.stop(2.0)

        store = SQLiteLogStore(Path(db_path))
        store.open()
        try:
            self.assertEqual(store.row_count(), 2)
        finally:
            store.close()


class TestObservabilityIngressLevelWiring(ManagerTestCase):
    def test_level_property_matches_config(self):
        manager = self.build(level="WARNING")
        self.assertEqual(manager.level, "WARNING")


if __name__ == "__main__":
    unittest.main()
