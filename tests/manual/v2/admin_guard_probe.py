"""Actual positive Admin guard, key read only from explicitly supplied env file.

No key in argv, output, config, vault writes or HTTP debug logs. Never changes a
server default. Runtime/model bootstrap and generation invalidation stay real.
"""
import argparse,asyncio,json,os,uuid
from pathlib import Path
from tests.manual.v2.suite_plan import ROOT,PROFILE_RUNTIME
from tests.manual.v2.suite_session import save
from tests.manual.v2.remote_runtime_probe import RemoteRuntime
from tests.manual.v2.verify_server_fix import read_info,check_identity


def read_key(path):
    from dotenv import dotenv_values
    key=dotenv_values(path,interpolate=False).get('VOICESTT_ADMIN_API_KEY')
    if not isinstance(key,str) or not key or '\n' in key or '\r' in key:
        raise ValueError('Requested Admin variable missing or invalid')
    return key


async def main(args):
    folder=PROFILE_RUNTIME/('admin-final-'+uuid.uuid4().hex[:12]);(folder/'tmp').mkdir(parents=True)
    os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),TEMP=str(folder/'tmp'),TMP=str(folder/'tmp'))
    args.output.mkdir(parents=True,exist_ok=False)
    key=read_key(args.secret_file)
    before=await asyncio.to_thread(read_info);assert check_identity(before,args.expected_server_commit)
    report=dict(result='RUNNING',pid=os.getpid(),runtimeFolder=str(folder),infoBefore=before,
        credentialSource='Explicit user file / VOICESTT_ADMIN_API_KEY; memory only',remember=False)
    save(args.output/'result.json',report)
    try:
        async with RemoteRuntime(folder,'actual-admin-guard',args.expected_server_commit) as case:
            ui=case.runtime.settings_ui_session();await ui.load()
            vault_before=await asyncio.to_thread(ui.store.read,ui.origin)
            defaults_before=await case.runtime.settings.http.request('GET','/api/v2/settings/server')
            view=await ui.verify(key,remember=False)
            verified=view.admin_verified
            previous=case.runtime.session.binding
            assert (await case.runtime.reconnect_server()).success
            await case.wait(lambda:case.runtime.is_ready and case.runtime.session.binding is not previous)
            await case.ready()
            invalidated=not ui.view().admin_verified
            await ui.load();again=await ui.verify(key,remember=False)
            defaults_after=await case.runtime.settings.http.request('GET','/api/v2/settings/server')
            report['checks']=dict(positiveGuardVerified=verified,oldGenerationInvalidated=invalidated,
                freshGenerationVerified=again.admin_verified,
                defaultsUnchanged=defaults_before.status==defaults_after.status==200 and defaults_before.body==defaults_after.body,
                vaultUnchanged=(await asyncio.to_thread(ui.store.read,ui.origin))==vault_before)
            ui.invalidate();report['checks']['inMemoryKeyInvalidated']=ui._key is None
            report['hello']=case.hello
        report['runtimeCleanupErrors']=case.cleanup
        # Scan only our own generated files, never the credential source.
        report['checks']['noSecretInOwnFiles']=not any(key.encode() in p.read_bytes() for p in folder.rglob('*') if p.is_file())
        after=await asyncio.to_thread(read_info);report.update(infoAfter=after,identityStable=before==after)
        report['result']='PASS_SCOPED' if all(report['checks'].values()) and not case.cleanup and before==after else 'FAIL'
    except Exception as error:
        # Do not stringify arbitrary exception/request objects carrying headers.
        report.update(result='FAIL',errorType=type(error).__name__)
    finally:
        key=None;save(args.output/'result.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('infoBefore','infoAfter')}),flush=True)
    return 0 if report['result']=='PASS_SCOPED' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--secret-file',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--expected-server-commit',required=True);a=p.parse_args()
    if not a.output.resolve().is_relative_to(ROOT/'build'):p.error('Project build output required')
    raise SystemExit(asyncio.run(main(a)))
