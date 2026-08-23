"""
Contract / isolation tests for OBS-020 (``health.py``, ``ingress.py``,
``adapters/python_logging.py``).

Frozen source: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §5.2 (layering/import
direction), §8.1 (G-1..G-7), WP-OBS-020 Contract-Tests.
"""

from __future__ import annotations

import inspect
import logging
import subprocess
import sys
import unittest
from pathlib import Path

from core.observability.health import EMERGENCY_LOGGER_NAME
from core.observability.ingress import ObservabilityIngress

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OBSERVABILITY_DIR = PROJECT_ROOT / "core" / "observability"


class TestModuleIsolation(unittest.TestCase):
    def test_health_imports_neither_event_models_nor_feedback_reducer(self):
        """G-5 / Regel: kein Logging-Fehler geht ueber den Feedbackweg. Der
        Nachweis, dass kein Feedbackweg entstehen kann. Only actual import
        statements are checked — the module docstring is free to name these
        modules in prose (it does, to state the very rule this test guards)."""
        text = (OBSERVABILITY_DIR / "health.py").read_text(encoding="utf-8")
        imports = "\n".join(
            line for line in text.splitlines()
            if line.strip().startswith(("import ", "from "))
        )
        self.assertNotIn("event_models", imports)
        self.assertNotIn("feedback_reducer", imports)

    def test_no_pyside6_or_qtcore_in_new_obs020_modules(self):
        for relative in ("health.py", "ingress.py", "adapters/__init__.py",
                         "adapters/python_logging.py"):
            path = OBSERVABILITY_DIR / relative
            with self.subTest(path=relative):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("PySide6", text)
                self.assertNotIn("QtCore", text)

    def test_ingress_module_does_not_import_sqlite3(self):
        text = (OBSERVABILITY_DIR / "ingress.py").read_text(encoding="utf-8")
        self.assertNotIn("sqlite3", text)

    def test_python_logging_handler_holds_no_runtime_references(self):
        """The handler must not import or reference controller/session/
        coordinator objects — it queries no session state (CONTRACTS §3.1 /
        FD-R8, WP-OBS-020 Implementierungsschritt 6)."""
        text = (OBSERVABILITY_DIR / "adapters" / "python_logging.py").read_text(
            encoding="utf-8"
        )
        for forbidden in ("session_coordinator", "core.controller",
                          "stt_session", "audio_capture", "core_bridge"):
            self.assertNotIn(forbidden, text)


class TestAcyclicImports(unittest.TestCase):
    def test_every_obs020_module_imports_in_a_fresh_interpreter(self):
        modules = [
            "core.observability",
            "core.observability.health",
            "core.observability.ingress",
            "core.observability.adapters",
            "core.observability.adapters.python_logging",
            "core.logging_setup",
        ]
        for module in modules:
            with self.subTest(module=module):
                completed = subprocess.run(
                    [sys.executable, "-c", f"import {module}"],
                    cwd=PROJECT_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                self.assertEqual(
                    completed.returncode, 0,
                    msg=f"{module}: {completed.stderr[-400:]}",
                )


class TestEmergencyLoggerContract(unittest.TestCase):
    def test_observability_internal_logger_never_propagates(self):
        self.assertFalse(logging.getLogger(EMERGENCY_LOGGER_NAME).propagate)


class TestIngressSignatures(unittest.TestCase):
    """CONTRACTS §6: ``submit``/``observe_server_result``/``event``/``drain``."""

    def test_submit_signature(self):
        signature = inspect.signature(ObservabilityIngress.submit)
        self.assertIn("record", signature.parameters)

    def test_observe_server_result_signature(self):
        signature = inspect.signature(ObservabilityIngress.observe_server_result)
        self.assertIn("context", signature.parameters)
        self.assertIn("result", signature.parameters)

    def test_drain_signature(self):
        signature = inspect.signature(ObservabilityIngress.drain)
        self.assertIn("max_items", signature.parameters)
        self.assertIn("timeout", signature.parameters)

    def test_event_signature_matches_frozen_ingress_protocol(self):
        from core.observability.ingress import Ingress
        protocol_sig = inspect.signature(Ingress.event)
        concrete_sig = inspect.signature(ObservabilityIngress.event)
        self.assertEqual(list(protocol_sig.parameters), list(concrete_sig.parameters))


class TestLoggingSetupSignature(unittest.TestCase):
    def test_setup_logging_observability_parameter_is_optional_keyword_only(self):
        from core.logging_setup import setup_logging
        signature = inspect.signature(setup_logging)
        self.assertIn("observability", signature.parameters)
        parameter = signature.parameters["observability"]
        self.assertEqual(parameter.kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertIsNone(parameter.default)


if __name__ == "__main__":
    unittest.main()
