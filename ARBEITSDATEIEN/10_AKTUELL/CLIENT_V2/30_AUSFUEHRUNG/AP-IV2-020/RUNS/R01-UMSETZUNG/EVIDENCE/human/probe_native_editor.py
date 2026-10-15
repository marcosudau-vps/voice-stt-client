"""One actual production V2 injection job into the explicitly armed own editor.

No microphone, server or global hotkey. The native queue owns its real worker
and Clipboard/SendInput backend. A test-only PID/field-focus guard prevents
injection into any other app. Previous Unicode clipboard text is restored by
the unchanged product contract. No automatic retry of an uncertain paste.
"""
import argparse
import ctypes
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time
import uuid
from editor_state import owned_editor_path, read_editor_state

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'scripts/qualify_v2_session.py').is_file())
sys.path.insert(0, str(ROOT))
TEXT = 'NATIVE TEST: Einfügen äöü funktioniert.'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--append-space', action='store_true')
    parser.add_argument('--guided-continuation', action='store_true')
    args = parser.parse_args()
    local = Path(os.environ['LOCALAPPDATA']) / 'VoiceSTT-Qualification/AP-IV2-020'
    os.environ['VOICESTT_CLIENT_HOME'] = str(local / 'client')
    args.state = owned_editor_path(args.state, local)
    from voice_stt_client.core.config import AppConfig
    from voice_stt_client.core.history import TranscriptHistoryManager
    from voice_stt_client.core.text_injector import (
        TextInjectionQueue, CtypesWindowsInjectionBackend, clipboard_session)
    from scripts.qualify_v2_real import identity
    state = lambda: read_editor_state(args.state)
    deadline = time.monotonic() + 600
    print('Waiting for operator Start button in own diagnostic editor', flush=True)
    while True:
        before = state()
        fresh = abs((datetime.now(UTC) - datetime.fromisoformat(before['timeUtc'])).total_seconds()) < 2
        if fresh and all(before.get(k) for k in ('foreground', 'editorHasFocus', 'operatorReady')):
            break
        if time.monotonic() > deadline:
            raise TimeoutError('Native probe not armed; nothing injected')
        time.sleep(.1)
    expected_pid = before['pid']
    native_calls = []

    class GuardedBackend(CtypesWindowsInjectionBackend):
        def get_foreground_window(self):
            hwnd = super().get_foreground_window()
            _thread, pid = self.get_window_thread_process_id(hwnd)
            return hwnd if pid == expected_pid else 0

        def send_input_keyboard(self, events):
            hwnd = super().get_foreground_window()
            _thread, pid = self.get_window_thread_process_id(hwnd)
            current = state()
            keyboard = ctypes.windll.user32.GetAsyncKeyState
            keyboard.argtypes = [ctypes.c_int]
            keyboard.restype = ctypes.c_short
            modifiers = {name: bool(keyboard(key) & 0x8000) for name, key in
                         (('ctrl', 0x11), ('shift', 0x10), ('alt', 0x12))}
            row = dict(timeUtc=datetime.now(UTC).isoformat(), nativeForegroundPid=pid,
                       editorHasFocus=current['editorHasFocus'], modifiers=modifiers)
            native_calls.append(row)
            if pid != expected_pid or not current['editorHasFocus']:
                row['suppressedByTestGuard'] = True
                return 0
            with clipboard_session(self, config, self.get_owner_window()):
                value = self.get_clipboard_data_unicode()
                row['clipboardCharacters'] = len(value) if value is not None else None
                row['clipboardSha256'] = hashlib.sha256(value.encode()).hexdigest() if value is not None else None
            sent = super().send_input_keyboard(events)
            row['sentEvents'] = sent
            return sent

    config = AppConfig()
    config.history.persistent.enabled = False
    config.text_injection.append_space = args.append_space
    config.clipboard.restore_previous = True
    history = TranscriptHistoryManager(config.history)
    sid, aid, segment, event = [str(uuid.uuid4()) for _ in range(4)]
    entry = history.add_entry_with_status(sid, segment, TEXT, protocol_version=2,
                              activation_id=aid, segment_sequence=1, event_id=event, event_seq=1).entry
    if entry is None:
        raise RuntimeError('Probe history reservation unavailable')
    queue = TextInjectionQueue(config, history, GuardedBackend())
    done = threading.Event()
    attempts = []

    def completed(attempt):
        attempts.append(dict(status=attempt.status, error=attempt.error, source=attempt.source))
        done.set()

    queue.on_attempt_result = completed
    try:
        queue.start()
        if not queue.enqueue_reserved(entry):
            raise RuntimeError('Probe admission failed')
        if not done.wait(10):
            raise TimeoutError('Native paste outcome unknown; no retry')
        time.sleep(.5)
        after = state()
        expected = TEXT + (' ' if args.append_space else '')
        passed = after['testText'] == expected and len(attempts) == 1 and attempts[0]['status'] == 'command_sent'
        result = dict(result='PASS' if passed else 'FAIL', identity=identity(),
            appendSpace=args.append_space, authoritativeTextPreserved=entry.text == TEXT,
            expectedSha256=hashlib.sha256(expected.encode()).hexdigest(),
            before={k: v for k, v in before.items() if k != 'testText'},
            after={k: v for k, v in after.items() if k != 'testText'},
            attempts=attempts, nativeCalls=native_calls,
            boundaries='Actual queue reservation/worker/native Clipboard/SendInput; own armed editor only; no speech/server.')
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
        message = ('Einfügen erfolgreich.\nBitte im Chat „Testtext sichtbar“ melden.' if passed else
                   'Prüfung beendet; Text nicht korrekt angekommen.\nBitte im Chat „Nichts sichtbar“ melden.')
        if passed and args.guided_continuation:
            message = 'EINFÜGEPROBE ERFOLGREICH\n• Der Sprachtest erhält einen eigenen Startknopf.'
        (args.state.parent/'command.json').write_text(json.dumps(dict(action='instruction', text=message)), encoding='utf8')
        print(json.dumps(dict(result=result['result'], nativeCalls=len(native_calls))), flush=True)
    finally:
        queue.stop()


if __name__ == '__main__':
    main()
