"""
Gate findings W-1, W-2, W-4, W-5 and W-7 — RUN-OBS-030-02.

Frozen source per case:

* **W-1** ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §8.3 (the store rows prescribe
  "Batch verworfen", nothing about the sink), invariant O-05 (failure
  isolation), ``LOGGING_CONTRACTS_FREEZE_V1.md`` §11.1 (the sink comes
  **after** the commit — an order, not a condition).
* **W-2** ``LOGGING_CONTRACTS_FREEZE_V1.md`` §5.6 and §12.4,
  ``LOGGING_DECISIONS_FREEZE_V1.md`` FD-D8: exceeding ``max_db_bytes``
  produces the structured worker record ``logging.retention_pressure``.
* **W-4** ARCH §8.3: after the 60 s suspension the store is re-checked "mit
  einem leeren Testschreibvorgang".
* **W-5** ARCH §8.3 freezes ``DISABLED`` as part of the state set.
* **W-7** CONTRACTS §5.2 (PRAGMA order) and §5.6 ("alle 2000 **geschriebenen**
  Records").
"""

from __future__ import annotations

import re
import threading
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Sequence

from core.config import LoggingObservabilityConfig
from core.observability.health import LoggingHealthState, LoggingInternalHealth
from core.observability.ingress import ObservabilityIngress
from core.observability.manager import ObservabilityManager
from core.observability.models import CanonicalLogRecord
from core.observability.storage.sqlite import OpenResult
from core.observability.worker import STORE_PAUSE_S, LoggingWorker

SQLITE_SOURCE = Path(__file__).resolve().parents[1] / "core" / "observability" / "storage" / "sqlite.py"


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


class ProgrammableStore:
    def __init__(self, *, write_exception: Optional[BaseException] = None,
                 db_bytes: Optional[int] = None, probe_result: bool = True,
                 dedupe_all: bool = False) -> None:
        self.write_exception = write_exception
        self.db_bytes = db_bytes
        self.probe_result = probe_result
        self.dedupe_all = dedupe_all
        self.batches: List[Sequence[CanonicalLogRecord]] = []
        self.write_calls = 0
        self.probe_calls = 0
        self.retention_calls = 0
        self._lock = threading.Lock()

    def open(self) -> OpenResult:
        return OpenResult(True, False, "")

    def write_batch(self, records: Sequence[CanonicalLogRecord]) -> tuple[int, int]:
        with self._lock:
            self.write_calls += 1
            if self.write_exception is not None:
                raise self.write_exception
            self.batches.append(list(records))
        if self.dedupe_all:
            return (0, len(records))
        return (len(records), 0)

    def probe_write(self) -> bool:
        self.probe_calls += 1
        return self.probe_result

    def clear(self) -> int:
        return 0

    def run_retention(self, **_kwargs) -> tuple[int, int]:
        self.retention_calls += 1
        return (0, 0)

    def measure_db_bytes(self) -> Optional[int]:
        return self.db_bytes

    def close(self) -> None:
        return None

    @property
    def all_records(self) -> List[CanonicalLogRecord]:
        out: List[CanonicalLogRecord] = []
        for batch in self.batches:
            out.extend(batch)
        return out


class RecordingSink:
    def __init__(self) -> None:
        self.records: List[CanonicalLogRecord] = []
        self.closed = False

    def write_batch(self, records: Sequence[CanonicalLogRecord]) -> None:
        self.records.extend(records)

    def close(self) -> None:
        self.closed = True


def build_worker(store, *, sink=None, **kwargs) -> tuple[LoggingWorker, ObservabilityIngress]:
    ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
    kwargs.setdefault("batch_size", 10)
    kwargs.setdefault("flush_interval_s", 0.02)
    kwargs.setdefault("queue_size", 100)
    worker = LoggingWorker(ingress, store, health=ingress.health, sink=sink, **kwargs)
    return worker, ingress


