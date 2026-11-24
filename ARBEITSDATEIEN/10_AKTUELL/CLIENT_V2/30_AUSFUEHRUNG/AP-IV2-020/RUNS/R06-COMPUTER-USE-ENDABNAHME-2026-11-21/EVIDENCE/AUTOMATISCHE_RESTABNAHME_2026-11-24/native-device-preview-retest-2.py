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
import winsound, sounddevice as sd
from PySide6.QtCore import Qt
from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.ui.v2_application import V2DesktopApplication
from voice_stt_client.ui.single_instance import SingleInstanceGuard
from voice_stt_client.core.event_cursor_store import DEFAULT_CURSOR_PATH,EventCursorStore
report={'scope':'real native Qt desktop from corrected source, real pinned V2 TLS server, isolated test profile, real native Qt UI, real acoustic ReSpeaker input, pinned V2, mock injection, no global hotkeys','start':datetime.now().astimezone().isoformat(),'checks':{},'evidenceFolder':folder.name}
def save():
    (root/'native-device-preview-retest-2.json').write_text(json.dumps(report,indent=2),encoding='utf8')
def check(n,v):
    report['checks'][n]=bool(v);save();print(n,bool(v),flush=True)
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
cursor_before=digest(DEFAULT_CURSOR_PATH)
config=AppConfig._load_single(DEFAULT_CONFIG_PATH)
config.server.url='wss://final.v2.voice-stt-server.marcosudau.com/ws/v2'
config.server.health_url='https://final.v2.voice-stt-server.marcosudau.com/health'
config.audio.device=2147483647
config.overlay.enabled=True;config.overlay.show_realtime_text=True
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
        check('no_audio_no_hotkeys',not runtime.audio.is_running and not desktop.hotkeys._registered_ids)
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
        check('invalid_audio_retained_and_no_capture',local._editors['audio.device'].currentData()==2147483647 and not runtime.audio.is_running)
        local.close()
        d.close()
        local.show();app.processEvents()
        device=next(i for i,x in enumerate(sd.query_devices()) if 'respeaker' in x['name'].casefold() and x['max_input_channels']>0)
        audio_editor=local._editors['audio.device']
        wait(lambda:audio_editor.findData(device)>=0,10)
        audio_editor.setCurrentIndex(audio_editor.findData(device))
        local.apply_changes()
        wait(lambda:desktop._pending_config is None and runtime.config.audio.device==device,15)
        wait(lambda:runtime.media.audio_available and runtime.audio.is_running,20)
        check('invalid_to_real_device_gui_recovery',runtime.config.audio.device==device and runtime.audio.is_running)
        local.close()
        def dictate(name,tokens):
            n=len(backend.send_input_calls);previews=[]
            wait(lambda:runtime.is_ready and runtime.media.audio_available and runtime.mirror.mirror.view.manual_available and desktop.bridge._published_view is not None and desktop.bridge._published_view.mirror.manual_available,15)
            report['before_'+name]={'ready':runtime.is_ready,'manualAvailable':runtime.mirror.mirror.view.manual_available,'reportedAvailable':bool(runtime.media._reported_available and runtime.media._reported_available[1])}
            assert desktop.bridge.press_control('primary')
            wait(lambda:bool(runtime.mirror.mirror.view.input.activation_id))
            aid=runtime.mirror.mirror.view.input.activation_id
            start=time.monotonic()
            while time.monotonic()-start<.65:app.processEvents();time.sleep(.02)
            fixture=root.parent/'autonome-restpruefung-2026-11-23'/'fixtures'/(name+'.wav')
            winsound.PlaySound(str(fixture),winsound.SND_FILENAME|winsound.SND_ASYNC|winsound.SND_NODEFAULT)
            start=time.monotonic()
            while time.monotonic()-start<4.1:
                app.processEvents()
                text=desktop.overlay.label.text()
                if desktop.overlay.isVisible() and text and text not in previews and len(backend.send_input_calls)==n:previews.append(text)
                time.sleep(.025)
            if runtime.mirror.mirror.view.input.activation_id==aid:
                import asyncio
                future=asyncio.run_coroutine_threadsafe(runtime.stop_dictation(),desktop.bridge._loop)
                wait(lambda:future.done())
            wait(lambda:runtime.mirror.mirror.view.input.activation_id is None,15)
            wait(lambda:len(backend.send_input_calls)>n,30)
            entries=[e for e in runtime.history.get_memory_entries() if e.activation_id==aid]
            report[name]={'previewCount':len(previews),'previewMarkerMatch':any(any(t in p.casefold() for t in tokens) for p in previews),'finalCount':len(entries),'injectionCount':len(backend.send_input_calls)-n}
            check(name+'_one_final',len(entries)==1 and len(backend.send_input_calls)-n==1 and any(all(t in e.text.casefold() for t in tokens) for e in entries))
            check(name+'_preview_before_injection',report[name]['previewMarkerMatch'])
        dictate('kurz-01',('blau','bahnhof'))
        local.show();app.processEvents()
        audio_editor=local._editors['audio.device']
        idx=audio_editor.findData(None)
        if idx<0:raise RuntimeError('Default audio item absent')
        audio_editor.setCurrentIndex(idx)
        local.apply_changes()
        wait(lambda:desktop._pending_config is None and runtime.config.audio.device is None,15)
        wait(lambda:runtime.media.audio_available and runtime.audio.is_running,20)
        check('device_switch_to_system_default',runtime.config.audio.device is None and runtime.audio.is_running)
        local.close()
        dictate('kurz-02',('zitron','tisch'))
        check('device_persisted',AppConfig.load(folder/'profile.yaml').audio.device is None)
        store=EventCursorStore()
        check('isolated_cursor_path',store.path==folder/'client'/'data'/'event_cursor.json')
    except Exception as exc:
        if desktop and desktop.bridge._controller:
            rt=desktop.bridge._controller
            v=rt.mirror.mirror.view
            report['failureContext']={'ready':rt.is_ready,'audioAvailable':rt.media.audio_available,'manualAvailable':v.manual_available,'reportedAvailable':bool(rt.media._reported_available and rt.media._reported_available[1]),'transport':rt.session.status.state.value,'trigger':dict(v.trigger),'phase':str(v.input.phase)}
        report['errorType']=type(exc).__name__
        report['error']=str(exc)
        traceback.print_exc()
    finally:
        if desktop is not None:
            desktop.tray.quit_action.trigger()
        else:app.quit()
QTimer.singleShot(0,run)
app.exec()
if desktop:
    desktop.shutdown()
    check('shutdown_core_tray',not desktop.bridge.is_running and not desktop.tray.tray.isVisible() and not desktop.hotkeys._registered_ids)
guard.release()
check('shared_cursor_unchanged',cursor_before==digest(DEFAULT_CURSOR_PATH))
report['end']=datetime.now().astimezone().isoformat()
report['result']='PASS_SCOPED' if report['checks'] and all(report['checks'].values()) and 'error' not in report else 'INCOMPLETE_OR_FAIL'
save()
print(report['result'],flush=True)