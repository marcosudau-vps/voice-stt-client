"""Real TLS server/model replay after Issue7; never modifies server code/defaults.

Only the previously authorized conscious WAV fixtures are transmitted, paced in
real time. Digital silence is a test stimulus, not a physical microphone proof.
No clipboard, native recording, sound playback, raw transcript or credential log.
"""
import argparse
import asyncio
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
import sys
import time
from urllib.request import Request, urlopen
import wave

from tests.manual.v2.suite_plan import ROOT, TARGET, target_origin
from tests.manual.v2.suite_session import save

FIXTURES = ROOT/'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/human/samples'


def check_identity(info, expected):
    if not isinstance(info,dict) or not isinstance(expected,str) or not re.fullmatch('[a-f0-9]{40}',expected):
        return False
    return (type(info.get('schemaVersion')) is int and info.get('schemaVersion') == 1
        and type(info.get('protocolVersion')) is int and info.get('protocolVersion') == 2
        and info.get('identityStatus') == 'complete' and info.get('serverCommit') == expected
        and info.get('build',{}).get('sourceDirty') is False
        and bool(re.fullmatch('[a-f0-9]{40}',info.get('build',{}).get('sourceTree','')))
        and info.get('runtime',{}).get('krokoVariant') == 'pro')


def read_info():
    url=target_origin(TARGET)+'/api/v2/info'
    with urlopen(Request(url,headers={'Accept':'application/json'}),timeout=180) as response:
        if response.status!=200 or response.url!=url:
            raise RuntimeError('Unexpected info response or redirect')
        data=response.read(1024*1024+1)
        if len(data)>1024*1024: raise RuntimeError('Oversized info document')
        return json.loads(data)


def fixture(name):
    path=FIXTURES/(name+'.wav')
    record=next(r for r in json.loads((FIXTURES/'manifest.json').read_text(encoding='utf8'))['records'] if r['file']==path.name)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:
        raise RuntimeError('Fixture hash mismatch')
    with wave.open(str(path),'rb') as handle:
        if (handle.getframerate(),handle.getnchannels(),handle.getsampwidth())!=(16000,1,2):
            raise ValueError('Expected qualified PCM format')
        return handle.readframes(handle.getnframes()),record


def assess_rearm(events, wake_id):
    starts=[e for e in events if e['type']=='activation.started']
    hits=[e for e in events if e['type']=='wakeword.detected']
    closed=[e for e in events if e['type']=='activation.input_closed']
    ids=[e.get('activationId') for e in starts]
    checks=dict(exactlyTwoActivations=len(starts)==2,distinctIds=len(set(ids))==2,
        exactlyTwoWakeEvents=len(hits)==2,
        selectedWakeId=bool(hits) and all(e.get('wakeWordId')==wake_id for e in hits),
        hitIdsMatchStarts=bool(ids) and sorted(e.get('activationId','') for e in hits)==sorted(ids),
        exactlyTwoClosures=len(closed)==2,
        closureIdsMatch=bool(ids) and sorted(e.get('activationId','') for e in closed)==sorted(ids))
    return checks


def observed_event(binding,event,elapsed):
    from tests.manual.v2.observed_session import safe_event
    return dict(timeSeconds=round(elapsed,4),bindingSessionId=binding.session_id,
        **safe_event(binding,event))


