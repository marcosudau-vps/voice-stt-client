"""Feature/Release integration boundaries; no V2 lifecycle implementation."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml
from PySide6.QtWidgets import QApplication

from voice_stt_client import app
from voice_stt_client.core.config import AppConfig
from voice_stt_client.core.history import TranscriptHistoryManager
from voice_stt_client.ui.v2_application import V2DesktopApplication as DesktopApplication
from voice_stt_client.ui.settings_dialog import SettingsDialog
from tests.test_ui_application import FakeBridge, FakeGuard, FakeHotkeyBackend, FakeLedFeedback


class IntegratedPreferences(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_disabled_hotkeys_remain_disabled_and_do_not_block_startup(self):
        config = AppConfig()
        config.hotkey.enabled = False
        bridge = FakeBridge()
        backend = FakeHotkeyBackend(fail=True)
        desktop = DesktopApplication(
            self.qt, config, FakeGuard(), bridge=bridge,
            hotkey_backend=backend, led_feedback=FakeLedFeedback(),
        )
        self.addCleanup(desktop.shutdown)
        with patch("voice_stt_client.ui.application.QMessageBox.critical"):
            self.assertTrue(desktop.start())
        self.assertFalse(config.hotkey.enabled)
        self.assertEqual(backend.registered, [])
        self.assertIn("start", bridge.calls)


    def test_cli_profile_argument_reaches_loader_without_touching_runtime(self):
        profile = Path("explicit-profile.yaml")
        with patch.object(app.AppConfig, "load", side_effect=RuntimeError("loader reached")) as loader:
            with self.assertRaisesRegex(RuntimeError, "loader reached"):
                app.main(["--config", str(profile), "--headless"])
        loader.assert_called_once_with(profile)

    def test_explicit_profile_keeps_feature_flags_and_preferences_on_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            profile = Path(folder) / "profile.yaml"
            profile.write_text(yaml.safe_dump({
                "session": {"manual_trigger_enabled": True, "wake_word_trigger_enabled": True},
                "hotkey": {"enabled": False, "toggle_key": "Ctrl+F8"},
                "feedback": {"sounds_enabled": False, "start_sound": "custom.wav"},
                "led": {"brightness": 37},
            }), encoding="utf-8")
            config = AppConfig.load(profile)
            config.save_user()
            loaded = AppConfig.load(profile)
            self.assertTrue(loaded.session.effective_manual_trigger_enabled)
            self.assertTrue(loaded.session.effective_wake_word_trigger_enabled)
            self.assertFalse(loaded.hotkey.enabled)
            self.assertEqual(loaded.hotkey.toggle_key, "Ctrl+F8")
            self.assertFalse(loaded.feedback.sounds_enabled)
            self.assertEqual(loaded.feedback.start_sound, "custom.wav")
            self.assertEqual(loaded.led.brightness, 37)

    def test_environment_profile_never_silently_falls_back_to_legacy(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            selected = root / "selected.yaml"
            legacy = root / "legacy.yaml"
            legacy.write_text("overlay:\n  opacity: 0.23\n", encoding="utf-8")
            with patch.dict(os.environ, {"VOICESTT_CLIENT_CONFIG": str(selected)}), patch(
                "voice_stt_client.core.config.DEFAULT_USER_CONFIG_PATH", selected
            ), patch("voice_stt_client.core.config.LEGACY_USER_CONFIG_PATH", legacy):
                with self.assertRaises(FileNotFoundError):
                    AppConfig.load()
                selected.write_text("overlay:\n  opacity: 0.54\n", encoding="utf-8")
                config = AppConfig.load()
                self.assertEqual(config.overlay.opacity, 0.54)
                config.save_user()
            self.assertEqual(legacy.read_text(encoding="utf-8"), "overlay:\n  opacity: 0.23\n")

    def test_existing_legacy_history_is_read_in_place_without_loss(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            legacy = root / "local" / "RealtimeSTT_Client" / "transcript_history.db"
            config = AppConfig().history
            config.persistent.store_all = True
            first = TranscriptHistoryManager(config, db_path=legacy)
            entry = first.add_entry("legacy-session", 1, "synthetic migration fixture")
            before = legacy.read_bytes()
            with patch.dict(os.environ, {"LOCALAPPDATA": str(root / "local")}), patch(
                "voice_stt_client.core.history.Path.home", return_value=root / "home"
            ):
                with patch.dict(os.environ):
                    os.environ.pop("VOICESTT_CLIENT_HOME", None)
                    loaded = TranscriptHistoryManager(config)
            # Windows hosted runners may expose TEMP through an 8.3 alias.
            # Verify the same existing file, not its spelling.
            self.assertTrue(loaded.db_path.samefile(legacy))
            self.assertEqual(loaded.get_persistent_entries()[0].id, entry.id)
            self.assertEqual(legacy.read_bytes(), before)
            self.assertFalse((root / "home" / ".voice-stt").exists())

    def test_feature_pr_ci_tests_namespace_build_and_installed_wheel(self):
        root = Path(__file__).resolve().parents[1]
        workflow = yaml.load((root / ".github/workflows/ci.yml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        self.assertIn("pull_request", workflow["on"])
        self.assertIn("feat/client-v2", workflow["on"]["push"]["branches"])
        commands = "\n".join(step.get("run", "") for step in workflow["jobs"]["test-and-build"]["steps"])
        for command in ("unittest discover", "compileall -q voice_stt_client", "scripts/build.py", "build --sdist --wheel", "find_spec('core')", "find_spec('ui')"):
            self.assertIn(command, commands)


if __name__ == "__main__":
    unittest.main()
