"""AP-IV2-010 fixed-pair qualification from the client project venv.

Requires an exact Git-blob export of the pinned server and its venv. The server
does not have to be promoted or merged. All subprocesses have hard deadlines;
complete logs and commands are stored alongside the report, including failures.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SERVER = 'ada13b011e1d3829f78e7f389e3b927795a2b3be'
CLIENT = '43759d345b2b88354e4f3b383a4833731621d1e3'


def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()


def run(args):
    args.evidence.mkdir(parents=True,exist_ok=True)
    env = dict(os.environ,PYTHONUTF8='1',QT_QPA_PLATFORM='offscreen',
               OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    env.pop('IV2_PROCESS_GATE',None)
    py = str(ROOT/'venv/Scripts/python.exe')
    entries=[]
    report=dict(clientProductCommit=CLIENT,serverCommit=SERVER,
        candidateCommit=git('rev-parse','HEAD'),candidateTree=git('rev-parse','HEAD^{tree}'),
        diff=git('diff','--binary',CLIENT), runtime=dict(python=sys.version,
        executable=sys.executable,platform=platform.platform()),commands=entries)
    def command(name,command,*,cwd=ROOT,custom_env=env,timeout=900):
        path=args.evidence/(name+'.txt')
        start=time.monotonic()
        with path.open('wb') as log:
            log.write((json.dumps(dict(command=command,cwd=str(cwd)))+'\n').encode())
            log.flush()
            try:
                result=subprocess.run(command,cwd=cwd,env=custom_env,
                    stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
                code=result.returncode
            except subprocess.TimeoutExpired:
                code=124
        raw=path.read_bytes(); text=raw.decode('utf8',errors='replace')
        packed=gzip.compress(raw,mtime=0)
        compressed=path.with_suffix('.txt.gz'); compressed.write_bytes(packed)
        path.unlink()
        count=re.search(r'Ran (\d+) tests',text)
        entry=dict(name=name,command=command,cwd=str(cwd),exitCode=code,
            durationSeconds=round(time.monotonic()-start,3),log=compressed.name,
            sha256=hashlib.sha256(raw).hexdigest(),compressedSha256=hashlib.sha256(packed).hexdigest(),
            testCount=int(count[1]) if count else None)
        entries.append(entry)
        report['result']='IN_PROGRESS'
        (args.evidence/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        print(name,code,flush=True)
        return code

    # Verify every server blob; archive/checkouts can apply EOL conversions.
    tracked=subprocess.check_output(['git','-C',str(args.server_repository),'ls-tree','-rz',SERVER]).split(b'\0')
    hashes={}
    for entry in tracked:
        if not entry: continue
        meta,name=entry.split(b'\t',1); mode,kind,oid=meta.split()
        if kind!=b'blob': continue
        name=name.decode('utf8')
        path=args.server_root/name
        actual=path.read_bytes()
        actual_oid=subprocess.check_output(['git','hash-object','--stdin'],input=actual).strip()
        if actual_oid!=oid: raise AssertionError('Changed server blob: '+name)
        hashes[name]=hashlib.sha256(actual).hexdigest()
    report['serverSourceHashes']=hashes
    # No product changes in this gate, staged or unstaged.
    for scope in ('voice_stt_client','requirements.txt','requirements-dev.txt','setup.py','VERSION'):
        if git('diff',CLIENT,'--',scope): raise AssertionError('Product changed in gate: '+scope)
    vector=ROOT/'tests/contracts/protocol-v2-vectors.json'
    if vector.read_bytes()!=(args.server_root/'tests/contracts/protocol-v2-vectors.json').read_bytes():
        raise AssertionError('Cross-repository vectors differ')
    report['vectorSha256']=hashlib.sha256(vector.read_bytes()).hexdigest()
    command('client-full',[py,'-m','unittest','discover','-v','-s','tests','-p','test_*.py'])
    process_env=dict(env,IV2_PROCESS_GATE='1',IV2_SERVER_ROOT=str(args.server_root),
        IV2_SERVER_REPOSITORY=str(args.server_repository),IV2_EVIDENCE=str(args.evidence))
    command('cross-process',[py,'-m','unittest','-v','tests.test_v2_cross_repository'],custom_env=process_env,timeout=240)
    # Explicitly execute every complementary deterministic scenario binding.
    sys.path.insert(0,str(ROOT))
    from tests.test_v2_cross_repository import SCENARIOS
    bindings=sorted({name for names in SCENARIOS.values() for name in names if not name.startswith('ProcessCases.')})
    command('scenario-boundaries',[py,'-m','unittest','-v',*bindings],timeout=180)
    for smoke in ('transport','audio','controls','results','settings','feedback','runtime'):
        command('server-'+smoke,[py,'scripts/check_v2_server_'+smoke+'.py',
            '--server-root',str(args.server_root),'--server-repository',str(args.server_repository)],timeout=180)
    serverpy=str(args.server_root/'venv/Scripts/python.exe')
    command('server-full',[serverpy,'-m','pytest','-v','tests/unit','-ra'],cwd=args.server_root,timeout=900)
    command('compileall',[py,'-m','compileall','-q','voice_stt_client','scripts','tests'])
    command('diff-check',['git','-c','core.safecrlf=false','diff','--check'])
    command('client-environment',[py,'-m','pip','freeze'])
    command('server-environment',[serverpy,'-m','pip','freeze'],cwd=args.server_root)
    report['scenarios']={key:dict(bindings=value,result='PASS' if all(e['exitCode']==0 for e in entries) else 'SEE_FAILURES')
                         for key,value in SCENARIOS.items()}
    report['realCases']=dict(SC_29='NOT_RUN/AP-IV2-020',SC_30='NOT_RUN/AP-IV2-020')
    report['result']='PASS' if all(e['exitCode']==0 for e in entries) else 'FAIL'
    (args.evidence/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    return 0 if report['result']=='PASS' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('server-root','server-repository','evidence'):
        parser.add_argument('--'+name,required=True,type=Path)
    args=parser.parse_args()
    args.server_root=args.server_root.resolve(); args.server_repository=args.server_repository.resolve()
    args.evidence=args.evidence.resolve()
    raise SystemExit(run(args))
