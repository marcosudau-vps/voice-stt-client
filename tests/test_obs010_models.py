"""
Contract tests for ``core.observability.models`` (OBS-010).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §1 and §2.1.
Field-by-field comparison anchor is the table in §1.1 — no field outside the
frozen record is constructed or asserted here.
"""

from __future__ import annotations

import unittest
from types import MappingProxyType

from core.observability.models import (
    CanonicalLogRecord,
    Channel,
    Level,
    ProducerKind,
    RecordPriority,
    Scope,
    level_rank,
)


def make_record(**changes):
    values = {
        "record_id": "a" * 32,
        "received_at": "2026-08-17T00:00:00.000Z",
        "producer_kind": "client",
        "producer_id": "voice-stt-client",
        "instance_id": "i" * 32,
        "scope": "instance",
        "channel": "system",
        "level": "INFO",
    }
    values.update(changes)
    return CanonicalLogRecord(**values)


class TestModelInvariants(unittest.TestCase):
    def test_all_frozen_fields_match_contract_2020611_table_11(self):
        record = make_record()
        # Fields exactly as in CONTRACTS §1.1 / §1.4 (identity, time, producer,
        # scope/channel/level, replay, source timestamp, type, component,
        # correlation fields, message, details, raw, is_internal).
        self.assertEqual(
            {
                "record_id", "received_at", "producer_kind", "producer_id",
                "instance_id", "scope", "channel", "level", "replayed",
                "source_timestamp", "type", "component", "session_id",
                "generation", "activation_id", "segment_id",
                "transcription_id", "command_id", "event_id",
                "correlation_id", "server_cursor", "message", "details",
                "raw", "is_internal",
            },
            set(record.__dataclass_fields__),
        )
        # Ausdruecklich NICHT im Record (§1.1):
        for forbidden in ("monotonic_ns", "host", "process_id", "sequence",
                          "provider_id", "source_record_id", "schema_version"):
            self.assertNotIn(forbidden, set(record.__dataclass_fields__))

    def test_details_are_frozen_after_construction(self):
        details = {"k": [1, {"n": 2}], "s": {"a", "b"}}
        record = make_record(details=details)
        self.assertIsInstance(record.details, MappingProxyType)
        self.assertIsInstance(record.details["k"], tuple)
        self.assertIsInstance(record.details["s"], frozenset)
        self.assertEqual(record.details["k"][1], {"n": 2})
        # Input payload is never mutated (no mutation of passed payloads).
        self.assertIsInstance(details, dict)
        self.assertIsInstance(details["k"], list)

    def test_raw_is_frozen_after_construction(self):
        raw = {"payload": {"nested": [1, 2]}}
        record = make_record(raw=raw)
        self.assertIsInstance(record.raw, MappingProxyType)
        self.assertEqual(record.raw["payload"]["nested"], (1, 2))
        self.assertIsInstance(record.raw["payload"]["nested"], tuple)
        self.assertIsInstance(raw, dict)

    def test_record_is_frozen_and_details_are_immutable(self):
        record = make_record()
        with self.assertRaises(AttributeError):
            record.channel = "audit"
        with self.assertRaises(TypeError):
            record.details["extra"] = 1  # MappingProxyType

    def test_already_frozen_server_payload_is_not_copied_on_build(self):
        frozen = MappingProxyType({"event": MappingProxyType({"x": 1})})
        record = make_record(details=frozen)
        self.assertIs(record.details, frozen)

    def test_optional_fields_default_to_none_required_are_present(self):
        record = make_record()
        for optional in (
            "source_timestamp", "type", "component", "session_id",
            "generation", "activation_id", "segment_id", "transcription_id",
            "command_id", "event_id", "correlation_id", "server_cursor",
            "message", "raw",
        ):
            self.assertIsNone(getattr(record, optional))
        self.assertEqual(record.replayed, False)
        self.assertEqual(record.is_internal, False)


