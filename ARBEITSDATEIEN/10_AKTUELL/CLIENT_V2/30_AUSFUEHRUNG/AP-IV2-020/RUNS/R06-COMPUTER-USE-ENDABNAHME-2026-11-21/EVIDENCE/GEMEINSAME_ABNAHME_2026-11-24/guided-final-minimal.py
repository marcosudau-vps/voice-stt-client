import os,sys,uuid,hashlib,json,subprocess,time,sqlite3,ctypes,winsound
from ctypes import wintypes
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
root=Path(__file__).parent
folder=root/('guided-final-'+uuid.uuid4().hex[:8])
folder.mkdir();(folder/'tmp').mkdir()
os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),VOICESTT_CLIENT_CONFIG=str(folder/'profile.yaml'),TEMP=str(folder/'tmp'),TMP=str(folder/'tmp'),QT_QPA_PLATFORM='windows')
from PySide6.QtCore import QTimer,QMimeData,Qt
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QLabel,QPushButton,QPlainTextEdit
from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.core.text_injector import CtypesWindowsInjectionBackend
from voice_stt_client.core.event_cursor_store import DEFAULT_CURSOR_PATH
import sounddevice as sd
exe=Path(r'P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\v2-final-automatik-nachweise-20261121')/'dist-r06-korrektur-lokal-20261123'/'voice-stt-client.exe'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
assert digest(exe)=='07cab945a8ca568f7a500a62a013a852e60e38a95a919b677453898539a205fe'
cfg=AppConfig._load_single(DEFAULT_CONFIG_PATH)
cfg.server.url='wss://final.v2.voice-stt-server.marcosudau.com/ws/v2'
cfg.server.health_url='https://final.v2.voice-stt-server.marcosudau.com/health'
cfg.audio.device=next(i for i,d in enumerate(sd.query_devices()) if 'respeaker' in d['name'].casefold() and d['max_input_channels']>0)
cfg.audio.sample_rate=16000;cfg.audio.channels=1
cfg.led.enabled=True;cfg.feedback.sounds_enabled=True;cfg.overlay.enabled=True;cfg.overlay.show_realtime_text=True
cfg.event_stream.enabled=False;cfg.event_stream.cursor_persistence_enabled=False
cfg.hotkey.auto_start=False;cfg.clipboard.restore_previous=True
cfg.history.persistent.db_path=str(folder/'history.sqlite');cfg.history.persistent.store_all=True
cfg.logging.log_dir=str(folder/'logs');cfg.logging.observability.db_path=str(folder/'observability.sqlite3')
cfg.logging.observability.store_transcription_content=False;cfg.logging.observability.store_raw_payload=False
profile=V2Profile(manual=True,wake_word=True,wake_word_ids=['hey_jarvis'],desired_settings={'activation.followupTimeoutMs':5000})
profile.controls.update(primary_key='Ctrl+Shift+F8',primary_action='cancel',secondary_key='Ctrl+Shift+F9',secondary_action='finish',wake_pause_key='Ctrl+Shift+F10',reinsert_last_key='Ctrl+Shift+F11',overlay_toggle_key='Ctrl+Shift+F12')
cfg.v2_profile=asdict(profile);cfg.save(folder/'profile.yaml')
cursor_before=digest(DEFAULT_CURSOR_PATH)
app=QApplication([]);window=QWidget();window.setWindowTitle('R06 – kurze gemeinsame Endabnahme')
layout=QVBoxLayout(window);label=QLabel('Einmal Start klicken. Danach bitte im Testfenster bleiben.');label.setWordWrap(True);label.setStyleSheet('font-size:20px;padding:10px;font-weight:bold;');layout.addWidget(label)
helptext=QLabel('LED-Ring und Töne beobachten. Testaudio läuft automatisch. Nur bei der ausdrücklichen Aufforderung einmal selbst sprechen.');helptext.setWordWrap(True);layout.addWidget(helptext)
editor=QPlainTextEdit();editor.setPlaceholderText('Hier erscheinen ausschließlich Testdiktate.');layout.addWidget(editor)
start=QPushButton('Start – kurze Abnahme');layout.addWidget(start)
stop=QPushButton('Abbrechen / Test beenden');layout.addWidget(stop)
window.resize(800,400);window.show();window.raise_();window.activateWindow()
backend=CtypesWindowsInjectionBackend()
user=ctypes.WinDLL('user32',use_last_error=True)
user.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)];user.GetWindowThreadProcessId.restype=wintypes.DWORD
user.PostThreadMessageW.argtypes=[wintypes.DWORD,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM];user.PostThreadMessageW.restype=wintypes.BOOL
WINFUNC=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
user.EnumWindows.argtypes=[WINFUNC,wintypes.LPARAM];user.GetClassNameW.argtypes=[wintypes.HWND,wintypes.LPWSTR,ctypes.c_int]
r=dict(scope='corrected frozen EXE, real speaker/mic, native hotkeys and paste into owned editor, guided LED/audio observations',folder=str(folder),exeSha256=digest(exe),result='WAITING_FOR_START',checks={},stages=[])
out=root/'guided-final-current.json'
child=None;pid=None;stage='waiting';since=time.monotonic();began=since;history=[];original=None;original_plain=None;oldseq=None;formats=[];base_count=0;base_text='';starts_before=0;close_before=0;quit_requested=False
fixtures=root.parent/'autonome-restpruefung-2026-11-23'/'fixtures'
def save():
    t=out.with_suffix('.tmp');t.write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf8')
    try:t.replace(out)
    except PermissionError:pass
