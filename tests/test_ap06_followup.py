"""Focused AP06 follow-up tests for modes, settings and dictation windows."""

from __future__ import annotations

import asyncio
import copy
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDoubleSpinBox,
    QKeySequenceEdit,
)

from voice_stt_client.core.audio_capture import AudioCapture
from voice_stt_client.core.config import AppConfig, OperatingMode, SessionConfig
from voice_stt_client.core.event_models import CanonicalEventType
from voice_stt_client.core.history import TranscriptHistoryManager
from voice_stt_client.core.settings_metadata import (
    ApplyPolicy,
    SETTING_DEFINITIONS,
    SettingType,
    build_candidate,
    get_config_value,
)
from tests.test_ui_application import FakeBridge, FakeGuard, FakeHotkeyBackend
from voice_stt_client.ui.application import DesktopApplication
from voice_stt_client.ui.hotkeys import (
    GlobalHotkeyManager,
    HOTKEY_ID_CANCEL,
    HOTKEY_ID_FINISH,
)
from voice_stt_client.ui.settings_dialog import SettingsDialog


class RecordingHotkeyBackend:
    def __init__(self) -> None:
        self.registered: list[int] = []
        self.unregistered: list[int] = []

    def register(self, hwnd, hotkey_id, modifiers, virtual_key):
        self.registered.append(hotkey_id)

    def unregister(self, hwnd, hotkey_id):
        self.unregistered.append(hotkey_id)




