"""
OBS-040 — contract and layering tests.

Frozen sources: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §5.1 (frozen module
structure), §5.2 (import direction, every rule to be proven by a contract
test), §6.2 (lifecycle), §7.3 (counter set is frozen), §11.1/§11.2 (what V1
does not build); ``LOGGING_CONTRACTS_FREEZE_V1.md`` §6 (wiring), §11.2
(``LoggingHealthSnapshot`` shape), §12 (hook list completeness).
"""

from __future__ import annotations

import dataclasses
import inspect
import pathlib
import unittest

import core.observability as observability_package
from core.observability.adapters.client_events import ClientEventEmitter
from core.observability.adapters.server_live import ServerLiveAdapter
from core.observability.health import LoggingHealthSnapshot
from core.observability.ingress import NULL_INGRESS, ObservabilityIngress

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TestFrozenModuleStructure(unittest.TestCase):
    def test_the_two_new_adapters_exist_where_arch_51_puts_them(self):
        for relative in (
            "core/observability/adapters/client_events.py",
            "core/observability/adapters/server_live.py",
        ):
            with self.subTest(module=relative):
                self.assertTrue((ROOT / relative).is_file())

    def test_both_are_re_exported_from_the_package(self):
        self.assertIs(
            observability_package.ClientEventEmitter, ClientEventEmitter
        )
        self.assertIs(
            observability_package.ServerLiveAdapter, ServerLiveAdapter
        )
        self.assertIn("ClientEventEmitter", observability_package.__all__)
        self.assertIn("ServerLiveAdapter", observability_package.__all__)

    def test_v1_still_does_not_create_the_modules_arch_51_excludes(self):
        """*"In V1 ausdruecklich NICHT angelegt: adapters/led.py,
        query/server_history.py, sinks/text_file.py, core/server_control/,
        ui/settings/logging_settings.py."*"""
        for relative in (
            "core/observability/adapters/led.py",
            "core/observability/query/server_history.py",
            "core/observability/sinks/text_file.py",
            "core/server_control",
            "ui/settings/logging_settings.py",
        ):
            with self.subTest(path=relative):
                self.assertFalse((ROOT / relative).exists())


class TestLayeringAndImportDirection(unittest.TestCase):
    def test_the_adapters_do_not_import_upwards(self):
        """§5.2: *"adapters kennen ingress + normalizer, NICHT umgekehrt."*"""
        for name in ("client_events", "server_live"):
            with self.subTest(module=name):
                source = (
                    ROOT / "core/observability/adapters" / f"{name}.py"
                ).read_text(encoding="utf-8")
                self.assertNotIn("from ..worker", source)
                self.assertNotIn("from ..manager", source)
                self.assertNotIn("import sqlite3", source)

    def test_no_observability_module_imports_pyside(self):
        """§5.2: ``core/**`` importiert NIE PySide6."""
        for path in (ROOT / "core").rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            with self.subTest(module=str(path.relative_to(ROOT))):
                self.assertNotIn("PySide6", path.read_text(encoding="utf-8"))

    @staticmethod
    def _observability_modules():
        for path in (ROOT / "core/observability").rglob("*.py"):
            if "__pycache__" not in path.parts:
                yield path

    @staticmethod
    def _names_used(path: pathlib.Path) -> set:
        """Every identifier the module actually USES.

        Parsed, not grepped: the freeze rules are about code, and a docstring
        that quotes the very rule it obeys ("dieses Modul importiert NIE
        core.feedback_reducer") must not read as a violation of it.
        """
        import ast

        tree = ast.parse(path.read_text(encoding="utf-8"))
        used = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                used.add(node.attr)
            elif isinstance(node, ast.Name):
                used.add(node.id)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    used.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                used.add(node.module or "")
                for alias in node.names:
                    used.add(alias.name)
        return used

    @staticmethod
    def _attributes_read(path: pathlib.Path) -> set:
        import ast

        tree = ast.parse(path.read_text(encoding="utf-8"))
        return {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }

    def test_the_logging_core_never_reads_the_session_log_token(self):
        """ARCH §10.1: *"Der Core sieht den Session-Log-Token auch NICHT
        indirekt: SessionContext.log_access traegt zwar den Token, wird vom
        Normalizer aber NIE gelesen."*

        Checked as ATTRIBUTE access, which is what the rule is about. The
        normalizer does read the hello payload's ``logAccess`` mapping — that is
        R-6's whitelist, and it deliberately omits ``accessToken`` — so a local
        variable of that name is not a violation while
        ``context.log_access`` would be.
        """
        for path in self._observability_modules():
            with self.subTest(module=str(path.relative_to(ROOT))):
                attributes = self._attributes_read(path)
                self.assertNotIn("log_access", attributes)
                self.assertNotIn("access_token", attributes)

    def test_the_logging_core_never_reaches_the_feedback_domain(self):
        """G-5 / ARCH §1.3: a logging failure is NEVER reported through
        ``report_local_feedback``, ``CanonicalEventType`` or the
        ``FeedbackEngine``."""
        for path in self._observability_modules():
            with self.subTest(module=str(path.relative_to(ROOT))):
                used = self._names_used(path)
                self.assertNotIn("core.feedback_reducer", used)
                self.assertNotIn("core.feedback_mapping", used)
                self.assertNotIn("CanonicalEventType", used)
                self.assertNotIn("FeedbackEngine", used)
                self.assertNotIn("report_local_feedback", used)


