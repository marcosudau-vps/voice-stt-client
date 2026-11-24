import os,sys,json,time,uuid,hashlib,asyncio,winsound,traceback
from pathlib import Path
from datetime import datetime
from dataclasses import asdict,replace
root=Path(__file__).parent
folder=root/('guided-separated-'+uuid.uuid4().hex[:8]);folder.mkdir()
os.chdir(folder)
os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),VOICESTT_CLIENT_CONFIG=str(folder/'profile.yaml'),QT_QPA_PLATFORM='windows')
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QLabel,QPushButton,QHBoxLayout,QComboBox
from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.core.v2_runtime import V2Runtime
from voice_stt_client.ui.v2_core_bridge import V2CoreBridge
from voice_stt_client.ui.v2_application import V2DesktopApplication
from voice_stt_client.ui.single_instance import SingleInstanceGuard
from voice_stt_client.core.event_cursor_store import DEFAULT_CURSOR_PATH
from tests.test_text_injector import MockInjectionBackend
import sounddevice as sd
cfg=AppConfig._load_single(DEFAULT_CONFIG_PATH)
cfg.server.url='wss://final.v2.voice-stt-server.marcosudau.com/ws/v2'
cfg.server.health_url='https://final.v2.voice-stt-server.marcosudau.com/health'
cfg.audio.device=next(i for i,d in enumerate(sd.query_devices()) if 'respeaker' in d['name'].casefold() and d['max_input_channels']>0)
cfg.audio.sample_rate=16000;cfg.audio.channels=1
cfg.led.enabled=True;cfg.feedback.sounds_enabled=True;cfg.overlay.enabled=False;cfg.overlay.show_realtime_text=True
cfg.event_stream.enabled=False;cfg.event_stream.cursor_persistence_enabled=False
cfg.history.persistent.db_path=str(folder/'history.sqlite');cfg.history.persistent.store_all=True
cfg.logging.log_dir=str(folder/'logs')
cfg.logging.observability.store_transcription_content=False;cfg.logging.observability.store_raw_payload=False
profile=V2Profile(manual=True,wake_word=True,wake_word_ids=['hey_jarvis'],desired_settings={'activation.followupTimeoutMs':5000})
profile.controls['enabled']=False
cfg.v2_profile=asdict(profile);cfg.save(folder/'profile.yaml');cfg=AppConfig.load(folder/'profile.yaml')
backend=MockInjectionBackend();app=QApplication([]);app.setQuitOnLastWindowClosed(False)
app.setApplicationName('R06-Isolated-Desktop');app.setOrganizationName('R06-Test')
guard=SingleInstanceGuard('Local\\CV2_R06_'+uuid.uuid4().hex)
window=QWidget();window.setWindowTitle('R06 – Abnahme in Einzelschritten')
layout=QVBoxLayout(window)
heading=QLabel();heading.setStyleSheet('font-size:21px;font-weight:bold;padding:8px');layout.addWidget(heading)
label=QLabel();label.setWordWrap(True);label.setStyleSheet('font-size:17px;padding:8px');layout.addWidget(label)
detail=QLabel();detail.setWordWrap(True);layout.addWidget(detail)
selector=QComboBox();steps=[
 ('idle','LED: Ruhezustand','Nur zum ReSpeaker schauen. Beobachte den LED-Ring in Ruhe.'),
 ('record','LED/Ton: Aufnahme und Abschluss','Nur zum ReSpeaker schauen und auf die Töne achten. Ein Testdiktat läuft automatisch.'),
 ('cancel','LED/Ton: Abbruch','Nur zum ReSpeaker schauen und auf den Abbruchton achten. Nicht sprechen.'),
 ('pause','LED: Wake-Pause','Nur zum ReSpeaker schauen. Wake wird deaktiviert und wieder aktiviert.'),
 ('screen','Overlay: Aufnahme und Abschluss','Nur zum Bildschirm schauen. Ein Testdiktat läuft automatisch.'),
 ('human','Wake Word: echte Stimme','Erst nach der Aufforderung einmal sprechen. Nur auf den Bildschirm achten.')]
