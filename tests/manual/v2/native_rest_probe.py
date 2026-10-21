"""Owned Qt target + production Windows injection queue in disposable workers.

Start the visible target, focus its editor with Computer Use, then click its
button. No foreign foreground input, no elevation, no original clipboard bytes
in evidence. Crash workers are deliberately killed before/after real SendInput.
"""
import argparse,json,os,subprocess,sys,time,uuid
from pathlib import Path
from tests.manual.v2.suite_plan import ROOT,PROFILE_RUNTIME
from tests.manual.v2.suite_session import save

TEXT='AP-IV2-020 Einfügeprobe äöü. '


def config(folder):
    from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
    cfg=AppConfig._load_single(DEFAULT_CONFIG_PATH)
    cfg.history.persistent.db_path=str(folder/'history.sqlite')
    cfg.history.persistent.enabled=True;cfg.history.persistent.store_all=True
    cfg.history.persistent.min_characters=0
    cfg.clipboard.restore_previous=False;cfg.text_injection.append_space=False
    return cfg


def worker(folder,mode,target_pid):
    from voice_stt_client.core.history import TranscriptHistoryManager
    from voice_stt_client.core.text_injector import CtypesWindowsInjectionBackend,TextInjectionQueue
    cfg=config(folder);history=TranscriptHistoryManager(cfg.history)
    class GuardedNative(CtypesWindowsInjectionBackend):
        def set_clipboard_data_unicode(self,text):
            result=super().set_clipboard_data_unicode(text)
            if result:save(folder/'clipboard.json',dict(sequence=self.get_clipboard_sequence_number()))
            return result
        def send_input_keyboard(self,events):
            if self.get_window_thread_process_id(self.get_foreground_window())[1]!=target_pid:
                raise RuntimeError('Owned target lost focus; no SendInput')
            if mode=='crash-before':
                save(folder/'barrier.json',dict(phase='before_send_input'))
                time.sleep(30);raise TimeoutError('Crash barrier not released')
            sent=super().send_input_keyboard(events)
            if mode=='crash-after':
                save(folder/'barrier.json',dict(phase='after_send_input',sent=sent,expected=len(events)))
                time.sleep(30);raise TimeoutError('Crash barrier not released')
            return sent
    queue=TextInjectionQueue(cfg,history,GuardedNative());attempts=[]
    queue.on_attempt_result=attempts.append;queue.start()
    try:
        if mode=='recover':
            time.sleep(1.5)
            entries=history.get_persistent_entries()
            save(folder/'recovered.json',dict(queueSize=queue.queue_size(),
                attempts=[a.status for e in entries for a in e.attempts],
                automaticCallbacks=len(attempts)))
            return 0
        entry=history.add_entry_with_status(str(uuid.uuid4()),1,TEXT).entry
        assert entry and queue.enqueue_reserved(entry)
        deadline=time.monotonic()+8
        while not attempts and time.monotonic()<deadline:time.sleep(.02)
        assert attempts,'No bounded queue outcome'
        save(folder/'worker.json',dict(attempt=attempts[0].status,source=attempts[0].source))
        return 0
    finally:queue.stop(3)


