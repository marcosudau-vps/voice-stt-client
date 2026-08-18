"""
OBS-050 — contract and isolation tests.

Frozen source: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §5.1 (module structure),
§5.2 (layering and import direction, each rule *"durch einen Contract-Test zu
belegen"*), §11.2/FD-S1 (no ring buffer), O-01/O-14 (the UI is a consumer;
the query layer never writes) and ``LOGGING_CONTRACTS_FREEZE_V1.md`` §8/§9.

The end-to-end case at the bottom is the one that matters most for this work
package: **logging works without the log view**. The view is a consumer, and
nothing in the write path may depend on it.
"""

from __future__ import annotations

import inspect
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUERY_DIR = PROJECT_ROOT / "core" / "observability" / "query"
UI_LOGS_DIR = PROJECT_ROOT / "ui" / "logs"

UI_MODULES = (
    "log_window.py",
    "log_page.py",
    "log_table_model.py",
    "log_filter_bar.py",
    "log_detail_view.py",
    "log_query_controller.py",
)


def _import_lines(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines()
        if line.strip().startswith(("import ", "from "))
    )


class TestFrozenModuleStructure(unittest.TestCase):
    def test_query_package_has_the_three_frozen_modules(self):
        """ARCH §5.1: ``query/base.py``, ``query/local.py``,
        ``query/service.py``."""
        for name in ("base.py", "local.py", "service.py"):
            with self.subTest(module=name):
                self.assertTrue((QUERY_DIR / name).is_file())

    def test_ui_logs_has_the_six_frozen_modules(self):
        for name in UI_MODULES:
            with self.subTest(module=name):
                self.assertTrue((UI_LOGS_DIR / name).is_file())

    def test_modules_explicitly_not_created_in_v1(self):
        """ARCH §5.1: *"In V1 ausdruecklich NICHT angelegt"*."""
        for missing in (
            PROJECT_ROOT / "core" / "observability" / "query" / "server_history.py",
            PROJECT_ROOT / "core" / "observability" / "adapters" / "led.py",
            PROJECT_ROOT / "core" / "observability" / "sinks" / "text_file.py",
            PROJECT_ROOT / "core" / "server_control",
            PROJECT_ROOT / "ui" / "settings" / "logging_settings.py",
        ):
            with self.subTest(path=str(missing)):
                self.assertFalse(missing.exists())


class TestImportDirection(unittest.TestCase):
    def test_ui_logs_never_imports_storage_or_sqlite3(self):
        """ARCH §5.2: *"ui/logs/** importiert core.observability.query.*,
        importiert NIE core.observability.storage.*, importiert NIE
        sqlite3"*."""
        for name in UI_MODULES:
            text = (UI_LOGS_DIR / name).read_text(encoding="utf-8")
            imports = _import_lines(text)
            with self.subTest(module=name):
                self.assertNotIn("sqlite3", imports)
                self.assertNotIn("observability.storage", imports)
                self.assertNotIn("observability.worker", imports)
                self.assertNotIn("observability.ingress", imports)
                self.assertNotIn("observability.manager", imports)

    def test_at_least_one_ui_module_uses_the_query_contracts(self):
        found = [
            name for name in UI_MODULES
            if "core.observability.query" in (UI_LOGS_DIR / name).read_text(encoding="utf-8")
        ]
        self.assertTrue(found)

    def test_query_layer_never_imports_ingress_worker_manager_or_pyside(self):
        """ARCH §5.2: *"query kennt models + storage"* — and no Qt anywhere
        under ``core/``."""
        for name in ("base.py", "local.py", "service.py"):
            text = (QUERY_DIR / name).read_text(encoding="utf-8")
            imports = _import_lines(text)
            with self.subTest(module=name):
                for forbidden in ("ingress", "worker", "manager", "normalizer", "redaction"):
                    self.assertNotIn(forbidden, imports)
                self.assertNotIn("PySide6", text)
                self.assertNotIn("QtCore", text)

    def test_core_never_imports_pyside6(self):
        """ARCH §5.2: *"core/** importiert NIE PySide6"* — checked over the
        whole package, including the modules OBS-050 touched."""
        for path in (PROJECT_ROOT / "core").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                self.assertNotIn("PySide6", text)

    def test_every_new_module_imports_in_a_fresh_interpreter(self):
        modules = [
            "core.observability.query.local",
            "core.observability.query.service",
            "core.logging_settings_metadata",
            "core.observability",
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
                    completed.returncode, 0, msg=f"{module}: {completed.stderr[-800:]}"
                )


