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

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QLabel, QPlainTextEdit, QVBoxLayout, QWidget


def run(self_check=False):
    root = Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020/editors'/str(os.getpid())
    root.mkdir(parents=True, exist_ok=False)
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle('AP-IV2-020 – leerer Testeditor')
    layout = QVBoxLayout(window)
    elevated = bool(ctypes.windll.shell32.IsUserAnAdmin())
    layout.addWidget(QLabel('Testziel '+('mit erhöhten Rechten' if elevated else 'mit normalen Rechten')+
        '. Bitte einmal in das Textfeld klicken. Nur vereinbarte Testsätze verwenden.'))
    editor = QPlainTextEdit()
    editor.setPlaceholderText('Hier erscheinen die finalen Transkriptionen.')
    layout.addWidget(editor)
    window.resize(1000, 600)
    foreground_window = ctypes.windll.user32.GetForegroundWindow
    foreground_window.restype = ctypes.c_void_p
    changes = 0
    def snapshot():
        # Deliberately chosen test text stays local; only counters/hashes are
        # suitable for the public evidence. No unrelated app is read.
        value = editor.toPlainText()
        data = dict(pid=os.getpid(), elevated=elevated, timeUtc=datetime.now(UTC).isoformat(),
                    foreground=int(foreground_window() or 0) == int(window.winId()),
                    changes=changes, characters=len(value), sha256=hashlib.sha256(value.encode()).hexdigest(),
                    testText=value, helperOnly=self_check)
        temp = root/'state.tmp'
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf8')
        temp.replace(root/'state.json')
    def changed():
        nonlocal changes
        changes += 1
        snapshot()
    editor.textChanged.connect(changed)
    timer = QTimer()
    timer.setInterval(250)
    timer.timeout.connect(snapshot)
    timer.start()
    control = root/'command.json'
    def command():
        if control.exists():
            action = json.loads(control.read_text(encoding='utf8')).get('action')
            control.unlink()
            if action == 'clear':
                editor.clear()
            elif action == 'close':
                app.quit()
    controls = QTimer()
    controls.setInterval(100)
    controls.timeout.connect(command)
    controls.start()
    window.show()
    snapshot()
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
