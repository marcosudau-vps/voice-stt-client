"""
OBS-050 — settings: the sixth tab's metadata, the apply chain and the
ownership domains.

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §10.1 (schema), §10.2
(``_from_dict`` special case, Nachweis N-12), §10.3 (entries and apply
policies), §10.4 (the apply-chain line and its **hard rule**: a pure
observability change sets none of ``session_changed``/``audio_changed``/
``mode_changed``), §10.5 (documented, not repaired legacy), and
``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §8.7 (one level value, two filters),
§10.5 (client-local / session / server-wide configuration stay separate).
"""

from __future__ import annotations

import logging
import tempfile
import unittest
from pathlib import Path

from core.config import AppConfig, LoggingObservabilityConfig
from core.logging_settings_metadata import (
    ALL_SETTING_DEFINITIONS,
    CATEGORY,
    LOGGING_SETTING_DEFINITIONS,
)
from core.observability.ingress import NULL_INGRESS, ObservabilityIngress
from core.observability.manager import ObservabilityManager
from core.settings_metadata import (
    SETTING_DEFINITIONS,
    ApplyPolicy,
    SettingType,
    build_candidate,
    get_config_value,
)


class TestSettingsMetadata(unittest.TestCase):
    """§10.3 lists nine entries with their policies. This is that list."""

    EXPECTED = {
        "logging.observability.enabled": (SettingType.BOOLEAN, ApplyPolicy.IMMEDIATE),
        "logging.observability.level": (SettingType.CHOICE, ApplyPolicy.IMMEDIATE),
        "logging.observability.store_enabled": (
            SettingType.BOOLEAN, ApplyPolicy.APP_RESTART,
        ),
        "logging.observability.retention_days": (
            SettingType.INTEGER, ApplyPolicy.IMMEDIATE,
        ),
        "logging.observability.max_entries": (
            SettingType.INTEGER, ApplyPolicy.IMMEDIATE,
        ),
        "logging.observability.file_sink_enabled": (
            SettingType.BOOLEAN, ApplyPolicy.IMMEDIATE,
        ),
        "logging.observability.file_sink_dir": (
            SettingType.STRING, ApplyPolicy.IMMEDIATE,
        ),
        "logging.observability.store_transcription_content": (
            SettingType.BOOLEAN, ApplyPolicy.IMMEDIATE,
        ),
        "logging.observability.store_raw_payload": (
            SettingType.BOOLEAN, ApplyPolicy.IMMEDIATE,
        ),
    }

    def test_exactly_the_nine_frozen_entries(self):
        self.assertEqual(
            {definition.path for definition in LOGGING_SETTING_DEFINITIONS},
            set(self.EXPECTED),
        )

    def test_types_and_apply_policies(self):
        for definition in LOGGING_SETTING_DEFINITIONS:
            expected_type, expected_policy = self.EXPECTED[definition.path]
            with self.subTest(path=definition.path):
                self.assertIs(definition.setting_type, expected_type)
                self.assertIs(definition.apply_policy, expected_policy)

    def test_every_path_targets_the_typed_config(self):
        config = AppConfig()
        for definition in LOGGING_SETTING_DEFINITIONS:
            with self.subTest(path=definition.path):
                get_config_value(config, definition.path)

    def test_config_only_fields_are_absent_from_the_dialog(self):
        """§10.3: *"NUR in config.yaml, nicht im Dialog: db_path, queue_size,
        batch_size, flush_interval_s, max_db_bytes"*."""
        paths = {definition.path for definition in ALL_SETTING_DEFINITIONS}
        for field in (
            "db_path", "queue_size", "batch_size", "flush_interval_s", "max_db_bytes"
        ):
            with self.subTest(field=field):
                self.assertNotIn(f"logging.observability.{field}", paths)

    def test_all_entries_live_in_the_sixth_tab(self):
        self.assertEqual(
            {definition.category for definition in LOGGING_SETTING_DEFINITIONS},
            {CATEGORY},
        )

    def test_file_sink_dir_is_only_visible_with_the_sink_enabled(self):
        definition = next(
            item for item in LOGGING_SETTING_DEFINITIONS
            if item.path == "logging.observability.file_sink_dir"
        )
        self.assertEqual(
            definition.visible_when,
            ("logging.observability.file_sink_enabled", True),
        )

    def test_the_transcript_option_names_the_surprising_part(self):
        """FD-D1 requires the description to say that unstructured log lines
        are covered as well."""
        definition = next(
            item for item in LOGGING_SETTING_DEFINITIONS
            if item.path == "logging.observability.store_transcription_content"
        )
        self.assertIn("technische Logzeilen", definition.description)

    def test_composition_extends_the_existing_definitions(self):
        self.assertEqual(
            ALL_SETTING_DEFINITIONS,
            SETTING_DEFINITIONS + LOGGING_SETTING_DEFINITIONS,
        )

    def test_pure_settings_metadata_module_stays_free_of_observability(self):
        """§12.7 keeps ``settings_metadata`` *"bewusst rein"*, which is why
        the sixth tab's entries live in their own module."""
        root = Path(__file__).resolve().parents[1] / "core"
        source = (root / "settings_metadata.py").read_text(encoding="utf-8")
        self.assertNotIn("observability", source)


