"""Resolve retained AP020 evidence offline; never start a client or server.

Only the explicit repository output is written. Runtime folders and retained
server sources are read-only inputs. Output contains hashes, IDs and counters,
never historical free-form speech, credentials, profiles or complete logs.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gc
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())
EVIDENCE = Path(__file__).resolve().parents[1]
PIN = 'ada13b011e1d3829f78e7f389e3b927795a2b3be'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]


def find_code(path, expected):
    """Find exactly recorded runner bytes, including explicit CRLF reconstruction."""
    commits = subprocess.check_output(['git', '-C', str(ROOT), 'log', '--all',
                                      '--format=%H', '--', path], text=True).splitlines()
    for commit in commits:
        result = subprocess.run(['git', '-C', str(ROOT), 'show', commit+':'+path], capture_output=True)
        if result.returncode:
            continue
        raw = result.stdout
        for mode, data in [('GIT_BYTES', raw), ('LF_TO_CRLF', raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))]:
            if sha(data) == expected:
                return {'path': path, 'recordedSha256': expected, 'retainedCommit': commit,
                        'byteRepresentation': mode, 'result': 'EXACT_RECORDED_HASH_FOUND'}, data
    return {'path': path, 'recordedSha256': expected, 'result': 'NOT_PROVEN'}, b''


def source_check(source, repository):
    tree = subprocess.check_output(['git', '-C', str(repository), 'ls-tree', '-rz', PIN])
    checked = {}
    for entry in tree.split(b'\0'):
        if not entry:
            continue
        meta, name = entry.split(b'\t', 1)
        _, kind, oid = meta.split()
        if kind != b'blob':
            continue
        name = name.decode('utf-8')
        data = (source/name).read_bytes()
        actual = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if actual != oid.decode():
            raise ValueError('Retained source differs from pinned Git blob: '+name)
        checked[name] = sha(data)
    return checked


def metadata(source, hashes):
    import onnxruntime as ort
    old_record = read(EVIDENCE/'real-wake-artifacts.json')
    packed = (EVIDENCE/old_record['log']).read_bytes()
    raw = gzip.decompress(packed)
    assert sha(packed) == old_record['gzipSha256'] and sha(raw) == old_record['sha256']
    historical = json.loads(raw.decode('utf-8').split('\n', 1)[1])
    base = source/'VoiceSTT/assets/wakeword_models'
    manifest = read(base/'models.json')
    options = ort.SessionOptions()
    options.log_severity_level = 3
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.enable_profiling = False
    result = []
    for row in historical['rows']:
        path = base/row['artifact']
        digest = sha(path.read_bytes())
        assert digest == hashes[path.relative_to(source).as_posix()]
        # Membership in the pinned manifest is checked separately from old results.
        matches = [v for v in manifest['wakeWords'] if v['id'] == row['id']]
        assert len(matches) == 1
        artifact = matches[0]['artifacts']['onnx']
        assert artifact['sha256'] == digest and artifact['file'] == path.name
        session = ort.InferenceSession(str(path), sess_options=options, providers=['CPUExecutionProvider'])
        frames = session.get_inputs()[0].shape[1]
        measured = {'id': row['id'], 'artifact': path.name, 'bytes': path.stat().st_size,
                    'inputFrames': frames, 'receptiveFieldMs': (frames-1)*80.0+760.0}
        assert all(measured[k] == row[k] for k in measured), row['id']
        measured.update(sha256=digest, onnxLoad='PASS', historicalCoreMetadataEqual=True)
        result.append(measured)
        del session
        gc.collect()
    return {'result': 'PASS_OFFLINE_METADATA_ONLY', 'onnxruntime': ort.__version__,
            'rows': result, 'sourceGitBlobsVerified': len(hashes),
            'receptiveFieldFormula': '(frames - 1) * 80 + 760; diagnostic only',
            'notReplayed': ['server runtime', 'TFLite health', 'inference scores', 'historical environment'],
            'oldEvidenceStillExcluded': True}


def fixture_checks():
    manifest = read(EVIDENCE/'human/samples/manifest.json')
    verified = []
    for record in manifest['records']:
        name = Path(record['file']).name
        p = EVIDENCE/'human/samples'/name
        digest = sha(p.read_bytes())
        assert digest == record['sha256'], name
        verified.append({'file': name, 'sha256': digest})
    full = EVIDENCE/'human/wake-scores-full.json.gz'
    score = read(EVIDENCE/'human/wake-scores-summary.json')
    unpacked = gzip.decompress(full.read_bytes())
    assert sha(unpacked) == score['fullTraceUncompressedSha256']
    known = {r['file']: r['sha256'] for r in verified}
    for trace in score['traces']:
        assert trace['audioSha256'] == known[Path(trace['audio']).name]
    replay = read(EVIDENCE/'human/wake-replay-calibration.json')
    for run in replay['runs']:
        for row in run['rows']:
            assert row['audioSha256'] == known[row['case']+'.wav']
    later = read(EVIDENCE/'ux02/real-model-replay-summary.json')
    for row in later['rows']:
        assert row['audioSha256'] == known[row['case']+'.wav']
    wrapper = read(EVIDENCE/'ux02/real-model-replay.json')
    packed = (EVIDENCE/'ux02'/wrapper['log']).read_bytes()
    assert sha(packed) == wrapper['gzipSha256'] and sha(gzip.decompress(packed)) == wrapper['sha256']
    return {'files': verified, 'scoreTraceSha256': sha(unpacked), 'scoreTraceGzipSha256': sha(full.read_bytes()),
            'scoreAndReplayInputHashesMatchRetainedWavs': True,
            'laterSixFixtureReplay': {'record': 'ux02/real-model-replay-summary.json', 'rows': len(later['rows']),
                'productCommit': later['identity']['commit'], 'preRollMs': sorted({r['preRollMs'] for r in later['rows']}),
                'helperSha256': later['helperSha256'], 'executionLogHashesVerified': True,
                'actualWordGroundTruth': 'NOT_PROVEN for Alexa-pause; planned mismatch preserved'}}


def retained_helpers():
    checks = []
    admission = read(EVIDENCE/'real-admission.json')
    digest = admission['identity']['sourceSha256']['scripts/qualify_v2_real.py']
    check, _ = find_code('scripts/qualify_v2_real.py', digest)
    check['record'] = 'real-admission.json'
    checks.append(check)
    replay = read(EVIDENCE/'human/wake-replay-calibration.json')
    for digest in sorted({r['helperSha256'] for r in replay['runs']}):
        check, code = find_code((EVIDENCE/'human/replay_real_samples.py').relative_to(ROOT).as_posix(), digest)
        check.update(record='human/wake-replay-calibration.json', admissionGuardInExactCode=
                     b"accepted.payload['serverCommit'] != '"+PIN.encode()+b"'" in code)
        checks.append(check)
    score = read(EVIDENCE/'human/wake-scores-summary.json')
    check, code = find_code((EVIDENCE/'human/score_real_wake.py').relative_to(ROOT).as_posix(), score['helperSha256'])
    check.update(record='human/wake-scores-summary.json', pinnedQualifiedImportInExactCode=b"'/qualified'" in code)
    checks.append(check)
    disk = read(EVIDENCE/'ux01/logstore-diskfull.json')
    check, code = find_code((EVIDENCE/'logstore_diskfull.py').relative_to(ROOT).as_posix(), disk['helperSha256'])
    check.update(record='ux01/logstore-diskfull.json', imageRecordedFromInspection=b"containerImage=guard()['Image']" in code,
                 imageEqualsQualifiedBuild=disk['containerImage'] == read(EVIDENCE/'local-server-build.json')['imageId'])
    checks.append(check)
    return checks


def select_observation(trace, observations):
    ack_ids = {r['commandId'] for r in trace if r.get('kind') == 'ack'}
    matches = [(file, events, len(ack_ids & command_ids)) for file, events, command_ids in observations
               if ack_ids & command_ids]
    if len(matches) > 1:
        raise ValueError('Ambiguous session/observation command identity')
    if matches:
        return (*matches[0], 'SHARED_COMMAND_IDS')
    start = datetime.fromisoformat(trace[0]['timeUtc'])
    # Temporal fallback applies only to old observers that recorded no command IDs.
    # Explicitly conflicting IDs can never be overridden by a similar timestamp.
    temporal = [(file, events, 0) for file, events, command_ids in observations if events and not command_ids
                and abs((datetime.fromisoformat(events[0]['timeUtc'])-start).total_seconds()) < 5]
    if len(temporal) == 1:
        return (*temporal[0], 'UNIQUE_START_TIME_WITHIN_5S_NOT_COMMAND_ID_PROOF')
    return None, [], 0, None


def session_checks(runtime):
    observations = []
    for file in sorted((runtime/'observations').glob('*/events.jsonl')):
        events = rows(file)
        command_ids = {r['commandId'] for r in events if r.get('type') == 'command.completed'}
        observations.append((file, events, command_ids))
    result = []
    for directory in sorted((runtime/'sessions').iterdir()):
        identity_path, trace_path = directory/'identity.json', directory/'trace.jsonl'
        if not identity_path.is_file() or not trace_path.is_file():
            continue
        identity = read(identity_path)
        trace = rows(trace_path)
        event_path, events, common_ids, match_method = select_observation(trace, observations)
        ids = sorted({r['sessionId'] for r in events if r.get('sessionId')})
        activations = sorted({r['activationId'] for r in events if r.get('activationId')})
        # Read only explicit allowlisted identity fields; do not export speech.
        all_rows = trace+events
        pins = sorted({r['serverCommit'] for r in all_rows if r.get('serverCommit')})
        ready = [r for r in trace if r.get('kind') == 'metrics' and r.get('ready')]
        def bounds(key, section=None):
            values = [r.get(section, {}).get(key) if section else r.get(key) for r in ready]
            values = [v for v in values if isinstance(v, (int, float))]
            return {'first': values[0], 'min': min(values), 'max': max(values), 'last': values[-1]} if values else None
        result.append({'folder': directory.name, 'identitySha256': sha(identity_path.read_bytes()),
                       'traceSha256': sha(trace_path.read_bytes()), 'eventsSha256': sha(event_path.read_bytes()) if events else None,
                       'observationFolder': event_path.parent.name if event_path else None, 'matchingCommandIds': common_ids,
                       'observationMatchMethod': match_method,
                       'candidateCommit': identity['candidate']['commit'], 'configurationSha256': identity['configSha256'],
                       'mode': identity['mode'], 'timeUtcFirst': trace[0]['timeUtc'], 'timeUtcLast': trace[-1]['timeUtc'],
                       'sessionIds': ids, 'activationIds': activations,
                       'recordedServerCommits': pins, 'traceRows': len(trace), 'eventRows': len(events),
                       'eventCounts': dict(Counter(r.get('type') for r in events)),
                       'transportStates': [r['state'] for r in trace if r.get('kind') == 'transport'],
                       'observedResources': {'readySamples': len(ready),
                           'privateBytes': bounds('privateBytes', 'memory'), 'tasks': bounds('tasks'),
                           'captureQueueDepth': bounds('capture_queue_depth', 'capture'),
                           'injectionQueue': bounds('injectionQueue'),
                           'lastActivations': ready[-1].get('activations') if ready else None,
                           'lastTerminalActivations': ready[-1].get('terminalActivations') if ready else None},
                       'settings': sorted({(r.get('effectiveFollowupMs'), r.get('effectivePreRollMs')) for r in events
                                           if 'effectiveFollowupMs' in r}, key=str),
                       'pinLimitation': 'No independent admission response retained' if not pins else None})
    return result


def terminal_check(runtime):
    assessment = read(EVIDENCE/'tv-wake-finish-20261018/live-analysis.json')
    activation = assessment['activationId']
    events = rows(runtime/'observations/20261018-020836/events.jsonl')
    selected = [r for r in events if r.get('activationId') == activation]
    close = next(r for r in selected if r['type'] == 'activation.input_closed')
    terminals = [r for r in selected if r['type'] in ('activation.completed', 'activation.cancelled', 'activation.failed')]
    trace = rows(runtime/'sessions/20261018-020836/trace.jsonl')
    last = trace[-1]
    duration = (datetime.fromisoformat(last['timeUtc'])-datetime.fromisoformat(close['timeUtc'])).total_seconds()
    return {'activationId': activation, 'inputCloseReason': close['reason'], 'inputClosedAtUtc': close['timeUtc'],
            'lastSessionObservationAtUtc': last['timeUtc'], 'secondsAfterClose': round(duration, 3),
            'terminalEvents': len(terminals), 'finalEvents': sum(r['type'] == 'transcription.completed' for r in selected),
            'acceptedEvents': sum(r['type'] == 'transcription.accepted' for r in selected),
            'observationEventsSha256': sha((runtime/'observations/20261018-020836/events.jsonl').read_bytes()),
            'conclusion': 'Finish, not cancel; missing final/terminal persists to recorded client shutdown. Server worker cause NOT_PROVEN.'}


def record_bindings(sessions):
    names = ['human/manual-followup-5000.json', 'human/wake-first-live.json',
             'ux01/repeatable-manual-20261016-01/assessment.json',
             'ux01/stepped-20261016-01/assessment.json', 'ux02/manual-voice-20261016-01/assessment.json',
             'human/free-exploration-20261016-01.json', 'ux03-close-sound/human-hearing-confirmed.json',
             'led-white-variant/native-ready.json', 'wake-retrigger-20261018/live-analysis.json',
             'tv-wake-finish-20261018/live-analysis.json']
    def values(value, keys):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in keys and isinstance(child, str):
                    yield child
                yield from values(child, keys)
        elif isinstance(value, list):
            for child in value:
                yield from values(child, keys)
    result = []
    for name in names:
        d = read(EVIDENCE/name)
        ids = set(values(d, {'sessionId', 'session_id'}))
        activation_ids = set(values(d, {'activationId', 'activation_id'}))
        configs = set(values(d, {'configSha256', 'configurationSha256', 'profileSha256'}))
        evidence_command_ids = set(values(d, {'commandId'}))
        folder = Path(d.get('session', {}).get('folder', '')).name
        matched = []
        for session in sessions:
            methods = []
            if ids & set(session['sessionIds']): methods.append('SESSION_ID')
            if activation_ids & set(session['activationIds']): methods.append('ACTIVATION_ID')
            if folder and session['folder'] == folder: methods.append('RECORDED_FOLDER')
            if not methods and evidence_command_ids:
                # Root traces include acknowledgements even before observers existed.
                # IDs are checked in the retained trace, never inferred from clock time.
                if evidence_command_ids & set(session.get('_ackIds', [])): methods.append('ACK_COMMAND_ID')
            if methods:
                matched.append({'folder': session['folder'], 'methods': methods,
                                'configurationHashMatches': session['configurationSha256'] in configs if configs else None,
                                'recordedServerCommits': session['recordedServerCommits']})
        result.append({'record': name, 'recordSha256': sha((EVIDENCE/name).read_bytes()),
                       'matchedSessions': matched, 'limitation': 'Session binding does not create a missing independent server admission attestation'})
    return result


def archive_checks():
    result = []
    for name in ['ux01/stepped-20261016-01/assessment.json', 'ux02/manual-voice-20261016-01/assessment.json']:
        p = EVIDENCE/name
        d = read(p)
        for f in d['files']:
            packed = (p.parent/f['file']).read_bytes()
            assert sha(packed) == f['sha256']
            assert sha(gzip.decompress(packed)) == f['uncompressedSha256']
        result.append({'record': name, 'archivesVerified': len(d['files']), 'result': 'PASS_HASHES'})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--server-repository', type=Path, required=True)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT.resolve()):
        parser.error('Output must be inside the client repository')
    hashes = source_check(args.source, args.server_repository)
    sessions = session_checks(args.runtime)
    for session in sessions:
        session['_ackIds'] = [r['commandId'] for r in rows(args.runtime/'sessions'/session['folder']/'trace.jsonl')
                              if r.get('kind') == 'ack']
    bindings = record_bindings(sessions)
    for session in sessions:
        session.pop('_ackIds')
    report = {'timeUtc': datetime.now(timezone.utc).isoformat(), 'requiredServerCommit': PIN,
              'method': 'Offline metadata execution plus read-only historical evidence checks',
              'metadata': metadata(args.source, hashes), 'fixtures': fixture_checks(),
              'helpers': retained_helpers(), 'sessions': sessions, 'recordBindings': bindings,
              'terminalObservation': terminal_check(args.runtime),
              'archives': archive_checks(), 'serverOrClientStarted': False,
              'historicalEvidenceModified': False, 'newMCasePass': False}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'metadataRows': len(report['metadata']['rows']), 'sourceBlobs': len(hashes),
                      'sessions': len(report['sessions']), 'fixtures': len(report['fixtures']['files']),
                      'helpers': [{k: r.get(k) for k in ('record', 'result', 'admissionGuardInExactCode',
                                                        'imageRecordedFromInspection', 'imageEqualsQualifiedBuild')} for r in report['helpers']]}))


if __name__ == '__main__':
    main()
