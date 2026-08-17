"""
Fault injection for ``LoggingWorker`` — gate finding B-1 (RUN-OBS-030-02).

Frozen source: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §8.3, Zeile
"Worker-Ausnahme in der Schleife" (*gefangen, ``worker_errors++``, Schleife
laeuft weiter. Bricht sie dennoch ab: Ingress wechselt in "nur verwerfen und
zaehlen". Kein Neustartversuch* → Health ``FAILED_WORKER``), §8.1 G-2/G-4
(every output out of ``core/observability/`` goes through the
non-propagating, hard rate-limited emergency channel), §8.4 and
``LOGGING_CONTRACTS_FREEZE_V1.md`` §11.2 (``FAILED_WORKER``, counter
``worker_errors``).

These tests inject failures **outside** the narrow ``try`` blocks that
already existed, i.e. exactly where the gate review found the loop
unprotected: ``ingress.drain()`` and the ``dataclasses.replace(...)`` exit
path of ``_prepare_record``.
"""

from __future__ import annotations

import io
import sys
import threading
import time
import unittest
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Sequence

from core.observability.health import LoggingHealthState
from core.observability.ingress import ObservabilityIngress
from core.observability.models import CanonicalLogRecord
from core.observability.storage.sqlite import OpenResult
from core.observability.worker import WORKER_FAILURE_THRESHOLD, LoggingWorker


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


class CollectingStore:
    """Healthy store double: everything the worker writes lands here."""

    def __init__(self) -> None:
        self.batches: List[Sequence[CanonicalLogRecord]] = []
        self.closed = False
        self._lock = threading.Lock()

    def open(self) -> OpenResult:
        return OpenResult(True, False, "")

    def write_batch(self, records: Sequence[CanonicalLogRecord]) -> tuple[int, int]:
        with self._lock:
            self.batches.append(list(records))
        return (len(records), 0)

    def clear(self) -> int:
        return 0

    def run_retention(self, **_kwargs) -> tuple[int, int]:
        return (0, 0)

    def measure_db_bytes(self) -> Optional[int]:
        return None

    def probe_write(self) -> bool:
        return True

    def close(self) -> None:
        self.closed = True

    @property
    def rows(self) -> int:
        with self._lock:
            return sum(len(batch) for batch in self.batches)


