"""AP06 composition root for the Windows tray application."""

from __future__ import annotations

import importlib.util
import logging
import signal
import sys
import threading
from dataclasses import replace
from typing import Optional, Sequence

from PySide6.QtCore import QObject, Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from core.config import AppConfig
from core.controller import CommandResult
from core.feedback_reducer import FeedbackDecision
from core.event_models import CanonicalEventType, FeedbackSource
from core.led_controller import LedConfigurationError
from core.settings_metadata import ApplyPolicy
from core.reinsertion import ReinsertionResult, ReinsertionStatus
from ui.core_bridge import CoreBridge
from ui.hotkeys import GlobalHotkeyManager, HotkeyBackend
from ui.feedback import SoundFeedback
from ui.led_feedback import LedFeedback
from ui.overlay import TranscriptOverlay
from ui.presentation import (
    FeedbackPresentation,
    IndicatorColor,
    presentation_for_feedback_decision,
)
from ui.single_instance import (
    InstanceAcquireStatus,
    SingleInstanceGuard,
)
from ui.settings_dialog import SettingsDialog
from ui.tray import TrayController, create_status_icon

logger = logging.getLogger("ui.application")

_TECHNICAL_EVENT_STREAM_EVENTS = {
    CanonicalEventType.CLIENT_EVENT_STREAM_CONNECTING,
    CanonicalEventType.CLIENT_EVENT_STREAM_REPLAYING,
    CanonicalEventType.CLIENT_EVENT_STREAM_LIVE,
    CanonicalEventType.CLIENT_EVENT_STREAM_DEGRADED,
}

EXIT_OK = 0
EXIT_ALREADY_RUNNING = 2
EXIT_INSTANCE_ERROR = 3
EXIT_TRAY_UNAVAILABLE = 4
EXIT_CORE_START_FAILED = 5
EXIT_UI_INITIALIZATION_FAILED = 6
EXIT_CONFIGURATION_INVALID = 7


