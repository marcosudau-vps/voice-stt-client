"""Owned real-server runtime harness. No local server or global server writes.

Real production runtime/services/ASR, authorized WAVs at PortAudio boundary,
controlled clipboard backend. Each case has an isolated profile/history.
"""
import asyncio
from collections import deque
from copy import deepcopy
from dataclasses import asdict
from datetime import UTC,datetime
import json,os,time
from pathlib import Path
from unittest.mock import patch
from tests.manual.v2.suite_plan import PROFILE_RUNTIME,TARGET
from tests.manual.v2.suite_session import prepare_profile,save
from tests.manual.v2.endurance_probe import ReplayStream,devices
from tests.manual.v2.verify_server_fix import fixture,observed_event


def replay_recipe(folder,mode):
    from voice_stt_client.core.config import AppConfig
    config=prepare_profile(folder,TARGET,dict(secondary='finish',both=mode=='both',wake=mode=='wake',sounds=False),0)
    config.audio.sample_rate=16000;config.audio.channels=1;config.audio.chunk_duration_ms=40
    config.event_stream.enabled=False;config.led.enabled=False
    config.v2_profile['desired_settings']['wakeWord.preRollMs']=320
    config.save(folder/'profile.yaml')
    # Runtime deliberately reads AppConfig's migration-source snapshot. After
    # editing a loaded recipe, reload the saved bytes before constructing it.
    return AppConfig.load(folder/'profile.yaml')


class FaultSocket:
    def __init__(self,ws,owner):self.ws,self.owner=ws,owner;self.preview_seen=False
    def __getattr__(self,name):return getattr(self.ws,name)
    async def recv(self):
        if self.preview_seen and self.owner.fault=='preview':
            self.owner.fault=None;self.owner.faults.append(dict(kind='after_actual_preview',seconds=self.owner.seconds()))
            self.ws.transport.abort();raise ConnectionResetError('Owned qualification socket interruption')
        frame=await self.ws.recv()
        value=json.loads(frame) if isinstance(frame,str) else {}
        kind=value.get('type')
        if self.owner.fault=='delay' and kind=='transcription.completed':
            self.owner.fault=None
            self.owner.faults.append(dict(kind='actual_final_delayed_one_second',seconds=self.owner.seconds(),
                activationId=value.get('activationId'),segmentId=value.get('segmentId')))
            await asyncio.sleep(1)
        if self.owner.fault=='preview' and kind=='transcription.interim':self.preview_seen=True
        if self.owner.fault=='pending' and kind=='transcription.completed':
            self.owner.fault=None
            self.owner.faults.append(dict(kind='actual_final_withheld_by_transport_fault',seconds=self.owner.seconds(),
                activationId=value.get('activationId'),segmentId=value.get('segmentId')))
            self.ws.transport.abort();raise ConnectionResetError('Owned qualification socket interruption')
        return frame


