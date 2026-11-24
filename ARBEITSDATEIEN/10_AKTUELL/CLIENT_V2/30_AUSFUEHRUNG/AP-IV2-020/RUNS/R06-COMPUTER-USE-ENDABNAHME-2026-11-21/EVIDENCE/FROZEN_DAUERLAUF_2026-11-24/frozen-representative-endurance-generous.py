import os,sys,uuid,hashlib,json,subprocess,time,sqlite3,ctypes,winsound,argparse,urllib.request,wave
from ctypes import wintypes
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
root=Path(__file__).parent
parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=int,default=1800);parser.add_argument('--auto',action='store_true');args=parser.parse_args()
folder=root/('frozen-endurance-'+uuid.uuid4().hex[:8])
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
profile=V2Profile(manual=True,wake_word=False,wake_word_ids=[],desired_settings={'activation.initialSpeechTimeoutMs':15000,'activation.followupTimeoutMs':10000})
profile.controls.update(enabled=True,primary_key='Ctrl+Alt+Shift+F8',primary_action='cancel',secondary_key='Ctrl+Alt+Shift+F9',secondary_action='finish',wake_pause_key='',reinsert_last_key='',overlay_toggle_key='')
cfg.v2_profile=asdict(profile);cfg.save(folder/'profile.yaml')
cursor_before=digest(DEFAULT_CURSOR_PATH)
app=QApplication([]);window=QWidget();window.setWindowTitle('R06 – EXE-Dauerlauf mit verlängerten Timeouts')
layout=QVBoxLayout(window);label=QLabel('Start klicken, dann das Testfenster im Vordergrund lassen. Keine Sprachprobe nötig.');label.setWordWrap(True);label.setStyleSheet('font-size:20px;padding:10px;font-weight:bold;');layout.addWidget(label)
helptext=QLabel('Automatische Diktate, Ressourcenmessung und Verbindungsprüfung. Bei Fokusverlust wird der Test abgebrochen. Beenden jederzeit möglich.');helptext.setWordWrap(True);layout.addWidget(helptext)
editor=QPlainTextEdit();editor.setPlaceholderText('Hier erscheinen ausschließlich Testdiktate.');layout.addWidget(editor)
start=QPushButton('Dauerlauf starten');layout.addWidget(start)
stop=QPushButton('Abbrechen / Test beenden');layout.addWidget(stop)
window.resize(800,400);window.show();window.raise_();window.activateWindow()
backend=CtypesWindowsInjectionBackend()
user=ctypes.WinDLL('user32',use_last_error=True)
user.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)];user.GetWindowThreadProcessId.restype=wintypes.DWORD
user.PostThreadMessageW.argtypes=[wintypes.DWORD,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM];user.PostThreadMessageW.restype=wintypes.BOOL
WINFUNC=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
user.EnumWindows.argtypes=[WINFUNC,wintypes.LPARAM];user.GetClassNameW.argtypes=[wintypes.HWND,wintypes.LPWSTR,ctypes.c_int]
r=dict(scope='corrected frozen EXE, real speaker/mic, native hotkeys and paste into owned editor, automated timed endurance, no operator speech',folder=str(folder),exeSha256=digest(exe),result='WAITING_FOR_START',checks={},stages=[])
out=root/('frozen-endurance-'+str(args.seconds)+'s-generous.json')
r.update(targetSeconds=args.seconds,cases=[],samples=[],missedTrials=[],timeouts=dict(initialSpeechMs=15000,followupMs=10000,startSeconds=120,activationSeconds=30,finalSeconds=120,maximumNoSpeechRetries=2))
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
    events=[(0x11,False),(0x12,False),(0x10,False),(key,False),(key,True),(0x10,True),(0x12,True),(0x11,True)]
    if backend.send_input_keyboard(events)!=8:raise RuntimeError('hotkey stimulus incomplete')
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

