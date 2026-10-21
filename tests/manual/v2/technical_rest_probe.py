"""Real-server combination probes using owned profiles and authorized fixtures."""
import argparse,asyncio,gc,json,os,time
from uuid import uuid4
from dataclasses import asdict,replace
from datetime import UTC,datetime
from pathlib import Path
from tests.manual.v2.suite_plan import ROOT,PROFILE_RUNTIME
from tests.manual.v2.suite_session import save
from tests.manual.v2.verify_server_fix import read_info,check_identity
from tests.manual.v2.remote_runtime_probe import RemoteRuntime


async def controls(c,phase,action,slot):
    aid=await c.activate()
    if phase=='recording':
        await c.play('negative_speech',4);await c.wait(lambda:str(c.view.input.phase)=='segment_active')
    elif phase=='followup':
        await c.play('negative_speech');await c.wait(lambda:str(c.view.input.phase)=='followup_wait')
    else:assert str(c.view.input.phase)=='waiting_first_speech'
    c.runtime.controls.config=replace(c.runtime.controls.config,**{slot+'_action':action})
    before=len(c.commands);count=len(c.of_type('transcription.completed'))
    result=await c.runtime.press_control(slot);await c.ready()
    mutations=[v for v in c.commands[before:] if v['action'] in ('refresh','finish','cancel')]
    blocked=action=='refresh' and phase=='waiting'
    checks=dict(correctControlOutcome=result.success is not blocked,
                exactlyExpectedMutation=len(mutations)==(0 if blocked else 1),
                onlyOriginalActivation=len(c.of_type('activation.started'))==1)
    if action=='refresh' or blocked:
        checks['sameInput']=c.view.input.activation_id==aid
        await c.close('cancel')
    else:
        await c.wait(lambda:c.view.input.activation_id is None)
        if action=='finish' and phase!='waiting':await c.wait(lambda:len(c.backend.send_input_calls)>=1)
        if action=='cancel':
            await asyncio.sleep(.4)
            checks['noAdditionalFinalAfterCancel']=len(c.of_type('transcription.completed'))==count
    return dict(checks=checks,phase=phase,action=action,slot=slot)


async def settings(c,choice):
    from voice_stt_client.core.settings_service import SettingsError
    aid=await c.activate();await c.play('negative_speech',4)
    await c.wait(lambda:str(c.view.input.phase)=='segment_active')
    ui=c.runtime.settings_ui_session();ui.wait_timeout=180
    old=c.runtime.session.binding;profile=asdict(c.runtime.settings.profile)
    profile.update(manual=False,wake_word=True,wake_word_ids=['alexa','hey_jarvis'])
    before=(c.folder/'profile.yaml').read_bytes()
    try:await ui.apply_profile(profile,ui.context())
    except SettingsError as error:assert error.code=='activation_choice_required'
    else:raise AssertionError('Missing decision accepted')
    checks=dict(missingChoiceNoPersist=(c.folder/'profile.yaml').read_bytes()==before,
                missingChoiceKeepsInput=c.view.input.activation_id==aid)
    await ui.apply_profile(profile,ui.context(),choice=choice,drain_choice='wait')
    if choice=='defer':
        checks.update(deferKeepsBinding=c.runtime.session.binding is old,
                      deferKeepsInput=c.view.input.activation_id==aid,
                      oldEffectiveStillManual=c.view.trigger['configured']['manual'] is True)
        await c.close('finish');await c.wait(lambda:len(c.backend.send_input_calls)==1)
        await c.wait(lambda:all(a.status not in ('draining','active') for a in c.view.activations.values()))
        assert (await c.runtime.reconnect_server()).success
    await c.wait(lambda:c.runtime.session.binding is not old and c.runtime.is_ready);await c.ready()
    checks.update(newWakeOnly=c.view.trigger['configured']['manual'] is False and c.view.trigger['configured']['wakeWord'] is True,
                  followupPreserved=c.view.effective_settings['activation.followupTimeoutMs']==5000,
                  preRollPreserved=c.view.effective_settings['wakeWord.preRollMs']==320,
                  noAutomaticActivation=c.view.input.activation_id is None,
                  oneOldActivation=len(c.of_type('activation.started'))==1)
    await asyncio.sleep(.4)
    checks['correctFinalCount']=len(c.of_type('transcription.completed'))==(0 if choice=='cancel' else 1)
    ui.invalidate()
    return dict(checks=checks,choice=choice)


