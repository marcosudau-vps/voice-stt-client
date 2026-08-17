"""
Tests for ``core.observability.adapters.python_logging.UnifiedLogHandler``
(OBS-020).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §3.1/§6,
``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §8.1 (G-1 reentrancy, G-3 handleError,
G-7 flush/close no-ops).
"""

from __future__ import annotations

import functools
import logging
import time
import unittest
from typing import Any, List, Optional

from core.observability.adapters.python_logging import (
    INTERNAL_LOGGER_NAME,
    UnifiedLogHandler,
)
from core.observability.health import LoggingInternalHealth
from core.observability.models import CanonicalLogRecord
from core.observability.normalizer import from_log_record


class RecordingIngress:
    """A recording fake ingress (WP-OBS-020 §8.3: "OBS-020 wird gegen einen
    aufzeichnenden Fake-Store abgenommen")."""

    def __init__(self, *, health: Optional[LoggingInternalHealth] = None,
                 always_reject: bool = False, raise_on_submit: bool = False) -> None:
        self.health = health if health is not None else LoggingInternalHealth()
        self.submitted: List[CanonicalLogRecord] = []
        self._always_reject = always_reject
        self._raise_on_submit = raise_on_submit

    def submit(self, record: Any) -> bool:
        if self._raise_on_submit:
            raise RuntimeError("submit exploded")
        if self._always_reject:
            return False
        self.submitted.append(record)
        return True


def build_normalizer(instance_id="i" * 32, store_transcription_content=False):
    return functools.partial(
        from_log_record,
        instance_id=instance_id,
        store_transcription_content=store_transcription_content,
        user_profile=None,
    )


def emit_via_handler(handler: UnifiedLogHandler, logger_name="controller",
                      level=logging.INFO, msg="hello", args=None, exc_info=None,
                      extra=None) -> logging.LogRecord:
    record = logging.LogRecord(logger_name, level, "mod.py", 1, msg, args, exc_info)
    for key, value in (extra or {}).items():
        record.__dict__[key] = value
    handler.emit(record)
    return record


class TestPositive(unittest.TestCase):
    def test_one_log_line_produces_exactly_one_record_with_correct_fields(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer())
        emit_via_handler(handler, logger_name="controller", level=logging.WARNING,
                         msg="core gestartet")
        self.assertEqual(len(ingress.submitted), 1)
        record = ingress.submitted[0]
        self.assertEqual(record.component, "controller")
        self.assertEqual(record.channel, "system")
        self.assertEqual(record.level, "WARNING")

    def test_exc_info_lands_as_text_and_args_appear_nowhere(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer())
        try:
            raise ValueError("boom")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        emit_via_handler(handler, msg="failed with %s", args=("secret-arg",),
                         exc_info=exc_info)
        self.assertEqual(len(ingress.submitted), 1)
        record = ingress.submitted[0]
        self.assertIn("exception", record.details)
        self.assertIsInstance(record.details["exception"], str)
        self.assertIn("ValueError", record.details["exception"])
        dumped = repr(dict(record.details))
        self.assertNotIn("secret-arg", dumped)

    def test_four_extra_fields_are_carried_through(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer())
        emit_via_handler(handler, extra={
            "session_id": "sess-1", "segment_id": 3,
            "event_type": "final", "detail": "x",
        })
        record = ingress.submitted[0]
        self.assertEqual(record.session_id, "sess-1")
        self.assertEqual(record.details["segment_id"], 3)
        self.assertEqual(record.details["event_type"], "final")
        self.assertEqual(record.details["detail"], "x")

    def test_null_ingress_style_always_false_backend_never_raises(self):
        ingress = RecordingIngress(always_reject=True)
        handler = UnifiedLogHandler(ingress, build_normalizer())
        for _ in range(50):
            try:
                emit_via_handler(handler)
            except Exception as exc:  # noqa: BLE001
                self.fail(f"emit() raised while ingress always rejects: {exc!r}")
        self.assertEqual(ingress.health.snapshot().worker_errors, 0)
        self.assertEqual(ingress.health.snapshot().malformed, 0)


class TestNegative(unittest.TestCase):
    def test_malformed_percent_format_does_not_raise(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer())
        try:
            emit_via_handler(handler, msg="value=%s", args=None)
        except Exception as exc:  # noqa: BLE001
            self.fail(f"emit() raised for malformed %%-format: {exc!r}")

    def test_extra_object_with_throwing_str_does_not_raise(self):
        class Throws:
            def __str__(self):
                raise RuntimeError("no str for you")

            def __repr__(self):
                raise RuntimeError("no repr either")

        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer())
        try:
            emit_via_handler(handler, extra={"detail": Throws()})
        except Exception as exc:  # noqa: BLE001
            self.fail(f"emit() raised for a throwing __str__ extra: {exc!r}")
        self.assertEqual(len(ingress.submitted), 1)

    def test_log_line_from_a_thread_without_a_name_does_not_raise(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer())
        record = logging.LogRecord("controller", logging.INFO, "m.py", 1,
                                    "no thread name", None, None)
        record.threadName = None
        try:
            handler.emit(record)
        except Exception as exc:  # noqa: BLE001
            self.fail(f"emit() raised for a nameless thread: {exc!r}")
        self.assertEqual(ingress.submitted[0].details["thread"], None)


