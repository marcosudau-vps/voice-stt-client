import asyncio,os,sys,time,json,hashlib,wave,winsound,uuid
from pathlib import Path
from dataclasses import asdict
from datetime import datetime
import sounddevice as sd
root=Path(__file__).parent
fixtures=root.parent/'autonome-restpruefung-2026-11-23'/'fixtures'
folder=root/('acoustic-'+uuid.uuid4().hex[:8])
folder.mkdir()
os.chdir(folder)
os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),VOICESTT_CLIENT_CONFIG=str(folder/'profile.yaml'))
from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.core.v2_runtime import V2Runtime
from tests.test_text_injector import MockInjectionBackend
target='wss://final.v2.voice-stt-server.marcosudau.com/ws/v2'
pin='e95858e3c010a7e9324b49bb44fee349abe7128a'
report={'scope':'real ReSpeaker capture, Windows speaker acoustic synthetic WAV, corrected source and real V2 server; mock clipboard only','folder':folder.name,'start':datetime.now().astimezone().isoformat(),'cases':[],'events':[],'sessions':[]}
out=root/'acoustic-automation-repeat.json'
def save():
    tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2),encoding='utf8');tmp.replace(out)
def row(name,**kw):
    report['cases'].append(dict(name=name,**kw));save();print(name,kw,flush=True)
async def main():
    config=AppConfig._load_single(DEFAULT_CONFIG_PATH)
    dev=next((i for i,d in enumerate(sd.query_devices()) if 'respeaker' in d['name'].casefold() and d['max_input_channels']>0),None)
    assert dev is not None
    config.server.url=target;config.server.health_url=target.replace('wss:','https:').replace('/ws/v2','/health')
    config.audio.device=dev;config.audio.sample_rate=16000;config.audio.channels=1;config.audio.chunk_duration_ms=40
    config.led.enabled=False;config.feedback.sounds_enabled=False;config.event_stream.enabled=False;config.event_stream.cursor_persistence_enabled=False
    config.history.persistent.db_path=str(folder/'history.sqlite')
    config.history.persistent.store_all=True;config.history.memory.max_entries=100
    config.logging.log_dir=str(folder/'logs');config.logging.observability.store_transcription_content=False;config.logging.observability.store_raw_payload=False
    profile=V2Profile(manual=True,wake_word=True,wake_word_ids=['hey_jarvis'],desired_settings={'activation.followupTimeoutMs':5000})
    config.v2_profile=asdict(profile);config.save(folder/'profile.yaml');config=AppConfig.load(folder/'profile.yaml')
    backend=MockInjectionBackend();rt=V2Runtime(config,backend=backend)
    report['device']={'index':dev,'name':sd.query_devices(dev)['name'],'output':sd.query_devices(sd.default.device[1])['name']}
    old=rt.session.on_accepted
    def accepted(b):
        report['sessions'].append(dict(generation=b.generation,commit=b.accepted.payload.get('serverCommit')))
        if old:old(b)
    rt.session.on_accepted=accepted
    original=rt.session.on_message
    def receive(binding,event):
        original(binding,event)
        data=event.to_mapping() if hasattr(event,'to_mapping') else {}
        kind=str(data.get('type',getattr(event,'type','')))
        if kind in ('activation.started','activation.input_closed','transcription.completed','wakeword.detected','transcription.interim'):
            report['events'].append(dict(kind=kind,activation=data.get('activationId'),segment=data.get('segmentId')))
    rt.session.on_message=receive
    task=asyncio.create_task(rt.run())
    view=lambda:rt.mirror.mirror.view
    async def wait(pred,seconds=15):
        end=time.monotonic()+seconds
        while not pred():
            if task.done():await task;raise RuntimeError('runtime ended')
            if time.monotonic()>end:raise TimeoutError('condition not met')
            await asyncio.sleep(.05)
    async def ready():
        await wait(lambda:rt.is_ready and rt.media.audio_available,30)
        assert rt.session.binding.accepted.payload.get('serverCommit')==pin
    async def play(name):
        path=fixtures/(name+'.wav')
        await asyncio.to_thread(winsound.PlaySound,str(path),winsound.SND_FILENAME|winsound.SND_NODEFAULT)
    async def clear():
        if view().input.activation_id:
            await rt.cancel_dictation()
            await wait(lambda:view().input.activation_id is None,10)
    async def sample(n,tokens):
        await ready();await clear()
        prev=len(backend.send_input_calls)
        result=await rt.press_control('primary')
        assert result.success
        await wait(lambda:bool(view().input.activation_id),8)
        aid=view().input.activation_id
        await asyncio.sleep(.65)
        await play(n)
        await asyncio.sleep(.8)
        if view().input.activation_id==aid:
            await rt.stop_dictation()
        await wait(lambda:view().input.activation_id is None,15)
        await wait(lambda:len(backend.send_input_calls)>prev,35)
        await asyncio.sleep(.35)
        entries=[e for e in rt.history.get_memory_entries() if e.activation_id==aid]
        matches=any(all(t in e.text.casefold() for t in tokens) for e in entries)
        ok=matches and len(entries)==1 and len(backend.send_input_calls)-prev==1
        row(n,match=matches,finals=len(entries),injectionRequests=len(backend.send_input_calls)-prev,pass_=ok)
        return ok
    try:
        await ready();row('ready',pass_=True)
        await rt.controls.set_pause('wakeWord',True)
        await wait(lambda:rt.controls.pause_view.confirmed_wake_word is True)
        tokens=[('blau','bahnhof'),('zitron','tisch'),('bibliothek','neun'),('garten','tulpen'),('fahrrad','garage'),('katze','sofa'),('hund','wiese'),('fenster','offen'),('apfelkuchen',),('bus','rathaus')]
        report['series']=[]
        for attempt in range(1,4):
            results=[]
            report['series'].append(dict(attempt=attempt,results=results))
            for i,t in enumerate(tokens,1):
                n=f'kurz-{i:02d}'
                try:
                    ok=await sample(n,t)
                    results.append(dict(name=n,pass_=ok))
                except Exception as exc:
                    row(n,error=type(exc).__name__)
                    results.append(dict(name=n,pass_=False,error=type(exc).__name__))
                    await clear()
                save()
            if all(r['pass_'] for r in results):
                report['result']='PASS_SCOPED';break
        else:report['result']='FAIL'
        save()
    except BaseException as exc:
        report['error']=type(exc).__name__
    finally:
        winsound.PlaySound(None,0)
        await rt.shutdown();await asyncio.gather(task,return_exceptions=True)
        report['cleanupErrors']=rt.cleanup_errors;report['end']=datetime.now().astimezone().isoformat();save()
        print('DONE',report.get('error'),len(report['cases']),flush=True)
asyncio.run(main())