class ExplodingDrainIngress(ObservabilityIngress):
    """An ingress whose ``drain`` raises — the loop-level exception path that
    had **no** ``try/except`` around it before this correction run."""

    def __init__(self, *, failures: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.remaining_failures = failures
        self.drain_calls = 0

    def drain(self, max_items: int, timeout: float):
        self.drain_calls += 1
        if self.remaining_failures != 0:
            if self.remaining_failures > 0:
                self.remaining_failures -= 1
            time.sleep(0.01)  # keep a permanently failing loop from spinning hot
            raise RuntimeError("injected drain failure")
        return super().drain(max_items, timeout)


def _wait_for(predicate, timeout: float = 3.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.02)
    return predicate()


class WorkerFaultTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._threads_before = {t.ident for t in threading.enumerate()}
        self._workers: List[LoggingWorker] = []

    def tearDown(self) -> None:
        for worker in self._workers:
            if worker.is_alive():
                worker.stop(2.0)
        after = {t.ident for t in threading.enumerate()}
        self.assertTrue(after.issubset(self._threads_before), "a worker thread survived")

    def make_worker(self, ingress, store, **kwargs) -> LoggingWorker:
        kwargs.setdefault("batch_size", 10)
        kwargs.setdefault("flush_interval_s", 0.02)
        kwargs.setdefault("queue_size", 100)
        worker = LoggingWorker(ingress, store, health=ingress.health, **kwargs)
        self._workers.append(worker)
        return worker


class TestSingleUnexpectedExceptionIsCaught(WorkerFaultTestCase):
    def test_one_unexpected_loop_exception_counts_and_the_loop_continues(self):
        """ARCH §8.3: *gefangen, ``worker_errors++``, Schleife laeuft weiter*."""
        ingress = ExplodingDrainIngress(failures=1, instance_id="i" * 32, queue_size=100)
        store = CollectingStore()
        worker = self.make_worker(ingress, store)
        worker.start()

        self.assertTrue(
            _wait_for(lambda: ingress.health.snapshot().worker_errors >= 1),
            "the injected exception was not counted as a worker error",
        )
        self.assertTrue(worker.is_alive(), "a single loop exception must not end the worker")

        record = make_record(message="after the injected failure")
        self.assertTrue(ingress.submit(record))
        self.assertTrue(
            _wait_for(lambda: store.rows >= 1),
            "the loop did not keep running after the injected failure",
        )
        self.assertTrue(worker.stop(2.0))
        self.assertEqual(ingress.health.snapshot().worker_errors, 1)
        self.assertNotEqual(ingress.health.state, LoggingHealthState.FAILED_WORKER)


class TestPermanentWorkerFailure(WorkerFaultTestCase):
    def test_dead_worker_is_visible_and_producers_are_no_longer_told_yes(self):
        """The exact scenario of gate finding B-1: before the correction the
        worker died silently, Health stayed ``ok``, ``worker_errors`` stayed
        ``0`` and ``submit()`` kept returning ``True`` while every record
        stranded in a queue nobody drained any more."""
        ingress = ExplodingDrainIngress(failures=-1, instance_id="i" * 32, queue_size=100)
        store = CollectingStore()
        worker = self.make_worker(ingress, store)

        # One record is queued BEFORE the worker dies: it must not vanish
        # unnoticed — it is dropped and counted at shutdown.
        self.assertTrue(ingress.submit(make_record(message="queued before death")))

        worker.start()
        self.assertTrue(
            _wait_for(lambda: not worker.is_alive(), timeout=5.0),
            "the worker loop never gave up despite permanent failures",
        )

        snapshot = ingress.health.snapshot()
        self.assertGreaterEqual(snapshot.worker_errors, WORKER_FAILURE_THRESHOLD)
        self.assertEqual(ingress.health.state, LoggingHealthState.FAILED_WORKER)
        self.assertTrue(ingress.health.is_failed())

        # ARCH §8.3, "nur verwerfen und zaehlen": submit() tells the truth
        # instead of pretending the record was accepted.
        depth_before = ingress.qsize()
        results = [ingress.submit(make_record()) for _ in range(5)]
        self.assertEqual(results, [False] * 5, "producers were still told 'accepted'")
        self.assertEqual(
            ingress.qsize(), depth_before,
            "a rejected record must never reach the queue",
        )
        # No record strands unnoticed: the one queued BEFORE the failure is
        # counted as dropped at shutdown (ARCH §8.3, Shutdown-Zeile) even
        # though the drain path itself is the injected fault.
        self.assertGreaterEqual(ingress.health.snapshot().dropped_shutdown, 1)

        # "Kein Neustartversuch": no observability thread comes back.
        self.assertEqual(
            [t for t in threading.enumerate() if t.name == "RealtimeSTT-Observability"],
            [],
        )

    def test_no_unfiltered_threading_traceback_reaches_stderr(self):
        """ARCH §8.1 G-2/G-4: every output out of ``core/observability/``
        goes through the non-propagating, hard rate-limited emergency
        channel. A worker exception escaping ``run()`` would be printed by
        ``threading``'s excepthook as a full traceback — bypassing it."""
        ingress = ExplodingDrainIngress(failures=-1, instance_id="i" * 32, queue_size=100)
        store = CollectingStore()
        worker = self.make_worker(ingress, store)

        captured = io.StringIO()
        original = sys.stderr
        sys.stderr = captured
        try:
            worker.start()
            _wait_for(lambda: not worker.is_alive(), timeout=5.0)
            worker.stop(2.0)
        finally:
            sys.stderr = original

        text = captured.getvalue()
        self.assertNotIn("Traceback (most recent call last)", text)
        self.assertNotIn("injected drain failure\n  File", text)
        for line in (line for line in text.splitlines() if line.strip()):
            self.assertTrue(
                line.startswith("[observability] "),
                f"unexpected non-emergency stderr output: {line!r}",
            )


class TestPrepareRecordExitPath(WorkerFaultTestCase):
    """``worker.py`` had ``return dataclasses.replace(record, raw=redacted)``
    OUTSIDE its own ``try`` block — a real exit path out of the protected
    region (gate finding B-1, point 3)."""

    class _NotADataclass:
        raw = {"token": "secret"}

    def test_replace_failure_is_caught_and_counted_as_malformed(self):
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=10)
        store = CollectingStore()
        worker = self.make_worker(ingress, store)

        broken = self.__class__._NotADataclass()
        result = worker._prepare_record(broken)  # must not raise

        self.assertIs(result, broken)
        self.assertGreaterEqual(ingress.health.snapshot().malformed, 1)

    def test_process_batch_survives_a_record_whose_preparation_fails(self):
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=10)
        store = CollectingStore()
        worker = self.make_worker(ingress, store)
        worker._process_batch([self.__class__._NotADataclass()])  # must not raise
        self.assertGreaterEqual(ingress.health.snapshot().malformed, 1)


class TestStopOnNeverStartedWorker(WorkerFaultTestCase):
    def test_queued_records_are_dropped_and_counted_not_silently_lost(self):
        """Gate finding W-7: ``stop()`` on a worker that was never started
        left queued records uncounted (ARCH §8.3, Shutdown-Zeile)."""
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
        store = CollectingStore()
        worker = self.make_worker(ingress, store)
        for _ in range(4):
            self.assertTrue(ingress.submit(make_record()))

        self.assertTrue(worker.stop(0.5))
        self.assertEqual(ingress.health.snapshot().dropped_shutdown, 4)
        self.assertEqual(ingress.qsize(), 0)


if __name__ == "__main__":
    unittest.main()
