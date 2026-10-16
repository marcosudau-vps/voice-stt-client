"""Verify existing candidate-bound UX02 evidence; never execute a product test.

Run with the project venv from the repository root. Historical failed/red
attempts are preserved and deliberately excluded from the successful final set.
"""
from datetime import UTC, datetime
import gzip
import hashlib
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())
HERE = Path(__file__).resolve().parent
PRODUCT = 'd95043e96051d4022b297099391a4fdff0dcc12b'
SERVER = 'ada13b011e1d3829f78e7f389e3b927795a2b3be'


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    pair = read(HERE/'pair/validation.json')
    assert pair['result'] == 'PASS' and pair['clientProductCommit'] == PRODUCT
    assert pair['candidateCommit'] == PRODUCT and pair['serverCommit'] == SERVER
    checks = []
    for item in pair['commands']:
        packed = (HERE/'pair'/item['log']).read_bytes()
        assert item['exitCode'] == 0
        assert hashlib.sha256(packed).hexdigest() == item['compressedSha256']
        assert hashlib.sha256(gzip.decompress(packed)).hexdigest() == item['sha256']
        checks.append(dict(name=item['name'], result='PASS', evidence='pair/validation.json',
                           tests=item['testCount'], skipped=item['skipped']))
    expected = {'client-full': (1390, 0), 'cross-process': (11, 0),
                'scenario-boundaries': (17, 0), 'server-full': (1964, 14)}
    for item in checks:
        if item['name'] in expected:
            assert (item['tests'], item['skipped']) == expected[item['name']]
    assert len(pair['serverSourceHashes']) == 555
    import sys
    sys.path.insert(0, str(ROOT))
    from scripts.qualify_v2_real import identity
    current = identity()['sourceSha256']
    names = ['targeted-green-final', 'original-composed-green', 'real-recovery',
             'native-desktop-restart', 'windows-hotkeys', 'windows-settings',
             'twine', 'frozen-native-real-server', 'wheel-install', 'wheel-runtime',
             'native-verdict-final', 'native-labels-final', 'native-helpers-compile',
             'real-model-replay']
    for name in names:
        item = read(HERE/(name+'.json'))
        assert item['result'] == 'PASS' and item['exitCode'] == 0, name
        # Old targeted checks preceded the product commit; the final sources
        # and all integration/build/runtime checks are exactly product-bound.
        if name not in ('targeted-green-final', 'original-composed-green'):
            for phase in ('before', 'after'):
                assert item[phase]['commit'] == PRODUCT, (name, phase)
                assert item[phase]['sourceSha256'] == current, (name, phase)
        packed = (HERE/item['log']).read_bytes()
        assert hashlib.sha256(packed).hexdigest() == item['gzipSha256'], name
        assert hashlib.sha256(gzip.decompress(packed)).hexdigest() == item['sha256'], name
        checks.append(dict(name=name, result='PASS', evidence=name+'.json',
                           seconds=item['durationSeconds']))
    artifacts = read(HERE/'build/artifacts.json')
    assert artifacts['result'] == 'PASS' and artifacts['productCommit'] == PRODUCT
    dist = ROOT/'dist-feedback-rc-iv2-020-ux02'
    for item in artifacts['files']:
        path = dist/item['file']
        assert path.stat().st_size == item['size'] and digest(path) == item['sha256']
    for name in ('frozen-native-runtime', 'wheel-native-runtime'):
        item = read(HERE/(name+'.json'))
        assert item['result'] == 'PASS'
        assert item['buildIdentity']['clientCommit'] == PRODUCT
        assert item['buildIdentity']['sourceCommit'] == PRODUCT
        assert item['buildIdentity']['sourceDirty'] is False
        assert item['network']['result'] == 'PASS' and item['network']['serverCommit'] == SERVER
        assert item['desktop']['result'] == 'PASS' and item['desktop']['coreStopped'] is True
    assert read(HERE/'config-roundtrip.json')['result'] == 'PASS'
    recovery = read(HERE/'real-recovery-summary.json')
    assert recovery['result'] == 'PASS' and len(recovery['restarts']) == 3
    result = dict(status='TECHNICAL_REQUALIFICATION_PASS_NATIVE_CONFIRMATION_PENDING',
        timeUtc=datetime.now(UTC).isoformat(), productCommit=PRODUCT,
        productTree=pair['candidateTree'], canonicalParent='b80ed8b81ad92bd02ac32553883443d2b7673bcd',
        serverCommit=SERVER, sourceManifestSha256=hashlib.sha256(
            json.dumps(current, sort_keys=True).encode()).hexdigest(),
        builds=artifacts['files'], checks=checks, serverVerifiedBlobs=555,
        restartRecoverySeconds=[r['recoverySeconds'] for r in recovery['restarts']],
        recoveryShutdownSeconds=recovery['shutdownSeconds'],
        physicalModifierTest='NOT_RUN', completeRealCases='NOT_PROVEN',
        boundaries=['Technical regression/build/runtime checks PASS; UX02 remains open until physical held-key/release proof.',
                    'Frozen/Wheel probes deliberately use unavailable capture, not live speech; separate native desktop probe uses actual ReSpeaker.',
                    'Model replay is real human fixtures and real local models, not live capture or native paste.',
                    'Previous product172 live results stay historical; no transfer of complete M-case qualification.',
                    'M-01..M-12, subjective calibration and 30min/100 real activations remain open.',
                    'Recovery detail filename collision is documented in real-recovery-summary.json; high-resolution resource samples not claimed from it.'],
        release='NOT_PUBLISHED', reviewReady=False)
    native = HERE/'native-physical-20261016-01'
    if (native/'assessment.json').exists():
        assessment = read(native/'assessment.json')
        attempt = read(native/'attempt-001.json')
        decision = read(native/'human-decision-chat.json')
        cleanup = read(native/'finalization.json')
        assert assessment['result'] == attempt['result'] == cleanup['result'] == 'PASS'
        assert assessment['productCommit'] == PRODUCT
        assert attempt['identity']['sourceSha256'] == current
        assert attempt['physicalModifierObservedByProductWorker'] and attempt['workerStopped']
        assert attempt['actualSha256'] == attempt['expectedSha256']
        assert attempt['authoritativeTextPreserved'] and decision['decision'] == 'accept'
        assert cleanup['hotkeyReservationReleasedAndReregistered']
        assert attempt['helperSha256'] == digest(HERE.parent/'human/native_modifier_trial.py')
        assert attempt['editorAdapterSha256'] == digest(HERE.parent/'human/native_modifier_editor.py')
        result.update(status='TECHNICAL_REQUALIFICATION_AND_UX02_NATIVE_PASS_REAL_GATES_OPEN',
            physicalModifierTest='PASS', nativeEvidence='native-physical-20261016-01/assessment.json',
            findingUX02='CLOSED', humanConfirmation='native-physical-20261016-01/human-decision-chat.json')
        result['boundaries'][0] = 'Technical checks and actual physical UX02 native confirmation PASS. This closes UX02 only; complete M-cases remain open.'
    (HERE/'qualification-summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print('PASS: final technical evidence, full logs, source identities, binary hashes and server pair verified;', result['physicalModifierTest'], 'physical confirmation; full real gates open')


if __name__ == '__main__':
    main()
