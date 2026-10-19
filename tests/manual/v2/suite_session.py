"""Real source desktop for one owned guided attempt. Never starts/stops a server.

All runtime paths are explicit, ignored and inside the repository. Transport
deadlines are diagnostic overrides, not changed product defaults. No raw PCM.
"""
import argparse
import asyncio
from dataclasses import asdict
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time

from tests.manual.v2.suite_plan import TASKS, owned_path, target_origin


def save(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf8')
    temp.replace(path)


def prepare_profile(folder, target, task, device):
    # Caller sets environment BEFORE importing the product configuration.
    from voice_stt_client.core.config import AppConfig, DEFAULT_CONFIG_PATH
    from voice_stt_client.core.v2_profile import V2Profile
    import yaml
    origin = target_origin(target)
    config = AppConfig._load_single(DEFAULT_CONFIG_PATH)
    config.server.url, config.server.health_url = target, origin+'/health'
    config.audio.device = device
    profile = V2Profile(manual=True, wake_word=False, wake_word_ids=[],
                        desired_settings={'activation.followupTimeoutMs': 5000})
    profile.controls.update(primary_key='Ctrl+Shift+F8', secondary_key='Ctrl+Shift+F9',
                            secondary_action=task['secondary'], wake_pause_key='Ctrl+Shift+F10',
                            reinsert_last_key='Ctrl+Shift+F11', overlay_toggle_key='Ctrl+Shift+F12')
    config.v2_profile = asdict(profile)
    config.history.persistent.db_path = str(folder/'client/history.sqlite')
    config.history.persistent.store_all = True
    config.history.persistent.min_characters = 0
    config.logging.log_dir = str(folder/'client/logs')
    config.logging.observability.store_transcription_content = False
    config.logging.observability.store_raw_payload = False
    config.event_stream.cursor_path = str(folder/'client/cursor.json')
    # Preserve the explicitly requested test variant without importing a V1
    # profile or the retired AppData instance. Flash and sound rules unchanged.
    raw = AppConfig._to_plain_data(asdict(config))
    raw['feedback_mappings'] = config.feedback_mappings.to_mapping()
    events = raw['feedback_mappings']['events']
    levels = [.1, .2, .3, .4, .5, .6, .7, .8, .9, 1., 1., 1.]
    colors = ['#'+f'{round(255*level):02X}'*3 for level in levels]
    for key in ('server.input.waiting', 'server.input.followup', 'server.input.idle'):
        calls = events[key]['led']
        if not isinstance(calls, list):
            calls = [calls]
            events[key]['led'] = calls
        for call in calls:
            if 'set_state' in call:
                if key.endswith('.idle'):
                    call.setdefault('config', {})['color'] = '#FFFFFF'
                else:
                    call.clear()
                    call.update(set_state='palette_cycle', config=dict(
                        colors=colors, brightness=1., speed=6., reverse=False))
    path = folder/'profile.yaml'
    path.write_text(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False), encoding='utf8')
    return AppConfig.load(path)