async def fault(c):
    aid=await c.activate();old=c.runtime.session.binding
    await c.play('negative_speech')
    await c.wait(lambda:bool(c.faults));await c.wait(lambda:c.runtime.session.binding is not old and c.runtime.is_ready)
    await c.ready();await asyncio.sleep(.5)
    checks=dict(ownTransportFault=len(c.faults)==1,noOldPaste=len(c.backend.send_input_calls)==0,
                oldNotResumed=c.view.input.activation_id is None,
                noAutomaticNewActivation=len(c.of_type('activation.started'))==1)
    fresh=await c.activate();await c.play('negative_speech');
    if c.view.input.activation_id:await c.close('finish')
    await c.wait(lambda:len(c.backend.send_input_calls)==1)
    finals=c.of_type('transcription.completed')
    checks.update(newActivationDistinct=fresh!=aid,oneNewFinal=len(finals)==1 and finals[0]['activationId']==fresh,
                  onlyNewSessionPublished=all(e['sessionId']==c.runtime.session.binding.session_id for e in finals))
    return dict(checks=checks,faults=c.faults)


async def wake(c):
    before=await c.runtime.press_control('primary')
    checks=dict(idleManualDisabled=not before.success)
    for i,name in enumerate(('alexa_pause','jarvis_direct')):
        await c.play(name,until=lambda:len(c.of_type('activation.started'))>i)
        await c.ready()
        aid=c.view.input.activation_id;assert aid
        c.runtime.controls.config=replace(c.runtime.controls.config,primary_action='cancel')
        result=await c.runtime.press_control('primary')
        assert result.success;await c.wait(lambda:c.view.input.activation_id is None)
        await asyncio.sleep(.8)
    checks.update(twoWakeIds={e['wakeWordId'] for e in c.of_type('wakeword.detected')}=={'alexa','hey_jarvis'},
                  exactlyTwoStarts=len(c.of_type('activation.started'))==2,
                  activePrimaryWorksWithoutManual=sum(v['action']=='cancel' and v['accepted'] for v in c.commands)==2)
    return dict(checks=checks)


async def race(c,delay):
    from tests.manual.v2.verify_server_fix import fixture
    data,_=fixture('alexa_direct');audio_at=c.seconds();c.queue(data);began=time.monotonic();before=len(c.commands)
    await asyncio.sleep(delay);command_at=c.seconds();result=await c.runtime.press_control('primary')
    await c.wait(lambda:bool(c.of_type('activation.started')));await c.ready()
    await c.wait(lambda:not c.chunks,20)
    if c.view.input.activation_id:await c.close('finish')
    await c.wait(lambda:len(c.backend.send_input_calls)==1)
    starts=c.of_type('activation.started');first=starts[0]
    return dict(checks=dict(oneWinner=len(starts)==1,oneFinal=len(c.of_type('transcription.completed'))==1,
        sourceConsistent=admission_consistent(first['primarySource'],c.commands[before:]),
        closeTriggerTiming=abs(command_at-first['timeSeconds'])<.3),
        audioStartSeconds=audio_at,manualRequestSeconds=command_at,firstAdmissionSeconds=first['timeSeconds'],primarySource=first['primarySource'])


def admission_consistent(source,commands):
    manual=any(v.get('action')=='activate' and v.get('accepted') for v in commands)
    return (source=='manual')==manual


async def cue(c):
    began=c.seconds();await c.play('alexa_direct',until=lambda:bool(c.of_type('activation.started')))
    await c.ready();hit=c.of_type('activation.started')[0]['timeSeconds']
    await c.close('cancel')
    return dict(checks=dict(oneWakeStart=len(c.of_type('activation.started'))==1),wakeOffset=hit-began)


async def drain(c):
    from voice_stt_client.core.settings_service import SettingsError
    aid=await c.activate();await c.play('negative_speech',2);await c.close('finish')
    ui=c.runtime.settings_ui_session();ui.wait_timeout=180;context=ui.context()
    assert aid in context.drain_ids,'Actual pending-final window was not captured'
    profile=asdict(c.runtime.settings.profile);profile.update(manual=False,wake_word=True,wake_word_ids=['alexa','hey_jarvis'])
    raw=(c.folder/'profile.yaml').read_bytes();old=c.runtime.session.binding
    try:await ui.apply_profile(profile,context)
    except SettingsError as error:assert error.code=='drain_choice_required'
    else:raise AssertionError('Missing drain choice accepted')
    checks=dict(pendingFinalGuard=True,guardNoPersist=(c.folder/'profile.yaml').read_bytes()==raw)
    await ui.apply_profile(profile,context,drain_choice='wait')
    await c.wait(lambda:c.runtime.session.binding is not old and c.runtime.is_ready);await c.ready()
    await c.wait(lambda:len(c.backend.send_input_calls)==1)
    finals=c.of_type('transcription.completed')
    checks.update(oneOldFinalPreserved=len(finals)==1 and finals[0]['activationId']==aid,
                  actualOrderedDelay=len(c.faults)==1,oneNewSession=len(c.hello)==2)
    ui.invalidate();return dict(checks=checks,capturedDrainIds=list(context.drain_ids))