class TestNoRingBuffer(unittest.TestCase):
    """FD-S1 / ARCH §11.2: the ring buffer is gone and stays gone."""

    def test_no_ring_buffer_and_no_live_buffer_size_anywhere(self):
        for directory in (PROJECT_ROOT / "core", PROJECT_ROOT / "ui"):
            for path in directory.rglob("*.py"):
                text = path.read_text(encoding="utf-8").lower()
                with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                    self.assertNotIn("live_buffer_size", text)
                    self.assertNotIn("ringbuffer", text)
                    self.assertNotIn("ring_buffer", text)

    def test_the_live_mode_queries_the_provider(self):
        """The live path uses the same provider interface as the history —
        one abstraction, not two.

        Both modes now go through the single funnel ``LogPage._issue``, which
        is what pairs a request id with the KIND of request (gate finding
        B-2); the tail is therefore checked at both ends: it asks ascending,
        and the funnel it uses is the provider query.
        """
        from ui.logs import log_page

        tail = inspect.getsource(log_page.LogPage._tail)
        self.assertIn("newest_first=False", tail)
        self.assertIn("_issue", tail)
        funnel = inspect.getsource(log_page.LogPage._issue)
        self.assertIn("request_page", funnel)

    def test_every_query_records_the_kind_of_request_it_was(self):
        """B-2 structurally: no code path may reserve a request id without
        recording what was asked — otherwise the answer would again have to
        be interpreted from mutable state."""
        from ui.logs import log_page

        for name in ("reload", "load_more", "_tail"):
            source = inspect.getsource(getattr(log_page.LogPage, name))
            with self.subTest(method=name):
                self.assertIn("self._issue(", source)
                self.assertNotIn("next_request_id", source)
        funnel = inspect.getsource(log_page.LogPage._issue)
        self.assertIn("self._active_kind = kind", funnel)

    def test_the_live_interval_is_the_frozen_250_ms(self):
        from ui.logs.log_page import LIVE_INTERVAL_MS
        from ui.logs.log_query_controller import LIVE_PAGE_SIZE

        self.assertEqual(LIVE_INTERVAL_MS, 250)
        self.assertEqual(LIVE_PAGE_SIZE, 500)


class TestQueryContracts(unittest.TestCase):
    def test_local_provider_satisfies_the_provider_protocol(self):
        """``LogProvider`` is a plain ``Protocol`` (not runtime-checkable, and
        OBS-010 froze it that way), so conformance is checked structurally:
        the four members of §8 and no more."""
        from core.observability.query.base import LogProvider
        from core.observability.query.local import LocalLogProvider

        provider = LocalLogProvider(None)
        expected = {"provider_id", "status", "query", "fetch_raw"}
        declared = {
            name for name in vars(LogProvider)
            if not name.startswith("_")
        }
        self.assertEqual(declared, expected)
        for name in expected:
            with self.subTest(member=name):
                self.assertTrue(hasattr(provider, name))

    def test_provider_query_signature_matches_the_freeze(self):
        from core.observability.query.local import LocalLogProvider

        parameters = list(
            inspect.signature(LocalLogProvider.query).parameters
        )
        self.assertEqual(parameters, ["self", "filter", "cursor", "limit"])

    def test_service_exposes_exactly_the_four_frozen_methods(self):
        from core.observability.query.service import LogQueryService

        for name in ("register", "providers", "query", "fetch_raw"):
            self.assertTrue(callable(getattr(LogQueryService, name)))

    def test_the_query_layer_has_no_subscribe_stream_count_or_delete(self):
        """§8.1 lists these as deliberately absent."""
        from core.observability.query.local import LocalLogProvider
        from core.observability.query.service import LogQueryService

        for owner in (LocalLogProvider, LogQueryService):
            for forbidden in ("subscribe", "stream", "count", "delete", "clear", "write"):
                with self.subTest(owner=owner.__name__, name=forbidden):
                    self.assertFalse(hasattr(owner, forbidden))

    def test_provider_capabilities_does_not_exist_in_v1(self):
        """FD-S3: additive later, absent now."""
        import core.observability.query.base as base

        self.assertFalse(hasattr(base, "ProviderCapabilities"))

    def test_auth_required_exists_although_v1_never_produces_it(self):
        """ARCH §10.1: the state exists from the start."""
        from core.observability.query.base import ProviderState

        self.assertEqual(ProviderState.AUTH_REQUIRED.value, "auth_required")


