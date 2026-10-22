"""Evaluate one explicitly selected manual speech trial, without exporting text.

Uses the actual native callbacks, protocol Acks, selected-session history and
owned-editor paste events. Orthographic ASR differences remain visible in the
assessment; the authoritative final must reach the editor unchanged.
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


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trial', type=Path, required=True)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--session', type=Path, required=True)
    parser.add_argument('--human-feedback', required=True)
    args = parser.parse_args()
    local = Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020'
    state_path = owned_editor_path(args.state, local)
    state = read_editor_state(state_path)
    trial = json.loads(args.trial.read_text(encoding='utf8'))
    assert len(trial['tasks']) == 1 and trial['tasks'][0]['case'] == 'manual'
    task = trial['tasks'][0]
    folder = args.session
    folder.resolve().relative_to((local/'sessions').resolve())
    observation = Path(task['observation'])
    observation.resolve().relative_to((local/'observations').resolve())
    events = [json.loads(s) for s in (observation/'events.jsonl').read_text().splitlines()]
    trace = [json.loads(s) for s in (folder/'trace.jsonl').read_text().splitlines()]
    identity = json.loads((folder/'identity.json').read_text())
    qualified = json.loads((args.trial.parent.parent/'windows-hotkeys.json').read_text())['after']
    finals = [e for e in events if e['type'] == 'transcription.completed']
    assert len(finals) == 1
    final = finals[0]
    sid = final['sessionId']
    assert all(e.get('sessionId', sid) == sid for e in events)
    db = sqlite3.connect('file:'+str(local/'client/history-manual.sqlite')+'?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        entries = [dict(r) for r in db.execute(
            'SELECT id,session_id,activation_id,segment_id,text,text_length FROM history_entries WHERE session_id=?', (sid,))]
        assert len(entries) == 1
        entry = entries[0]
        text = entry.pop('text')
        attempts = [dict(r) for r in db.execute(
            'SELECT status,source,error FROM injection_attempts WHERE entry_id=?', (entry['id'],))]
    finally:
        db.close()
    controls = [e for e in events if e['type'] == 'control.received']
    actions = [e for e in events if e['type'] == 'command.completed' and e['action'] in ('activate', 'finish')]
    assert [e['slot'] for e in controls] == ['primary', 'secondary']
    assert [e['action'] for e in actions] == ['activate', 'finish']
    assert all(e['accepted'] and e['result'] == 'applied' and e['activationId'] == final['activationId'] for e in actions)
    ended = next(e for e in events if e['type'] == 'segment.recording_ended')
    closed = next(e for e in events if e['type'] == 'activation.input_closed')
    assert closed['reason'] == 'finished'
    metrics = [e for e in trace if e['kind'] == 'metrics']
    editor_events = [json.loads(s) for s in (state_path.parent/'events.jsonl').read_text().splitlines()]
    begin = next(e['timeUtc'] for e in editor_events if e['kind'] == 'operator_start' and e['taskId'] == task['taskId'])
    safe_keys = ('kind','timeUtc','monotonic','foreground','editorHasFocus','operatorReady','taskId',
                 'startSequence','changes','characters','sha256','shiftHeld','altHeld','hasText','elevated')
    safe = [{k:e[k] for k in safe_keys if k in e} for e in editor_events if begin <= e['timeUtc'] <= trace[-1]['timeUtc']]
    keys = [e for e in safe if e['kind'] == 'paste_key']
    pastes = [e for e in safe if e['kind'] == 'paste_mime']
    assert len(keys) == len(pastes) == 1 and not keys[0]['shiftHeld'] and not keys[0]['altHeld']
    source_match = identity['candidate']['sourceSha256'] == qualified['sourceSha256']
    assert source_match
    authoritative_match = sha(text.encode()) == final['textSha256']
    editor_match = state['testText'] == text+' ' and pastes[0]['sha256'] == sha((text+' ').encode())
    assert authoritative_match and editor_match
    assert attempts == [dict(status='command_sent', source='automatic', error=None)]
    assert task['processExitCode'] == 0 and trace[-1]['kind'] == 'session_stopped'
    assert task['operatorDecision'] == 'accept' and state['phase'] == 'done'
    output = args.trial.parent
    target = output/'assessment.json'
    if target.exists():
        raise FileExistsError('Preserve prior trial assessment')
    manifest = []
    for name, data in [('events',events), ('trace',trace), ('identity',identity), ('editor-events',safe)]:
        raw = (json.dumps(data,ensure_ascii=True,indent=2)+'\n').encode()
        filename = name+'.json.gz'
        packed = gzip.compress(raw,mtime=0)
        (output/filename).write_bytes(packed)
        manifest.append(dict(file=filename,sha256=sha(packed),uncompressedSha256=sha(raw)))
    result = dict(result='PASS_CONTROL_AND_NATIVE_OUTPUT',evaluatedAtUtc=datetime.now(UTC).isoformat(),
        evaluatorSha256=sha(Path(__file__).read_bytes()),humanFeedback=args.human_feedback,
        humanFeedbackOrigin='Actual human reply in R01 chat',productCommit='d95043e96051d4022b297099391a4fdff0dcc12b',
        sourceCommit=identity['candidate']['commit'],qualifiedFullSourceManifestMatch=source_match,
        serverCommit='ada13b011e1d3829f78e7f389e3b927795a2b3be',configurationSha256=identity['configSha256'],
        sessionId=sid,activationId=final['activationId'],segmentId=final['segmentId'],
        operatorStartSequence=task['actualStartSequence'],nativeControls=controls,activationAcks=actions,
        inputClosedReason=closed['reason'],finalAfterRecordingEndedMs=round((final['monotonic']-ended['monotonic'])*1000,3),
        expectedPlannedPhraseSha256=sha(task['phrase'].encode()),actualFinalSha256=final['textSha256'],
        plannedPhraseExactMatch=text==task['phrase'],
        plannedDifference=('NONE' if text==task['phrase'] else
            'Hyphenation differs; removing hyphens matches the planned phrase exactly. Human confirms complete content; exact planned spelling is not claimed.'
            if text.replace('-','')==task['phrase'].replace('-','') else
            'Other ASR difference retained. This assessment proves controls and unchanged native output, not exact planned wording.'),
        authoritativeFinalHistoryExact=authoritative_match,recognizedFinalAndSpaceExactlyInEditor=editor_match,
        editorCharacters=state['characters'],editorSha256=state['sha256'],nativePasteCount=len(pastes),
        shiftHeldAtPaste=False,altHeldAtPaste=False,injectionAttempts=attempts,
        eventCounts=dict(Counter(e['type'] for e in events)),metricsSamples=len(metrics),
        peakTasks=max(m['tasks'] for m in metrics),peakPrivateBytes=max(m['memory']['privateBytes'] for m in metrics),
        lastMetrics=metrics[-1],sessionStopped=True,processExitCode=0,operatorDecision='accept',
        boundaries='Live human speech, real ReSpeaker/ASR/server/native hotkeys/Clipboard/SendInput/owned editor. Source desktop, not Frozen. One activation/segment; full M01 multi-segment/overlap, M04 phase matrix and M12 remain NOT_PROVEN.',
        files=manifest)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('PASS: actual manual Activate/Finish, one final/history/native paste, authoritative text preserved; planned spelling difference retained; full M-gates open')


if __name__ == '__main__':
    main()