async def memory(c):
    import tracemalloc,weakref
    from scripts.qualify_v2_session import process_memory
    tracemalloc.start();samples=[];released=[]
    for batch in range(3):
        for _ in range(6):
            await c.activate();await c.play('negative_speech',2);await c.close('cancel')
        gc.collect()
        retained=dict(activations=len(c.view.activations),segments=len(c.view.segments),terminals=len(c.runtime.results._terminals))
        refs=[weakref.ref(v) for v in c.view.activations.values()]
        traced=tracemalloc.get_traced_memory()
        allocation=tracemalloc.take_snapshot().statistics('lineno')[:10]
        samples.append(dict(batch=batch+1,retained=retained,pythonTracedBytes=traced[0],pythonPeakBytes=traced[1],
            memory=process_memory(),tasks=len(asyncio.all_tasks()),pending=c.runtime.session.pending_count,
            allocationTop=[dict(file=str(v.traceback[0].filename).replace(str(ROOT),'<repo>'),line=v.traceback[0].lineno,
                                bytes=v.size,count=v.count) for v in allocation]))
        old=c.runtime.session.binding;assert (await c.runtime.reconnect_server()).success
        await c.wait(lambda:c.runtime.session.binding is not old and c.runtime.is_ready);await c.ready();gc.collect()
        released.append(dict(remainingOldActivationObjects=sum(r() is not None for r in refs),
            newActivations=len(c.view.activations),newSegments=len(c.view.segments),newTerminals=len(c.runtime.results._terminals)))
    tracemalloc.stop()
    return dict(checks=dict(oldGenerationObjectsReleased=all(not any(s.values()) for s in released),
                           knownSessionRetention=all(s['retained']==dict(activations=6,segments=6,terminals=6) for s in samples),
                           noPending=all(s['pending']==0 for s in samples)),samples=samples,released=released,
        meaning='18 real speech/cancel activations, actual tracemalloc and Win memory. Tests documented socket-session retention and generation release; not another30min run or universal no-leak proof.')