for key,title,desc in steps:selector.addItem(title,key)
layout.addWidget(selector)
run=QPushButton('Schritt starten / wiederholen');layout.addWidget(run)
row=QHBoxLayout();ok=QPushButton('Beobachtung OK – weiter');bad=QPushButton('Abweichung – weiter');skip=QPushButton('Nicht gesehen – später');row.addWidget(ok);row.addWidget(bad);row.addWidget(skip);layout.addLayout(row)
stop=QPushButton('Beenden (Fortschritt gespeichert)');layout.addWidget(stop)
window.resize(790,360);window.show();window.raise_();window.activateWindow()
desktop=None;rt=None;busy=False
out=root/'guided-steps-progress.json'
report=dict(scope='corrected source native GUI, real physical LED/audio and acoustic input; no native paste or global hotkeys; each step requires explicit observation confirmation',attempts=[],observations={},selected=0,result='WAITING')
if out.exists():
    try:
        previous=json.loads(out.read_text(encoding='utf8'))
        report=previous
    except Exception:pass
report['folder']=folder.name;report['result']='WAITING'
selector.setCurrentIndex(min(max(0,report.get('selected',0)),len(steps)-1))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
before=digest(DEFAULT_CURSOR_PATH)
def save():
    tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    try:tmp.replace(out)
    except PermissionError:pass
def stage(n,t):
    report['currentStage']=n;label.setText(t);save()
def check(n,v):report.setdefault('technical',{})[n]=bool(v);save()
def wait(fn,limit=20):
    end=time.monotonic()+limit
    while time.monotonic()<end:
        app.processEvents()
        if fn():return
        time.sleep(.025)
    raise TimeoutError('condition not met')
def delay(sec):
    end=time.monotonic()+sec
    while time.monotonic()<end:app.processEvents();time.sleep(.025)
def command(coro):
    f=asyncio.run_coroutine_threadsafe(coro,desktop.bridge._loop)
    wait(f.done,15);return f.result()
def view():return rt.mirror.mirror.view
def pause(v):
    command(rt.controls.set_pause('wakeWord',v));wait(lambda:rt.controls.pause_view.confirmed_wake_word==v)
def activate():
    wait(lambda:rt.is_ready and rt.media.audio_available and view().manual_available and desktop.bridge._published_view is not None and desktop.bridge._published_view.mirror.manual_available)
    assert desktop.bridge.press_control('primary')
    wait(lambda:bool(view().input.activation_id),8);return view().input.activation_id

last_activity=time.monotonic()
def select():
    if busy:return
    i=selector.currentIndex();report['selected']=i
    key,title,desc=steps[i]
    heading.setText(f'Schritt {i+1} von {len(steps)}: {title}')
    label.setText(desc)
    detail.setText('Bereit. Es startet erst nach deinem Klick. Vorherige Beobachtung: '+report.get('observations',{}).get(key,'offen'))
    ok.setEnabled(False);bad.setEnabled(False);skip.setEnabled(True)
    run.setEnabled(True);save()
def init():
    global desktop,rt
    if desktop is not None:return
    stage('boot','Client startet. Der eigentliche Test beginnt erst nach einer kurzen Vorbereitung.')
    assert guard.acquire().acquired
    bridge=V2CoreBridge(cfg,runtime_factory=lambda c:V2Runtime(c,backend=backend))
    desktop=V2DesktopApplication(app,cfg,guard,bridge=bridge)
    assert desktop.start()
    wait(lambda:desktop._runtime_ready,30);rt=bridge._controller
    check('server_pin',rt.session.binding.accepted.payload['serverCommit']=='e95858e3c010a7e9324b49bb44fee349abe7128a')
    pause(True)
def manual_pause(v):
    command(rt.controls.set_pause('manual',v))
    wait(lambda:rt.controls.pause_view.confirmed_manual==v,10)
def acoustic():
    manual_pause(False);aid=activate();delay(.7)
    p=root.parent/'autonome-restpruefung-2026-11-23'/'fixtures'/'kurz-01.wav'
    n=len(backend.send_input_calls)
    winsound.PlaySound(str(p),winsound.SND_FILENAME|winsound.SND_ASYNC|winsound.SND_NODEFAULT)
    delay(4)
    if view().input.activation_id==aid:command(rt.stop_dictation())
    wait(lambda:view().input.activation_id is None,15)
    wait(lambda:len(backend.send_input_calls)>n,25)
    e=[e for e in rt.history.get_memory_entries() if e.activation_id==aid]
    return len(e)==1 and len(backend.send_input_calls)-n==1
