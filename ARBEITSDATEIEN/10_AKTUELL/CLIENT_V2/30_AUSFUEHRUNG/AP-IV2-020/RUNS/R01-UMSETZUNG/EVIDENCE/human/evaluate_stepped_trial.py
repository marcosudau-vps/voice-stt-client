"""Evaluate the two consented direct phrases; export no unrelated history/text.

Requires an explicit session folder per task and the operator's actual feedback.
Process exit alone never establishes functional success or a complete M-case.
"""
import argparse
from collections import Counter
from datetime import UTC, datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import sqlite3

from editor_state import owned_editor_path, read_editor_state

EXPECTED = {'jarvis': 'Der rote Ball liegt auf dem Boden.',
            'alexa': 'Die gelbe Tasche steht vor der Tür.'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trial', type=Path, required=True)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--session', type=Path, action='append', required=True)
    parser.add_argument('--human-feedback', required=True)
    args = parser.parse_args()
    local = Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020'
    state_path = owned_editor_path(args.state, local)
    state = read_editor_state(state_path)
    trial = json.loads(args.trial.read_text(encoding='utf8'))
    assert [r['case'] for r in trial['tasks']] == ['jarvis', 'alexa']
    assert len(args.session) == 2
    output = args.trial.parent
    target = output/'assessment.json'
    if target.exists():
        raise FileExistsError('Never overwrite a prior evaluation')
    qualified = json.loads((output.parent/'real-recovery.json').read_text(encoding='utf8'))['before']
    report = dict(productCommit=qualified['commit'], serverCommit='ada13b011e1d3829f78e7f389e3b927795a2b3be',
        evaluatedAtUtc=datetime.now(UTC).isoformat(), evaluatorSha256=digest(Path(__file__).read_bytes()),
        humanFeedback=args.human_feedback, humanFeedbackOrigin='Actual user reply in this R01 chat', tasks=[])
    manifest = []
    def export(name, value):
        data = (json.dumps(value, ensure_ascii=True, indent=2)+'\n').encode()
        (output/name).write_bytes(gzip.compress(data, mtime=0))
        manifest.append(dict(file=name, uncompressedSha256=digest(data), sha256=digest((output/name).read_bytes())))
    db = sqlite3.connect('file:'+str(local/'client/history-wake.sqlite')+'?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        for task, folder in zip(trial['tasks'], args.session):
            # Containment check only; keep logical Windows AppData path for I/O.
            folder.resolve().relative_to((local/'sessions').resolve())
            events = [json.loads(l) for l in (Path(task['observation'])/'events.jsonl').read_text().splitlines()]
            trace = [json.loads(l) for l in (folder/'trace.jsonl').read_text().splitlines()]
            identity = json.loads((folder/'identity.json').read_text())
            finals = [e for e in events if e['type']=='transcription.completed']
            hits = [e for e in events if e['type']=='wakeword.detected']
            assert len(finals)==len(hits)==1
            session_id = finals[0]['sessionId']
            assert all(e.get('sessionId', session_id)==session_id for e in events)
            entries = [dict(r) for r in db.execute('SELECT id,session_id,segment_id,activation_id,text,text_length FROM history_entries WHERE session_id=?', (session_id,))]
            assert len(entries)==1
            attempts = [dict(r) for r in db.execute('SELECT status,source,error FROM injection_attempts WHERE entry_id=?', (entries[0]['id'],))]
            expected = EXPECTED[task['case']]
            entry = entries[0]
            history_exact = entry.pop('text') == expected
            entry['textSha256'] = digest(expected.encode()) if history_exact else None
            metrics = [r for r in trace if r['kind']=='metrics']
            acknowledgements = [r for r in trace if r['kind']=='ack']
            end = next(e for e in events if e['type']=='segment.recording_ended')
            closed = next(e for e in events if e['type']=='activation.input_closed')
            applied = [r for r in events if r.get('effectiveFollowupMs')==5000 and r.get('effectivePreRollMs')==320]
            row = dict(case=task['case'], taskId=task['taskId'], operatorStartSequence=task['actualStartSequence'],
                sessionId=session_id, activationId=finals[0]['activationId'], wakeWordId=hits[0]['wakeWordId'], score=hits[0]['score'],
                configurationSha256=identity['configSha256'], sourceHead=identity['candidate']['commit'],
                qualifiedSourceHashEquality=identity['candidate']['sourceSha256']==qualified['sourceSha256'],
                finalExact=finals[0]['textSha256']==digest(expected.encode()), rawHistoryExact=history_exact,
                history=entry, injectionAttempts=attempts, eventCounts=dict(Counter(e['type'] for e in events)),
                inputClosedReason=closed['reason'], nativeFinishCommandAcknowledgements=sum(r['type']=='activation' for r in acknowledgements),
                finalAfterRecordingEndedMs=round((finals[0]['monotonic']-end['monotonic'])*1000,3),
                followupUntilCloseMs=closed['occurredAtUnixMs']-end['occurredAtUnixMs'],
                effectiveSettingsConfirmed=bool(applied), effectiveFollowupMs=5000, effectivePreRollMs=320,
                metricsSamples=len(metrics), maxTasks=max(r['tasks'] for r in metrics), lastTasks=metrics[-1]['tasks'],
                maxPrivateBytes=max(r['memory']['privateBytes'] for r in metrics),
                lastTrackerPending=metrics[-1]['trackerPending'], lastInjectionQueue=metrics[-1]['injectionQueue'],
                lastMedia=metrics[-1]['media'], lastCapture=metrics[-1]['capture'],
                processExitCode=task['processExitCode'], sessionStopped=trace[-1]['kind']=='session_stopped')
            row['directPhraseAndOutputResult'] = 'PASS' if all((row['finalExact'], history_exact,
                row['qualifiedSourceHashEquality'], row['effectiveSettingsConfirmed'], row['sessionStopped'],
                len(attempts)==1 and attempts[0]['status']=='command_sent', task['processExitCode']==0)) else 'FAIL'
            report['tasks'].append(row)
            for suffix, value in (('events',events),('trace',trace),('identity',identity)):
                export(task['case']+'-'+suffix+'.json.gz', value)
    finally:
        db.close()
    editor_events = [json.loads(l) for l in (state_path.parent/'events.jsonl').read_text().splitlines()]
    # Export only the chosen task IDs and paste/state changes during these trials.
    begin = next(e['timeUtc'] for e in editor_events if e['kind']=='operator_start' and e['taskId']==trial['tasks'][0]['taskId'])
    end = trace[-1]['timeUtc']
    safe_keys = ('kind','timeUtc','monotonic','foreground','editorHasFocus','operatorReady','taskId',
                 'startSequence','changes','characters','sha256','shiftHeld','altHeld','hasText','elevated')
    safe = [{k:e[k] for k in safe_keys if k in e} for e in editor_events if begin <= e['timeUtc'] <= end]
    export('editor-events.json.gz',safe)
    expected_editor = ''.join(EXPECTED[k]+' ' for k in ('jarvis','alexa'))
    report['editor'] = dict(characters=state['characters'], sha256=state['sha256'],
        expectedCharacters=len(expected_editor), exact=state['testText']==expected_editor,
        nativePasteKeyCount=sum(e['kind']=='paste_key' for e in safe),
        nativePasteMimeCount=sum(e['kind']=='paste_mime' for e in safe),
        actualSeparateStarts=[e for e in safe if e['kind']=='operator_start'])
    report['directPhraseAndSpacedOutputResult'] = 'PASS' if report['editor']['exact'] and all(
        r['directPhraseAndOutputResult']=='PASS' for r in report['tasks']) else 'FAIL'
    report['hotkeyFinish'] = 'NOT_PROVEN: both input windows timed out; no activation command acknowledged'
    report['completeM02'] = 'NOT_PROVEN: separate sessions, controls/phonetic annotation still open'
    report['completeM12'] = 'NOT_PROVEN: not a 30min/100-activation run'
    report['boundaries'] = 'Human live speech and visible-output confirmation; real ReSpeaker, models, native clipboard/SendInput. No raw audio recorded. Source run; frozen build separately qualified. No claim of all-parameter subjective acceptance.'
    report['files'] = manifest
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(result=report['directPhraseAndSpacedOutputResult'], evidence=str(target),
                          hotkeyFinish=report['hotkeyFinish'])))


if __name__=='__main__':
    main()
