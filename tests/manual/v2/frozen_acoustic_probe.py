"""Unmodified qualified EXE with a real Windows input endpoint and native paste.

Agent/operator presses actual Windows hotkey for manual case and clicks the
fixture buttons in this OWN empty editor. No PCM/clipboard monkeypatch in EXE.
Playback is audible. Stop own client immediately if test target loses focus.
Stereomix is a separate endpoint, never a ReSpeaker acoustic qualification.
"""
import argparse,ctypes,hashlib,json,os,sqlite3,subprocess,time,uuid,winsound
from pathlib import Path
from tests.manual.v2.suite_plan import ROOT,PROFILE_RUNTIME,TARGET
from tests.manual.v2.suite_session import prepare_profile,save
from tests.manual.v2.verify_server_fix import FIXTURES,read_info,check_identity


def expected_append(baseline, history, history_before):
    return baseline+''.join(t if t[-1:].isspace() else t+' ' for t in history[history_before:])


def all_cases_passed(cases, names):
    return all(any(c['name']==name and c.get('nativeTextMatchesHistory') for c in cases) for name in names)


def main(args):
    folder=PROFILE_RUNTIME/('frozen-acoustic-'+uuid.uuid4().hex[:12]);(folder/'tmp').mkdir(parents=True)
    os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),VOICESTT_CLIENT_CONFIG=str(folder/'profile.yaml'),
        TEMP=str(folder/'tmp'),TMP=str(folder/'tmp'),QT_QPA_PLATFORM='windows')
    from PySide6.QtCore import QMimeData,QTimer
    from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QLabel,QPushButton,QPlainTextEdit
    from tests.manual.v2.step_board import StepBoard
    from voice_stt_client.core.audio_capture import AudioCapture
    from voice_stt_client.core.text_injector import CtypesWindowsInjectionBackend
    from scripts.qualify_v2_real import identity
    exe=ROOT/'dist-iv2-020-usb/voice-stt-client.exe'
    assert hashlib.sha256(exe.read_bytes()).hexdigest()=='e20059f6dff1279cb23fb01576d447fb285aa94cb270d71968b8430a063a15fc'
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenMutexW.argtypes=[ctypes.c_uint,ctypes.c_int,ctypes.c_wchar_p];kernel.OpenMutexW.restype=ctypes.c_void_p
    if kernel.OpenMutexW(0x100000,False,r'Local\RealtimeSTT_Client_7F51A2C9'):raise RuntimeError('Existing client: no launch')
    device=next(d for d in AudioCapture.list_devices() if 'respeaker' in d['name'].lower() and d['default_samplerate']==16000)
    if args.device is not None:device=next(d for d in AudioCapture.list_devices() if d['index']==args.device)
    config=prepare_profile(folder,TARGET,dict(secondary='finish',both=True,sounds=True),device['index'])
    if args.device is not None:
        # Use the endpoint's supported native format, with truthful wire metadata.
        # This is a different input device, never a ReSpeaker hardware proof.
        config.audio.sample_rate=int(device['default_samplerate'])
        config.audio.channels=device['channels']
    if args.reinsert_history:
        if not args.reinsert_history.resolve().is_relative_to(PROFILE_RUNTIME.resolve()):raise ValueError('Only own test history')
        (folder/'client').mkdir(exist_ok=True)
        with sqlite3.connect(f'file:{args.reinsert_history.as_posix()}?mode=ro',uri=True) as source,sqlite3.connect(folder/'client/history.sqlite') as target_db:source.backup(target_db)
        config.v2_profile.update(manual=True,wake_word=False,wake_word_ids=[])
    config.event_stream.enabled=False;config.hotkey.auto_start=False;config.clipboard.restore_previous=False;config.save(folder/'profile.yaml')
    before=read_info();assert check_identity(before,args.expected_server_commit)
    args.output.mkdir(parents=True,exist_ok=False)
    app=QApplication([]);app.setQuitOnLastWindowClosed(True)
    window=QWidget();window.setWindowTitle('AP-IV2-020 – endgültige EXE / eigener Akustiktest')
    layout=QVBoxLayout(window);label=QLabel('Client startet. Eigener leerer Editor – autonome Akustikprüfung.');layout.addWidget(label)
    instructions=QLabel('');instructions.setWordWrap(True);layout.addWidget(instructions)
    if args.human:
        instructions.setText('Beide Aufgaben vorher lesen, jeweils selbst starten.\n'
            '1: Start → Strg+Umschalt+F8 → „Der blaue Becher steht auf dem Tisch.“ → Strg+Umschalt+F9.\n'
            '2: Start → „Alexa die grüne Lampe steht neben dem Fenster.“ → schweigen.\n'
            'Jede Aufgabe kann wiederholt oder mit Abweichung beendet werden. Keine automatische Folgeaufgabe.')
    phrase=QLabel('');phrase.setStyleSheet('font-size:22px;font-weight:bold;color:#70e080;padding:12px;');layout.addWidget(phrase)
    board=StepBoard();layout.addWidget(board);board.setVisible(args.human)
    if args.human:
        board.configure('wake' if args.only=='wake' else 'manual')
        if args.only=='wake':
            board.steps[5]='Schweigen · der Client beendet die Eingabe selbst'
            board.set_stage(0)
            instructions.setText('Einmal Start klicken, danach auf die leuchtende Sprechzeile warten. '
                'Nur den grünen Satz einmal sprechen und anschließend schweigen. Keine Tastenkombination. '
                'Bei fehlender Einfügung: Versuch beenden / Wiederholen. Es gibt keine automatische Folgeaufgabe.')
            phrase.setText('Alexa die grüne Lampe steht neben dem Fenster.')
    class ObservedEditor(QPlainTextEdit):
        key_count=0
        def keyPressEvent(self,event):
            self.key_count+=1
            super().keyPressEvent(event)
    editor=ObservedEditor();layout.addWidget(editor);buttons=[]
    native=CtypesWindowsInjectionBackend();original=QMimeData();formats=[];mime=app.clipboard().mimeData()
    if mime:
        for fmt in mime.formats():
            data=mime.data(fmt)
            if len(data)>64*1024*1024:raise RuntimeError('Clipboard preservation limit')
            original.setData(fmt,data);formats.append(fmt)
    def launch():
        return subprocess.Popen([str(exe),'--config',str(folder/'profile.yaml')],cwd=folder,env=os.environ.copy(),creationflags=subprocess.CREATE_NO_WINDOW)
    # In the operator flow, no microphone/client starts before the explicit click.
    child=None if args.human else launch()
    report=dict(result='RUNNING',pid=os.getpid(),runtimeFolder=str(folder),bootloaderPid=child.pid if child else None,identity=identity(),
        device=device,infoBefore=before,exeSha256=hashlib.sha256(exe.read_bytes()).hexdigest(),cases=[],scope=__doc__)
    from tests.manual.v2.process_security_probe import process_security
    report['targetSecurity']=process_security(os.getpid())
    product_pid=None;armed=False;selected=None;started=time.monotonic();history=[]
    def logs():
        db=folder/'client/observability.sqlite3'
        if not db.exists():return []
        try:
            with sqlite3.connect(f'file:{db.as_posix()}?mode=ro',uri=True,timeout=.1) as c:
                return c.execute('select type,details_json,activation_id from logs order by id').fetchall()
        except sqlite3.Error:return []
    def play(name):
        nonlocal armed,selected,child
        if selected is not None:return
        if native.get_window_thread_process_id(native.get_foreground_window())[1]!=os.getpid():return
        selected=dict(name=name,began=time.monotonic()-started,historyBefore=len(history),
            editorBefore=editor.toPlainText());armed=True;editor.setFocus()
        if args.human:
            if child is None:
                child=launch();report['bootloaderPid']=child.pid
            selected['stimulusKind']='human_live'
            board.configure('manual' if name=='negative_speech' else 'wake')
            if name!='negative_speech':board.steps[5]='Schweigen · der Client beendet die Eingabe selbst'
            board.set_stage(1)
            phrase.setText('Der blaue Becher steht auf dem Tisch.' if name=='negative_speech' else 'Alexa die grüne Lampe steht neben dem Fenster.')
            return
        candidates=list(FIXTURES.glob('*'+name+'*.wav'))
        if len(candidates)!=1:raise RuntimeError('Fixture must resolve uniquely')
        selected['fixtureSha256']=hashlib.sha256(candidates[0].read_bytes()).hexdigest()
        winsound.PlaySound(str(candidates[0]),winsound.SND_FILENAME|winsound.SND_ASYNC|winsound.SND_NODEFAULT)
    tasks=(('Aufgabe 1 starten – F8 / grünen Satz sprechen / F9','negative_speech'),('Aufgabe 2 starten – grünen Alexa-Satz sprechen / schweigen','alexa_direct')) if args.human else (('1 – manuelle Aufnahme: Sprachprobe abspielen','negative_speech'),('2 – Alexa mit Nutzsatz abspielen','alexa_direct'),('3 – Hey Jarvis mit Nutzsatz abspielen','jarvis_direct'))
    if args.only:tasks=tuple(task for task in tasks if (task[1]=='negative_speech')==(args.only=='manual'))
    if len(tasks)==1:tasks=(('Start – eine Sprachprobe',tasks[0][1]),)
    for text,name in tasks:
        button=QPushButton(text);button.clicked.connect(lambda checked=False,name=name:play(name));layout.addWidget(button);buttons.append(button)
    def release_attempt():
        nonlocal selected,armed
        if selected:
            selected.update(ended=time.monotonic()-started,nativeTextMatchesHistory=False,
                disposition='operator_finished_or_retry_requested')
            report['cases'].append(selected);selected=None
        armed=child is not None
        phrase.setText('Aufgabe erneut starten oder nächste Aufgabe wählen. Keine erneute Sprache ohne eigenen Start.')
    retry=QPushButton('Versuch beenden / Wiederholen oder Weiter freigeben')
    retry.clicked.connect(release_attempt);layout.addWidget(retry)
    stop=QPushButton('Test beenden und sichern');layout.addWidget(stop);stop.clicked.connect(app.quit)
    window.resize(860,450);window.show();window.activateWindow();editor.setFocus()
    def tick():
        nonlocal product_pid,armed,selected,history
        rows=logs();counts={};states=[];phase=None
        for kind,details,aid in rows:
            value=json.loads(details) if details else {}
            if kind=='client.app.started':product_pid=value.get('process_id')
            if kind=='client.v2.transport_state':states.append(value.get('state'))
            if kind=='client.domain.observed':
                event=value.get('eventType');counts[event]=counts.get(event,0)+1;phase=value.get('phase')
        if armed and native.get_window_thread_process_id(native.get_foreground_window())[1]!=os.getpid():
            report['result']='ABORTED_TARGET_LOST_FOCUS';app.quit();return
        db=folder/'client/history.sqlite'
        try:
            with sqlite3.connect(f'file:{db.as_posix()}?mode=ro',uri=True,timeout=.1) as c:history=[r[0] for r in c.execute('select text from history_entries order by timestamp')]
        except sqlite3.Error:pass
        if selected and len(history)>selected['historyBefore'] and phase=='idle':
            expected=expected_append(selected['editorBefore'],history,selected['historyBefore'])
            if editor.toPlainText()==expected:
                selected.update(ended=time.monotonic()-started,historyAfter=len(history),nativeTextMatchesHistory=True)
                report['cases'].append(selected);selected=None
                phrase.setText('Einfügung bestätigt. Nächste Aufgabe selbst starten oder Test beenden.')
                if args.human:
                    board.set_stage(7)
                    if all_cases_passed(report['cases'],[name for _,name in tasks]):QTimer.singleShot(1500,app.quit)
        if args.human and selected:
            if states and states[-1]=='ready' and board.active==1:
                selected['readyAt']=time.monotonic()-started;board.set_stage(2,8)
            if board.active==2 and time.monotonic()-started-selected.get('readyAt',float('inf'))>=8:board.set_stage(3)
            if phase=='segment_active':board.set_stage(4)
            if phase=='followup_wait':board.set_stage(5)
            if phase=='idle' and len(history)>selected['historyBefore']:board.set_stage(6)
        retry.setEnabled(phase in ('idle',None))
        for button in buttons:button.setEnabled(selected is None and (child is None or bool(states) and states[-1]=='ready'))
        status=dict(states=states[-4:],phase=phase,counts=counts,historyEntries=len(history),editorCharacters=len(editor.toPlainText()),
            selected=selected,productPid=product_pid,realCases=report['cases'],editorFocused=editor.hasFocus(),keyPresses=editor.key_count)
        if product_pid and 'sourceSecurity' not in report:report['sourceSecurity']=process_security(product_pid)
        label.setText('Startbereit – Client beginnt erst beim Klick' if child is None else 'CLIENT BEREIT' if states and states[-1]=='ready' else 'Client startet – bitte warten')
        label.setStyleSheet('font-size:20px;font-weight:bold;padding:10px;color:#70e080;' if states and states[-1]=='ready' else 'font-size:20px;font-weight:bold;padding:10px;color:#ffcf70;')
        report['status']=status;save(args.output/'result.json',report)
        if time.monotonic()-started>(1800 if args.human else 240):report['result']='TIMEOUT';app.quit()
    timer=QTimer();timer.timeout.connect(tick);timer.start(150)
    try:app.exec()
    finally:
        winsound.PlaySound(None,winsound.SND_PURGE)
        for pid in (product_pid,child.pid if child else None):
            if pid:
                kernel.OpenProcess.argtypes=[ctypes.c_uint,ctypes.c_int,ctypes.c_uint];kernel.OpenProcess.restype=ctypes.c_void_p
                handle=kernel.OpenProcess(1,False,pid)
                if handle:
                    kernel.TerminateProcess.argtypes=[ctypes.c_void_p,ctypes.c_uint];kernel.TerminateProcess(handle,0)
                    kernel.CloseHandle.argtypes=[ctypes.c_void_p];kernel.CloseHandle(handle)
        expected_last=history[-1] if history else None
        if expected_last and native.open_clipboard(0):
            try:owned=native.get_clipboard_data_unicode() in (expected_last,expected_last+' ')
            finally:native.close_clipboard()
            if owned:
                app.clipboard().setMimeData(original);app.processEvents()
                report['clipboardRestored']=all(app.clipboard().mimeData().data(fmt)==original.data(fmt) for fmt in formats)
        after=read_info();report.update(infoAfter=after,identityStable=before==after)
        if report['result']=='RUNNING':report['result']='PASS_SCOPED' if all_cases_passed(report['cases'],[name for _,name in tasks]) and before==after else 'NOT_PROVEN'
        save(args.output/'result.json',report)
    return 0 if report['result']=='PASS_SCOPED' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--expected-server-commit',required=True);p.add_argument('--human',action='store_true');p.add_argument('--reinsert-history',type=Path);p.add_argument('--device',type=int);p.add_argument('--only',choices=('manual','wake'));a=p.parse_args()
    if not a.output.resolve().is_relative_to(ROOT/'build'):p.error('Project build output required')
    raise SystemExit(main(a))
