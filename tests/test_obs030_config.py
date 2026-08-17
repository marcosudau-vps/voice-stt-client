"""
Tests for the ``logging.observability`` config sub-section added in OBS-030
(``core/config.py``, ``LoggingObservabilityConfig``).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §10.1/§10.2.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.config import (
    DEFAULT_LOCAL_APP_DIR,
    AppConfig,
    LoggingConfig,
    LoggingObservabilityConfig,
)

# CONTRACTS §4.3 P-8 (implemented in RUN-OBS-030-02): a configured store or
# sink path must resolve inside the user profile. The round-trip below needs a
# path that is valid under that rule; the earlier literal ``C:/tmp/obs-sink``
# is exactly the case P-8 forbids and now has its own negative test in
# ``tests/test_obs030_path_boundaries.py``.
SINK_DIR_INSIDE_PROFILE = str(DEFAULT_LOCAL_APP_DIR / "obs-sink")


class TestDefaults(unittest.TestCase):
    def test_defaults_match_frozen_schema(self):
        cfg = LoggingObservabilityConfig()
        self.assertTrue(cfg.enabled)
        self.assertEqual(cfg.level, "INFO")
        self.assertTrue(cfg.store_enabled)
        self.assertIsNone(cfg.db_path)
        self.assertEqual(cfg.retention_days, 14)
        self.assertEqual(cfg.max_entries, 200_000)
        self.assertEqual(cfg.max_db_bytes, 268_435_456)
        self.assertEqual(cfg.queue_size, 8192)
        self.assertEqual(cfg.batch_size, 200)
        self.assertEqual(cfg.flush_interval_s, 0.5)
        self.assertFalse(cfg.file_sink_enabled)
        self.assertIsNone(cfg.file_sink_dir)
        self.assertFalse(cfg.store_transcription_content)
        self.assertTrue(cfg.store_raw_payload)

    def test_app_config_has_observability_by_default(self):
        cfg = AppConfig()
        self.assertIsInstance(cfg.logging.observability, LoggingObservabilityConfig)
        cfg.validate()  # must not raise


class TestValidation(unittest.TestCase):
    def test_negative_invalid_level_raises(self):
        with self.assertRaises(ValueError):
            LoggingObservabilityConfig(level="TRACE").validate()

    def test_negative_negative_retention_days_raises(self):
        with self.assertRaises(ValueError):
            LoggingObservabilityConfig(retention_days=-1).validate()

    def test_negative_zero_queue_size_raises(self):
        with self.assertRaises(ValueError):
            LoggingObservabilityConfig(queue_size=0).validate()

    def test_negative_non_positive_flush_interval_raises(self):
        with self.assertRaises(ValueError):
            LoggingObservabilityConfig(flush_interval_s=0).validate()

    def test_positive_valid_config_does_not_raise(self):
        LoggingObservabilityConfig(
            level="DEBUG", retention_days=0, max_entries=0, max_db_bytes=0,
        ).validate()


class TestSaveLoadRoundTrip(unittest.TestCase):
    def test_non_default_observability_values_survive_save_and_load(self):
        """This is the exact scenario that would silently corrupt
        ``logging.observability`` into a raw dict without the
        ``_from_dict`` special-casing added in this run (CONTRACTS §10.2)."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            cfg = AppConfig()
            cfg.logging.observability = LoggingObservabilityConfig(
                enabled=False,
                level="ERROR",
                store_enabled=False,
                retention_days=30,
                max_entries=5000,
                queue_size=512,
                batch_size=50,
                flush_interval_s=1.5,
                file_sink_enabled=True,
                file_sink_dir=SINK_DIR_INSIDE_PROFILE,
                store_transcription_content=True,
                store_raw_payload=False,
            )
            cfg.save(path)

            loaded = AppConfig.load(path)
            observability = loaded.logging.observability
            self.assertIsInstance(observability, LoggingObservabilityConfig)
            self.assertFalse(observability.enabled)
            self.assertEqual(observability.level, "ERROR")
            self.assertFalse(observability.store_enabled)
            self.assertEqual(observability.retention_days, 30)
            self.assertEqual(observability.max_entries, 5000)
            self.assertEqual(observability.queue_size, 512)
            self.assertEqual(observability.batch_size, 50)
            self.assertEqual(observability.flush_interval_s, 1.5)
            self.assertTrue(observability.file_sink_enabled)
            self.assertEqual(observability.file_sink_dir, SINK_DIR_INSIDE_PROFILE)
            self.assertTrue(observability.store_transcription_content)
            self.assertFalse(observability.store_raw_payload)
            loaded.validate()  # must not raise

    def test_absent_observability_section_still_yields_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text("logging:\n  level: DEBUG\n", encoding="utf-8")
            loaded = AppConfig.load(path)
            self.assertEqual(loaded.logging.level, "DEBUG")
            self.assertIsInstance(loaded.logging.observability, LoggingObservabilityConfig)
            self.assertTrue(loaded.logging.observability.enabled)

    def test_unknown_observability_key_is_ignored_not_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text(
                "logging:\n  observability:\n    enabled: false\n    made_up_field: 123\n",
                encoding="utf-8",
            )
            loaded = AppConfig.load(path)
            self.assertFalse(loaded.logging.observability.enabled)


if __name__ == "__main__":
    unittest.main()
