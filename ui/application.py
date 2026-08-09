"""AP06 composition root for the Windows tray application."""

from __future__ import annotations

import logging
import signal
import sys
import threading
from typing import Optional, Sequence

from PySide6.QtCore import QObject, Qt, Slot
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from core.config import AppConfig
from core.controller import CommandResult, TransientEvent
from core.settings_metadata import ApplyPolicy
from core.reinsertion import ReinsertionResult, ReinsertionStatus
from ui.core_bridge import CoreBridge
from ui.hotkeys import GlobalHotkeyManager, HotkeyBackend
from ui.feedback import SoundFeedback
from ui.overlay import TranscriptOverlay
from ui.presentation import (
    FeedbackPresentation,
    IndicatorColor,
    presentation_for_feedback,
)
from ui.single_instance import (
    InstanceAcquireStatus,
    SingleInstanceGuard,
)
from ui.settings_dialog import SettingsDialog
from ui.tray import TrayController, create_status_icon

logger = logging.getLogger("ui.application")

EXIT_OK = 0
EXIT_ALREADY_RUNNING = 2
EXIT_INSTANCE_ERROR = 3
EXIT_TRAY_UNAVAILABLE = 4
EXIT_CORE_START_FAILED = 5
EXIT_UI_INITIALIZATION_FAILED = 6


class DesktopApplication(QObject):
    """Own all Qt-side AP06 components in the QApplication thread."""

    def __init__(
        self,
        application: QApplication,
        config: AppConfig,
        instance_guard: SingleInstanceGuard,
        *,
        bridge: Optional[CoreBridge] = None,
        hotkey_backend: Optional[HotkeyBackend] = None,
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
            parent=self,
        )
        self.hotkeys = self._create_hotkey_manager(config)
        self._started = False
        self._shutting_down = False
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
            enabled=config.hotkey.enabled,
            backend=self._hotkey_backend,
            application=self.application,
        )

    def _wire_signals(self) -> None:
        queued = Qt.ConnectionType.QueuedConnection
        self.bridge.snapshot_changed.connect(
            self.tray.update_snapshot, queued
        )
        self.bridge.feedback_received.connect(self._on_feedback, queued)
        self.bridge.text_received.connect(self._on_text_received, queued)
        self.bridge.command_completed.connect(
            self._on_command_completed, queued
        )
        self.bridge.history_received.connect(self._on_history_received, queued)
        self.bridge.fatal_error.connect(self._on_fatal_error, queued)

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
        return True

    def _on_feedback(self, event: TransientEvent) -> None:
        self.overlay.show_feedback(presentation_for_feedback(event))

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

        if isinstance(result, CommandResult) and result.success:
            if name in {"primary_dictation_action", "start_dictation"}:
                self.sound_feedback.play("start")
            elif name in {"stop_dictation"}:
                self.sound_feedback.play("stop")
            elif name == "cancel_dictation":
                self.sound_feedback.play("cancel")

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
            self.config = candidate
            self.overlay.apply_config(candidate.overlay)
            self.sound_feedback.apply_config(candidate.feedback)
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
        if self._pending_config is not None:
            self._rollback_pending_settings("Anwendung wird beendet")
        self.hotkeys.unregister()
        self.tray.hide()
        self.overlay.hide()
        if self.settings_dialog is not None:
            self.settings_dialog.close()
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