async def run_case(name, kind, word, close_mode, expected, *, press_control=None):
    from voice_stt_client.core import protocol_v2 as p
    from voice_stt_client.core.v2_transport import V2STTSession,V2TransportConfig
    from voice_stt_client.core.v2_mirror import V2MirrorConnection
    from voice_stt_client.core.v2_profile import V2Profile
    from voice_stt_client.core.settings_service import SettingsHTTP,SettingsService
    refresh_probe = kind == 'control_refresh'
    profile=V2Profile(manual=refresh_probe,wake_word=not refresh_probe,
        wake_word_ids=[] if refresh_probe else ['hey_jarvis','alexa'],
        desired_settings={'activation.followupTimeoutMs':5000,'wakeWord.preRollMs':320})
    session=V2STTSession(V2TransportConfig(url=TARGET,connect_timeout=180,
        admission_timeout=180,bootstrap_timeout=180))
    mirror=V2MirrorConnection(session)
    settings=SettingsService(session,profile,http=SettingsHTTP(TARGET,timeout=180))
    controls = None
    if refresh_probe:
        from voice_stt_client.core.v2_controls import V2ControlService
        controls = V2ControlService(session, mirror, audio_ready=lambda: session.is_ready)
    async def press(slot):
        if press_control is not None:
            return await press_control(controls,mirror,slot)
        return await controls.press(slot)
    events,hello,finals=[],[],[]
    runner=None
    start=time.monotonic()
    async def bootstrap(client,binding):
        if binding.accepted.payload['serverCommit']!=expected:
            raise ValueError('WebSocket server identity differs from selected info commit')
        hello.append(dict(generation=binding.generation,sessionId=binding.session_id,
            serverCommit=binding.accepted.payload['serverCommit']))
        await client.bootstrap_command(binding,p.CommandType.AUDIO_AVAILABILITY,audioAvailable=True)
        await settings.bootstrap(client,binding)
    session.bootstrap=bootstrap
    previous=session.on_message
    def receive(binding,event):
        previous(binding,event)
        events.append(observed_event(binding,event,time.monotonic()-start))
    session.on_message=receive
    old_reduction=mirror.on_reduction
    def reduced(value):
        if old_reduction: old_reduction(value)
        for final in value.finals:
            finals.append(dict(activationId=final.activation_id,segmentId=final.segment_id,
                textLength=len(final.text),textSha256=hashlib.sha256(final.text.encode()).hexdigest()))
    mirror.on_reduction=reduced
    async def wait(predicate,seconds=180):
        async with asyncio.timeout(seconds):
            while not predicate():
                if runner.done():
                    await runner
                    raise RuntimeError('Transport ended before expected observation')
                if session.status.state.value=='blocked':
                    raise RuntimeError('Transport blocked: '+session.status.reason)
                await asyncio.sleep(.02)
    async def ready():
        await wait(lambda: session.is_ready and mirror.mirror.view.operations_ready
            and not mirror.mirror.view.snapshot_pending)
    async def send(pcm,until=None):
        began=time.monotonic()
        sent=0
        for offset in range(0,len(pcm),1280):
            if until and until(): break
            chunk=pcm[offset:offset+1280]
            if not await session.send_audio(chunk,16000,1,len(chunk)//2,binding=session.binding):
                raise RuntimeError('Replay transport gated unexpectedly')
            sent+=len(chunk)
            await asyncio.sleep(max(0,began+sent/32000-time.monotonic()))
        return sent//2
    async def silence(seconds,until=None):
        return await send(b'\0'*int(32000*seconds),until)
    def starts(): return [e for e in events if e['type']=='activation.started']
    async def hit(pcm,count):
        await send(pcm,lambda:len(starts())>=count)
        await silence(1,lambda:len(starts())>=count)
        await wait(lambda:len(starts())>=count,5)
        await ready()
    async def close(action,aid):
        completion=await session.request(p.CommandType.ACTIVATION,action=action,activationId=aid)
        if not completion.ack.accepted: raise AssertionError('Explicit close rejected')
        await silence(2,lambda:any(e['type']=='activation.input_closed' and e.get('activationId')==aid for e in events))
        await wait(lambda:any(e['type']=='activation.input_closed' and e.get('activationId')==aid for e in events),10)
        await ready()
    data,record=fixture(name)
    result=dict(case=f'{name}-{kind}-{close_mode}',kind=kind,word=word,
        closeMode=close_mode,fixtureSha256=record['sha256'],
        method='Authorized human WAV replay at real time over TLS to actual selected server; digital silence after close. Not a new live-microphone or sound-feedback proof.')
    runner=asyncio.create_task(session.run())
    try:
        await ready()
        if refresh_probe:
            activated = await press('primary')
            assert activated is not None and activated.ack.accepted
            aid = activated.ack.activationId
            await ready()
            def ended():return any(e['type']=='segment.recording_ended' for e in events)
            await send(data,ended)
            await silence(12,ended)
            await wait(ended,5)
            await ready()
            assert mirror.mirror.view.input.phase == p.InputPhase.FOLLOWUP_WAIT
            before = mirror.mirror.view.input.deadline.unix_ms
            await silence(2)
            assert mirror.mirror.view.input.phase == p.InputPhase.FOLLOWUP_WAIT
            first = await press('primary')
            await ready()
            after = mirror.mirror.view.input.deadline.unix_ms
            remaining = mirror.mirror.view.input.deadline.remaining(time.monotonic())
            repeat_at = time.monotonic()
            second = await press('primary')
            await ready()
            repeated = mirror.mirror.view.input.deadline.unix_ms
            repeat_ms = (time.monotonic()-repeat_at)*1000
            await silence(3.3)
            crossed_old = mirror.mirror.view.input.activation_id == aid
            await silence(10,lambda:mirror.mirror.view.input.activation_id is None)
            await wait(lambda:mirror.mirror.view.input.activation_id is None,5)
            await ready()
            await wait(lambda:bool(finals),180)
            result['checks']=dict(oneActivation=len(starts())==1,
                twoAcceptedRefreshes=all(c is not None and c.ack.accepted and c.command.payload.get('action')=='refresh'
                    and c.command.payload.get('activationId')==aid for c in (first,second)),
                extendedDeadline=after>before+1000,freshFiveSecondWindow=4500<=remaining<=5000,
                repeatNotCumulative=0<=repeated-after<=repeat_ms+250,
                stillOpenPastOriginalDeadline=crossed_old,
                naturalTimeout=any(e['type']=='activation.input_closed' and e.get('activationId')==aid
                    and e.get('reason')=='timed_out' for e in events),
                terminal=any(e['type']=='activation.completed' and e.get('activationId')==aid for e in events),
                realAsrFinal=bool(finals) and all(f['textLength']>0 for f in finals))
            result['deadlines']=dict(beforeUnixMs=before,afterUnixMs=after,repeatedUnixMs=repeated,
                remainingAfterRefreshMs=remaining,repeatRoundTripMs=round(repeat_ms,3))
            result['method']='Real authorized human speech fixture and digital silence through production Controls/Settings/Mirror/TLS and real server ASR; no physical hotkey or microphone/paste qualification.'
        elif kind=='rearm':
            await hit(data,1)
            aid=starts()[0]['activationId']
            if close_mode=='timeout':
                await silence(40,lambda:any(e['type']=='activation.input_closed' and e.get('activationId')==aid for e in events))
                await wait(lambda:any(e['type']=='activation.input_closed' and e.get('activationId')==aid for e in events),5)
            else:
                await close('cancel' if close_mode=='reconnect' else close_mode,aid)
            await silence(5)
            result['checks']=dict(noExtraActivationOnSilence=len(starts())==1)
            if close_mode=='reconnect':
                binding=session.binding
                await session.reconnect(binding,'qualification_wake_rearm')
                await wait(lambda:session.is_ready and session.binding is not binding)
                await ready()
                await silence(5)
                result['checks']['noActivationAfterReconnect']=len(starts())==1
            await hit(data,2)
            await close('cancel',starts()[1]['activationId'])
            await silence(5)
            result['checks'].update(assess_rearm(events,word))
            if close_mode=='timeout':
                result['checks']['actualTimeout']=any(e['type']=='activation.input_closed'
                    and e.get('activationId')==aid and e.get('reason')=='timed_out' for e in events)
        elif kind=='negative':
            await send(data)
            await silence(5)
            result['checks']=dict(noWake=not any(e['type']=='wakeword.detected' for e in events),
                noActivation=not starts(),noFinal=not finals)
        else:
            await send(data)
            await silence(10)
            await wait(lambda:bool(finals) and mirror.mirror.view.input.activation_id is None)
            await silence(5)
            result['checks']=dict(oneActivation=len(starts())==1,
                oneWake=len([e for e in events if e['type']=='wakeword.detected'])==1,
                nonemptyFinal=bool(finals) and all(f['textLength']>0 for f in finals),
                selectedWakeId=all(e.get('wakeWordId')==word for e in events if e['type']=='wakeword.detected'))
            result['transcriptQuality']='NOT_PROVEN: hashes/lengths only; no phonetic boundary annotation or new human assessment'
        await ready()
        # A terminal event may schedule its snapshot request on the next turn.
        # Await actual tracker drain; don't mistake a just-started resync for
        # leaked commands or inspect it before its real Ack has been consumed.
        await wait(lambda: session.pending_count == 0 and not mirror.mirror.view.snapshot_pending)
        result['checks']['noPendingCommands']=session.pending_count==0
        result['checks']['effectivePreferences']=(settings.report().effective.get('activation.followupTimeoutMs')==5000
            and settings.report().effective.get('wakeWord.preRollMs')==320)
        result['result']='PASS_SCOPED' if all(result['checks'].values()) else 'FAIL'
        result['effectiveSettings']=dict(settings.report().effective)
        result['serverEffectiveSettings']=dict(settings.server_effective)
    except Exception as error:
        result.update(result='FAIL',errorType=type(error).__name__,error=str(error))
    finally:
        if controls:
            await controls.close()
        await settings.close()
        await mirror.close()
        await asyncio.gather(runner,return_exceptions=True)
        result.update(hello=hello,events=events,finals=finals,seconds=round(time.monotonic()-start,3))
    return result


def cases():
    rows=[]
    for name,word in [('alexa_pause','alexa'),('jarvis_direct','hey_jarvis')]:
        rows.extend((name,'rearm',word,mode) for mode in ('timeout','finish','cancel','reconnect'))
    rows.extend((name,'negative',None,'none') for name in ('negative_speech','unselected_phrase','jarvis_pause'))
    rows.extend((name,'speech',word,'natural') for name,word in [('alexa_direct','alexa'),('jarvis_direct','hey_jarvis')])
    return rows


async def main(args):
    from scripts.qualify_v2_real import identity
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'build').resolve()): raise ValueError('Output must be in project build')
    out.mkdir(parents=True,exist_ok=True)
    before=await asyncio.to_thread(read_info)
    if not check_identity(before,args.expected_server_commit): raise ValueError('Info identity not complete or not selected commit/variant')
    report=dict(timeUtc=datetime.now(UTC).isoformat(),identity=identity(),target=TARGET,
        infoBefore=before,rows=[],scope='Real deployed model and production V2 components; fixture replay, not physical human qualification')
    selected=([(name,'control_refresh',None,'natural') for name in ('negative_speech','alexa_direct')]
        if args.controls_refresh_only else cases())
    if args.first_only: selected=selected[:1]
    for row in selected:
        print('START '+' / '.join(str(v) for v in row),flush=True)
        result=await run_case(*row,args.expected_server_commit)
        report['rows'].append(result)
        save(out/'result.json',report)
        print(json.dumps(dict(case=result['case'],result=result['result'],seconds=result['seconds'],error=result.get('error'))),flush=True)
        if result['result']=='FAIL': break
    after=await asyncio.to_thread(read_info)
    report['infoAfter']=after
    report['identityStable']=before==after
    report['result']='PASS_SCOPED' if (len(report['rows'])==len(selected) and all(r['result']=='PASS_SCOPED' for r in report['rows'])
        and before==after) else 'FAIL'
    save(out/'result.json',report)
    print(json.dumps(dict(result=report['result'],cases=len(report['rows']),identityStable=report['identityStable'])),flush=True)
    return 0 if report['result']=='PASS_SCOPED' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-server-commit',required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--first-only',action='store_true')
    parser.add_argument('--controls-refresh-only',action='store_true',
        help='Real ASR/followup refresh and noncumulative deadline diagnostic; no native hotkey or microphone')
    raise SystemExit(asyncio.run(main(parser.parse_args())))