class DesktopApplication(QObject):
    """Own all Qt-side AP06 components in the QApplication thread."""

    device_mute_changed = Signal(bool)
    """The device's mute line moved. Emitted from the LED worker, handled here.

    A signal rather than a direct call because the reading happens on the worker
    thread and everything it leads to -- the tray, the menu text -- belongs to
    the Qt thread.
    """

    def __init__(
        self,
        application: QApplication,
        config: AppConfig,
        instance_guard: SingleInstanceGuard,
        *,
        bridge: Optional[CoreBridge] = None,
        hotkey_backend: Optional[HotkeyBackend] = None,
        led_feedback: Optional[LedFeedback] = None,
    ) -> None:
        super().__init__()
        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError("DesktopApplication must be created in main thread")

        self.application = application
        self.config = config
        self.instance_guard = instance_guard
        self.bridge = bridge or CoreBridge(config)
        self.overlay = TranscriptOverlay(config.overlay)
        self.sound_feedback = SoundFeedback(config.feedback, self)
        self.led_feedback = led_feedback or LedFeedback(
            config.led,
            on_failure=self._on_led_failure,
            on_device_mute_changed=self.device_mute_changed.emit,
        )
        self._muted = False
        # Every effect a rule names has to exist before anything is meant to
        # light up. Raises LedConfigurationError, which run_gui turns into a
        # refusal to start -- unlike a missing device, which is not an error.
        self.led_feedback.verify_targets(config.feedback_mappings.led_targets())
        self._hotkey_backend = hotkey_backend
        self.settings_dialog: Optional[SettingsDialog] = None
        self._pending_config: Optional[AppConfig] = None
        self._pending_old_config: Optional[AppConfig] = None
        self._pending_old_hotkeys: Optional[GlobalHotkeyManager] = None
        self.tray = TrayController(
            on_toggle=getattr(
                self.bridge,
                "primary_dictation_action",
                self.bridge.toggle_dictation,
            ),
            on_reinsert_last=self.bridge.reinsert_last,
            on_reinsert_entry=self.bridge.reinsert_entry,
            on_request_history=lambda: self.bridge.request_history(10),
            on_quit=self.application.quit,
            on_settings=self.show_settings,
            on_switch_led_sink=self.switch_led_sink,
            on_toggle_mute=self.set_microphone_muted,
            on_reconnect_device=self.reconnect_device,
            on_reconnect_server=self.reconnect_server,
            parent=self,
        )
        self._led_watch = QTimer(self)
        self._led_watch.setInterval(10_000)
        self._led_watch.timeout.connect(self._review_led_availability)
        if self._simulation_offer_possible():
            self._led_watch.start()
        # The mute line can move without this application touching it, and only
        # the worker may read it.
        self.led_feedback.watch_device_mute()
        self.hotkeys = self._create_hotkey_manager(config)
        self._started = False
        self._shutting_down = False
        self._lifecycle_started_reported = False
        self._lifecycle_stopping_reported = False
        self._wire_signals()
        self.application.aboutToQuit.connect(self.shutdown)

    def _create_hotkey_manager(self, config: AppConfig) -> GlobalHotkeyManager:
        return GlobalHotkeyManager(
            toggle_key=config.hotkey.effective_toggle_key,
            reinsert_last_key=config.hotkey.reinsert_last_key,
            finish_key=config.hotkey.finish_key,
            cancel_key=config.hotkey.cancel_key,
            overlay_toggle_key=config.hotkey.overlay_toggle_key,
            on_toggle=getattr(
                self.bridge,
                "primary_dictation_action",
                self.bridge.toggle_dictation,
            ),
            on_reinsert_last=self.bridge.reinsert_last,
            on_finish=getattr(
                self.bridge, "stop_dictation", self.bridge.toggle_dictation
            ),
            on_cancel=getattr(
                self.bridge,
                "cancel_dictation",
                getattr(
                    self.bridge, "stop_dictation", self.bridge.toggle_dictation
                ),
            ),
            on_overlay_toggle=self.overlay.toggle_visibility,
            # Global hotkeys only make sense while the manual trigger is a
            # source for this session. A wake-word-only installation must not
            # claim system-wide key combinations, and must therefore also not
            # be able to fail on a hotkey conflict it never needed.
            enabled=(
                config.hotkey.enabled
                and config.session.effective_manual_trigger_enabled
            ),
            backend=self._hotkey_backend,
            application=self.application,
        )

    def _wire_signals(self) -> None:
        queued = Qt.ConnectionType.QueuedConnection
        self.bridge.snapshot_changed.connect(
            self.tray.update_snapshot, queued
        )
        self.bridge.feedback_decision_received.connect(
            self._on_feedback_decision,
            queued,
        )
        self.bridge.text_received.connect(self._on_text_received, queued)
        self.bridge.command_completed.connect(
            self._on_command_completed, queued
        )
        self.bridge.history_received.connect(self._on_history_received, queued)
        self.bridge.fatal_error.connect(self._on_fatal_error, queued)
        self.sound_feedback.failure.connect(self._on_sound_failure)
        self.device_mute_changed.connect(self._on_device_mute_changed, queued)

    def start(self) -> bool:
        if self._started:
            return True
        self.tray.show()
        hotkeys_ok = self.hotkeys.register()
        if not hotkeys_ok:
            self.overlay.show_hotkey_error()
        if not self.bridge.start():
            self._on_fatal_error("Core konnte nicht gestartet werden")
            self.hotkeys.unregister()
            self.tray.hide()
            return False
        self._started = True
        self._report_lifecycle_started()
        return True

    def _report_lifecycle_started(self) -> None:
        if self._lifecycle_started_reported:
            return
        if self.bridge.report_local_feedback(
            CanonicalEventType.CLIENT_LIFECYCLE_STARTED
        ):
            self._lifecycle_started_reported = True
        else:
            logger.warning("Could not publish client.lifecycle.started.")

    def _report_lifecycle_stopping(self) -> None:
        if self._lifecycle_stopping_reported or not self._started:
            return
        if self.bridge.report_local_feedback(
            CanonicalEventType.CLIENT_LIFECYCLE_STOPPING,
            wait_timeout=1.0,
        ):
            self._lifecycle_stopping_reported = True
            # The Core signal is queued back to this Qt thread. Deliver it
            # before the LED and sound adapters are torn down.
            self.application.processEvents()
        else:
            logger.info("Core was already unavailable during lifecycle shutdown.")

    @Slot(object)
    def _on_feedback_decision(self, decision: FeedbackDecision) -> None:
        if not isinstance(decision, FeedbackDecision):
            logger.warning("Ignoring invalid feedback decision from Core.")
            return
        if not decision.publish or decision.replay:
            return
        self._log_feedback_decision(decision)
        self.tray.update_feedback_decision(decision)
        presentation = presentation_for_feedback_decision(
            decision,
            operating_mode=self.config.session.presentation_mode,
        )
        if presentation is not None:
            self.overlay.show_feedback(presentation)
        self.sound_feedback.play(decision.rule.sound)
        self.led_feedback.submit(
            decision.rule.led,
            # An impulse marks a fact that just happened. Without one this is
            # rebuilt state, which may restore what the ring shows but must not
            # replay an announcement.
            live=self._allows_live_led_events(decision),
        )

    @staticmethod
    def _allows_live_led_events(decision: FeedbackDecision) -> bool:
        if decision.impulse is not None:
            return True
        event = decision.event
        return bool(
            event is not None
            and event.source is FeedbackSource.LOCAL_ONLY
            and event.event_type not in _TECHNICAL_EVENT_STREAM_EVENTS
        )

    @staticmethod
    def _log_feedback_decision(decision: FeedbackDecision) -> None:
        event = decision.event
        event_type = event.event_type.value if event is not None else None
        led_calls = [
            {"verb": call.verb.value, "target": call.target, "slot": call.slot}
            for call in decision.rule.led
        ]
        logger.info(
            "Feedback decision",
            extra={
                "event_type": event_type,
                "detail": {
                    "source": decision.source.value,
                    "state": decision.state.value,
                    "revision": decision.revision,
                    "duplicate": decision.duplicate,
                    "replay": decision.replay,
                    "eventId": event.event_id if event is not None else None,
                    "correlationId": (
                        event.correlation_id if event is not None else None
                    ),
                    "sound": (
                        {
                            "cue": decision.rule.sound.cue.value,
                            "action": decision.rule.sound.action,
                        }
                        if decision.rule.sound is not None
                        else None
                    ),
                    "led": led_calls,
                },
            },
        )

    @Slot(str)
    def _on_sound_failure(self, failure_key: str) -> None:
        category = failure_key.partition(":")[0] or "unknown"
        self.bridge.report_local_feedback(
            CanonicalEventType.CLIENT_SOUND_FAILED,
            {"category": category},
        )

    def _on_led_failure(self, reason: str) -> None:
        self.bridge.report_local_feedback(
            CanonicalEventType.CLIENT_LED_UNAVAILABLE,
            {"reason": reason},
        )

    # -- mute and manual reconnects -----------------------------------------

    def set_microphone_muted(self, muted: bool) -> None:
        """Mute the microphone here and on the device, and darken the ring.

        Both halves, because they answer different questions. The device line
        lights its own mute LED and mutes in hardware, which is what somebody
        looking at the reSpeaker expects to see. The client-side mute is what
        guarantees nothing captured leaves this machine -- and it still holds if
        the reSpeaker is unplugged, which is exactly when a mute must not
        quietly stop working.
        """
        self._muted = muted
        self.bridge.set_microphone_muted(muted)
        reached_device = False
        try:
            reached_device = self.led_feedback.set_device_mute(muted)
        except Exception:
            logger.exception("Setting the device mute line failed.")
        if reached_device:
            # Ours, so the watcher must not report it back as a change.
            self.led_feedback.note_device_mute(muted)

        self.tray.set_muted(muted, on_device=reached_device)
        if muted and not reached_device:
            self.tray.notify(
                "Mikrofon stummgeschaltet",
                "Der ReSpeaker war nicht erreichbar - die Mute-LED am Gerät "
                "bleibt aus. Aufgenommen wird trotzdem nichts.",
            )

    @Slot(bool)
    def _on_device_mute_changed(self, muted: bool) -> None:
        """The device's mute line moved without us moving it.

        X0D30 is the mute function, not the button: it reads the same however it
        was set. So this is simply "the device is now muted" and the client
        follows, rather than trying to work out who did it.
        """
        if muted == self._muted:
            return
        logger.info("Device mute changed to %s; following it.", muted)
        self._muted = muted
        self.bridge.set_microphone_muted(muted)
        try:
            self.led_feedback.controller.set_output(enabled=not muted)
        except Exception:
            logger.debug("could not follow the mute on the ring", exc_info=True)
        self.tray.set_muted(muted, on_device=True)

    def reconnect_device(self) -> None:
        """Drop the USB connection and build it again, now."""
        self.tray.notify("ReSpeaker", "Verbindung wird neu aufgebaut …")
        self._replace_led_feedback(self.config, self.config.led)
        if self._simulation_offer_possible():
            self.tray.offer_led_simulation(False)

    def reconnect_server(self) -> None:
        self.tray.notify("Server", "Verbindung wird neu aufgebaut …")
        self.bridge.reconnect_server()

    # -- offering the simulator ---------------------------------------------

    def _simulation_offer_possible(self) -> bool:
        """Whether offering to switch would lead anywhere.

        Three conditions, all of them cheap to check and all of them reasons the
        offer would be a lie: the ring has to be the thing that is failing, the
        offer has to be switched on, and the simulator has to be installed --
        it is an optional package and a release build does not carry it.
        """
        if not self.config.led.enabled or self.config.led.sink != "respeaker":
            return False
        if self.config.led.simulation_offer_after_s <= 0:
            return False
        return importlib.util.find_spec("lefx.device.simulated_respeaker") is not None

    def _review_led_availability(self) -> None:
        if not self._simulation_offer_possible():
            self.tray.offer_led_simulation(False)
            return
        waited = self.led_feedback.unavailable_seconds
        self.tray.offer_led_simulation(
            waited >= self.config.led.simulation_offer_after_s
        )

    def switch_led_sink(self, sink: str = "simulator") -> bool:
        """Move the LED output to another sink without restarting anything else.

        The controller is rebuilt rather than retargeted: a sink is chosen when
        the service is constructed, and swapping one underneath a running render
        loop would be a second way to do it for no gain. The old one is released
        first, because two owners of one USB device is exactly the situation
        this is trying to escape.
        """
        candidate = replace(self.config, led=replace(self.config.led, sink=sink))
        old_led_config = self.config.led
        self._replace_led_feedback(candidate, old_led_config)
        if self.led_feedback.config.sink != sink:
            self.tray.notify(
                "Umschalten fehlgeschlagen",
                f"Die LED-Ausgabe läuft weiter auf {old_led_config.sink}.",
            )
            return False
        self.config = candidate
        self.tray.offer_led_simulation(
            False, "Auf LED-Simulation umschalten"
        )
        self.tray.notify(
            "LED-Simulation aktiv",
            "Das Ringfenster zeigt jetzt die Ausgabe. Mit lefx-simulator öffnen.",
        )
        return True

    @Slot(int, str, bool)
    def _on_text_received(
        self,
        segment_id: int,
        text: str,
        is_final: bool,
    ) -> None:
        del segment_id
        if not is_final and not self.config.overlay.show_realtime_text:
            return
        self.overlay.show_transcript(text, is_final)

    def _on_command_completed(self, name: str, result: object) -> None:
        if name == "apply_runtime_config":
            self._complete_settings_apply(result)
            return
        if name in {"delete_history_entry", "clear_history"}:
            self.bridge.request_history(500)
        if isinstance(result, ReinsertionResult):
            if result.status == ReinsertionStatus.QUEUED:
                self.overlay.show_feedback(
                    FeedbackPresentation(
                        IndicatorColor.GREEN,
                        "Transkript wird erneut eingefügt",
                        800,
                    )
                )
            elif result.status == ReinsertionStatus.EMPTY_HISTORY:
                self.overlay.show_feedback(
                    FeedbackPresentation(
                        IndicatorColor.YELLOW,
                        "Noch kein Transkript zum Einfügen vorhanden",
                        1200,
                    )
                )
            else:
                self.overlay.show_feedback(
                    FeedbackPresentation(
                        IndicatorColor.RED,
                        result.error_message or "Erneutes Einfügen fehlgeschlagen",
                        1400,
                    )
                )
        elif (
            isinstance(result, CommandResult)
            and not result.success
            and result.status == "core_unavailable"
        ):
            self.overlay.show_feedback(
                FeedbackPresentation(
                    IndicatorColor.RED,
                    "Core ist noch nicht verfügbar",
                    1000,
                )
            )

    def show_settings(self) -> None:
        if self.settings_dialog is None:
            dialog = SettingsDialog(self.config, self._apply_settings)
            dialog.history_refresh_requested.connect(
                lambda: self.bridge.request_history(500)
            )
            dialog.history_reinsert_requested.connect(self.bridge.reinsert_entry)
            dialog.history_delete_requested.connect(
                self.bridge.delete_history_entry
            )
            dialog.history_clear_requested.connect(self.bridge.clear_history)
            dialog.reconnect_device_requested.connect(self.reconnect_device)
            dialog.reconnect_server_requested.connect(self.reconnect_server)
            self.settings_dialog = dialog
        self.bridge.request_history(500)
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def _on_history_received(self, entries: object) -> None:
        self.tray.set_history_entries(entries)
        if self.settings_dialog is not None:
            self.settings_dialog.set_history_entries(entries)

    def _apply_settings(
        self,
        candidate: AppConfig,
        policies: frozenset[ApplyPolicy],
    ) -> bool:
        if self._pending_config is not None:
            return False
        old_config = self.config
        old_hotkeys = self.hotkeys
        new_hotkeys = old_hotkeys
        if ApplyPolicy.HOTKEY_REREGISTER in policies:
            old_hotkeys.unregister()
            try:
                new_hotkeys = self._create_hotkey_manager(candidate)
                if not new_hotkeys.register():
                    raise RuntimeError("global hotkey registration failed")
            except Exception:
                logger.exception("New hotkey set rejected; restoring old bindings.")
                old_hotkeys.register()
                return False
        try:
            candidate.save_user()
        except Exception:
            logger.exception("Could not persist candidate user configuration.")
            if new_hotkeys is not old_hotkeys:
                new_hotkeys.unregister()
                old_hotkeys.register()
            return False

        self._pending_config = candidate
        self._pending_old_config = old_config
        self._pending_old_hotkeys = old_hotkeys
        if new_hotkeys is not old_hotkeys:
            self.hotkeys = new_hotkeys
        if not self.bridge.apply_runtime_config(candidate):
            self._rollback_pending_settings("Core akzeptiert keine Befehle")
            return False
        return True

    def _complete_settings_apply(self, result: object) -> None:
        candidate = self._pending_config
        if candidate is None:
            return
        if isinstance(result, CommandResult) and result.success:
            old_led_config = self.config.led
            old_mappings = self.config.feedback_mappings
            self.config = candidate
            self.overlay.apply_config(candidate.overlay)
            self.sound_feedback.apply_config(candidate.feedback)
            if (
                candidate.led != old_led_config
                or candidate.feedback_mappings != old_mappings
            ):
                self._replace_led_feedback(candidate, old_led_config)
            self._pending_config = None
            self._pending_old_config = None
            self._pending_old_hotkeys = None
            if self.settings_dialog is not None:
                self.settings_dialog.complete_apply(True, candidate, "")
            return
        message = (
            result.message
            if isinstance(result, CommandResult) and result.message
            else "Unbekannter Laufzeitfehler"
        )
        self._rollback_pending_settings(message)
        if self.settings_dialog is not None:
            self.settings_dialog.complete_apply(False, None, message)

    def _replace_led_feedback(self, candidate: AppConfig, old_led_config) -> None:
        """Swap the LED output for the new settings, or keep what already works.

        Only a configuration that survives the catalogue check may replace one
        that already survived it. A candidate naming an effect nobody has is
        discarded and the previous output is rebuilt from the previous settings,
        so the ring goes on working on the last known good ones rather than
        going dark because of a typo.
        """
        if not self.led_feedback.shutdown():
            logger.error(
                "LED output did not stop in time; it keeps running on the "
                "previous settings."
            )
            return
        try:
            replacement = LedFeedback(
                candidate.led,
                on_failure=self._on_led_failure,
                on_device_mute_changed=self.device_mute_changed.emit,
            )
            replacement.verify_targets(candidate.feedback_mappings.led_targets())
        except Exception:
            logger.exception(
                "New LED configuration rejected; restoring the previous one."
            )
            try:
                self.led_feedback = LedFeedback(
                    old_led_config,
                    on_failure=self._on_led_failure,
                    on_device_mute_changed=self.device_mute_changed.emit,
                )
                self.led_feedback.watch_device_mute()
            except Exception:
                logger.exception("The previous LED configuration is gone too.")
            return
        self.led_feedback = replacement
        self.led_feedback.watch_device_mute()

    def _rollback_pending_settings(self, message: str) -> None:
        del message
        old_config = self._pending_old_config
        old_hotkeys = self._pending_old_hotkeys
        if self.hotkeys is not old_hotkeys and old_hotkeys is not None:
            self.hotkeys.unregister()
            old_hotkeys.register()
            self.hotkeys = old_hotkeys
        if old_config is not None:
            try:
                old_config.save_user()
            except Exception:
                logger.exception("Failed to restore previous user config file.")
        self._pending_config = None
        self._pending_old_config = None
        self._pending_old_hotkeys = None

    def _on_fatal_error(self, message: str) -> None:
        logger.error("UI received fatal Core error: %s", message)
        self.tray.status_action.setText("Core-Fehler")
        self.tray.tray.setIcon(create_status_icon(IndicatorColor.RED))
        self.tray.tray.setToolTip(f"RealtimeSTT – Core-Fehler\n{message}")
        self.overlay.show_feedback(
            FeedbackPresentation(
                IndicatorColor.RED,
                "RealtimeSTT-Core wurde unerwartet beendet",
                1800,
            )
        )

    def shutdown(self) -> None:
        if self._shutting_down:
            return
        self._shutting_down = True
        self._report_lifecycle_stopping()
        if self._pending_config is not None:
            self._rollback_pending_settings("Anwendung wird beendet")
        self.hotkeys.unregister()
        self.tray.hide()
        self.overlay.hide()
        if self.settings_dialog is not None:
            self.settings_dialog.close()
        if not self.led_feedback.shutdown():
            logger.warning("LED worker did not stop within its configured timeout.")
        self.bridge.stop(timeout=10.0)
        self.instance_guard.release()
        self._started = False


