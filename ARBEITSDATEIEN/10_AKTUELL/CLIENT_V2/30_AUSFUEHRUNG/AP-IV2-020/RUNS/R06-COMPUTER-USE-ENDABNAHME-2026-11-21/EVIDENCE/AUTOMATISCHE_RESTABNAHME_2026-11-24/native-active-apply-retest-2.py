import os,sys,json,time,uuid,hashlib,traceback
from pathlib import Path
from datetime import datetime
from dataclasses import asdict,replace
root=Path(__file__).parent
folder=root/('native-desktop-'+uuid.uuid4().hex[:8])
folder.mkdir()
os.chdir(folder)
os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),VOICESTT_CLIENT_CONFIG=str(folder/'profile.yaml'),QT_QPA_PLATFORM='windows')
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QSystemTrayIcon,QMessageBox,QPushButton
from voice_stt_client.core.v2_runtime import V2Runtime
from voice_stt_client.ui.v2_core_bridge import V2CoreBridge
from tests.test_text_injector import MockInjectionBackend
from voice_stt_client.core.history import TranscriptHistoryManager
from copy import deepcopy
from unittest.mock import patch
from tests.manual.v2.endurance_probe import ReplayStream,devices
from voice_stt_client.ui.v2_settings_dialog import ApplyDecisionDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtCore import Qt
import numpy as np
from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.ui.v2_application import V2DesktopApplication
from voice_stt_client.ui.single_instance import SingleInstanceGuard
from voice_stt_client.core.event_cursor_store import DEFAULT_CURSOR_PATH,EventCursorStore
report={'scope':'real native Qt desktop from corrected source, real pinned V2 TLS server, isolated test profile, real native Qt and real server with controlled synthetic PortAudio, mock injection, isolated profile; no OS hotkeys','start':datetime.now().astimezone().isoformat(),'checks':{},'evidenceFolder':folder.name}
def save():
    (root/'native-active-apply-retest-2.json').write_text(json.dumps(report,indent=2),encoding='utf8')
def check(n,v):
    report['checks'][n]=bool(v);save();print(n,bool(v),flush=True)
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
cursor_before=digest(DEFAULT_CURSOR_PATH)
config=AppConfig._load_single(DEFAULT_CONFIG_PATH)
config.server.url='wss://final.v2.voice-stt-server.marcosudau.com/ws/v2'
config.server.health_url='https://final.v2.voice-stt-server.marcosudau.com/health'
config.audio.device=0
config.audio.sample_rate=16000;config.audio.channels=1;config.audio.chunk_duration_ms=40
config.led.enabled=False
config.feedback.sounds_enabled=False
config.event_stream.enabled=False
config.event_stream.cursor_persistence_enabled=False
config.history.persistent.db_path=str(folder/'history.sqlite')
config.history.persistent.store_all=True
config.history.memory.max_entries=100
config.clipboard.restore_previous=False
config.logging.log_dir=str(folder/'logs')
config.logging.observability.store_transcription_content=False
config.logging.observability.store_raw_payload=False
profile=V2Profile()
profile.controls['enabled']=False
config.v2_profile=asdict(profile)
config.save(folder/'profile.yaml')
config=AppConfig.load(folder/'profile.yaml')
seed=TranscriptHistoryManager(config.history)
entries=[seed.add_entry_with_status('r06-synthetic',i,f'R06 synthetic test {i}').entry for i in range(1,4)]
assert all(entries)
backend=MockInjectionBackend()
app=QApplication([])
app.setQuitOnLastWindowClosed(False)
app.setOrganizationName('R06-Test')
app.setApplicationName('R06-Isolated-Desktop')
guard=SingleInstanceGuard('Local\\CV2_R06_'+uuid.uuid4().hex)
desktop=None
def wait(fn,limit=25):
    end=time.monotonic()+limit
    while time.monotonic()<end:
        app.processEvents()
        if fn():return
        time.sleep(.02)
    raise TimeoutError('Condition not met')
