"""Desktop composition: one V2 session, mirror and set of side-effect owners.

Mutable services live on the existing asyncio core loop. No Qt dependency.
Only the device, HTTP/socket and Windows injection boundaries are injectable.
"""
from __future__ import annotations

import asyncio
from copy import deepcopy
from dataclasses import asdict, dataclass, replace
import inspect
import logging
import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from .config import AppConfig
from .controller import CommandResult
from .audio_capture import AudioCapture
from .feedback_reducer import FeedbackEngine
from .final_results import V2ResultService
from .history import TranscriptHistoryManager
from .observability.adapters.client_events import ClientEventEmitter
from .observability.adapters.server_live import ServerLiveAdapter
from .observability.ingress import NULL_INGRESS
from .reinsertion import TranscriptReinsertionService
from .session_coordinator import DualSessionCoordinator
from .settings_service import SettingsService, SettingsHTTP, SettingsError
from .settings_ui_service import SettingsUISession
from .text_injector import TextInjectionQueue, CtypesWindowsInjectionBackend
from .v2_controls import ControlConfig, ControlSlot
from .v2_feedback import V2FeedbackConnection
from .v2_media import V2MediaConnection
from .v2_mirror import V2MirrorConnection
from .v2_profile import migrate_profile
from .v2_transport import V2STTSession, V2TransportConfig, V2TransportState
from .version import __version__

logger = logging.getLogger('controller')


def backup_v1_profile(path):
    """Preserve the actual override bytes without a provisional config write."""
    path = Path(path)
    backup = path.with_name(path.name + '.pre-v2.bak')
    if path.exists() and not backup.exists():
        with backup.open('xb') as handle:
            handle.write(path.read_bytes())
            handle.flush()
            os.fsync(handle.fileno())


def v2_endpoint(url):
    """Migrate the known V1 route; retain origin, reject arbitrary routes.

    V1 query parameters describe legacy session wishes and have no V2 effect.
    New trigger/settings wishes come exclusively from the versioned profile.
    """
    parts = urlsplit(url)
    if parts.path == '/ws/transcribe':
        return urlunsplit(parts._replace(path='/ws/v2', query=''))
    return url


def runtime_profile(config):
    raw = getattr(config, '_v2_migration_source', None)
    return migrate_profile(raw if raw is not None else asdict(config))


@dataclass(frozen=True)
class RuntimeView:
    generation: int
    session_id: str | None
    transport: str
    reason: str
    ready: bool
    closing: bool
    mirror: object
    controls: ControlConfig