class TestW1SinkIndependentOfStore(unittest.TestCase):
    def test_broken_store_does_not_silence_the_intact_jsonl_sink(self):
        store = ProgrammableStore(write_exception=RuntimeError("store is broken"))
        sink = RecordingSink()
        worker, ingress = build_worker(store, sink=sink)
        records = [make_record(message=f"r{i}") for i in range(3)]

        worker._process_batch(records)

        self.assertEqual(len(sink.records), 3, "a failing store must not take the sink down")
        self.assertGreaterEqual(ingress.health.snapshot().store_errors, 1)

    def test_suspended_store_does_not_silence_the_sink(self):
        store = ProgrammableStore()
        sink = RecordingSink()
        worker, _ = build_worker(store, sink=sink)
        # Simulate an active 60 s suspension (ARCH §8.3 circuit breaker).
        worker._store_paused_until = float("inf")

        worker._process_batch([make_record()])

        self.assertEqual(store.write_calls, 0)
        self.assertEqual(len(sink.records), 1)

    def test_store_still_comes_first(self):
        """CONTRACTS §11.1: write_batch ZUERST, Sink DANACH."""
        order: List[str] = []

        class OrderedStore(ProgrammableStore):
            def write_batch(self, records):
                order.append("store")
                return super().write_batch(records)

        class OrderedSink(RecordingSink):
            def write_batch(self, records):
                order.append("sink")
                super().write_batch(records)

        worker, _ = build_worker(OrderedStore(), sink=OrderedSink())
        worker._process_batch([make_record()])
        self.assertEqual(order, ["store", "sink"])


class TestW2RetentionPressureRecord(unittest.TestCase):
    def test_exceeding_max_db_bytes_produces_a_canonical_record(self):
        store = ProgrammableStore(db_bytes=1024)
        worker, _ = build_worker(store, max_db_bytes=512)

        worker._run_retention_if_due(force=True)

        pressure = [r for r in store.all_records if r.type == "logging.retention_pressure"]
        self.assertEqual(len(pressure), 1)
        record = pressure[0]
        self.assertTrue(record.is_internal)
        self.assertEqual(record.channel, "performance")
        self.assertEqual(record.level, "WARNING")
        self.assertEqual(record.component, "observability.worker")
        self.assertEqual(dict(record.details), {"db_bytes": 1024, "max_db_bytes": 512})

    def test_pressure_record_is_edge_triggered_not_once_per_retention_run(self):
        store = ProgrammableStore(db_bytes=1024)
        worker, _ = build_worker(store, max_db_bytes=512)
        worker._run_retention_if_due(force=True)
        worker._run_retention_if_due(force=True)
        pressure = [r for r in store.all_records if r.type == "logging.retention_pressure"]
        self.assertEqual(len(pressure), 1)

    def test_pressure_is_reported_again_after_the_database_shrank_below_the_limit(self):
        store = ProgrammableStore(db_bytes=1024)
        worker, _ = build_worker(store, max_db_bytes=512)
        worker._run_retention_if_due(force=True)
        store.db_bytes = 100
        worker._run_retention_if_due(force=True)
        store.db_bytes = 2048
        worker._run_retention_if_due(force=True)
        pressure = [r for r in store.all_records if r.type == "logging.retention_pressure"]
        self.assertEqual(len(pressure), 2)

    def test_no_record_while_the_database_stays_below_the_limit(self):
        store = ProgrammableStore(db_bytes=100)
        worker, _ = build_worker(store, max_db_bytes=512)
        worker._run_retention_if_due(force=True)
        self.assertEqual(
            [r for r in store.all_records if r.type == "logging.retention_pressure"], []
        )


