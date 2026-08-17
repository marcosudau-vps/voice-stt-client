"""
Tests for ``core.observability.worker.LoggingWorker`` (OBS-030).

Frozen source: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §6 (thread model,
lifecycle, non-blocking invariant), §7 (backpressure/priority/counters),
§8 (failure domain), ``LOGGING_CONTRACTS_FREEZE_V1.md`` §5.5/§5.6/§8.2/§11.
"""

from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import List, Optional, Sequence

from core.observability.health import LoggingHealthState, LoggingInternalHealth
from core.observability.ingress import ObservabilityIngress
from core.observability.models import CanonicalLogRecord
from core.observability.storage.sqlite import OpenResult, SQLiteLogStore
from core.observability.worker import LoggingWorker


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


class FakeStore:
    """A programmable in-memory store double for worker-level unit tests
    that must not depend on real SQLite failure injection."""

    def __init__(self, *, open_result: Optional[OpenResult] = None) -> None:
        self.open_result = open_result if open_result is not None else OpenResult(True, False, "")
        self.batches: List[Sequence[CanonicalLogRecord]] = []
        self.opened = False
        self.closed = False
        self.write_exception: Optional[BaseException] = None
        self.write_exception_calls = 0
        self.clear_calls = 0
        self.clear_return = 0
        self.retention_calls: list[dict] = []
        self._lock = threading.Lock()

    def open(self) -> OpenResult:
        self.opened = True
        return self.open_result

    def write_batch(self, records: Sequence[CanonicalLogRecord]) -> tuple[int, int]:
        with self._lock:
            if self.write_exception is not None and self.write_exception_calls > 0:
                self.write_exception_calls -= 1
                raise self.write_exception
            self.batches.append(list(records))
            return (len(records), 0)

    def clear(self) -> int:
        self.clear_calls += 1
        return self.clear_return

    def run_retention(self, **kwargs) -> tuple[int, int]:
        self.retention_calls.append(kwargs)
        return (0, 0)

    def measure_db_bytes(self) -> Optional[int]:
        return 4096

    def close(self) -> None:
        self.closed = True

    @property
    def all_records(self) -> List[CanonicalLogRecord]:
        out: List[CanonicalLogRecord] = []
        for batch in self.batches:
            out.extend(batch)
        return out


class FakeSink:
    def __init__(self, *, fail_after: Optional[int] = None) -> None:
        self.batches: List[Sequence[CanonicalLogRecord]] = []
        self.closed = False
        self.fail_after = fail_after
        self._calls = 0

    def write_batch(self, records: Sequence[CanonicalLogRecord]) -> None:
        self._calls += 1
        if self.fail_after is not None and self._calls > self.fail_after:
            raise RuntimeError("simulated sink failure")
        self.batches.append(list(records))

    def close(self) -> None:
        self.closed = True


def _no_threads_leaked(before: set) -> bool:
    after = {t.ident for t in threading.enumerate()}
    return after.issubset(before)


class WorkerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._threads_before = {t.ident for t in threading.enumerate()}
        self._workers: List[LoggingWorker] = []

    def tearDown(self) -> None:
        for worker in self._workers:
            if worker.is_alive():
                worker.stop(2.0)
        self.assertTrue(
            _no_threads_leaked(self._threads_before),
            "a LoggingWorker thread survived stop()",
        )

    def make_worker(self, ingress=None, store=None, **kwargs) -> tuple[LoggingWorker, ObservabilityIngress, FakeStore]:
        ingress = ingress if ingress is not None else ObservabilityIngress(instance_id="i" * 32, queue_size=1000)
        store = store if store is not None else FakeStore()
        kwargs.setdefault("batch_size", 50)
        kwargs.setdefault("flush_interval_s", 0.05)
        kwargs.setdefault("queue_size", 1000)
        worker = LoggingWorker(ingress, store, health=ingress.health, **kwargs)
        self._workers.append(worker)
        return worker, ingress, store


