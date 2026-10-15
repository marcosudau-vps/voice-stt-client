"""Read-only event observer around the existing isolated desktop test runner.

Run with the project venv and --mode manual|wake|both. No production files are
modified. The observer chains existing callbacks; transport/reducers/audio and
Windows side effects remain production-owned. Raw text/tokens are never logged.
"""
import argparse
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
    os.environ['VOICESTT_CLIENT_HOME'] = str(local / 'client')
    from voice_stt_client.core import v2_runtime
    from scripts.qualify_v2_session import run
    folder = local / 'observations' / datetime.now().strftime('%Y%m%d-%H%M%S')
    folder.mkdir(parents=True)
    trace = folder / 'events.jsonl'
    (local / 'active-observation.json').write_text(json.dumps(dict(
        folder=str(folder), pid=os.getpid(), mode=args.mode,
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

    v2_runtime.V2Runtime = ObservedRuntime
    try:
        run(args.mode)
    finally:
        v2_runtime.V2Runtime = original


if __name__ == '__main__':
    main()
