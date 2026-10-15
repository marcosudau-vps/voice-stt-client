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
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('manual', 'wake', 'both'), default='wake')
    parser.add_argument('--self-check', action='store_true')
    parser.add_argument('--wait-for-editor-state', type=Path)
    parser.add_argument('--stop-after', type=int, default=0)
    args = parser.parse_args()
    if args.self_check:
        from types import SimpleNamespace
        record = safe_event(SimpleNamespace(generation=2), SimpleNamespace(
            type='transcription.completed', payload=dict(activationId='a',
            text='deliberate test', logAccess='secret', accessToken='secret',
            effectiveSettings={'activation.followupTimeoutMs': 5000, 'private': 'secret'})))
        assert record['activationId'] == 'a' and record['effectiveFollowupMs'] == 5000
        assert record['textLength'] == 15 and 'text' not in record
        assert 'secret' not in json.dumps(record)
        print('PASS: explicit identity/settings allowlist; text hashed; tokens excluded')
        return
    local = Path(os.environ['LOCALAPPDATA']) / 'VoiceSTT-Qualification/AP-IV2-020'
    focus_gate = None
    if not 0 <= args.stop_after <= 100:
        parser.error('--stop-after must be 0..100')
    if args.wait_for_editor_state:
        state_file = args.wait_for_editor_state.resolve()
        if not state_file.is_relative_to((local / 'editors').resolve()):
            parser.error('Only the owned test editor state is allowed')
        deadline = time.monotonic() + 120
        print('Waiting for operator to focus the owned test editor', flush=True)
        while True:
            state = json.loads(state_file.read_text(encoding='utf8'))
            fresh = abs((datetime.now(UTC) - datetime.fromisoformat(state['timeUtc'])).total_seconds()) < 2
            if fresh and state['foreground']:
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
        helperSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())), encoding='utf8')
    original = v2_runtime.V2Runtime

    class ObservedRuntime(original):
        def __init__(self, *values, **options):
            super().__init__(*values, **options)
            previous = self.session.on_message

            def receive(binding, event):
                previous(binding, event)
                record = safe_event(binding, event)
                record.update(timeUtc=datetime.now(UTC).isoformat(), monotonic=time.monotonic())
                with trace.open('a', encoding='utf8') as handle:
                    handle.write(json.dumps(record, ensure_ascii=True) + '\n')

            self.session.on_message = receive
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


if __name__ == '__main__':
    main()
