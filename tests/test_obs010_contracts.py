"""
Contract / isolation tests for ``core.observability`` (OBS-010).

Frozen source: ARCH §5.2 (Schichtung und Importrichtung), WP-OBS-010
Contract-Tests and Mutation-Checks (MT-1/MT-2 are verified manually in the
run; their guards live here).
"""

from __future__ import annotations

import inspect
import subprocess
import sys
import unittest
from pathlib import Path

from core.observability import redaction
from core.observability.ingress import Ingress

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OBSERVABILITY_DIR = PROJECT_ROOT / "core" / "observability"


class TestModuleIsolation(unittest.TestCase):
    """client-tested rules:

    - ``core/observability/**`` imports neither ``PySide6`` nor ``QtCore``.
    - ``models.py`` imports nothing from its own package.
    - ``normalizer.py`` imports no ``sqlite3`` and no runtime objects
      (controller/session/coordinator).
    """

    @staticmethod
    def _sources():
        results = []
        for path in OBSERVABILITY_DIR.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            results.append(path)
        return results

    def test_no_pyside6_or_qtcore_anywhere(self):
        for path in self._sources():
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("PySide6", text)
                self.assertNotIn("QtCore", text)

    def test_no_sqlite_import_in_normalizer(self):
        text = (OBSERVABILITY_DIR / "normalizer.py").read_text(encoding="utf-8")
        self.assertNotIn("sqlite3", text)

    def test_models_imports_nothing_from_own_package(self):
        text = (OBSERVABILITY_DIR / "models.py").read_text(encoding="utf-8")
        self.assertNotIn("from .", text)
        self.assertNotIn("from core.observability", text)

    def test_normalizer_imports_no_runtime_objects(self):
        """The normalizer must neither import nor reference the runtime
        objects (controller/session/coordinator): its correlation fields come
        from ``record.__dict__`` (CONTRACTS §3.1 / FD-R8)."""
        text = (OBSERVABILITY_DIR / "normalizer.py").read_text(encoding="utf-8")
        imports = "".join(
            line for line in text.splitlines()
            if line.strip().startswith(("import ", "from "))
        )
        imports = imports.replace("from __future__", "")
        for forbidden in ("session_coordinator", "controller", "stt_session",
                          "audio_capture", "core_bridge", "application"):
            self.assertNotIn(forbidden, imports)
        # Normative source rule (CONTRACTS §3.1 / FD-R8) enforced in code:
        self.assertIn('record.__dict__.get("session_id")', text)
        self.assertIn('record.__dict__.get("generation")', text)
        self.assertIn('record.__dict__.get("segment_id")', text)


class TestAcyclicImports(unittest.TestCase):
    def test_every_module_imports_in_a_fresh_interpreter(self):
        modules = [
            "core.observability",
            "core.observability.models",
            "core.observability.redaction",
            "core.observability.normalizer",
            "core.observability.ingress",
            "core.observability.storage.base",
            "core.observability.sinks.base",
            "core.observability.query.base",
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


class TestIngressSignature(unittest.TestCase):
    """The ClientObservation-API signature must match the frozen ``event(...)``
    of CONTRACTS §6."""

    def assert_parameter(self, signature, name, kind):
        parameters = signature.parameters
        self.assertIn(name, parameters)
        self.assertEqual(parameters[name].kind, kind)

    def test_event_signature_matches_frozen_contract(self):
        signature = inspect.signature(Ingress.event)
        self.assert_parameter(signature, "type", inspect.Parameter.POSITIONAL_OR_KEYWORD)
        for name in ("channel", "component", "message", "details",
                     "session_id", "generation", "activation_id", "segment_id",
                     "command_id", "correlation_id", "transcription_id"):
            self.assert_parameter(signature, name,
                                  inspect.Parameter.KEYWORD_ONLY)
        self.assertEqual(
            signature.parameters["level"].default, "INFO"
        )
        self.assertIsNone(signature.parameters["component"].default)
        self.assertIsNone(signature.parameters["message"].default)
        self.assertIsNone(signature.parameters["details"].default)


class TestMutationGuards(unittest.TestCase):
    """Design guards for the run's mandatory mutation checks (WP-OBS-010):

    - Mutation 1: "Redaction-Aufruf am Ende des Normalizer-Pfades entfernen"
      must turn the U-Redaction tests red.
    - Mutation 2: "unfreeze() vor der Serialisierung entfernen" must turn N-01 red.
    """

    def test_redaction_is_actually_applied_end_to_end(self):
        record = redaction_from_client_event()
        self.assertIn("[redacted:", str(dict(record.details)))
        self.assertNotIn("vertraulicherText", str(dict(record.details)))

    def test_unfreeze_is_required_before_serialization(self):
        from types import MappingProxyType
        payload = MappingProxyType({"data": {"text": "t"}})
        try:
            import json
            json.dumps(payload)  # would fail without unfreeze()
        except TypeError:
            pass
        else:
            self.fail("json.dumps must not accept frozen containers")
        unfrozen = redaction.unfreeze(payload)
        self.assertIsInstance(json.dumps(unfrozen), str)


def redaction_from_client_event():
    from core.observability.normalizer import from_client_event
    record = from_client_event(
        "client.final.deduplicated",
        channel="transcription",
        level="WARNING",
        message="Final [seg=1]: vertraulicherText",
        details={"text": "vertraulicherText"},
        instance_id="i" * 32,
    )
    assert record is not None
    return record


if __name__ == "__main__":
    unittest.main()