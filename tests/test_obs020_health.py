"""
Tests for ``core.observability.health`` (OBS-020).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §11.2 (state/snapshot) and
``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §8.1 (G-2 dedicated logger, G-4 rate
limit).
"""

from __future__ import annotations

import io
import logging
import threading
import unittest
from unittest import mock

from core.observability.health import (
    EMERGENCY_LOGGER_NAME,
    LoggingHealthSnapshot,
    LoggingHealthState,
    LoggingInternalHealth,
    _RateLimiter,
    emergency,
)


class TestHealthSnapshotShape(unittest.TestCase):
    def test_state_enum_has_frozen_seven_values(self):
        values = {member.value for member in LoggingHealthState}
        self.assertEqual(
            values,
            {"ok", "dropping", "degraded_sink", "degraded_store",
             "failed_store", "failed_worker", "disabled"},
        )

    def test_fresh_health_is_ok_with_zeroed_counters(self):
        health = LoggingInternalHealth()
        snapshot = health.snapshot(queue_depth=0)
        self.assertIsInstance(snapshot, LoggingHealthSnapshot)
        self.assertEqual(snapshot.state, LoggingHealthState.OK)
        self.assertIsNone(snapshot.since)
        for field_name in ("enqueued", "written", "deduplicated",
                           "dropped_watermark", "dropped_queue_full",
                           "dropped_shutdown", "malformed", "store_errors",
                           "sink_errors", "retention_errors", "worker_errors"):
            with self.subTest(field=field_name):
                self.assertEqual(getattr(snapshot, field_name), 0)
        self.assertIsNone(snapshot.db_bytes)

    def test_is_failed_true_only_for_failed_states(self):
        health = LoggingInternalHealth()
        for state in LoggingHealthState:
            with self.subTest(state=state):
                health.set_state(state)
                expected = state in (
                    LoggingHealthState.FAILED_STORE,
                    LoggingHealthState.FAILED_WORKER,
                )
                self.assertEqual(health.is_failed(), expected)

    def test_set_state_records_since_on_transition_only(self):
        health = LoggingInternalHealth()
        self.assertIsNone(health.snapshot().since)
        health.set_state(LoggingHealthState.DROPPING, "watermark")
        first_since = health.snapshot().since
        self.assertIsNotNone(first_since)
        health.set_state(LoggingHealthState.DROPPING, "watermark still")
        self.assertEqual(health.snapshot().since, first_since)


