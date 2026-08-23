"""
Tests for ``core.observability.ingress.ObservabilityIngress``/``NullIngress``
(OBS-020).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §6,
``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §6.3/§7 (non-blocking invariant,
backpressure/watermark rule, priority §1.5 / FD-R1).
"""

from __future__ import annotations

import threading
import time
import unittest

from core.observability.health import LoggingHealthState, LoggingInternalHealth
from core.observability.ingress import (
    NULL_INGRESS,
    NullIngress,
    ObservabilityIngress,
)
from core.observability.models import CanonicalLogRecord


def make_record(**overrides) -> CanonicalLogRecord:
    fields = dict(
        record_id=overrides.pop("record_id", None) or _uuid(),
        received_at="2026-08-17T00:00:00.000Z",
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


def _uuid() -> str:
    import uuid
    return uuid.uuid4().hex


def make_high_record(**overrides) -> CanonicalLogRecord:
    overrides.setdefault("is_internal", True)
    return make_record(**overrides)


def make_low_record(**overrides) -> CanonicalLogRecord:
    overrides.setdefault("level", "INFO")
    overrides.setdefault("channel", "system")
    overrides.setdefault("type", None)
    overrides.setdefault("replayed", False)
    return make_record(**overrides)


class TestSubmitPositive(unittest.TestCase):
    def test_accepted_record_is_enqueued_and_counted(self):
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=10)
        record = make_record()
        self.assertTrue(ingress.submit(record))
        self.assertEqual(ingress.qsize(), 1)
        self.assertEqual(ingress.health.snapshot().enqueued, 1)

    def test_high_survives_and_low_is_dropped_under_watermark(self):
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100,
                                       watermark_ratio=0.75)
        for _ in range(75):
            self.assertTrue(ingress.submit(make_low_record()))
        # At/above watermark: LOW is dropped, HIGH still accepted.
        self.assertFalse(ingress.submit(make_low_record()))
        self.assertTrue(ingress.submit(make_high_record()))
        snapshot = ingress.health.snapshot()
        self.assertEqual(snapshot.dropped_watermark, 1)
        self.assertEqual(snapshot.enqueued, 76)

    def test_n04_replayed_server_event_with_type_is_dropped_at_watermark(self):
        """N-04: without ``not replayed`` in the priority rule this test would
        be green-false (WP-OBS-020 Tests/Failure)."""
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=100,
                                       watermark_ratio=0.75)
        for _ in range(75):
            self.assertTrue(ingress.submit(make_low_record()))
        replayed_typed = make_record(
            type="transcription.completed", replayed=True, level="INFO",
            channel="transcription",
        )
        self.assertEqual(replayed_typed.priority.value, "low")
        self.assertFalse(ingress.submit(replayed_typed))
        self.assertEqual(ingress.health.snapshot().dropped_watermark, 1)


class TestSubmitNegative(unittest.TestCase):
    def test_submit_none_returns_false_without_raising(self):
        ingress = ObservabilityIngress(instance_id="i" * 32)
        self.assertFalse(ingress.submit(None))

    def test_submit_foreign_type_returns_false_without_raising(self):
        ingress = ObservabilityIngress(instance_id="i" * 32)
        self.assertFalse(ingress.submit("not a record"))
        self.assertFalse(ingress.submit({"not": "a record"}))
        self.assertFalse(ingress.submit(object()))

    def test_disabled_ingress_returns_false_immediately(self):
        ingress = ObservabilityIngress(instance_id="i" * 32, enabled=False)
        self.assertFalse(ingress.submit(make_high_record()))
        self.assertEqual(ingress.qsize(), 0)
        self.assertEqual(ingress.health.snapshot().enqueued, 0)

    def test_level_filter_rejects_below_configured_level(self):
        ingress = ObservabilityIngress(instance_id="i" * 32, level="WARNING")
        self.assertFalse(ingress.submit(make_record(level="INFO")))
        self.assertTrue(ingress.submit(make_record(level="WARNING")))