def execute():
    global busy,last_activity
    if busy:return
    busy=True;last_activity=time.monotonic()
    for b in (run,ok,bad,skip,stop):b.setEnabled(False)
    selector.setEnabled(False)
    i=selector.currentIndex();key,title,desc=steps[i]
    attempt=dict(step=key,start=datetime.now().astimezone().isoformat())
    report['attempts'].append(attempt);report['result']='RUNNING';save()
    try:
        init()
        pause(True);manual_pause(False)
        desktop.overlay.apply_config(replace(cfg.overlay,enabled=key in ('screen','human')))
        if key not in ('screen','human'):desktop.overlay.hide()
        stage('countdown',desc+' – Start in 4 Sekunden.');delay(4)
        stage('active',desc)
        if key=='idle':delay(8);success=True
        elif key in ('record','screen'):success=acoustic();delay(4)
        elif key=='cancel':
            n=len(backend.send_input_calls);aid=activate();delay(2)
            command(rt.cancel_dictation());wait(lambda:view().input.activation_id is None)
            delay(4);success=len(backend.send_input_calls)==n
        elif key=='pause':
            pause(False);delay(4);pause(True);delay(6);success=rt.controls.pause_view.confirmed_wake_word is True
        elif key=='human':
            pause(False)
            stage('speak','JETZT SPRECHEN: Hey Jarvis, die grüne Lampe steht neben dem Fenster. Danach schweigen.')
            n=len(backend.send_input_calls)
            wait(lambda:bool(view().input.activation_id),30)
            aid=view().input.activation_id;stage('human_active','Wake erkannt. Overlay beobachten, bitte schweigen.')
            wait(lambda:view().input.activation_id is None,25)
            wait(lambda:len(backend.send_input_calls)>n,25)
            entries=[e for e in rt.history.get_memory_entries() if e.activation_id==aid]
            success=len(entries)==1 and len(backend.send_input_calls)-n==1 and all(t in entries[0].text.casefold() for t in ('lampe','fenster'))
        attempt['technicalPass']=bool(success)
        stage('awaiting_confirmation','Schritt beendet. Bitte deine Beobachtung bestätigen – oder denselben Schritt wiederholen.')
        detail.setText('Technik: '+('OK' if success else 'Abweichung')+'. Kein automatischer Wechsel zum nächsten Schritt.')
        ok.setEnabled(True);bad.setEnabled(True)
    except Exception as exc:
        attempt['error']=type(exc).__name__
        stage('retry','Schritt nicht vollständig. Du kannst ihn ohne Neustart wiederholen.')
        detail.setText('Kein automatisches Weitergehen. Fehler: '+type(exc).__name__)
        traceback.print_exc()
    finally:
        winsound.PlaySound(None,0)
        if rt:
            try:
                if view().input.activation_id:command(rt.cancel_dictation())
                pause(True);manual_pause(True)
            except Exception:attempt['pauseError']=True
        attempt['end']=datetime.now().astimezone().isoformat()
        busy=False;last_activity=time.monotonic();report['result']='WAITING_FOR_CONFIRMATION'
        run.setEnabled(True);skip.setEnabled(True);stop.setEnabled(True);selector.setEnabled(True);save()
def confirm(value):
    if busy:return
    i=selector.currentIndex();key=steps[i][0]
    report['observations'][key]=value;save()
    if i<len(steps)-1:selector.setCurrentIndex(i+1)
    else:
        heading.setText('Ende der Prüfschritte')
        label.setText('Du kannst jeden Schritt oben erneut auswählen. Beenden speichert alle Ergebnisse.')
        detail.setText('Bestätigungen: '+str(report['observations']))
        report['result']='CONFIRMATIONS_RECORDED';save()
        ok.setEnabled(False);bad.setEnabled(False)
def safety():
    # No forced advancement, never close the test window. After 10 minutes of
    # inactivity release the microphone/client; next click restarts this private runtime.
    global desktop,rt
    if not busy and desktop is not None and time.monotonic()-last_activity>600:
        desktop.shutdown();desktop=None;rt=None;guard.release()
        detail.setText('Client wegen Inaktivität pausiert. Fortschritt gespeichert; nächster Start verbindet erneut.')
selector.currentIndexChanged.connect(select)
run.clicked.connect(execute);ok.clicked.connect(lambda:confirm('OK'));bad.clicked.connect(lambda:confirm('ABWEICHUNG'));skip.clicked.connect(lambda:confirm('NICHT_BEOBACHTET'));stop.clicked.connect(app.quit)
timer=QTimer();timer.timeout.connect(safety);timer.start(1000)
select();print('READY_FOR_STEP',flush=True)
try:app.exec()
finally:
    winsound.PlaySound(None,0)
    if desktop:desktop.shutdown()
    guard.release();report['sharedCursorUnchanged']=before==digest(DEFAULT_CURSOR_PATH)
    report['end']=datetime.now().astimezone().isoformat();save();print('DONE',report['result'],flush=True)