class TestEndToEndLoggerToSqlite(unittest.TestCase):
    """The mandatory end-to-end proof: logger.info -> Canonical -> Queue ->
    Worker -> SQLite (WP-OBS-030 Pflichtpruefungen)."""

    def test_logger_info_reaches_sqlite(self):
        from core.observability.adapters.python_logging import UnifiedLogHandler
        from core.observability.normalizer import from_log_record

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "obs.sqlite3"
            ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
            store = SQLiteLogStore(db_path)
            worker = LoggingWorker(ingress, store, health=ingress.health,
                                   batch_size=10, flush_interval_s=0.05)

            def normalize(record, _ingress=ingress):
                return from_log_record(record, instance_id=_ingress.instance_id)

            handler = UnifiedLogHandler(ingress, normalize)
            logger = __import__("logging").getLogger("test_obs030_e2e")
            logger.addHandler(handler)
            logger.setLevel(__import__("logging").INFO)
            logger.propagate = False

            worker.start()
            try:
                logger.info("hello from obs030 e2e test")
                deadline = time.monotonic() + 3.0
                while time.monotonic() < deadline:
                    if ingress.health.snapshot().written >= 1:
                        break
                    time.sleep(0.02)
                self.assertGreaterEqual(ingress.health.snapshot().written, 1)
            finally:
                logger.removeHandler(handler)
                worker.stop(2.0)

            store2 = SQLiteLogStore(db_path)
            store2.open()
            try:
                self.assertGreaterEqual(store2.row_count(), 1)
            finally:
                store2.close()


class TestPositiveBatching(WorkerTestCase):
    def test_batch_is_written_and_counters_updated(self):
        worker, ingress, store = self.make_worker()
        worker.start()
        for _ in range(5):
            ingress.submit(make_record())
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and ingress.health.snapshot().written < 5:
            time.sleep(0.02)
        worker.stop(2.0)
        self.assertEqual(len(store.all_records), 5)
        self.assertEqual(ingress.health.snapshot().written, 5)
        self.assertEqual(ingress.health.snapshot().deduplicated, 0)


class TestNonBlockingDrain(WorkerTestCase):
    def test_worker_shutdown_does_not_hang_with_no_records(self):
        worker, ingress, store = self.make_worker()
        worker.start()
        time.sleep(0.1)
        start = time.perf_counter()
        stopped = worker.stop(2.0)
        elapsed = time.perf_counter() - start
        self.assertTrue(stopped)
        self.assertLess(elapsed, 2.5)


class TestPriorityAndDropPolicyEndToEnd(WorkerTestCase):
    def test_high_records_survive_persistently_under_watermark_pressure(self):
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100, watermark_ratio=0.75)
        store = FakeStore()
        worker, _, _ = self.make_worker(ingress=ingress, store=store, batch_size=200, flush_interval_s=0.05)
        for _ in range(75):
            self.assertTrue(ingress.submit(make_record(level="INFO", channel="system", type=None)))
        # at/above watermark: LOW dropped, HIGH (is_internal) still accepted
        self.assertFalse(ingress.submit(make_record(level="INFO", channel="system", type=None)))
        high = make_record(is_internal=True, message="must survive")
        self.assertTrue(ingress.submit(high))

        worker.start()
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and ingress.health.snapshot().written < 76:
            time.sleep(0.02)
        worker.stop(2.0)

        persisted_ids = {r.record_id for r in store.all_records}
        self.assertIn(high.record_id, persisted_ids)
        self.assertEqual(ingress.health.snapshot().dropped_watermark, 1)


class TestHighSpecialRule(WorkerTestCase):
    def test_replayed_typed_server_event_is_low_and_may_be_dropped_at_watermark(self):
        """N-04: the ``not replayed`` correction (ARCH §7.2) — a replayed
        server event WITH a type must still be droppable under backpressure."""
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100, watermark_ratio=0.75)
        for _ in range(75):
            self.assertTrue(ingress.submit(make_record()))
        replayed_typed = make_record(type="transcription.completed", replayed=True,
                                     channel="transcription")
        self.assertEqual(replayed_typed.priority.value, "low")
        self.assertFalse(ingress.submit(replayed_typed))
        self.assertEqual(ingress.health.snapshot().dropped_watermark, 1)


