"""Clickable starter for the existing isolated AP-IV2-020 exploration session."""
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import uuid
import yaml

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())
LOCAL = Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020'
CONTAINER = 'voicestt-qualification-iv2-020'
IMAGE = 'sha256:5aaa17e9963fea4c3109027a2ce141b2037b5eadfe7cbd91ff39a9f15626ff20'
MUTEX = r'Local\VoiceSTT_Qualification_AP_IV2_020'


def running():
    """Inspect the qualification mutex without acquiring or changing it."""
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenMutexW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.OpenMutexW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.OpenMutexW(0x00100000, False, MUTEX)
    if handle:
        kernel.CloseHandle(handle)
        return True
    error = ctypes.get_last_error()
    if error != 2:
        raise OSError(error, 'Testinstanzstatus nicht lesbar')
    return False


def validate_container(info):
    if (info.get('Image') != IMAGE
            or info.get('Config', {}).get('Labels', {}).get('voice-stt.qualification') != 'AP-IV2-020'
            or info.get('HostConfig', {}).get('PortBindings') != {
                '8010/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '18020'}]}):
        raise ValueError('Testserver-Identität oder lokale Portbindung stimmt nicht. Agent prüfen lassen.')


def ensure_server(status):
    def docker(*args):
        return subprocess.run(['docker', *args], capture_output=True, text=True,
                              timeout=45, check=True, creationflags=subprocess.CREATE_NO_WINDOW).stdout
    info = json.loads(docker('inspect', CONTAINER))[0]
    validate_container(info)
    if not info['State']['Running']:
        status('Lokaler Testserver wird gestartet …')
        docker('start', CONTAINER)
    status('Warte auf lokalen Testserver …')
    deadline = time.monotonic()+90
    while time.monotonic() < deadline:
        info = json.loads(docker('inspect', CONTAINER))[0]
        validate_container(info)
        if info['State'].get('Health', {}).get('Status') == 'healthy':
            return
        if not info['State']['Running']:
            raise RuntimeError('Lokaler Testserver ist beendet. Agent prüfen lassen.')
        time.sleep(1)
    raise TimeoutError('Testserver wurde nicht rechtzeitig bereit. Erneut versuchen oder Agent fragen.')


def start_client(status):
    if running():
        return
    profile = yaml.safe_load((LOCAL/'client-both.yaml').read_text(encoding='utf-8'))
    if profile.get('server', {}).get('url') != 'ws://127.0.0.1:18020/ws/v2':
        raise ValueError('Isoliertes lokales Testprofil fehlt oder zeigt auf einen anderen Server.')
    ensure_server(status)
    if running():
        return
    status('Client startet – Mikrofon und Modelle werden vorbereitet …')
    env = dict(os.environ, QT_QPA_PLATFORM='windows', PYTHONUTF8='1',
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    log = LOCAL/'launcher-logs'/f'{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}.log'
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open('wb') as output:
        child = subprocess.Popen([str(ROOT/'venv/Scripts/python.exe'), '-u',
            str(Path(__file__).with_name('explore_with_logging.py')), '--mode', 'both'],
            cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW)
    deadline = time.monotonic()+30
    while time.monotonic() < deadline:
        if child.poll() is not None:
            raise RuntimeError(f'Clientstart fehlgeschlagen. Lokale Diagnose: {log}')
        if running():
            return
        time.sleep(.2)
    raise TimeoutError('Client startet noch. Status beobachten; keine weitere Instanz starten.')


def latest_status():
    active = json.loads((LOCAL/'active-session.json').read_text(encoding='utf-8'))
    folder = Path(active['folder'])
    if not folder.absolute().is_relative_to(LOCAL.absolute()):
        raise ValueError('Fremdes Sitzungsverzeichnis')
    # Read only a bounded tail; never expose transcript content in this window.
    with (folder/'trace.jsonl').open('rb') as trace:
        trace.seek(max(0, trace.seek(0, 2)-65536))
        lines = trace.read().decode('utf-8', errors='replace').splitlines()
    for line in reversed(lines):
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get('kind') != 'metrics':
            continue
        age = (datetime.now(timezone.utc)-datetime.fromisoformat(row['timeUtc'])).total_seconds()
        if age > 5:
            return 'Client läuft – warte auf aktuelle Diagnose …'
        if row.get('ready') and row.get('media', {}).get('audio_available'):
            return 'CLIENT BEREIT – du kannst jetzt sprechen.'
        return 'Client läuft – Verbindung oder Mikrofon wird vorbereitet …'
    return 'Client läuft – warte auf Bereitschaft …'


def main():
    from PySide6.QtCore import QObject, QTimer, Signal
    from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
    class Events(QObject):
        status = Signal(str)
        finished = Signal(str)
    app = QApplication.instance() or QApplication([])
    window = QWidget()
    window.setWindowTitle('V2-Testinstanz – Start und Status')
    window.resize(600, 300)
    layout = QVBoxLayout(window)
    title = QLabel('Isolierte V2-Testinstanz')
    title.setStyleSheet('font-size:22px;font-weight:bold;')
    layout.addWidget(title)
    description = QLabel('Lokales Testprofil · ReSpeaker · Wakewords und Hotkeys\n'
                         'Der Startknopf ändert keine Kalibrierwerte. Beenden über das Client-Tray.')
    description.setWordWrap(True)
    layout.addWidget(description)
    status = QLabel('Status wird geprüft …')
    status.setWordWrap(True)
    status.setStyleSheet('font-size:18px;font-weight:bold;padding:14px;background:#16324a;color:white;')
    layout.addWidget(status)
    start = QPushButton('Testinstanz starten')
    start.setMinimumHeight(48)
    layout.addWidget(start)
    settings = QPushButton('Einstellungen der laufenden Testinstanz öffnen')
    layout.addWidget(settings)
    events = Events()
    busy = [False]
    error = ['']
    events.status.connect(status.setText)
    def finished(message):
        busy[0] = False
        error[0] = message
        refresh()
    events.finished.connect(finished)
    def refresh():
        if busy[0]:
            return
        try:
            active = running()
            start.setEnabled(not active)
            settings.setEnabled(active)
            start.setText('Testinstanz läuft bereits' if active else 'Testinstanz starten')
            status.setText(error[0] or (latest_status() if active else 'Testinstanz ist beendet – zum Starten klicken.'))
        except (OSError, ValueError, KeyError) as exc:
            status.setText(f'Status nicht verfügbar: {exc}')
    def launch():
        busy[0] = True
        error[0] = ''
        start.setEnabled(False)
        settings.setEnabled(False)
        def worker():
            try:
                start_client(events.status.emit)
            except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
                events.finished.emit(str(exc))
            else:
                events.finished.emit('')
        threading.Thread(target=worker, daemon=True).start()
    def open_settings():
        if running():
            inbox = LOCAL/'commands'
            inbox.mkdir(exist_ok=True)
            target = inbox/(uuid.uuid4().hex+'.json')
            temp = target.with_suffix('.tmp')
            temp.write_text(json.dumps({'action': 'settings'}), encoding='utf-8')
            temp.replace(target)
    start.clicked.connect(launch)
    settings.clicked.connect(open_settings)
    timer = QTimer(window)
    timer.timeout.connect(refresh)
    timer.start(1000)
    refresh()
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
