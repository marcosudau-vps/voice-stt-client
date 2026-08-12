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

from PySide6.QtWidgets import QApplication, QCheckBox, QDoubleSpinBox

from core.audio_capture import AudioCapture
from core.config import AppConfig, OperatingMode, SessionConfig
from core.controller import (
    DictationState,
    DictationWindowPhase,
    STTController,
)
from core.event_models import CanonicalEventType
from core.history import TranscriptHistoryManager
from core.settings_metadata import (
    ApplyPolicy,
    SETTING_DEFINITIONS,
    SettingType,
    build_candidate,
    get_config_value,
)
from core.stt_session import (
    ClientState,
    SessionConfigurationError,
    SessionState,
    STTSession,
    TransportState,
)
from tests.test_controller import (
    FakeAudioCapture,
    FakeInjectionQueue,
    FakeSTTSession,
)
from tests.test_ui_application import FakeBridge, FakeGuard, FakeHotkeyBackend
from ui.application import DesktopApplication
from ui.hotkeys import (
    GlobalHotkeyManager,
    HOTKEY_ID_CANCEL,
    HOTKEY_ID_FINISH,
)
from ui.settings_dialog import SettingsDialog


class RecordingHotkeyBackend:
    def __init__(self) -> None:
        self.registered: list[int] = []
        self.unregistered: list[int] = []

    def register(self, hwnd, hotkey_id, modifiers, virtual_key):
        self.registered.append(hotkey_id)

    def unregister(self, hwnd, hotkey_id):
        self.unregistered.append(hotkey_id)


class ReconfigurableFakeSTTSession(FakeSTTSession):
    """Long-running fake that reproduces real session generations."""

    def __init__(self) -> None:
        super().__init__()
        self.reconfigure_calls = []
        self._run_stopped = asyncio.Event()

    async def run(self) -> None:
        await self._run_stopped.wait()

    async def stop(self) -> None:
        await super().stop()
        self._run_stopped.set()

    async def reconfigure(self, session_config, server_config) -> None:
        self.reconfigure_calls.append((session_config.mode, server_config.url))
        self.generation += 1
        self._streaming = False
        self.state = ClientState(
            transport=TransportState.READY,
            ready_ok=True,
            server_status=SessionState.IDLE,
            generation=self.generation,
            session_id=f"fake-session-{self.generation}",
        )