async def overlap(c):
    import numpy as np
    from tests.manual.v2.verify_server_fix import fixture
    first=await c.activate();await c.play('negative_speech',4);await c.close('finish')
    second=await c.activate()
    pcm,_=fixture('negative_speech')
    samples=np.frombuffer(pcm,dtype=np.int16)
    # Remove only leading silence from the authorized second speech recording.
    # Transport/event order and actual server ASR latency remain untouched.
    frames=samples[:len(samples)//160*160].reshape(-1,160)
    voiced=np.flatnonzero(np.sqrt(np.mean(frames.astype(float)**2,axis=1))>300)
    start=max(0,int(voiced[0])*160-320) if len(voiced) else 0
    c.queue(pcm[start*2:start*2+128000]);await c.wait(lambda:not c.chunks,20)
    if c.view.input.activation_id:await c.close('finish')
    await c.wait(lambda:len(c.backend.send_input_calls)==2)
    finals=c.of_type('transcription.completed');old=next(e for e in finals if e['activationId']==first)
    return dict(checks=dict(twoDistinctFinals=len(finals)==2 and len({e['activationId'] for e in finals})==2,
        oldFinalDuringNewSpeech=old['inputAtReceipt']==dict(activationId=second,phase='segment_active')),
        oldFinal=old,firstId=first,secondId=second,leadingSilenceTrimMs=start/16,
        method='Two actual real-server ASR operations; no reordered/delayed wire events.')


async def admin(c):
    from voice_stt_client.core.settings_service import SettingsError
    ui=c.runtime.settings_ui_session();await ui.load();await ui.load_credential()
    present=ui.view().credential_saved
    before=(dict(c.runtime.settings.server_requested),dict(c.runtime.settings.server_effective),c.runtime.settings.server_revision)
    try:await ui.verify('qualification-deliberately-invalid-key')
    except SettingsError as error:rejected=error.status in (401,403)
    else:rejected=False
    if present:await ui.load_credential();await ui.verify()
    after=(dict(c.runtime.settings.server_requested),dict(c.runtime.settings.server_effective),c.runtime.settings.server_revision)
    result=dict(checks=dict(invalidKeyRejected=rejected,noDefaultMutation=before==after),
        validKey='PASS' if present and ui.view().admin_verified else 'NOT_RUN_MISSING_CREDENTIAL',
        credentialPresent=present)
    ui.invalidate();return result


async def main(args):
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'build').resolve()):raise ValueError('Output must stay in project build')
    out.mkdir(parents=True,exist_ok=False)
    folder=PROFILE_RUNTIME/('technical-rest-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid4().hex[:8])
    (folder/'tmp').mkdir(parents=True)
    os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),VOICESTT_CLIENT_CONFIG=str(folder/'profile.yaml'),TEMP=str(folder/'tmp'),TMP=str(folder/'tmp'))
    from scripts.qualify_v2_real import identity
    before=await asyncio.to_thread(read_info)
    if not check_identity(before,args.expected_server_commit):raise ValueError('Wrong server identity')
    report=dict(result='RUNNING',timeUtc=datetime.now(UTC).isoformat(),pid=os.getpid(),runtimeFolder=str(folder),
        identity=identity(),infoBefore=before,rows=[],scope='Real runtime/models/TLS with controlled PCM/clipboard boundary; no physical/Frozen qualification')
    plan=[]
    if args.group in ('all','settings'):plan += [('settings-'+v,'manual',settings,(v,),None) for v in ('defer','finish','cancel')]
    if args.group in ('all','fault'):plan += [('fault-'+v,'manual',fault,(),v) for v in ('preview','pending')]
    if args.group in ('all','wake'):plan += [('wake-only-controls','wake',wake,(),None)]+[('race-'+str(v),'both',race,(v,),None) for v in (.52,.68)]
    if args.group=='race':plan += [('race-cue','both',cue,(),None),('race-near-before','both',race,('before',),None),('race-near-after','both',race,('after',),None)]
    if args.group in ('all','drain'):plan += [('idle-pending-final-wait','manual',drain,(),'delay')]
    if args.group in ('all','memory'):plan += [('memory-generation-release','manual',memory,(),None)]
    if args.group=='overlap':plan += [('old-final-during-new-speech-'+str(i),'manual',overlap,(),None) for i in range(1,4)]
    if args.group in ('all','admin'):plan += [('admin-guard','manual',admin,(),None)]
    if args.group in ('all','controls'):plan += [('control-'+p+'-'+a+'-'+s,'manual',controls,(p,a,s),None)
        for p in ('waiting','recording','followup') for a in ('refresh','finish','cancel') for s in ('primary','secondary')]
    if args.first_only:plan=plan[:1]
    save(out/'result.json',report)
    for name,mode,operation,values,fault_kind in plan:
        print('START '+name,flush=True);case=RemoteRuntime(folder,name,args.expected_server_commit,mode,fault_kind)
        try:
            async with case:
                if operation is race and values and isinstance(values[0],str):
                    offset=args.race_offset if args.race_offset is not None else report['rows'][0]['wakeOffset'];values=(max(0,offset+(-.08 if values[0]=='before' else .08)),)
                row=await operation(case,*values)
                row.update(name=name,result='PASS_SCOPED' if all(row['checks'].values()) else 'FAIL',
                           pending=case.runtime.session.pending_count)
        except Exception as error:
            row=dict(name=name,result='FAIL',errorType=type(error).__name__,error=str(error))
        row['cleanupErrors']=getattr(case,'cleanup',[])
        row['observations']=str(case.folder/'observed.json')
        report['rows'].append(row);save(out/'result.json',report);print(json.dumps(row),flush=True)
    after=await asyncio.to_thread(read_info);report.update(infoAfter=after,identityStable=before==after,
        result='PASS_SCOPED' if before==after and all(r['result']=='PASS_SCOPED' and not r['cleanupErrors'] for r in report['rows']) else 'FAIL')
    save(out/'result.json',report);return 0 if report['result']=='PASS_SCOPED' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--expected-server-commit',required=True)
    p.add_argument('--group',choices=('all','settings','fault','wake','race','admin','controls','drain','memory','overlap'),default='all')
    p.add_argument('--race-offset',type=float,help='Measured warm wake-admission offset; actual timing is still checked')
    p.add_argument('--first-only',action='store_true');raise SystemExit(asyncio.run(main(p.parse_args())))
