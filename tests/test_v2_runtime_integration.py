"""AP100 composed production core; only wire/HTTP/device/Win32 are fake."""
import asyncio
from copy import deepcopy
from dataclasses import asdict, replace
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import numpy as np

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.config import AppConfig, LedConfig
from voice_stt_client.core.feedback_mapping import FeedbackMappingConfig
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.core.v2_runtime import V2Runtime, runtime_profile, v2_endpoint
from voice_stt_client.core.v2_transport import V2TransportConfig
from tests.test_v2_settings_service import SettingsSocket, FakeHTTP, KEY
from tests.test_v2_protocol import FIXTURES
from tests.test_v2_mirror import msg, A, B, S
from tests.test_v2_transport import until, close_error
from tests.test_text_injector import MockInjectionBackend


class Stream:
    """PortAudio boundary; AudioCapture's actual PCM/processing thread runs."""
    def __init__(self, **kwargs):
        self.callback = kwargs['callback']
        self.active = False
    def start(self): self.active = True
    def stop(self): self.active = False
    def close(self): pass
    def emit(self):
        self.callback(np.full((640, 1), 16384, dtype=np.int16), 640, None, None)


def devices(*args, **kwargs):
    device = {'name': 'synthetic PCM', 'default_samplerate': 16000, 'max_input_channels': 1}
    return device if args or kwargs else [device]


class RuntimeSocket(SettingsSocket):
    def __init__(self, *, null_effective=False):
        super().__init__()
        self.null_effective = null_effective
        self.activation_count = 0

    def push(self, value):
        if isinstance(value, dict) and value.get('type') == 'hello.accepted':
            value = deepcopy(value)
            value['logAccess'] = dict(available=False, code='disabled', reason='test boundary')
        super().push(value)

    async def send(self, wire):
        if isinstance(wire, str) and json.loads(wire)['type'] == 'hello':
            hello = json.loads(wire)
            self.state['trigger']['configured'] = hello['requestedSession']['trigger']
            self.state['effectiveSettings']['wakeWord.selection'] = hello['requestedSession']['wakeWordIds']
        await super().send(wire)

    def emit_event(self, kind, *, aid=A, sid=S, segment_sequence=1, **fields):
        seq = self.state['lastEventSeq'] + 1
        self.state.update(lastEventSeq=seq, stateVersion=seq)
        event = msg(kind, seq, aid=aid, sid=sid, segment_sequence=segment_sequence, **fields)
        self.push(event.to_mapping())
        return event

    def start_activation(self, aid=A, source='manual'):
        self.activation_count += 1
        self.state['input'] = dict(phase='waiting_first_speech', activationId=aid,
            primarySource=source, deadlineAtUnixMs=100000, remainingMs=10000, closeRequested=False)
        self.emit_event(p.EventType.ACTIVATION_STARTED, aid=aid, primarySource=source,
            activationSequence=self.activation_count, effectiveSettings=self.state['effectiveSettings'])

    def phase(self, phase, aid=A):
        previous = self.state['input']['phase']
        self.state['input']['phase'] = phase
        self.state['input']['closeRequested'] = phase == 'closing_input'
        self.emit_event(p.EventType.PHASE_CHANGED, aid=aid, previousPhase=previous,
            inputPhase=phase, deadlineAtUnixMs=100000, remainingMs=10000)

    def finish(self, aid=A):
        self.state['input'] = deepcopy(FIXTURES['snapshot']['input'])
        self.state['input'].update(phase='idle', activationId=None, primarySource=None,
            remainingMs=None, deadlineAtUnixMs=None, closeRequested=False)
        self.emit_event(p.EventType.INPUT_CLOSED, aid=aid, acceptedSegmentCount=1)

    async def respond(self, command):
        if command['type'] == p.CommandType.ACTIVATION:
            if self.hook: await self.hook(command)
            if self.drop == command['type']: return
            action = command['action']
            aid = command.get('activationId', A if self.activation_count == 0 else B)
            if action == 'activate': self.start_activation(aid)
            elif action in ('finish', 'cancel'): self.finish(aid)
            self.reply(command, version=self.state['stateVersion'], revision=self.state['settingsRevision'],
                       phase=self.state['input']['phase'])
            return
        await super().respond(command)
        if command['type'] in (p.CommandType.SUPPRESSION, p.CommandType.AUDIO_AVAILABILITY):
            self.state['trigger']['effective'] = {source: bool(not self.null_effective
                and self.state['trigger']['configured'][source]
                and not self.state['trigger']['suppressed'][source]) for source in ('manual', 'wakeWord')}


