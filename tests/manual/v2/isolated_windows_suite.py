"""Full discovery, every discovered Windows test, isolated module workers.

Avoid Qt application/decoder state leaking between test modules. No skips,
selection reduction or product patches; exact discovered test-ID set checked.
"""
import argparse,concurrent.futures,hashlib,json,os,re,subprocess,sys,threading,time,unittest,uuid
from pathlib import Path
from tests.manual.v2.suite_plan import ROOT,PROFILE_RUNTIME
from tests.manual.v2.suite_session import save


def flatten(suite):
    for entry in suite:
        if isinstance(entry,unittest.TestSuite):yield from flatten(entry)
        else:yield entry


def observed_ids(data):
    # Verbose unittest puts docstrings on a NEW line before the status.
    return set(re.findall(r'^(?:test_\w+|runTest) \(([^\n)]+)\)',data,re.M))


def main(args):
    args.output.mkdir(parents=True,exist_ok=False)
    folder=PROFILE_RUNTIME/('isolated-suite-'+uuid.uuid4().hex[:12]);folder.mkdir()
    discovered=list(flatten(unittest.defaultTestLoader.discover(str(ROOT/'tests'))))
    expected={case.id() for case in discovered};modules={}
    for case in discovered:modules.setdefault(type(case).__module__,set()).add(case.id())
    names={name.rsplit('.',1)[-1]+'.py' for name in modules}
    assert len(names)==len(modules),'Nonunique module filename: require explicit worker targets'
    lock=threading.Lock();qt_lock=threading.Lock();report=dict(result='RUNNING',pid=os.getpid(),runtimeFolder=str(folder),
        expectedCount=len(expected),expectedTestIds=sorted(expected),rows=[],method=__doc__)
    save(args.output/'result.json',report)
    def run(module):
        filename=module.rsplit('.',1)[-1]+'.py';worker=folder/module;worker.mkdir()
        env=dict(os.environ,TEMP=str(worker),TMP=str(worker),VOICESTT_CLIENT_HOME=str(worker/'client'),QT_QPA_PLATFORM='offscreen')
        command=[sys.executable,'-X','faulthandler','-m','unittest','discover','-v','-s','tests','-p',filename]
        log=args.output/(module+'.log');begin=time.monotonic()
        source=next((ROOT/'tests').rglob(filename)).read_text(encoding='utf8')
        native_qt='PySide6' in source or 'QApplication' in source or 'release_probe' in source
        def execute():
            with log.open('w',encoding='utf8') as stream:
                return subprocess.run(command,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=180).returncode
        try:
            if native_qt:
                with qt_lock:code=execute()
            else:code=execute()
        except subprocess.TimeoutExpired:code='WORKER_TIMEOUT'
        data=log.read_text(encoding='utf8',errors='replace')
        observed=observed_ids(data)
        row=dict(module=module,exitCode=code,seconds=round(time.monotonic()-begin,3),
            tests=len(observed),expected=len(modules[module]),skips=len(re.findall(r'\.\.\. skipped ',data)),
            exactIds=observed==modules[module],logSha256=hashlib.sha256(log.read_bytes()).hexdigest(),command=command)
        row['result']='PASS' if code==0 and row['exactIds'] and not row['skips'] else 'FAIL'
        with lock:
            report['rows'].append(row);save(args.output/'result.json',report);print(module+' '+row['result'],flush=True)
        return observed
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:observed=set().union(*pool.map(run,modules))
    report.update(observedCount=len(observed),exactDiscoveredSet=observed==expected,
        result='PASS' if observed==expected and all(r['result']=='PASS' for r in report['rows']) else 'FAIL')
    save(args.output/'result.json',report)
    print(json.dumps(dict(result=report['result'],tests=len(observed),modules=len(modules))),flush=True)
    return 0 if report['result']=='PASS' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if not a.output.resolve().is_relative_to(ROOT/'build'):p.error('Project build output required')
    raise SystemExit(main(a))
