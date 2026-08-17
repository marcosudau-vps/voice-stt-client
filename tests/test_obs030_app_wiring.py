"""
Tests for the ``app.py::main()`` observability wiring (OBS-030).

Frozen source: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §6.2 AR-5/AR-6
(``AppConfig.load() -> Manager bauen und starten -> setup_logging(...)``;
manager lifetime in ``app.py::main()``'s ``try/finally``, stopped after the
headless/gui path returns — regardless of success, headless mode, or an
exception).
"""

from __future__ import annotations

import unittest
from unittest import mock

import app


class TestObservabilityManagerLifecycleInMain(unittest.TestCase):
    def test_headless_path_starts_and_stops_the_manager_in_order(self):
        calls: list[str] = []

        class FakeManager:
            def __init__(self, config, **kwargs):
                calls.append("__init__")
                self.config = config

            def start(self):
                calls.append("start")

            def stop(self, timeout=2.0):
                calls.append(f"stop:{timeout}")
                return True

            @property
            def level(self):
                return "INFO"

            @property
            def ingress(self):
                return None

        def fake_run_headless(config):
            calls.append("run_headless")
            return 0

        with mock.patch("core.observability.manager.ObservabilityManager", FakeManager), \
             mock.patch.object(app, "run_headless", fake_run_headless), \
             mock.patch.object(app, "setup_logging") as fake_setup_logging:
            exit_code = app.main(["--headless"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(calls, ["__init__", "start", "run_headless", "stop:2.0"])
        fake_setup_logging.assert_called_once()
        _, kwargs = fake_setup_logging.call_args
        self.assertIn("observability", kwargs)

    def test_manager_is_stopped_even_if_headless_run_raises(self):
        calls: list[str] = []

        class FakeManager:
            def __init__(self, config, **kwargs):
                calls.append("__init__")

            def start(self):
                calls.append("start")

            def stop(self, timeout=2.0):
                calls.append("stop")
                return True

            @property
            def level(self):
                return "INFO"

            @property
            def ingress(self):
                return None

        def fake_run_headless(config):
            raise RuntimeError("boom")

        with mock.patch("core.observability.manager.ObservabilityManager", FakeManager), \
             mock.patch.object(app, "run_headless", fake_run_headless), \
             mock.patch.object(app, "setup_logging"):
            with self.assertRaises(RuntimeError):
                app.main(["--headless"])

        self.assertEqual(calls, ["__init__", "start", "stop"])


if __name__ == "__main__":
    unittest.main()