def setstage(name,text):
    global stage,since
    stage=name;since=time.monotonic();label.setText(text);r['stage']=name;r['stages'].append(dict(stage=name,seconds=round(since-began,2)));save()
def own():return backend.get_window_thread_process_id(backend.get_foreground_window())[1]==os.getpid()
def impulse(key):
    if not own() or backend.get_pressed_modifiers():raise RuntimeError('Test target not safe for hotkey')
    events=[(0x11,False),(0x10,False),(key,False),(key,True),(0x10,True),(0x11,True)]
    if backend.send_input_keyboard(events)!=6:raise RuntimeError('hotkey stimulus incomplete')
def read(db,sql):
    try:
        with sqlite3.connect(db.as_uri()+'?mode=ro',uri=True,timeout=.1) as c:return c.execute(sql).fetchall()
    except sqlite3.Error:return []
def play(n):winsound.PlaySound(str(fixtures/(n+'.wav')),winsound.SND_FILENAME|winsound.SND_ASYNC|winsound.SND_NODEFAULT)
def quit_client():
    global quit_requested
    if not child or child.poll() is not None:return
    if not pid:return
    threads=set()
    @WINFUNC
    def cb(h,_):
        owner=wintypes.DWORD();thread=user.GetWindowThreadProcessId(h,ctypes.byref(owner))
        if owner.value==pid:
            name=ctypes.create_unicode_buffer(256);user.GetClassNameW(h,name,256)
            if name.value.startswith('Qt'):threads.add(thread)
        return True
    user.EnumWindows(cb,0)
    if len(threads)==1:quit_requested=bool(user.PostThreadMessageW(next(iter(threads)),0x12,0,0))
def begin():
    global child,original,original_plain,oldseq,began
    if child or not own():return
    # Capture existing clipboard formats only in memory; do not store them.
    mime=app.clipboard().mimeData();original=QMimeData()
    if mime:
        for fmt in mime.formats():
            data=mime.data(fmt)
            if len(data)>64*1024*1024:label.setText('Zwischenablage zu groß; Test nicht gestartet.');return
            original.setData(fmt,data);formats.append(fmt)
        original_plain=mime.text()
    oldseq=backend.get_clipboard_sequence_number()
    began=time.monotonic()
    start.setEnabled(False);editor.setFocus()
    child=subprocess.Popen([str(exe),'--config',str(folder/'profile.yaml')],cwd=folder,env=os.environ.copy())
    r['bootloaderPid']=child.pid;r['result']='RUNNING';setstage('ready','Client startet – LED und Töne beobachten.')
def finish(reason):
    r['result']=reason
    winsound.PlaySound(None,0)
    quit_client();setstage('shutdown','Test beendet. Client wird geschlossen.')
