"""Read-only inventory/hash audit of the explicitly authorized test namespace.

Never deletes, moves or rewrites a runtime/archive; cannot bypass approval.
Output is safe metadata in project build. Active run names must be explicit.
"""
import argparse
from datetime import UTC,datetime
import hashlib
import json
import re
from pathlib import Path
from tests.manual.v2.suite_plan import ROOT,PROFILE_RUNTIME
from tests.manual.v2.suite_session import save


def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def inspect_folder(source,archive):
    manifest=archive/'archive-manifest.json'
    result=dict(name=source.name,archiveExists=archive.is_dir(),manifestExists=manifest.is_file())
    if not manifest.is_file():return dict(result,result='ARCHIVE_NOT_PROVEN')
    raw=json.loads(manifest.read_text(encoding='utf-8-sig'))
    files=raw.get('files',raw)
    if isinstance(files,list):
        mapped={v['path']:v['sha256'] for v in files if isinstance(v,dict) and 'path' in v and 'sha256' in v}
        if len(mapped)!=len(files):return dict(result,result='UNSUPPORTED_MANIFEST')
        files=mapped
    if not isinstance(files,dict):return dict(result,result='UNSUPPORTED_MANIFEST')
    issues=[];byte_count=0
    for name,expected in files.items():
        # Historical direct hash maps and current bound manifests are supported.
        if not isinstance(expected,str) or not re.fullmatch('[a-f0-9]{64}',expected):
            raise ValueError('Malformed archive hash')
        s=(source/name).resolve();a=(archive/name).resolve()
        if not s.is_relative_to(source.resolve()) or not a.is_relative_to(archive.resolve()):
            raise ValueError('Archive manifest path escapes bound roots')
        if not s.is_file() or not a.is_file():issues.append(dict(file=name,reason='missing'));continue
        byte_count+=s.stat().st_size
        if digest(s)!=expected or digest(a)!=expected:issues.append(dict(file=name,reason='hash_mismatch'))
    actual={p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
    named={str(Path(n).as_posix()) for n in files}
    unindexed=sorted(actual-named)
    return dict(result,result='ARCHIVED_HASH_VERIFIED' if not issues and not unindexed else 'ARCHIVE_NEEDS_RECONCILIATION',
        indexedFiles=len(named),bytes=byte_count,issues=issues,unindexed=unindexed)


def main(args):
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'build').resolve()):raise ValueError('Audit output must stay in project build')
    rows=[]
    for source in sorted(PROFILE_RUNTIME.iterdir()):
        if not source.is_dir():continue
        if source.name in args.active:
            rows.append(dict(name=source.name,result='ACTIVE_EXCLUDED_FROM_CLEANUP'));continue
        rows.append(inspect_folder(source,ROOT/'build/ap-iv2-020-suite/private-archive'/source.name))
    report=dict(timeUtc=datetime.now(UTC).isoformat(),authorizedRoot=str(PROFILE_RUNTIME),readOnly=True,
        previousDeletionFailure=dict(layer='Automatic tool approval review, before OS command execution',reason='blocked by policy',
            exactRule='NOT_EXPOSED',originalRejectedCommandExecuted=False,
            saferRemoval='Remove-VerifiedRuntime.ps1: approved hash-verified individual nonrecursive removal; receipts separate'),
        folders=rows,stoppedFolders=sum(r['result']!='ACTIVE_EXCLUDED_FROM_CLEANUP' for r in rows))
    save(out,report)
    print(json.dumps(dict(stopped=report['stoppedFolders'],verified=sum(r['result']=='ARCHIVED_HASH_VERIFIED' for r in rows),
        unresolved=[r['name'] for r in rows if r['result']=='ARCHIVE_NEEDS_RECONCILIATION']),ensure_ascii=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--active',nargs='*',default=[]);main(p.parse_args())
