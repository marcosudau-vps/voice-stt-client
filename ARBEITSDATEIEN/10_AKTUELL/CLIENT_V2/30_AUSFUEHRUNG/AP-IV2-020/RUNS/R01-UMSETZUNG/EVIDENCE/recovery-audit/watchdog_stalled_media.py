"""Legal 60s watchdog with real ASR followed by a controlled PCM transport stall.

This is deliberate replay of energy-selected real WAV chunks and a media stall, not fresh human
speech. No fake clock, fake recorder, synthetic waveform or model replacement.
Session-only timing overrides disappear on disconnect; server defaults untouched.
"""
import argparse
import asyncio
import json
from pathlib import Path
import sys
import time
import wave

sys.path.insert(0,str(next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())))
from scripts.qualify_v2_real import digest,identity,save,SERVER


async def run(audio,evidence):
    import numpy as np
    from voice_stt_client.core import protocol_v2 as p
    from voice_stt_client.core.v2_transport import V2STTSession,V2TransportConfig
    from voice_stt_client.core.v2_mirror import V2MirrorConnection
    from voice_stt_client.core.v2_profile import V2Profile
    from voice_stt_client.core.settings_service import SettingsService
    with wave.open(str(audio),'rb') as w:
        assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(16000,1,2)
        pcm=w.readframes(w.getnframes())
    chunks=[pcm[i:i+1280] for i in range(0,len(pcm)-1280,1280)]
    chunks=[c for c in chunks if np.sqrt(np.mean(np.frombuffer(c,dtype='<i2').astype(float)**2))>400]
    if not chunks:raise RuntimeError('Reference speech energy missing')
    desired={'activation.segmentWatchdogInitialMs':60000,
             'activation.segmentWatchdogRefreshMs':30000,
             'activation.segmentWatchdogWarningMs':5000,
             'activation.followupTimeoutMs':60000}
    session=V2STTSession(V2TransportConfig(url='ws://127.0.0.1:18020/ws/v2'))
    mirror=V2MirrorConnection(session)
    settings=SettingsService(session,V2Profile(desired_settings=desired))
    async def bootstrap(client,binding):
        await settings.bootstrap(client,binding)
        await client.bootstrap_command(binding,p.CommandType.AUDIO_AVAILABILITY,audioAvailable=True)
    session.bootstrap=bootstrap
    events=[];finals=[]
    def reduction(value):
        for e in value.events:
            events.append(dict(type=str(e.type),time=time.monotonic(),reason=e.payload.get('reason')))
        finals.extend(dict(time=time.monotonic(),characters=len(f.text)) for f in value.finals)
    mirror.on_reduction=reduction
    task=asyncio.create_task(session.run())
    async def until(predicate,seconds):
        async with asyncio.timeout(seconds):
            while not predicate():
                if task.done():raise RuntimeError('Transport stopped')
                await asyncio.sleep(.02)
    try:
        await until(lambda:session.is_ready,30)
        assert session.binding.accepted.payload['serverCommit']==SERVER
        await session.request(p.CommandType.ACTIVATION,action='activate',source='manual')
        start=time.monotonic()
        for index in range(100):
            chunk=chunks[index%len(chunks)]
            await session.send_audio(chunk,16000,1,640,binding=session.binding)
            await asyncio.sleep(max(0,start+(index+1)*.04-time.monotonic()))
            if any(e['reason']=='segment_watchdog_timeout' for e in events):break
        await until(lambda:any(e['reason']=='segment_watchdog_timeout' for e in events),75)
        await until(lambda:bool(finals),30)
        warning=next((e for e in events if e['type']=='watchdog.warning'),None)
        closed=next((e for e in events if e['reason']=='segment_watchdog_timeout'),None)
        result=dict(identity=identity(),serverCommit=SERVER,audioSha256=digest(audio),
            sessionOverrides=desired,events=events,finals=finals,
            replayDerivation='100 energy-selected real 40ms WAV chunks (4s), then no PCM until watchdog expiry; real clock and models; no new human recording.',
            warning=warning,watchdogExpiry=closed,
            result='PASS' if warning and closed and finals else 'FAIL',boundaries=__doc__)
        save(evidence/'real-watchdog-stalled-media.json',result)
        print(json.dumps(dict(result=result['result'],warning=warning,expiry=closed,finals=len(finals))))
    finally:
        await session.stop();await mirror.close();await asyncio.gather(task,return_exceptions=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio',type=Path,required=True)
    parser.add_argument('--evidence',type=Path,required=True)
    args=parser.parse_args()
    asyncio.run(run(args.audio,args.evidence))