class RemoteRuntime:
    def __init__(self,root,name,expected,mode='manual',fault=None):
        self.folder=root/name;self.folder.mkdir()
        self.expected=expected;self.mode=mode;self.fault=fault;self.faults=[]
        self.events=[];self.commands=[];self.hello=[];self.settings=[];self.chunks=deque()
        self.started=time.monotonic();self.stopping=False
    def seconds(self):return round(time.monotonic()-self.started,4)
    async def __aenter__(self):
        os.environ.update(VOICESTT_CLIENT_HOME=str(self.folder/'client'),VOICESTT_CLIENT_CONFIG=str(self.folder/'profile.yaml'))
        from voice_stt_client.core.v2_runtime import V2Runtime
        from voice_stt_client.core.v2_transport import V2TransportConfig
        from voice_stt_client.core.settings_service import SettingsHTTP
        from tests.test_text_injector import MockInjectionBackend
        from websockets.asyncio.client import connect
        self.config=replay_recipe(self.folder,self.mode)
        self.backend=MockInjectionBackend()
        async def connector(*args,**kwargs):return FaultSocket(await connect(*args,**kwargs),self)
        async def persist(profile):
            cfg=deepcopy(self.runtime.config);cfg.v2_profile=asdict(profile)
            await asyncio.to_thread(cfg.save,self.folder/'profile.yaml')
        self.patches=[patch('sounddevice.InputStream',ReplayStream),patch('sounddevice.query_devices',devices),
                      patch('sounddevice.check_input_settings',lambda **kw:None)]
        for p in self.patches:p.start()
        self.runtime=V2Runtime(self.config,backend=self.backend,persist_profile=persist,connector=connector,
            http=SettingsHTTP(TARGET,timeout=180),transport_config=V2TransportConfig(url=TARGET,
                connect_timeout=180,admission_timeout=180,bootstrap_timeout=180))
        previous=self.runtime.session.on_message
        def receive(binding,event):
            previous(binding,event)
            observation=observed_event(binding,event,self.seconds())
            observation['inputAtReceipt']=dict(activationId=self.view.input.activation_id,phase=str(self.view.input.phase))
            self.events.append(observation)
        self.runtime.session.on_message=receive
        old=self.runtime.session.on_accepted
        def accepted(binding):
            if binding.accepted.payload.get('serverCommit')!=self.expected:raise ValueError('Wrong Hello commit')
            self.hello.append(dict(generation=binding.generation,sessionId=binding.session_id,serverCommit=self.expected))
            if old:old(binding)
        self.runtime.session.on_accepted=accepted
        old_completion=self.runtime.session.on_completion
        def completed(value):
            if old_completion:old_completion(value)
            payload=value.command.payload
            self.commands.append(dict(seconds=self.seconds(),type=str(value.command.type),action=payload.get('action'),
                activationId=payload.get('activationId'),accepted=value.ack.accepted,result=str(value.ack.result)))
        self.runtime.session.on_completion=completed
        self.runner=asyncio.create_task(self.runtime.run());self.feed=asyncio.create_task(self.feeder())
        try:await self.ready();return self
        except BaseException:
            await self.__aexit__(None,None,None);raise
    async def feeder(self):
        import numpy as np
        clock=time.monotonic()
        while not self.stopping:
            stream=ReplayStream.latest
            if stream and stream.active:
                data=self.chunks.popleft() if self.chunks else b'\0'*1280
                stream.callback(np.frombuffer(data,dtype=np.int16).reshape(-1,1),len(data)//2,None,None)
            clock+=.04;await asyncio.sleep(max(0,clock-time.monotonic()))
            if time.monotonic()-clock>1:clock=time.monotonic()
    async def wait(self,predicate,timeout=180):
        async with asyncio.timeout(timeout):
            while not predicate():
                if self.runner.done():await self.runner;raise RuntimeError('Runtime ended')
                if self.runtime.session.status.state.value=='blocked':raise RuntimeError('Transport blocked')
                await asyncio.sleep(.005)
    async def ready(self):
        await self.wait(lambda:self.runtime.is_ready and self.runtime.media.audio_available and self.runtime.session.pending_count==0)
        session=self.runtime.session.binding.session_id
        if not any(s['sessionId']==session for s in self.settings):
            self.settings.append(dict(sessionId=session,effective=dict(self.runtime.settings.report().effective),
                triggers=dict(self.runtime.mirror.mirror.view.trigger['configured'])))
    def queue(self,data):
        if self.chunks:raise RuntimeError('Previous fixture still queued')
        self.chunks.extend(data[n:n+1280] for n in range(0,len(data),1280))
    async def play(self,name,seconds=None,until=None):
        data,_=fixture(name)
        if seconds is not None:data=data[:int(seconds*32000)]
        self.queue(data)
        await self.wait(lambda:not self.chunks or (until is not None and until()),25)
        if self.chunks:self.chunks.clear()
    def of_type(self,name):return [e for e in self.events if e['type']==name]
    @property
    def view(self):return self.runtime.mirror.mirror.view
    async def activate(self):
        result=await self.runtime.press_control('primary');assert result.success
        await self.ready();assert self.view.input.activation_id
        return self.view.input.activation_id
    async def close(self,action='finish'):
        result=await (self.runtime.cancel_dictation() if action=='cancel' else self.runtime.stop_dictation())
        assert result.success;await self.wait(lambda:self.view.input.activation_id is None);await self.ready()
    async def __aexit__(self,*exc):
        self.stopping=True;await self.runtime.shutdown();await asyncio.gather(self.runner,return_exceptions=True)
        self.feed.cancel();await asyncio.gather(self.feed,return_exceptions=True)
        for p in reversed(self.patches):p.stop()
        ReplayStream.latest=None
        self.cleanup=list(self.runtime.cleanup_errors)
        save(self.folder/'observed.json',dict(events=self.events,commands=self.commands,hello=self.hello,
            settings=self.settings,faults=self.faults,cleanupErrors=self.cleanup))
