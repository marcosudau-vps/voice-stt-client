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
import threading
import time
from tests.manual.v2.editor_state import owned_editor_path, read_editor_state, operator_started

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
    parser.add_argument('--editor-case', choices=('jarvis', 'alexa', 'manual'))
    parser.add_argument('--expected-task-id')
    parser.add_argument('--prepare-seconds',type=int,default=8)
    args = parser.parse_args()
    if not 10 <= args.arm_timeout <= 1800:
        parser.error('--arm-timeout must be 10..1800 seconds')
    if not 0 <= args.prepare_seconds <= 30:
        parser.error('--prepare-seconds must be 0..30')
    if args.editor_guided and (not args.editor_case or args.stop_after != 1):
        parser.error('Guided tasks require one --editor-case and --stop-after 1; each task needs its own start')
    if args.editor_guided and ((args.editor_case == 'manual') != (args.mode == 'manual')):
        parser.error('The manual task requires manual mode; wake tasks require wake/both mode')
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
            if (state.get('requestAction') == 'abort'
                    and state.get('requestTaskId') == args.expected_task_id):
                print('OPERATOR_ABORTED_BEFORE_CLIENT_START', flush=True)
                return
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
    from voice_stt_client.ui import v2_core_bridge
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
    original_bridge = v2_core_bridge.V2CoreBridge
    instruction_lock = threading.Lock()
    control_seen = {'secondary': False}
    def editor_instruction(text, step=None, seconds=None):
        with instruction_lock:
            path = state_file.parent/'command.json'
            temporary = path.with_suffix('.observer.tmp')
            temporary.write_text(json.dumps(dict(action='progress' if step is not None else 'instruction', text=text,
                taskId=args.expected_task_id,step=step,seconds=seconds)), encoding='utf8')
            temporary.replace(path)

    def diagnostic(kind, **fields):
        with trace.open('a', encoding='utf8') as handle:
            handle.write(json.dumps(dict(type=kind, timeUtc=datetime.now(UTC).isoformat(),
                monotonic=time.monotonic(), **fields), ensure_ascii=True)+'\n')

    class ObservedBridge(original_bridge):
        def __init__(self, *values, **options):
            super().__init__(*values, **options)
            if args.editor_guided:
                from PySide6.QtCore import QTimer
                from PySide6.QtWidgets import QApplication
                self._operator_abort_timer = QTimer(self)
                self._operator_abort_timer.setInterval(100)
                def check_abort():
                    current = read_editor_state(state_file)
                    if (current.get('requestAction') == 'abort'
                            and current.get('requestTaskId') == args.expected_task_id):
                        self._operator_abort_timer.stop()
                        diagnostic('operator.abort', taskId=args.expected_task_id)
                        QApplication.instance().quit()
                self._operator_abort_timer.timeout.connect(check_abort)
                self._operator_abort_timer.start()

        def _remember_view(self, view):
            super()._remember_view(view)
            keys = (view.controls.enabled, view.controls.primary_key, view.controls.secondary_key)
            if view.ready and getattr(self, '_observed_controls', None) != keys:
                self._observed_controls = keys
                diagnostic('controls.confirmed', enabled=keys[0], primaryKey=keys[1], secondaryKey=keys[2],
                    primaryAction=str(view.controls.primary_action), secondaryAction=str(view.controls.secondary_action))

        def press_control(self, slot):
            # Observe the actual native-hotkey callback, with no injected impulse.
            view = self._published_view
            diagnostic('control.received', slot=str(slot), ready=bool(view and view.ready),
                generation=view.generation if view else None,
                phase=str(view.mirror.input.phase) if view else None,
                activationId=view.mirror.input.activation_id if view else None)
            if str(slot) == 'secondary':
                control_seen['secondary'] = True
            result = super().press_control(slot)
            if args.editor_guided and args.editor_case == 'manual' and str(slot) == 'secondary':
                if view and view.mirror.input.activation_id:
                    editor_instruction('F9 ANGEKOMMEN – TEXT UND ABSCHLUSS ABWARTEN',6)
                else:
                    editor_instruction('F9 IM LEERLAUF – BITTE ZUERST F8 DRÜCKEN',3)
            return result

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
                if args.editor_guided and args.editor_case == 'manual' and str(event.type) == 'activation.started':
                    editor_instruction('F8 ANGEKOMMEN – GRÜNEN SATZ SPRECHEN',4)
                if args.editor_guided and str(event.type) == 'segment.recording_started':
                    editor_instruction('AUFNAHME LÄUFT – GRÜNEN SATZ SPRECHEN',4)
                if args.editor_guided and str(event.type) == 'segment.recording_ended':
                    deadline = self.mirror.mirror.view.input.deadline
                    seconds = deadline.remaining(time.monotonic())/1000 if deadline else None
                    editor_instruction('SATZ BEENDET – F9 KURZ DRÜCKEN UND TASTEN LOSLASSEN',5,seconds)
                if args.editor_guided and str(event.type) in (
                        'activation.completed', 'activation.cancelled', 'activation.failed'):
                    count = sum(a.status in ('completed', 'cancelled', 'failed')
                                for a in self.mirror.mirror.view.activations.values())
                    if count >= 1:
                        prefix = ('F9 ANGEKOMMEN – BITTE KURZ WARTEN' if args.editor_case == 'manual'
                                  and control_seen['secondary'] else 'BITTE KURZ WARTEN')
                        editor_instruction(prefix+' – TESTCLIENT WIRD BEENDET',6)

            self.session.on_message = receive
            previous_completion = self.session.on_completion

            def completed(value):
                if previous_completion:
                    previous_completion(value)
                diagnostic('command.completed', commandType=str(value.command.type),
                    action=value.command.payload.get('action'), commandId=value.command.commandId,
                    accepted=value.ack.accepted, result=str(value.ack.result),
                    activationId=value.ack.activationId, inputPhase=str(value.ack.inputPhase))

            self.session.on_completion = completed
            if args.stop_after:
                original_run = self.run

                async def stop_when_finished():
                    deadline = time.monotonic() + 180
                    shown = False
                    preparation_started = None
                    while not self.is_closing:
                        if args.editor_guided and not shown and self.is_ready and self.media.audio_available:
                            if preparation_started is None:
                                preparation_started = time.monotonic()
                                diagnostic('guided.preparation_started',seconds=args.prepare_seconds)
                                editor_instruction('BEREITMACHEN – NOCH NICHT SPRECHEN',2,args.prepare_seconds)
                            if time.monotonic()-preparation_started >= args.prepare_seconds:
                                shown = True
                                diagnostic('guided.client_ready', audioAvailable=True, runtimeReady=True)
                                if self.mirror.mirror.view.input.activation_id is None:
                                    editor_instruction('CLIENT BEREIT – JETZT F8 DRÜCKEN' if args.editor_case == 'manual'
                                        else 'CLIENT BEREIT – JETZT GRÜNEN SATZ SPRECHEN',3)
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
    v2_core_bridge.V2CoreBridge = ObservedBridge
    try:
        run(args.mode)
    finally:
        v2_runtime.V2Runtime = original
        v2_core_bridge.V2CoreBridge = original_bridge
        if args.editor_guided:
            editor_instruction('AUFGABE BEENDET – TESTCLIENT AUS\n'
                               '• Die nächste Aufgabe benötigt wieder deinen Start.')


if __name__ == '__main__':
    main()