# Bounded measurement; never start recording before the owned editor has focus.
kernel=ctypes.WinDLL('kernel32',use_last_error=True);psapi=ctypes.WinDLL('psapi',use_last_error=True)
class PMC(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]
kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
kernel.CloseHandle.argtypes=[wintypes.HANDLE]
kernel.GetProcessTimes.argtypes=[wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4
psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(PMC),wintypes.DWORD]
def sample(pid):
    h=kernel.OpenProcess(0x1000|0x10,False,pid)
    if not h:return None
    try:
        m=PMC();m.cb=ctypes.sizeof(m);times=[wintypes.FILETIME() for _ in range(4)]
        if not psapi.GetProcessMemoryInfo(h,ctypes.byref(m),m.cb) or not kernel.GetProcessTimes(h,*[ctypes.byref(x) for x in times]):return None
        cpu=sum((x.dwHighDateTime<<32|x.dwLowDateTime)/1e7 for x in times[2:])
        return dict(privateMiB=round(m.PrivateUsage/2**20,3),workingMiB=round(m.WorkingSetSize/2**20,3),cpuSeconds=cpu)
    finally:kernel.CloseHandle(h)
tokens=[('blau','bahnhof'),('zitron','tisch'),('bibliothek','neun'),('garten','tulpen'),('fahrrad','garage'),('katze','sofa'),('hund','wiese'),('fenster','offen'),('apfelkuchen',),('bus','rathaus')]
ready_at=None;last_sample=0;next_trial=0;trial=0;attempt=0;cmd_before=0;target_count=max(2,args.seconds//90);trial_case=None;original_plain=None;no_speech_retries=0;play_seconds=0;segments_before=0
def read_identity():
    with urllib.request.urlopen('https://final.v2.voice-stt-server.marcosudau.com/api/v2/info',timeout=8) as f:
        d=json.load(f)
    return {k:d.get(k) for k in ('serverCommit','serverInstanceId')}
def begin():
    global child,original_plain,oldseq,began
    if child or not own():return
    mime=app.clipboard().mimeData()
    if mime and any(f not in ('text/plain','text/plain;charset=utf-8') for f in mime.formats()):
        label.setText('Rich-Text-Zwischenablage bleibt unverändert. Bitte vor Start einen harmlosen Klartext kopieren.');return
    original_plain=mime.text() if mime else ''
    try:
        identity=read_identity()
        if identity['serverCommit']!='e95858e3c010a7e9324b49bb44fee349abe7128a':raise RuntimeError('Wrong candidate')
        r['serverBefore']=identity
    except Exception:
        label.setText('Final-Serveridentität nicht bestätigt. Kein Test gestartet.');return
    r['startedAt']=datetime.now().astimezone().isoformat()
    oldseq=backend.get_clipboard_sequence_number()
    began=time.monotonic();start.setEnabled(False);editor.setFocus()
    child=subprocess.Popen([str(exe),'--config',str(folder/'profile.yaml')],cwd=folder,env=os.environ.copy())
    r['bootloaderPid']=child.pid;r['result']='RUNNING';setstage('ready','Client startet – Testfenster im Vordergrund lassen.')
def finish(reason):
    r['result']=reason;winsound.PlaySound(None,0)
    quit_client();setstage('shutdown','Test beendet. Client wird geschlossen.')
def tick():
    global pid,history,base_count,base_text,starts_before,close_before,ready_at,last_sample,next_trial,trial,attempt,cmd_before,trial_case,no_speech_retries,play_seconds,segments_before
    if stage=='waiting':
        return
    try:
        rows=read(folder/'observability.sqlite3','select type,details_json,activation_id from logs order by id')
        states=[];transitions=[];counts={};commands=[];phase=None
        for typ,detail,aid in rows:
            d=json.loads(detail) if detail else {}
            if typ=='client.app.started':pid=d.get('process_id')
            if typ=='client.v2.transport_state':states.append(d.get('state'));transitions.append({'state':d.get('state'),'reason':d.get('reason')})
            if typ=='client.command.completed' and d.get('command')=='control':commands.append(d.get('status'))
            if typ=='client.domain.observed':
                kind=d.get('eventType');counts[kind]=counts.get(kind,0)+1;phase=d.get('phase')
        history=[t for (t,) in read(folder/'history.sqlite','select text from history_entries order by timestamp')]
        starts=counts.get('activation.started',0);closes=counts.get('activation.input_closed',0)
        now=time.monotonic();elapsed=now-since
        r['transportTransitions']=transitions
        r['status']=dict(states=states[-4:],counts=counts,historyEntries=len(history),editorCharacters=len(editor.toPlainText()),pid=pid,focused=own(),controlStatuses=commands[-4:],phase=phase)
        if stage=='shutdown':
            if child.poll() is not None or elapsed>15:app.quit()
            return
        if not own():finish('ABORTED_TARGET_LOST_FOCUS');return
        if child.poll() is not None:finish('EARLY_CLIENT_EXIT');return
        if ready_at is not None:
            r['elapsedSeconds']=round(now-ready_at,2)
            if now-last_sample>=5:
                m=sample(pid) if pid else None
                if m:m.update(seconds=r['elapsedSeconds'],state=states[-1] if states else None);r['samples'].append(m)
                last_sample=now;save()
            if stage=='idle':
                label.setText(f"Dauerlauf: {r['elapsedSeconds']:.0f} / {args.seconds} Sekunden · {trial} / {target_count} Diktate")
                if now-ready_at>=args.seconds and trial>=target_count:
                    finish('PASS_SCOPED' if all(c.get('nativeExact') for c in r['cases']) else 'COMPLETED_WITH_DEVIATION');return
                if now>=next_trial and trial<target_count and states and states[-1]=='ready':
                    mime=app.clipboard().mimeData()
                    if (mime and any(f not in ('text/plain','text/plain;charset=utf-8') for f in mime.formats())) or app.clipboard().text()!=original_plain:
                        finish('EXTERNAL_CLIPBOARD_CHANGE');return
                    base_count=len(history);base_text=editor.toPlainText();starts_before=starts;close_before=closes;cmd_before=len(commands);segments_before=counts.get('segment.recording_started',0)
                    attempt=1;editor.setFocus();impulse(0x77);setstage('activate',f'Testdiktat {trial+1} – automatische Aufnahme');return
        if stage=='ready':
            if pid and states and states[-1]=='ready' and elapsed>12:
                ready_at=now;next_trial=now;setstage('idle','Bereit – automatischer Dauerlauf')
            elif elapsed>120:finish('START_TIMEOUT')
        elif stage=='activate':
            if starts>starts_before and elapsed>.65:
                name='kurz-'+str(trial%10+1).zfill(2)
                trial_case=dict(number=trial+1,fixture=name,startSeconds=round(now-ready_at,2),hotkeyAttempts=attempt)
                with wave.open(str(fixtures/(name+'.wav')),'rb') as f:play_seconds=f.getnframes()/f.getframerate()
                play(name);setstage('play','Testaudio läuft – keine Benutzereingabe')
            elif elapsed>30:
                if len(commands)>cmd_before and commands[-1] in ('core_unavailable','not_ready','control_unavailable','not_applicable','stale_control') and attempt<4:
                    attempt+=1;cmd_before=len(commands);impulse(0x77);setstage('activate','Core-Bereitschaft – erneuter Hotkey')
                else:finish('ACTIVATION_TIMEOUT')
        elif stage=='play' and elapsed>play_seconds+2.0:
            if closes==close_before:impulse(0x78)
            setstage('final','Final und native Texteinfügung werden geprüft')
        elif stage=='final':
            if len(history)>base_count and closes>close_before:
                expected=base_text+''.join(t if t[-1:].isspace() else t+' ' for t in history[base_count:])
                if editor.toPlainText()==expected:
                    trial_case.setdefault('pasteObservedAt',now)
                if editor.toPlainText()==expected and now-trial_case.get('pasteObservedAt',now)>1.5:
                    trial_case.pop('pasteObservedAt',None)
                    trial_case.update(nativeExact=len(history)==base_count+1,markers=all(t in history[-1].casefold() for t in tokens[trial%10]),clipboardRestored=app.clipboard().text()==original_plain,finals=len(history)-base_count,endSeconds=round(now-ready_at,2))
                    r['cases'].append(trial_case);trial+=1;trial_case=None;no_speech_retries=0
                    if not r['cases'][-1]['clipboardRestored']:finish('CLIPBOARD_CHANGED');return
                    next_trial=max(now+2,ready_at+trial*args.seconds/target_count);setstage('idle','Diktat geprüft')
            if elapsed>120:
                # Retry only a fully closed activation with no segment/final/paste.
                # Keep all misses in evidence; never repeat an uncertain paste.
                if closes>close_before and phase=='idle' and counts.get('segment.recording_started',0)==segments_before and len(history)==base_count and editor.toPlainText()==base_text and no_speech_retries<2:
                    no_speech_retries+=1
                    r['missedTrials'].append(dict(number=trial+1,reason='NO_SPEECH_FINAL_TIMEOUT',retry=no_speech_retries,elapsedSeconds=round(now-ready_at,2)))
                    trial_case=None;next_trial=now+3;setstage('idle','Keine Sprache erkannt – kontrollierte Wiederholung');return
                finish('FINAL_TIMEOUT')
        if now-began>args.seconds+900:finish('BOUNDED_TIMEOUT')
        if stage!='idle':save()
    except Exception as exc:
        r['errorType']=type(exc).__name__;finish('HARNESS_ERROR')
start.clicked.connect(begin);stop.clicked.connect(lambda:finish('OPERATOR_STOP') if child else app.quit())
timer=QTimer();timer.setInterval(100);timer.timeout.connect(tick);timer.start()
save();print('READY_FOR_START',folder,flush=True)
if args.auto:
    def auto():
        if own():begin()
        else:label.setText('Testfenster nicht im Vordergrund. Start bitte manuell klicken.')
    QTimer.singleShot(2000,auto)
try:app.exec()
finally:
    winsound.PlaySound(None,0)
    if child:
        quit_client()
        try:child.wait(15)
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],capture_output=True);child.wait(5);r['forcedCleanup']=True
        r['exitCode']=child.returncode;r['quitPosted']=quit_requested
        r['tempRemaining']=[x.name for x in (folder/'tmp').glob('_MEI*')]
    r['sharedCursorUnchanged']=cursor_before==digest(DEFAULT_CURSOR_PATH)
    r['end']=datetime.now().astimezone().isoformat()
    if len(r['samples'])>1:
        ss=r['samples'];r['resources']=dict(firstPrivateMiB=ss[0]['privateMiB'],lastPrivateMiB=ss[-1]['privateMiB'],peakPrivateMiB=max(x['privateMiB'] for x in ss),meanCoreCpuPct=round(100*(ss[-1]['cpuSeconds']-ss[0]['cpuSeconds'])/max(.1,ss[-1]['seconds']-ss[0]['seconds']),3))
    log=folder/'logs/client.log'
    if log.exists():
        txt=log.read_text(encoding='utf8',errors='replace')
        r['errorLogCount']=sum('"level": "ERROR"' in l for l in txt.splitlines())
        r['fallbackMessages']=txt.count('using default')
    r['markerPassCount']=sum(c.get('markers') is True for c in r['cases'])
    r['nativePastePassCount']=sum(c.get('nativeExact') is True and c.get('clipboardRestored') is True for c in r['cases'])
    if child:
        try:r['serverAfter']=read_identity()
        except Exception:r['serverAfter']=None
    if r['result']=='PASS_SCOPED':
        unstable=any(t.get('state')=='backoff' for t in r.get('transportTransitions',[]))
        good=(r.get('exitCode')==0 and not r.get('forcedCleanup') and not r.get('tempRemaining') and r['sharedCursorUnchanged'] and len(r['cases'])==target_count and r['nativePastePassCount']==target_count and r.get('elapsedSeconds',0)>=args.seconds and r.get('serverBefore')==r.get('serverAfter') and not unstable and not r.get('errorLogCount'))
        r['result']=('COMPLETED_WITH_DEVIATION' if r['missedTrials'] or r['markerPassCount']!=target_count else 'PASS_SCOPED_ENDURANCE') if good else 'COMPLETED_WITH_DEVIATION'
    save();print('DONE',r['result'],flush=True)