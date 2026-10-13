"""Read-only AP090 candidate, log, requirement and record verification."""
from pathlib import Path
import base64
import hashlib
import importlib.util
import json
import subprocess

E = Path(__file__).resolve().parent
ROOT = E.parents[7]
B = ROOT / 'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2'
spec = importlib.util.spec_from_file_location('records', B / 'PLANUNG/SKILLS/GEMEINSAM/scripts/pruefe_arbeitsakten.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
changed = subprocess.check_output(['git','diff','--name-only','1bc5be893060e0d6a80e1d890102bfffebb73a17','-z'],cwd=ROOT,text=True,encoding='utf-8').split('\0')
extra = [ROOT/x for x in changed if x.endswith('.md')]
extra += [ROOT/'docs/protocol-v2-feedback.md']
records = module.validate_records(B, extra)
assert records['result'] == 'PASS', records
w = json.loads((E/'windows-validation.json').read_text(encoding='utf-8'))
assert w['result'] == 'PASS'
for path, sha in w['sourceHashes'].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == sha, path
for path, blob in w['qualifiedGitBlobs'].items():
    current = subprocess.check_output(['git','rev-parse',':'+path],cwd=ROOT,text=True).strip()
    assert current == blob, path
for item in w['checks']:
    assert item['exitCode'] == 0, item
    assert hashlib.sha256((E/item['log']).read_bytes()).hexdigest() == item['sha256'], item['log']
    if item.get('stderrLog'):
        assert hashlib.sha256((E/item['stderrLog']).read_bytes()).hexdigest() == item['stderrSha256']
encoded = (E/w['productDiff']).read_bytes()
assert hashlib.sha256(encoded).hexdigest() == w['productDiffArtifactSha256']
assert hashlib.sha256(base64.decodebytes(encoded)).hexdigest() == w['productDiffSha256']
reqs = json.loads((B/'PLANUNG/REFERENZ/TRACEABILITY/requirements.json').read_text(encoding='utf-8'))
clientlog = (E/'targeted-unittest.txt').read_text(encoding='utf-8')
checkpoint = json.loads((E/'server-feedback-checkpoint.json').read_text(encoding='utf-8'))
count = 0
for item in reqs['requirements']:
    if item['ap'] != 'AP-CV2-090':
        continue
    ev = item['implementationEvidence']
    for method in ev['testMethods']:
        owner, name = method.rsplit('.',1)
        assert name+' ('+owner+'.'+name+') ... ok' in clientlog, method
    for case in ev['checkpointCases']:
        assert case in checkpoint['checks'], case
    assert ev['testMethods'] and ev['checkpointCases'], item['id']
    assert item['status'] == 'CLIENT OPEN'
    count += 1
assert count == 9
for args in (['git','diff','--check'], ['git','diff','--cached','--check']):
    assert subprocess.run(args,cwd=ROOT).returncode == 0
print(json.dumps(dict(result='PASS',canonicalParent=w['canonicalParent'],candidateBranch=w['candidateBranch'],
    serverCommit=w['serverCommit'],qualifiedBlobCount=len(w['qualifiedGitBlobs']),
    sourceAndLogHashesMatch=True,productAndTestsUnchangedSinceQualification=True,
    requirementCount=count,records=records,diffCheck='PASS'),indent=2))