def target(output):
    from PySide6.QtCore import QMimeData,QTimer
    from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QLabel,QPushButton,QPlainTextEdit
    from voice_stt_client.core.text_injector import CtypesWindowsInjectionBackend
    folder=PROFILE_RUNTIME/('native-rest-'+uuid.uuid4().hex[:12]);(folder/'tmp').mkdir(parents=True)
    os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),TEMP=str(folder/'tmp'),TMP=str(folder/'tmp'))
    output.mkdir(parents=True,exist_ok=False)
    app=QApplication([]);window=QWidget();window.setWindowTitle('AP-IV2-020 – autonomes Windows-Einfügeziel')
    layout=QVBoxLayout(window);label=QLabel('Eigener leerer Editor. Nur automatische Einfüge-/Abbruchprüfung.');layout.addWidget(label)
    editor=QPlainTextEdit();layout.addWidget(editor);button=QPushButton('Automatische Windows-Prüfung starten');layout.addWidget(button)
    window.resize(760,340);window.show()
    native=CtypesWindowsInjectionBackend();original=QMimeData();formats=[]
    rows=[];child=None;stage=0;current=None;started=0;last_sequence=None;locked=False;recovery=False;finished=False
    modes=('normal','conflict','crash-before','crash-after')
    def read(path):
        try:return json.loads(path.read_text(encoding='utf8'))
        except (OSError,ValueError):return {}
    def report(result):save(output/'result.json',dict(result=result,pid=os.getpid(),runtimeFolder=str(folder),rows=rows,
        scope=__doc__,elevatedTarget='NOT_RUN_REQUIRES_HUMAN_UAC',originalClipboardBytesSaved=False))
    def spawn(mode):
        return subprocess.Popen([sys.executable,'-m','tests.manual.v2.native_rest_probe','--worker',str(current),'--mode',mode,'--target-pid',str(os.getpid())],
            cwd=ROOT,env=os.environ.copy(),creationflags=subprocess.CREATE_NO_WINDOW)
    def begin():
        nonlocal stage
        mime=app.clipboard().mimeData()
        if mime:
            for fmt in mime.formats():
                data=mime.data(fmt)
                if len(data)>64*1024*1024:raise RuntimeError('Clipboard preservation limit')
                original.setData(fmt,data);formats.append(fmt)
        button.setEnabled(False);editor.setFocus();stage=1
    button.clicked.connect(begin);report('WAITING_FOR_OWNED_FOCUS')
    def finish():
        nonlocal finished
        sequence=native.get_clipboard_sequence_number();own_text=False
        if native.open_clipboard(int(editor.winId())):
            try:own_text=native.get_clipboard_data_unicode()==TEXT
            finally:native.close_clipboard()
        eligible=last_sequence is None or sequence==last_sequence or (own_text and native.get_clipboard_sequence_number()==sequence)
        if last_sequence is None:restored=True
        elif eligible:
            app.clipboard().setMimeData(original);app.processEvents()
            restored=all(app.clipboard().mimeData().data(fmt)==original.data(fmt) for fmt in formats)
        else:restored=False
        rows.append(dict(name='clipboard-preservation',checks=dict(originalFormatsRestored=restored),
            lastOwnSequence=last_sequence,finalSequenceBeforeRestore=sequence,
            currentTextStillOwned=own_text,originalFormatCount=len(formats),restoreEligible=eligible))
        finished=True;report('PASS_SCOPED' if all(all(r['checks'].values()) for r in rows) else 'FAIL')
        label.setText('FERTIG – native Einfügung, Konflikt und Prozessabbruch ausgewertet.');QTimer.singleShot(1200,app.quit)
    def tick():
        nonlocal child,stage,current,started,last_sequence,locked,recovery
        if finished or not stage:return
        try:
            if child is None:
                if stage>len(modes):finish();return
                if native.get_window_thread_process_id(native.get_foreground_window())[1]!=os.getpid():
                    raise RuntimeError('Owned target not focused; no worker launched')
                current=folder/modes[stage-1];current.mkdir();editor.clear();editor.setFocus();recovery=False
                if modes[stage-1]=='conflict':
                    locked=native.open_clipboard(int(editor.winId()));assert locked
                child=spawn(modes[stage-1]);started=time.monotonic();label.setText(modes[stage-1]);return
            marker=read(current/'clipboard.json')
            if marker:last_sequence=marker['sequence']
            barrier=read(current/'barrier.json')
            if barrier and not recovery and child.poll() is None:
                if barrier['phase']=='after_send_input' and editor.toPlainText()!=TEXT:return
                child.terminate();child.wait(3);child=spawn('recover');recovery=True;started=time.monotonic();return
            if child.poll() is None:
                if time.monotonic()-started>12:raise TimeoutError('Native worker deadline')
                return
            assert child.returncode==0,'Native worker failed'
            if locked:native.close_clipboard();locked=False
            mode=modes[stage-1];text=editor.toPlainText()
            if recovery:
                recovered=read(current/'recovered.json')
                checks=dict(recoveredUnknown=recovered.get('attempts')==['unknown'],
                    noAutomaticRetry=recovered.get('queueSize')==0 and recovered.get('automaticCallbacks')==0,
                    actualEffectMatchesBarrier=text==(TEXT if mode=='crash-after' else ''))
                if mode=='crash-after':checks['nativeSendComplete']=barrier['sent']==barrier['expected']
            else:
                result=read(current/'worker.json')
                checks=dict(expectedStatus=result.get('attempt')==('failed' if mode=='conflict' else 'command_sent'),
                    exactText=text==('' if mode=='conflict' else TEXT))
            rows.append(dict(name=mode,checks=checks));report('RUNNING');child=None;stage+=1
        except Exception as error:
            if child and child.poll() is None:child.terminate();child.wait(3)
            if locked:native.close_clipboard();locked=False
            rows.append(dict(name='harness',checks=dict(noError=False),error=type(error).__name__));finish()
    timer=QTimer();timer.timeout.connect(tick);timer.start(30)
    QTimer.singleShot(180000,app.quit)
    try:app.exec()
    finally:
        if child and child.poll() is None:child.terminate();child.wait(3)
        if locked:native.close_clipboard()
    return 0 if read(output/'result.json').get('result')=='PASS_SCOPED' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path)
    p.add_argument('--worker',type=Path);p.add_argument('--mode');p.add_argument('--target-pid',type=int)
    args=p.parse_args()
    if args.worker:
        if not args.worker.resolve().is_relative_to(PROFILE_RUNTIME.resolve()):p.error('Owned qualification worker path required')
        raise SystemExit(worker(args.worker,args.mode,args.target_pid))
    if args.output is None or not args.output.resolve().is_relative_to(ROOT/'build'):p.error('Project build output required')
    raise SystemExit(target(args.output.resolve()))
