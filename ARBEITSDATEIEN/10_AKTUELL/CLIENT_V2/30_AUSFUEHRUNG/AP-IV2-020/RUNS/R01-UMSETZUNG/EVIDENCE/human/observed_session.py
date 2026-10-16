"""Read-only event observer around the existing isolated desktop test runner.

Run with the project venv and --mode manual|wake|both. No production files are
modified. The observer chains existing callbacks; transport/reducers/audio and
Windows side effects remain production-owned. Raw text/tokens are never logged.
"""
import argparse
import asyncio
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from editor_state import owned_editor_path, read_editor_state, operator_started

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'scripts/qualify_v2_session.py').is_file())
sys.path.insert(0, str(ROOT))
FIELDS = ('sessionId', 'activationId', 'segmentId', 'segmentSequence',
          'eventId', 'eventSeq', 'stateVersion', 'occurredAtUnixMs',
          'wakeWordId', 'score', 'primarySource', 'phase', 'reason',
          'deadlineAtUnixMs', 'remainingMs', 'settingsRevision')


def safe_event(binding, event):
    result = dict(type=str(event.type), generation=binding.generation)
    payload = event.payload
    for key in FIELDS:
        if key in payload:
            result[key] = payload[key]
    text = payload.get('text')
    if isinstance(text, str):
        result.update(textLength=len(text),
                      textSha256=hashlib.sha256(text.encode('utf8')).hexdigest())
    effective = payload.get('effectiveSettings')
    if effective is not None:
        result['effectiveFollowupMs'] = effective.get('activation.followupTimeoutMs')
        result['effectivePreRollMs'] = effective.get('wakeWord.preRollMs')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('manual', 'wake', 'both'), default='wake')
    parser.add_argument('--self-check', action='store_true')
    parser.add_argument('--wait-for-editor-state', type=Path)
    parser.add_argument('--stop-after', type=int, default=0)
    parser.add_argument('--editor-guided', action='store_true')
    parser.add_argument('--arm-timeout', type=int, default=120)
    parser.add_argument('--editor-case', choices=('jarvis', 'alexa'))
    parser.add_argument('--expected-task-id')
    args = parser.parse_args()
    if not 10 <= args.arm_timeout <= 1800:
        parser.error('--arm-timeout must be 10..1800 seconds')
    if args.editor_guided and (not args.editor_case or args.stop_after != 1):
        parser.error('Guided tasks require one --editor-case and --stop-after 1; each task needs its own start')
    if args.self_check:
        from types import SimpleNamespace
        record = safe_event(SimpleNamespace(generation=2), SimpleNamespace(
            type='transcription.completed', payload=dict(activationId='a',
            text='deliberate test', logAccess='secret', accessToken='secret',
            effectiveSettings={'activation.followupTimeoutMs': 5000,
                               'wakeWord.preRollMs': 320, 'private': 'secret'})))
        assert record['activationId'] == 'a' and record['effectiveFollowupMs'] == 5000
        assert record['effectivePreRollMs'] == 320
        assert record['textLength'] == 15 and 'text' not in record
        assert 'secret' not in json.dumps(record)
        print('PASS: explicit identity/settings allowlist; text hashed; tokens excluded')
        return
    local = Path(os.environ['LOCALAPPDATA']) / 'VoiceSTT-Qualification/AP-IV2-020'
    focus_gate = None
    if not 0 <= args.stop_after <= 100:
        parser.error('--stop-after must be 0..100')
    if args.editor_guided and not args.wait_for_editor_state:
        parser.error('--editor-guided requires the owned editor state')
    if args.wait_for_editor_state:
        state_file = owned_editor_path(args.wait_for_editor_state, local)
        deadline = time.monotonic() + args.arm_timeout
        print('Waiting for operator to focus the owned test editor', flush=True)
        while True:
            state = read_editor_state(state_file)
            fresh = abs((datetime.now(UTC) - datetime.fromisoformat(state['timeUtc'])).total_seconds()) < 2
            started = (operator_started(state, args.expected_task_id) if args.editor_guided
                       else fresh and state['foreground'] and state.get('editorHasFocus', False))
            if started:
                focus_gate = {k: v for k, v in state.items() if k != 'testText'}
                break
            if time.monotonic() >= deadline:
                raise TimeoutError('Owned editor was not focused; desktop not started')
            time.sleep(.1)
    os.environ['VOICESTT_CLIENT_HOME'] = str(local / 'client')
    from voice_stt_client.core import v2_runtime
    from scripts.qualify_v2_session import run
    folder = local / 'observations' / datetime.now().strftime('%Y%m%d-%H%M%S')
    folder.mkdir(parents=True)
    trace = folder / 'events.jsonl'
    (local / 'active-observation.json').write_text(json.dumps(dict(
        folder=str(folder), pid=os.getpid(), mode=args.mode,
        initialEditorFocus=focus_gate, stopAfterTerminalActivations=args.stop_after,
        taskId=args.expected_task_id, editorCase=args.editor_case,
        helperSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())), encoding='utf8')
    original = v2_runtime.V2Runtime
    def editor_instruction(text):
        (state_file.parent/'command.json').write_text(json.dumps(dict(
            action='instruction', text=text)), encoding='utf8')

    class ObservedRuntime(original):
        def __init__(self, *values, **options):
            if args.editor_guided:
                from voice_stt_client.core.text_injector import CtypesWindowsInjectionBackend

                class OwnEditorBackend(CtypesWindowsInjectionBackend):
                    # Test target guard only. A focus loss is an actual failed/skipped
                    # test attempt, never a synthetic successful native paste.
                    def target_focused(backend, hwnd):
                        _, pid = backend.get_window_thread_process_id(hwnd)
                        current = read_editor_state(state_file)
                        fresh = abs((datetime.now(UTC) - datetime.fromisoformat(
                            current['timeUtc'])).total_seconds()) < 2
                        return bool(fresh and pid == focus_gate['pid']
                                    and current.get('editorHasFocus'))

                    def get_foreground_window(backend):
                        hwnd = super().get_foreground_window()
                        return hwnd if backend.target_focused(hwnd) else 0

                    def send_input_keyboard(backend, events):
                        hwnd = super().get_foreground_window()
                        if not backend.target_focused(hwnd):
                            return 0
                        return super().send_input_keyboard(events)

                options['backend'] = OwnEditorBackend()
            super().__init__(*values, **options)
            previous = self.session.on_message

            def receive(binding, event):
                previous(binding, event)
                record = safe_event(binding, event)
                record.update(timeUtc=datetime.now(UTC).isoformat(), monotonic=time.monotonic())
                with trace.open('a', encoding='utf8') as handle:
                    handle.write(json.dumps(record, ensure_ascii=True) + '\n')
                if args.editor_guided and str(event.type) in (
                        'activation.completed', 'activation.cancelled', 'activation.failed'):
                    count = sum(a.status in ('completed', 'cancelled', 'failed')
                                for a in self.mirror.mirror.view.activations.values())
                    if count >= 1:
                        editor_instruction('BITTE KURZ WARTEN\n• Der Testclient wird beendet.\n'
                                           '• Danach erscheint hier „FERTIG“.')

            self.session.on_message = receive
            if args.editor_guided:
                previous_status = self.session.on_status
                shown = False

                def status(value):
                    nonlocal shown
                    previous_status(value)
                    if str(value.state) == 'ready' and not shown:
                        shown = True
                        phrase = ('Hey Jarvis der rote Ball liegt auf dem Boden.'
                                  if args.editor_case == 'jarvis' else
                                  'Alexa die gelbe Tasche steht vor der Tür.')
                        editor_instruction('CLIENT BEREIT – JETZT SPRECHEN\n'
                            '• Ohne Pause sprechen:\n'+phrase+'\n'
                            '• Danach Strg+Umschalt+F9 drücken.\n'
                            '• Auf die nächste Aufgabe hier im Fenster warten.')

                self.session.on_status = status
            if args.stop_after:
                original_run = self.run

                async def stop_when_finished():
                    deadline = time.monotonic() + 180
                    while not self.is_closing:
                        terminal = sum(a.status in ('completed', 'cancelled', 'failed')
                                       for a in self.mirror.mirror.view.activations.values())
                        if terminal >= args.stop_after or time.monotonic() >= deadline:
                            await asyncio.sleep(3)  # allow actual queued paste to complete
                            inbox = local / 'commands'
                            inbox.mkdir(exist_ok=True)
                            command = dict(action='stop', case='bounded-human-trial',
                                           observedTerminalCount=terminal)
                            (inbox / f'bounded-stop-{os.getpid()}-{time.monotonic_ns()}.json').write_text(
                                json.dumps(command), encoding='utf8')
                            return
                        await asyncio.sleep(.05)

                async def bounded_run():
                    watcher = asyncio.create_task(stop_when_finished(), name='qualification-bounded-stop')
                    try:
                        return await original_run()
                    finally:
                        watcher.cancel()
                        await asyncio.gather(watcher, return_exceptions=True)

                self.run = bounded_run

    v2_runtime.V2Runtime = ObservedRuntime
    try:
        run(args.mode)
    finally:
        v2_runtime.V2Runtime = original
        if args.editor_guided:
            editor_instruction('AUFGABE BEENDET – TESTCLIENT AUS\n'
                               '• Die nächste Aufgabe benötigt wieder deinen Start.')


if __name__ == '__main__':
    main()
