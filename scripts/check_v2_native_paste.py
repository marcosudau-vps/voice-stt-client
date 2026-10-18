"""Real Clipboard/SendInput into a disposable, separate Windows editor process.

The production queue/history/backend are retained. A narrow test guard permits
SendInput only while our child owns the foreground window. All pre-existing
clipboard MIME formats remain in memory and are restored if no third party has
replaced the clipboard. No private clipboard content or raw transcript is saved.
This proves one normal target; elevated/UIPI and other applications remain M-11.
"""
import argparse
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.qualify_v2_real import LOCAL, identity, save

TEXT='AP-IV2-020 Clipboardprüfung äöü 123.'


def target(folder, append_space=False):
    from PySide6.QtWidgets import QApplication,QPlainTextEdit
    from PySide6.QtCore import QTimer
    from voice_stt_client.core.text_injector import CtypesWindowsInjectionBackend
    app=QApplication([])
    editor=QPlainTextEdit();editor.setWindowTitle('AP-IV2-020 – isoliertes Einfügeziel')
    editor.resize(650,240);editor.show();editor.activateWindow();editor.setFocus()
    backend=CtypesWindowsInjectionBackend()
    payload=TEXT + (' ' if append_space else '')
    locked=False
    def update():
        nonlocal locked
        if (folder/'lock.request').exists() and not locked:
            locked=backend.open_clipboard(int(editor.winId()))
        text=editor.toPlainText()
        save(folder/'target.json',dict(pid=os.getpid(),hwnd=int(editor.winId()),
            characters=len(text),firstExact=text==payload,reinsertExact=text==payload+payload,
            clipboardLocked=locked))
        if (folder/'stop.request').exists():
            if locked:backend.close_clipboard()
            app.quit()
    timer=QTimer();timer.setInterval(25);timer.timeout.connect(update);timer.start()
    QTimer.singleShot(60000,app.quit)
    try:app.exec()
    finally:
        if locked:backend.close_clipboard()