class TestWorkerFailureIsolation(WorkerTestCase):
    def test_store_exception_does_not_crash_worker_loop(self):
        store = FakeStore()
        store.write_exception = RuntimeError("boom")
        store.write_exception_calls = 100  # keep failing
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
        worker, _, _ = self.make_worker(ingress=ingress, store=store, batch_size=10, flush_interval_s=0.05)
        worker.start()
        ingress.submit(make_record())
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and ingress.health.snapshot().store_errors < 1:
            time.sleep(0.02)
        self.assertTrue(worker.is_alive())
        self.assertGreaterEqual(ingress.health.snapshot().store_errors, 1)
        self.assertIn(
            ingress.health.state,
            (LoggingHealthState.DEGRADED_STORE, LoggingHealthState.FAILED_STORE),
        )
        stopped = worker.stop(2.0)
        self.assertTrue(stopped)

    def test_store_recovers_after_transient_failures_and_resumes_writing(self):
        """A batch that exhausts its retry-once budget is discarded (ARCH
        §8.3: "einmal wiederholen, dann verwerfen") — but the WORKER itself
        keeps running and the NEXT batch, once the transient fault is gone,
        succeeds and clears the health state back to OK."""
        store = FakeStore()
        store.write_exception = RuntimeError("transient")
        store.write_exception_calls = 2  # exhausts exactly one batch's retry budget
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
        worker, _, _ = self.make_worker(ingress=ingress, store=store, batch_size=1, flush_interval_s=0.05)
        worker.start()
        ingress.submit(make_record())  # this batch's two attempts both fail
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and ingress.health.snapshot().store_errors < 1:
            time.sleep(0.02)
        self.assertGreaterEqual(ingress.health.snapshot().store_errors, 1)

        second = make_record()
        ingress.submit(second)  # the transient fault is exhausted: this one lands
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and not store.all_records:
            time.sleep(0.02)
        worker.stop(2.0)
        persisted_ids = {r.record_id for r in store.all_records}
        self.assertIn(second.record_id, persisted_ids)
        # The transition back to OK also writes a direct "logging.recovered"
        # internal record (G-6), which is why more than one row may land.
        self.assertEqual(ingress.health.state, LoggingHealthState.OK)

    def test_permanently_broken_store_reaches_failed_state_worker_keeps_running(self):
        store = FakeStore()
        store.write_exception = RuntimeError("permanently broken")
        store.write_exception_calls = 10_000
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
        worker, _, _ = self.make_worker(ingress=ingress, store=store, batch_size=1, flush_interval_s=0.02)
        worker.start()
        for _ in range(6):
            ingress.submit(make_record())
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline and ingress.health.state != LoggingHealthState.FAILED_STORE:
            time.sleep(0.02)
        self.assertEqual(ingress.health.state, LoggingHealthState.FAILED_STORE)
        self.assertTrue(worker.is_alive(), "the worker must keep running (application unaffected)")
        worker.stop(2.0)

    def test_disk_full_error_suspends_retention_and_sets_failed_store(self):
        store = FakeStore()
        store.write_exception = RuntimeError("database or disk is full")
        store.write_exception_calls = 10_000
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
        worker, _, _ = self.make_worker(ingress=ingress, store=store, batch_size=1, flush_interval_s=0.02)
        worker.start()
        ingress.submit(make_record())
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and ingress.health.state != LoggingHealthState.FAILED_STORE:
            time.sleep(0.02)
        self.assertEqual(ingress.health.state, LoggingHealthState.FAILED_STORE)
        worker.stop(2.0)


class TestSinkFailureIsolation(WorkerTestCase):
    def test_sink_failure_disables_sink_but_store_keeps_writing(self):
        store = FakeStore()
        sink = FakeSink(fail_after=0)
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
        worker, _, _ = self.make_worker(ingress=ingress, store=store, sink=sink,
                                        batch_size=1, flush_interval_s=0.02)
        worker.start()
        for _ in range(3):
            ingress.submit(make_record())
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and len(store.all_records) < 3:
            time.sleep(0.02)
        worker.stop(2.0)
        self.assertEqual(len(store.all_records), 3, "store must be unaffected by a sink failure")
        self.assertGreaterEqual(ingress.health.snapshot().sink_errors, 1)
        self.assertEqual(ingress.health.state, LoggingHealthState.DEGRADED_SINK)


