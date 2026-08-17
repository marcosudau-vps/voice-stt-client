"""
Contract tests for the Python-``LogRecord`` input of the normalizer (OBS-010).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §3.1 and FD-R2/FD-R8.
"""

from __future__ import annotations

import logging
import sys
import unittest

from core.observability.normalizer import (
    LOGGER_CHANNEL_MAP,
    from_log_record,
)


def make_record(logger_name="controller", level=logging.INFO, message="test",
                args=None, extras=None, exc_info=None):
    record = logging.LogRecord(
        logger_name, level, "module.py", 42, message, args, exc_info
    )
    for key, value in (extras or {}).items():
        record.__dict__[key] = value
    return record


class TestPythonLogMapping(unittest.TestCase):
    def test_info_record_from_controller_logger(self):
        record = make_record("controller", logging.INFO, "core gestartet")
        result = from_log_record(record, instance_id="i" * 32)
        self.assertIsNotNone(result)
        self.assertEqual(result.channel, "system")
        self.assertEqual(result.component, "controller")
        self.assertIsNone(result.type)
        self.assertEqual(result.message, "core gestartet")
        self.assertEqual(result.producer_kind, "client")
        self.assertEqual(result.producer_id, "voice-stt-client")
        self.assertEqual(result.level, "INFO")
        self.assertEqual(result.scope, "instance")
        self.assertEqual(result.replayed, False)
        self.assertEqual(result.details["logger"], "controller")
        self.assertEqual(result.details["line"], 42)

    def test_text_logger_maps_to_transcription_channel(self):
        record = make_record("text", logging.INFO, "zeile")
        result = from_log_record(record, instance_id="i" * 32)
        self.assertEqual(result.channel, "transcription")

    def test_any_other_logger_name_is_system(self):
        for logger_name in ("audio", "connection", "controller",
                            "event_stream", "core.controller",
                            "ui.core_bridge", "lefx.anything"):
            with self.subTest(logger=logger_name):
                result = from_log_record(
                    make_record(logger_name), instance_id="i" * 32
                )
                self.assertEqual(result.channel, "system")

    def test_logger_channel_map_has_only_text(self):
        self.assertEqual(LOGGER_CHANNEL_MAP, {"text": "transcription"})

    def test_type_is_none_from_logger_names(self):
        record = make_record("controller", level=logging.WARNING,
                             message="warnung")
        result = from_log_record(record, instance_id="i" * 32)
        self.assertIsNone(result.type)

    def test_lefx_logger_is_led_producer_with_system_channel(self):
        record = make_record("lefx.device.respeaker.transport",
                             logging.INFO, "led rausgeworfen")
        result = from_log_record(record, instance_id="i" * 32)
        self.assertEqual(result.producer_kind, "led")
        self.assertEqual(result.producer_id, "respeaker-led-controller")
        self.assertEqual(result.component, "lefx.device.respeaker.transport")
        self.assertEqual(result.channel, "system")  # lefx aendert nur Producer
        self.assertEqual(result.scope, "instance")  # ohne session -> instance

    def test_four_existing_extra_fields_land_in_details(self):
        record = make_record(
            "controller", extras={
                "session_id": "session-1",
                "segment_id": 7,
                "event_type": "final",
                "detail": "schnell",
            }
        )
        result = from_log_record(record, instance_id="i" * 32)
        self.assertEqual(result.details["session_id"], "session-1")
        self.assertEqual(result.details["segment_id"], 7)
        self.assertEqual(result.details["event_type"], "final")
        self.assertEqual(result.details["detail"], "schnell")


class TestPythonLogCorrelation(unittest.TestCase):
    def test_session_and_generation_come_only_from_record_dict(self):
        """CONTRACTS §3.1 / FD-R8: session_id/generation/segment_id come
        exclusively from ``record.__dict__`` — even if the signature
        parameters carry values."""
        record = make_record(extras={"session_id": "extra-session",
                                     "generation": 9,
                                     "segment_id": 4})
        result = from_log_record(
            record,
            instance_id="i" * 32,
            session_id="parameter-session",
            generation=99,
        )
        self.assertEqual(result.session_id, "extra-session")
        self.assertEqual(result.generation, 9)
        self.assertEqual(result.segment_id, 4)

    def test_without_extra_correlation_is_none(self):
        result = from_log_record(make_record(), instance_id="i" * 32)
        self.assertIsNone(result.session_id)
        self.assertIsNone(result.generation)
        self.assertIsNone(result.segment_id)

    def test_scope_is_session_when_record_has_session(self):
        record = make_record(extras={"session_id": "session-9"})
        result = from_log_record(record, instance_id="i" * 32)
        self.assertEqual(result.scope, "session")

    def test_malformed_extra_correlation_rejects_the_record(self):
        """Verwerfen statt Reparieren: a malformed extra correlation is not
        silently coerced — the model gate rejects the record (None)."""
        record = make_record(extras={"session_id": 5, "generation": True},
                             message="halte durch")
        result = from_log_record(record, instance_id="i" * 32)
        self.assertIsNone(result)


class TestPythonLogTime(unittest.TestCase):
    def test_source_timestamp_is_iso8601_utc_with_z(self):
        record = make_record()
        result = from_log_record(record, instance_id="i" * 32)
        self.assertIsNotNone(result)
        pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z"
        self.assertRegex(result.source_timestamp, pattern)

    def test_received_at_is_full_timestamp(self):
        result = from_log_record(make_record(), instance_id="i" * 32)
        self.assertIn("Z", result.received_at)
        self.assertIsNotNone(result.record_id)
        self.assertEqual(len(result.record_id), 32)


class TestPythonLogNegative(unittest.TestCase):
    def test_msg_placeholders_without_args_do_not_raise(self):
        record = make_record(
            "text", logging.INFO, "Final [seg=%s]: %s", args=()
        )
        result = from_log_record(record, instance_id="i" * 32)
        self.assertIsNotNone(result)
        self.assertIn("%s", result.message)

    def test_exc_info_whose_format_raising_does_not_break_record(self):
        class ExplodingError(Exception):
            def __str__(self):
                raise RuntimeError("exploding __str__")

        try:
            raise ExplodingError("dont care")
        except ExplodingError:
            exc_info = sys.exc_info()
        record = make_record("controller", logging.ERROR, "kaputt",
                             exc_info=exc_info)
        result = from_log_record(record, instance_id="i" * 32)
        self.assertIsNotNone(result)
        self.assertEqual(result.level, "ERROR")

    def test_exc_info_rendered_into_details_exception(self):
        try:
            raise ValueError("bombe")
        except ValueError:
            exc_info = sys.exc_info()
        record = make_record("controller", logging.ERROR, "kaputt",
                             exc_info=exc_info)
        result = from_log_record(record, instance_id="i" * 32)
        self.assertIsNotNone(result)
        self.assertIn("ValueError: bombe", result.details["exception"])

    def test_non_logrecord_input_is_none_not_raised(self):
        self.assertIsNone(from_log_record(object(), instance_id="i" * 32))

    def test_missing_instance_id_yields_none(self):
        self.assertIsNone(from_log_record(make_record(), instance_id=" "))


if __name__ == "__main__":
    unittest.main()