class TestFrozenCounterSetIsUnchanged(unittest.TestCase):
    def test_the_health_snapshot_has_exactly_the_frozen_fields(self):
        """ARCH §7.3 is headed *"Zaehler -- eingefroren"*, and CONTRACTS §11.2
        fixes the dataclass. OBS-040 adds producer-side counters on the
        producers themselves and none to logging's own set."""
        expected = [
            "state",
            "since",
            "detail",
            "enqueued",
            "written",
            "deduplicated",
            "dropped_watermark",
            "dropped_queue_full",
            "dropped_shutdown",
            "malformed",
            "store_errors",
            "sink_errors",
            "retention_errors",
            "worker_errors",
            "queue_depth",
            "db_bytes",
        ]
        actual = [field.name for field in dataclasses.fields(LoggingHealthSnapshot)]
        self.assertEqual(actual, expected)

    def test_normative_documents_are_untouched_by_this_run(self):
        """A frozen document is never changed by an implementation run; a real
        need would be a ``DECISION REQUIRED``, not an edit."""
        normative = (
            ROOT
            / "ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV"
        )
        for name in (
            "LOGGING_ARCHITEKTUR_FREEZE_V1.md",
            "LOGGING_CONTRACTS_FREEZE_V1.md",
            "LOGGING_DECISIONS_FREEZE_V1.md",
        ):
            with self.subTest(document=name):
                text = (normative / name).read_text(encoding="utf-8")
                self.assertIn("status: FROZEN", text)
                self.assertNotIn("OBS-040", text.split("# 1.")[0])


class TestWiringContract(unittest.TestCase):
    def test_the_ingress_keyword_is_optional_everywhere(self):
        """Every injection point is additive: the default is ``NULL_INGRESS``,
        so no existing caller has to change (CONTRACTS §6)."""
        from core.audio_capture import AudioCapture
        from core.controller import STTController
        from core.event_stream import EventStreamTransport
        from core.session_coordinator import DualSessionCoordinator
        from core.stt_session import STTSession
        from core.text_injector import TextInjectionQueue
        from ui.application import DesktopApplication, run_gui
        from ui.core_bridge import CoreBridge
        from ui.hotkeys import GlobalHotkeyManager
        from ui.led_feedback import LedFeedback
        from ui.settings_dialog import SettingsDialog

        targets = (
            AudioCapture.__init__,
            STTController.__init__,
            EventStreamTransport.__init__,
            DualSessionCoordinator.__init__,
            STTSession.__init__,
            TextInjectionQueue.__init__,
            DesktopApplication.__init__,
            run_gui,
            CoreBridge.__init__,
            GlobalHotkeyManager.__init__,
            LedFeedback.__init__,
            SettingsDialog.__init__,
        )
        for target in targets:
            with self.subTest(target=getattr(target, "__qualname__", target)):
                parameter = inspect.signature(target).parameters.get(
                    "observability"
                )
                self.assertIsNotNone(parameter)
                self.assertIsNot(parameter.default, inspect.Parameter.empty)

    def test_the_controller_factory_stays_single_argument(self):
        """CONTRACTS §6: *"Mit der Default-Factory bleibt eine von aussen
        uebergebene Factory einstellig und der Controller erhaelt
        NULL_INGRESS."*"""
        from core.config import AppConfig
        from ui.core_bridge import CoreBridge

        seen = {}

        def one_argument_factory(config):
            seen["config"] = config
            return object()

        bridge = CoreBridge(AppConfig(), one_argument_factory)
        self.assertIs(bridge._controller_factory, one_argument_factory)

    def test_the_default_factory_hands_the_ingress_to_the_controller(self):
        from core.config import AppConfig
        from ui.core_bridge import CoreBridge

        ingress = ObservabilityIngress(instance_id="bridge-test")
        config = AppConfig()
        config.history.persistent.enabled = False
        bridge = CoreBridge(config, observability=ingress)
        controller = bridge._controller_factory(config)
        try:
            self.assertIs(controller.observability, ingress)
        finally:
            controller.history.cleanup()

    def test_null_ingress_answers_the_full_obs040_surface(self):
        """``NULL_INGRESS`` must be behaviourally equivalent (CONTRACTS §6),
        including the methods OBS-040 added."""
        self.assertIsNone(NULL_INGRESS.emit_record_rejected("x", ValueError()))
        self.assertIsNone(
            NULL_INGRESS.register_aggregate_source("t", lambda: {"a": 1})
        )
        self.assertEqual(NULL_INGRESS.collect_aggregates(), [])
        self.assertFalse(NULL_INGRESS.submit(object()))
        self.assertIsNone(NULL_INGRESS.observe_server_result(None, None))


