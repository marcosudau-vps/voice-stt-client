"""Composition and lifecycle tests for the AP06 desktop application."""

from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from app import build_argument_parser
from core.config import AppConfig, LedConfig
from core.controller import CommandResult
from core.event_models import (
    CanonicalEventType,
    EventOrigin,
    FeedbackImpulse,
    FeedbackSource,
    FeedbackState,
    NormalizedFeedbackEvent,
)
from core.feedback_mapping import (
    AppActionId,
    AppEffect,
    FeedbackRule,
    LedCall,
    LedVerb,
    SoundCueId,
    SoundEffect,
)
from core.feedback_reducer import FeedbackDecision
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
    feedback_decision_received = Signal(object)
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

    def report_local_feedback(self, event_type, details=None):
        self.calls.append(("local_feedback", event_type, details))
        return True

    def set_microphone_muted(self, muted):
        self.calls.append(("mute", muted))
        return True

    def reconnect_server(self):
        self.calls.append("reconnect_server")
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


class FakeLedFeedback:
    def __init__(self):
        self.calls = []
        self.verified = None
        self.mute_reaches_device = True
        self.config = LedConfig(enabled=False)
        self.noted = None
        self.watching = False
        self.controller = SimpleNamespace(set_output=lambda **kwargs: None)

    def submit(self, calls, *, live=False):
        self.calls.append((calls, live))
        return True

    def verify_targets(self, targets):
        self.verified = list(targets)

    def set_device_mute(self, muted):
        self.calls.append(("device_mute", muted))
        return self.mute_reaches_device

    def note_device_mute(self, muted):
        self.noted = muted

    def watch_device_mute(self):
        self.watching = True

    @property
    def unavailable_seconds(self):
        return 0.0

    def shutdown(self):
        self.calls.append("shutdown")
        return True


class TestDesktopApplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def make_desktop(
        self,
        *,
        bridge=None,
        hotkey_backend=None,
        guard=None,
        led_feedback=None,
        config=None,
    ):
        if config is None:
            # No LED output unless a test asks for one. The default config names
            # the reSpeaker, and building it for real would open a USB transport
            # from a unit test — slow, and dependent on what is plugged in.
            config = AppConfig()
            config.led = LedConfig(enabled=False)
        return DesktopApplication(
            self.application,
            config,
            guard or FakeGuard(),
            bridge=bridge or FakeBridge(),
            hotkey_backend=hotkey_backend or FakeHotkeyBackend(),
            led_feedback=led_feedback,
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

    def test_mapped_feedback_decision_updates_ui_and_enqueues_one_sound(self):
        bridge = FakeBridge()
        led_feedback = FakeLedFeedback()
        desktop = self.make_desktop(
            bridge=bridge,
            led_feedback=led_feedback,
        )
        self.addCleanup(desktop.shutdown)
        desktop.sound_feedback.play = MagicMock(return_value=True)
        decision = FeedbackDecision(
            state=FeedbackState.RECORDING,
            source=FeedbackSource.EVENT_STREAM,
            rule=FeedbackRule(
                led=(LedCall(LedVerb.SET_STATE, target="listening"),),
                sound=SoundEffect(SoundCueId.START, 0.4),
                app=AppEffect(AppActionId.INDICATOR_RECORDING),
            ),
            event=NormalizedFeedbackEvent(
                event_type=CanonicalEventType.SERVER_RECORDING_STARTED,
                origin=EventOrigin.LIVE,
                source=FeedbackSource.EVENT_STREAM,
                state=FeedbackState.RECORDING,
                impulse=FeedbackImpulse.RECORDING_STARTED,
            ),
            impulse=FeedbackImpulse.RECORDING_STARTED,
        )

        bridge.feedback_decision_received.emit(decision)
        self.application.processEvents()

        self.assertEqual(desktop.tray.status_action.text(), "Sprache wird aufgenommen")
        self.assertEqual(desktop.overlay.label.text(), "Aufnahme läuft")
        desktop.sound_feedback.play.assert_called_once_with(decision.rule.sound)
        self.assertIn((decision.rule.led, True), led_feedback.calls)

    def test_replay_or_unpublished_decision_never_reaches_ui_adapters(self):
        bridge = FakeBridge()
        led_feedback = FakeLedFeedback()
        desktop = self.make_desktop(
            bridge=bridge,
            led_feedback=led_feedback,
        )
        self.addCleanup(desktop.shutdown)
        desktop.sound_feedback.play = MagicMock(return_value=True)
        decision = FeedbackDecision(
            state=FeedbackState.RECORDING,
            source=FeedbackSource.EVENT_STREAM,
            rule=FeedbackRule(
                led=(LedCall(LedVerb.SET_STATE, target="listening"),),
                sound=SoundEffect(SoundCueId.START),
                app=AppEffect(AppActionId.INDICATOR_RECORDING),
            ),
            publish=False,
            replay=True,
        )

        bridge.feedback_decision_received.emit(decision)
        self.application.processEvents()

        desktop.sound_feedback.play.assert_not_called()
        self.assertNotIn((decision.rule.led, False), led_feedback.calls)
        self.assertFalse(desktop.overlay.isVisible())

    def test_legacy_command_completion_no_longer_triggers_sound(self):
        desktop = self.make_desktop()
        self.addCleanup(desktop.shutdown)
        desktop.sound_feedback.play = MagicMock(return_value=True)

        desktop._on_command_completed(
            "start_dictation",
            CommandResult(True, "started"),
        )

        desktop.sound_feedback.play.assert_not_called()

    def test_sound_failure_returns_as_canonical_local_fact(self):
        bridge = FakeBridge()
        desktop = self.make_desktop(bridge=bridge)
        self.addCleanup(desktop.shutdown)

        desktop.sound_feedback.failure.emit("backend:error")

        self.assertIn(
            (
                "local_feedback",
                CanonicalEventType.CLIENT_SOUND_FAILED,
                {"category": "backend"},
            ),
            bridge.calls,
        )

    def test_led_failure_returns_as_canonical_local_fact(self):
        bridge = FakeBridge()
        desktop = self.make_desktop(bridge=bridge)
        self.addCleanup(desktop.shutdown)

        desktop._on_led_failure("unavailable")

        self.assertIn(
            (
                "local_feedback",
                CanonicalEventType.CLIENT_LED_UNAVAILABLE,
                {"reason": "unavailable"},
            ),
            bridge.calls,
        )

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


class TestMuteAndReconnect(unittest.TestCase):
    """The three deliberate actions in the tray, and where each one lands."""

    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def make_desktop(self, bridge, led_feedback):
        config = AppConfig()
        config.led = LedConfig(enabled=False)
        return DesktopApplication(
            self.application,
            config,
            FakeGuard(),
            bridge=bridge,
            hotkey_backend=FakeHotkeyBackend(),
            led_feedback=led_feedback,
        )

    def test_muting_reaches_both_the_client_and_the_device(self):
        bridge, led = FakeBridge(), FakeLedFeedback()
        desktop = self.make_desktop(bridge, led)
        self.addCleanup(desktop.shutdown)

        desktop.set_microphone_muted(True)

        self.assertIn(("mute", True), bridge.calls)
        self.assertIn(("device_mute", True), led.calls)
        self.assertTrue(desktop.tray.mute_action.isChecked())
        self.assertIn("aufheben", desktop.tray.mute_action.text())

    def test_a_mute_the_device_never_saw_is_labelled_honestly(self):
        """The mute LED stays dark, so the menu must not imply otherwise."""
        bridge, led = FakeBridge(), FakeLedFeedback()
        led.mute_reaches_device = False
        desktop = self.make_desktop(bridge, led)
        self.addCleanup(desktop.shutdown)

        desktop.set_microphone_muted(True)

        self.assertIn(("mute", True), bridge.calls)
        self.assertIn("nur Client", desktop.tray.mute_action.text())

    def test_unmuting_clears_the_label(self):
        bridge, led = FakeBridge(), FakeLedFeedback()
        desktop = self.make_desktop(bridge, led)
        self.addCleanup(desktop.shutdown)

        desktop.set_microphone_muted(True)
        desktop.set_microphone_muted(False)

        self.assertIn(("mute", False), bridge.calls)
        self.assertFalse(desktop.tray.mute_action.isChecked())
        self.assertEqual(desktop.tray.mute_action.text(), "Mikrofon stummschalten")

    def test_the_tray_entry_toggles_the_mute(self):
        bridge, led = FakeBridge(), FakeLedFeedback()
        desktop = self.make_desktop(bridge, led)
        self.addCleanup(desktop.shutdown)

        desktop.tray.mute_action.trigger()

        self.assertIn(("mute", True), bridge.calls)

    def test_server_reconnect_goes_to_the_core(self):
        bridge, led = FakeBridge(), FakeLedFeedback()
        desktop = self.make_desktop(bridge, led)
        self.addCleanup(desktop.shutdown)

        desktop.tray.reconnect_server_action.trigger()

        self.assertIn("reconnect_server", bridge.calls)

    def test_device_reconnect_rebuilds_the_led_output(self):
        bridge, led = FakeBridge(), FakeLedFeedback()
        desktop = self.make_desktop(bridge, led)
        self.addCleanup(desktop.shutdown)

        desktop.tray.reconnect_device_action.trigger()

        self.assertIn("shutdown", led.calls)
        self.assertIsNot(desktop.led_feedback, led)