def main():
    sys.stdout.reconfigure(encoding='utf8', errors='backslashreplace')
    sys.stderr.reconfigure(encoding='utf8', errors='backslashreplace')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, required=True)
    parser.add_argument('--editor-state', type=Path, required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--task', choices=[task['id'] for task in TASKS], required=True)
    parser.add_argument('--device', type=int, required=True)
    parser.add_argument('--smoke', action='store_true', help='Autonomous real microphone/transport precheck; no keys, sounds, LEDs or activation')
    args = parser.parse_args()
    target_origin(args.target)
    folder, editor_state = owned_path(args.folder), owned_path(args.editor_state)
    task = next(task for task in TASKS if task['id'] == args.task)
    folder.mkdir(parents=True, exist_ok=True)
    os.environ['VOICESTT_CLIENT_HOME'] = str(folder/'client')
    os.environ['VOICESTT_CLIENT_CONFIG'] = str(folder/'profile.yaml')
    os.environ['TEMP'] = os.environ['TMP'] = str(folder/'tmp')
    (folder/'tmp').mkdir(exist_ok=True)
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from voice_stt_client.core.audio_capture import AudioCapture
    from voice_stt_client.core.logging_setup import setup_logging
    from voice_stt_client.core.observability.manager import ObservabilityManager
    from voice_stt_client.core.settings_service import SettingsHTTP
    from voice_stt_client.core.text_injector import CtypesWindowsInjectionBackend
    from voice_stt_client.core.v2_runtime import V2Runtime
    from voice_stt_client.core.v2_transport import V2TransportConfig
    from voice_stt_client.core.version import __version__
    from voice_stt_client.ui.v2_application import V2DesktopApplication
    from voice_stt_client.ui.v2_core_bridge import V2CoreBridge
    from voice_stt_client.ui.single_instance import SingleInstanceGuard
    from tests.manual.v2.editor_state import read_editor_state
    from tests.manual.v2.observed_session import safe_event
    from scripts.qualify_v2_session import process_memory
    config = prepare_profile(folder, args.target, task, args.device)
    if args.smoke:
        config.feedback.sounds_enabled = False
        config.led.enabled = False
        config.v2_profile['controls']['enabled'] = False
        config.save(folder/'profile.yaml')
        from voice_stt_client.core.config import AppConfig
        config = AppConfig.load(folder/'profile.yaml')
    # Validate device identity again after any USB enumeration change.
    device = next((device for device in AudioCapture.list_devices()
                   if device['index'] == args.device and 'respeaker' in device['name'].lower()), None)
    if device is None:
        raise RuntimeError('Selected ReSpeaker is not available; no fallback microphone used')
    trace, lock = folder/'events.jsonl', threading.Lock()
    def emit(kind, **fields):
        with lock, trace.open('a', encoding='utf8') as handle:
            handle.write(json.dumps(dict(type=kind, timeUtc=datetime.now(UTC).isoformat(),
                                         monotonic=time.monotonic(), **fields), ensure_ascii=True)+'\n')
    expected_pid = read_editor_state(editor_state)['pid']

    class OwnEditorBackend(CtypesWindowsInjectionBackend):
        def allowed(self, hwnd):
            try:
                state = read_editor_state(editor_state)
            except TimeoutError:
                emit('owner.state_unreadable')
                app.quit()
                return
            age = abs((datetime.now(UTC)-datetime.fromisoformat(state['timeUtc'])).total_seconds())
            _, pid = self.get_window_thread_process_id(hwnd)
            return bool(age < 2 and pid == expected_pid and state.get('editorHasFocus') and state.get('foreground'))

        def get_foreground_window(self):
            hwnd = super().get_foreground_window()
            return hwnd if self.allowed(hwnd) else 0

        def send_input_keyboard(self, events):
            if not self.allowed(super().get_foreground_window()):
                return 0
            return super().send_input_keyboard(events)

    manager = ObservabilityManager(config.logging.observability, log_dir=config.logging.log_dir)
    manager.start()
    setup_logging(config.logging, observability=manager)
    app = QApplication([])
    app.setOrganizationName('VoiceSTTQualification')
    app.setApplicationName('AP-IV2-020 guided isolated test')
    app.setQuitOnLastWindowClosed(False)
    guard = SingleInstanceGuard(r'Local\VoiceSTT_Qualification_AP_IV2_020')
    if not guard.acquire().acquired:
        manager.stop(2)
        raise RuntimeError('Another qualification client is running')
    runtime = None

    def factory(cfg):
        nonlocal runtime
        runtime = V2Runtime(cfg, observability=manager.ingress, backend=OwnEditorBackend(),
            http=SettingsHTTP(args.target, timeout=180), transport_config=V2TransportConfig(
                url=args.target, client_version=__version__, connect_timeout=180,
                admission_timeout=180, bootstrap_timeout=180))
        previous = runtime.session.on_message
        def receive(binding, event):
            previous(binding, event)
            emit('wire', event=safe_event(binding, event))
        runtime.session.on_message = receive
        previous_completion = runtime.session.on_completion
        def completed(value):
            if previous_completion:
                previous_completion(value)
            emit('command.completed', commandType=str(value.command.type),
                 action=value.command.payload.get('action'), commandId=value.command.commandId,
                 accepted=value.ack.accepted, result=str(value.ack.result), activationId=value.ack.activationId)
        runtime.session.on_completion = completed
        return runtime

    class ObservedBridge(V2CoreBridge):
        def press_control(self, slot):
            view = self._published_view
            emit('control.received', slot=str(slot), ready=bool(view and view.ready),
                 generation=view.generation if view else None,
                 phase=str(view.mirror.input.phase) if view else None)
            return super().press_control(slot)

    desktop = None
    latest = {}
    latest_metrics = {}
    started_at = time.monotonic()
    smoke_ready_at = None
    def snapshot(view):
        latest.update(ready=view.ready, generation=view.generation, sessionId=view.session_id,
                      transport=view.transport, reason=view.reason, phase=str(view.mirror.input.phase),
                      activationId=view.mirror.input.activation_id)
        emit('runtime.view', **latest)

    try:
        bridge = ObservedBridge(config, runtime_factory=factory, observability=manager.ingress)
        bridge.snapshot_changed.connect(snapshot)
        desktop = V2DesktopApplication(app, config, guard, bridge=bridge,
                                      observability=manager.ingress, observability_manager=manager)
        app.aboutToQuit.connect(desktop.shutdown)
        if not desktop.start():
            raise RuntimeError('Desktop failed to start')
        emit('desktop.started', sourceOnly=True, configSha256=hashlib.sha256((folder/'profile.yaml').read_bytes()).hexdigest(),
             target=args.target, device=device, timeouts=dict(http=180, connect=180, admission=180, bootstrap=180),
             boundaries='Actual production source desktop; own editor guard; no frozen-build qualification.')
        processed = set()
        inbox = folder/'commands'
        inbox.mkdir(exist_ok=True)
        def poll():
            nonlocal smoke_ready_at
            # A lost/killed workbench cannot leave an orphan microphone client.
            state = read_editor_state(editor_state)
            age = abs((datetime.now(UTC)-datetime.fromisoformat(state['timeUtc'])).total_seconds())
            if age > 15 or time.monotonic()-started_at > 30*60:
                emit('owner.timeout', staleSeconds=age)
                app.quit()
                return
            for path in sorted(inbox.glob('*.json')):
                if path.name in processed:
                    continue
                processed.add(path.name)
                command = json.loads(path.read_text(encoding='utf8'))
                action = command.get('action')
                emit('operator.command', action=action)
                if action == 'stop':
                    app.quit()
                elif action == 'settings':
                    desktop.show_settings()
                elif action == 'reconnect':
                    desktop.reconnect_server()
            status = dict(latest, pid=os.getpid(), timeUtc=datetime.now(UTC).isoformat())
            with lock:
                status.update(latest_metrics)
            save(folder/'status.json', status)
            if args.smoke and status.get('ready') and status.get('audioAvailable'):
                smoke_ready_at = smoke_ready_at or time.monotonic()
                if time.monotonic()-smoke_ready_at >= 5 and status.get('media', {}).get('sent', 0) > 20:
                    save(folder/'smoke.json', dict(result='PASS', actualAudioFrames=status.get('media', {}).get('sent'),
                         scope='Five seconds real source desktop READY/audio; no activation, human feedback or frozen qualification'))
                    app.quit()
            elif args.smoke:
                smoke_ready_at = None
            if args.smoke and time.monotonic()-started_at > 600:
                save(folder/'smoke.json', dict(result='FAIL', reason='No stable ready/audio within 600 seconds'))
                app.quit()
        timer = QTimer()
        timer.timeout.connect(poll)
        timer.start(250)
        async def metrics():
            while not runtime.is_closing:
                values = dict(tasks=len(asyncio.all_tasks()), commands=len(runtime._commands),
                     trackerPending=runtime.session.pending_count, memory=process_memory(),
                     media=runtime.media.counters(), capture=runtime.audio.capture_counters(),
                     injectionQueue=runtime.queue.queue_size(), audioAvailable=bool(runtime.media.audio_available))
                with lock:
                    latest_metrics.update(values)
                emit('metrics', **values)
                await asyncio.sleep(1)
        metrics_future = asyncio.run_coroutine_threadsafe(metrics(), bridge._loop)
        app.exec()
        metrics_future.cancel()
    finally:
        if desktop:
            desktop.shutdown()
        guard.release()
        manager.stop(2)
        emit('desktop.stopped')


if __name__ == '__main__':
    main()