class TestSessionConfigAndMetadata(unittest.TestCase):
    def test_url_generation_replaces_each_public_key_exactly_once(self):
        config = SessionConfig(
            mode=OperatingMode.WAKE_WORD.value,
            wake_words="hey jarvis,computer",
            wake_word_sensitivity=0.42,
        )
        url = config.build_url(
            "wss://example/ws?keep=1&wakeWordEnabled=false&wakeWordEnabled=false"
        )
        self.assertEqual(url.count("wakeWordEnabled="), 1)
        self.assertIn("wakeWordEnabled=true", url)
        self.assertIn("wakeWords=hey+jarvis%2Ccomputer", url)
        self.assertIn("keep=1", url)

    def test_effective_mode_mismatch_is_rejected(self):
        config = AppConfig()
        session = STTSession(
            config.server,
            config.session,
            require_session_contract=True,
        )
        with self.assertRaises(SessionConfigurationError):
            session._verify_session_contract(
                {
                    "type": "hello",
                    "sessionConfig": {"effectiveWakeWordEnabled": True},
                }
            )

    def test_fallback_metadata_is_recorded_after_valid_confirmation(self):
        config = AppConfig()
        session = STTSession(
            config.server,
            config.session,
            require_session_contract=True,
        )
        session._verify_session_contract(
            {
                "type": "hello",
                "sessionConfig": {
                    "effectiveWakeWordEnabled": False,
                    "fallbacks": ["sensitivity"],
                    "warnings": ["fallback used"],
                    "ignoredFields": ["wakeWords"],
                },
                "sessionCapabilities": {"availableWakeWords": []},
            }
        )
        self.assertFalse(
            session.effective_session_config["effectiveWakeWordEnabled"]
        )
        self.assertEqual(session.session_capabilities["availableWakeWords"], [])

    def test_every_metadata_path_targets_typed_config(self):
        config = AppConfig()
        for definition in SETTING_DEFINITIONS:
            get_config_value(config, definition.path)
            self.assertIsInstance(definition.setting_type, SettingType)

    def test_candidate_validation_does_not_mutate_current_config(self):
        current = AppConfig()
        candidate = build_candidate(
            current, {"dictation_window.followup_timeout": 7.5}
        )
        self.assertEqual(current.dictation_window.followup_timeout, 3.0)
        self.assertEqual(candidate.dictation_window.followup_timeout, 7.5)
        with self.assertRaises(ValueError):
            build_candidate(current, {"dictation_window.followup_timeout": 0.0})

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
            with patch("core.config.DEFAULT_CONFIG_PATH", project):
                config = AppConfig.load(user_path=user)
            self.assertTrue(config.overlay.enabled)
            self.assertEqual(config.server.ping_interval, 9)
            self.assertEqual(config.session.mode, "wake_word")

            destination = root / "saved.yaml"
            destination.write_text("old: value\n", encoding="utf-8")
            with patch("core.config.os.replace", side_effect=OSError("disk")):
                with self.assertRaises(OSError):
                    config.save(destination)
            self.assertEqual(destination.read_text(encoding="utf-8"), "old: value\n")
            self.assertFalse(any(root.glob(f".{destination.name}.*.tmp")))

    def test_unknown_user_field_rejects_complete_override(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project.yaml"
            user = root / "user.yaml"
            project.write_text("overlay:\n  enabled: false\n", encoding="utf-8")
            user.write_text(
                "overlay:\n  enabled: true\n  invented: 123\n",
                encoding="utf-8",
            )
            with patch("core.config.DEFAULT_CONFIG_PATH", project):
                config = AppConfig.load(user_path=user)
            self.assertFalse(config.overlay.enabled)


WINDOW = 0.25
"""Base length for the dictation windows in these tests.

Short, so the tests stay quick -- but not so short that they race the clock.
One assertion here checks that a window has *not* expired yet, and that is the
fragile direction: overshooting a sleep is normal, and Windows schedules on
roughly 15 ms granularity. At the original 40 ms window checked at 30 ms, ten
milliseconds of scheduling noise was enough to fail it, which is why it failed
only on a busy machine and never when run alone.
"""


class TestDictationWindow(unittest.IsolatedAsyncioTestCase):
    def make_controller(self) -> tuple[STTController, FakeSTTSession]:
        config = AppConfig()
        config.history.enabled = False
        config.dictation_window.initial_speech_timeout = WINDOW
        config.dictation_window.followup_timeout = WINDOW / 2
        config.dictation_window.extension_seconds = WINDOW
        config.dictation_window.timeout_warning_seconds = WINDOW / 4
        session = FakeSTTSession()
        controller = STTController(
            config,
            session=session,
            audio=FakeAudioCapture(),
            injection_queue=FakeInjectionQueue(),
        )
        return controller, session

    async def test_initial_timeout_stops_accidental_start(self):
        controller, _ = self.make_controller()
        result = await controller.start_dictation()
        self.assertTrue(result.success)
        self.assertEqual(
            controller.get_snapshot().dictation_window_phase,
            DictationWindowPhase.WAITING_FIRST_SPEECH,
        )
        await asyncio.sleep(WINDOW * 1.8)
        self.assertEqual(controller.dictation_state, DictationState.IDLE)

    async def test_timeline_and_extension_are_bound_to_current_window(self):
        controller, session = self.make_controller()
        await controller.start_dictation()
        controller.handle_server_event(
            "timeline",
            {
                "type": "timeline",
                "event": "recording_started",
                "sessionId": session.state.session_id,
                "_clientGeneration": session.generation,
            },
        )
        self.assertEqual(
            controller.get_snapshot().dictation_window_phase,
            DictationWindowPhase.SEGMENT_ACTIVE,
        )
        extension = controller.extend_dictation_window()
        self.assertEqual(extension.status, "extension_armed")
        controller.handle_server_event(
            "timeline",
            {
                "type": "timeline",
                "event": "recording_ended",
                "sessionId": session.state.session_id,
                "_clientGeneration": session.generation,
            },
        )
        await asyncio.sleep(WINDOW * 0.6)
        self.assertEqual(controller.dictation_state, DictationState.ACTIVE)
        await asyncio.sleep(WINDOW * 1.2)
        self.assertEqual(controller.dictation_state, DictationState.IDLE)

    async def test_stale_timeline_event_does_not_cancel_initial_timer(self):
        controller, session = self.make_controller()
        await controller.start_dictation()
        controller.handle_server_event(
            "timeline",
            {
                "type": "timeline",
                "event": "recording_started",
                "sessionId": session.state.session_id,
                "_clientGeneration": session.generation - 1,
            },
        )
        self.assertEqual(
            controller.get_snapshot().dictation_window_phase,
            DictationWindowPhase.WAITING_FIRST_SPEECH,
        )
        await controller.stop_dictation()

    async def test_hotkey_followup_warns_then_new_speech_clears_warning(self):
        controller, session = self.make_controller()
        decisions = []
        controller.on_feedback_decision = decisions.append
        await controller.start_dictation()
        base = {
            "type": "timeline",
            "sessionId": session.state.session_id,
            "_clientGeneration": session.generation,
        }
        controller.handle_server_event(
            "timeline", {**base, "event": "recording_started"}
        )
        controller.handle_server_event(
            "timeline", {**base, "event": "recording_ended"}
        )

        await asyncio.sleep(WINDOW * 0.35)
        self.assertIn(
            CanonicalEventType.CLIENT_DICTATION_TIMEOUT_WARNING,
            [item.event.event_type for item in decisions],
        )
        controller.handle_server_event(
            "timeline", {**base, "event": "recording_started"}
        )
        self.assertEqual(
            [item.event.event_type for item in decisions][-1],
            CanonicalEventType.CLIENT_DICTATION_TIMEOUT_WARNING_CLEARED,
        )
        await controller.stop_dictation()

    async def test_wake_word_followup_uses_server_duration_and_clears_on_speech(self):
        config = AppConfig()
        config.history.enabled = False
        config.session.mode = "wake_word"
        config.dictation_window.timeout_warning_seconds = WINDOW / 4
        session = FakeSTTSession()
        controller = STTController(
            config,
            session=session,
            audio=FakeAudioCapture(),
            injection_queue=FakeInjectionQueue(),
        )
        decisions = []
        controller.on_feedback_decision = decisions.append
        await controller.start_dictation()
        base = {
            "type": "timeline",
            "sessionId": session.state.session_id,
            "_clientGeneration": session.generation,
        }
        controller.handle_server_event(
            "timeline",
            {
                **base,
                "event": "wakeword_followup_started",
                "durationSeconds": WINDOW,
            },
        )

        await asyncio.sleep(WINDOW * 0.8)
        self.assertIn(
            CanonicalEventType.CLIENT_DICTATION_TIMEOUT_WARNING,
            [item.event.event_type for item in decisions],
        )
        controller.handle_server_event(
            "timeline", {**base, "event": "recording_started"}
        )
        self.assertEqual(
            [item.event.event_type for item in decisions][-1],
            CanonicalEventType.CLIENT_DICTATION_TIMEOUT_WARNING_CLEARED,
        )
        await controller.stop_dictation()

    async def test_unavailable_audio_candidate_does_not_change_runtime(self):
        controller, _ = self.make_controller()
        candidate = AppConfig()
        candidate.history.enabled = False
        candidate.audio.device = 99
        with patch.object(
            AudioCapture,
            "list_devices",
            return_value=[
                {
                    "index": 3,
                    "name": "Mic",
                    "channels": 1,
                    "default_samplerate": 16000,
                    "is_default": True,
                }
            ],
        ):
            result = await controller.apply_runtime_config(candidate)
        self.assertFalse(result.success)
        self.assertIsNone(controller.config.audio.device)

    async def test_server_recorder_state_change_publishes_snapshot_for_tray(self):
        controller, session = self.make_controller()
        snapshots = []
        controller.on_snapshot_change = snapshots.append

        session.state.server_status = SessionState.WAKEWORD_DETECTED
        controller._handle_state_change(session.state)
        controller._handle_state_change(session.state)

        self.assertEqual(len(snapshots), 1)
        self.assertEqual(
            snapshots[0].server_status,
            SessionState.WAKEWORD_DETECTED,
        )


class TestConfigurationReconnectGuard(unittest.IsolatedAsyncioTestCase):
    async def test_configuration_block_stops_connection_attempts_until_change(self):
        config = AppConfig()
        session = STTSession(config.server, config.session)
        session._configuration_blocked = True
        calls = 0

        async def connect_once():
            nonlocal calls
            calls += 1
            await session.stop()

        session._connect_and_run = connect_once
        run_task = asyncio.create_task(session.run())
        await asyncio.sleep(0.02)
        self.assertEqual(calls, 0)
        await session.reconfigure(config.session, config.server)
        await asyncio.wait_for(run_task, 0.2)
        self.assertEqual(calls, 1)


class TestRuntimeModeSwitchLifecycle(unittest.IsolatedAsyncioTestCase):
    def make_controller(
        self,
    ) -> tuple[
        STTController,
        ReconfigurableFakeSTTSession,
        FakeAudioCapture,
    ]:
        config = AppConfig()
        config.history.enabled = False
        session = ReconfigurableFakeSTTSession()
        audio = FakeAudioCapture()
        controller = STTController(
            config,
            session=session,
            audio=audio,
            injection_queue=FakeInjectionQueue(),
        )
        return controller, session, audio

    async def stop_controller(
        self,
        controller: STTController,
        run_task: asyncio.Task,
    ) -> None:
        await controller.shutdown()
        await asyncio.wait_for(run_task, 1.0)

    async def test_hotkey_wake_hotkey_switch_arms_stream_and_keeps_core_alive(self):
        controller, session, audio = self.make_controller()
        run_task = asyncio.create_task(controller.run())
        await asyncio.sleep(0.12)

        for cycle in range(3):
            wake_config = copy.deepcopy(controller.config)
            wake_config.session.mode = "wake_word"
            wake_result = await controller.apply_runtime_config(wake_config)

            self.assertTrue(wake_result.success, wake_result)
            self.assertEqual(controller.config.session.mode, "wake_word")
            self.assertEqual(controller.dictation_state, DictationState.ACTIVE)
            self.assertTrue(controller.dictation_requested)
            self.assertTrue(audio.is_running)
            self.assertFalse(run_task.done())

            hotkey_config = copy.deepcopy(controller.config)
            hotkey_config.session.mode = "hotkey"
            hotkey_result = await controller.apply_runtime_config(hotkey_config)

            self.assertTrue(hotkey_result.success, hotkey_result)
            self.assertEqual(controller.config.session.mode, "hotkey")
            self.assertEqual(controller.dictation_state, DictationState.IDLE)
            self.assertFalse(controller.dictation_requested)
            self.assertFalse(audio.is_running)
            await asyncio.sleep(0.15)
            self.assertFalse(
                run_task.done(),
                f"Core terminated during mode-switch cycle {cycle + 1}",
            )

        self.assertEqual(
            [mode for mode, _ in session.reconfigure_calls],
            ["wake_word", "hotkey"] * 3,
        )
        await self.stop_controller(controller, run_task)

    async def test_failed_wake_stream_activation_restores_hotkey_runtime(self):
        controller, session, audio = self.make_controller()
        run_task = asyncio.create_task(controller.run())
        await asyncio.sleep(0.12)
        session.send_start_should_fail = True

        candidate = copy.deepcopy(controller.config)
        candidate.session.mode = "wake_word"
        result = await controller.apply_runtime_config(candidate)

        self.assertFalse(result.success)
        self.assertEqual(result.status, "wake_word_arm_failed")
        self.assertEqual(controller.config.session.mode, "hotkey")
        self.assertEqual(controller.dictation_state, DictationState.IDLE)
        self.assertFalse(controller.dictation_requested)
        self.assertFalse(audio.is_running)
        self.assertEqual(
            [mode for mode, _ in session.reconfigure_calls],
            ["wake_word", "hotkey"],
        )
        self.assertFalse(run_task.done())
        await self.stop_controller(controller, run_task)

    async def test_switched_wake_mode_rearms_after_recoverable_reconnect(self):
        controller, session, audio = self.make_controller()
        run_task = asyncio.create_task(controller.run())
        await asyncio.sleep(0.12)

        candidate = copy.deepcopy(controller.config)
        candidate.session.mode = "wake_word"
        result = await controller.apply_runtime_config(candidate)
        self.assertTrue(result.success, result)
        first_start_calls = session.start_calls

        session.state = ClientState(
            transport=TransportState.DISCONNECTED,
            ready_ok=False,
            server_status=SessionState.CLOSED,
            generation=session.generation,
            session_id=session.state.session_id,
        )
        controller._handle_transport_change(TransportState.DISCONNECTED)
        self.assertEqual(controller.dictation_state, DictationState.IDLE)
        self.assertFalse(audio.is_running)

        session.generation += 1
        session.state = ClientState(
            transport=TransportState.READY,
            ready_ok=True,
            server_status=SessionState.IDLE,
            generation=session.generation,
            session_id=f"fake-session-{session.generation}",
        )
        controller._handle_transport_change(TransportState.READY)

        deadline = asyncio.get_running_loop().time() + 1.0
        while (
            controller.dictation_state != DictationState.ACTIVE
            and asyncio.get_running_loop().time() < deadline
        ):
            await asyncio.sleep(0.02)

        self.assertEqual(controller.dictation_state, DictationState.ACTIVE)
        self.assertGreater(session.start_calls, first_start_calls)
        self.assertTrue(audio.is_running)
        self.assertFalse(run_task.done())
        await self.stop_controller(controller, run_task)


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

    def test_five_tabs_and_standard_editor_types(self):
        calls = []
        dialog = SettingsDialog(
            AppConfig(),
            lambda candidate, policies: calls.append((candidate, policies)) or True,
        )
        self.assertEqual(
            [dialog.tabs.tabText(index) for index in range(dialog.tabs.count())],
            list(SettingsDialog.TAB_NAMES),
        )
        self.assertIsInstance(dialog._editors["hotkey.enabled"], QCheckBox)
        self.assertIsInstance(
            dialog._editors["overlay.opacity"], QDoubleSpinBox
        )
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

    def test_dependency_visibility_tracks_mode_and_sound_toggle(self):
        dialog = SettingsDialog(AppConfig(), lambda candidate, policies: True)
        wake_words = dialog._editors["session.wake_words"]
        self.assertTrue(wake_words.isHidden())
        mode = dialog._editors["session.mode"]
        mode.setCurrentIndex(mode.findData("wake_word"))
        self.assertFalse(wake_words.isHidden())
        start_sound = dialog._editors["feedback.start_sound"]
        self.assertTrue(start_sound.isHidden())
        sounds = dialog._editors["feedback.sounds_enabled"]
        sounds.setChecked(True)
        self.assertFalse(start_sound.isHidden())
        dialog.close()

    def test_failed_runtime_submit_rolls_hotkeys_and_file_back(self):
        class RejectingBridge(FakeBridge):
            def apply_runtime_config(self, candidate):
                self.calls.append(("apply_runtime_config", candidate))
                return False

        bridge = RejectingBridge()
        backend = FakeHotkeyBackend()
        desktop = DesktopApplication(
            self.app,
            AppConfig(),
            FakeGuard(),
            bridge=bridge,
            hotkey_backend=backend,
        )
        old_manager = desktop.hotkeys
        candidate = build_candidate(
            desktop.config, {"hotkey.toggle_key": "Ctrl+Shift+F12"}
        )
        with patch.object(AppConfig, "save_user") as save_user:
            accepted = desktop._apply_settings(
                candidate, frozenset({ApplyPolicy.HOTKEY_REREGISTER})
            )
        self.assertFalse(accepted)
        self.assertIs(desktop.hotkeys, old_manager)
        self.assertEqual(save_user.call_count, 2)
        desktop.shutdown()
