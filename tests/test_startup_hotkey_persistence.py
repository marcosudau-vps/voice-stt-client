"""R02-F01: a real isolated profile changes only after successful startup."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml
from PySide6.QtWidgets import QApplication

from voice_stt_client.core.config import AppConfig
from voice_stt_client.ui.application import DesktopApplication
from voice_stt_client.ui.hotkeys import HOTKEY_ID_REINSERT_LAST
from tests.test_ui_application import FakeBridge, FakeGuard, FakeHotkeyBackend, FakeLedFeedback


FALLBACK = "Ctrl+Alt+Shift+F12"


class SpaceConflictBackend(FakeHotkeyBackend):
    def __init__(self):
        super().__init__()
        self.attempts = []
        self.active = set()

    def register(self, hwnd, hotkey_id, modifiers, virtual_key):
        self.attempts.append(hotkey_id)
        if hotkey_id == HOTKEY_ID_REINSERT_LAST and virtual_key == 0x20:
            raise OSError(1409, "occupied")
        super().register(hwnd, hotkey_id, modifiers, virtual_key)
        self.active.add(hotkey_id)

    def unregister(self, hwnd, hotkey_id):
        super().unregister(hwnd, hotkey_id)
        self.active.discard(hotkey_id)


class StartupPersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def make_desktop(self, *, success, mode="manual"):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        profile = Path(folder.name) / "profile.yaml"
        raw = {
            "overlay": {"opacity": 0.54},
            "feedback": {"sounds_enabled": False},
            "led": {"enabled": False, "brightness": 37},
        }
        if mode == "disabled":
            raw["hotkey"] = {"enabled": False}
        elif mode == "wake-only":
            raw["session"] = {"manual_trigger_enabled": False, "wake_word_trigger_enabled": True}
        profile.write_text(yaml.safe_dump(raw), encoding="utf-8")
        config = AppConfig.load(profile)
        bridge, backend = FakeBridge(success), SpaceConflictBackend()
        desktop = DesktopApplication(
            self.qt, config, FakeGuard(), bridge=bridge,
            hotkey_backend=backend, led_feedback=FakeLedFeedback(),
        )
        self.addCleanup(desktop.shutdown)
        self.enterContext(patch("voice_stt_client.ui.application.fallback_hotkeys", return_value=[FALLBACK]))
        self.enterContext(patch("voice_stt_client.ui.application.QMessageBox.critical"))
        return desktop, bridge, backend, profile

    def test_failed_core_preserves_profile_and_restores_in_memory_hotkeys(self):
        desktop, bridge, backend, profile = self.make_desktop(success=False)
        before = profile.read_bytes()
        old_key, old_manager = desktop.config.hotkey.reinsert_last_key, desktop.hotkeys
        self.assertFalse(desktop.start())
        self.assertIn("start", bridge.calls)
        self.assertIn(HOTKEY_ID_REINSERT_LAST, backend.registered)
        self.assertEqual(profile.read_bytes(), before)
        self.assertEqual(AppConfig.load(profile).hotkey.reinsert_last_key, old_key)
        self.assertEqual(desktop.config.hotkey.reinsert_last_key, old_key)
        self.assertIs(desktop.hotkeys, old_manager)
        self.assertFalse(desktop.hotkeys.is_registered)
        self.assertEqual(backend.active, set())
        self.assertFalse(desktop.tray.tray.isVisible())

    def test_success_persists_after_core_start_and_preserves_preferences(self):
        desktop, bridge, backend, profile = self.make_desktop(success=True)
        before = profile.read_bytes()

        def start():
            self.assertIn(HOTKEY_ID_REINSERT_LAST, backend.registered)
            self.assertEqual(profile.read_bytes(), before)
            return True

        bridge.start = start
        self.assertTrue(desktop.start())
        loaded = AppConfig.load(profile)
        self.assertEqual(loaded.hotkey.reinsert_last_key, FALLBACK)
        self.assertEqual(loaded.overlay.opacity, 0.54)
        self.assertFalse(loaded.feedback.sounds_enabled)
        self.assertEqual(loaded.led.brightness, 37)
        persisted = profile.read_bytes()
        self.assertTrue(desktop.start())
        self.assertEqual(profile.read_bytes(), persisted)

    def test_disabled_and_wake_only_never_register_or_rewrite_profile(self):
        for mode in ("disabled", "wake-only"):
            for success in (False, True):
                with self.subTest(mode=mode, success=success):
                    desktop, bridge, backend, profile = self.make_desktop(success=success, mode=mode)
                    before = profile.read_bytes()
                    self.assertEqual(desktop.start(), success)
                    self.assertEqual(backend.registered, [])
                    self.assertEqual(backend.attempts, [])
                    self.assertEqual(profile.read_bytes(), before)
                    desktop.shutdown()

    def test_save_failure_stops_started_core_and_restores_hotkeys(self):
        desktop, bridge, backend, profile = self.make_desktop(success=True)
        before = profile.read_bytes()
        old_key = desktop.config.hotkey.reinsert_last_key
        with patch.object(desktop.config, "save_user", side_effect=PermissionError("read-only profile")):
            self.assertFalse(desktop.start())
        self.assertIn("start", bridge.calls)
        self.assertIn(("stop", 10.0), bridge.calls)
        self.assertEqual(profile.read_bytes(), before)
        self.assertEqual(desktop.config.hotkey.reinsert_last_key, old_key)
        self.assertFalse(desktop.hotkeys.is_registered)
        self.assertEqual(backend.active, set())
        self.assertFalse(desktop._started)

    def test_retry_after_failed_core_uses_original_binding_then_persists(self):
        desktop, bridge, backend, profile = self.make_desktop(success=False)
        before = profile.read_bytes()
        self.assertFalse(desktop.start())
        self.assertEqual(profile.read_bytes(), before)
        bridge.start_result = True
        self.assertTrue(desktop.start())
        self.assertEqual(AppConfig.load(profile).hotkey.reinsert_last_key, FALLBACK)
