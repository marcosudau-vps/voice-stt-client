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
from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.ui.v2_application import V2DesktopApplication
from voice_stt_client.ui.single_instance import SingleInstanceGuard
from voice_stt_client.core.event_cursor_store import DEFAULT_CURSOR_PATH,EventCursorStore
report={'scope':'real native Qt desktop from corrected source, real pinned V2 TLS server, isolated test profile, no microphone or global hotkeys; synthetic isolated history and mock injection','start':datetime.now().astimezone().isoformat(),'checks':{},'evidenceFolder':folder.name}
def save():
    (root/'native-invalid-endpoint-retest.json').write_text(json.dumps(report,indent=2),encoding='utf8')
def check(n,v):
    report['checks'][n]=bool(v);save();print(n,bool(v),flush=True)
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
cursor_before=digest(DEFAULT_CURSOR_PATH)
config=AppConfig._load_single(DEFAULT_CONFIG_PATH)
config.server.url='wss://final.v2.voice-stt-server.marcosudau.com/ws/invalid-r06'
config.server.health_url='https://final.v2.voice-stt-server.marcosudau.com/health'
config.audio.device=2147483647
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
        runtime=desktop.bridge._controller
        wait(lambda:desktop.bridge._controller is not None,10)
        runtime=desktop.bridge._controller
        wait(lambda:runtime.session.status.state.value=='blocked',10)
        check('invalid_endpoint_blocked',runtime.session.status.state.value=='blocked' and runtime.session.generation==0)
        check('no_binding_no_audio',runtime.session.binding is None and not runtime.audio.is_running)
        check('tray_configuration_message',desktop.tray.status_action.text()=='Konfiguration pr\u00fcfen')
        report['trayTooltip']=desktop.tray.tray.toolTip()
        check('tray_toggle_disabled',not desktop.tray.toggle_action.isEnabled())
        desktop.tray.settings_action.trigger()
        wait(lambda:desktop.settings_dialog is not None)
        d=desktop.settings_dialog
        app.processEvents()
        report['settingsStatus']=d.status.text()
        check('settings_still_accessible',d.isVisible())
        check('profile_unchanged',AppConfig.load(folder/'profile.yaml').server.url.endswith('/ws/invalid-r06'))
    except Exception as exc:
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