class TestEnumValueSets(unittest.TestCase):
    def test_producer_kind_closed_set(self):
        self.assertEqual(
            {kind.value for kind in ProducerKind},
            {"client", "server", "led", "other"},
        )

    def test_scope_closed_set(self):
        self.assertEqual(
            {scope.value for scope in Scope},
            {"session", "instance", "global"},
        )

    def test_level_closed_set(self):
        self.assertEqual(
            {level.value for level in Level},
            {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"},
        )

    def test_channel_canonical_four(self):
        self.assertEqual(
            {channel.value for channel in Channel},
            {"system", "audit", "transcription", "performance"},
        )

    def test_unknown_enum_values_are_rejected(self):
        for cls in (ProducerKind, Level, Scope):
            with self.subTest(cls=cls.__name__):
                with self.assertRaises(ValueError):
                    cls("bogus")

    def test_level_rank_defaults_to_info_for_unknown(self):
        self.assertLess(level_rank("DEBUG"), level_rank("INFO"))
        self.assertGreaterEqual(level_rank("WARNING"), level_rank("WARNING"))
        self.assertEqual(level_rank("CRITICAL"), 4)
        self.assertEqual(level_rank("VERBOSE"), level_rank("INFO"))


class TestPfieldValidation(unittest.TestCase):
    def test_required_string_fields_must_be_nonempty(self):
        for field_name in ("record_id", "received_at", "producer_kind",
                           "producer_id", "instance_id", "scope", "channel",
                           "level"):
            with self.subTest(field=field_name):
                with self.assertRaises(ValueError):
                    make_record(**{field_name: " "})

    def test_producer_kind_outside_closed_set_rejected(self):
        with self.assertRaises(ValueError):
            make_record(producer_kind="other_host")

    def test_scope_outside_closed_set_rejected(self):
        with self.assertRaises(ValueError):
            make_record(scope="derived")

    def test_level_outside_closed_set_rejected(self):
        with self.assertRaises(ValueError):
            make_record(level="VERBOSE")

    def test_replayed_and_is_internal_must_be_booleans(self):
        for field_name in ("replayed", "is_internal"):
            with self.subTest(field=field_name):
                with self.assertRaises(ValueError):
                    make_record(**{field_name: 1})
                with self.assertRaises(ValueError):
                    make_record(**{field_name: "yes"})

    def test_segment_id_negative_or_bool_rejected(self):
        for bad in (-1, True, 1.5):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    make_record(segment_id=bad)

    def test_generation_negative_rejected(self):
        with self.assertRaises(ValueError):
            make_record(generation=-1)

    def test_details_must_be_a_mapping(self):
        with self.assertRaises(ValueError):
            make_record(details=[1, 2, 3])
        with self.assertRaises(ValueError):
            make_record(details="text")

    def test_raw_must_be_mapping_or_none(self):
        with self.assertRaises(ValueError):
            make_record(raw=[1, 2, 3])

    def test_optional_string_fields_must_be_nonempty_when_set(self):
        for field_name in ("type", "component", "session_id",
                           "transcription_id", "command_id", "correlation_id"):
            with self.subTest(field=field_name):
                with self.assertRaises(ValueError):
                    make_record(**{field_name: "  "})


class TestPriorityDerivation(unittest.TestCase):
    """Priority derivation frozen in §1.5 / FD-R1::

        HIGH  := is_internal or (not replayed and (level >= WARNING or
                 channel == audit or type is not None)) else LOW
    """

    def test_warning_level_is_high(self):
        self.assertEqual(
            make_record(level="WARNING").priority, RecordPriority.HIGH
        )

    def test_audit_channel_is_high_even_at_info(self):
        record = make_record(level="INFO", channel="audit")
        self.assertEqual(record.priority, RecordPriority.HIGH)

    def test_typed_event_is_high(self):
        record = make_record(level="DEBUG", type="transcription.completed")
        self.assertEqual(record.priority, RecordPriority.HIGH)

    def test_internal_is_high(self):
        record = make_record(level="DEBUG", is_internal=True)
        self.assertEqual(record.priority, RecordPriority.HIGH)

    def test_plain_info_is_low(self):
        record = make_record(level="INFO", channel="system", type=None)
        self.assertEqual(record.priority, RecordPriority.LOW)

    def test_debug_without_criteria_is_low(self):
        record = make_record(level="DEBUG", channel="transcription")
        self.assertEqual(record.priority, RecordPriority.LOW)

    def test_replayed_forced_low_even_with_type_and_error(self):
        record = make_record(
            level="ERROR", type="transcription.completed", replayed=True
        )
        self.assertEqual(record.priority, RecordPriority.LOW)

    def test_replayed_audit_is_low(self):
        record = make_record(level="INFO", channel="audit", replayed=True)
        self.assertEqual(record.priority, RecordPriority.LOW)

    def test_internal_wins_over_replayed(self):
        record = make_record(level="DEBUG", replayed=True, is_internal=True)
        self.assertEqual(record.priority, RecordPriority.HIGH)


if __name__ == "__main__":
    unittest.main()