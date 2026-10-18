"""Read-only historical server identity audit; no server startup or export.

Verify retained source bytes against the pinned Git tree, then compare every
explicit server source map and identity field in existing JSON evidence.
Declared commit strings alone never become runtime/content attestation.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

PIN = 'ada13b011e1d3829f78e7f389e3b927795a2b3be'
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())
EVIDENCE = Path(__file__).resolve().parents[1]
KEYS = {'serverCommit', 'server_commit', 'serverBaseline', 'qualifiedServerCommit'}


def identities(value, path=''):
    if isinstance(value, dict):
        for key, item in value.items():
            here = path+'.'+key
            if key in KEYS and isinstance(item, str):
                yield here, item
            if key not in ('sourceSha256', 'sourceHashes', 'serverSourceHashes'):
                yield from identities(item, here)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from identities(item, path+'['+str(index)+']')


def source_maps(value, file_name, path=''):
    if not isinstance(value, dict):
        return
    for key, item in value.items():
        here = path+'.'+key
        if isinstance(item, dict) and (key == 'serverSourceHashes'
                or key == 'sourceHashes' and path == '.server'
                or key == 'sourceSha256' and file_name in ('local-server-build.json', 'inspected-server-sources.json')):
            yield here, item
        elif isinstance(item, dict) and key not in ('before', 'after', 'identity', 'candidate'):
            yield from source_maps(item, file_name, here)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--retained-source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.output.absolute().is_relative_to(ROOT)
    tree = subprocess.check_output(['git', '-C', str(args.repository), 'ls-tree', '-rz', PIN])
    expected, archive_bad = {}, []
    for entry in tree.split(b'\0'):
        if not entry:
            continue
        meta, name_bytes = entry.split(b'\t', 1)
        _mode, kind, oid = meta.split()
        if kind != b'blob':
            continue
        name = name_bytes.decode('utf-8')
        data = (args.retained_source/name).read_bytes()
        actual = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if actual != oid.decode():
            archive_bad.append(name)
        expected[name] = hashlib.sha256(data).hexdigest()
    assert not archive_bad, archive_bad

    records, maps, guarded = [], [], []
    code_cache = {}

    def retained_code(script, digest, execution_commit):
        key = (script, digest)
        if key not in code_cache:
            commits = [execution_commit] + subprocess.check_output(
                ['git', '-C', str(ROOT), 'log', '--format=%H', '--', script], text=True).splitlines()
            code_cache[key] = (None, b'')
            for candidate in dict.fromkeys(commits):
                response = subprocess.run(['git', '-C', str(ROOT), 'show', candidate+':'+script], capture_output=True)
                if response.returncode == 0 and hashlib.sha256(response.stdout).hexdigest() == digest:
                    code_cache[key] = (candidate, response.stdout)
                    break
        return code_cache[key]
    for file in sorted(EVIDENCE.rglob('*.json')):
        if file.parent == args.output.parent:
            continue
        raw = file.read_bytes()
        value = json.loads(raw.decode('utf-8-sig'))
        refs = list(identities(value))
        # Some runners save the PIN only after checking the real admission.
        # Verify the runner bytes at the recorded commit/hash, not today's text.
        guard_script = None
        if file.name == 'real-admission.json':
            guard_script = 'scripts/qualify_v2_real.py'
        elif file.name == 'real-audio-pipeline.json':
            guard_script = 'scripts/check_v2_real_audio.py'
        elif file.name == 'real-recovery.json':
            guard_script = 'scripts/check_v2_recovery.py'
        if guard_script and isinstance(value, dict):
            identity = value.get('identity', value.get('before', {}))
            digest = identity.get('sourceSha256', {}).get(guard_script)
            commit = identity.get('commit')
            if digest and commit:
                retained_commit, old = retained_code(guard_script, digest, commit)
                source = old.decode('utf-8')
                checked = hashlib.sha256(old).hexdigest() == digest
                checked = checked and "accepted.payload['serverCommit']" in source
                checked = checked and ('!=SERVER' in source.replace(' ', '') or '==SERVER' in source.replace(' ', ''))
                checked = checked and value.get('result') == 'PASS' and value.get('serverCommit') == PIN
                guarded.append({'record': file.relative_to(EVIDENCE).as_posix(),
                    'historicalClientCommit': commit, 'retainedCodeCommitWithExactRecordedHash': retained_commit, 'script': guard_script,
                    'scriptSha256': digest, 'result': 'CONFIRMED_BY_HASHED_ADMISSION_GUARD' if checked else 'NOT_PROVEN'})
        fixture_unknown = [p for p, v in refs if v == 'unknown' and '.wire[' in p]
        meaningful = [(p, v) for p, v in refs if p not in fixture_unknown]
        mismatches = [(p, v) for p, v in meaningful if v != PIN]
        comparisons = []
        for path, mapping in source_maps(value, file.name):
            bad = [name for name, digest in mapping.items() if expected.get(name) != digest]
            row = {'record': file.relative_to(EVIDENCE).as_posix(), 'field': path,
                   'files': len(mapping), 'mismatches': bad,
                   'result': 'MATCH' if mapping and not bad else 'MISMATCH'}
            maps.append(row)
            comparisons.append(row)
        if mismatches or any(row['result'] != 'MATCH' for row in comparisons):
            state = 'INVALID_COMMIT_OR_CONTENT_MISMATCH'
        elif comparisons:
            state = 'SERVER_CONTENT_PIN_CONFIRMED'
        elif any(path.startswith(('.network.', '.desktop.', '.schema.', '.serverDefaults.')) for path, _ in meaningful):
            state = 'SERVER_REPORTED_PIN_RECORDED'
        elif meaningful:
            state = 'DECLARED_PIN_ONLY_NO_INDIVIDUAL_ATTESTATION'
        else:
            state = 'NO_SERVER_ATTESTATION_IN_THIS_RECORD'
        records.append({'record': file.relative_to(EVIDENCE).as_posix(),
            'sha256': hashlib.sha256(raw).hexdigest(), 'identityAssessment': state,
            'serverCommitFields': [{'field': p, 'value': v} for p, v in meaningful],
            'mismatches': mismatches, 'modelFreeWireUnknownFields': len(fixture_unknown)})
    result = {'timeUtc': datetime.now(timezone.utc).isoformat(),
        'requiredServerCommit': PIN,
        'requiredSource': 'PLANUNG/ARBEITSPAKETE/AP-IV2-020.md: Referenzserver',
        'retainedArchive': {'gitTreeSha256': hashlib.sha256(tree).hexdigest(),
            'verifiedGitBlobs': len(expected), 'mismatches': archive_bad,
            'canonicalSourceMapSha256': hashlib.sha256(json.dumps(expected, sort_keys=True).encode()).hexdigest()},
        'sourceMapChecks': maps, 'historicalAdmissionGuardChecks': guarded, 'records': records,
        'counts': dict(Counter(r['identityAssessment'] for r in records)),
        'mismatchingRecords': [r['record'] for r in records if r['identityAssessment'].startswith('INVALID')],
        'policy': 'Mismatch is invalid as required-server qualification. Declaration-only and unattested individual records cannot independently qualify the server; use only explicit reviewed bindings or mark NOT_PROVEN. Client-only tests/raw captures/admin records require no server commit and are not invalidated in their own scope. Wire unknown in model-free process fixtures is not evidence of a different source commit. Historical test PASS is not automatically a current product or full hardware PASS.',
        'noServerStartedOrModified': True}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'blobs': len(expected), 'sourceMapChecks': len(maps),
                      'counts': result['counts'], 'mismatches': result['mismatchingRecords']}))


if __name__ == '__main__':
    main()
