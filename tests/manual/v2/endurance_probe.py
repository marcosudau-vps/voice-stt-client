"""30min/100 automated activations through the production runtime and real ASR.

Only PortAudio input and the OS clipboard boundary are controlled. Authorized
human WAVs enter actual AudioCapture, media queue, TLS, selected real models,
Controls, mirror, Results, History, injection queue and log coordinator.
No live microphone, foreground paste, sound/LED, server lifecycle or global PATCH.
"""
import argparse
import asyncio
from collections import Counter,deque
from datetime import UTC,datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from unittest.mock import patch

from tests.manual.v2.suite_plan import ROOT,PROFILE_RUNTIME,TARGET,select_tasks,both_tasks
from tests.manual.v2.suite_session import save,prepare_profile
from tests.manual.v2.verify_server_fix import fixture,read_info,check_identity,observed_event
from tests.manual.v2.endurance_assessment import same_build


def schedule(count=100,seconds=1800):
    if type(count) is not int or count<100 or seconds<1800 or seconds/count<16:
        raise ValueError('Qualification needs >=100 slots, >=1800s and >=16s/slot')
    return [dict(index=i+1,atSeconds=i*seconds/count,kind=('manual','alexa','hey_jarvis')[i%3]) for i in range(count)]


def new_activation_starts(events,known_ids):
    # Rounded diagnostic timestamps are not ordering fences. An immediate
    # event-before-Ack can round below the exact local trigger timestamp.
    return [e for e in events if e['type']=='activation.started' and e['activationId'] not in known_ids]


class ReplayStream:
    latest=None
    def __init__(self,**kwargs):
        self.callback=kwargs['callback'];self.active=False;ReplayStream.latest=self
    def start(self):self.active=True
    def stop(self):self.active=False
    def close(self):self.active=False


def devices(*args,**kwargs):
    d=dict(name='Authorized real WAV replay at PortAudio boundary',default_samplerate=16000,max_input_channels=1)
    return d if args or kwargs else [d]


