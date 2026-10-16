"""Separate real Windows text target. Test content remains outside Git.

No clipboard writes, input injection, global keys, product configuration or
elevation. The human focuses this window once. JSON diagnostics remove the
need for the operator to collect logs. --self-check is only a helper precheck.
"""
import argparse
import ctypes
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import time

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget


def run(self_check=False):
    root = Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020/editors'/str(os.getpid())
    root.mkdir(parents=True, exist_ok=False)
    app = QApplication([])
    def diagnostic(kind, **fields):
        with (root/'events.jsonl').open('a', encoding='utf8') as handle:
            handle.write(json.dumps(dict(kind=kind, timeUtc=datetime.now(UTC).isoformat(),
                monotonic=time.monotonic(), **fields), ensure_ascii=True)+'\n')

    class TestEditor(QPlainTextEdit):
        def keyPressEvent(self, event):
            if event.key() == Qt.Key.Key_V and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                diagnostic('paste_key', shiftHeld=bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier),
                           altHeld=bool(event.modifiers() & Qt.KeyboardModifier.AltModifier))
            super().keyPressEvent(event)

        def insertFromMimeData(self, source):
            text = source.text() if source.hasText() else ''
            diagnostic('paste_mime', hasText=source.hasText(), characters=len(text),
                       sha256=hashlib.sha256(text.encode()).hexdigest())
            super().insertFromMimeData(source)

    window = QWidget()
    window.setWindowTitle('AP-IV2-020 – leerer Testeditor')
    layout = QVBoxLayout(window)
    elevated = bool(ctypes.windll.shell32.IsUserAnAdmin())
    layout.addWidget(QLabel('Testziel '+('mit erhöhten Rechten' if elevated else 'mit normalen Rechten')+
        '. Nur vereinbarte Testsätze verwenden. Die aktuelle Aktion steht direkt darunter.'))
    instruction = QLabel('VORBEREITUNG\nDie Aufgabe und der vollständige Satz erscheinen vor dem Start.')
    instruction.setWordWrap(True)
    instruction.setStyleSheet('font-size: 18px; padding: 8px;')
    layout.addWidget(instruction)
    phrase = QLabel('Der Testsatz erscheint hier vor dem Start.')
    phrase.setWordWrap(True)
    phrase.setTextFormat(Qt.TextFormat.PlainText)
    phrase.setStyleSheet('font-size: 28px; font-weight: bold; color: #117333; background: #effaf1; padding: 16px; border: 2px solid #117333;')
    layout.addWidget(phrase)
    start_button = QPushButton('Vorbereitung läuft')
    start_button.setEnabled(False)
    layout.addWidget(start_button)
    repeat_button = QPushButton('Aufgabe wiederholen')
    accept_button = QPushButton('Versuch übernehmen / weiter')
    abort_button = QPushButton('Versuch abbrechen und neu vorbereiten')
    for button in (repeat_button, accept_button, abort_button):
        button.setEnabled(False)
        layout.addWidget(button)
    editor = TestEditor()
    editor.setPlaceholderText('Hier erscheinen die finalen Transkriptionen.')
    layout.addWidget(editor)
    window.resize(1100, 850)
    foreground_window = ctypes.windll.user32.GetForegroundWindow
    foreground_window.restype = ctypes.c_void_p
    foreground_process = ctypes.windll.user32.GetWindowThreadProcessId
    foreground_process.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    foreground_process.restype = ctypes.c_ulong
    changes = 0
    last_state = None
    operator_ready = False
    task_id = None
    start_sequence = 0
    clear_on_start = True
    restore_on_start = None
    phase = 'preparing'
    request_sequence = 0
    request_action = None
    request_task_id = None
    def snapshot():
        nonlocal last_state
        # Deliberately chosen test text stays local; only counters/hashes are
        # suitable for the public evidence. No unrelated app is read.
        value = editor.toPlainText()
        foreground = int(foreground_window() or 0)
        target_pid = ctypes.c_ulong()
        foreground_process(foreground, ctypes.byref(target_pid))
        data = dict(pid=os.getpid(), elevated=elevated, timeUtc=datetime.now(UTC).isoformat(),
                    foreground=foreground == int(window.winId()), editorHasFocus=editor.hasFocus(),
                    operatorReady=operator_ready,
                    taskId=task_id, startSequence=start_sequence,
                    phase=phase, requestSequence=request_sequence,
                    requestAction=request_action, requestTaskId=request_task_id,
                    foregroundPid=target_pid.value, diagnosticTrace=str(root/'events.jsonl'),
                    changes=changes, characters=len(value), sha256=hashlib.sha256(value.encode()).hexdigest(),
                    testText=value, helperOnly=self_check)
        temp = root/'state.tmp'
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf8')
        temp.replace(root/'state.json')
        current = (data['foreground'], data['editorHasFocus'], target_pid.value, changes)
        if current != last_state:
            diagnostic('state_change', **{k: v for k, v in data.items() if k not in ('testText','timeUtc')})
            last_state = current
    def changed():
        nonlocal changes
        changes += 1
        snapshot()
    editor.textChanged.connect(changed)
    def start():
        nonlocal operator_ready, start_sequence, phase
        if phase != 'preview':
            return
        if restore_on_start is not None:
            editor.setPlainText(restore_on_start)
            editor.moveCursor(QTextCursor.MoveOperation.End)
        elif clear_on_start:
            editor.clear()
        start_sequence += 1
        start_button.setEnabled(False)
        editor.setFocus(Qt.FocusReason.OtherFocusReason)
        operator_ready = True
        phase = 'running'
        abort_button.setEnabled(True)
        diagnostic('operator_start', taskId=task_id, startSequence=start_sequence)
        snapshot()
    start_button.clicked.connect(start)
    def request(action):
        nonlocal request_sequence, request_action, request_task_id, operator_ready, phase
        if (action == 'abort' and phase != 'running') or (action != 'abort' and phase != 'review'):
            return
        request_sequence += 1
        request_action, request_task_id = action, task_id
        operator_ready = False
        phase = 'stopping' if action == 'abort' else 'preparing'
        for button in (start_button, repeat_button, accept_button, abort_button):
            button.setEnabled(False)
        instruction.setText('VERSUCH WIRD BEENDET\nDanach kannst du dieselbe Aufgabe in Ruhe neu starten.' if action == 'abort'
                            else 'DEINE AUSWAHL WIRD VORBEREITET\nDer nächste Versuch startet erst nach deinem Startklick.')
        diagnostic('operator_request', action=action, taskId=task_id, requestSequence=request_sequence)
        snapshot()
    repeat_button.clicked.connect(lambda: request('repeat'))
    accept_button.clicked.connect(lambda: request('accept'))
    abort_button.clicked.connect(lambda: request('abort'))
    timer = QTimer()
    timer.setInterval(250)
    timer.timeout.connect(snapshot)
    timer.start()
    control = root/'command.json'
    def command():
        nonlocal operator_ready, task_id, clear_on_start, restore_on_start, phase
        if control.exists():
            value = json.loads(control.read_text(encoding='utf8'))
            action = value.get('action')
            control.unlink()
            if value.get('taskId') is not None and action != 'prepare' and value['taskId'] != task_id:
                diagnostic('stale_instruction_rejected', taskId=value['taskId'])
                return
            if action == 'clear':
                editor.clear()
            elif action == 'close':
                app.quit()
            elif action == 'instruction':
                instruction.setText(value['text'])
            elif action == 'prepare':
                operator_ready = False
                phase = 'preview'
                task_id = value.get('taskId')
                clear_on_start = value.get('clearOnStart', True)
                restore_on_start = value.get('restoreOnStart')
                phrase.setText(value.get('phrase', 'Der vereinbarte Testsatz bleibt während des Versuchs hier sichtbar.'))
                instruction.setText(value['text'])
                start_button.setText(value.get('buttonText', 'Test starten'))
                start_button.setEnabled(True)
                for button in (repeat_button, accept_button, abort_button):
                    button.setEnabled(False)
                snapshot()
            elif action == 'review':
                operator_ready = False
                phase = 'review'
                instruction.setText(value['text'])
                start_button.setEnabled(False)
                abort_button.setEnabled(False)
                repeat_button.setEnabled(True)
                accept_button.setText(value.get('acceptText', 'Versuch übernehmen / weiter'))
                accept_button.setEnabled(True)
                snapshot()
            elif action == 'complete':
                operator_ready = False
                phase = 'done'
                instruction.setText(value['text'])
                for button in (start_button, repeat_button, accept_button, abort_button):
                    button.setEnabled(False)
                snapshot()
    controls = QTimer()
    controls.setInterval(100)
    controls.timeout.connect(command)
    controls.start()
    window.show()
    snapshot()
    (root.parent/'active.json').write_text(json.dumps(dict(pid=os.getpid(),
        state=str(root/'state.json'))), encoding='utf8')
    print(json.dumps(dict(pid=os.getpid(), state=str(root/'state.json'), elevated=elevated)), flush=True)
    QTimer.singleShot(2*60*60*1000, app.quit)
    if self_check:
        def check():
            def prepare(task, clear):
                control.write_text(json.dumps(dict(action='prepare', taskId=task,
                    text='VOR DEM START: Schritte', phrase='Vereinbarter grüner Testsatz', clearOnStart=clear)), encoding='utf8')
                command()
            prepare('one', True)
            assert not operator_ready and start_sequence == 0
            assert instruction.text().startswith('VOR DEM START')
            assert phrase.text() == 'Vereinbarter grüner Testsatz' and '#117333' in phrase.styleSheet()
            start_button.click()
            assert operator_ready and start_sequence == 1
            editor.setPlainText('Vereinbarter Prüftext äöü ß')
            prepare('two', False)
            assert not operator_ready and start_sequence == 1
            assert editor.toPlainText() == 'Vereinbarter Prüftext äöü ß'
            app.processEvents()
            assert not operator_ready and start_sequence == 1
            start_button.click()
            assert operator_ready and start_sequence == 2
            snapshot()
            data = json.loads((root/'state.json').read_text(encoding='utf8'))
            assert data['testText'] == editor.toPlainText() and data['taskId'] == 'two'
            control.write_text(json.dumps(dict(action='review', taskId='two', text='Versuch aus, Auswahl nötig')),encoding='utf8')
            command()
            assert phase == 'review' and repeat_button.isEnabled() and accept_button.isEnabled()
            assert phrase.text() == 'Vereinbarter grüner Testsatz'
            repeat_button.click()
            assert request_action == 'repeat' and request_task_id == 'two' and start_sequence == 2
            prepare('retry-three', False)
            app.processEvents()
            assert phase == 'preview' and not operator_ready and start_sequence == 2
            start_button.click()
            assert start_sequence == 3 and abort_button.isEnabled()
            abort_button.click()
            assert request_action == 'abort' and phase == 'stopping' and not operator_ready
            control.write_text(json.dumps(dict(action='instruction', taskId='old-task',text='STALE')),encoding='utf8')
            command()
            assert instruction.text() != 'STALE'
            control.write_text(json.dumps(dict(action='review', taskId='retry-three',text='Beendet')),encoding='utf8')
            command()
            accept_button.click()
            assert request_action == 'accept' and start_sequence == 3 and not operator_ready
            editor.setPlainText('Unbrauchbarer Text des wiederholten Versuchs')
            control.write_text(json.dumps(dict(action='prepare',taskId='restored',text='Vorschau',
                phrase='Grüner Satz bleibt',restoreOnStart='Akzeptierter vorheriger Satz ')),encoding='utf8')
            command()
            assert start_sequence == 3 and not operator_ready
            start_button.click()
            assert editor.toPlainText() == 'Akzeptierter vorheriger Satz ' and start_sequence == 4
            assert editor.textCursor().atEnd()
            print('HELPER_SELF_CHECK_PASS: persistent green phrase, preview, separate clicks, repeat without auto-start, abort, stale instruction rejected, explicit acceptance (no native paste or M-case proof)', flush=True)
            app.quit()
        QTimer.singleShot(100, check)
    app.exec()
    snapshot()
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    raise SystemExit(run(parser.parse_args().self_check))
