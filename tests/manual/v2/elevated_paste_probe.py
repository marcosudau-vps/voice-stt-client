"""Actual medium-integrity injection into an owned UAC-elevated Qt target.

User must accept Windows UAC. No automation of the consent dialog. Test source
stays in the repo; only isolated runtime metadata/history in the approved home.
"""
import argparse,ctypes,json,os,subprocess,sys,time,uuid
from pathlib import Path
from tests.manual.v2.suite_plan import ROOT,PROFILE_RUNTIME
from tests.manual.v2.suite_session import save


def target(folder):
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication,QPlainTextEdit
    class ObservedEditor(QPlainTextEdit):
        key_count=0
        def keyPressEvent(self,event):
            self.key_count+=1
            super().keyPressEvent(event)
    app=QApplication([]);editor=ObservedEditor()
    editor.setWindowTitle('AP-IV2-020 – erhöhtes leeres Einfügeziel')
    editor.resize(700,280);editor.show();editor.activateWindow();editor.setFocus()
    admin=bool(ctypes.windll.shell32.IsUserAnAdmin())
    def tick():
        save(folder/'target.json',dict(pid=os.getpid(),elevated=admin,characters=len(editor.toPlainText()),
            editorFocused=editor.hasFocus(),active=editor.isActiveWindow(),keyPresses=editor.key_count))
        if (folder/'stop.request').exists():app.quit()
    timer=QTimer();timer.timeout.connect(tick);timer.start(40);tick()
    QTimer.singleShot(180000,app.quit)
    return app.exec()


def run(output):
    folder=PROFILE_RUNTIME/('elevated-final-'+uuid.uuid4().hex[:12]);(folder/'tmp').mkdir(parents=True)
    os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),TEMP=str(folder/'tmp'),TMP=str(folder/'tmp'),QT_QPA_PLATFORM='windows')
    from PySide6.QtCore import QMimeData
    from PySide6.QtWidgets import QApplication
    from voice_stt_client.core.text_injector import CtypesWindowsInjectionBackend
    from tests.manual.v2.native_rest_probe import TEXT
    from scripts.qualify_v2_real import identity
    app=QApplication([]);native=CtypesWindowsInjectionBackend();original=QMimeData();formats=[]
    mime=app.clipboard().mimeData()
    if mime:
        for fmt in mime.formats():
            data=mime.data(fmt)
            if len(data)>64*1024*1024:raise RuntimeError('Clipboard preservation limit')
            original.setData(fmt,data);formats.append(fmt)
    output.mkdir(parents=True,exist_ok=False)
    report=dict(result='WAITING_FOR_HUMAN_UAC',pid=os.getpid(),runtimeFolder=str(folder),identity=identity(),
        sourceElevated=bool(ctypes.windll.shell32.IsUserAnAdmin()),scope=__doc__)
    save(output/'result.json',report)
    def read(path):
        try:return json.loads(path.read_text(encoding='utf8'))
        except (OSError,ValueError):return {}
    def wait(predicate,seconds):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            app.processEvents()
            if predicate():return
            time.sleep(.03)
        raise TimeoutError('Owned target observation deadline')
    own_clipboard=False
    try:
        assert not report['sourceElevated'],'Injection source must remain medium integrity'
        shell=ctypes.windll.shell32.ShellExecuteW
        shell.argtypes=[ctypes.c_void_p,ctypes.c_wchar_p,ctypes.c_wchar_p,ctypes.c_wchar_p,ctypes.c_wchar_p,ctypes.c_int]
        shell.restype=ctypes.c_void_p
        arguments=subprocess.list2cmdline(['-m','tests.manual.v2.elevated_paste_probe','--target',str(folder)])
        launched=shell(None,'runas',sys.executable,arguments,str(ROOT),0)
        if not launched or launched<=32:raise RuntimeError('UAC launch not accepted')
        wait(lambda:read(folder/'target.json').get('elevated') is True,120)
        target_pid=read(folder/'target.json')['pid'];report['targetPid']=target_pid
        wait(lambda:native.get_window_thread_process_id(native.get_foreground_window())[1]==target_pid,25)
        worker=subprocess.Popen([sys.executable,'-m','tests.manual.v2.native_rest_probe','--worker',str(folder),
            '--mode','normal','--target-pid',str(target_pid)],cwd=ROOT,env=os.environ.copy(),creationflags=subprocess.CREATE_NO_WINDOW)
        wait(lambda:worker.poll() is not None,15);assert worker.returncode==0
        attempt=read(folder/'worker.json');api=read(folder/'native-api.json');before=read(folder/'target.json');time.sleep(1.5);app.processEvents()
        after=read(folder/'target.json')
        report['checks']=dict(actualElevatedTarget=before.get('elevated') is True,
            mediumSource=not report['sourceElevated'],correctCommandStatus=attempt.get('attempt')==
                ('command_sent' if api.get('sentEvents')==api.get('expectedEvents')==4 else 'failed'),
            focusedTarget=before.get('editorFocused') and before.get('active'),
            noUnauthorizedPaste=before.get('characters')==after.get('characters')==0)
        report['attempt']=attempt;report['nativeAPI']=api;report['targetAfter']=after
        report['statusMeaning']='command_sent confirms only the native SendInput return count; it is not a document-insertion confirmation. No automatic retry.'
        report['result']='PASS_SCOPED' if all(report['checks'].values()) else 'FAIL'
    except Exception as error:
        report.update(result='FAIL',errorType=type(error).__name__)
    finally:
        if native.open_clipboard(0):
            try:own_clipboard=native.get_clipboard_data_unicode()==TEXT
            finally:native.close_clipboard()
        if own_clipboard:
            app.clipboard().setMimeData(original);app.processEvents()
            report['originalClipboardFormatsRestored']=all(app.clipboard().mimeData().data(fmt)==original.data(fmt) for fmt in formats)
        else:report['originalClipboardFormatsRestored']='Clipboard changed independently or injection never wrote; no overwrite'
        (folder/'stop.request').touch();save(output/'result.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='identity'}),flush=True)
    return 0 if report['result']=='PASS_SCOPED' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.target:
        if not a.target.resolve().is_relative_to(PROFILE_RUNTIME.resolve()):p.error('Owned target directory required')
        raise SystemExit(target(a.target))
    if a.output is None or not a.output.resolve().is_relative_to(ROOT/'build'):p.error('Project build output required')
    raise SystemExit(run(a.output.resolve()))