def config_in(folder, profile=None):
    config = AppConfig()
    config._config_source_path = Path(folder) / 'config.yaml'
    config.v2_profile = asdict(profile or V2Profile())
    config.history.persistent.db_path = str(Path(folder) / 'history.sqlite')
    config.history.persistent.store_all = True
    config.event_stream.enabled = False
    config.led = LedConfig(enabled=False)
    config.feedback_mappings = FeedbackMappingConfig.from_mapping({'schema_version': 2,
        'events': {'server.activation.started': {'led': {'emit_event': 'rainbow'},
            'sound': {'cue': 'start'}}}})
    config.text_injection.paste_delay_ms = 0
    config.text_injection.append_space = False
    config.clipboard.restore_enabled = False
    return config


class Runtime(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        for target, kwargs in (
            ('sounddevice.query_devices', dict(side_effect=devices)),
            ('sounddevice.check_input_settings', {}), ('sounddevice.InputStream', dict(new=Stream))):
            active = patch(target, **kwargs)
            active.start(); self.addCleanup(active.stop)

    async def start(self, *, profile=None, socket=None, http=None, config=None):
        socket = socket or RuntimeSocket()
        http = http or FakeHTTP()
        http.origin = 'https://stt.voice.marcosudau.com'
        async def connector(*args, **kwargs): return socket
        backend = MockInjectionBackend()
        config = config or config_in(self.folder.name, profile)
        runtime = V2Runtime(config, connector=connector, http=http, backend=backend,
            transport_config=V2TransportConfig(ack_timeout=.1, command_retries=0, bootstrap_timeout=.8))
        decisions = []
        runtime.on_feedback_decision = decisions.append
        running = asyncio.create_task(runtime.run())
        async def cleanup():
            await runtime.shutdown()
            await asyncio.gather(running, return_exceptions=True)
        self.addAsyncCleanup(cleanup)
        await until(lambda: runtime.is_ready or runtime.session.status.state.value == 'blocked' or running.done())
        if running.done(): await running
        if runtime.is_ready:
            await until(lambda: runtime.media._gate or not runtime.media.device_available)
        return runtime, socket, backend, decisions, running

    async def test_manual_wake_both_and_null_effective_share_bootstrap(self):
        for manual, wake, effective in ((True, False, True), (False, True, True), (True, True, True), (True, True, False)):
            with self.subTest(manual=manual, wake=wake, effective=effective):
                r, s, _, d, _ = await self.start(profile=V2Profile(manual=manual, wake_word=wake,
                    wake_word_ids=['hey_jarvis'] if wake else []), socket=RuntimeSocket(null_effective=not effective))
                self.assertTrue(r.is_ready)
                hello = json.loads(s.sent[0])
                self.assertEqual(hello['requestedSession']['trigger'], dict(manual=manual, wakeWord=wake))
                self.assertEqual(hello['runtimeSuppression'], dict(manual=True, wakeWord=True))
                self.assertEqual(r.mirror.mirror.view.manual_available, bool(manual and effective))
                self.assertTrue(r.audio.is_running)
                self.assertIs(r.results.connection, r.mirror)
                self.assertIs(r.controls.mirror_connection, r.mirror)
                await r.shutdown()

    async def test_restore_confirmed_before_first_pcm_and_ready_projection(self):
        r, s, _, decisions, _ = await self.start(profile=V2Profile(desired_settings={KEY: 4000}))
        self.assertEqual(r.settings.report().effective[KEY], 4000)
        self.assertEqual(r.mirror.mirror.view.trigger['suppressed']['manual'], False)
        r.audio._stream.emit()
        await until(lambda: any(isinstance(x, bytes) for x in s.sent))
        first = next(i for i, x in enumerate(s.sent) if isinstance(x, bytes))
        preceding = [json.loads(x)['type'] for x in s.sent[:first]]
        self.assertLess(preceding.index(p.CommandType.SETTINGS_PATCH), preceding.index(p.CommandType.SUPPRESSION))
        self.assertTrue(all(not d.snapshot.manual_available for d in decisions if d.snapshot and d.snapshot.availability != 'ready'))

    async def test_disconnect_at_each_bootstrap_boundary_never_releases_pcm(self):
        for kind in (p.CommandType.SETTINGS_PATCH, p.CommandType.SNAPSHOT_REQUEST, p.CommandType.SUPPRESSION):
            s = RuntimeSocket()
            async def fail(command):
                if command['type'] == kind:
                    s.closed = True
                    s.inbox.put_nowait(close_error(4400))
            s.hook = fail
            r, _, _, _, _ = await self.start(profile=V2Profile(desired_settings={KEY: 4000}), socket=s)
            self.assertFalse(r.is_ready)
            self.assertFalse(any(isinstance(x, bytes) for x in s.sent))
            await r.shutdown()

    async def test_multiple_activations_background_final_and_history_before_paste(self):
        r, s, backend, decisions, _ = await self.start()
        self.assertTrue((await r.primary_dictation_action()).success)
        s.emit_event(p.EventType.RECORDING_STARTED)
        s.phase('segment_active')
        s.emit_event(p.EventType.INTERIM, text='synthetic interim')
        await until(lambda: bool(r.feedback._v2_snapshot.previews))
        self.assertEqual(backend.set_calls, [])
        s.emit_event(p.EventType.RECORDING_ENDED)
        s.emit_event(p.EventType.TRANSCRIPTION_ACCEPTED)
        s.finish()
        s.start_activation(B)
        s.emit_event(p.EventType.RECORDING_STARTED, aid=B, sid=p.new_id(), segment_sequence=2)
        s.phase('segment_active', B)
        final = s.emit_event(p.EventType.COMPLETED, text='synthetic final')
        await until(lambda: len(backend.set_calls) == 1)
        entries = r.get_recent_entries()
        self.assertEqual((entries[0].activation_id, entries[0].segment_id), (A, S))
        self.assertEqual(r.mirror.mirror.view.input.activation_id, B)
        s.push(final.to_mapping())
        await asyncio.sleep(.03)
        self.assertEqual(len(backend.set_calls), 1)
        self.assertEqual(len(entries), 1)
        self.assertEqual(r.reinsert_last().status.value, 'queued')
        await until(lambda: len(backend.set_calls) == 2)
        self.assertEqual(len(r.get_recent_entries()), 1)

    async def test_history_disabled_keeps_terminal_dedup(self):
        config = config_in(self.folder.name)
        config.history.enabled = False
        r, s, backend, _, _ = await self.start(config=config)
        s.start_activation(); s.emit_event(p.EventType.RECORDING_STARTED)
        final = s.emit_event(p.EventType.COMPLETED, text='synthetic final')
        await until(lambda: len(backend.set_calls) == 1)
        s.push(final.to_mapping()); await asyncio.sleep(.03)
        self.assertEqual(len(backend.set_calls), 1)
        self.assertEqual(r.get_recent_entries(), ())

    async def test_history_fault_isolated_with_diagnostic_and_controls_survive(self):
        r, s, backend, decisions, _ = await self.start()
        s.start_activation(); s.emit_event(p.EventType.RECORDING_STARTED)
        with patch.object(r.history, 'add_entry_with_status', side_effect=OSError('synthetic')):
            s.emit_event(p.EventType.COMPLETED, text='synthetic final')
            await until(lambda: 'history_unavailable' in r._issues)
        await until(lambda: r.is_ready)
        self.assertEqual(backend.set_calls, [])
        self.assertTrue(any(d.snapshot and 'history_unavailable' in d.snapshot.diagnostics for d in decisions))
        self.assertTrue((await r.cancel_dictation()).success)

    async def test_device_loss_preserves_background_results_and_pause(self):
        r, s, backend, _, _ = await self.start()
        s.start_activation(); s.emit_event(p.EventType.RECORDING_STARTED)
        s.emit_event(p.EventType.RECORDING_ENDED); s.emit_event(p.EventType.TRANSCRIPTION_ACCEPTED); s.finish()
        r.media.set_device_available(False)
        await until(lambda: not r.audio.is_running)
        s.emit_event(p.EventType.COMPLETED, text='synthetic background final')
        await until(lambda: len(backend.set_calls) == 1)
        self.assertTrue(r.session.is_ready)
        self.assertFalse(r.media.audio_available)
        self.assertFalse(r.media.set_hardware_muted(True, binding=object()))

    async def test_pending_command_disconnect_completes_and_shutdown_joins_workers(self):
        r, s, _, _, running = await self.start()
        s.drop = p.CommandType.ACTIVATION
        command = asyncio.create_task(r.primary_dictation_action())
        await until(lambda: r.session.pending_count > 0)
        s.inbox.put_nowait(close_error(4400))
        result = await asyncio.gather(command, return_exceptions=True)
        self.assertIsInstance(result[0], Exception)
        await r.shutdown(); await running
        self.assertEqual(r.session.pending_count, 0)
        self.assertFalse(r.queue._worker_thread.is_alive())
        self.assertFalse(r.audio.is_running)
        self.assertEqual(r.media.queue.duration_ms, 0)
        self.assertEqual(r.logs.active_transport_count, 0)
        self.assertEqual(r.cleanup_errors, [])

    async def test_resync_without_snapshot_remains_guarded_and_bounded(self):
        r, s, _, _, _ = await self.start()
        s.snapshot_missing = True
        r.mirror.mirror.limits = replace(r.mirror.mirror.limits, snapshot_timeout=.03)
        s.state['lastEventSeq'] = 1
        s.emit_event(p.EventType.ACTIVATION_STARTED)
        await until(lambda: not r.is_ready)
        self.assertFalse((await r.primary_dictation_action()).success)
        await asyncio.sleep(.15)
        self.assertLessEqual(r.session.pending_count, 1)
        await r.shutdown()

    async def test_local_audio_probe_and_persist_failure_roll_back_config(self):
        r, s, _, _, _ = await self.start()
        old = deepcopy(r.config)
        candidate = deepcopy(old); candidate.audio.device = 'missing'
        with patch.object(r.audio, 'probe', side_effect=OSError('synthetic device failure')):
            result = await r.apply_runtime_config(candidate)
        self.assertFalse(result.success)
        self.assertEqual(r.config.audio, old.audio)
        self.assertEqual(r.audio._config, old.audio)
        self.assertTrue(r.media.device_available)
        candidate = deepcopy(old); candidate.overlay.enabled = not old.overlay.enabled
        with patch.object(AppConfig, 'save_user', side_effect=OSError('synthetic disk failure')):
            result = await r.apply_runtime_config(candidate)
        self.assertFalse(result.success)
        self.assertEqual(r.config, old)

    async def test_reconnect_requires_explicit_open_input_or_drain_decision(self):
        r, s, _, _, _ = await self.start()
        s.start_activation()
        await until(lambda: r.mirror.mirror.view.input.activation_id == A)
        before = r.session.generation
        result = await r.reconnect_server()
        self.assertFalse(result.success)
        self.assertEqual(result.status, 'apply_choice_required')
        self.assertEqual(r.session.generation, before)

    async def test_autostart_after_confirmed_ready_only_once(self):
        r, s, _, _, _ = await self.start()
        r.request_initial_auto_start()
        r._reduction(None)
        await until(lambda: s.activation_count == 1)
        await until(lambda: r.is_ready)
        r._reduction(None)
        await asyncio.sleep(.03)
        self.assertEqual(s.activation_count, 1)

    async def test_migration_backup_and_persist_are_actual_raw_overrides(self):
        path = Path(self.folder.name)/'legacy.yaml'
        original = b'session:\n  mode: hotkey\noverlay:\n  enabled: false\n'
        path.write_bytes(original)
        config = AppConfig.load(path)
        config.history.persistent.db_path = str(Path(self.folder.name)/'migration.sqlite')
        config.event_stream.enabled = False
        r, s, _, _, _ = await self.start(config=config)
        self.assertTrue(r.is_ready)
        self.assertEqual(path.with_name(path.name+'.pre-v2.bak').read_bytes(), original)
        loaded = AppConfig.load(path)
        self.assertEqual(loaded.v2_profile['desired_settings'], {})
        self.assertFalse(loaded.overlay.enabled)
        self.assertTrue(loaded.server.url.endswith('/ws/v2'))

    async def test_two_segments_same_activation_same_text_keep_distinct_results(self):
        r, s, backend, _, _ = await self.start()
        s.start_activation(source='wake_word')
        s.emit_event(p.EventType.RECORDING_STARTED)
        s.emit_event(p.EventType.RECORDING_ENDED)
        s.emit_event(p.EventType.TRANSCRIPTION_ACCEPTED)
        s.emit_event(p.EventType.COMPLETED, text='synthetic identical text')
        await until(lambda: len(backend.set_calls) == 1)
        second = p.new_id()
        s.emit_event(p.EventType.RECORDING_STARTED, sid=second, segment_sequence=2)
        s.emit_event(p.EventType.COMPLETED, sid=second, segment_sequence=2, text='synthetic identical text')
        await until(lambda: len(backend.set_calls) == 2)
        entries = r.get_recent_entries()
        self.assertEqual({e.segment_id for e in entries}, {S, second})
        self.assertEqual({e.activation_id for e in entries}, {A})


class QtRuntime(unittest.TestCase):
    def setUp(self):
        if os.environ.get('VOICE_STT_RUNTIME_QT_CHILD') != '1':
            child = subprocess.run([sys.executable, '-W', 'error', '-m', 'unittest',
                'tests.test_v2_runtime_integration.QtRuntime.' + self._testMethodName, '-v'],
                env=dict(os.environ, VOICE_STT_RUNTIME_QT_CHILD='1', QT_QPA_PLATFORM='offscreen', PYTHONUTF8='1'),
                capture_output=True, text=True, encoding='utf-8', timeout=40)
            self.assertEqual(child.returncode, 0, child.stdout + child.stderr)
            self._child_done = True
            return
        self._child_done = False
        from PySide6.QtWidgets import QApplication
        from voice_stt_client.ui.v2_core_bridge import V2CoreBridge
        from voice_stt_client.ui.v2_application import V2DesktopApplication
        from tests.test_ui_application import FakeGuard, FakeHotkeyBackend, FakeLedFeedback
        self.app = QApplication.instance() or QApplication([])
        self.folder = tempfile.TemporaryDirectory(); self.addCleanup(self.folder.cleanup)
        self.socket = None
        self.runtime = None
        self.backend = MockInjectionBackend()
        self.hotkey_backend = FakeHotkeyBackend()
        for target, kwargs in (
            ('sounddevice.query_devices', dict(side_effect=devices)),
            ('sounddevice.check_input_settings', {}), ('sounddevice.InputStream', dict(new=Stream))):
            active = patch(target, **kwargs); active.start(); self.addCleanup(active.stop)
        config = config_in(self.folder.name)
        def factory(cfg):
            self.socket = RuntimeSocket()
            http = FakeHTTP(); http.origin = 'https://stt.voice.marcosudau.com'
            async def connector(*a, **kw): return self.socket
            self.runtime = V2Runtime(cfg, http=http, connector=connector, backend=self.backend)
            return self.runtime
        self.bridge = V2CoreBridge(config, runtime_factory=factory)
        self.desktop = V2DesktopApplication(self.app, config, FakeGuard(), bridge=self.bridge,
            hotkey_backend=self.hotkey_backend, led_feedback=FakeLedFeedback())
        self.addCleanup(self.desktop.shutdown)
        self.assertTrue(self.desktop.start())
        self.wait(lambda: self.desktop._runtime_ready and self.runtime.media._gate)

    def wait(self, predicate, timeout=8):
        deadline = time.monotonic() + timeout
        while not predicate() and time.monotonic() < deadline:
            self.app.processEvents(); time.sleep(.005)
        self.app.processEvents()
        self.assertTrue(predicate())

    def core(self, operation):
        return asyncio.run_coroutine_threadsafe(operation(), self.bridge._loop)

    def test_actual_bridge_thread_qt_output_and_native_role_dispatch(self):
        if self._child_done: return
        touched = []
        original = self.desktop.tray.update_feedback_decision
        self.desktop.tray.update_feedback_decision = lambda d: (touched.append(threading.get_ident()), original(d))
        primary = self.desktop.hotkeys.role_ids['primary']
        self.assertTrue(self.desktop.hotkeys.dispatch_hotkey_id(primary))
        self.wait(lambda: self.desktop.tray.status_action.text() == 'Wartet auf Sprache')
        self.assertTrue(touched)
        self.assertEqual(set(touched), {threading.get_ident()})
        self.assertNotEqual(self.bridge.worker_thread_id, threading.get_ident())
        self.assertFalse(any(c['type'] in ('start', 'stop', 'ping') for c in self.socket.commands))

    def test_profile_transaction_rebind_persist_and_failure_rollback(self):
        if self._child_done: return
        async def apply(key):
            ui = self.runtime.settings_ui_session()
            profile = asdict(self.runtime.settings.profile)
            profile['controls']['primary_key'] = key
            return await ui.apply_profile(profile, ui.context())
        success = self.core(lambda: apply('Ctrl+Shift+F11'))
        self.wait(success.done); success.result()
        self.assertEqual(self.desktop.hotkeys.config.primary_key, 'Ctrl+Shift+F11')
        self.assertEqual(AppConfig.load(self.desktop.config._config_source_path).v2_profile['controls']['primary_key'], 'Ctrl+Shift+F11')
        with patch.object(AppConfig, 'save_user', side_effect=OSError('synthetic disk failure')):
            failure = self.core(lambda: apply('Ctrl+Shift+F12'))
            self.wait(failure.done)
            self.assertIsNotNone(failure.exception())
        self.assertEqual(self.desktop.hotkeys.config.primary_key, 'Ctrl+Shift+F11')
        self.assertEqual(self.runtime.controls.config.primary_key, 'Ctrl+Shift+F11')
        self.assertEqual(self.desktop.config.v2_profile['controls']['primary_key'], 'Ctrl+Shift+F11')

    def test_dialog_close_reopen_new_lease_and_shutdown_all_workers(self):
        if self._child_done: return
        self.desktop.show_settings()
        self.wait(lambda: self.desktop.settings_dialog._view is not None)
        old = self.desktop._settings_port._session
        self.desktop.settings_dialog.close(); self.app.processEvents()
        self.assertFalse(old.active)
        self.desktop.show_settings()
        self.wait(lambda: self.desktop._settings_port._session is not None)
        self.assertIsNot(old, self.desktop._settings_port._session)
        self.desktop.shutdown()
        self.assertFalse(self.bridge.is_running)
        self.assertFalse(self.runtime.queue._worker_thread.is_alive())
        self.assertEqual(self.runtime.cleanup_errors, [])
        self.assertTrue(self.desktop.output._closed)

    def test_adapter_failure_keeps_capture_controls_and_results_alive(self):
        if self._child_done: return
        seen = []
        failures = []
        self.bridge.feedback_decision_received.connect(lambda d: seen.append((
            d.event.event_type.value if d.event else None, bool(d.rule.led), bool(d.rule.sound), d.publish)))
        self.desktop.output.failure.connect(failures.append)
        def failed(*args, **kwargs): raise RuntimeError('synthetic adapter failure')
        self.desktop.output.led.submit = failed
        self.desktop.output.sound.play = failed
        self.desktop.hotkeys.dispatch_hotkey_id(self.desktop.hotkeys.role_ids['primary'])
        try:
            self.wait(lambda: 'led_unavailable' in self.runtime._issues)
        except AssertionError:
            self.fail(repr((seen, failures, self.runtime._issues, self.runtime.feedback.mapping.to_mapping())))
        self.assertTrue(self.runtime.is_ready)
        self.assertTrue(self.runtime.media._gate)

    def test_shutdown_during_disk_commit_finishes_and_releases_native_keys(self):
        if self._child_done: return
        from PySide6.QtCore import QTimer
        entered, release = threading.Event(), threading.Event()
        save = AppConfig.save_user
        disk_threads = []
        def slow_save(config):
            disk_threads.append(threading.get_ident())
            entered.set()
            if not release.wait(3):
                raise OSError('synthetic commit timeout')
            return save(config)
        async def apply():
            ui = self.runtime.settings_ui_session()
            profile = asdict(self.runtime.settings.profile)
            profile['controls']['primary_key'] = 'Ctrl+Shift+F11'
            return await ui.apply_profile(profile, ui.context())
        with patch.object(AppConfig, 'save_user', slow_save):
            future = self.core(apply)
            self.wait(entered.is_set)
            QTimer.singleShot(20, release.set)
            self.desktop.shutdown()
        self.assertFalse(self.bridge.is_running)
        self.assertFalse(self.desktop.hotkeys._registered_ids)
        self.assertFalse(self.runtime._transactions)
        self.assertNotIn(threading.get_ident(), disk_threads)
        self.assertEqual(AppConfig.load(self.desktop.config._config_source_path).v2_profile['controls']['primary_key'],
                         self.desktop.config.v2_profile['controls']['primary_key'])
        self.assertTrue(future.done())

    def test_device_enumeration_on_worker_and_local_config_apply(self):
        if self._child_done: return
        enumerations = []
        def listed():
            enumerations.append(threading.get_ident())
            return [dict(index=0, name='synthetic input', channels=1)]
        with patch('voice_stt_client.core.audio_capture.AudioCapture.list_devices', side_effect=listed):
            self.desktop.show_settings()
            self.wait(lambda: self.desktop._local_dialog._editors['audio.device'].count() == 2)
        self.assertNotIn(threading.get_ident(), enumerations)
        candidate = deepcopy(self.desktop.config)
        candidate.overlay.enabled = not candidate.overlay.enabled
        self.assertTrue(self.desktop._apply_settings(candidate, set()))
        self.wait(lambda: self.desktop._pending_config is None)
        self.assertEqual(self.desktop.config.overlay, self.runtime.config.overlay)
        self.assertEqual(AppConfig.load(candidate._config_source_path).overlay, candidate.overlay)


class MigrationBoundary(unittest.TestCase):
    def test_loaded_profile_uses_actual_user_values_and_known_endpoint_migration(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'config.yaml'
            path.write_text('session:\n  mode: hotkey\noverlay:\n  enabled: false\n', encoding='utf-8')
            cfg = AppConfig.load(path)
            profile = runtime_profile(cfg)
            self.assertEqual(profile.desired_settings, {})
            self.assertFalse(profile.wake_word)
            self.assertFalse(cfg.overlay.enabled)
            self.assertEqual(v2_endpoint('wss://stt.voice.marcosudau.com/ws/transcribe?wakeWords=old'),
                             'wss://stt.voice.marcosudau.com/ws/v2')
            self.assertEqual(v2_endpoint('wss://host.example/other'), 'wss://host.example/other')


if __name__ == '__main__': unittest.main()