def tick():
    global pid,history,base_count,base_text,starts_before,close_before
    if stage=='waiting':
        if time.monotonic()-began>600:r['result']='NOT_STARTED';app.quit()
        return
    try:
        rows=read(folder/'observability.sqlite3','select type,details_json,activation_id from logs order by id')
        states=[];counts={}
        for typ,detail,aid in rows:
            d=json.loads(detail) if detail else {}
            if typ=='client.app.started':pid=d.get('process_id')
            if typ=='client.v2.transport_state':states.append(d.get('state'))
            if typ=='client.domain.observed':
                kind=d.get('eventType');counts[kind]=counts.get(kind,0)+1
        history=[t for (t,) in read(folder/'history.sqlite','select text from history_entries order by timestamp')]
        starts=counts.get('activation.started',0);closes=counts.get('activation.input_closed',0)
        r['status']=dict(states=states[-4:],counts=counts,historyEntries=len(history),editorCharacters=len(editor.toPlainText()),pid=pid,focused=own())
        elapsed=time.monotonic()-since
        if stage=='shutdown':
            if child.poll() is not None or elapsed>12:app.quit()
            return
        if not own():finish('ABORTED_TARGET_LOST_FOCUS');return
        if child.poll() is not None:finish('EARLY_CLIENT_EXIT');return
        if time.monotonic()-began>240:finish('TIMEOUT');return
        if stage=='ready' and states and states[-1]=='ready' and elapsed>5:
            base_count=len(history);base_text=editor.toPlainText();starts_before=starts
            impulse(0x77);setstage('manual_activate','Automatische Aufnahme – LED und Ton beobachten.')
        elif stage=='manual_activate' and starts>starts_before and elapsed>.7:
            play('kurz-01');setstage('manual_play','Automatisches Testdiktat läuft.')
        elif stage=='manual_play' and elapsed>4.3:
            impulse(0x78);setstage('manual_final','Abschluss – Text, LED und Ton beobachten.')
        elif stage=='manual_final' and len(history)>base_count and closes>0:
            expected=base_text+''.join(t if t[-1:].isspace() else t+' ' for t in history[base_count:])
            if editor.toPlainText()==expected:
                r['checks']['manual_native_paste']=len(history)==base_count+1
                r['checks']['manual_expected_markers']=all(t in history[-1].casefold() for t in ('blau','bahnhof'))
                setstage('manual_idle','Abschluss erfolgt – kurz den LED-Ring ansehen.')
        elif stage=='manual_idle' and elapsed>2.5:
            starts_before=starts;base_count=len(history);base_text=editor.toPlainText()
            impulse(0x77);setstage('cancel_start','Abbruchprobe – nicht sprechen.')
        elif stage=='cancel_start' and starts>starts_before and elapsed>1.4:
            close_before=closes;impulse(0x77);setstage('cancel_end','Abbruch – LED und Abbruchton beobachten.')
        elif stage=='cancel_end' and closes>close_before and elapsed>2:
            r['checks']['cancel_no_paste']=len(history)==base_count and editor.toPlainText()==base_text
            impulse(0x79);setstage('pause','Wake-Pause – LED/Anzeige beobachten.')
        elif stage=='pause' and elapsed>2.5:
            starts_before=starts;play('jarvis');setstage('pause_test','Automatische Wake-Negativprobe.')
        elif stage=='pause_test' and elapsed>5:
            r['checks']['pause_no_activation']=starts==starts_before and len(history)==base_count
            impulse(0x79);setstage('resume','Wake wieder aktiv – gleich folgt dein einziger Satz.')
        elif stage=='resume' and elapsed>3:
            starts_before=starts;close_before=closes;base_count=len(history);base_text=editor.toPlainText()
            setstage('human','JETZT EINMAL SPRECHEN:\nHey Jarvis, die grüne Lampe steht neben dem Fenster.\nDanach schweigen.')
        elif stage=='human' and len(history)>base_count and closes>close_before:
            expected=base_text+''.join(t if t[-1:].isspace() else t+' ' for t in history[base_count:])
            if editor.toPlainText()==expected:
                r['checks']['human_wake_activation']=starts==starts_before+1
                r['checks']['human_native_paste']=len(history)==base_count+1
                r['checks']['human_markers']=all(t in history[-1].casefold() for t in ('lampe','fenster'))
                finish('PASS_SCOPED' if all(r['checks'].values()) else 'COMPLETED_WITH_DEVIATION')
        elif elapsed>(45 if stage=='human' else 30):finish('STAGE_TIMEOUT_'+stage)
        save()
    except Exception as exc:
        r['errorType']=type(exc).__name__;finish('HARNESS_ERROR')
start.clicked.connect(begin);stop.clicked.connect(lambda:finish('OPERATOR_STOP') if child else app.quit())
timer=QTimer();timer.setInterval(80);timer.timeout.connect(tick);timer.start()
save();print('READY_FOR_CLICK',folder,flush=True)
try:app.exec()
finally:
    winsound.PlaySound(None,0)
    if child:
        quit_client()
        try:child.wait(12)
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],capture_output=True);child.wait(5);r['forcedCleanup']=True
        r['exitCode']=child.returncode;r['quitPosted']=quit_requested
        r['tempRemaining']=[x.name for x in (folder/'tmp').glob('_MEI*')]
    if original is not None and backend.get_clipboard_sequence_number()!=oldseq:
        mime=app.clipboard().mimeData();current=mime.text() if mime else None
        if current==original_plain or current in [v for t in history for v in (t,t+' ')]:
            app.clipboard().setMimeData(original);app.processEvents()
            r['clipboardFormatsRestored']=all(app.clipboard().mimeData().data(f)==original.data(f) for f in formats)
        else:r['clipboardRestoreSkippedExternalChange']=True
    r['sharedCursorUnchanged']=cursor_before==digest(DEFAULT_CURSOR_PATH)
    r['end']=datetime.now().astimezone().isoformat();save();print('DONE',r['result'],flush=True)
