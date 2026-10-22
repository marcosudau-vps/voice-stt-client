"""Lock only our actual SQLite log store while real TLS/ASR dictation completes."""
import argparse,asyncio,json,os,sqlite3,time,uuid
from pathlib import Path
from unittest.mock import patch
from tests.manual.v2.suite_plan import PROFILE_RUNTIME,ROOT
from tests.manual.v2.suite_session import save
from tests.manual.v2.remote_runtime_probe import RemoteRuntime
from tests.manual.v2.verify_server_fix import read_info,check_identity


async def main(args):
    folder=PROFILE_RUNTIME/('logstore-rest-'+uuid.uuid4().hex[:12]);(folder/'tmp').mkdir(parents=True)
    os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),TEMP=str(folder/'tmp'),TMP=str(folder/'tmp'))
    from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
    from voice_stt_client.core.observability.manager import ObservabilityManager
    from voice_stt_client.core.v2_runtime import V2Runtime
    from scripts.qualify_v2_real import identity
    config=AppConfig._load_single(DEFAULT_CONFIG_PATH);config.logging.observability.enabled=True
    config.logging.observability.store_raw_payload=False
    config.logging.observability.store_transcription_content=False
    config.logging.log_dir=str(folder/'client/logs')
    manager=ObservabilityManager(config.logging.observability,log_dir=config.logging.log_dir);manager.start()
    args.output.mkdir(parents=True,exist_ok=False)
    before=await asyncio.to_thread(read_info);assert check_identity(before,args.expected_server_commit)
    report=dict(result='RUNNING',pid=os.getpid(),runtimeFolder=str(folder),identity=identity(),infoBefore=before,
        helperSha256=__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest())
    save(args.output/'result.json',report);lock=None
    def factory(*a,**kw):return V2Runtime(*a,**kw,observability=manager.ingress)
    try:
        with patch('voice_stt_client.core.v2_runtime.V2Runtime',factory):
            async with RemoteRuntime(folder,'actual-locked-logstore',args.expected_server_commit) as case:
                await case.wait(lambda:manager._db_path is not None and manager._db_path.exists())
                lock=sqlite3.connect(str(manager._db_path),timeout=5);lock.execute('BEGIN IMMEDIATE')
                began=time.monotonic();case.runtime._observe.system('qualification.logstore_locked')
                aid=await case.activate();await case.play('negative_speech',4);await case.close('finish')
                await case.wait(lambda:len(case.backend.send_input_calls)==1)
                # The first bounded write failure is DEGRADED_STORE; only
                # repeated failures cross the documented FAILED_STORE threshold.
                await case.wait(lambda:manager.health_snapshot().state.value in ('degraded_store','failed_store')
                    and manager.health_snapshot().store_errors>0,15)
                report['checks']=dict(realStoreFailureObserved=True,readyDespiteStoreFailure=case.runtime.is_ready,
                    oneBoundFinal=len(case.of_type('transcription.completed'))==1 and case.of_type('transcription.completed')[0]['activationId']==aid,
                    oneControlledPaste=len(case.backend.send_input_calls)==1,pendingEmpty=case.runtime.session.pending_count==0)
                report['lockedSeconds']=round(time.monotonic()-began,3)
                report['healthDuringFailure']=str(manager.health_snapshot().state)
                report['storeErrors']=manager.health_snapshot().store_errors
                lock.rollback();lock.close();lock=None
            report['runtimeCleanupErrors']=case.cleanup
        report['loggingWorkerJoined']=await asyncio.to_thread(manager.stop,10)
        after=await asyncio.to_thread(read_info);report.update(infoAfter=after,identityStable=before==after)
        report['result']='PASS_SCOPED' if all(report['checks'].values()) and not case.cleanup and report['loggingWorkerJoined'] and before==after else 'FAIL'
    except Exception as error:
        report.update(result='FAIL',errorType=type(error).__name__,error=str(error))
    finally:
        if lock:lock.rollback();lock.close()
        await asyncio.to_thread(manager.stop,10)
        save(args.output/'result.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('identity','infoBefore','infoAfter')}),flush=True)
    return 0 if report['result']=='PASS_SCOPED' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--expected-server-commit',required=True)
    args=p.parse_args()
    if not args.output.resolve().is_relative_to(ROOT/'build'):p.error('Output must stay in project build')
    raise SystemExit(asyncio.run(main(args)))
