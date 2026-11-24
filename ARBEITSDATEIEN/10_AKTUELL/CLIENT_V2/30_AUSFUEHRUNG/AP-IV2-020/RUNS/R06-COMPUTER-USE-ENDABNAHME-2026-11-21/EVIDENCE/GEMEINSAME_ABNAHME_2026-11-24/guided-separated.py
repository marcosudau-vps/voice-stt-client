import os,sys,json,time,uuid,hashlib,asyncio,winsound,traceback
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
root=Path(__file__).parent
folder=root/('guided-separated-'+uuid.uuid4().hex[:8]);folder.mkdir()
os.chdir(folder)
os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),VOICESTT_CLIENT_CONFIG=str(folder/'profile.yaml'),QT_QPA_PLATFORM='windows')
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QLabel,QPushButton
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
cfg.led.enabled=True;cfg.feedback.sounds_enabled=True;cfg.overlay.enabled=True;cfg.overlay.show_realtime_text=True
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
window=QWidget();window.setWindowTitle('R06 – LED und Bildschirm getrennt')
layout=QVBoxLayout(window);label=QLabel('1. LED- und Tonprobe starten. Danach nur nach rechts zum ReSpeaker schauen.');label.setWordWrap(True);label.setStyleSheet('font-size:19px;font-weight:bold;padding:12px');layout.addWidget(label)
detail=QLabel('Reihenfolge: Ruhe → Aufnahme → Abschluss → Abbruch → Wake-Pause. Keine Sprache nötig.');detail.setWordWrap(True);layout.addWidget(detail)
first=QPushButton('1. LED- und Tonprobe starten');layout.addWidget(first)
second=QPushButton('2. Bildschirmprobe starten');second.setEnabled(False);layout.addWidget(second)
stop=QPushButton('Beenden');layout.addWidget(stop);window.resize(760,270);window.show();window.raise_();window.activateWindow()
desktop=None;rt=None;busy=False;deadline=time.monotonic()+600
report=dict(scope='corrected source native GUI, real ReSpeaker LEDs and sound, real acoustic input, pinned V2, mock paste and no global hotkeys',folder=folder.name,checks={},stages=[],result='WAITING')
out=root/'guided-separated-current.json'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
before=digest(DEFAULT_CURSOR_PATH)
def save():
    tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    try:tmp.replace(out)
    except PermissionError:pass
def stage(n,t):
    report['stages'].append(dict(name=n,time=datetime.now().astimezone().isoformat()));label.setText(t);save()
def check(n,v):report['checks'][n]=bool(v);save()
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
def run_first():
    global desktop,rt,busy,deadline
    if busy:return
    busy=True;first.setEnabled(False);stop.setEnabled(False)
    try:
        stage('boot','Client startet. Nur den LED-Ring beobachten.')
        assert guard.acquire().acquired
        bridge=V2CoreBridge(cfg,runtime_factory=lambda c:V2Runtime(c,backend=backend))
        desktop=V2DesktopApplication(app,cfg,guard,bridge=bridge)
        assert desktop.start()
        wait(lambda:desktop._runtime_ready,30);rt=bridge._controller
        check('server_pin',rt.session.binding.accepted.payload['serverCommit']=='e95858e3c010a7e9324b49bb44fee349abe7128a')
        pause(True)
        stage('idle','Ruhezustand. Bitte weiter nur den ReSpeaker ansehen.')
        delay(4);aid=activate();stage('recording','Aufnahme – bitte weiter auf den LED-Ring achten.')
        delay(1)
        p=root.parent/'autonome-restpruefung-2026-11-23'/'fixtures'/'kurz-01.wav'
        n=len(backend.send_input_calls);winsound.PlaySound(str(p),winsound.SND_FILENAME|winsound.SND_ASYNC|winsound.SND_NODEFAULT)
        delay(4.1)
        if view().input.activation_id==aid:command(rt.stop_dictation())
        wait(lambda:view().input.activation_id is None,15)
        wait(lambda:len(backend.send_input_calls)>n,25)
        e=[e for e in rt.history.get_memory_entries() if e.activation_id==aid]
        check('manual_final',len(e)==1 and len(backend.send_input_calls)-n==1)
        stage('final','Abschluss. Ruhephase beobachten.');delay(3)
        aid=activate();stage('cancel','Abbruchprobe. Nicht sprechen.');delay(2)
        command(rt.cancel_dictation());wait(lambda:view().input.activation_id is None)
        check('cancel_no_injection',len(backend.send_input_calls)==n+1);delay(3)
        pause(False);delay(2);pause(True);stage('pause','Wake-Pause. Rückmeldung beobachten.');delay(4)
        report['result']='HARDWARE_SEQUENCE_DONE';stage('hardware_done','LED-/Tonprobe abgeschlossen. Jetzt wieder zum Bildschirm schauen.');detail.setText('Wenn du bereit bist: Bildschirmprobe starten.');second.setEnabled(True);deadline=time.monotonic()+600
    except Exception as exc:
        report['error']=type(exc).__name__;report['result']='INCOMPLETE';stage('error','Test nicht vollständig: '+type(exc).__name__+'. Bitte Bescheid sagen.')
        traceback.print_exc()
    finally:busy=False;stop.setEnabled(True);save()
def run_second():
    global busy,deadline
    if busy or rt is None:return
    busy=True;second.setEnabled(False);stop.setEnabled(False)
    try:
        pause(False)
        stage('human','JETZT EINMAL SPRECHEN: Hey Jarvis, die grüne Lampe steht neben dem Fenster.')
        detail.setText('Danach schweigen und nur auf den Bildschirm / das Overlay achten.')
        n=len(backend.send_input_calls)
        wait(lambda:bool(view().input.activation_id),30)
        aid=view().input.activation_id;stage('human_active','Wake erkannt – Overlay beobachten, bitte schweigen.')
        wait(lambda:view().input.activation_id is None,25)
        wait(lambda:len(backend.send_input_calls)>n,25)
        entries=[e for e in rt.history.get_memory_entries() if e.activation_id==aid]
        check('human_wake_final',len(entries)==1 and len(backend.send_input_calls)-n==1 and all(t in entries[0].text.casefold() for t in ('lampe','fenster')))
        pause(True)
        report['result']='PASS_SCOPED' if all(report['checks'].values()) else 'COMPLETED_WITH_DEVIATION'
        stage('done','Fertig. Jetzt kannst du das Fenster schließen und im Chat antworten.')
        detail.setText('Technischer Test: '+report['result']+'. LED und Töne bitte im Chat bewerten.')
    except Exception as exc:
        report['error']=type(exc).__name__;report['result']='INCOMPLETE';stage('error','Sprachprobe nicht vollständig. Bitte Bescheid sagen.')
        traceback.print_exc()
    finally:
        busy=False;stop.setEnabled(True);deadline=time.monotonic()+120;save()
def timer_tick():
    if not busy and time.monotonic()>deadline:app.quit()
first.clicked.connect(run_first);second.clicked.connect(run_second);stop.clicked.connect(app.quit)
timer=QTimer();timer.timeout.connect(timer_tick);timer.start(500)
save();print('READY_FOR_CLICK',flush=True)
try:app.exec()
finally:
    winsound.PlaySound(None,0)
    if desktop:desktop.shutdown()
    guard.release();report['sharedCursorUnchanged']=before==digest(DEFAULT_CURSOR_PATH)
    report['end']=datetime.now().astimezone().isoformat();save();print('DONE',report['result'],flush=True)
