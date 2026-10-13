"""AP100 actual desktop/core thread against the byte-verified pinned server.

Only PortAudio, Windows injection/registration, recorder/ASR/scheduler and
physical sound/LED sinks are controlled. No replacement of client services.
"""
import argparse
import asyncio
from dataclasses import asdict
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import tempfile
import threading
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_v2_server_transport import SERVER_SHA, verify_sources, until
from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.config import AppConfig, DEFAULT_CONFIG_PATH
from voice_stt_client.core.event_models import EventConnectionState
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.core.v2_runtime import V2Runtime
from voice_stt_client.ui.v2_core_bridge import V2CoreBridge
from voice_stt_client.ui.v2_application import V2DesktopApplication
from tests.test_v2_runtime_integration import Stream, devices
from tests.test_text_injector import MockInjectionBackend
from tests.test_ui_application import FakeGuard, FakeHotkeyBackend, FakeLedFeedback


def run(root, repository):
    # Keep the client fixtures already imported; expose only the server's unit
    # fixture namespace. Both production modules and imported fixture bytes are
    # checked against git show ada13b0 before admission and after the run.
    import tests
    tests.__path__.append(str(root / 'tests'))
    sys.path.insert(0, str(root))
    import uvicorn
    from PySide6.QtWidgets import QApplication
    from api_fastapi_server.server import create_app, ServerSettings
    from tests.unit.test_server_controlled_e2e import GateAwareRecorder
    from tests.unit.test_fastapi_server_multi_user import ManualScheduler
    source_hashes = verify_sources(root, repository)
    qt = QApplication.instance() or QApplication([])
    checks, state, published_threads = [], {}, []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    def wait(predicate, timeout=15):
        end = time.monotonic() + timeout
        while not predicate():
            qt.processEvents()
            if time.monotonic() > end:
                raise AssertionError('checkpoint timeout: ' + str(state.get('runtime').get_snapshot()
                    if state.get('runtime') else checks))
            time.sleep(.005)
        qt.processEvents()
    server_loop = asyncio.new_event_loop()
    server_thread = threading.Thread(target=server_loop.run_forever, name='AP100-production-server')
    server_thread.start()
    def server_call(operation):
        return asyncio.run_coroutine_threadsafe(operation(), server_loop).result(15)
    with tempfile.TemporaryDirectory(prefix='cv2-100-server-') as folder, patch.dict(
        os.environ, {'VOICESTT_SERVER_COMMIT': SERVER_SHA}), patch('sounddevice.query_devices',
        side_effect=devices), patch('sounddevice.check_input_settings'), patch('sounddevice.InputStream', Stream):
        async def start_server():
            settings = ServerSettings(data_root_path=str(Path(folder)/'server'), model_warmup=False,
                request_logging_enabled=False, performance_logging_enabled=False,
                performance_log_mirror_enabled=False, transcription_logging_enabled=True,
                system_event_logging_enabled=False, event_store_enabled=True, log_live_enabled=True)
            app = create_app(settings, recorder_factory=GateAwareRecorder, scheduler_factory=ManualScheduler)
            service = app.state.voicestt_service
            service.wakeword_catalog.set_artifact_prober(lambda path: None)
            tcp = socket.socket(); tcp.bind(('127.0.0.1', 0)); tcp.listen(16)
            server = uvicorn.Server(uvicorn.Config(app, log_level='error', access_log=False))
            serving = asyncio.create_task(server.serve(sockets=[tcp]))
            await until(lambda: server.started)
            state.update(service=service, server=server, serving=serving, tcp=tcp)
            return f'ws://127.0.0.1:{tcp.getsockname()[1]}/ws/v2'
        desktop = None
        try:
            url = server_call(start_server)
            config = AppConfig._load_single(DEFAULT_CONFIG_PATH)
            config.server.url = url
            config._config_source_path = Path(folder)/'client.yaml'
            config.v2_profile = asdict(V2Profile(desired_settings={'activation.followupTimeoutMs': 4000}))
            config.history.persistent.db_path = str(Path(folder)/'history.sqlite')
            config.history.persistent.store_all = True
            config.event_stream.cursor_path = str(Path(folder)/'cursor.json')
            config.event_stream.cursor_persistence_enabled = False
            config.led.enabled = False
            config.text_injection.append_space = False
            config.text_injection.paste_delay_ms = 0
            backend = MockInjectionBackend()
            def factory(cfg):
                state['runtime'] = V2Runtime(cfg, backend=backend)
                return state['runtime']
            bridge = V2CoreBridge(config, runtime_factory=factory)
            desktop = V2DesktopApplication(qt, config, FakeGuard(), bridge=bridge,
                hotkey_backend=FakeHotkeyBackend(), led_feedback=FakeLedFeedback())
            sounds = []
            desktop.sound_feedback.play = sounds.append
            bridge.feedback_decision_received.connect(lambda d: published_threads.append(threading.get_ident()))
            def core(operation):
                future = asyncio.run_coroutine_threadsafe(operation(), bridge._loop)
                wait(future.done)
                return future.result()
            check('desktop/actual_start', desktop.start())
            r = state['runtime']
            wait(lambda: desktop._runtime_ready and r.media._gate and r.logs.context.event_state == EventConnectionState.LIVE)
            check('admission/pinned_server', r.session.binding.accepted.payload['serverCommit'] == SERVER_SHA)
            check('bootstrap/restore_before_capture', r.settings.report().effective['activation.followupTimeoutMs'] == 4000)
            check('ownership/shared_mirror', r.results.connection is r.controls.mirror_connection is r.mirror)
            check('threads/qt_and_core_separate', bridge.worker_thread_id != threading.get_ident())
            domain = state['service'].sessions.get(r.session.binding.session_id)
            def settled(): wait(lambda: desktop._runtime_ready and r.is_ready)
            def activate():
                settled()
                desktop.hotkeys.dispatch_hotkey_id(desktop.hotkeys.role_ids['primary'])
                wait(lambda: r.mirror.mirror.view.input.activation_id is not None)
                settled()
                return r.mirror.mirror.view.input.activation_id
            def record():
                previous = set(r.mirror.mirror.view.segments)
                r.audio._stream.emit()
                wait(lambda: bool(set(r.mirror.mirror.view.segments)-previous))
                return next(iter(set(r.mirror.mirror.view.segments)-previous))
            def end_recording():
                previous = len(state['service'].scheduler.jobs)
                async def flush(): domain.recorder.flush_buffered_audio()
                server_call(flush)
                wait(lambda: len(state['service'].scheduler.jobs) > previous)
                wait(lambda: r.mirror.mirror.view.input.phase == p.InputPhase.FOLLOWUP_WAIT)
                settled()
                return state['service'].scheduler.jobs[-1]
            aid = activate(); sid = record()
            async def preview(): domain._on_realtime_text('synthetic runtime preview')
            server_call(preview)
            wait(lambda: desktop.overlay.label.text() == 'synthetic runtime preview')
            check('interim/overlay_only', not backend.set_calls)
            job = end_recording()
            core(r.stop_dictation)
            wait(lambda: r.mirror.mirror.view.input.phase == p.InputPhase.IDLE)
            settled()
            check('drain/ready_with_pending_final', r.mirror.mirror.view.activations[aid].status == 'draining')
            ui = core(lambda: asyncio.sleep(0, result=r.settings_ui_session()))
            async def apply():
                profile = asdict(r.settings.profile)
                profile.update(manual=False, wake_word=True, wake_word_ids=['hey_jarvis'])
                return await ui.apply_profile(profile, ui.context(), drain_choice='wait')
            applying = asyncio.run_coroutine_threadsafe(apply(), bridge._loop)
            wait(lambda: ui.controls.pause_view.desired_manual and ui.controls.pause_view.desired_wake_word)
            check('apply/drain_wait_no_destructive_reconnect', not applying.done() and r.session.binding.session_id == domain.session_id)
            async def complete(): state['service'].scheduler.complete(job, text='synthetic runtime final')
            server_call(complete)
            wait(applying.done); applying.result()
            wait(lambda: r.is_ready and r.media._gate and r.session.binding.session_id != domain.session_id)
            wait(lambda: len(backend.set_calls) == 1)
            entries = core(lambda: asyncio.sleep(0, result=r.get_recent_entries()))
            check('final/history_identity_and_single_injection', len(entries) == 1 and
                (entries[0].activation_id, entries[0].segment_id) == (aid, sid))
            check('apply/new_session_wake_only', not r.mirror.mirror.view.manual_available and
                not r.mirror.mirror.view.trigger['configured']['manual'] and r.mirror.mirror.view.trigger['configured']['wakeWord'])
            check('apply/actual_persistence', AppConfig.load(config._config_source_path).v2_profile['wake_word'])
            core(lambda: asyncio.sleep(0, result=r.reinsert_last()))
            wait(lambda: len(backend.set_calls) == 2)
            check('reinsert/separate_no_new_history', len(core(lambda: asyncio.sleep(0, result=r.get_recent_entries()))) == 1)
            wait(lambda: r.logs.context.event_state == EventConnectionState.LIVE)
            check('logs/independent_live_reconnected', r.logs.active_transport_count == 1)
            check('qt/all_published_updates_on_main', published_threads and set(published_threads) == {threading.get_ident()})
            check('feedback/single_final_cue', sum(s.cue.value == 'complete' for s in sounds) == 1)
            started = time.monotonic()
            desktop.shutdown()
            check('shutdown/within_bridge_bound', time.monotonic()-started < 10)
            check('shutdown/core_audio_clipboard_logs_closed', not bridge.is_running and not r.audio.is_running and
                not r.queue._worker_thread.is_alive() and r.logs.active_transport_count == 0 and not r.cleanup_errors)
            return dict(result='PASS', checkCount=len(checks), checks=checks, serverCommit=SERVER_SHA,
                clientHead=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                sourceHashes=verify_sources(root, repository),
                runtime=dict(executable=sys.executable, python=sys.version, platform=platform.platform(), qt=os.environ.get('QT_QPA_PLATFORM')),
                boundaries=__doc__.strip())
        finally:
            if desktop: desktop.shutdown()
            async def close_server():
                if state.get('server'):
                    state['server'].should_exit = True
                    await asyncio.wait_for(state['serving'], 10)
                    state['tcp'].close()
            try: server_call(close_server)
            finally:
                server_loop.call_soon_threadsafe(server_loop.stop)
                server_thread.join(10)
                server_loop.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server-root', required=True, type=Path)
    parser.add_argument('--server-repository', required=True, type=Path)
    args = parser.parse_args()
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    print(json.dumps(run(args.server_root.resolve(), args.server_repository.resolve()), indent=2))