class TestHookListCoverage(unittest.TestCase):
    """Every §12 record type that OBS-040 implements must actually appear in
    the product source. A type that only exists in a test would be a coverage
    claim without an implementation (gate finding B-2 of OBS-030)."""

    IMPLEMENTED_TYPES = {
        # §12.1
        "client.app.started": "ui/application.py",
        "client.app.stopping": "ui/application.py",
        "client.core.thread_started": "ui/core_bridge.py",
        "client.core.thread_stopped": "ui/core_bridge.py",
        "client.controller.run_started": "core/controller.py",
        "client.websocket.connecting": "core/stt_session.py",
        "client.websocket.connected": "core/stt_session.py",
        "client.websocket.disconnected": "core/stt_session.py",
        "client.session.admitted": "core/stt_session.py",
        "client.session.ready": "core/stt_session.py",
        "client.reconnect.scheduled": "core/stt_session.py",
        "client.eventstream.state_changed": "core/session_coordinator.py",
        "client.eventstream.protocol_error": "core/event_stream.py",
        "client.config.validation_failed": "core/controller.py",
        # §12.2
        "client.hotkey.pressed": "ui/hotkeys.py",
        "client.command.requested": "ui/core_bridge.py",
        "client.command.completed": "ui/core_bridge.py",
        "client.trigger.sent": "core/stt_session.py",
        "client.trigger.ack_received": "core/stt_session.py",
        "client.trigger.ack_dropped": "core/stt_session.py",
        "client.stream.start_sent": "core/stt_session.py",
        "client.dictation.start_attempt": "core/controller.py",
        "client.dictation.confirmed": "core/controller.py",
        "client.dictation.failed": "core/controller.py",
        "client.dictation.interrupted": "core/controller.py",
        "client.settings.apply_started": "ui/application.py",
        "client.settings.apply_completed": "ui/application.py",
        "client.settings.runtime_apply": "core/controller.py",
        "client.action.blocked": "core/controller.py",
        "client.audio.stream_started": "core/audio_capture.py",
        "client.audio.stream_stopped": "core/audio_capture.py",
        # §12.3
        "client.injection.enqueued": "core/controller.py",
        "client.injection.rejected": "core/controller.py",
        "client.final.deduplicated": "core/controller.py",
        # §12.4
        "client.audio.stream_stats": "core/controller.py",
        "client.queue.state": "core/text_injector.py",
        "logging.record_rejected": "core/observability/ingress.py",
        # §12.5
        "client.feedback.decision": "ui/application.py",
        "client.led.dispatch_failed": "ui/led_feedback.py",
        "client.led.queue_overflow": "ui/led_feedback.py",
        "client.sound.failed": "ui/application.py",
        "client.server.error_classified": "core/controller.py",
    }

    def test_every_implemented_type_appears_in_its_module(self):
        for record_type, relative in sorted(self.IMPLEMENTED_TYPES.items()):
            with self.subTest(type=record_type):
                source = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn(record_type, source)

    def test_the_worker_produced_types_of_obs030_are_still_there(self):
        source = (ROOT / "core/observability/worker.py").read_text(
            encoding="utf-8"
        )
        for record_type in (
            "logging.records_dropped",
            "logging.recovered",
            "logging.retention_pressure",
        ):
            with self.subTest(type=record_type):
                self.assertIn(record_type, source)

    def test_p_only_hooks_keep_their_existing_logger_lines(self):
        """§12: ``P`` means *"bestehende Python-Logzeile genuegt"*. Those lines
        must neither be removed nor reworded."""
        expectations = (
            ("core/history.py", "logger."),
            ("core/config.py", "logger."),
            ("core/controller.py", 'logger.error("Error stopping audio capture'),
        )
        for relative, needle in expectations:
            with self.subTest(module=relative):
                source = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn(needle, source)


if __name__ == "__main__":
    unittest.main()