def run_gui(
    config: AppConfig,
    argv: Optional[Sequence[str]] = None,
    *,
    instance_guard: Optional[SingleInstanceGuard] = None,
) -> int:
    """Run the regular tray application and return a process exit code."""
    guard = instance_guard or SingleInstanceGuard()
    acquire_result = guard.acquire()
    if acquire_result.status == InstanceAcquireStatus.ALREADY_RUNNING:
        logger.info("RealtimeSTT is already running; second instance exits.")
        return EXIT_ALREADY_RUNNING
    if acquire_result.status == InstanceAcquireStatus.ERROR:
        logger.error(
            "Single-instance guard could not be acquired: %s",
            acquire_result.error,
        )
        return EXIT_INSTANCE_ERROR

    try:
        application = QApplication.instance()
        owns_application = application is None
        if application is None:
            application = QApplication(
                list(argv) if argv is not None else sys.argv
            )
        if not isinstance(application, QApplication):
            raise RuntimeError("Existing Qt application is not a QApplication")
        application.setApplicationName("RealtimeSTT Client")
        application.setOrganizationName("MarcoSudau")
        application.setQuitOnLastWindowClosed(False)
        application.setWindowIcon(create_status_icon(IndicatorColor.GREEN))

        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.error("No system tray is available.")
            guard.release()
            return EXIT_TRAY_UNAVAILABLE

        desktop = DesktopApplication(application, config, guard)
    except LedConfigurationError as error:
        # Not a UI failure and not a hardware one: the configuration file asks
        # for something that cannot be carried out. Said plainly and once,
        # because the next start will fail in exactly the same way until the
        # file is fixed.
        logger.error("LED configuration is not usable:\n%s", error)
        guard.release()
        return EXIT_CONFIGURATION_INVALID
    except Exception:
        logger.exception("Qt UI initialization failed.")
        guard.release()
        return EXIT_UI_INITIALIZATION_FAILED
    if not desktop.start():
        desktop.shutdown()
        return EXIT_CORE_START_FAILED

    previous_sigint = None
    if threading.current_thread() is threading.main_thread():
        previous_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, lambda sig, frame: application.quit())
    try:
        return application.exec() if owns_application else EXIT_OK
    finally:
        desktop.shutdown()
        if previous_sigint is not None:
            signal.signal(signal.SIGINT, previous_sigint)