class TestLoggingWorksWithoutTheLogView(unittest.TestCase):
    """O-01: the view is a consumer. The write path must not know it exists."""

    def test_records_are_written_with_no_ui_imported(self):
        script = (
            "import sys, json\n"
            "from pathlib import Path\n"
            "from core.config import LoggingObservabilityConfig\n"
            "from core.observability.manager import ObservabilityManager\n"
            "from core.observability.query.local import LocalLogProvider\n"
            "from core.observability.query.base import QueryFilter\n"
            "db = Path(sys.argv[1])\n"
            "config = LoggingObservabilityConfig(db_path=str(db), flush_interval_s=0.05)\n"
            "manager = ObservabilityManager(config)\n"
            "manager.start()\n"
            "manager.ingress.event('client.app.started', channel='system',\n"
            "                      component='probe', message='ohne UI')\n"
            "manager.stop(2.0)\n"
            "loaded = [name for name in sys.modules if name.startswith(('ui.', 'PySide6'))]\n"
            "page = LocalLogProvider(db).query(QueryFilter())\n"
            "print(json.dumps({'ui_modules': loaded, 'rows': len(page.records),\n"
            "                  'types': [r.type for r in page.records]}))\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "observability.sqlite3"
            completed = subprocess.run(
                [sys.executable, "-c", script, str(db_path)],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(completed.returncode, 0, msg=completed.stderr[-2000:])
            import json

            result = json.loads(completed.stdout.strip().splitlines()[-1])
            self.assertEqual(result["ui_modules"], [])
            self.assertGreaterEqual(result["rows"], 1)
            self.assertIn("client.app.started", result["types"])

    def test_the_query_layer_does_not_start_a_worker_or_touch_the_ingress(self):
        """A provider is a reader: constructing and using it must not start a
        thread, and it holds no reference into the write path."""
        import threading

        from core.observability.query.local import LocalLogProvider
        from core.observability.query.base import QueryFilter

        before = {thread.name for thread in threading.enumerate()}
        provider = LocalLogProvider(None)
        provider.query(QueryFilter())
        provider.fetch_raw("x")
        after = {thread.name for thread in threading.enumerate()}
        self.assertEqual(before, after)
        self.assertNotIn("RealtimeSTT-Observability", after)


class TestNoLaterWorkPackageIsAnticipated(unittest.TestCase):
    """ARCH §10.1: no admin key, no "all sessions" switch, no HTTP client —
    not even a disabled one."""

    def test_no_admin_or_remote_history_vocabulary_in_the_new_modules(self):
        forbidden = ("admin_key", "adminKey", "allSessions", "all_sessions",
                     "ServerHistoryProvider", "historyPath")
        paths = list(QUERY_DIR.glob("*.py")) + list(UI_LOGS_DIR.glob("*.py"))
        paths.append(PROJECT_ROOT / "core" / "logging_settings_metadata.py")
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for term in forbidden:
                with self.subTest(path=path.name, term=term):
                    self.assertNotIn(term, text)

    def test_no_http_client_dependency_was_introduced(self):
        """FD-B3: the client has no HTTP client, and OBS-050 does not add
        one."""
        paths = list(QUERY_DIR.glob("*.py")) + list(UI_LOGS_DIR.glob("*.py"))
        for path in paths:
            imports = _import_lines(path.read_text(encoding="utf-8"))
            for term in ("requests", "httpx", "urllib", "http.client", "aiohttp"):
                with self.subTest(path=path.name, term=term):
                    self.assertNotIn(term, imports)


if __name__ == "__main__":
    unittest.main()
