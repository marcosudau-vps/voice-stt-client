"""Actual ReSpeaker PortAudio failure with real pending ASR and run pauses.

PCM/clipboard remain explicit controlled test boundaries. Native device opens,
callbacks, stream abort and production recovery are real. No physical unplug,
microphone recording, foreground paste, server mutation or human action.
"""
import argparse,asyncio,json,os,time,uuid
from pathlib import Path
from tests.manual.v2.suite_plan import ROOT,PROFILE_RUNTIME
from tests.manual.v2.suite_session import save
from tests.manual.v2.remote_runtime_probe import RemoteRuntime
from tests.manual.v2.verify_server_fix import fixture,read_info,check_identity


async def check(c):
    from voice_stt_client.core.audio_capture import AudioCapture
    media=c.runtime.media;capture=media.capture
    def mark(stage):
        save(c.folder/'progress.json',dict(stage=stage,running=capture.is_running,
            captureAvailable=media.capture_available,deviceAvailable=media.device_available,
            chunks=capture.chunks_captured,failures=media.capture_failures,
            mediaClosed=media._closed,mediaTaskDone=media._task.done() if media._task else None,
            taskException=type(media._task.exception()).__name__ if media._task and media._task.done() and not media._task.cancelled() else None,
            operationDone=media._capture_operation.done() if media._capture_operation else None))
    mark('before-native-switch')
    media.set_device_available(False);await c.wait(lambda:not capture.is_running,15)
    for patch in reversed(c.patches):patch.stop()
    c.patches=[]
    import sounddevice as sd
    device=next(d for d in AudioCapture.list_devices() if 'respeaker' in d['name'].lower() and
        sd.query_hostapis(sd.query_devices(d['index'])['hostapi'])['name']=='Windows DirectSound')
    capture._config.device=device['index'];capture._config.sample_rate=int(device['default_samplerate']);capture._config.channels=1
    start_native=capture.start
    def observed_start():
        try:return start_native()
        except Exception as error:
            save(c.folder/'capture-error.json',dict(type=type(error).__name__,reason=str(error)));raise
    capture.start=observed_start
    actual_packet_factory=media._packet_callback
    # Native capture counts/liveness are real; transmit only deliberate fixtures.
    media._packet_callback=lambda binding,epoch:lambda *packet:None
    media.set_device_available(True);mark('opening-native')
    try:await c.wait(lambda:media.audio_available,5)
    except TimeoutError:mark('native-open-timeout');raise
    mark('native-open');await c.wait(lambda:capture.chunks_captured>=20,15)
    async def play(name,seconds):
        data,_=fixture(name);data=data[:int(seconds*32000)]
        callback=actual_packet_factory(c.runtime.session.binding,media._epoch)
        began=time.monotonic()
        for offset in range(0,len(data),1280):
            chunk=data[offset:offset+1280];callback(chunk,16000,1,len(chunk)//2)
            await asyncio.sleep(max(0,began+(offset+len(chunk))/32000-time.monotonic()))
    mark('real-asr');first=await c.activate();await play('negative_speech',4);await c.close('finish')
    second=await c.activate();binding=c.runtime.session.binding
    pending=not any(e['activationId']==first for e in c.of_type('transcription.completed'))
    initial_chunks=capture.chunks_captured;stream=capture._stream
    mark('native-abort');await asyncio.to_thread(stream.abort);media._wake.set()
    fault_seconds=c.seconds()
    await c.wait(lambda:c.view.input.activation_id is None,15)
    await c.ready();await c.wait(lambda:len(c.backend.send_input_calls)==1)
    finals=c.of_type('transcription.completed');cancelled=c.of_type('activation.cancelled')
    checks=dict(nativeCallbacksBeforeFault=initial_chunks>=20,pendingAtNativeFault=pending,
        distinctOpenInput=first!=second,oldFinalRetained=len(finals)==1 and finals[0]['activationId']==first,
        sameSessionAndGeneration=c.runtime.session.binding is binding,
        openInputCancelled=any(e['activationId']==second for e in cancelled),
        noAutomaticActivation=len(c.of_type('activation.started'))==2,
        nativeCaptureRecovered=capture.device_active and capture._stream is not stream,
        exactlyOneControlledPaste=len(c.backend.send_input_calls)==1)
    masks=[]
    for source in ('manual','wakeWord'):
        await c.runtime.controls.set_pause(source,True)
        before=tuple(c.runtime.controls._desired)
        c.runtime.set_microphone_muted(True);await c.wait(lambda:not media.audio_available)
        c.runtime.set_microphone_muted(False);await c.ready()
        masks.append(dict(source=source,before=list(before),after=list(c.runtime.controls._desired)))
    checks['runPauseMasksSurviveNativeReopen']=all(m['before']==m['after'] for m in masks)
    await c.runtime.controls.set_pause('manual',False);await c.runtime.controls.set_pause('wakeWord',False)
    return dict(checks=checks,device=device,nativeChunksBeforeFault=initial_chunks,
        faultSeconds=fault_seconds,firstId=first,secondId=second,finals=finals,cancelled=cancelled,masks=masks,
        boundary='Real native capture/abort/reopen. Deliberate PCM injection after capture; controlled clipboard. Software mute is not physical-button actuation; actual earlier physical USB/mute proofs remain separate.')


async def main(args):
    args.output.mkdir(parents=True,exist_ok=False)
    folder=PROFILE_RUNTIME/('native-pending-'+uuid.uuid4().hex[:12]);(folder/'tmp').mkdir(parents=True)
    os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),TEMP=str(folder/'tmp'),TMP=str(folder/'tmp'))
    before=await asyncio.to_thread(read_info);assert check_identity(before,args.expected_server_commit)
    report=dict(result='RUNNING',pid=os.getpid(),runtimeFolder=str(folder),infoBefore=before,scope=__doc__)
    save(args.output/'result.json',report)
    try:
        async with RemoteRuntime(folder,'native-audio-fault',args.expected_server_commit) as c:
            report.update(await check(c))
        report['cleanupErrors']=c.cleanup
        after=await asyncio.to_thread(read_info);report.update(infoAfter=after,identityStable=before==after)
        report['result']='PASS_SCOPED' if all(report['checks'].values()) and not c.cleanup and before==after else 'FAIL'
    except Exception as error:report.update(result='FAIL',errorType=type(error).__name__,error=str(error))
    save(args.output/'result.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ('infoBefore','infoAfter')}),flush=True)
    return 0 if report['result']=='PASS_SCOPED' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--expected-server-commit',required=True);a=p.parse_args()
    if not a.output.resolve().is_relative_to(ROOT/'build'):p.error('Project build output required')
    raise SystemExit(asyncio.run(main(a)))
