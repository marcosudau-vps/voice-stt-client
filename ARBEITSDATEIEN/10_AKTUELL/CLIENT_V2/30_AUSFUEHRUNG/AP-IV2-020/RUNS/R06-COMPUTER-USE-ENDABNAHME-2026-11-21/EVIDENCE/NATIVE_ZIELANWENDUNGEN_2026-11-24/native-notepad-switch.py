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
report={'scope':'real native Qt desktop from corrected source, real pinned V2 TLS server, isolated test profile, real pinned V2 acoustic input, guarded production clipboard/SendInput to owned Notepad then Qt editor; no global hotkeys','start':datetime.now().astimezone().isoformat(),'checks':{},'evidenceFolder':folder.name}
def save():
    (root/'native-notepad-switch.json').write_text(json.dumps(report,indent=2),encoding='utf8')
def check(n,v):
    report['checks'][n]=bool(v);save();print(n,bool(v),flush=True)
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
cursor_before=digest(DEFAULT_CURSOR_PATH)
config=AppConfig._load_single(DEFAULT_CONFIG_PATH)
config.server.url='wss://final.v2.voice-stt-server.marcosudau.com/ws/v2'
config.server.health_url='https://final.v2.voice-stt-server.marcosudau.com/health'
config.audio.device=next(i for i,x in enumerate(sd.query_devices()) if 'respeaker' in x['name'].casefold() and x['max_input_channels']>0)
config.overlay.enabled=True;config.overlay.show_realtime_text=True
config.led.enabled=False
config.feedback.sounds_enabled=False
config.event_stream.enabled=False
config.event_stream.cursor_persistence_enabled=False
config.history.persistent.db_path=str(folder/'history.sqlite')
config.history.persistent.store_all=True
config.history.memory.max_entries=100
config.clipboard.restore_previous=True
config.text_injection.append_space=False
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
import ctypes,subprocess,base64
from ctypes import wintypes
from voice_stt_client.core.text_injector import CtypesWindowsInjectionBackend
from PySide6.QtWidgets import QPlainTextEdit
app=QApplication([])
class Guard(CtypesWindowsInjectionBackend):
    def __init__(self):
        super().__init__();self.target=None;self.sent=0
    def send_input_keyboard(self,events):
        if self.get_foreground_window()!=self.target:raise RuntimeError('Owned target not foreground')
        n=super().send_input_keyboard(events);self.sent+=1;return n
    def empty_clipboard(self):
        if self.get_foreground_window()!=self.target:raise RuntimeError('Owned target lost focus')
        return super().empty_clipboard()
backend=Guard()
npid=47048;nhwnd=465546
user=backend.user32
user.SetForegroundWindow.argtypes=[wintypes.HWND];user.SetForegroundWindow.restype=wintypes.BOOL
user.IsWindow.argtypes=[wintypes.HWND];user.IsWindow.restype=wintypes.BOOL
editor=QPlainTextEdit();editor.setWindowTitle('R06 – isolated second target');editor.resize(600,240)
def notepad(mode):
    cmd=r"""Add-Type -AssemblyName UIAutomationClient,UIAutomationTypes
$p=Get-Process -Id 47048 -ErrorAction Stop
if($p.MainWindowHandle -ne 465546 -or $p.MainWindowTitle -notlike '*R06-Notepad-Disposable*'){throw 'Not owned'}
$root=[System.Windows.Automation.AutomationElement]::FromHandle($p.MainWindowHandle)
$cond=New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty,[System.Windows.Automation.ControlType]::Document)
$e=$root.FindFirst([System.Windows.Automation.TreeScope]::Descendants,$cond)
if(!$e){throw 'No document'}
"""
    if mode=='focus':cmd+='$e.SetFocus()'
    else:cmd+='$v=$e.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value; [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($v))'
    p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',cmd],capture_output=True,text=True,timeout=8,creationflags=0x08000000)
    if p.returncode:raise RuntimeError('Notepad UI Automation failed')
    return base64.b64decode(p.stdout.strip()).decode('utf8') if mode=='read' else None

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
        import asyncio
        mime=app.clipboard().mimeData()
        if mime and any(f not in ('text/plain','text/plain;charset=utf-8') for f in mime.formats()):raise RuntimeError('Rich clipboard preserved')
        original=mime.text() if mime else ''
        check('notepad_owned',user.IsWindow(nhwnd) and backend.get_window_thread_process_id(nhwnd)[1]==npid and notepad('read')=='')
        if not report['checks']['notepad_owned']:raise RuntimeError('Notepad ownership not confirmed')
        def focus(hwnd):
            backend.target=hwnd;user.SetForegroundWindow(hwnd)
            wait(lambda:backend.get_foreground_window()==hwnd,5)
        def dictate(name,hwnd,reader,tokens):
            n=backend.sent
            wait(lambda:runtime.is_ready and runtime.media.audio_available and runtime.mirror.mirror.view.manual_available and desktop.bridge._published_view is not None and desktop.bridge._published_view.mirror.manual_available,15)
            if hwnd==nhwnd:notepad('focus')
            focus(hwnd)
            assert desktop.bridge.press_control('primary')
            wait(lambda:bool(runtime.mirror.mirror.view.input.activation_id),10)
            aid=runtime.mirror.mirror.view.input.activation_id
            start=time.monotonic()
            while time.monotonic()-start<.8:app.processEvents();time.sleep(.02)
            fixture=root.parent/'autonome-restpruefung-2026-11-23'/'fixtures'/(name+'.wav')
            winsound.PlaySound(str(fixture),winsound.SND_FILENAME|winsound.SND_ASYNC|winsound.SND_NODEFAULT)
            start=time.monotonic()
            while time.monotonic()-start<4.2:
                app.processEvents()
                if backend.get_foreground_window()!=hwnd:
                    future=asyncio.run_coroutine_threadsafe(runtime.cancel_dictation(),desktop.bridge._loop)
                    wait(lambda:future.done(),5);raise RuntimeError('Target lost focus')
                time.sleep(.02)
            if runtime.mirror.mirror.view.input.activation_id==aid:
                future=asyncio.run_coroutine_threadsafe(runtime.stop_dictation(),desktop.bridge._loop)
                wait(lambda:future.done())
            wait(lambda:runtime.mirror.mirror.view.input.activation_id is None,15)
            wait(lambda:backend.sent>n,20)
            entries=[e for e in runtime.history.get_memory_entries() if e.activation_id==aid]
            wait(lambda:bool(entries),5)
            start=time.monotonic()
            while time.monotonic()-start<1:app.processEvents();time.sleep(.02)
            observed=reader()
            expected=''.join(e.text for e in entries)
            check(name+'_exact_native_paste',len(entries)==1 and observed==expected and backend.sent-n==1)
            check(name+'_markers',all(t in expected.casefold() for t in tokens))
            check(name+'_clipboard_restored',app.clipboard().text()==original)
            if observed!=expected:raise RuntimeError('Native paste not exact')
            return observed
        first=dictate('kurz-01',nhwnd,lambda:notepad('read'),('blau','bahnhof'))
        editor.show();editor.activateWindow();editor.setFocus();app.processEvents()
        second=dictate('kurz-02',int(editor.winId()),editor.toPlainText,('zitron','tisch'))
        check('first_target_unchanged_after_switch',notepad('read')==first)
        check('distinct_targets',first!=second)
        editor.close()
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
