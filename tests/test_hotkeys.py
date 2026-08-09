"""Tests for native global-hotkey parsing, registration, and dispatch."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from ui.hotkeys import (
    HOTKEY_ID_REINSERT_LAST,
    HOTKEY_ID_TOGGLE,
    MOD_ALT,
    MOD_CONTROL,
    MOD_NOREPEAT,
    MOD_SHIFT,
    GlobalHotkeyManager,
    parse_hotkey,
)


class FakeHotkeyBackend:
    def __init__(self, fail_on_id=None):
        self.fail_on_id = fail_on_id
        self.registered = []
        self.unregistered = []

    def register(self, window_handle, hotkey_id, modifiers, virtual_key):
        if hotkey_id == self.fail_on_id:
            raise OSError("simulated hotkey conflict")
        self.registered.append(
            (window_handle, hotkey_id, modifiers, virtual_key)
        )

    def unregister(self, window_handle, hotkey_id):
        self.unregistered.append((window_handle, hotkey_id))


class TestHotkeyParser(unittest.TestCase):
    def test_parses_legacy_toggle_hotkey(self):
        spec = parse_hotkey("<ctrl>+<shift>+space")
        self.assertEqual(spec.canonical, "Ctrl+Shift+Space")
        self.assertEqual(
            spec.modifiers,
            MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT,
        )
        self.assertEqual(spec.virtual_key, 0x20)

    def test_parses_reinsertion_and_function_keys(self):
        reinsert = parse_hotkey("Ctrl+Alt+Space")
        self.assertEqual(
            reinsert.modifiers,
            MOD_CONTROL | MOD_ALT | MOD_NOREPEAT,
        )
        self.assertEqual(parse_hotkey("Ctrl+F24").virtual_key, 0x87)


class TestGlobalHotkeyManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def _manager(self, backend, calls):
        return GlobalHotkeyManager(
            toggle_key="Ctrl+Shift+Space",
            reinsert_last_key="Ctrl+Alt+Space",
            on_toggle=lambda: calls.append("toggle"),
            on_reinsert_last=lambda: calls.append("reinsert"),
            backend=backend,
            application=self.application,
        )

    def test_registers_both_and_dispatches_exact_action(self):
        backend = FakeHotkeyBackend()
        calls = []
        manager = self._manager(backend, calls)
        self.addCleanup(manager.unregister)

        self.assertTrue(manager.register())
        self.assertEqual(
            [item[1] for item in backend.registered],
            [HOTKEY_ID_TOGGLE, HOTKEY_ID_REINSERT_LAST],
        )
        self.assertTrue(manager.dispatch_hotkey_id(HOTKEY_ID_TOGGLE))
        self.assertTrue(manager.dispatch_hotkey_id(HOTKEY_ID_REINSERT_LAST))
        self.assertFalse(manager.dispatch_hotkey_id(123))
        self.assertEqual(calls, ["toggle", "reinsert"])

    def test_partial_registration_rolls_back_and_is_retryable(self):
        backend = FakeHotkeyBackend(fail_on_id=HOTKEY_ID_REINSERT_LAST)
        manager = self._manager(backend, [])

        self.assertFalse(manager.register())
        self.assertEqual(
            backend.unregistered,
            [(0, HOTKEY_ID_TOGGLE)],
        )
        self.assertFalse(manager.is_registered)

        backend.fail_on_id = None
        self.assertTrue(manager.register())
        manager.unregister()

    def test_unregister_is_idempotent_and_disables_dispatch(self):
        backend = FakeHotkeyBackend()
        calls = []
        manager = self._manager(backend, calls)
        manager.register()

        manager.unregister()
        manager.unregister()

        self.assertEqual(len(backend.unregistered), 2)
        self.assertFalse(manager.dispatch_hotkey_id(HOTKEY_ID_TOGGLE))
        self.assertEqual(calls, [])

    def test_disabled_manager_never_touches_backend(self):
        backend = FakeHotkeyBackend()
        manager = GlobalHotkeyManager(
            toggle_key="Ctrl+Shift+Space",
            reinsert_last_key="Ctrl+Alt+Space",
            on_toggle=lambda: None,
            on_reinsert_last=lambda: None,
            enabled=False,
            backend=backend,
            application=self.application,
        )
        self.assertTrue(manager.register())
        self.assertTrue(manager.is_registered)
        self.assertEqual(backend.registered, [])


if __name__ == "__main__":
    unittest.main()
