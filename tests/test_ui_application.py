"""Composition and lifecycle tests for the AP06 desktop application."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from app import build_argument_parser
from core.config import AppConfig
from ui.application import (
    DesktopApplication,
    EXIT_ALREADY_RUNNING,
    EXIT_TRAY_UNAVAILABLE,
    EXIT_UI_INITIALIZATION_FAILED,
    run_gui,
)
from ui.hotkeys import HOTKEY_ID_REINSERT_LAST, HOTKEY_ID_TOGGLE
from ui.single_instance import (
    InstanceAcquireResult,
    InstanceAcquireStatus,
)


class FakeBridge(QObject):
    snapshot_changed = Signal(object)
    feedback_received = Signal(object)
    text_received = Signal(int, str, bool)
    transport_changed = Signal(object)
    command_completed = Signal(str, object)
    history_received = Signal(object)
    fatal_error = Signal(str)

    def __init__(self, start_result=True):
        super().__init__()
        self.start_result = start_result
        self.calls = []

    def start(self):
        self.calls.append("start")
        return self.start_result

    def stop(self, timeout=10.0):
        self.calls.append(("stop", timeout))
        return True

    def toggle_dictation(self):
        self.calls.append("toggle")
        return True

    def reinsert_last(self):
        self.calls.append("reinsert_last")
        return True

    def reinsert_entry(self, entry_id):
        self.calls.append(("reinsert_entry", entry_id))
        return True

    def request_history(self, limit=10):
        self.calls.append(("history", limit))
        return True


class FakeHotkeyBackend:
    def __init__(self, fail=False):
        self.fail = fail
        self.registered = []
        self.unregistered = []

    def register(self, hwnd, hotkey_id, modifiers, virtual_key):
        if self.fail:
            raise OSError("conflict")
        self.registered.append(hotkey_id)

    def unregister(self, hwnd, hotkey_id):
        self.unregistered.append(hotkey_id)


class FakeGuard:
    def __init__(self, status=InstanceAcquireStatus.ACQUIRED):
        self.status = status
        self.released = 0

    def acquire(self):
        return InstanceAcquireResult(self.status)

    def release(self):
        self.released += 1


class TestDesktopApplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def make_desktop(self, *, bridge=None, hotkey_backend=None, guard=None):
        return DesktopApplication(
            self.application,
            AppConfig(),
            guard or FakeGuard(),
            bridge=bridge or FakeBridge(),
            hotkey_backend=hotkey_backend or FakeHotkeyBackend(),
        )

    def test_start_wires_native_hotkeys_to_core_and_shutdown_releases_all(self):
        bridge = FakeBridge()
        backend = FakeHotkeyBackend()
        guard = FakeGuard()
        desktop = self.make_desktop(
            bridge=bridge,
            hotkey_backend=backend,
            guard=guard,
        )
        self.addCleanup(desktop.shutdown)

        self.assertTrue(desktop.start())
        desktop.hotkeys.dispatch_hotkey_id(HOTKEY_ID_TOGGLE)
        desktop.hotkeys.dispatch_hotkey_id(HOTKEY_ID_REINSERT_LAST)
        desktop.shutdown()
        desktop.shutdown()

        self.assertIn("toggle", bridge.calls)
        self.assertIn("reinsert_last", bridge.calls)
        self.assertEqual(
            backend.registered,
            [HOTKEY_ID_TOGGLE, HOTKEY_ID_REINSERT_LAST],
        )
        self.assertEqual(len(backend.unregistered), 2)
        self.assertEqual(guard.released, 1)
        self.assertIn(("stop", 10.0), bridge.calls)

    def test_hotkey_conflict_keeps_tray_core_operational(self):
        bridge = FakeBridge()
        desktop = self.make_desktop(
            bridge=bridge,
            hotkey_backend=FakeHotkeyBackend(fail=True),
        )
        self.addCleanup(desktop.shutdown)

        self.assertTrue(desktop.start())
        self.assertIn("start", bridge.calls)
        self.assertTrue(desktop.overlay.isVisible())
        self.assertIn("Hotkeys", desktop.overlay.label.text())

    def test_text_signal_adapts_segment_text_and_final_for_overlay(self):
        bridge = FakeBridge()
        desktop = self.make_desktop(bridge=bridge)
        self.addCleanup(desktop.shutdown)

        bridge.text_received.emit(13, "Korrekt verbundener Text", False)
        self.application.processEvents()

        self.assertEqual(desktop.overlay.label.text(), "Korrekt verbundener Text")
        self.assertTrue(desktop.overlay.isVisible())

    def test_core_start_failure_rolls_back_hotkeys_and_tray(self):
        bridge = FakeBridge(start_result=False)
        backend = FakeHotkeyBackend()
        desktop = self.make_desktop(
            bridge=bridge,
            hotkey_backend=backend,
        )
        self.addCleanup(desktop.shutdown)

        self.assertFalse(desktop.start())
        self.assertEqual(len(backend.unregistered), 2)
        self.assertFalse(desktop.tray.tray.isVisible())

    def test_argument_parser_preserves_explicit_headless_mode(self):
        parser = build_argument_parser()
        self.assertFalse(parser.parse_args([]).headless)
        self.assertTrue(parser.parse_args(["--headless"]).headless)

    def test_second_instance_exits_before_ui_start(self):
        guard = FakeGuard(InstanceAcquireStatus.ALREADY_RUNNING)
        result = run_gui(AppConfig(), [], instance_guard=guard)
        self.assertEqual(result, EXIT_ALREADY_RUNNING)
        self.assertEqual(guard.released, 0)

    def test_missing_system_tray_is_controlled_and_releases_mutex(self):
        guard = FakeGuard()
        with patch(
            "ui.application.QSystemTrayIcon.isSystemTrayAvailable",
            return_value=False,
        ):
            result = run_gui(AppConfig(), [], instance_guard=guard)
        self.assertEqual(result, EXIT_TRAY_UNAVAILABLE)
        self.assertEqual(guard.released, 1)

    def test_ui_initialization_exception_releases_mutex(self):
        guard = FakeGuard()
        with (
            patch(
                "ui.application.QSystemTrayIcon.isSystemTrayAvailable",
                return_value=True,
            ),
            patch(
                "ui.application.DesktopApplication",
                side_effect=RuntimeError("simulated UI construction failure"),
            ),
        ):
            result = run_gui(AppConfig(), [], instance_guard=guard)

        self.assertEqual(result, EXIT_UI_INITIALIZATION_FAILED)
        self.assertEqual(guard.released, 1)


if __name__ == "__main__":
    unittest.main()
