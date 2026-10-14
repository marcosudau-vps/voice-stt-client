"""Real reference WAV -> production V2 WS/mirror -> real local ASR.

No recorder/ASR fake and no clipboard side effect. English material through the
German qualification model is a pipeline/latency smoke, not a German quality
judgement. Separate English Golden test checks actual recognized wording.
"""
import argparse
import asyncio
import json
from pathlib import Path
import sys
import time
import wave

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.qualify_v2_real import SERVER,digest,identity,save


async def run(audio,evidence):
    from voice_stt_client.core import protocol_v2 as p
    from voice_stt_client.core.v2_transport import V2STTSession,V2TransportConfig
    from voice_stt_client.core.v2_mirror import V2MirrorConnection
    from voice_stt_client.core.v2_profile import V2Profile
    from voice_stt_client.core.settings_service import SettingsService
    with wave.open(str(audio),'rb') as handle:
        if (handle.getframerate(),handle.getnchannels(),handle.getsampwidth())!=(16000,1,2):
            raise ValueError('Use a mono/16000Hz/16bit reference WAV')
        pcm=handle.readframes(handle.getnframes())
    session=V2STTSession(V2TransportConfig(url='ws://127.0.0.1:18020/ws/v2'))
    mirror=V2MirrorConnection(session)
    settings=SettingsService(session,V2Profile())
    async def bootstrap(client,binding):
        await settings.bootstrap(client,binding)
        await client.bootstrap_command(binding,p.CommandType.AUDIO_AVAILABILITY,audioAvailable=True)
    session.bootstrap=bootstrap
    trace=[];finals=[]
    previous=mirror.on_reduction
    def reduce(value):
        if previous:previous(value)
        now=time.monotonic()
        for event in value.events:
            trace.append(dict(type=str(event.type),time=now,eventSeq=event.eventSeq))
        for result in value.finals:
            finals.append(dict(segmentId=result.segment_id,characters=len(result.text),time=now))
    mirror.on_reduction=reduce
    task=asyncio.create_task(session.run())
    async def wait(predicate,timeout=60):
        async with asyncio.timeout(timeout):
            while not predicate():
                if task.done():raise RuntimeError('Real server transport stopped')
                await asyncio.sleep(.02)
    async def stream(data):
        started=time.monotonic()
        for offset in range(0,len(data),1280):
            chunk=data[offset:offset+1280]
            if not await session.send_audio(chunk,16000,1,len(chunk)//2,binding=session.binding):
                raise RuntimeError('Real audio rejected')
            await asyncio.sleep(max(0,started+(offset+len(chunk))/32000-time.monotonic()))
    try:
        await wait(lambda:session.is_ready and mirror.mirror.view.operations_ready)
        if session.binding.accepted.payload['serverCommit']!=SERVER:raise RuntimeError('Wrong server')
        ack=await session.request(p.CommandType.ACTIVATION,action='activate',source='manual')
        if not ack.ack.accepted:raise RuntimeError('Activation rejected')
        await stream(b'\0'*16000)
        audio_started=time.monotonic()
        await stream(pcm)
        audio_finished=time.monotonic()
        await stream(b'\0'*48000)
        if mirror.mirror.view.input.activation_id:
            await session.request(p.CommandType.ACTIVATION,action='finish',
                                  activationId=mirror.mirror.view.input.activation_id)
        await wait(lambda:len(finals)>0,90)
        result=dict(identity=identity(),serverCommit=SERVER,audioSha256=digest(audio),
            durationSeconds=len(pcm)/32000,audioStarted=audio_started,audioFinished=audio_finished,
            trace=trace,finals=finals,pending=session.pending_count,
            result='PASS' if finals and all(f['characters']>0 for f in finals) else 'FAIL',
            boundaries=__doc__,quality='NOT_PROVEN (English reference / German model)',paste='NOT_RUN')
        save(evidence/'real-audio-pipeline.json',result)
        print(json.dumps(dict(result=result['result'],finals=len(finals),
            finalAfterAudioSeconds=round(finals[-1]['time']-audio_finished,3))))
    finally:
        await session.stop();await mirror.close();await asyncio.gather(task,return_exceptions=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio',type=Path,required=True)
    parser.add_argument('--evidence',type=Path,required=True)
    args=parser.parse_args()
    asyncio.run(run(args.audio,args.evidence))