def check(evidence, focus_timeout=8, append_space=False):
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QMimeData
    from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
    from voice_stt_client.core.history import TranscriptHistoryManager
    from voice_stt_client.core.text_injector import CtypesWindowsInjectionBackend,TextInjectionQueue
    from voice_stt_client.core import protocol_v2 as p
    from voice_stt_client.core.activation_mirror import ActivationMirror
    from voice_stt_client.core.final_results import V2ResultService
    from tests.test_v2_mirror import msg,snapshot
    app=QApplication([])
    clipboard=app.clipboard()
    original=QMimeData()
    current=clipboard.mimeData()
    formats=[]
    if current is not None:
        for fmt in current.formats():
            data=current.data(fmt)
            if len(data)>64*1024*1024:raise RuntimeError('Clipboard too large to preserve; defer test')
            original.setData(fmt,data);formats.append(fmt)
    folder=LOCAL/'native-paste'/uuid.uuid4().hex
    folder.mkdir(parents=True)
    config=AppConfig._load_single(DEFAULT_CONFIG_PATH)
    config.clipboard.restore_previous=False
    config.text_injection.append_space=append_space
    config.history.persistent.db_path=str(folder/'history.sqlite')
    config.history.persistent.store_all=True
    history=TranscriptHistoryManager(config.history)
    backend=None;queue=None
    child=subprocess.Popen([sys.executable,str(Path(__file__)), '--target',str(folder)]
                           + (['--append-space'] if append_space else []),
                           env=dict(os.environ,QT_QPA_PLATFORM='windows'))
    def wait(predicate,timeout=8):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            app.processEvents()
            if predicate():return
            time.sleep(.02)
        raise TimeoutError('Native paste observation deadline')
    def observed():
        try:return json.loads((folder/'target.json').read_text())
        except (FileNotFoundError,json.JSONDecodeError):return {}
    attempts=[]
    checks={}
    initial_foreground=None
    run_error=None
    try:
        wait(lambda:observed().get('hwnd'))
        hwnd=observed()['hwnd']
        class GuardedNative(CtypesWindowsInjectionBackend):
            last_write=None
            def set_clipboard_data_unicode(self,text):
                result=super().set_clipboard_data_unicode(text)
                if result:self.last_write=self.get_clipboard_sequence_number()
                return result
            def send_input_keyboard(self,events):
                foreground=self.get_foreground_window()
                if self.get_window_thread_process_id(foreground)[1]!=child.pid:
                    raise RuntimeError('Test target lost foreground; no input sent')
                return super().send_input_keyboard(events)
        backend=GuardedNative()
        initial_foreground=backend.get_foreground_window()
        backend.user32.SetForegroundWindow.argtypes=[wintypes.HWND]
        backend.user32.SetForegroundWindow(hwnd)
        wait(lambda:backend.get_window_thread_process_id(backend.get_foreground_window())[1]==child.pid,
             timeout=focus_timeout)
        queue=TextInjectionQueue(config,history,backend)
        queue.on_attempt_result=attempts.append
        queue.start()
        mirror=ActivationMirror()
        service=V2ResultService(history,queue)
        service.consume(mirror.begin(1,snapshot(),1))
        reduction=mirror.consume(1,msg(p.EventType.COMPLETED,1,text=TEXT),1)
        outcomes=service.consume(reduction)
        if [o.status for o in outcomes]!=['queued']:raise RuntimeError('Final admission refused')
        entry=history.get_memory_entries()[0]
        wait(lambda:len(attempts)==1)
        wait(lambda:observed().get('firstExact'))
        checks['separate_process_exact_unicode_paste']=attempts[0].status=='command_sent'
        # Automatic duplicate is rejected before another clipboard operation.
        duplicate=service.consume(reduction)
        checks['automatic_duplicate_rejected']=[o.status for o in duplicate]==['deduplicated']
        if not queue.enqueue_manual(entry):raise RuntimeError('Explicit reinsert refused')
        wait(lambda:len(attempts)==2)
        wait(lambda:observed().get('reinsertExact'))
        checks['explicit_reinsert_exactly_once']=attempts[1].status=='command_sent'
        (folder/'lock.request').touch()
        wait(lambda:observed().get('clipboardLocked'))
        another=history.add_entry_with_status(str(uuid.uuid4()),str(uuid.uuid4()),TEXT,
            protocol_version=2,activation_id=str(uuid.uuid4()),segment_sequence=1,
            event_id=str(uuid.uuid4()),event_seq=1,primary_source='manual',activation_sequence=1).entry
        queue.enqueue_reserved(another)
        wait(lambda:len(attempts)==3)
        checks['real_foreign_clipboard_lock_fails_bounded']=attempts[2].status=='failed'
        checks['clipboard_conflict_does_not_paste']=observed().get('reinsertExact',False)
    except Exception as error:
        run_error=type(error).__name__
    finally:
        if queue:queue.stop(5)
        (folder/'stop.request').touch()
        try:child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            child.terminate();child.wait(timeout=5)
        if backend and backend.last_write is None:
            checks['clipboard_untouched']=True
        elif backend and backend.last_write==backend.get_clipboard_sequence_number():
            clipboard.setMimeData(original);app.processEvents()
            checks['original_clipboard_formats_restored']=all(
                clipboard.mimeData().data(fmt)==original.data(fmt) for fmt in formats)
        else:
            checks['original_clipboard_formats_restored']='NOT_PROVEN / clipboard changed externally'
        if initial_foreground and backend:
            backend.user32.SetForegroundWindow(initial_foreground)
    verdict=('NOT_RUN' if run_error and not attempts else
             'PASS' if not run_error and checks and all(v is True for v in checks.values()) else 'FAIL')
    result=dict(identity=identity(),tester='Codex on native Windows',checks=checks,errorType=run_error,
        appendSpace=append_space,authoritativeHistoryTextPreserved=all(
            e.text==TEXT for e in history.get_memory_entries()),
        attempts=[dict(status=a.status,source=a.source) for a in attempts],
        result=verdict,
        boundaries=__doc__,targetProcessSeparate=True,privateClipboardSaved=False,
        elevatedTarget='NOT_RUN',otherApplications='NOT_RUN',processAbortNearPaste='NOT_RUN')
    save(Path(evidence)/'native-paste.json',result)
    print(json.dumps(dict(result=result['result'],checks=checks)))
    return 0 if result['result']=='PASS' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',type=Path)
    parser.add_argument('--evidence',type=Path)
    parser.add_argument('--focus-timeout',type=float,default=8)
    parser.add_argument('--append-space',action='store_true')
    args=parser.parse_args()
    if args.target:target(args.target,args.append_space)
    else:raise SystemExit(check(args.evidence,args.focus_timeout,args.append_space))