class TestFailureAndBackpressure(unittest.TestCase):
    def test_queue_full_returns_false_and_counts_without_raising(self):
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=1,
                                       watermark_ratio=1.0)
        self.assertTrue(ingress.submit(make_high_record()))
        self.assertFalse(ingress.submit(make_high_record()))
        self.assertEqual(ingress.health.snapshot().dropped_queue_full, 1)

    def test_health_failed_state_blocks_submit_before_anything_else(self):
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=10)
        ingress.health.set_state(LoggingHealthState.FAILED_STORE, "disk full")
        self.assertFalse(ingress.submit(make_high_record()))
        self.assertEqual(ingress.qsize(), 0)

    def test_submit_never_raises_for_a_wide_input_space(self):
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=2,
                                       watermark_ratio=0.5)
        inputs = [None, 1, "x", object(), make_low_record(), make_high_record()]
        for value in inputs:
            with self.subTest(value=repr(value)[:30]):
                try:
                    ingress.submit(value)
                except Exception as exc:  # noqa: BLE001
                    self.fail(f"submit() raised for {value!r}: {exc!r}")


class TestDrain(unittest.TestCase):
    def test_drain_returns_up_to_max_items_in_fifo_order(self):
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=10)
        ids = []
        for _ in range(5):
            record = make_high_record()
            ids.append(record.record_id)
            ingress.submit(record)
        drained = ingress.drain(max_items=3, timeout=0.2)
        self.assertEqual(len(drained), 3)
        self.assertEqual([r.record_id for r in drained], ids[:3])

    def test_drain_on_empty_queue_times_out_without_blocking_long(self):
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=10)
        start = time.monotonic()
        drained = ingress.drain(max_items=10, timeout=0.1)
        elapsed = time.monotonic() - start
        self.assertEqual(drained, [])
        self.assertLess(elapsed, 1.0)


class TestNullIngressIsBehaviorallyEquivalent(unittest.TestCase):
    def test_submit_always_false_never_raises(self):
        self.assertFalse(NULL_INGRESS.submit(make_high_record()))
        self.assertFalse(NULL_INGRESS.submit(None))
        self.assertFalse(NULL_INGRESS.submit("garbage"))

    def test_event_and_observe_server_result_are_no_ops(self):
        null = NullIngress()
        self.assertIsNone(null.event("client.app.started", channel="system"))
        self.assertIsNone(null.observe_server_result(None, None))

    def test_drain_is_always_empty(self):
        self.assertEqual(NULL_INGRESS.drain(100, 0.1), [])

    def test_null_ingress_is_a_subclass_of_observability_ingress(self):
        self.assertIsInstance(NULL_INGRESS, ObservabilityIngress)

    def test_module_constant_is_a_singleton_instance(self):
        from core.observability.ingress import NULL_INGRESS as again
        self.assertIs(NULL_INGRESS, again)


class TestConcurrencyAndTiming(unittest.TestCase):
    def test_eight_threads_5000_submits_counts_reconcile_no_duplicates(self):
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=500,
                                       watermark_ratio=0.75)
        per_thread = 5000
        thread_count = 8
        results = []
        results_lock = threading.Lock()

        def worker():
            local = 0
            for i in range(per_thread):
                record = make_high_record() if i % 2 == 0 else make_low_record()
                if ingress.submit(record):
                    local += 1
            with results_lock:
                results.append(local)

        threads = [threading.Thread(target=worker) for _ in range(thread_count)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        snapshot = ingress.health.snapshot()
        total_submitted = per_thread * thread_count
        self.assertEqual(
            snapshot.enqueued + snapshot.dropped_watermark + snapshot.dropped_queue_full,
            total_submitted,
        )
        self.assertEqual(sum(results), snapshot.enqueued)

        remaining_ids = []
        while True:
            batch = ingress.drain(max_items=500, timeout=0.05)
            if not batch:
                break
            remaining_ids.extend(r.record_id for r in batch)
        self.assertEqual(len(remaining_ids), len(set(remaining_ids)))

    def test_100000_submits_against_a_full_queue_timing_baseline(self):
        """ARCH §6.3: non-blocking invariant. No absolute threshold is
        mandated by the plan; the measured duration is written to
        TEST_RESULTS.md as the regression baseline. This assertion is only a
        hang-guard, not a performance contract."""
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=1,
                                       watermark_ratio=1.0)
        self.assertTrue(ingress.submit(make_high_record()))  # fill the queue
        start = time.perf_counter()
        for _ in range(100_000):
            accepted = ingress.submit(make_high_record())
            self.assertFalse(accepted)
        elapsed = time.perf_counter() - start
        print(f"\n[OBS-020 timing baseline] 100000 submits at full queue: "
              f"{elapsed:.4f}s ({elapsed / 100_000 * 1e6:.2f}us/call)")
        self.assertLess(elapsed, 10.0)
        self.assertEqual(ingress.health.snapshot().dropped_queue_full, 100_000)


if __name__ == "__main__":
    unittest.main()
