"""Read-only product, evidence, requirement and record checks for AP060."""
import ast
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

EV = Path(__file__).resolve().parent
ROOT = EV.parents[7]
BLOCK = ROOT / 'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def verify():
    q = json.loads((EV / 'windows-validation.json').read_text(encoding='utf-8'))
    assert q['result'] == 'PASS'
    lines = git('ls-files', '-s', '-z').decode().split('\0')
    current = {line.split('\t', 1)[1]: line.split()[1] for line in lines if line}
    assert all(current.get(path) == blob for path, blob in q['qualifiedGitBlobs'].items())
    assert all(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == sha for path, sha in q['sourceHashes'].items())
    hashes = {}
    for check in q['checks']:
        for log, key in [(check['log'], 'sha256')] + ([(check['stderrLog'], 'stderrSha256')] if 'stderrLog' in check else []):
            sha = hashlib.sha256((EV/log).read_bytes()).hexdigest()
            assert sha == check[key], log
            hashes[log] = sha
    patch = (EV/q['productDiff']).read_bytes()
    assert hashlib.sha256(patch).hexdigest() == q['productDiffArtifactSha256']
    assert hashlib.sha256(base64.decodebytes(patch)).hexdigest() == q['productDiffSha256']
    reqfile = 'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/REFERENZ/TRACEABILITY/requirements.json'
    old = json.loads(git('show', q['canonicalParent']+':'+reqfile))['requirements']
    new = json.loads((ROOT/reqfile).read_text(encoding='utf-8'))['requirements']
    administrative = {'status', 'implementationEvidence', 'canonicalizationEvidence'}
    assert len(new) == len(old)
    for before, after in zip(old, new):
        assert {k:v for k,v in before.items() if k not in administrative} == {k:v for k,v in after.items() if k not in administrative}, before['id']
    count = 0
    coverage = (EV/'requirement-coverage.md').read_text(encoding='utf-8')
    for row in new:
        if row['ap'] != 'AP-CV2-060':
            continue
        count += 1
        assert row['status'] not in ('ROOT_PASS', 'ACCEPTED')
        for method in row['implementationEvidence']['testMethods']:
            module, cls, name = method.rsplit('.', 2)
            path = ROOT / (module.replace('.', '/') + '.py')
            tree = ast.parse(path.read_text(encoding='utf-8'))
            assert any(isinstance(c, ast.ClassDef) and c.name == cls and any(isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name == name for f in c.body) for c in tree.body), method
            assert method in coverage
    assert count == 13
    validator = BLOCK/'PLANUNG/SKILLS/GEMEINSAM/scripts/pruefe_arbeitsakten.py'
    spec = importlib.util.spec_from_file_location('records', validator)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    changed = git('diff', '--name-only', q['canonicalParent']).decode('utf-8').splitlines()
    # Git quotes Unicode paths unless core.quotepath is disabled for this query.
    changed = git('-c', 'core.quotepath=false', 'diff', '--name-only', q['canonicalParent']).decode('utf-8').splitlines()
    changed += ['docs/protocol-v2-results.md']
    paths = [ROOT/x for x in changed if x.endswith('.md') and (ROOT/x).is_file()]
    pr_summary = EV/'pr-summary.md'
    records = mod.validate_records(BLOCK, paths, pr_summary if pr_summary.exists() else None)
    assert records['result'] == 'PASS', records
    for args in [('diff', '--check'), ('diff', '--cached', '--check')]:
        assert subprocess.run(['git', *args], cwd=ROOT).returncode == 0
    return dict(result='PASS', canonicalParent=q['canonicalParent'], candidateBranch=q['candidateBranch'], qualifiedProductBlobCount=len(q['qualifiedGitBlobs']), matchedProductBlobs=True, matchedRuntimeSources=True, matchedLogSha256=hashes, unchangedRequirementCriteria=True, tracedRequirements=count, actualTestMethodsVerified=True, records=records, diffCheck='PASS', scope='Index qualification; final commit SHA/tree reported externally after administrative publication refs. No self-SHA.')

if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
