"""V2 desktop bindings using the retained tray, overlay and worker shell."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import uuid
import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from voice_stt_client.core.controller import CommandResult
from voice_stt_client.core.event_models import CanonicalEventType
from voice_stt_client.core.settings_service import SettingsError
from voice_stt_client.core.v2_controls import ControlConfig
from voice_stt_client.core.v2_runtime import runtime_profile, v2_endpoint
from .application import DesktopApplication
from .feedback import V2FeedbackOutput
from .hotkeys import V2HotkeyManager, fallback_hotkeys
from .settings_dialog import SettingsDialog
from .v2_core_bridge import V2CoreBridge
from .v2_settings_dialog import V2SettingsDialog


class V2DesktopApplication(DesktopApplication):
    def __init__(self, application, config, instance_guard, *, bridge=None, **kwargs):
        self._profile_transaction = None
        self._local_dialog = None
        self._settings_port = None
        self._runtime_generation = -1
        self._runtime_ready = False
        config = deepcopy(config)
        if bridge is None:
            ingress = kwargs.get('observability')
            bridge = V2CoreBridge(config, **({'observability': ingress} if ingress is not None else {}))
        super().__init__(application, config, instance_guard,
            bridge=bridge, **kwargs)

    def _create_hotkey_manager(self, config):
        return V2HotkeyManager(ControlConfig(**runtime_profile(config).controls),
            on_control=self.bridge.press_control, on_reinsert_last=self.bridge.reinsert_last,
            on_overlay_toggle=self.overlay.toggle_visibility, backend=self._hotkey_backend,
            application=self.application, observability=self._observability)

    def _wire_signals(self):
        self.output = V2FeedbackOutput(tray=self.tray, overlay=self.overlay,
            sound=self.sound_feedback, led=self.led_feedback, parent=self)
        queued = Qt.ConnectionType.QueuedConnection
        self.bridge.feedback_decision_received.connect(self.output.apply, queued)
        self.bridge.snapshot_changed.connect(self._runtime_view, queued)
        self.bridge.ui_transaction.connect(self._profile_transaction_step, queued)
        self.bridge.audio_devices_received.connect(self._audio_devices, queued)
        self.bridge.command_completed.connect(self._on_command_completed, queued)
        self.bridge.history_received.connect(self._on_history_received, queued)
        self.bridge.fatal_error.connect(self._on_fatal_error, queued)
        self.sound_feedback.failure.connect(self._on_sound_failure)
        self.output.failure.connect(self._output_failure)
        self.device_mute_changed.connect(self._on_device_mute_changed, queued)

    def _output_failure(self, category):
        event = {'sound_failed': CanonicalEventType.CLIENT_SOUND_FAILED,
                 'led_unavailable': CanonicalEventType.CLIENT_LED_UNAVAILABLE}.get(category)
        if event is not None:
            self.bridge.report_local_feedback(event)
        else:
            logging.getLogger('ui').warning('V2 output unavailable: %s', category)

    def _runtime_view(self, view):
        if view.generation < self._runtime_generation or self._shutting_down:
            return
        self._runtime_generation, self._runtime_ready = view.generation, view.ready
        if not view.ready:
            message = {'connecting': 'Verbindung wird aufgebaut', 'accepting': 'Session wird angenommen',
                'configuring': 'Einstellungen werden bestätigt', 'blocked': 'Konfiguration prüfen',
                'backoff': 'Verbindung unterbrochen', 'closed': 'Nicht verbunden',
                'stopping': 'Wird beendet'}.get(view.transport, 'Zustand wird synchronisiert')
            self.tray.status_action.setText(message)
            self.tray.toggle_action.setEnabled(False)
            if view.reason:
                self.tray.tray.setToolTip('RealtimeSTT – ' + message + '\n' + view.reason)

    def _register_startup_hotkeys(self):
        # Preserve configured V2 slots even in wake-only mode. Fallback is
        # provisional until core startup succeeds, as in the retained shell.
        if self.hotkeys.register():
            return True
        profile = runtime_profile(self.config)
        keys = ('primary_key', 'secondary_key', 'wake_pause_key', 'reinsert_last_key', 'overlay_toggle_key')
        for role in keys:
            if not profile.controls.get(role):
                continue
            trial = deepcopy(profile)
            for key in fallback_hotkeys():
                trial.controls[role] = key
                try:
                    controls = ControlConfig(**trial.controls)
                except ValueError:
                    continue
                if self.hotkeys.apply(controls):
                    self.config.v2_profile = asdict(trial)
                    self.config._v2_migration_source = {'v2_profile': asdict(trial)}
                    self.bridge.config = deepcopy(self.config)
                    # Bootstrap persists this provisional binding on a worker,
                    # only after the actual core and metadata have started.
                    self.config._needs_profile_persist = True
                    self.bridge.config = deepcopy(self.config)
                    return True
        return False

    def start(self):
        old = deepcopy(self.config)
        ok = super().start()
        if not ok:
            self.config = old
            self.bridge.config = deepcopy(old)
            self.hotkeys.unregister()
            self.hotkeys = self._create_hotkey_manager(old)
        return ok

    def _profile_transaction_step(self, operation, payload, reply):
        if reply.done():
            return
        try:
            if self._shutting_down and operation == 'profile_prepare':
                raise SettingsError('core_unavailable')
            if operation == 'profile_prepare':
                if self._profile_transaction is not None or self._pending_config is not None:
                    raise SettingsError('settings_busy')
                old = deepcopy(self.config)
                old_controls = self.hotkeys.config
                controls = ControlConfig(**payload.controls)
                if not self.hotkeys.apply(controls):
                    raise SettingsError('hotkey_registration_failed')
                token = uuid.uuid4().hex
                candidate = deepcopy(old)
                candidate.v2_profile = asdict(payload)
                candidate._v2_migration_source = {'v2_profile': asdict(payload)}
                candidate.server.url = v2_endpoint(old.server.url)
                self._profile_transaction = (token, old_controls, old)
                reply.set_result((token, candidate, old))
            elif operation == 'profile_commit':
                token, candidate = payload
                if self._profile_transaction is None or self._profile_transaction[0] != token:
                    raise SettingsError('profile_transaction_changed')
                self.config = deepcopy(candidate)
                self._profile_transaction = None
                if self._local_dialog and not self._shutting_down:
                    self._local_dialog.complete_apply(True, self.config, '')
                reply.set_result(True)
            elif operation == 'profile_rollback':
                if self._profile_transaction is not None and self._profile_transaction[0] == payload:
                    _, controls, old = self._profile_transaction
                    if not self.hotkeys.apply(controls):
                        self.last_apply_error = 'Die bisherigen Hotkeys konnten nicht wiederhergestellt werden.'
                    self.config = old
                    self._profile_transaction = None
                reply.set_result(True)
            else:
                raise SettingsError('invalid_ui_transaction')
        except Exception as error:
            reply.set_exception(error)

    def show_settings(self):
        if self.settings_dialog is None:
            port = self.bridge.settings_bridge(self)
            if port is None:
                return
            local = SettingsDialog(self.config, self._apply_settings, v2_local=True, audio_devices=(),
                observability=self._observability, apply_error=lambda: self.last_apply_error)
            local.history_refresh_requested.connect(lambda: self.bridge.request_history(500))
            local.history_reinsert_requested.connect(self.bridge.reinsert_entry)
            local.history_delete_requested.connect(self.bridge.delete_history_entry)
            local.history_clear_requested.connect(self.bridge.clear_history)
            local.reconnect_device_requested.connect(self.reconnect_device)
            local.logging_view_requested.connect(self.show_logs)
            local.logging_clear_requested.connect(self.clear_diagnostics_history)
            self._local_dialog, self._settings_port = local, port
            self.settings_dialog = V2SettingsDialog(port, local_dialog=local)
        self.bridge.request_audio_devices()
        self.bridge.request_history(500)
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def _audio_devices(self, devices):
        if self._shutting_down or self._local_dialog is None:
            return
        editor = self._local_dialog._editors.get('audio.device')
        if editor is None:
            return
        selected = editor.currentData()
        editor.blockSignals(True)
        editor.clear()
        editor.addItem('Systemstandard', None)
        for device in devices:
            editor.addItem(str(device['name']), int(device['index']))
        if selected is not None and editor.findData(selected) < 0:
            editor.addItem(str(selected), selected)
        editor.setCurrentIndex(max(0, editor.findData(selected)))
        editor.blockSignals(False)

    def _on_history_received(self, entries):
        self.tray.set_history_entries(entries)
        if self._local_dialog:
            self._local_dialog.set_history_entries(entries)

    def _apply_settings(self, candidate, policies):
        if self._pending_config is not None or self._profile_transaction is not None:
            self.last_apply_error = 'Eine Änderung wird noch angewendet.'
            return False
        self.last_apply_error = ''
        correlation_id = f'settings:{uuid.uuid4().hex[:12]}'
        self._settings_apply_correlation = correlation_id
        self._observe.audit('client.settings.apply_started',
            details={'policies': sorted(policy.value for policy in policies)},
            correlation_id=correlation_id)
        self._pending_config = deepcopy(candidate)
        self._pending_old_config = deepcopy(self.config)
        if not self.bridge.apply_runtime_config(candidate, settings_correlation_id=correlation_id):
            self._pending_config = self._pending_old_config = None
            self._complete_settings_observation(False, 'core_unavailable')
            return False
        return True

    def _complete_settings_apply(self, result):
        candidate = self._pending_config
        if candidate is None:
            return
        success = isinstance(result, CommandResult) and result.success
        if success:
            old = self.config
            self.config = deepcopy(candidate)
            self.bridge.config = deepcopy(candidate)
            self.overlay.apply_config(candidate.overlay)
            self.sound_feedback.apply_config(candidate.feedback)
            if candidate.led != old.led or candidate.feedback_mappings != old.feedback_mappings:
                self._replace_led_feedback(candidate, old.led)
                self.output.led = self.led_feedback
        self._pending_config = self._pending_old_config = None
        self._complete_settings_observation(success, str(getattr(result, 'status', 'unknown_error')))
        if self._local_dialog:
            self._local_dialog.complete_apply(success, self.config if success else None,
                '' if success else 'Lokale Einstellungen konnten nicht übernommen werden.')

    def reconnect_server(self):
        self.bridge.reconnect_server()

    def _on_command_completed(self, name, result):
        if isinstance(result, CommandResult) and result.status == 'apply_choice_required':
            self.show_settings()
            if self.settings_dialog:
                self.settings_dialog.status.setText(result.message)
            return
        super()._on_command_completed(name, result)

    def _replace_led_feedback(self, candidate, old_led_config):
        super()._replace_led_feedback(candidate, old_led_config)
        if hasattr(self, 'output'):
            self.output.led = self.led_feedback

    def shutdown(self):
        if self._shutting_down:
            return
        self._shutting_down = True
        self._observe.system('client.app.stopping', details={'started': bool(self._started)})
        self._report_lifecycle_stopping()
        self.output.close()
        if self._settings_port:
            self._settings_port.close()
        if self.settings_dialog:
            self.settings_dialog.close()
        if not self.bridge.stop(timeout=10):
            logging.getLogger('ui').warning('V2 core did not stop within 10 seconds.')
        # Stop accepts commit/rollback replies on Qt; unregister afterwards so
        # a finishing transaction cannot resurrect native keys during teardown.
        self.hotkeys.unregister()
        self.tray.hide()
        self.overlay.hide()
        if self.log_window:
            self.log_window.shutdown()
            self.log_window.hide()
        if not self.led_feedback.shutdown():
            logging.getLogger('ui').warning('LED worker did not stop within its configured timeout.')
        self._complete_settings_observation(False, 'shutdown')
        self._pending_config = self._pending_old_config = None
        self.instance_guard.release()
        self._started = False
