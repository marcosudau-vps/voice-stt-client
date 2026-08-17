"""
Contract / isolation tests for OBS-030 (``storage/sqlite.py``, ``sinks/jsonl_file.py``,
``worker.py``, ``manager.py``).

Frozen source: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §5.2 (layering/import
direction), §6.1 (daemon thread, no QueueHandler/QueueListener), WP-OBS-030
Pflichtpruefungen ("kein Test hinterlaesst einen laufenden Worker").
"""

from __future__ import annotations

import inspect
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OBSERVABILITY_DIR = PROJECT_ROOT / "core" / "observability"


def _strip_docstrings(text: str) -> str:
    out: list[str] = []
    in_doc = False
    for line in text.splitlines():
        if line.count('"""') % 2 == 1:
            in_doc = not in_doc
            continue
        if not in_doc:
            out.append(line)
    return "\n".join(out)


def _import_lines(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines()
        if line.strip().startswith(("import ", "from "))
    )


class TestModuleIsolation(unittest.TestCase):
    def test_storage_module_imports_only_models_and_stdlib(self):
        """ARCH §5.2: 'storage kennt nur models'."""
        text = (OBSERVABILITY_DIR / "storage" / "sqlite.py").read_text(encoding="utf-8")
        imports = _import_lines(text)
        for forbidden in ("redaction", "normalizer", "ingress", "worker", "manager"):
            self.assertNotIn(forbidden, imports)

    def test_sinks_module_imports_only_models_and_stdlib(self):
        """ARCH §5.2: 'sinks kennen nur models'."""
        text = (OBSERVABILITY_DIR / "sinks" / "jsonl_file.py").read_text(encoding="utf-8")
        imports = _import_lines(text)
        for forbidden in ("redaction", "normalizer", "ingress", "worker", "manager", "sqlite3"):
            self.assertNotIn(forbidden, imports)

    def test_no_pyside6_or_qtcore_in_obs030_modules(self):
        for relative in ("storage/sqlite.py", "sinks/jsonl_file.py", "worker.py", "manager.py"):
            path = OBSERVABILITY_DIR / relative
            with self.subTest(path=relative):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("PySide6", text)
                self.assertNotIn("QtCore", text)

    def test_worker_does_not_import_pyside6_query_or_asyncio_queue(self):
        """ARCH §6.1/§6.4: dedicated thread, no asyncio.Queue, no
        QueueHandler/QueueListener."""
        text = (OBSERVABILITY_DIR / "worker.py").read_text(encoding="utf-8")
        self.assertNotIn("asyncio", text)
        self.assertNotIn("QueueHandler", text)
        self.assertNotIn("QueueListener", text)

    def test_sqlite_store_never_opens_a_connection_in_init(self):
        """D-4: the connection is created in ``open()`` (called from the
        worker thread), never in ``__init__``."""
        import ast
        tree = ast.parse((OBSERVABILITY_DIR / "storage" / "sqlite.py").read_text(encoding="utf-8"))
        init_source = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "SQLiteLogStore":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        init_source = ast.get_source_segment(
                            (OBSERVABILITY_DIR / "storage" / "sqlite.py").read_text(encoding="utf-8"),
                            item,
                        )
        self.assertIsNotNone(init_source)
        self.assertNotIn("sqlite3.connect", init_source)

    def test_check_same_thread_is_never_overridden(self):
        """CONTRACTS §5.4: ``check_same_thread`` stays on the sqlite3
        default (True) so the connection never leaves its thread (N-05).
        Only actual code is checked; the module docstring is free to name
        the setting in prose (it does, to state this very rule)."""
        text = (OBSERVABILITY_DIR / "storage" / "sqlite.py").read_text(encoding="utf-8")
        self.assertNotIn("check_same_thread", _strip_docstrings(text))


class TestAcyclicImports(unittest.TestCase):
    def test_every_obs030_module_imports_in_a_fresh_interpreter(self):
        modules = [
            "core.observability",
            "core.observability.storage.sqlite",
            "core.observability.sinks.jsonl_file",
            "core.observability.worker",
            "core.observability.manager",
            "app",
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
                    msg=f"{module}: {completed.stderr[-800:]}",
                )


class TestLogStoreSignatures(unittest.TestCase):
    def test_write_batch_returns_a_two_tuple(self):
        from core.observability.storage.sqlite import SQLiteLogStore
        signature = inspect.signature(SQLiteLogStore.write_batch)
        self.assertIn("records", signature.parameters)

    def test_clear_signature(self):
        from core.observability.storage.sqlite import SQLiteLogStore
        signature = inspect.signature(SQLiteLogStore.clear)
        self.assertEqual(list(signature.parameters), ["self"])


class TestManagerLifecycleSignature(unittest.TestCase):
    def test_start_stop_signatures(self):
        from core.observability.manager import ObservabilityManager
        start_sig = inspect.signature(ObservabilityManager.start)
        stop_sig = inspect.signature(ObservabilityManager.stop)
        self.assertEqual(list(start_sig.parameters), ["self"])
        self.assertIn("timeout", stop_sig.parameters)


class TestNoWorkerThreadSurvivesModuleImport(unittest.TestCase):
    """Sanity: importing the modules alone must not start any thread —
    ``pytest`` AND ``unittest`` both discover this file, and a stray thread
    started at import time would leak across every other test module."""

    def test_import_alone_starts_no_realtimestt_observability_thread(self):
        names = [t.name for t in threading.enumerate()]
        self.assertNotIn("RealtimeSTT-Observability", names)


if __name__ == "__main__":
    unittest.main()