class TestSessionConfigAndMetadata(unittest.TestCase):



    def test_every_metadata_path_targets_typed_config(self):
        config = AppConfig()
        for definition in SETTING_DEFINITIONS:
            get_config_value(config, definition.path)
            self.assertIsInstance(definition.setting_type, SettingType)

    def test_candidate_validation_does_not_mutate_current_config(self):
        current = AppConfig()
        candidate = build_candidate(
            current, {"overlay.opacity": 0.55}
        )
        self.assertEqual(current.overlay.opacity, 0.85)
        self.assertEqual(candidate.overlay.opacity, 0.55)
        with self.assertRaises(ValueError):
            build_candidate(current, {"overlay.opacity": 1.5})

    def test_project_and_user_files_are_layered_and_save_is_atomic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project.yaml"
            user = root / "user.yaml"
            project.write_text(
                "overlay:\n  enabled: false\nserver:\n  ping_interval: 9\n",
                encoding="utf-8",
            )
            user.write_text(
                "overlay:\n  enabled: true\nsession:\n  mode: wake_word\n",
                encoding="utf-8",
            )
            with patch("voice_stt_client.core.config.DEFAULT_CONFIG_PATH", project):
                config = AppConfig.load(user_path=user)
            self.assertTrue(config.overlay.enabled)
            self.assertEqual(config.server.ping_interval, 9)
            self.assertEqual(config.session.mode, "wake_word")

            destination = root / "saved.yaml"
            destination.write_text("old: value\n", encoding="utf-8")
            with patch("voice_stt_client.core.config.os.replace", side_effect=OSError("disk")):
                with self.assertRaises(OSError):
                    config.save(destination)
            self.assertEqual(destination.read_text(encoding="utf-8"), "old: value\n")
            self.assertFalse(any(root.glob(f".{destination.name}.*.tmp")))

    def test_unknown_user_field_keeps_valid_override(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project.yaml"
            user = root / "user.yaml"
            project.write_text("overlay:\n  enabled: false\n", encoding="utf-8")
            user.write_text(
                "overlay:\n  enabled: true\n  invented: 123\n",
                encoding="utf-8",
            )
            with patch("voice_stt_client.core.config.DEFAULT_CONFIG_PATH", project):
                config = AppConfig.load(user_path=user)
            self.assertTrue(config.overlay.enabled)

    def test_legacy_user_config_is_fallback_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project.yaml"
            current = root / "current.yaml"
            legacy = root / "legacy.yaml"
            project.write_text("overlay:\n  enabled: false\n", encoding="utf-8")
            legacy.write_text("overlay:\n  enabled: true\n", encoding="utf-8")
            with (
                patch("voice_stt_client.core.config.DEFAULT_CONFIG_PATH", project),
                patch("voice_stt_client.core.config.DEFAULT_USER_CONFIG_PATH", current),
                patch("voice_stt_client.core.config.LEGACY_USER_CONFIG_PATH", legacy),
            ):
                self.assertTrue(AppConfig.load().overlay.enabled)
                current.write_text(
                    "overlay:\n  enabled: false\n", encoding="utf-8"
                )
                self.assertFalse(AppConfig.load().overlay.enabled)


WINDOW = 0.25
"""Base length for the dictation windows in these tests.

Short, so the tests stay quick -- but not so short that they race the clock.
One assertion here checks that a window has *not* expired yet, and that is the
fragile direction: overshooting a sleep is normal, and Windows schedules on
roughly 15 ms granularity. At the original 40 ms window checked at 30 ms, ten
milliseconds of scheduling noise was enough to fail it, which is why it failed
only on a busy machine and never when run alone.
"""








class TestHistoryDeletion(unittest.TestCase):
    def test_delete_and_clear_keep_dedupe_semantics(self):
        config = AppConfig()
        config.history.persistent.enabled = False
        history = TranscriptHistoryManager(config.history)
        first = history.add_entry("session", 1, "eins")
        history.add_entry("session", 2, "zwei")
        self.assertTrue(history.delete_entry(first.id))
        duplicate = history.add_entry_with_status("session", 1, "eins")
        self.assertIsNone(duplicate.entry)
        self.assertEqual(history.clear_entries(), 1)
        self.assertEqual(history.get_memory_entries(), [])


class TestActionHotkeys(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_optional_actions_are_registered_and_dispatched(self):
        backend = RecordingHotkeyBackend()
        calls: list[str] = []
        manager = GlobalHotkeyManager(
            toggle_key="Ctrl+Shift+Space",
            reinsert_last_key="Ctrl+Alt+Space",
            finish_key="Ctrl+Shift+Enter",
            cancel_key="Ctrl+Shift+Escape",
            on_toggle=lambda: calls.append("primary"),
            on_reinsert_last=lambda: calls.append("reinsert"),
            on_finish=lambda: calls.append("finish"),
            on_cancel=lambda: calls.append("cancel"),
            backend=backend,
            application=self.app,
        )
        self.assertTrue(manager.register())
        self.assertTrue(manager.dispatch_hotkey_id(HOTKEY_ID_FINISH))
        self.assertTrue(manager.dispatch_hotkey_id(HOTKEY_ID_CANCEL))
        self.assertEqual(calls, ["finish", "cancel"])
        manager.unregister()


class TestSettingsDialog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])



    def test_reopening_dialog_discards_unapplied_draft(self):
        dialog = SettingsDialog(AppConfig(), lambda candidate, policies: True)
        dialog.show()
        opacity = dialog._editors["overlay.opacity"]
        opacity.setValue(0.55)
        dialog.status_label.setText("Vorschlag noch nicht übernommen")

        dialog.close()
        dialog.show()

        self.assertEqual(opacity.value(), dialog._config.overlay.opacity)
        self.assertEqual(dialog.status_label.text(), "")
        dialog.close()



    def test_slider_spinbox_preserves_non_step_audio_rate(self):
        config = AppConfig()
        config.audio.sample_rate = 44100
        dialog = SettingsDialog(config, lambda candidate, policies: True)
        editor = dialog._editors["audio.sample_rate"]
        self.assertEqual(editor.value(), 44100)
        editor.slider.setValue(48000 - 8000)
        self.assertEqual(editor.value(), 48000)
        dialog.close()

    def test_installed_defaults_round_trip_through_every_settings_editor(self):
        with tempfile.TemporaryDirectory() as directory:
            config = AppConfig.load(user_path=Path(directory) / "missing.yaml")
        dialog = SettingsDialog(config, lambda candidate, policies: True)
        for path, definition in dialog._definitions.items():
            if path not in dialog._editors:
                continue
            with self.subTest(path=path):
                value = dialog._editor_value(definition)
                expected = get_config_value(config, path)
                if path == "session.manual_trigger_enabled":
                    expected = config.session.effective_manual_trigger_enabled
                elif path == "session.wake_word_trigger_enabled":
                    expected = config.session.effective_wake_word_trigger_enabled
                if isinstance(expected, float) and expected is not None:
                    self.assertAlmostEqual(value, expected, places=3)
                else:
                    self.assertEqual(value, expected)
        self.assertTrue(dialog._editors["feedback.start_sound"].text())
        dialog.close()

    def test_standard_editor_builds_typed_candidate(self):
        calls = []
        dialog = SettingsDialog(
            AppConfig(),
            lambda candidate, policies: calls.append((candidate, policies)) or True,
        )
        opacity = dialog._editors["overlay.opacity"]
        self.assertIsInstance(opacity, QDoubleSpinBox)
        opacity.setValue(0.55)
        dialog.apply_changes()
        self.assertEqual(len(calls), 1)
        self.assertIsInstance(calls[0][0].overlay.opacity, float)
        self.assertEqual(calls[0][0].overlay.opacity, 0.55)
        dialog.close()
