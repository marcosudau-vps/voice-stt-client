"""Operator-started, finite deliberate wake samples; all audio stays outside Git.

Run only after the qualification desktop has stopped. Each button starts a
three-second countdown followed by nine seconds of recording. No background
recording, clipboard access, server mutation or changes to client profiles.
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
import wave

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'scripts/qualify_v2_session.py').is_file())
sys.path.insert(0, str(ROOT))
CASES = (
    ('jarvis_pause', 'Hey Jarvis', 'Der blaue Becher steht auf dem Tisch.', True),
    ('alexa_pause', 'Alexa', 'Die grüne Lampe steht neben dem Fenster.', True),
    ('jarvis_direct', 'Hey Jarvis', 'Der rote Ball liegt auf dem Boden.', False),
    ('alexa_direct', 'Alexa', 'Die gelbe Tasche steht vor der Tür.', False),
    ('negative_speech', '', 'Heute ist ein guter Tag für einen Spaziergang.', False),
    ('unselected_phrase', 'Computer', 'Das Buch liegt auf dem Schreibtisch.', False),
)


def save_wave(path, data):
    with wave.open(str(path), 'wb') as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(16000)
        handle.writeframes(data)


def require_desktop_stopped(local):
    active = local / 'active-session.json'
    if not active.exists():
        return
    pid = json.loads(active.read_text(encoding='utf-8-sig'))['pid']
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.OpenProcess(0x1000, False, pid)
    if handle:
        try:
            code = wintypes.DWORD()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value == 259:
                raise RuntimeError('Stop qualification desktop before opening the recorder')
        finally:
            kernel.CloseHandle(handle)
    elif ctypes.get_last_error() != 87:  # ERROR_INVALID_PARAMETER: process gone
        raise ctypes.WinError(ctypes.get_last_error())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'synthetic-writer-only.wav'
            save_wave(path, b'\x00\x00' * 16000)
            with wave.open(str(path), 'rb') as handle:
                assert (handle.getnchannels(), handle.getsampwidth(), handle.getframerate(),
                        handle.getnframes()) == (1, 2, 16000, 16000)
        assert len({c[0] for c in CASES}) == len(CASES) == 6
        print('PASS: WAV writer/finite sample plan only; no microphone/model qualification')
        return
    import sounddevice as sd
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
    from voice_stt_client.core.audio_capture import AudioCapture
    local = Path(os.environ['LOCALAPPDATA']) / 'VoiceSTT-Qualification/AP-IV2-020'
    require_desktop_stopped(local)
    device = next(d for d in AudioCapture.list_devices() if 'respeaker' in d['name'].lower())
    folder = local / 'samples' / datetime.now().strftime('human-%Y%m%d-%H%M%S')
    folder.mkdir(parents=True)
    (local / 'active-recorder.json').write_text(json.dumps(dict(
        pid=os.getpid(), folder=str(folder), device=device,
        helperSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())), encoding='utf8')
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle('AP-IV2-020 – bewusste Wake-Testaufnahmen')
    layout = QVBoxLayout(window)
    status = QLabel('')
    instructions = QLabel('')
    instructions.setWordWrap(True)
    button = QPushButton('')
    layout.addWidget(status)
    layout.addWidget(instructions)
    layout.addWidget(button)
    index = 0
    data = None
    started = None
    start_monotonic = None

    def present():
        if index == len(CASES):
            status.setText('Alle sechs Aufnahmen gespeichert. Bitte im Chat „Aufnahmen fertig“ melden.')
            instructions.setText('Keine weitere Aufnahme läuft. Rohaufnahmen bleiben nur lokal.')
            button.setEnabled(False)
            return
        name, wake, phrase, pause = CASES[index]
        status.setText(f'Bewusste Testaufnahme {index + 1} von {len(CASES)}. Noch keine Aufnahme.')
        instructions.setText((f'„{wake}“ – eine Sekunde Pause – „{phrase}“' if pause else
                              f'Ohne bewusste Pause: „{wake + " " if wake else ""}{phrase}“') +
                             '\nNach Klick: drei Sekunden Countdown, dann neun Sekunden Aufnahme. '
                             'Bei „JETZT SPRECHEN“ genau einmal sprechen, anschließend schweigen.')
        button.setText('Diese Testaufnahme starten')
        button.setEnabled(True)

    def finish():
        nonlocal index, data
        capture_status = sd.wait()
        name, wake, phrase, pause = CASES[index]
        path = folder / (name + '.wav')
        raw = data.astype('<i2', copy=False).tobytes()
        save_wave(path, raw)
        meta = dict(case=name, startedAtUtc=started, startMonotonic=start_monotonic,
                    finishedAtUtc=datetime.now(UTC).isoformat(), frames=len(data),
                    sampleRate=16000, channels=1, durationSeconds=9, device=device,
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    operatorInitiated=True, origin='Deliberate human speech via real ReSpeaker',
                    peakAbsolute=int(abs(data.astype('int32')).max()),
                    captureStatus=str(capture_status),
                    inputOverflow=bool(capture_status and capture_status.input_overflow),
                    expectedWakePhrase=wake, expectedUserPhrase=phrase, requestedPause=pause,
                    boundaryAnnotation='PENDING; requested timing is not measured phonetic timing')
        path.with_suffix('.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
        data = None
        index += 1
        present()

    def record():
        nonlocal data, started, start_monotonic
        status.setText('JETZT SPRECHEN – Aufnahme läuft neun Sekunden')
        started = datetime.now(UTC).isoformat()
        start_monotonic = time.monotonic()
        try:
            data = sd.rec(9 * 16000, samplerate=16000, channels=1, dtype='int16', device=device['index'])
        except sd.PortAudioError as error:
            status.setText(f'Mikrofonstart fehlgeschlagen ({type(error).__name__}); bitte im Chat melden.')
            (folder / 'capture-error.json').write_text(json.dumps(dict(
                case=CASES[index][0], errorType=type(error).__name__,
                timeUtc=datetime.now(UTC).isoformat())), encoding='utf8')
            return
        QTimer.singleShot(9100, finish)

    def countdown(remaining=3):
        button.setEnabled(False)
        if remaining:
            status.setText(f'Aufnahme beginnt in {remaining} …')
            QTimer.singleShot(1000, lambda: countdown(remaining - 1))
        else:
            record()

    button.clicked.connect(lambda: countdown())
    present()
    window.resize(720, 230)
    window.show()
    try:
        app.exec()
    finally:
        sd.stop()


if __name__ == '__main__':
    main()