class TestCandidateBuilding(unittest.TestCase):
    def test_a_logging_change_produces_a_valid_candidate(self):
        candidate = build_candidate(
            AppConfig(),
            {
                "logging.observability.level": "DEBUG",
                "logging.observability.retention_days": 3,
                "logging.observability.store_transcription_content": True,
            },
        )
        self.assertEqual(candidate.logging.observability.level, "DEBUG")
        self.assertEqual(candidate.logging.observability.retention_days, 3)
        self.assertTrue(candidate.logging.observability.store_transcription_content)

    def test_an_invalid_level_is_rejected_by_validation(self):
        with self.assertRaises(ValueError):
            build_candidate(AppConfig(), {"logging.observability.level": "LOUD"})

    def test_a_path_outside_the_user_profile_is_rejected(self):
        """CONTRACTS §4.3 P-8, through the dialog's own candidate builder."""
        with self.assertRaises(ValueError):
            build_candidate(
                AppConfig(),
                {"logging.observability.file_sink_dir": "C:\\Windows\\Temp\\logs"},
            )

    def test_null_file_sink_dir_means_the_default(self):
        candidate = build_candidate(
            AppConfig(), {"logging.observability.file_sink_dir": None}
        )
        self.assertIsNone(candidate.logging.observability.file_sink_dir)

    def test_nested_section_survives_a_save_load_roundtrip(self):
        """§10.2 / Nachweis N-12: without the ``_from_dict`` special case the
        field would silently keep its defaults."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            config = AppConfig()
            config.logging.observability.retention_days = 7
            config.logging.observability.level = "WARNING"
            config.save(path)
            loaded = AppConfig._load_single(path)  # noqa: SLF001
            self.assertEqual(loaded.logging.observability.retention_days, 7)
            self.assertEqual(loaded.logging.observability.level, "WARNING")


class TestIngressOwnershipDomain(unittest.TestCase):
    """§10.4 + ARCH §5.2: the ingress applies what it owns and forwards the
    rest; it never learns what a worker or a store is."""

    def make_ingress(self):
        return ObservabilityIngress(instance_id="i-1", level="INFO")

    def test_ingress_applies_its_own_four_settings(self):
        ingress = self.make_ingress()
        ingress.apply_config(
            LoggingObservabilityConfig(
                level="ERROR",
                store_transcription_content=True,
                store_raw_payload=False,
            )
        )
        self.assertEqual(ingress.level, "ERROR")
        self.assertTrue(ingress.store_transcription_content)
        self.assertTrue(ingress.enabled)

    def test_disabling_stops_acceptance_and_re_enabling_restores_it(self):
        from core.observability.models import CanonicalLogRecord

        ingress = self.make_ingress()
        record = CanonicalLogRecord(
            record_id="r-1", received_at="2026-08-17T10:00:00.000Z",
            producer_kind="client", producer_id="voice-stt-client",
            instance_id="i-1", scope="instance", channel="system", level="INFO",
        )
        self.assertTrue(ingress.submit(record))
        ingress.apply_config(LoggingObservabilityConfig(enabled=False))
        self.assertFalse(ingress.submit(record))
        ingress.apply_config(LoggingObservabilityConfig(enabled=True))
        self.assertTrue(ingress.submit(record))

    def test_level_filter_follows_immediately(self):
        from core.observability.models import CanonicalLogRecord

        ingress = self.make_ingress()
        debug_record = CanonicalLogRecord(
            record_id="r-2", received_at="2026-08-17T10:00:00.000Z",
            producer_kind="client", producer_id="voice-stt-client",
            instance_id="i-1", scope="instance", channel="system", level="DEBUG",
        )
        self.assertFalse(ingress.submit(debug_record))
        ingress.apply_config(LoggingObservabilityConfig(level="DEBUG"))
        self.assertTrue(ingress.submit(debug_record))

    def test_an_unknown_level_keeps_the_current_one(self):
        ingress = self.make_ingress()
        ingress.apply_config(LoggingObservabilityConfig(level="INFO"))

        class Broken:
            level = "LOUD"

        ingress.apply_config(Broken())
        self.assertEqual(ingress.level, "INFO")

    def test_listeners_receive_the_configuration(self):
        ingress = self.make_ingress()
        seen = []
        ingress.register_config_listener(seen.append)
        ingress.register_config_listener(seen.append)  # idempotent
        config = LoggingObservabilityConfig(retention_days=2)
        ingress.apply_config(config)
        self.assertEqual(seen, [config])

    def test_a_raising_listener_never_escapes(self):
        ingress = self.make_ingress()

        def boom(_config):
            raise RuntimeError("listener exploded")

        ingress.register_config_listener(boom)
        ingress.apply_config(LoggingObservabilityConfig())  # must not raise

    def test_apply_config_returns_nothing_and_never_raises(self):
        ingress = self.make_ingress()
        self.assertIsNone(ingress.apply_config(None))
        self.assertIsNone(ingress.apply_config(object()))

    def test_null_ingress_stays_a_no_op(self):
        self.assertIsNone(NULL_INGRESS.apply_config(LoggingObservabilityConfig()))
        self.assertFalse(NULL_INGRESS.enabled)


class TestManagerOwnershipDomain(unittest.TestCase):
    """The manager applies the settings the ingress does not own — and only
    those. ``store_enabled``/``db_path`` are APP_RESTART (§10.3)."""

    def make_manager(self, **overrides):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "observability.sqlite3"
            config = LoggingObservabilityConfig(db_path=None, **overrides)
            manager = ObservabilityManager(config, log_dir=str(Path(directory) / "logs"))
            manager._db_path = path  # noqa: SLF001 - avoids touching %LOCALAPPDATA%
            return manager, path

    def test_handler_level_follows_the_single_config_value(self):
        """ARCH §8.7: one value feeds the handler AND the ingress filter."""
        manager, _path = self.make_manager()
        handler = logging.Handler()
        handler.setLevel(logging.INFO)
        manager.register_log_handler(handler)
        manager.ingress.apply_config(LoggingObservabilityConfig(level="ERROR"))
        self.assertEqual(handler.level, logging.ERROR)
        self.assertEqual(manager.ingress.level, "ERROR")

    def test_worker_receives_retention_entry_limit_and_sink(self):
        manager, _path = self.make_manager()
        received = []

        class WorkerSpy:
            def request_settings(self, **settings):
                received.append(settings)

        manager._worker = WorkerSpy()  # noqa: SLF001
        manager.ingress.apply_config(
            LoggingObservabilityConfig(retention_days=3, max_entries=99)
        )
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]["retention_days"], 3)
        self.assertEqual(received[0]["max_entries"], 99)
        self.assertIsNone(received[0]["sink"])

    def test_enabling_the_file_sink_hands_the_worker_a_sink(self):
        from core.observability.sinks.jsonl_file import JsonlSink

        manager, _path = self.make_manager()
        received = []

        class WorkerSpy:
            def request_settings(self, **settings):
                received.append(settings)

        manager._worker = WorkerSpy()  # noqa: SLF001
        manager.ingress.apply_config(
            LoggingObservabilityConfig(file_sink_enabled=True)
        )
        self.assertIsInstance(received[0]["sink"], JsonlSink)

    def test_store_enabled_and_db_path_are_not_applied_at_runtime(self):
        """APP_RESTART: the running worker keeps its open connection."""
        manager, path = self.make_manager()
        before = manager.db_path
        manager.ingress.apply_config(
            LoggingObservabilityConfig(store_enabled=False, db_path=None)
        )
        self.assertEqual(manager.db_path, before)
        self.assertEqual(manager.db_path, path)

    def test_health_follows_enabled_but_never_overwrites_a_failure(self):
        from core.observability.health import LoggingHealthState

        manager, _path = self.make_manager()
        manager.ingress.apply_config(LoggingObservabilityConfig(enabled=False))
        self.assertIs(manager.health.state, LoggingHealthState.DISABLED)
        manager.ingress.apply_config(LoggingObservabilityConfig(enabled=True))
        self.assertIs(manager.health.state, LoggingHealthState.OK)
        manager.health.set_state(LoggingHealthState.FAILED_STORE, "disk full")
        manager.ingress.apply_config(LoggingObservabilityConfig(enabled=True))
        self.assertIs(manager.health.state, LoggingHealthState.FAILED_STORE)

    def test_health_snapshot_is_available_for_the_status_line(self):
        manager, _path = self.make_manager()
        snapshot = manager.health_snapshot()
        self.assertEqual(snapshot.written, 0)
        self.assertIsNotNone(snapshot.state)

    def test_query_service_is_built_once_and_carries_the_local_provider(self):
        manager, path = self.make_manager()
        service = manager.query_service
        self.assertIs(service, manager.query_service)
        self.assertEqual(service.provider_ids(), ("local",))
        page = service.query("local", __import__(
            "core.observability.query.base", fromlist=["QueryFilter"]
        ).QueryFilter())
        self.assertEqual(page.records, ())
        self.assertFalse(path.exists())


class TestWorkerRuntimeSettings(unittest.TestCase):
    """The worker applies deposited settings on ITS thread (CONTRACTS §5.4:
    connection and sink ownership)."""

    def make_worker(self):
        from core.observability.worker import LoggingWorker

        class NullStore:
            def open(self):
                from core.observability.storage.sqlite import OpenResult

                return OpenResult(True, False, "")

            def write_batch(self, records):
                return (len(records), 0)

            def run_retention(self, **kwargs):
                return (0, 0)

            def measure_db_bytes(self):
                return None

            def probe_write(self):
                return True

            def close(self):
                return None

        ingress = ObservabilityIngress(instance_id="i-1")
        return LoggingWorker(ingress, NullStore())

    def test_settings_are_not_applied_before_the_worker_runs_them(self):
        worker = self.make_worker()
        worker.request_settings(retention_days=1, max_entries=2)
        self.assertEqual(worker._retention_days, 14)  # noqa: SLF001
        worker._apply_pending_settings()  # noqa: SLF001
        self.assertEqual(worker._retention_days, 1)  # noqa: SLF001
        self.assertEqual(worker._max_entries, 2)  # noqa: SLF001

    def test_only_provided_keys_change(self):
        worker = self.make_worker()
        worker.request_settings(retention_days=5)
        worker._apply_pending_settings()  # noqa: SLF001
        self.assertEqual(worker._retention_days, 5)  # noqa: SLF001
        self.assertEqual(worker._max_entries, 200_000)  # noqa: SLF001

    def test_switching_the_sink_off_closes_the_old_one(self):
        worker = self.make_worker()
        closed = []

        class SinkSpy:
            def close(self):
                closed.append(True)

            def write_batch(self, records):
                return None

        worker._sink = SinkSpy()  # noqa: SLF001
        worker.request_settings(sink=None)
        worker._apply_pending_settings()  # noqa: SLF001
        self.assertIsNone(worker._sink)  # noqa: SLF001
        self.assertEqual(closed, [True])

    def test_request_settings_never_raises(self):
        worker = self.make_worker()
        self.assertIsNone(worker.request_settings(retention_days=1))


class TestApplyChain(unittest.IsolatedAsyncioTestCase):
    """§10.4's hard rule, measured on the real ``apply_runtime_config``."""

    async def test_pure_observability_change_triggers_no_reconnect(self):
        from tests.obs050_apply_support import build_controller

        controller, session = build_controller()
        candidate = build_candidate(
            controller.config, {"logging.observability.level": "DEBUG"}
        )
        result = await controller.apply_runtime_config(candidate)
        self.assertTrue(result.success)
        # The fake session fails on reconfigure; reaching it at all would be
        # the violation.
        self.assertEqual(session.reconfigure_calls, 0)

    async def test_the_observability_config_reaches_the_ingress(self):
        from tests.obs050_apply_support import build_controller

        controller, _session = build_controller()
        candidate = build_candidate(
            controller.config, {"logging.observability.retention_days": 5}
        )
        await controller.apply_runtime_config(candidate)
        self.assertEqual(
            [config.retention_days for config in controller.observability.applied],
            [5],
        )

    async def test_a_raising_apply_config_does_not_fail_the_apply(self):
        """§10.4: *"ein Fehler dort darf das Apply-Ergebnis nicht
        beeinflussen"*."""
        from tests.obs050_apply_support import build_controller

        controller, _session = build_controller(apply_config_raises=True)
        candidate = build_candidate(
            controller.config, {"logging.observability.level": "WARNING"}
        )
        result = await controller.apply_runtime_config(candidate)
        self.assertTrue(result.success)

    async def test_an_ingress_without_apply_config_is_tolerated(self):
        """Pre-OBS-050 doubles have no such method; O-01 forbids the logging
        domain from deciding whether an apply succeeds."""
        from tests.obs050_apply_support import build_controller

        controller, _session = build_controller(apply_config_missing=True)
        candidate = build_candidate(
            controller.config, {"logging.observability.level": "WARNING"}
        )
        result = await controller.apply_runtime_config(candidate)
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
