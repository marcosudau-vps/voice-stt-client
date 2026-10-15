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
    instruction = QLabel('Einfügen ohne Sprache prüfen.\nBitte „Einfügeprüfung starten“ klicken und danach warten.')
    instruction.setWordWrap(True)
    instruction.setStyleSheet('font-size: 18px; padding: 8px;')
    layout.addWidget(instruction)
    start_button = QPushButton('Einfügeprüfung starten')
    layout.addWidget(start_button)
    editor = TestEditor()
    editor.setPlaceholderText('Hier erscheinen die finalen Transkriptionen.')
    layout.addWidget(editor)
    window.resize(1000, 600)
    foreground_window = ctypes.windll.user32.GetForegroundWindow
    foreground_window.restype = ctypes.c_void_p
    foreground_process = ctypes.windll.user32.GetWindowThreadProcessId
    foreground_process.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    foreground_process.restype = ctypes.c_ulong
    changes = 0
    last_state = None
    operator_ready = False
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
        nonlocal operator_ready
        editor.clear()
        start_button.setEnabled(False)
        editor.setFocus(Qt.FocusReason.OtherFocusReason)
        operator_ready = True
        diagnostic('operator_start')
        snapshot()
    start_button.clicked.connect(start)
    timer = QTimer()
    timer.setInterval(250)
    timer.timeout.connect(snapshot)
    timer.start()
    control = root/'command.json'
    def command():
        nonlocal operator_ready
        if control.exists():
            value = json.loads(control.read_text(encoding='utf8'))
            action = value.get('action')
            control.unlink()
            if action == 'clear':
                editor.clear()
            elif action == 'close':
                app.quit()
            elif action == 'instruction':
                instruction.setText(value['text'])
            elif action == 'prepare':
                operator_ready = False
                instruction.setText(value['text'])
                start_button.setText(value.get('buttonText', 'Test starten'))
                start_button.setEnabled(True)
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
            editor.setPlainText('Vereinbarter Prüftext äöü ß')
            snapshot()
            data = json.loads((root/'state.json').read_text(encoding='utf8'))
            assert data['testText'] == editor.toPlainText() and data['changes'] == 1
            print('HELPER_SELF_CHECK_PASS (no native paste or M-case proof)', flush=True)
            app.quit()
        QTimer.singleShot(100, check)
    app.exec()
    snapshot()
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    raise SystemExit(run(parser.parse_args().self_check))