class TestRawRedactionAndTruncation(WorkerTestCase):
    def test_raw_payload_is_redacted_before_reaching_the_store(self):
        store = FakeStore()
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
        worker, _, _ = self.make_worker(ingress=ingress, store=store, batch_size=10, flush_interval_s=0.05)
        record = make_record(raw={"token": "super-secret", "safe": "value"})
        worker.start()
        ingress.submit(record)
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and not store.all_records:
            time.sleep(0.02)
        worker.stop(2.0)
        self.assertEqual(len(store.all_records), 1)
        persisted_raw = store.all_records[0].raw
        self.assertEqual(persisted_raw["token"], "[redacted]")
        self.assertEqual(persisted_raw["safe"], "value")

    def test_oversized_raw_payload_is_truncated_with_marker(self):
        store = FakeStore()
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
        worker, _, _ = self.make_worker(ingress=ingress, store=store, batch_size=10, flush_interval_s=0.05)
        big_value = "x" * (70 * 1024)
        record = make_record(raw={"payload": big_value})
        worker.start()
        ingress.submit(record)
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and not store.all_records:
            time.sleep(0.02)
        worker.stop(2.0)
        persisted_raw = store.all_records[0].raw
        self.assertTrue(persisted_raw.get("_truncated"))
        self.assertGreater(persisted_raw.get("_bytes", 0), 64 * 1024)

    def test_details_are_not_redacted_again_in_the_worker(self):
        """``details`` is already redacted at ingress time (CONTRACTS §3.3);
        the worker must pass it through unchanged."""
        store = FakeStore()
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
        worker, _, _ = self.make_worker(ingress=ingress, store=store, batch_size=10, flush_interval_s=0.05)
        record = make_record(details={"already": "redacted", "token": "[redacted]"})
        worker.start()
        ingress.submit(record)
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and not store.all_records:
            time.sleep(0.02)
        worker.stop(2.0)
        self.assertEqual(dict(store.all_records[0].details), {"already": "redacted", "token": "[redacted]"})


class TestRetentionCadence(WorkerTestCase):
    def test_retention_runs_once_at_start(self):
        store = FakeStore()
        worker, ingress, _ = self.make_worker(store=store, retention_days=14, max_entries=1000)
        worker.start()
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and not store.retention_calls:
            time.sleep(0.02)
        worker.stop(2.0)
        self.assertGreaterEqual(len(store.retention_calls), 1)


class TestClearRequest(WorkerTestCase):
    def test_request_clear_runs_on_worker_thread_and_returns_count(self):
        store = FakeStore()
        store.clear_return = 42
        worker, ingress, _ = self.make_worker(store=store)
        worker.start()
        result = worker.request_clear(timeout=2.0)
        worker.stop(2.0)
        self.assertEqual(result, 42)
        self.assertEqual(store.clear_calls, 1)

    def test_request_clear_times_out_if_worker_never_started(self):
        store = FakeStore()
        worker, ingress, _ = self.make_worker(store=store)
        with self.assertRaises(TimeoutError):
            worker.request_clear(timeout=0.2)


class TestHealthAndDropCounters(WorkerTestCase):
    def test_written_and_deduplicated_counters_reflect_store_results(self):
        class DedupeStore(FakeStore):
            def write_batch(self, records):
                return (1, max(0, len(records) - 1))

        store = DedupeStore()
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
        worker, _, _ = self.make_worker(ingress=ingress, store=store, batch_size=10, flush_interval_s=0.05)
        worker.start()
        for _ in range(3):
            ingress.submit(make_record())
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and ingress.health.snapshot().written < 1:
            time.sleep(0.02)
        worker.stop(2.0)
        snapshot = ingress.health.snapshot()
        self.assertGreaterEqual(snapshot.written, 1)
        self.assertGreaterEqual(snapshot.deduplicated, 1)

    def test_no_internal_store_exception_ever_propagates_out_of_submit_or_worker(self):
        store = FakeStore()
        store.write_exception = RuntimeError("boom")
        store.write_exception_calls = 10_000
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
        worker, _, _ = self.make_worker(ingress=ingress, store=store, batch_size=1, flush_interval_s=0.02)
        worker.start()
        try:
            for _ in range(20):
                accepted = ingress.submit(make_record())
                self.assertIsInstance(accepted, bool)
        finally:
            worker.stop(2.0)


class TestShutdownFlush(WorkerTestCase):
    def test_queued_records_are_flushed_before_stop_returns(self):
        store = FakeStore()
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=1000)
        worker, _, _ = self.make_worker(ingress=ingress, store=store, batch_size=500, flush_interval_s=0.5)
        worker.start()
        time.sleep(0.05)
        for _ in range(20):
            ingress.submit(make_record())
        stopped = worker.stop(2.0)
        self.assertTrue(stopped)
        self.assertEqual(len(store.all_records), 20)

    def test_thread_is_gone_after_stop(self):
        worker, ingress, _ = self.make_worker()
        worker.start()
        worker.stop(2.0)
        self.assertFalse(worker.is_alive())
        self.assertNotIn(worker.ident, [t.ident for t in threading.enumerate()])


if __name__ == "__main__":
    unittest.main()
