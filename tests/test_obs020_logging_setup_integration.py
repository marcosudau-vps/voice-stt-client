"""
Integration tests for the additive ``observability`` parameter of
``core.logging_setup.setup_logging`` (OBS-020).

Frozen source: WP-OBS-020 Sollzustand / ``LOGGING_CONTRACTS_FREEZE_V1.md`` §6.
"""

from __future__ import annotations

import logging
import tempfile
import unittest
from pathlib import Path

from core.config import LoggingConfig
from core.logging_setup import setup_logging
from core.observability.adapters.python_logging import UnifiedLogHandler
from core.observability.health import LoggingInternalHealth
from core.observability.ingress import ObservabilityIngress


class FakeObservability:
    """Stand-in for the future ``ObservabilityManager`` (OBS-030). Only
    ``.ingress`` and ``.level`` are part of the frozen Sollzustand — nothing
    else is invented on this composition root at OBS-020 stage."""

    def __init__(self, ingress, level="INFO"):
        self.ingress = ingress
        self.level = level


def _make_config(tmp_dir: str) -> LoggingConfig:
    return LoggingConfig(
        level="INFO", log_dir=tmp_dir, max_bytes=1_000_000, backup_count=1,
        stdout=True, json_format=True, channel_levels={},
    )


class TestBackwardCompatibility(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(logging.getLogger().handlers.clear)

    def test_without_observability_param_behaves_exactly_as_before(self):
        config = _make_config(self._tmp.name)
        setup_logging(config)
        root = logging.getLogger()
        self.assertEqual(len(root.handlers), 2)  # file + stdout, unchanged
        for handler in root.handlers:
            self.assertNotIsInstance(handler, UnifiedLogHandler)

    def test_file_and_stdout_output_identical_with_and_without_observability(self):
        config_a = _make_config(str(Path(self._tmp.name) / "a"))
        Path(config_a.log_dir).mkdir(parents=True, exist_ok=True)
        setup_logging(config_a)
        logging.getLogger("controller").info("identical line %s", 1)
        content_without = (Path(config_a.log_dir) / "client.log").read_text(encoding="utf-8")

        ingress = ObservabilityIngress(instance_id="i" * 32)
        observability = FakeObservability(ingress, level="INFO")
        config_b = _make_config(str(Path(self._tmp.name) / "b"))
        Path(config_b.log_dir).mkdir(parents=True, exist_ok=True)
        setup_logging(config_b, observability=observability)
        logging.getLogger("controller").info("identical line %s", 1)
        content_with = (Path(config_b.log_dir) / "client.log").read_text(encoding="utf-8")

        # Both files carry one "Logging initialized" line first; strip it and
        # compare the actual application line, which must be structurally
        # identical (the third handler must not alter file/stdout output at
        # all). Only "ts" legitimately differs between the two runs.
        import json
        line_without = next(ln for ln in content_without.splitlines() if "identical line" in ln)
        line_with = next(ln for ln in content_with.splitlines() if "identical line" in ln)
        parsed_without = json.loads(line_without)
        parsed_with = json.loads(line_with)
        del parsed_without["ts"]
        del parsed_with["ts"]
        self.assertEqual(parsed_without, parsed_with)


class TestObservabilityWiring(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(logging.getLogger().handlers.clear)

    def test_third_handler_is_added_and_level_set_from_observability(self):
        config = _make_config(self._tmp.name)
        ingress = ObservabilityIngress(instance_id="i" * 32)
        observability = FakeObservability(ingress, level="WARNING")
        setup_logging(config, observability=observability)
        root = logging.getLogger()
        unified = [h for h in root.handlers if isinstance(h, UnifiedLogHandler)]
        self.assertEqual(len(unified), 1)
        self.assertEqual(unified[0].level, logging.WARNING)

    def test_logging_through_root_reaches_the_ingress(self):
        config = _make_config(self._tmp.name)
        ingress = ObservabilityIngress(instance_id="i" * 32, queue_size=10)
        observability = FakeObservability(ingress, level="INFO")
        setup_logging(config, observability=observability)
        logging.getLogger("controller").info("via root logger")
        self.assertEqual(ingress.qsize(), 1)

    def test_double_setup_logging_call_yields_exactly_one_unified_handler(self):
        config = _make_config(self._tmp.name)
        ingress = ObservabilityIngress(instance_id="i" * 32)
        observability = FakeObservability(ingress, level="INFO")
        setup_logging(config, observability=observability)
        setup_logging(config, observability=observability)
        root = logging.getLogger()
        unified = [h for h in root.handlers if isinstance(h, UnifiedLogHandler)]
        self.assertEqual(len(unified), 1)
        self.assertEqual(len(root.handlers), 3)  # file + stdout + unified


if __name__ == "__main__":
    unittest.main()
