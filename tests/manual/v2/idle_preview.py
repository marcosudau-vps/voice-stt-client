"""Direct, operator-started LED comparison. No client, audio, hotkeys or server."""
import argparse
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import uuid

import yaml
from tests.manual.v2.suite_plan import ROOT, RUNTIME, PROFILE_RUNTIME
from tests.manual.v2.suite_session import save


class Preview:
    def __init__(self, factory, *, clock=time.monotonic):
        self.factory, self.clock = factory, clock
        self.controller = None
        self.available = False
        self.started = self.visible_since = None
        self.params = yaml.safe_load(Path(__file__).with_name('calibration.yaml').read_text(encoding='utf8'))['idle']

    def start(self):
        self.stop()
        self.available = False
        self.started, self.visible_since = self.clock(), None
        self.controller = self.factory(on_sink_changed=self.sink_changed)
        try:
            self.controller.set_state('ready_state', config=self.params)
        except Exception:
            self.stop()
            raise

    def sink_changed(self, available, detail):
        self.available = bool(available)

    def remaining(self):
        if not self.available:
            self.visible_since = None
            if self.clock()-self.started >= 15:
                raise TimeoutError('LED output unavailable')
            return None
        if self.visible_since is None:
            self.visible_since = self.clock()
        return max(0., 20-(self.clock()-self.visible_since))

    def stop(self):
        controller, self.controller = self.controller, None
        if controller is not None:
            controller.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile-runtime', action='store_true')
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if not args.profile_runtime and not args.self_check:
        parser.error('Use the explicitly authorized profile runtime or a hardware-free self-check')
    RUNTIME.mkdir(parents=True, exist_ok=True)
    folder = (RUNTIME if args.self_check else PROFILE_RUNTIME)/('idle-preview-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6])
    (folder/'tmp').mkdir(parents=True)
    os.environ['TEMP'] = os.environ['TMP'] = str(folder/'tmp')
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QPlainTextEdit
    from voice_stt_client.core.led_controller import InProcessLedController
    from voice_stt_client.ui.single_instance import SingleInstanceGuard
    app = QApplication([])
    guard = SingleInstanceGuard(r'Local\VoiceSTT_Qualification_AP_IV2_020')
    if not guard.acquire().acquired:
        raise RuntimeError('Another hardware qualification client is already open')
    def factory(**kwargs):
        return InProcessLedController(sink='respeaker', brightness=192/255,
            state_file=folder/'led-state.json', **kwargs)
    preview = Preview(factory)
    record = dict(scope='LED-only; no microphone, V2 client, hotkeys, activation or server',
        result='NOT_PROVEN', params=preview.params, globalBrightness=192,
        started=False, deviceAvailableObserved=False, selfCheck=args.self_check,
        sourceSha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (Path(__file__).resolve(), Path(__file__).with_name('calibration.yaml').resolve(),
                      ROOT/'voice_stt_client/core/led_controller.py')})
    def persist():
        save(folder/'result.json', record)
        if record.get('attemptId'):
            attempts = folder/'attempts'
            attempts.mkdir(exist_ok=True)
            save(attempts/(record['attemptId']+'.json'), record)
    class Window(QWidget):
        def closeEvent(self, event):
            preview.stop()
            persist()
            super().closeEvent(event)
    window = Window(); window.setWindowTitle('AP-IV2-020 – nur Idle-LEDs · eigener Start')
    layout = QVBoxLayout(window)
    instructions = QLabel('1. Erst lesen: Weißer Ring, sanfter Puls von 30 bis 100 % der Effekthelligkeit.\n'
        '2. Selbst START drücken. Nichts sprechen, keine Taste und kein USB nötig.\n'
        '3. Zwei Pulszyklen beobachten: bleibt Weiß erhalten, passt die Mindesthelligkeit?\n'
        '4. Ergebnis auswählen und übernehmen. Wiederholen ist möglich.')
    instructions.setStyleSheet('font-size:16px;padding:12px;'); layout.addWidget(instructions)
    status = QLabel('BEREIT ZUM SELBSTSTART · LEDs noch nicht übernommen')
    status.setStyleSheet('font-size:20px;color:#146b39;padding:16px;background:#e1f5e9;'); layout.addWidget(status)
    start = QPushButton('START / Wiederholen'); layout.addWidget(start)
    choice = QComboBox(); choice.addItems(['Ergebnis auswählen', 'Passt – weiß und angenehme Mindesthelligkeit', 'Noch violett', 'Andere Abweichung']); layout.addWidget(choice)
    notes = QPlainTextEdit(); notes.setPlaceholderText('Optionale Beobachtung'); layout.addWidget(notes)
    accept = QPushButton('Ergebnis übernehmen / Test beenden'); accept.setEnabled(False); layout.addWidget(accept)
    def begin():
        accept.setEnabled(False)
        if record.get('attemptId') and record['result'] == 'NOT_PROVEN':
            record['result'] = 'ABORTED_BY_REPEAT'
            persist()
        for key in ('humanObservation','humanNotes','tester','observationSeconds','reason','errorType'):
            record.pop(key, None)
        record.update(result='NOT_PROVEN', started=True, timeUtc=datetime.now(UTC).isoformat(),
            deviceAvailableObserved=False, attemptId=uuid.uuid4().hex)
        try:
            preview.start()
            status.setText('WARTE AUF LED-AUSGABE …')
            timer.start(100)
        except Exception as error:
            record.update(result='FAIL', errorType=type(error).__name__)
            status.setText('LED-START FEHLGESCHLAGEN · Wiederholung möglich')
        persist()
    def tick():
        try:
            remaining = preview.remaining()
        except TimeoutError:
            timer.stop(); preview.stop()
            record.update(result='FAIL', reason='LED output unavailable')
            status.setText('KEINE LED-AUSGABE · Wiederholung möglich')
            persist()
            return
        if remaining is None:
            return
        record['deviceAvailableObserved'] = True
        status.setText(f'JETZT NUR LEDs BEOBACHTEN · noch {remaining:.0f} Sekunden')
        if remaining == 0:
            timer.stop(); accept.setEnabled(True)
            status.setText('BEOBACHTUNG BEENDET · Ergebnis auswählen und übernehmen')
            record['observationSeconds'] = 20
            persist()
    def finish():
        if choice.currentIndex() == 0:
            status.setText('Bitte zuerst ein Ergebnis auswählen.')
            return
        timer.stop(); preview.stop()
        record.update(result='NOT_PROVEN_PENDING_AGENT_EVALUATION',
            humanObservation=choice.currentText(), humanNotes=notes.toPlainText(),
            tester='Marco: visual perception; Codex: direct LED configuration/instrumentation')
        persist()
        status.setText('FERTIG · LEDs freigegeben · Im Chat „fertig“ melden')
        accept.setEnabled(False)
    timer = QTimer(); timer.timeout.connect(tick)
    def check_owner_command():
        command = folder/'ui-command.json'
        if command.exists() and json.loads(command.read_text(encoding='utf8')).get('action') == 'close':
            window.close()
    lifecycle = QTimer(); lifecycle.timeout.connect(check_owner_command); lifecycle.start(250)
    start.clicked.connect(begin); accept.clicked.connect(finish)
    window.resize(900,550); window.show()
    save(folder/'result.json', record)
    save(RUNTIME/'active-idle-preview.json', dict(pid=os.getpid(), folder=str(folder),
        profileRuntime=args.profile_runtime, clientStarted=False))
    if args.self_check:
        class Dummy:
            def __init__(self, **kwargs): self.changed=kwargs['on_sink_changed']
            def set_state(self, target, config): self.changed(True, 'controlled test')
            def close(self): pass
        now = [0.]; preview.factory = Dummy; preview.clock = lambda: now[0]
        assert not record['started'] and preview.controller is None
        begin(); tick(); now[0] = 21.; tick()
        assert accept.isEnabled() and record['observationSeconds']==20
        choice.setCurrentIndex(1); finish()
        assert preview.controller is None and not accept.isEnabled()
        first = record['attemptId']
        begin()
        assert record['attemptId'] != first and 'humanObservation' not in record
        assert json.loads((folder/'attempts'/(first+'.json')).read_text(encoding='utf8'))['humanObservation']
        window.close(); guard.release(); print('IDLE_PREVIEW_SELF_CHECK_PASS'); return
    try:
        app.exec()
    finally:
        preview.stop()
        guard.release()


if __name__ == '__main__':
    main()
