"""Read-only validation for the sole documentation finding F01."""
import ast
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys

EV = Path(__file__).resolve().parent
ROOT = EV.parents[7]
BLOCK = ROOT/'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2'
START = 'ad1086958c0bddfc80e7d5fc31aedf5f0d512240'
REVIEWED = '33fef1d892917030100c0583566367f49fff14eb'

def git(*args):
    return subprocess.check_output(['git', '-c', 'core.quotepath=false', *args], cwd=ROOT)

def verify(pr_summary=None):
    path = 'docs/protocol-v2-results.md'
    before = git('show', START+':'+path).decode('utf-8')
    after = (ROOT/path).read_text(encoding='utf-8')
    assert before.count('ClientController.attach_v2_results') == 1
    assert after == before.replace('ClientController.attach_v2_results', 'STTController.attach_v2_results')
    tree = ast.parse((ROOT/'voice_stt_client/core/controller.py').read_text(encoding='utf-8'))
    classes = {n.name: {f.name for f in n.body if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))} for n in tree.body if isinstance(n, ast.ClassDef)}
    assert 'attach_v2_results' in classes['STTController'] and 'ClientController' not in classes
    q = json.loads((BLOCK/'30_AUSFUEHRUNG/AP-CV2-060/RUNS/R01-UMSETZUNG/EVIDENCE/windows-validation.json').read_text(encoding='utf-8'))
    blobs = {}
    for line in git('ls-files', '-s', '-z').decode().split('\0'):
        if line:
            identity, name = line.split('\t', 1)
            blobs[name] = identity.split()[1]
    assert all(blobs.get(name) == blob for name, blob in q['qualifiedGitBlobs'].items())
    assert q['result'] == 'PASS'
    log_hashes = {}
    r01 = BLOCK/'30_AUSFUEHRUNG/AP-CV2-060/RUNS/R01-UMSETZUNG/EVIDENCE'
    for check in q['checks']:
        for name, key in [(check['log'], 'sha256')] + ([(check['stderrLog'], 'stderrSha256')] if 'stderrLog' in check else []):
            sha = hashlib.sha256((r01/name).read_bytes()).hexdigest()
            assert sha == check[key], name
            log_hashes[name] = sha
    historical = [BLOCK/'30_AUSFUEHRUNG/AP-CV2-060/RUNS'/x for x in ('R01-UMSETZUNG', 'R02-ABNAHME')]
    assert not git('diff', START, '--', *[str(x.relative_to(ROOT)) for x in historical])
    changed = git('diff', '--name-only', START).decode('utf-8').splitlines()
    assert all(name == path or name.startswith('ARBEITSDATEIEN/') or name in ('docs/PROJEKTUEBERSICHT.md', 'task.md', 'ÜBERGABE.md') for name in changed), changed
    req_path = 'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/REFERENZ/TRACEABILITY/requirements.json'
    old = json.loads(git('show', START+':'+req_path))['requirements']
    new = json.loads((ROOT/req_path).read_text(encoding='utf-8'))['requirements']
    for a, b in zip(old, new):
        assert {k:v for k,v in a.items() if k != 'implementationEvidence'} == {k:v for k,v in b.items() if k != 'implementationEvidence'}
        assert a.get('implementationEvidence', {}).get('testMethods') == b.get('implementationEvidence', {}).get('testMethods')
    assert len(old) == len(new)
    validator = BLOCK/'PLANUNG/SKILLS/GEMEINSAM/scripts/pruefe_arbeitsakten.py'
    spec = importlib.util.spec_from_file_location('records', validator)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    extra = [ROOT/x for x in changed if x.endswith('.md')]
    records = mod.validate_records(BLOCK, extra, Path(pr_summary) if pr_summary else None)
    assert records['result'] == 'PASS', records
    for args in [('diff', '--check'), ('diff', '--cached', '--check'), ('diff', '--check', START)]:
        subprocess.run(['git', *args], cwd=ROOT, check=True)
    return dict(result='PASS', finding='CV2-060-R02-F01', findingAssessment='justified; corrected; independent recheck pending', startCommit=START, previouslyReviewedCommit=REVIEWED, canonicalParent=q['canonicalParent'], serverCommit=q['serverCommit'], exactSingleClassNameReplacement=True, actualPublicClassAndMethod='STTController.attach_v2_results', unchangedQualifiedProductBlobCount=len(q['qualifiedGitBlobs']), unchangedQualificationLogHashes=log_hashes, preservedR01R02Records=True, unchangedRequirementCriteriaAndTestMethods=True, records=records, diffCheck='PASS', localFullSuite='NOT_RUN: documentation only, explicitly allowed by R02', runtime=dict(python=sys.version, executable=sys.executable, platform=platform.platform()), utc=datetime.datetime.now(datetime.UTC).isoformat())

if __name__ == '__main__':
    print(json.dumps(verify(sys.argv[1] if len(sys.argv) > 1 else None), ensure_ascii=False, indent=2))