async def run(args):
    plan=schedule(args.count,args.seconds)
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'build').resolve()):raise ValueError('Output must be in project build')
    out.mkdir(parents=True,exist_ok=False)
    local=PROFILE_RUNTIME/('endurance-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    local.mkdir(parents=True,exist_ok=False)
    os.environ['VOICESTT_CLIENT_HOME']=str(local/'client')
    os.environ['VOICESTT_CLIENT_CONFIG']=str(local/'profile.yaml')
    os.environ['TEMP']=os.environ['TMP']=str(local/'tmp');(local/'tmp').mkdir()
    import numpy as np
    from voice_stt_client.core.v2_runtime import V2Runtime
    from voice_stt_client.core.v2_transport import V2TransportConfig
    from voice_stt_client.core.settings_service import SettingsHTTP
    from scripts.qualify_v2_session import process_memory
    from scripts.qualify_v2_real import identity
    from tests.test_text_injector import MockInjectionBackend
    config=prepare_profile(local,TARGET,both_tasks(select_tasks(['finish']))[0],0)
    config.audio.sample_rate=16000;config.audio.channels=1;config.audio.chunk_duration_ms=40
    # These are observable test boundaries, never native clipboard success.
    backend=MockInjectionBackend()
    before=await asyncio.to_thread(read_info)
    if not check_identity(before,args.expected_server_commit):raise ValueError('Unexpected server identity')
    report=dict(result='RUNNING',startedAtUtc=datetime.now(UTC).isoformat(),pid=os.getpid(),runtimeFolder=str(local),
        identity=identity(),helperSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),infoBefore=before,
        plannedSeconds=args.seconds,plannedActivations=args.count,rows=[],
        method=__doc__,hardwareUsbRecovery='NOT_RUN',frozenNativeUiClipboard='NOT_RUN',fullM12='NOT_PROVEN')
    save(out/'result.json',report)
    print(json.dumps(dict(state='STARTING',output=str(out),runtime=str(local),pid=os.getpid())),flush=True)
    chunks=deque();stopping=False;events=deque(maxlen=2000);finals=deque(maxlen=200);stage='bootstrap'
    counts=Counter();pastes=[];hellos=[];metrics=[];runtime=None;runner=None
    event_file=(out/'events.jsonl').open('w',encoding='utf8');metric_file=(out/'metrics.jsonl').open('w',encoding='utf8')
    async def wait(predicate,timeout=180):
        async with asyncio.timeout(timeout):
            while not predicate():
                if runner.done():await runner;raise RuntimeError('Runtime ended')
                if runtime.session.status.state.value=='blocked':raise RuntimeError('Transport blocked')
                await asyncio.sleep(.02)
    async def feeder():
        clock=time.monotonic()
        while not stopping:
            stream=ReplayStream.latest
            if stream is not None and stream.active:
                data=chunks.popleft() if chunks else b'\0'*1280
                stream.callback(np.frombuffer(data,dtype=np.int16).reshape(-1,1),len(data)//2,None,None)
            clock+=.04
            await asyncio.sleep(max(0,clock-time.monotonic()))
            if time.monotonic()-clock>1:clock=time.monotonic()
    def queue_pcm(pcm):
        if chunks:raise RuntimeError('Previous stimulus not drained')
        chunks.extend(pcm[n:n+1280] for n in range(0,len(pcm),1280))
    async def sampler():
        while not stopping:
            sample=dict(timeUtc=datetime.now(UTC).isoformat(),elapsedSeconds=round(time.monotonic()-began,3),
                tasks=len(asyncio.all_tasks()),pendingCommands=runtime.session.pending_count,
                media=runtime.media.counters(),capture=runtime.audio.capture_counters(),
                activationsRetained=len(runtime.mirror.mirror.view.activations),
                resultTerminalsRetained=len(runtime.results._terminals),**process_memory())
            metrics.append(sample);metric_file.write(json.dumps(sample)+'\n');metric_file.flush()
            save(out/'progress.json',dict(state='RUNNING',elapsedSeconds=sample['elapsedSeconds'],plannedSeconds=args.seconds,
                completed=sum(r['result']=='PASS_SCOPED' for r in report['rows']),attempted=len(report['rows']),planned=args.count,
                activations=counts['activation.started'],finals=counts['transcription.completed'],latest=sample))
            await asyncio.sleep(5)
    async def settle():
        await wait(lambda:runtime.is_ready and runtime.media.audio_available and runtime.session.pending_count==0)
    try:
        with patch('sounddevice.InputStream',ReplayStream),patch('sounddevice.query_devices',devices),patch('sounddevice.check_input_settings',lambda **kw:None):
            runtime=V2Runtime(config,backend=backend,http=SettingsHTTP(TARGET,timeout=180),
                transport_config=V2TransportConfig(url=TARGET,connect_timeout=180,admission_timeout=180,bootstrap_timeout=180))
            old_bootstrap=runtime.session.bootstrap
            # V2Media owns bootstrap; observe the actual accepted binding callback.
            old_accepted=runtime.session.on_accepted
            def accepted(binding):
                if binding.accepted.payload.get('serverCommit')!=args.expected_server_commit:raise ValueError('Hello identity changed')
                hellos.append(dict(sessionId=binding.session_id,generation=binding.generation,serverCommit=binding.accepted.payload['serverCommit']))
                if old_accepted:old_accepted(binding)
            runtime.session.on_accepted=accepted
            previous=runtime.session.on_message
            def receive(binding,event):
                previous(binding,event)
                e=observed_event(binding,event,time.monotonic()-began)
                events.append(e);counts[e['type']]+=1;event_file.write(json.dumps(e)+'\n');event_file.flush()
                if e['type']=='transcription.completed':finals.append(e)
            runtime.session.on_message=receive
            began=time.monotonic();runner=asyncio.create_task(runtime.run())
            feed=asyncio.create_task(feeder());sample=asyncio.create_task(sampler())
            await settle()
            warm=time.monotonic();report['measurementStartedAtUtc']=datetime.now(UTC).isoformat()
            save(out/'result.json',report)
            print('MEASUREMENT_STARTED 1800 seconds / 100 automatic mixed activations',flush=True)
            blobs={k:fixture(n)[0] for k,n in [('manual','negative_speech'),('alexa','alexa_direct'),('hey_jarvis','jarvis_direct')]}
            for slot in plan:
                stage='scheduled_slot_'+str(slot['index'])
                while time.monotonic()<warm+slot['atSeconds']:await asyncio.sleep(min(1,warm+slot['atSeconds']-time.monotonic()))
                await settle()
                if runtime.mirror.mirror.view.input.activation_id is not None:raise RuntimeError('Previous input still open')
                start_count=counts['activation.started'];final_count=counts['transcription.completed'];paste_count=len(backend.send_input_calls)
                known_ids={e['activationId'] for e in events if e['type']=='activation.started'}
                slot_at=time.monotonic();row=dict(index=slot['index'],kind=slot['kind'],startSeconds=round(slot_at-warm,3))
                if slot['kind']=='manual':
                    activation=await runtime.press_control('primary')
                    if not activation.success:raise RuntimeError('Manual trigger rejected')
                queue_pcm(blobs[slot['kind']])
                stage='feed_slot_'+str(slot['index'])
                await wait(lambda:not chunks,20)
                if slot['kind']=='manual' and runtime.mirror.mirror.view.input.activation_id is not None:
                    finish=await runtime.press_control('secondary')
                    if not finish.success:raise RuntimeError('Finish rejected')
                stage='await_input_close_and_final_slot_'+str(slot['index'])
                await wait(lambda:runtime.mirror.mirror.view.input.activation_id is None and counts['activation.completed']>=slot['index'],180)
                stage='await_injection_slot_'+str(slot['index'])
                await wait(lambda:len(backend.send_input_calls)>paste_count,180)
                await settle()
                started=new_activation_starts(events,known_ids)
                new_finals=list(finals)[-(counts['transcription.completed']-final_count):]
                row.update(result='PASS_SCOPED' if counts['activation.started']==start_count+1 and len(started)==1 and
                    counts['transcription.completed']>final_count and len(backend.send_input_calls)-paste_count==len(new_finals) else 'FAIL',
                    activationIds=[e['activationId'] for e in started],finals=[dict(segmentId=e['segmentId'],textLength=e['textLength'],textSha256=e['textSha256']) for e in new_finals],
                    elapsedSeconds=round(time.monotonic()-slot_at,3),injectionBoundary='Controlled backend; actual production queue/history, no OS paste')
                report['rows'].append(row);save(out/'result.json',report)
                print(json.dumps(row),flush=True)
                # Prevent diagnostic-only raw-string/call logs from becoming the measured leak.
                backend.set_calls.clear();backend.event_log.clear();backend.foreground_window_calls.clear()
                if row['result']!='PASS_SCOPED':raise RuntimeError('Activation accounting mismatch')
                if slot['index'] in (25,50,75):
                    binding=runtime.session.binding
                    if slot['index']==50:runtime.session._ws.transport.abort()
                    else:await runtime.session.reconnect(binding,'qualification_endurance_owned_reconnect')
                    await wait(lambda:runtime.session.binding is not binding and runtime.is_ready)
                    await settle()
            while time.monotonic()-warm<args.seconds:await asyncio.sleep(min(1,args.seconds-(time.monotonic()-warm)))
            report['measurementSeconds']=round(time.monotonic()-warm,3)
            report['result']='PASS_SCOPED' if len(report['rows'])>=100 and report['measurementSeconds']>=1800 else 'FAIL'
    except Exception as error:
        report.update(result='FAIL',errorType=type(error).__name__,error=str(error),failureStage=stage)
    finally:
        stopping=True
        if runtime:await runtime.shutdown()
        if runner:await asyncio.gather(runner,return_exceptions=True)
        for task in (locals().get('feed'),locals().get('sample')):
            if task:task.cancel();await asyncio.gather(task,return_exceptions=True)
        event_file.close();metric_file.close()
        report.update(hello=hellos,eventCounts=dict(counts),metricSamples=len(metrics),
            cleanupErrors=runtime.cleanup_errors if runtime else [],durationSeconds=round(time.monotonic()-began,3) if 'began' in locals() else 0)
        after=await asyncio.to_thread(read_info);report['infoAfter']=after;report['identityStable']=after==before
        report['buildIdentityStable']=same_build(before,after)
        report['serverInstanceChanged']=after.get('serverInstanceId')!=before.get('serverInstanceId')
        if not report['buildIdentityStable'] or report['cleanupErrors']:report['result']='FAIL'
        save(out/'result.json',report);save(out/'progress.json',dict(state=report['result'],completed=len(report['rows']),seconds=report.get('measurementSeconds')))
        print(json.dumps(dict(result=report['result'],completed=len(report['rows']),seconds=report.get('measurementSeconds'))),flush=True)
    return 0 if report['result']=='PASS_SCOPED' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-server-commit',required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--seconds',type=float,default=1800);parser.add_argument('--count',type=int,default=100)
    raise SystemExit(asyncio.run(run(parser.parse_args())))
