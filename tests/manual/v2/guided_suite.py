"""Guided Windows operator workbench. Opening it never starts audio or a client.

python -m tests.manual.v2.guided_suite [--self-check]
Only deliberate Start launches one isolated source desktop. Continue records
human observations, never a qualification PASS. Each task can be repeated.
"""
import argparse
from datetime import UTC, datetime
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

from tests.manual.v2.suite_plan import (
    select_tasks, DEFERRED, ROOT, RUNTIME, PROFILE_RUNTIME, TARGET, PREPARE_SECONDS, SuiteRecord, owned_path, target_origin)
from tests.manual.v2.suite_session import save
from tests.manual.v2.suite_analysis import summarize
from tests.manual.v2.suite_progress import guide_progress, wake_stop_delay


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    parser.add_argument('--profile-runtime', action='store_true',
        help='Use dedicated Windows-profile runtime only after explicit human authorization; otherwise preview only')
    parser.add_argument('--tasks', nargs='+', help='Only these task IDs, each with its own Start')
    parser.add_argument('--server-info', type=Path, help='Saved current /api/v2/info in this repository; bind child Hello to its commit')
    args = parser.parse_args()
    try:
        TASKS = select_tasks(args.tasks)
    except ValueError as error:
        parser.error(str(error))
    server_info = None
    if args.server_info:
        info_path = args.server_info.resolve()
        if not info_path.is_relative_to(ROOT.resolve()):
            parser.error('Server identity evidence must be inside this project')
        server_info = json.loads(info_path.read_text(encoding='utf-8-sig'))
        from tests.manual.v2.verify_server_fix import check_identity
        if not check_identity(server_info, server_info.get('serverCommit')):
            parser.error('Incomplete or mismatched Pro-V2 identity evidence')
    if any(t.get('wake') for t in TASKS) and not server_info and not args.self_check:
        parser.error('Wake requalification requires current --server-info evidence')
    RUNTIME.mkdir(parents=True, exist_ok=True)
    base = PROFILE_RUNTIME if args.profile_runtime else RUNTIME
    folder = base/('suite-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6])
    folder.mkdir(parents=True)
    (folder/'tmp').mkdir()
    os.environ['TEMP'] = os.environ['TMP'] = str(folder/'tmp')
    os.environ['VOICESTT_CLIENT_HOME'] = str(folder/'ui-home')
    os.environ['VOICESTT_CLIENT_CONFIG'] = str(folder/'ui-home/config.yaml')
    from PySide6.QtCore import QTimer, Qt
    from PySide6.QtGui import QFont, QFontDatabase
    from PySide6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
        QPushButton, QPlainTextEdit, QListWidget, QComboBox, QScrollArea, QMessageBox)
    app = QApplication([])
    from voice_stt_client.ui.single_instance import SingleInstanceGuard
    workbench_guard = SingleInstanceGuard(r'Local\VoiceSTT_Qualification_Guided_Workbench')
    if not workbench_guard.acquire().acquired:
        raise RuntimeError('The guided workbench is already open; use its existing window')
    font = Path(os.environ.get('WINDIR', 'C:/Windows'))/'Fonts/segoeui.ttf'
    if app.platformName() == 'offscreen' and font.is_file():
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont('Segoe UI', 10))
    app.setStyleSheet('QWidget {background:#f7f8fb;color:#172b57;} QPushButton {padding:9px;} '
                     'QPlainTextEdit,QComboBox {background:white;}')
    record = SuiteRecord()
    index, child, attempt_folder, output_handle = 0, None, None, None
    step, phase, prepare_at, started_at = 0, 'preview', None, None
    device = None
    changes, paste_events = 0, []
    confirmed_steps = set()
    last_board = None
    closing = False
    stop_requested = False
    last_progress = {}
    user32 = __import__('ctypes').windll.user32
    user32.GetForegroundWindow.restype = __import__('ctypes').c_void_p
    class Window(QWidget):
        def closeEvent(self, event):
            nonlocal closing
            if child is not None and child.poll() is None:
                closing = True
                stop()
                event.ignore()
                return
            super().closeEvent(event)
    window = Window()
    window.setWindowTitle('AP-IV2-020 – geführte Resttests · Start / Wiederholen / Weiter')
    outer = QHBoxLayout(window)
    side = QVBoxLayout()
    progress = QLabel()
    side.addWidget(progress)
    tasks = QListWidget()
    tasks.setMinimumWidth(310)
    for task in TASKS:
        tasks.addItem('○ '+task['title'])
    tasks.setSelectionMode(QListWidget.SelectionMode.NoSelection)
    side.addWidget(tasks)
    remaining = QLabel('SEPARAT OFFEN\n\n'+'\n\n'.join(DEFERRED))
    remaining.setWordWrap(True)
    remaining.setStyleSheet('color:#626a78;font-size:11px;padding:5px;')
    scroll_side = QScrollArea()
    scroll_side.setWidgetResizable(True)
    scroll_side.setWidget(remaining)
    side.addWidget(scroll_side)
    side.addWidget(QLabel('✓ = Bedienversuch übernommen\nFachliche Auswertung erfolgt danach.'))
    outer.addLayout(side, 1)
    content = QVBoxLayout()
    outer.addLayout(content, 3)
    title = QLabel()
    title.setStyleSheet('font-size:23px;font-weight:bold')
    content.addWidget(title)
    target = QLabel('Testziel: '+TARGET+'\nManual-only · Wake aus · Follow-up 5 s · getrenntes Testprofil'+
                    '\nF8 / F9 / F11 bedeutet hier IMMER: Strg+Umschalt+F8 / F9 / F11.')
    target.setWordWrap(True)
    content.addWidget(target)
    status = QLabel('NOCH NICHT GESTARTET – Mikrofon und Client sind aus.')
    status.setWordWrap(True)
    status.setStyleSheet('background:#e5efff;padding:12px;font-weight:bold;font-size:17px')
    content.addWidget(status)
    phrase = QLabel()
    phrase.setWordWrap(True)
    phrase.setTextFormat(Qt.TextFormat.PlainText)
    phrase.setStyleSheet('background:#effaf1;color:#117333;padding:14px;font-weight:bold;font-size:24px;border:2px solid #117333')
    content.addWidget(phrase)
    steps_widget = QWidget()
    steps_layout = QVBoxLayout(steps_widget)
    steps_layout.setContentsMargins(0, 0, 0, 0)
    labels = []
    content.addWidget(steps_widget)
    expected = QLabel()
    expected.setWordWrap(True)
    content.addWidget(expected)

    class Editor(QPlainTextEdit):
        def insertFromMimeData(self, source):
            text = source.text() if source.hasText() else ''
            paste_events.append(dict(timeUtc=datetime.now(UTC).isoformat(), characters=len(text),
                                     sha256=hashlib.sha256(text.encode()).hexdigest()))
            super().insertFromMimeData(source)
    editor = Editor()
    editor.setPlaceholderText('Nur hier werden vereinbarte Testsätze eingefügt. Beim Sprechen hier fokussiert bleiben.')
    editor.setMinimumHeight(100)
    content.addWidget(editor)
    start_button = QPushButton('Aufgabe starten')
    advance = QPushButton('Beobachtung / Geräteaktion erledigt →')
    finish_button = QPushButton('Versuch beenden / auswerten')
    for button in (start_button, advance, finish_button):
        content.addWidget(button)
    utilities = QHBoxLayout()
    settings = QPushButton('Einstellungen öffnen')
    reconnect = QPushButton('Diesen Testclient wiederverbinden')
    utilities.addWidget(settings)
    utilities.addWidget(reconnect)
    content.addLayout(utilities)
    observation = QComboBox()
    observation.addItems(['Bitte Ergebnis wählen', 'Wie erwartet', 'Problem / Abweichung', 'Nicht sicher / nicht beobachtet'])
    notes = QPlainTextEdit()
    notes.setPlaceholderText('Beobachtung / LED / Sound / Overlay / Timingwunsch – keine Zugangsdaten. Nach dem Versuch ausfüllen.')
    notes.setMaximumHeight(65)
    content.addWidget(observation)
    content.addWidget(notes)
    review_row = QHBoxLayout()
    repeat = QPushButton('Wiederholen')
    accept = QPushButton('Übernehmen → Weiter')
    skip = QPushButton('Offen lassen → Weiter')
    for button in (repeat, accept, skip):
        review_row.addWidget(button)
    content.addLayout(review_row)
    window.resize(1280, 1000)

    def write_record():
        save(folder/'report.json', dict(target=TARGET, sourceOnly=True, result='NOT_PROVEN_PENDING_AGENT_REVIEW',
             updatedAtUtc=datetime.now(UTC).isoformat(), currentTask=index,
             attempts=record.attempts, deferred=DEFERRED,
             boundary='Human acceptance is not a PASS. No frozen-build, full M-case or server-FIX claim.'))
        save(RUNTIME/'active-suite.json', dict(pid=os.getpid(), folder=str(folder),
             state=str(folder/'editor-state.json'), target=TARGET,
             clientStarted=child is not None and child.poll() is None))

    def board(active, origin='ui'):
        nonlocal step, last_board
        step = active
        signature = (index, active, tuple(sorted(confirmed_steps)))
        if signature != last_board:
            with (folder/'operator-events.jsonl').open('a',encoding='utf8') as handle:
                handle.write(json.dumps(dict(timeUtc=datetime.now(UTC).isoformat(),task=TASKS[index]['id'],
                    activeStep=active,confirmedSteps=sorted(confirmed_steps),origin=origin))+'\n')
            last_board = signature
        for row, label in enumerate(labels):
            current, done = row == active, row in confirmed_steps
            label.setText(('▶  ' if current else '✓  ' if done else '○  ' if row < active else f'{row+1}.  ')+label.property('instructionText'))
            label.setStyleSheet('padding:8px;font-size:14px;border-radius:4px;'+(
                'color:#172b57;background:#dceaff;border:2px solid #2563eb;font-weight:bold' if current else
                'color:#41664b;background:#edf5ee' if done else 'color:#818895;background:#eef0f3'))

    def preview():
        nonlocal phase, prepare_at, stop_requested
        phase, prepare_at = 'preview', None
        stop_requested = False
        last_progress.clear()
        confirmed_steps.clear()
        task = TASKS[index]
        finish_button.setText('Versuch beenden (Ruheprüfung wird abgewartet)' if task.get('wake') else 'Versuch beenden / auswerten')
        tasks.setCurrentRow(index)
        title.setText(task['title'])
        phrase.setText(task['phrase'])
        expected.setText('Erwartung: '+task['expected'])
        for label in labels:
            steps_layout.removeWidget(label)
            label.deleteLater()
        labels.clear()
        for text in ['Alles vorher lesen; erst dann selbst Start drücken.',
                     'Client / Modelle starten; danach 10 Sekunden entspannt bereitmachen.', *task['steps'],
                     'Versuch beenden, Ergebnis wählen und Wiederholen oder Weiter.']:
            label = QLabel()
            label.setWordWrap(True)
            label.setProperty('instructionText', text)
            steps_layout.addWidget(label)
            labels.append(label)
        board(0)
        editor.clear()
        notes.clear()
        observation.setCurrentIndex(0)
        progress.setText(f'Aufgabe {index+1} von {len(TASKS)}\nKein automatischer Folgestart')
        status.setText('VORHER LESEN · Start in deinem Tempo · Mikrofon und Client aus' if args.profile_runtime else
                       'VORSCHAU · Realstart wartet auf Freigabe der getrennten Windows-Testablage.')
        for button in (advance, finish_button, settings, reconnect, repeat, accept):
            button.setEnabled(False)
        skip.setEnabled(True)
        start_button.setEnabled(args.profile_runtime and not args.self_check)
        observation.setEnabled(False)
        notes.setEnabled(False)
        write_record()

    def command(action):
        if child is not None and child.poll() is None:
            inbox = attempt_folder/'commands'
            inbox.mkdir(exist_ok=True)
            save(inbox/f'{time.monotonic_ns()}.json', dict(action=action))

    def start():
        nonlocal child, attempt_folder, output_handle, phase, started_at, prepare_at, device
        if not args.profile_runtime or phase != 'preview' or (child is not None and child.poll() is None):
            return
        from voice_stt_client.core.audio_capture import AudioCapture
        devices = AudioCapture.list_devices()
        available = [value for value in devices if 'respeaker' in value['name'].lower()]
        if not available:
            status.setText('ReSpeaker nicht verfügbar. Anschließen und erneut Start drücken; kein anderes Mikrofon gewählt.')
            return
        device = available[0]
        attempt = record.start(TASKS[index]['id'])
        attempt_folder = folder/attempt['attemptId']
        attempt_folder.mkdir()
        attempt['folder'] = str(attempt_folder)
        attempt['editorBeforeSha256'] = hashlib.sha256(editor.toPlainText().encode()).hexdigest()
        editor.clear()
        paste_events.clear()
        phase, prepare_at, started_at = 'starting', None, time.monotonic()
        confirmed_steps.add(0)
        start_button.setEnabled(False)
        skip.setEnabled(False)
        finish_button.setEnabled(True)
        board(1)
        editor.setFocus()
        write_state()
        output_handle = (attempt_folder/'process.log').open('w', encoding='utf8')
        argv = [sys.executable, '-u', '-m', 'tests.manual.v2.suite_session',
                '--folder', str(attempt_folder), '--editor-state', str(folder/'editor-state.json'),
                '--target', TARGET, '--task', TASKS[index]['id'], '--device', str(device['index'])]
        if server_info:
            argv += ['--expected-server-commit',server_info['serverCommit']]
        try:
            child = subprocess.Popen(argv, cwd=ROOT, stdout=output_handle, stderr=subprocess.STDOUT)
        except OSError as error:
            output_handle.close()
            record.stopped(-1)
            phase = 'review'
            status.setText(f'Clientstart fehlgeschlagen: {type(error).__name__}. Wiederholung möglich.')
            review_controls()
        write_record()

    def next_step():
        if phase == 'running' and advance.isEnabled() and step < len(labels)-1:
            confirmed_steps.add(step)
            board(step+1,'human_observation')
            editor.setFocus()
            if step == len(labels)-1:
                advance.setEnabled(False)

    def stop():
        nonlocal phase, stop_requested
        if child is not None and child.poll() is None:
            delay=wake_stop_delay(TASKS[index]['id'],last_progress,closing=closing)
            if phase=='running' and delay:
                stop_requested=True
                finish_button.setEnabled(False)
                status.setText(f'Beenden vorgemerkt · Noch {delay} s schweigen. Die laufende Ruheprüfung endet zuerst. Fenster schließen bleibt Abbrechen.')
                return
            stop_requested=False
            command('stop')
            phase = 'stopping'
            finish_button.setEnabled(False)
            advance.setEnabled(False)
            status.setText('Testclient wird regulär beendet. Nächste Aufgabe wartet auf deinen Start.')

    def review_controls():
        board(len(labels)-1)
        for button in (repeat, accept, skip):
            button.setEnabled(True)
        for button in (start_button, advance, finish_button, settings, reconnect):
            button.setEnabled(False)
        observation.setEnabled(True)
        notes.setEnabled(True)

    def decide(decision):
        nonlocal index, phase
        if phase not in ('review', 'preview'):
            return
        if phase == 'preview':
            if decision != 'skip':
                return
            record.start(TASKS[index]['id'])
            record.stopped(None)
        if decision == 'accept' and observation.currentIndex() == 0:
            status.setText('Bitte Ergebnis auswählen; „nicht sicher“ ist ebenfalls möglich.')
            return
        record.decide(decision, observation.currentText(), notes.toPlainText())
        tasks.item(index).setText(('↻ ' if decision == 'repeat' else '○ ' if decision == 'skip' else '✓ ')+TASKS[index]['title'])
        write_record()
        if decision != 'repeat':
            index += 1
        if index == len(TASKS):
            phase = 'done'
            progress.setText(f'{len(TASKS)} Aufgaben durchgesehen')
            status.setText('FERTIG – TESTCLIENT AUS · Alle Versuche gespeichert. Jetzt im Chat „Durchlauf fertig“ melden.')
            for button in (start_button, advance, finish_button, repeat, accept, skip, settings, reconnect):
                button.setEnabled(False)
            write_record()
            return
        preview()

    def write_state():
        value = editor.toPlainText()
        save(folder/'editor-state.json', dict(pid=os.getpid(), timeUtc=datetime.now(UTC).isoformat(),
             foreground=int(user32.GetForegroundWindow() or 0) == int(window.winId()),
             editorHasFocus=editor.hasFocus(), phase=phase, activeStep=step,
             confirmedSteps=sorted(confirmed_steps), characters=len(value),
             sha256=hashlib.sha256(value.encode()).hexdigest()))

    def tick():
        nonlocal phase, prepare_at, child
        write_state()
        ui_command = folder/'ui-command.json'
        if ui_command.exists():
            value = json.loads(ui_command.read_text(encoding='utf8'))
            ui_command.unlink()
            if value.get('action') == 'close':
                window.close()
                return
        if child is None:
            return
        code = child.poll()
        if code is not None and record.active is not None and 'exitCode' not in record.active:
            record.stopped(code)
            record.active.update(editorAfter=dict(characters=len(editor.toPlainText()),
                sha256=hashlib.sha256(editor.toPlainText().encode()).hexdigest()), nativePastes=list(paste_events))
            record.active['observed'] = summarize(attempt_folder)
            (attempt_folder/'test-editor.txt').write_text(editor.toPlainText(), encoding='utf8')
            output_handle.close()
            phase = 'review'
            status.setText('CLIENT AUS – Ergebnis prüfen und auswählen. '+('' if code == 0 else f'Prozessfehler {code}; Nachweis offen.'))
            review_controls()
            write_record()
            if closing:
                window.close()
            return
        if code is not None or phase in ('review', 'preview', 'done'):
            return
        path = attempt_folder/'status.json'
        if path.exists():
            try:
                live = json.loads(path.read_text(encoding='utf8'))
            except (PermissionError, FileNotFoundError, json.JSONDecodeError):
                return
            age = abs((datetime.now(UTC)-datetime.fromisoformat(live['timeUtc'])).total_seconds())
            ready = age < 3 and live.get('ready') and live.get('audioAvailable')
            if phase == 'starting':
                if ready:
                    prepare_at = prepare_at or time.monotonic()
                    left = max(0, math.ceil(PREPARE_SECONDS-(time.monotonic()-prepare_at)))
                    status.setText(f'CLIENT BEREIT · Noch {left} s bereitmachen · Noch nicht sprechen.')
                    if left == 0:
                        phase = 'running'
                        confirmed_steps.add(1)
                        board(2)
                        settings.setEnabled(True)
                        reconnect.setEnabled(True)
                else:
                    prepare_at = None
                    status.setText('CLIENT STARTET / MODELLE LADEN · Bitte warten · '+str(live.get('transport', ''))+' · '+str(live.get('reason', '')))
            if phase == 'running':
                last_progress.clear()
                last_progress.update(live.get('operatorProgress',{}))
                guide = guide_progress(TASKS[index]['id'],last_progress,len(paste_events))
                if stop_requested and not wake_stop_delay(TASKS[index]['id'],last_progress):
                    stop()
                    return
                confirmed_steps.update(guide['confirmed'])
                board(max(step,guide['active']),'observed_client_events')
                advance.setEnabled(guide['manualAllowed'] and step < len(labels)-1)
                status.setText(('CLIENT BEREIT' if ready else 'WARTEN / AUDIO ODER VERBINDUNG FEHLT')+
                    f" · Phase: {live.get('phase')} · Audio: {live.get('audioAvailable')} · Generation: {live.get('generation')}"+
                    f"\nSession: {live.get('sessionId')} · {live.get('reason', '')}"+
                    (f"\nWarten: {guide['waitRemaining']} s" if guide['waitRemaining'] is not None else '')+
                    ('\n'+guide['notice'] if guide['notice'] else ''))
                if stop_requested:
                    status.setText(status.text()+'\nBEENDEN VORGEMERKT · Ruheprüfung wird noch abgeschlossen; weiter schweigen.')
        elif phase == 'starting':
            status.setText(f'CLIENT STARTET · {int(time.monotonic()-started_at)} s · Modellstart darf mehrere Minuten dauern.')

    start_button.clicked.connect(start)
    advance.clicked.connect(next_step)
    finish_button.clicked.connect(stop)
    repeat.clicked.connect(lambda: decide('repeat'))
    accept.clicked.connect(lambda: decide('accept'))
    skip.clicked.connect(lambda: decide('skip'))
    settings.clicked.connect(lambda: command('settings'))
    reconnect.clicked.connect(lambda: (command('reconnect'), editor.setFocus()))
    preview()
    timer = QTimer()
    timer.timeout.connect(tick)
    timer.start(250)
    window.show()
    write_state()
    save(RUNTIME/'active-suite.json', dict(pid=os.getpid(), folder=str(folder),
        state=str(folder/'editor-state.json'), target=TARGET, clientStarted=False))
    from scripts.qualify_v2_real import identity
    proof = args.server_info.resolve() if args.server_info else ROOT/'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/target-and-deferral-20261019/selected-server-identity.json'
    save(folder/'identity.json', dict(client=identity(), target=TARGET,
        serverProvenance=str(proof.relative_to(ROOT)), serverProvenanceSha256=hashlib.sha256(proof.read_bytes()).hexdigest(),
        selectedServerInfo=server_info,
        boundary='Source desktop only; deployment evidence is timestamped and not a live wire commit assertion.'))
    print(json.dumps(dict(uiPid=os.getpid(), folder=str(folder), clientStarted=False)), flush=True)
    if args.self_check:
        def check():
            nonlocal child, phase, attempt_folder, record
            assert child is None and record.active is None and phase == 'preview'
            assert phrase.text() == TASKS[0]['phrase'] and len(labels) == len(TASKS[0]['steps'])+3
            assert not advance.isEnabled() and not accept.isEnabled()
            if TASKS[0].get('wake'):
                assert 'Ruheprüfung' in finish_button.text()
            assert all(label.text() for label in labels)
            # Exercise actual JSON polling, not only the reducer or layout.
            class SimulatedChild:
                def poll(self):
                    return None
            child=SimulatedChild()
            attempt_folder=folder/'simulated-client-status'
            attempt_folder.mkdir()
            phase='running'
            observed = {'counts':{'activation.started':1,'segment.recording_started':1}}
            save(attempt_folder/'status.json',dict(timeUtc=datetime.now(UTC).isoformat(),
                 ready=True,audioAvailable=True,generation=1,phase='recording',operatorProgress=observed))
            tick()
            assert step==3 and labels[3].text().startswith('▶')
            assert labels[2].text().startswith('✓')
            assert not advance.isEnabled(), 'F8/speech progression must not need a Next click'
            review_controls()
            assert not labels[3].text().startswith('✓'), 'Review must not fabricate F9 completion'
            if TASKS[0].get('wake'):
                phase='running'
                observed={'counts':{'activation.started':1,'activation.input_closed':1},
                    'closedReason':'timed_out','postCloseQuietRemaining':3}
                save(attempt_folder/'status.json',dict(timeUtc=datetime.now(UTC).isoformat(),
                    ready=True,audioAvailable=True,generation=1,phase='idle',operatorProgress=observed))
                tick()
                finish_button.setEnabled(True)
                finish_button.click()
                assert stop_requested and phase=='running'
                assert not (attempt_folder/'commands').exists(), 'Quiet tail must continue after explicit Finish request'
                observed['postCloseQuietRemaining']=0
                save(attempt_folder/'status.json',dict(timeUtc=datetime.now(UTC).isoformat(),
                    ready=True,audioAvailable=True,generation=1,phase='idle',operatorProgress=observed))
                tick()
                assert phase=='stopping' and len(list((attempt_folder/'commands').glob('*.json')))==1
            child=None
            phase='preview'
            confirmed_steps.clear()
            record=SuiteRecord()
            # Explicitly skipping is recorded, never launches the next task.
            decide('skip')
            assert index == 1 and phase == 'preview' and child is None
            assert record.attempts[0]['decision'] == 'skip'
            assert record.attempts[0]['evaluation'].startswith('NOT_PROVEN')
            app.processEvents()
            assert phrase.text() == TASKS[1]['phrase']
            assert labels[2].property('instructionText') == TASKS[1]['steps'][0]
            window.grab().save(str(folder/'preview.png'))
            save(folder/'ui-self-check.json', dict(result='PASS', noClientStarted=child is None,
                quietStopDeferVerified=bool(TASKS[0].get('wake')),
                scope='Qt preview/layout/explicit skip; no real model/audio/paste qualification'))
            print('GUIDED_UI_SELF_CHECK_PASS', flush=True)
            app.quit()
        def checked():
            try:
                check()
            except Exception:
                import traceback
                traceback.print_exc()
                app.exit(1)
        QTimer.singleShot(200, checked)
    try:
        return app.exec()
    finally:
        workbench_guard.release()


if __name__ == '__main__':
    raise SystemExit(main())
