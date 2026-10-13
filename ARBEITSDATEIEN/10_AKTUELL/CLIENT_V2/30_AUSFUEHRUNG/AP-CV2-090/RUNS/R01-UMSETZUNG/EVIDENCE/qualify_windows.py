"""R01 implementation qualification artifact for AP-CV2-090. Run with the client project venv."""
from pathlib import Path
import base64
import datetime
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import subprocess
import sys
import time

EV = Path(__file__).resolve().parent
ROOT = EV.parents[7]
os.chdir(ROOT)
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['PYTHONUTF8'] = '1'
patch = subprocess.check_output(['git', 'diff', '--cached', '--binary', '--unified=0', 'HEAD', '--', 'voice_stt_client', 'tests', 'scripts'])
encoded_patch = base64.encodebytes(patch)
(EV / 'tested-product.patch.base64').write_bytes(encoded_patch)
paths = [x for x in subprocess.check_output(['git', 'ls-files', '-z', '--', 'voice_stt_client', 'tests', 'scripts', '.github', 'pyproject.toml', 'requirements.txt', 'requirements-dev.txt', 'config.yaml', 'VERSION'], text=True).split('\0') if x]
blobs = {}
for line in subprocess.check_output(['git', 'ls-files', '-s', '-z', '--', *paths], text=True).split('\0'):
    if line:
        identity, path = line.split('\t', 1)
        blobs[path] = identity.split()[1]
data = dict(testedBase=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            candidateBranch='work/client-v2/ap-cv2-090', canonicalParent='1bc5be893060e0d6a80e1d890102bfffebb73a17',
            serverCommit='ada13b011e1d3829f78e7f389e3b927795a2b3be', productDiff='tested-product.patch.base64', productDiffEncoding='base64',
            productDiffArtifactSha256=hashlib.sha256(encoded_patch).hexdigest(),
            productDiffSha256=hashlib.sha256(patch).hexdigest(),
            sourceHashes={x:hashlib.sha256(Path(x).read_bytes()).hexdigest() for x in paths},qualifiedGitBlobs=blobs,
            runtime=dict(python=sys.version, executable=sys.executable, platform=platform.platform(),cwd=str(ROOT),qt='offscreen',dependencies={x:importlib.metadata.version(x) for x in ['PySide6','websockets','fastapi','uvicorn','halo']}),
            startedAtUtc=datetime.datetime.now(datetime.UTC).isoformat(),checks=[],
            lineEndingNote='Runtime hashes cover local bytes; Git blobs/exact staged product diff identify normalized published content. All qualification logs are UTF-8 LF before SHA256 and versioning.')
checks = [
    (['-W','error','-m','unittest','tests.test_v2_feedback','tests.test_feedback_reducer','tests.test_event_normalizer','tests.test_feedback_mapping','tests.test_feedback_ui','tests.test_led_feedback','tests.test_obs050_ui','tests.test_obs040_client_hooks','tests.test_obs010_models','tests.test_obs010_normalizer_client','tests.test_obs010_normalizer_server','tests.test_obs030_sqlite_store','tests.test_obs050_local_provider','-v'], 'targeted-unittest.txt', 180),
    (['scripts/check_v2_server_feedback.py','--server-root','C:/Users/marco/AppData/Local/Temp/voice-stt-ap-cv2-020-ada13b0','--server-repository','P:/GithubRepos/marcosudau-vps/voice-stt-server/main'], 'server-feedback-checkpoint.json', 90),
    (['-m','compileall','-q','voice_stt_client','scripts','tests'], 'compileall.txt', 60),
    (['-m','unittest','discover','-s','tests','-p','test_*.py','-v'], 'windows-full-unittest.txt', 900),
]
for args, name, timeout in checks:
    command = [sys.executable, *args]
    start = time.monotonic()
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', timeout=timeout)
    except subprocess.TimeoutExpired as error:
        # Retain diagnostic output even when a qualification attempt times out.
        def decode(value):
            return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else (value or '')
        result = subprocess.CompletedProcess(command, -9, decode(error.stdout), decode(error.stderr))
    text = result.stdout.replace('\r\n','\n')
    stderr = result.stderr.replace('\r\n','\n')
    if name.endswith('.json'):
        (EV/(name+'.stderr.txt')).write_text(stderr,encoding='utf-8',newline='\n')
    else:
        text += stderr
        text = '\n'.join(line.rstrip(' \t') for line in text.split('\n'))
    (EV/name).write_text(text,encoding='utf-8',newline='\n')
    check = dict(command=command,exitCode=result.returncode,elapsedSeconds=round(time.monotonic()-start,3),log=name,sha256=hashlib.sha256((EV/name).read_bytes()).hexdigest(),result='PASS' if result.returncode==0 else 'FAIL')
    count=re.search(r'Ran (\d+) tests in ([\d.]+)s',text)
    if count: check.update(testCount=int(count[1]),testSeconds=float(count[2]))
    if name == 'server-feedback-checkpoint.json' and result.returncode==0:
        check['stderrLog']=name+'.stderr.txt'; check['stderrSha256']=hashlib.sha256((EV/check['stderrLog']).read_bytes()).hexdigest()
        server=json.loads(text); check.update(serverCheckCount=server['checkCount'],verifiedSourceCount=len(server.get('sourceHashes',{})))
    if name == 'server-contracts.json' and result.returncode == 0:
        server=json.loads(text); check.update(testCount=server['testCount'], skipped=server['skipped'], verifiedSourceCount=len(server['sourceHashes']), stderrLog=name+'.stderr.txt', stderrSha256=hashlib.sha256((EV/(name+'.stderr.txt')).read_bytes()).hexdigest())
    data['checks'].append(check)
    (EV/'windows-validation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(name,check['result'],check.get('testCount',check.get('serverCheckCount','')),flush=True)
    if result.returncode: raise SystemExit(result.returncode)
assert all(hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha for path,sha in data['sourceHashes'].items()), 'Source changed during qualification'
assert subprocess.run(['git','diff','--check']).returncode == 0
assert subprocess.run(['git','diff','--cached','--check']).returncode == 0

data['diffCheckResult']='PASS'
data['finishedAtUtc']=datetime.datetime.now(datetime.UTC).isoformat()
data['result']='PASS'
(EV/'windows-validation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