class V2Runtime:
    def __init__(self, config: AppConfig, *, connector=None, http=None, audio=None,
                 backend=None, history_manager=None, observability=NULL_INGRESS,
                 persist_profile=None, transport_config=None):
        self.config = deepcopy(config)
        self.observability = observability
        self._observe = ClientEventEmitter(observability, component='controller')
        self.on_snapshot_change = self.on_feedback_event = self.on_feedback_decision = None
        self.on_text = self.on_transport_change = None
        self.persist_profile = persist_profile
        self._loop = None
        self._stop = asyncio.Event()
        self._shutdown_task = None
        self._runner = None
        self._commands = set()
        self._transactions = set()
        self._closing = False
        self.is_running = False
        self._initial_auto_start = False
        self._auto_start_task = None
        self._issues = set()
        self._apply_lock = asyncio.Lock()
        self.cleanup_errors = []
        profile = runtime_profile(config)
        tc = transport_config or V2TransportConfig(url=v2_endpoint(config.server.url),
            client_version=__version__, backoff_initial=config.server.reconnect_min_delay,
            backoff_max=config.server.reconnect_max_delay,
            capacity_min=max(10, config.server.server_busy_min_delay))
        self.session = V2STTSession(tc, observability=observability,
            **({'connector': connector} if connector else {}))
        self.mirror = V2MirrorConnection(self.session)
        self.settings = SettingsService(self.session, profile, http=http)
        self.audio = audio or AudioCapture(config.audio, observability=observability)
        self.logs = DualSessionCoordinator(replace(config.server, url=tc.url),
            config.event_stream, observability=observability)
        self.logs.on_observation = ServerLiveAdapter(observability)
        self.media = V2MediaConnection(self.session, self.audio, logs=self.logs,
            settings_bootstrap=self._bootstrap)
        from .v2_controls import V2ControlService
        self.controls = V2ControlService(self.session, self.mirror,
            config=ControlConfig(**profile.controls), audio_ready=lambda: self.media.audio_available)
        self.history = history_manager or TranscriptHistoryManager(config.history)
        self.queue = TextInjectionQueue(config, self.history,
            backend if backend is not None else CtypesWindowsInjectionBackend(),
            observability=observability)
        self.reinsertion = TranscriptReinsertionService(self.history, self.queue)
        self.results = V2ResultService(self.history, self.queue, self.mirror)
        self.results.on_result = self._result
        self.results.on_attempt_result = self._attempt
        # Result consumer is attached first. Every emitted final is reserved
        # before the corresponding feedback decision reaches Qt.
        self.mirror.on_reduction = self._chain(self.mirror.on_reduction, self._reduction)
        self.feedback = FeedbackEngine(config.feedback_mappings)
        self.feedback_port = V2FeedbackConnection(self.mirror, self.feedback,
            observability=observability)
        self.feedback_port.on_decision = self._decision
        self.logs.on_context_change = self._log_context
        self.logs.on_event = self._log_event
        self.session.on_status = self._chain(self.session.on_status, self._status)
        observability.register_aggregate_source('client.audio.stream_stats',
            self._audio_stats, component='audio')

    @staticmethod
    def _chain(previous, callback):
        def receive(value):
            if previous:
                previous(value)
            callback(value)
        return receive

    @property
    def is_closing(self):
        return self._closing

    @property
    def is_ready(self):
        b, v = self.session.binding, self.mirror.mirror.view
        return bool(not self._closing and self.session.is_ready and b and v.operations_ready
                    and not v.snapshot_pending and (v.generation, v.session_id) == (b.generation, b.session_id))

    def get_snapshot(self):
        b = self.session.binding
        return RuntimeView(self.session.generation, b.session_id if b else None,
            self.session.status.state.value, self.session.status.reason,
            self.is_ready, self._closing, self.mirror.mirror.view, self.controls.config)

    def _publish(self):
        if self.on_snapshot_change:
            self.on_snapshot_change(self.get_snapshot())

    def _reduction(self, reduction):
        self._publish()
        if self._initial_auto_start and self.is_ready and self.media.audio_available:
            self._initial_auto_start = False
            self._auto_start_task = asyncio.create_task(self.primary_dictation_action())

    def _status(self, status):
        self._publish()
        if self.feedback._v2_view is not None:
            self._decision(self.feedback.update_v2_issues(tuple(sorted(self._issues))))
        if self.on_transport_change:
            self.on_transport_change(status)

    def _decision(self, decision):
        if decision and decision.snapshot and not self.is_ready and decision.snapshot.availability == 'ready':
            decision = replace(decision, snapshot=replace(decision.snapshot,
                availability=self.session.status.state.value, manual_available=False))
        if self.on_feedback_decision:
            self.on_feedback_decision(decision)

    def _log_context(self, context):
        self._decision(self.feedback.update_connection(context.event_state,
            stt_ready=self.session.is_ready, generation=context.generation, session_id=context.session_id))

    async def _log_event(self, context, result):
        # Validated diagnostics only. No log/fallback result or state authority.
        self.feedback.handle_event_stream(result, generation=context.generation, session_id=context.session_id)
        return True

    def _audio_stats(self):
        return dict(self.audio.capture_counters(), **self.media.counters())

    def _issue(self, category, enabled=True):
        self._issues.add(category) if enabled else self._issues.discard(category)
        decision = self.feedback.update_v2_issues(tuple(sorted(self._issues)))
        if decision:
            self._decision(decision)

    def _result(self, outcome):
        if outcome.status in ('history_unavailable', 'failed'):
            self._issue('history_unavailable')
        elif outcome.status == 'queue_unavailable':
            self._issue('injection_failed')

    def _attempt(self, attempt):
        # Queue callbacks run on its Windows worker; marshal back before mutation.
        if self._loop is not None and not self._loop.is_closed() and not self._closing:
            self._loop.call_soon_threadsafe(self._issue, 'injection_failed', attempt.status != 'command_sent')

    async def _bootstrap(self, session, binding):
        await self.settings.bootstrap(session, binding)
        # Metadata has resolved aliases. Persist migration before READY/PCM,
        # preserving original raw bytes via the established backup transaction.
        if self.config.v2_profile is None or getattr(self.config, '_needs_profile_persist', False):
            async def migrate():
                path = getattr(self.config, '_v2_migration_path', getattr(self.config, '_config_source_path', None))
                if path is not None:
                    await asyncio.to_thread(backup_v1_profile, path)
                candidate = deepcopy(self.config)
                candidate.v2_profile = asdict(self.settings.profile)
                candidate.server.url = session.config.url
                if self.persist_profile is not None:
                    await self._persist(self.settings.profile)
                else:
                    await asyncio.to_thread(candidate.save_user)
                    self.config = candidate
                self.controls.config = ControlConfig(**self.settings.profile.controls)
                self.config._needs_profile_persist = False
            await self._transaction(migrate)

    async def _persist(self, profile):
        if self.persist_profile is None:
            raise SettingsError('profile_persistence_required')
        async def commit():
            value = self.persist_profile(deepcopy(profile))
            if inspect.isawaitable(value):
                await value
            self.config.v2_profile = asdict(profile)
        await self._transaction(commit)

    async def _transaction(self, operation):
        if self._closing:
            raise SettingsError('core_unavailable')
        task = asyncio.create_task(operation())
        self._transactions.add(task)
        try:
            try:
                return await asyncio.shield(task)
            except asyncio.CancelledError:
                await task
                raise
        finally:
            self._transactions.discard(task)

    def settings_ui_session(self):
        if self._closing:
            raise SettingsError('core_unavailable')
        return SettingsUISession(self.settings, self.controls, self.mirror,
            persist_profile=self._persist)

    def request_initial_auto_start(self):
        self._initial_auto_start = True

    async def run(self):
        self._loop = asyncio.get_running_loop()
        self.is_running = True
        try:
            await asyncio.to_thread(self.queue.start)
            self._runner = asyncio.create_task(self.session.run(), name='v2-runtime-transport')
            # BLOCKED keeps the desktop/settings alive for an explicit repair.
            stopped = asyncio.create_task(self._stop.wait())
            try:
                done, _ = await asyncio.wait((stopped, self._runner), return_when=asyncio.FIRST_COMPLETED)
                if self._runner in done and not self._stop.is_set():
                    await self._runner
            finally:
                stopped.cancel()
                await asyncio.gather(stopped, return_exceptions=True)
            await self._stop.wait()
        finally:
            await self.shutdown()

    async def _control(self, operation):
        if not self.is_ready:
            return CommandResult(False, 'not_ready')
        task = asyncio.current_task()
        self._commands.add(task)
        try:
            result = await operation()
            return CommandResult(bool(result and result.ack.accepted),
                str(result.ack.result) if result else 'action_blocked')
        finally:
            self._commands.discard(task)

    async def press_control(self, slot):
        return await self._control(lambda: self.controls.press(slot))

    async def primary_dictation_action(self):
        return await self.press_control(ControlSlot.PRIMARY)

    toggle_dictation = primary_dictation_action
    start_dictation = primary_dictation_action

    async def stop_dictation(self):
        return await self._control(lambda: self.controls.control('finish'))

    async def cancel_dictation(self):
        return await self._control(lambda: self.controls.control('cancel'))

    def set_microphone_muted(self, muted):
        return self.media.set_hardware_muted(muted)

    def report_local_feedback(self, event_type, details=None):
        name = getattr(event_type, 'value', event_type)
        category = {'client.sound.failed': 'sound_failed', 'client.led.unavailable': 'led_unavailable'}.get(name)
        if category:
            self._issue(category)
        else:
            self._observe.system(name, details=details or {})

    def reinsert_last(self):
        return self.reinsertion.reinsert_last()

    def reinsert_entry(self, entry_id):
        return self.reinsertion.reinsert_entry(entry_id)

    def get_recent_entries(self, limit=10):
        return tuple(self.reinsertion.get_recent_entries(limit))

    def delete_history_entry(self, entry_id):
        return self.history.delete_entry(entry_id)

    def clear_history(self):
        return self.history.clear_entries()

    async def reconnect_server(self):
        if self._closing:
            return CommandResult(False, 'core_unavailable')
        v = self.mirror.mirror.view
        if v.input.activation_id or any(a.status == 'draining' for a in v.activations.values()):
            return CommandResult(False, 'apply_choice_required', 'Eingabe oder Ergebnisse offen; V2-Einstellungen verwenden.')
        if self.session.binding:
            await self.session.reconnect(self.session.binding, 'user_reconnect')
        elif self._runner is None or self._runner.done():
            self._runner = asyncio.create_task(self.session.run(), name='v2-runtime-transport')
        return CommandResult(True, 'reconnecting')

    def _apply_observability(self, config):
        try:
            apply = getattr(self.observability, 'apply_config', None)
            if apply is not None:
                apply(config)
        except Exception:
            logger.warning('Observability preferences could not be applied')

    async def apply_runtime_config(self, candidate, *, correlation_id=None):
        """Local preferences only; triggers/settings go through SettingsUISession."""
        if self._closing:
            return CommandResult(False, 'core_unavailable')
        return await self._transaction(lambda: self._apply_runtime_config(deepcopy(candidate), correlation_id))

    async def _apply_runtime_config(self, candidate, correlation_id):
        async with self._apply_lock:
            old = self.config
            if candidate.server != old.server or candidate.v2_profile != old.v2_profile:
                return CommandResult(False, 'v2_settings_required')
            saved = False
            previous_device = self.media.device_available
            audio_changed = candidate.audio != old.audio
            result = CommandResult(False, 'local_apply_failed', 'Lokale Einstellungen konnten nicht übernommen werden.')
            try:
                candidate.validate()
                if audio_changed:
                    self.media.set_device_available(False)
                    if self.session.is_ready:
                        await self.media._report_availability(self.session.binding, False)
                    def reconfigure_audio():
                        self.audio.stop()
                        self.audio._config = deepcopy(candidate.audio)
                        self.audio.bound_queue(500)
                        self.audio.probe()
                    await self.media._capture_call(reconfigure_audio)
                await asyncio.to_thread(candidate.save_user)
                saved = True
                self.config = deepcopy(candidate)
                self.history.config = deepcopy(candidate.history)
                self.queue.config = deepcopy(candidate)
                self.feedback.reconfigure_mapping(candidate.feedback_mappings)
                await self.logs.update_config(replace(candidate.server, url=self.session.config.url), candidate.event_stream)
                self._apply_observability(candidate.logging.observability)
                result = CommandResult(True, 'applied')
                return result
            except Exception:
                if saved:
                    await asyncio.to_thread(old.save_user)
                self.audio._config = deepcopy(old.audio)
                self.config = old
                self.history.config = deepcopy(old.history)
                self.queue.config = deepcopy(old)
                self.feedback.reconfigure_mapping(old.feedback_mappings)
                await self.logs.update_config(replace(old.server, url=self.session.config.url), old.event_stream)
                self._apply_observability(old.logging.observability)
                return result
            finally:
                self.media.set_device_available(previous_device)
                binding = self.session.binding
                # This port admits only local preferences: session/trigger
                # changes require SettingsUISession. Observe the completed
                # transaction, including a failed apply after its rollback.
                self._observe.audit('client.settings.runtime_apply',
                    details=dict(session_changed=False, audio_changed=audio_changed,
                        mode_changed=False, success=result.success, status=result.status),
                    session_id=binding.session_id if binding else None,
                    generation=self.session.generation, correlation_id=correlation_id)

    async def shutdown(self):
        if self._shutdown_task is None:
            self._closing = True
            self._stop.set()
            self._shutdown_task = asyncio.create_task(self._cleanup(), name='v2-runtime-shutdown')
        await asyncio.shield(self._shutdown_task)

    async def _cleanup(self):
        self.feedback_port.close()
        self.results.close()
        # Disk commits and Qt registration rollback are indivisible. The bridge
        # pumps Qt replies until these transactions finish before unregistering.
        if self._transactions:
            await asyncio.gather(*tuple(self._transactions), return_exceptions=True)
        commands = [task for task in self._commands if task is not asyncio.current_task()]
        for task in tuple(self._commands):
            if task is not asyncio.current_task():
                task.cancel()
        if self._auto_start_task:
            self._auto_start_task.cancel()
            commands.append(self._auto_start_task)
        if commands:
            await asyncio.gather(*commands, return_exceptions=True)
        # Each component owns its cleanup; one failure must not skip the rest.
        for name, operation in (('controls', self.controls.close), ('settings', self.settings.close),
                                ('media', self.media.close), ('mirror', self.mirror.close)):
            try:
                await asyncio.wait_for(operation(), 7)
            except Exception:
                self.cleanup_errors.append(name)
                logger.error('V2 cleanup failed: %s', name)
        if self._runner:
            self._runner.cancel()
            await asyncio.gather(self._runner, return_exceptions=True)
        await asyncio.to_thread(self.queue.stop, timeout=2)
        self.observability.register_aggregate_source('client.audio.stream_stats', None)
        self.is_running = False
        self._publish()