class TestFailure(unittest.TestCase):
    def test_ingress_always_false_no_exception_no_stderr(self):
        import io
        from unittest import mock
        ingress = RecordingIngress(always_reject=True)
        handler = UnifiedLogHandler(ingress, build_normalizer())
        buffer = io.StringIO()
        with mock.patch("sys.stderr", buffer):
            for _ in range(20):
                emit_via_handler(handler)
        self.assertEqual(buffer.getvalue(), "")

    def test_normalizer_raising_routes_through_handle_error_and_continues(self):
        ingress = RecordingIngress()

        def exploding_normalizer(_record):
            raise RuntimeError("normalizer exploded")

        handler = UnifiedLogHandler(ingress, exploding_normalizer)
        handle_error_calls = []
        original = handler.handleError

        def spy(record):
            handle_error_calls.append(record)
            original(record)

        handler.handleError = spy
        try:
            emit_via_handler(handler)
        except Exception as exc:  # noqa: BLE001
            self.fail(f"emit() must not raise when normalizer raises: {exc!r}")
        self.assertEqual(len(handle_error_calls), 1)
        self.assertEqual(ingress.submitted, [])
        self.assertEqual(ingress.health.snapshot().malformed, 1)

    def test_submit_raising_is_caught_via_handle_error(self):
        ingress = RecordingIngress(raise_on_submit=True)
        handler = UnifiedLogHandler(ingress, build_normalizer())
        try:
            emit_via_handler(handler)
        except Exception as exc:  # noqa: BLE001
            self.fail(f"emit() must not raise when submit() raises: {exc!r}")
        self.assertEqual(ingress.health.snapshot().malformed, 1)

    def test_reentrant_logging_call_during_emit_stays_bounded(self):
        """G-1: a threading.local reentrancy guard must cap the number of
        records produced, even if something inside the pipeline itself
        triggers another ``logging`` call on the same thread."""
        logger_name = "obs020.recursion.test"
        test_logger = logging.getLogger(logger_name)
        test_logger.setLevel(logging.DEBUG)
        test_logger.propagate = False
        ingress = RecordingIngress()

        submissions: List[int] = []

        def recursive_normalizer(record):
            # Simulate an internal component that itself logs an error while
            # this very handler is already processing a record.
            if not getattr(recursive_normalizer, "_nested", False):
                recursive_normalizer._nested = True
                test_logger.error("nested failure while emitting")
                recursive_normalizer._nested = False
            submissions.append(1)
            return from_log_record(record, instance_id="i" * 32)

        handler = UnifiedLogHandler(ingress, recursive_normalizer)
        test_logger.addHandler(handler)
        try:
            test_logger.info("outer line")
        finally:
            test_logger.removeHandler(handler)

        self.assertLessEqual(len(submissions), 1)
        self.assertLessEqual(len(ingress.submitted), 1)


class TestFlushCloseAreNoOps(unittest.TestCase):
    def test_flush_and_close_are_fast_no_ops(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer())
        emit_via_handler(handler)
        self.assertEqual(len(ingress.submitted), 1)
        start = time.perf_counter()
        handler.flush()
        handler.close()
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.05)
        # G-7: no-ops must not touch anything already submitted/queued.
        self.assertEqual(len(ingress.submitted), 1)

    def test_flush_and_close_do_not_raise_even_without_health(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer(), health=None)
        try:
            handler.flush()
            handler.close()
        except Exception as exc:  # noqa: BLE001
            self.fail(f"flush()/close() must never raise: {exc!r}")


class TestInternalLoggerFilter(unittest.TestCase):
    def test_records_from_observability_internal_are_filtered_out(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer())
        record = logging.LogRecord(INTERNAL_LOGGER_NAME, logging.ERROR, "m.py",
                                    1, "internal failure", None, None)
        self.assertFalse(handler.filter(record))

    def test_regular_logger_records_pass_the_filter(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer())
        record = logging.LogRecord("controller", logging.INFO, "m.py", 1,
                                    "regular", None, None)
        self.assertTrue(handler.filter(record))


if __name__ == "__main__":
    unittest.main()