class TestCounters(unittest.TestCase):
    def test_each_counter_method_increments_exactly_one_field(self):
        health = LoggingInternalHealth()
        health.record_enqueued()
        health.record_dropped_watermark()
        health.record_dropped_queue_full()
        health.record_dropped_shutdown()
        health.record_malformed()
        snapshot = health.snapshot()
        self.assertEqual(snapshot.enqueued, 1)
        self.assertEqual(snapshot.dropped_watermark, 1)
        self.assertEqual(snapshot.dropped_queue_full, 1)
        self.assertEqual(snapshot.dropped_shutdown, 1)
        self.assertEqual(snapshot.malformed, 1)

    def test_error_counters_increment_and_go_through_emergency(self):
        health = LoggingInternalHealth()
        with mock.patch.object(health, "_limiter") as limiter:
            limiter.should_emit.return_value = (False, 0)
            health.record_store_error("store_write_failed", "database is locked")
            health.record_sink_error("sink_write_failed", "disk full")
            health.record_retention_error("retention_failed", "disk full")
            health.record_worker_error("worker_loop_failed", "boom")
        snapshot = health.snapshot()
        self.assertEqual(snapshot.store_errors, 1)
        self.assertEqual(snapshot.sink_errors, 1)
        self.assertEqual(snapshot.retention_errors, 1)
        self.assertEqual(snapshot.worker_errors, 1)

    def test_counters_are_thread_safe_under_contention(self):
        health = LoggingInternalHealth()

        def hammer():
            for _ in range(2000):
                health.record_enqueued()

        threads = [threading.Thread(target=hammer) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(health.snapshot().enqueued, 16000)

    def test_db_bytes_defaults_none_and_is_settable(self):
        health = LoggingInternalHealth()
        self.assertIsNone(health.snapshot().db_bytes)
        health.set_db_bytes(4096)
        self.assertEqual(health.snapshot().db_bytes, 4096)


class _FakeClock:
    def __init__(self, start: float = 1000.0) -> None:
        self.value = start

    def __call__(self) -> float:
        return self.value


class TestEmergencyRateLimit(unittest.TestCase):
    """G-4: at most one stderr line per code and 60s, with a repeat counter."""

    def test_burst_of_2000_within_one_second_yields_at_most_one_line(self):
        clock = _FakeClock()
        limiter = _RateLimiter(window_s=60.0)
        buffer = io.StringIO()
        with mock.patch("core.observability.health.time.monotonic", clock), \
             mock.patch("sys.stderr", buffer):
            for _ in range(2000):
                emergency("burst_code", "detail", limiter=limiter)
                clock.value += 0.0001  # 2000 calls comfortably inside 1s
        lines = [line for line in buffer.getvalue().splitlines() if line]
        self.assertLessEqual(len(lines), 1)
        self.assertEqual(len(lines), 1)
        self.assertIn("burst_code", lines[0])

    def test_repeat_counter_reflects_suppressed_occurrences(self):
        clock = _FakeClock()
        limiter = _RateLimiter(window_s=10.0)
        buffer = io.StringIO()
        with mock.patch("core.observability.health.time.monotonic", clock), \
             mock.patch("sys.stderr", buffer):
            emergency("rep_code", "first", limiter=limiter)  # emitted, count=1
            for _ in range(4):
                emergency("rep_code", "suppressed", limiter=limiter)
            clock.value += 10.1  # window elapses
            emergency("rep_code", "after window", limiter=limiter)
        lines = [line for line in buffer.getvalue().splitlines() if line]
        self.assertEqual(len(lines), 2)
        self.assertNotIn("(x", lines[0])  # first emission: nothing suppressed yet
        self.assertIn("(x5)", lines[1])   # 4 suppressed + this one

    def test_different_codes_have_independent_windows(self):
        clock = _FakeClock()
        limiter = _RateLimiter(window_s=60.0)
        buffer = io.StringIO()
        with mock.patch("core.observability.health.time.monotonic", clock), \
             mock.patch("sys.stderr", buffer):
            emergency("code_a", "a", limiter=limiter)
            emergency("code_b", "b", limiter=limiter)
            emergency("code_a", "a again", limiter=limiter)
            emergency("code_b", "b again", limiter=limiter)
        lines = [line for line in buffer.getvalue().splitlines() if line]
        self.assertEqual(len(lines), 2)  # one per code; repeats suppressed


class TestEmergencyNeverRaises(unittest.TestCase):
    def test_stderr_is_none_does_not_raise(self):
        with mock.patch("sys.stderr", None):
            try:
                emergency("code_x", "detail", limiter=_RateLimiter())
            except Exception as exc:  # noqa: BLE001
                self.fail(f"emergency() raised with sys.stderr is None: {exc!r}")

    def test_stderr_write_raising_does_not_raise(self):
        class ThrowingStream:
            def write(self, *_args, **_kwargs):
                raise OSError("broken pipe")

            def flush(self):
                raise OSError("broken pipe")

        with mock.patch("sys.stderr", ThrowingStream()):
            try:
                emergency("code_y", "detail", limiter=_RateLimiter())
            except Exception as exc:  # noqa: BLE001
                self.fail(f"emergency() raised when sys.stderr.write() raises: {exc!r}")

    def test_counters_keep_incrementing_even_when_stderr_is_broken(self):
        health = LoggingInternalHealth()
        with mock.patch("sys.stderr", None):
            health.record_store_error("s1", "db locked")
            health.record_store_error("s1", "db locked again")
        self.assertEqual(health.snapshot().store_errors, 2)


class TestEmergencyLoggerContract(unittest.TestCase):
    def test_observability_internal_logger_does_not_propagate(self):
        logger = logging.getLogger(EMERGENCY_LOGGER_NAME)
        self.assertFalse(logger.propagate)

    def test_observability_internal_logger_has_a_stream_handler(self):
        logger = logging.getLogger(EMERGENCY_LOGGER_NAME)
        self.assertTrue(
            any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
        )


if __name__ == "__main__":
    unittest.main()