class TestW4EmptyTestWriteAfterThePause(unittest.TestCase):
    def test_expired_pause_probes_before_risking_a_batch(self):
        store = ProgrammableStore(probe_result=False)
        worker, _ = build_worker(store)
        worker._store_paused_until = 0.0  # pause has expired

        result = worker._write_with_policy([make_record()])

        self.assertEqual(result, (0, 0, False))
        self.assertEqual(store.probe_calls, 1, "the store must be re-checked with a probe")
        self.assertEqual(store.write_calls, 0, "a failing probe must not cost a batch")
        self.assertIsNotNone(worker._store_paused_until)
        self.assertGreater(worker._store_paused_until, 0.0, "the pause must be extended")

    def test_successful_probe_resumes_normal_writing(self):
        store = ProgrammableStore(probe_result=True)
        worker, _ = build_worker(store)
        worker._store_paused_until = 0.0

        inserted, _deduplicated, ok = worker._write_with_policy([make_record()])

        self.assertTrue(ok)
        self.assertEqual(inserted, 1)
        self.assertEqual(store.probe_calls, 1)
        self.assertIsNone(worker._store_paused_until)

    def test_probe_write_on_the_real_store_detects_a_closed_database(self):
        from core.observability.storage.sqlite import SQLiteLogStore
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteLogStore(Path(tmp) / "obs.sqlite3")
            self.assertFalse(store.probe_write(), "an unopened store cannot be written to")
            store.open()
            try:
                self.assertTrue(store.probe_write())
            finally:
                store.close()
            self.assertFalse(store.probe_write())

    def test_pause_is_still_honoured_while_it_lasts(self):
        store = ProgrammableStore(probe_result=True)
        worker, _ = build_worker(store)
        worker._store_paused_until = float("inf")
        self.assertEqual(worker._write_with_policy([make_record()]), (0, 0, False))
        self.assertEqual(store.probe_calls, 0)
        self.assertEqual(store.write_calls, 0)


class TestW5DisabledHealthState(unittest.TestCase):
    def test_disabled_observability_reports_disabled_not_ok(self):
        manager = ObservabilityManager(LoggingObservabilityConfig(enabled=False))
        try:
            self.assertEqual(manager.health.state, LoggingHealthState.DISABLED)
            self.assertFalse(manager.health.is_failed(), "DISABLED is not a failure state")
        finally:
            manager.stop(0.5)

    def test_enabled_observability_still_starts_in_ok(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            manager = ObservabilityManager(
                LoggingObservabilityConfig(db_path=str(Path(tmp) / "obs.sqlite3")),
                log_dir=tmp,
            )
            try:
                self.assertEqual(manager.health.state, LoggingHealthState.OK)
            finally:
                manager.stop(0.5)


class TestW7SmallerDeviations(unittest.TestCase):
    def test_pragma_order_follows_the_frozen_ddl(self):
        """CONTRACTS §5.2: journal_mode, synchronous, busy_timeout,
        foreign_keys — "in dieser Reihenfolge"."""
        text = SQLITE_SOURCE.read_text(encoding="utf-8")
        open_source = text.split("def open(self)", 1)[1].split("def _migrate", 1)[0]
        found = re.findall(r"PRAGMA (\w+)\s*=", open_source)
        self.assertEqual(
            found[:4], ["journal_mode", "synchronous", "busy_timeout", "foreign_keys"]
        )

    def test_retention_cadence_counts_written_records_not_drawn_ones(self):
        """CONTRACTS §5.6: "alle 2000 **geschriebenen** Records"."""
        store = ProgrammableStore(dedupe_all=True)
        worker, _ = build_worker(store)
        worker._process_batch([make_record() for _ in range(7)])
        self.assertEqual(
            worker._records_since_retention, 0,
            "deduplicated records were never written and must not advance the cadence",
        )

    def test_written_records_do_advance_the_retention_cadence(self):
        store = ProgrammableStore()
        worker, _ = build_worker(store)
        worker._process_batch([make_record() for _ in range(7)])
        self.assertEqual(worker._records_since_retention, 7)

    def test_records_dropped_by_a_broken_store_do_not_advance_the_cadence(self):
        store = ProgrammableStore(write_exception=RuntimeError("broken"))
        worker, _ = build_worker(store)
        worker._process_batch([make_record() for _ in range(3)])
        self.assertEqual(worker._records_since_retention, 0)


class TestStorePauseConstantUnchanged(unittest.TestCase):
    def test_pause_is_the_frozen_sixty_seconds(self):
        self.assertEqual(STORE_PAUSE_S, 60.0)


if __name__ == "__main__":
    unittest.main()
