"""Read-only staged product/log identity and administrative link verification."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

EV = Path(__file__).resolve().parent
ROOT = EV.parents[7]
os.chdir(ROOT)
manifest = json.loads((EV/'windows-validation.json').read_text(encoding='utf-8'))
assert manifest['result'] == 'PASS'
for path, blob in manifest['qualifiedGitBlobs'].items():
    actual = subprocess.check_output(['git', 'ls-files', '-s', '--', path], text=True).split()[1]
    assert actual == blob, 'Qualification blob changed: '+path
for check in manifest['checks']:
    assert check['exitCode'] == 0
    assert hashlib.sha256((EV/check['log']).read_bytes()).hexdigest() == check['sha256'], check['log']
    if check.get('stderrLog'):
        assert hashlib.sha256((EV/check['stderrLog']).read_bytes()).hexdigest() == check['stderrSha256']
assert subprocess.run(['git','diff','--check']).returncode == 0
assert subprocess.run(['git','diff','--cached','--check']).returncode == 0
script = 'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/SKILLS/GEMEINSAM/scripts/pruefe_arbeitsakten.py'
changed = subprocess.check_output(['git','diff','--name-only','--cached','-z'],text=True,encoding='utf-8').split('\0')
markdown = [path for path in changed if path.endswith('.md')]
command = [sys.executable, script, '--paths', *markdown]
if len(sys.argv) > 1:
    command.extend(['--pr-summary', sys.argv[1]])
(EV/'submission-verification.json').write_text(json.dumps(dict(result='IN_PROGRESS',
    qualificationProductBlobs=len(manifest['qualifiedGitBlobs']), qualificationLogs='hashes_match'))+'\n',encoding='utf-8')
process = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
records = json.loads(process.stdout)
assert records['result'] == 'PASS', process.stdout+process.stderr
out = dict(result='PASS', checkedAtUtc=datetime.datetime.now(datetime.UTC).isoformat(),
    qualificationProductBlobs=len(manifest['qualifiedGitBlobs']), qualificationLogs='hashes_match',
    productChangeSinceQualification=False, administrativePaths=markdown,
    recordsCommand=command, records=records)
(EV/'submission-verification.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(result='PASS', qualifiedProductBlobs=len(manifest['qualifiedGitBlobs']),
    markdownFiles=records['markdownFiles'], links=records['relativeLinks']),indent=2))