def run():
    global desktop
    try:
        assert guard.acquire().acquired
        bridge=V2CoreBridge(config,runtime_factory=lambda cfg:V2Runtime(cfg,backend=backend))
        desktop=V2DesktopApplication(app,config,guard,bridge=bridge)
        assert desktop.start()
        wait(lambda:desktop._runtime_ready,40)
        runtime=desktop.bridge._controller
        identity=runtime.session.binding.accepted.payload['serverCommit']
        check('server_identity',identity=='e95858e3c010a7e9324b49bb44fee349abe7128a')
        wait(lambda:runtime.media.audio_available)
        check('replay_audio_no_hotkeys',runtime.media.audio_available and not desktop.hotkeys._registered_ids)
        check('tray_available_and_visible',QSystemTrayIcon.isSystemTrayAvailable() and desktop.tray.tray.isVisible())
        check('tray_tooltip_and_menu',bool(desktop.tray.tray.toolTip()) and desktop.tray.settings_action in desktop.tray.menu.actions() and desktop.tray.quit_action in desktop.tray.menu.actions())
        desktop.tray.settings_action.trigger()
        wait(lambda:desktop.settings_dialog is not None and desktop.settings_dialog._view is not None)
        d=desktop.settings_dialog
        wait(lambda:d._view.connected_ready)
        check('native_settings_tabs',d.isVisible() and d.tabs.count()==3)
        d._local_dialog if hasattr(d,'_local_dialog') else None
        local=desktop._local_dialog
        local.show();app.processEvents()
        check('native_local_tabs',local.isVisible() and local.tabs.count()==5)
        local.close()
        d.timer.start()
        def view():return runtime.mirror.mirror.view
        def activate():
            assert desktop.bridge.press_control('primary')
            wait(lambda:bool(view().input.activation_id),10)
            aid=view().input.activation_id
            wait(lambda:d._view.context.activation_id==aid,10)
            return aid
        def select_wake(enabled):
            d.wake.setChecked(enabled)
            for i in range(d.wake_list.count()):
                item=d.wake_list.item(i)
                item.setCheckState(Qt.CheckState.Checked if enabled and item.data(Qt.ItemDataRole.UserRole)=='hey_jarvis' else Qt.CheckState.Unchecked)
        def apply_decision(index):
            found=[]
            def choose():
                dialog=app.activeModalWidget()
                if isinstance(dialog,ApplyDecisionDialog):
                    found.append(not dialog.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
                    if index==0:dialog.reject()
                    else:
                        dialog.choice.setCurrentIndex(index)
                        dialog.drain.setCurrentIndex(1)
                        dialog.buttons.button(QDialogButtonBox.StandardButton.Ok).click()
            QTimer.singleShot(150,choose)
            d.apply_profile_button.click()
            if not found:raise RuntimeError('Decision modal missing')
            return found[0]
        def ready_generation(g):
            wait(lambda:runtime.is_ready and runtime.session.generation>g and d._view.connected_ready and d._view.context.generation==runtime.session.generation,25)
        aid=activate();g=runtime.session.generation
        select_wake(True)
        before=digest(folder/'profile.yaml')
        check('no_decision_default',apply_decision(0))
        check('modal_cancel_preserves_input_profile',view().input.activation_id==aid and digest(folder/'profile.yaml')==before and runtime.session.generation==g)
        check('defer_choice_present',apply_decision(3))
        wait(lambda:runtime.settings.profile.wake_word)
        check('defer_preserves_active_input_and_connection',view().input.activation_id==aid and runtime.session.generation==g and not view().trigger['configured']['wakeWord'])
        # Explicitly choose cancel on the same current input.
        wait(lambda:d._view.profile['wake_word'])
        select_wake(True)
        check('cancel_choice_present',apply_decision(1))
        ready_generation(g)
        check('cancel_reconnect_hybrid',view().input.activation_id is None and view().trigger['configured']['wakeWord'] and len(backend.send_input_calls)==0)
        # Finish an open, deliberately silent activation while returning to manual only.
        aid=activate();g=runtime.session.generation
        select_wake(False)
        check('finish_choice_present',apply_decision(2))
        ready_generation(g)
        check('finish_reconnect_manual',view().input.activation_id is None and view().trigger['configured']['manual'] and not view().trigger['configured']['wakeWord'])
        check('saved_trigger_matches_runtime',not AppConfig.load(folder/'profile.yaml').v2_profile['wake_word'])
        d.close()
        store=EventCursorStore()
        check('isolated_cursor_path',store.path==folder/'client'/'data'/'event_cursor.json')
    except Exception as exc:
        if desktop and desktop.bridge._controller:
            rr=desktop.bridge._controller
            report['failureContext']={'generation':rr.session.generation,'transport':rr.session.status.state.value,'ready':rr.is_ready,'dialogStatus':desktop.settings_dialog.status.text() if desktop.settings_dialog else None,'activation':rr.mirror.mirror.view.input.activation_id}
        report['errorType']=type(exc).__name__
        report['error']=str(exc)
        traceback.print_exc()
    finally:
        if desktop is not None:
            desktop.tray.quit_action.trigger()
        else:app.quit()
patches=[patch('sounddevice.InputStream',ReplayStream),patch('sounddevice.query_devices',devices),patch('sounddevice.check_input_settings',lambda **kw:None)]
for p in patches:p.start()
feed=QTimer();feed.setInterval(40)
def feed_silence():
    stream=ReplayStream.latest
    if stream and stream.active:stream.callback(np.zeros((640,1),dtype=np.int16),640,None,None)
feed.timeout.connect(feed_silence);feed.start()
QTimer.singleShot(0,run)
app.exec()
if desktop:
    desktop.shutdown()
    check('shutdown_core_tray',not desktop.bridge.is_running and not desktop.tray.tray.isVisible() and not desktop.hotkeys._registered_ids)
guard.release()
for p in reversed(patches):p.stop()
check('shared_cursor_unchanged',cursor_before==digest(DEFAULT_CURSOR_PATH))
report['end']=datetime.now().astimezone().isoformat()
report['result']='PASS_SCOPED' if report['checks'] and all(report['checks'].values()) and 'error' not in report else 'INCOMPLETE_OR_FAIL'
save()
print(report['result'],flush=True)