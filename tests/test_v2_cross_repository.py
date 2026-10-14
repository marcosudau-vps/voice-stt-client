"""AP-IV2-010 opt-in qualification of immutable client/server product inputs.

Default suite always checks coverage bindings. Real process cases are invoked
by scripts/qualify_v2_pair.py in a fresh interpreter with IV2_PROCESS_GATE=1.
Absent server inputs on that path are errors, never skips. Controlled PCM,
recorder/ASR, clipboard sinks; production runtime and network stay unchanged.
"""
import asyncio
from dataclasses import asdict
import json
import importlib
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.config import AppConfig, DEFAULT_CONFIG_PATH
from voice_stt_client.core.event_models import EventConnectionState
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.core.v2_runtime import V2Runtime
from voice_stt_client.core.v2_transport import V2TransportConfig
from tests.test_v2_runtime_integration import Stream, devices
from tests.test_text_injector import MockInjectionBackend
from tests.integration.v2_process_harness import ROOT, ProcessServer


# Full names are executable bindings, not invented test labels. Rare ordering
# violations and OS failure paths additionally run in deterministic core tests.
SCENARIOS = {
    'SC-01': ['ProcessCases.test_segments_overlap_interim_and_log_dedup'],
    'SC-02': ['ProcessCases.test_wake_only_and_shared_admission_race'],
    'SC-03': ['ProcessCases.test_wake_only_and_shared_admission_race'],
    'SC-04': ['ProcessCases.test_segments_overlap_interim_and_log_dedup'],
    'SC-05': ['tests.test_v2_mirror.Mirror.test_terminal_before_close_does_not_release_foreground'],
    'SC-06': ['tests.test_v2_mirror.Mirror.test_b_start_before_a_close_and_old_final_during_b'],
    'SC-07': ['tests.test_v2_mirror.Mirror.test_discard_and_failure_before_ended_accepted_interim'],
    'SC-08': ['ProcessCases.test_segments_overlap_interim_and_log_dedup',
              'tests.test_v2_results.Results.test_first_discard_failed_empty_then_completed_and_late_interim_never_paste'],
    'SC-09': ['ProcessCases.test_lost_finish_ack_retries_identical_without_second_effect',
              'tests.test_v2_transport.Tracker.test_fake_ack_wait_retry_identical_and_revision_guard'],
    'SC-10': ['ProcessCases.test_device_loss_drain_and_led_isolation'],
    'SC-11': ['ProcessCases.test_client_injected_gap_salvages_buffered_final'],
    'SC-12': ['ProcessCases.test_client_dropped_final_is_incomplete_without_log_paste'],
    'SC-13': ['tests.test_v2_mirror.Mirror.test_generation_session_duplicate_and_unknown_sequence'],
    'SC-14': ['ProcessCases.test_wake_sources_settings_and_bootstrap'],
    'SC-15': ['ProcessCases.test_wake_sources_settings_and_bootstrap'],
    'SC-16': ['ProcessCases.test_wake_sources_settings_and_bootstrap'],
    'SC-17': ['ProcessCases.test_device_loss_drain_and_led_isolation'],
    'SC-18': ['ProcessCases.test_device_loss_drain_and_led_isolation'],
    'SC-19': ['ProcessCases.test_autonomous_terminal_recovery_and_stale_callback'],
    'SC-20': ['ProcessCases.test_autonomous_terminal_recovery_and_stale_callback'],
    'SC-21': ['ProcessCases.test_negative_admission'],
    'SC-22': ['ProcessCases.test_settings_atomicity_and_admin',
              'tests.test_v2_settings_ui.CoreActions.test_auth_revision_validation_persistence_errors_do_not_unlock'],
    'SC-23': ['ProcessCases.test_segments_overlap_interim_and_log_dedup'],
    'SC-24': ['ProcessCases.test_segments_overlap_interim_and_log_dedup'],
    'SC-25': ['tests.test_v2_results.Migration.test_v1_backup_ids_attempts_origin_and_second_start_idempotent',
              'tests.test_v2_results.CrashRecovery.test_real_process_crash_at_five_boundaries_never_auto_reinjects'],
    'SC-26': ['tests.test_v2_controls.Migration.test_defaults_alias_and_explicit_bindings_preserved',
              'tests.test_v2_controls.NativeRegistration.test_partial_failure_restores_old_and_apply_rebind_invalidates_old_ids'],
    'SC-27': ['tests.test_v2_settings_ui.CoreActions.test_cancel_targets_captured_activation_and_separate_drain_loss',
              'tests.test_v2_settings_ui.CoreActions.test_finish_waits_for_actual_completion_before_reconnect',
              'tests.test_v2_settings_ui.CoreActions.test_defer_preserves_foreground_and_background',
              'tests.test_v2_runtime_integration.Runtime.test_reconnect_requires_explicit_open_input_or_drain_decision'],
    'SC-28': ['ProcessCases.test_settings_atomicity_and_admin',
              'tests.test_v2_settings_ui.Credentials.test_create_replace_delete_and_redacted_repr',
              'tests.test_v2_settings_ui.CoreActions.test_store_failure_is_memory_only_and_explicit_error'],
}


async def until(predicate, timeout=15):
    async with asyncio.timeout(timeout):
        while not predicate():
            await asyncio.sleep(.01)


class Coverage(unittest.TestCase):
    def test_all_automated_scenarios_bind_existing_methods(self):
        path = ROOT/'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/REFERENZ/KONTRAKTE/VEKTOREN/client-scenarios.json'
        cases = json.loads(path.read_text(encoding='utf-8-sig'))['scenarios']
        self.assertEqual(set(SCENARIOS), {c['id'] for c in cases if c['owner']=='AP-IV2-010'})
        for names in SCENARIOS.values():
            for name in names:
                name = 'tests.test_v2_cross_repository.'+name if name.startswith('ProcessCases.') else name
                module, cls, method = name.rsplit('.',2)
                self.assertTrue(callable(getattr(getattr(importlib.import_module(module),cls),method)),name)


class _ProcessCases(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.server = await asyncio.to_thread(ProcessServer().start)
        self.addCleanup(self.server.cleanup)
        self.runtime = None
        self.running = None
        self.backend = MockInjectionBackend()
        for target, kwargs in (('sounddevice.query_devices', dict(side_effect=devices)),
                              ('sounddevice.check_input_settings', {}),
                              ('sounddevice.InputStream', dict(new=Stream))):
            active = patch(target, **kwargs); active.start(); self.addCleanup(active.stop)
        self.decisions = []

    async def asyncTearDown(self):
        try:
            if self.runtime:
                await asyncio.wait_for(self.runtime.shutdown(), 15)
                await asyncio.wait_for(self.running, 15)
                self.assertFalse(self.runtime.cleanup_errors)
        finally:
            code = await asyncio.to_thread(self.server.close)
            self.assertEqual(code, 0)
            report = self.server.report()
            if self._testMethodName=='test_autonomous_terminal_recovery_and_stale_callback':
                index=next(i for i,x in enumerate(report['wire']) if x.get('action')=='recovery')
                after=report['wire'][index+1:]
                closed=next(i for i,x in enumerate(after) if x.get('closeCode')==1011)
                self.assertFalse(any(x['direction']=='client_to_server' and x.get('path')=='/ws/v2'
                                     for x in after[:closed]), '1011 must be autonomous')
            output = os.environ.get('IV2_EVIDENCE')
            if output:
                Path(output, self._testMethodName+'.json').write_text(json.dumps(dict(
                    server=report, clientPid=os.getpid(), process=self.server.identity,
                    command=self.server.command), indent=2), encoding='utf8')

    async def start(self, *, manual=True, wake=False, desired=None, connector=None, ack_timeout=5):
        cfg = AppConfig._load_single(DEFAULT_CONFIG_PATH)
        cfg.server.url = self.server.url
        cfg.v2_profile = asdict(V2Profile(manual=manual, wake_word=wake,
            wake_word_ids=['hey_jarvis'] if wake else [], desired_settings=desired or {}))
        cfg._config_source_path = self.server.path/'client.yaml'
        cfg.history.persistent.db_path = str(self.server.path/'history.sqlite')
        cfg.history.persistent.store_all = True
        cfg.event_stream.cursor_path = str(self.server.path/'cursor.json')
        cfg.event_stream.cursor_persistence_enabled = False
        cfg.led.enabled = False
        cfg.text_injection.append_space = False
        cfg.text_injection.paste_delay_ms = 0
        self.runtime = V2Runtime(cfg, backend=self.backend, connector=connector,
            transport_config=V2TransportConfig(url=self.server.url, backoff_initial=.02, backoff_max=.1,
                                              ack_timeout=ack_timeout))
        self.runtime.on_feedback_decision = self.decisions.append
        self.running = asyncio.create_task(self.runtime.run())
        await until(lambda: self.runtime.is_ready and self.runtime.media._gate)
        await until(lambda: self.runtime.media._gate and self.runtime.logs.context.event_state == EventConnectionState.LIVE)
        self.assertEqual(self.runtime.session.binding.accepted.payload['serverCommit'], 'unknown')
        return self.runtime

    async def control(self, action, **fields):
        return await self.server.control(action, self.runtime.session.binding.session_id, **fields)

    async def settled(self):
        await until(lambda: self.runtime.is_ready and self.runtime.media._gate)

    async def activate(self):
        await self.settled()
        reply = await self.runtime.controls.press('primary')
        await until(lambda: self.runtime.mirror.mirror.view.input.activation_id == reply.ack.activationId)
        await self.settled()
        return reply.ack.activationId

    async def record(self):
        before = set(self.runtime.mirror.mirror.view.segments)
        self.runtime.audio._stream.emit()
        await until(lambda: bool(set(self.runtime.mirror.mirror.view.segments)-before))
        return next(iter(set(self.runtime.mirror.mirror.view.segments)-before))

    async def flush(self):
        await self.control('flush')
        await until(lambda: self.runtime.mirror.mirror.view.input.phase == p.InputPhase.FOLLOWUP_WAIT)
        await self.settled()
        jobs = (await self.control('inspect'))['jobs']
        return [j['index'] for j in jobs if j['kind']=='final'][-1]

    async def finish(self):
        await self.runtime.controls.control('finish')
        await until(lambda: self.runtime.mirror.mirror.view.input.phase == p.InputPhase.IDLE)
        await self.settled()

    async def test_segments_overlap_interim_and_log_dedup(self):
        r = await self.start()
        aid = await self.activate(); sid = await self.record()
        await self.control('interim', text='synthetic one')
        await until(lambda: r.mirror.mirror.view.segments[sid].preview is not None)
        version = r.mirror.mirror.view.state_version
        await self.control('interim', text='synthetic two')
        await until(lambda: r.mirror.mirror.view.segments[sid].preview == 'synthetic two')
        self.assertEqual(version, r.mirror.mirror.view.state_version)
        self.assertFalse(self.backend.set_calls)
        first = await self.flush()
        sid2 = await self.record(); second = await self.flush()
        self.assertNotEqual(sid, sid2)
        self.assertEqual(r.mirror.mirror.view.segments[sid2].activation_id, aid)
        await self.finish()
        bid = await self.activate(); await self.record()
        await self.control('complete', index=first, text='synthetic identical final')
        await self.control('complete', index=second, text='synthetic identical final')
        await until(lambda: len(self.backend.set_calls)==2)
        self.assertEqual(r.mirror.mirror.view.input.activation_id, bid)
        self.assertEqual(r.mirror.mirror.view.input.phase, p.InputPhase.SEGMENT_ACTIVE)
        entries = r.get_recent_entries()
        self.assertEqual({e.segment_id for e in entries}, {sid, sid2})
        self.assertEqual({e.activation_id for e in entries}, {aid})
        from voice_stt_client.core.event_protocol import EventProtocolProcessor
        from voice_stt_client.core.event_stream import EventStreamTransport
        from voice_stt_client.core.config import EventStreamConfig
        access=r.logs.context.log_access
        replayed=[]
        async def replayed_event(result):
            replayed.append(result)
            self.assertIsNone(r.feedback.handle_event_stream(result,
                generation=r.session.generation,session_id=r.session.binding.session_id))
            return True
        replay=EventStreamTransport(EventStreamConfig(cursor_persistence_enabled=False),access,
            EventProtocolProcessor(access),on_event=replayed_event)
        replay_task=asyncio.create_task(replay.run())
        try:
            await until(lambda: replay.state==EventConnectionState.LIVE)
            self.assertTrue(any(e.event.event=='transcription.completed' for e in replayed))
        finally:
            await replay.stop(); await asyncio.wait_for(replay_task,10)
        await asyncio.sleep(.1)  # Domain and log-final race has settled.
        self.assertEqual(len(self.backend.set_calls), 2)
        await r.controls.control('cancel')

    async def test_device_loss_drain_and_led_isolation(self):
        r = await self.start()
        aid = await self.activate(); sid = await self.record(); job = await self.flush(); await self.finish()
        bid = await self.activate(); await self.record()
        binding = r.session.binding
        r.media.set_led_available(False)
        self.assertTrue(r.media.audio_available)
        self.assertEqual(r.mirror.mirror.view.input.activation_id, bid)
        r.media.set_device_available(False)
        await until(lambda: r.mirror.mirror.view.input.phase == p.InputPhase.IDLE and not r.mirror.mirror.view.audio_available)
        await self.control('complete', index=job, text='synthetic preserved drain')
        await until(lambda: bool(self.backend.set_calls))
        self.assertIs(r.session.binding, binding)
        self.assertEqual(r.get_recent_entries()[0].activation_id, aid)
        r.media.set_led_available(True); r.media.set_device_available(True)
        await until(lambda: r.media._gate and r.mirror.mirror.view.audio_available)
        self.assertEqual(r.mirror.mirror.view.input.phase, p.InputPhase.IDLE)

    async def test_wake_sources_settings_and_bootstrap(self):
        key = 'activation.followupTimeoutMs'
        r = await self.start(manual=True, wake=True, desired={key:4000})
        aid = await self.activate()
        self.assertFalse((await self.control('wake'))['accepted'])
        self.assertEqual(r.mirror.mirror.view.input.activation_id, aid)
        r.settings.set_desired({key:5000})
        report = await r.settings.apply_session()
        self.assertEqual((report.requested[key], report.effective[key]), (5000,4000))
        await r.controls.control('cancel'); await self.settled()
        aid2 = await self.activate()
        self.assertEqual(r.mirror.mirror.view.activations[aid2].effective_settings[key],5000)
        await r.controls.control('cancel'); await self.settled()
        old = r.session.binding
        await r.controls.set_pause('wakeWord', True)
        await r.session.reconnect(old, 'qualification_reconnect')
        await until(lambda: r.session.binding is not None and r.session.binding is not old and r.is_ready)
        self.assertTrue(r.mirror.mirror.view.trigger['suppressed']['wakeWord'])
        self.assertEqual(r.settings.report().effective[key],5000)
        # NS values remain requested-only even after reconnect.
        revision = r.mirror.mirror.view.settings_revision
        await r.session.request(p.CommandType.SETTINGS_PATCH, baseSettingsRevision=revision,
            changes={'wakeWord.noiseSuppressionEnabled':True,'wakeWord.vadThreshold':.5})
        await r.settings.refresh_session()
        self.assertFalse(r.settings.report().effective['wakeWord.noiseSuppressionEnabled'])
        old = r.session.binding
        await r.session.reconnect(old,'qualification_NS_no_individual_start')
        await until(lambda: r.session.binding is not None and r.session.binding is not old and r.is_ready)
        revision=r.mirror.mirror.view.settings_revision
        await r.session.request(p.CommandType.SETTINGS_PATCH,baseSettingsRevision=revision,
            changes={'wakeWord.noiseSuppressionEnabled':True,'wakeWord.vadThreshold':.5})
        await r.settings.refresh_session()
        self.assertFalse(r.settings.report().effective['wakeWord.noiseSuppressionEnabled'])
        self.assertEqual(r.settings.report().effective['wakeWord.vadThreshold'],0)
        await r.controls.set_pause('manual',True)
        await r.controls.set_pause('wakeWord',False); await self.settled()
        self.assertTrue((await self.control('wake'))['accepted'])
        await until(lambda: r.mirror.mirror.view.input.activation_id is not None)
        self.assertEqual(r.mirror.mirror.view.input.primary_source,'wake_word')
        self.assertIsNone(await r.controls.press('primary'))
        await r.controls.press('secondary'); await self.settled()

    async def test_wake_only_and_shared_admission_race(self):
        r=await self.start(manual=False,wake=True)
        self.assertIsNone(await r.controls.press('primary'))
        # Actual continuous capture path stays available in wake-only idle.
        r.audio._stream.emit()
        self.assertTrue((await self.control('wake'))['accepted'])
        await until(lambda: r.mirror.mirror.view.input.activation_id is not None)
        await self.settled()
        self.assertEqual(r.mirror.mirror.view.input.primary_source,'wake_word')
        await r.controls.press('secondary'); await self.settled()
        self.assertEqual(r.mirror.mirror.view.input.phase,p.InputPhase.IDLE)
        await r.shutdown(); await self.running
        r=await self.start(manual=True,wake=True)
        before=set(r.mirror.mirror.view.activations)
        await asyncio.gather(self.control('wake'),r.controls.press('primary'))
        await until(lambda: r.mirror.mirror.view.input.activation_id is not None)
        await self.settled()
        self.assertEqual(len(set(r.mirror.mirror.view.activations)-before),1)
        self.assertIn(r.mirror.mirror.view.input.primary_source,('manual','wake_word'))
        sid=await self.record(); job=await self.flush()
        await self.control('complete',index=job,text='synthetic race final')
        await until(lambda: len(self.backend.set_calls)==1)
        self.assertEqual(r.get_recent_entries()[0].segment_id,sid)
        await self.finish()

    async def test_settings_atomicity_and_admin(self):
        r = await self.start()
        key = 'activation.followupTimeoutMs'
        before = r.settings.report()
        for changes, revision, result in (({key:5000,'unknown':2},before.session_revision,p.AckResult.SETTINGS_REJECTED),
            ({'activation.segmentWatchdogRefreshMs':30000},before.session_revision,p.AckResult.SETTINGS_REJECTED),
            ({key:5000},999,p.AckResult.SETTINGS_REVISION_CONFLICT)):
            response = await r.session.request(p.CommandType.SETTINGS_PATCH,baseSettingsRevision=revision,changes=changes)
            self.assertEqual(response.ack.result,result)
            await r.settings.refresh_session()
            self.assertEqual(r.settings.report().requested[key],before.requested[key])
        ui = r.settings_ui_session()
        self.assertFalse(ui.view().admin_verified)
        from voice_stt_client.core.settings_service import SettingsError
        with self.assertRaises(SettingsError):
            await ui.verify('synthetic-invalid')
        await ui.verify('synthetic-process-admin')
        self.assertTrue(ui.view().admin_verified)
        self.assertEqual(r.settings.server_revision,0)

    async def test_autonomous_terminal_recovery_and_stale_callback(self):
        r = await self.start(); await self.activate(); sid = await self.record()
        old = r.session.binding; callback = r.audio.on_audio_packet
        await self.control('recovery')
        await until(lambda: r.session.binding is not None and r.session.binding is not old and r.is_ready)
        await self.settled()
        self.assertNotEqual(r.session.binding.session_id,old.session_id)
        self.assertEqual(r.session.pending_count,0)
        callback(b'\0\x40'*640,16000,1,640)
        self.assertFalse(r.mirror.mirror.view.input.activation_id)
        await self.activate(); await self.record()
        await r.controls.control('cancel')

    async def test_lost_finish_ack_retries_identical_without_second_effect(self):
        from websockets.asyncio.client import connect
        class LostAckSocket:
            def __init__(self,ws):
                self.ws=ws; self.command_id=None; self.wires=[]; self.dropped=False; self.closes=[]
            def __getattr__(self,name): return getattr(self.ws,name)
            async def send(self,wire):
                if isinstance(wire,str):
                    value=json.loads(wire)
                    if value.get('action')=='finish':
                        self.command_id=value['commandId']; self.wires.append(wire)
                await self.ws.send(wire)
            async def recv(self):
                while True:
                    wire=await self.ws.recv(); value=json.loads(wire)
                    if value.get('type')=='activation.input_closed': self.closes.append(value)
                    if value.get('type')=='command.ack' and value.get('commandId')==self.command_id and not self.dropped:
                        self.dropped=True; continue
                    return wire
        sockets=[]
        async def connector(*args,**kwargs):
            sock=LostAckSocket(await connect(*args,**kwargs)); sockets.append(sock); return sock
        r=await self.start(connector=connector,ack_timeout=.2)
        await self.activate(); await self.finish()
        sock=sockets[-1]
        self.assertTrue(sock.dropped)
        self.assertEqual(len(sock.wires),2)
        self.assertEqual(sock.wires[0],sock.wires[1])
        self.assertEqual(len(sock.closes),1)
        self.assertEqual(r.session.pending_count,0)

    async def gap(self, drop_final):
        from websockets.asyncio.client import connect
        class FilterSocket:
            def __init__(self, ws): self.ws=ws; self.armed=False; self.dropped=[]
            def __getattr__(self,name): return getattr(self.ws,name)
            async def recv(self):
                while True:
                    wire = await self.ws.recv()
                    value = json.loads(wire) if isinstance(wire,str) else {}
                    target = 'transcription.completed' if drop_final else 'transcription.accepted'
                    if self.armed and value.get('type') == target and not self.dropped:
                        self.dropped.append(value); continue
                    return wire
        sockets=[]
        async def connector(*args,**kwargs):
            sock=FilterSocket(await connect(*args,**kwargs)); sockets.append(sock); return sock
        r = await self.start(connector=connector)
        aid=await self.activate(); sid=await self.record()
        sock=sockets[-1]; sock.armed=True
        job=await self.flush()
        await self.control('complete', index=job, text='synthetic gap final')
        await self.finish(); await self.settled()
        self.assertEqual(len(sock.dropped),1)
        if drop_final:
            self.assertFalse(self.backend.set_calls)
            self.assertTrue(r.mirror.mirror.view.incomplete)
            self.assertIsNone(r.mirror.mirror.view.segments[sid].text)
        else:
            await until(lambda: len(self.backend.set_calls)==1)
            self.assertEqual(r.get_recent_entries()[0].segment_id,sid)
        self.assertEqual(r.mirror.mirror.view.input.phase,p.InputPhase.IDLE)

    async def test_client_injected_gap_salvages_buffered_final(self):
        await self.gap(False)

    async def test_client_dropped_final_is_incomplete_without_log_paste(self):
        await self.gap(True)

    async def test_negative_admission(self):
        from websockets.asyncio.client import connect
        from websockets.exceptions import ConnectionClosed
        hello=p.build_hello(clientVersion='qualification',clientCommit='43759d345b2b88354e4f3b383a4833731621d1e3',
            clientRunId=p.new_id(),manual=True,wakeWord=False,wakeWordIds=[],
            suppressManual=True,suppressWakeWord=True).to_mapping()
        for payload, code in ((b'\0\0',4400),('[]',4400),
                              (json.dumps(dict(hello,supportedProtocolVersions=[1])),4406)):
            async with connect(self.server.url) as ws:
                await ws.send(payload)
                with self.assertRaises(ConnectionClosed) as caught:
                    while True: await asyncio.wait_for(ws.recv(),3)
                self.assertEqual(caught.exception.rcvd.code,code)
        for selected in (['unknown'],['jarvis']):
            request=dict(hello,requestedSession=dict(trigger=dict(manual=False,wakeWord=True),wakeWordIds=selected))
            async with connect(self.server.url) as ws:
                await ws.send(json.dumps(request))
                rejected=json.loads(await asyncio.wait_for(ws.recv(),3))
                self.assertEqual(rejected['type'],'session.rejected')
                with self.assertRaises(ConnectionClosed) as caught:
                    await asyncio.wait_for(ws.recv(),3)
                self.assertEqual(caught.exception.rcvd.code,4409)


# Avoid duplicate loading and optional skips in the ordinary client suite.
if os.environ.get('IV2_PROCESS_GATE') == '1':
    ProcessCases = _ProcessCases
else:
    # Binding validation still resolves method names without executing sockets.
    class ProcessCases:
        pass
    for _name in dir(_ProcessCases):
        if _name.startswith('test_'):
            setattr(ProcessCases, _name, getattr(_ProcessCases,_name))
del _ProcessCases


if __name__ == '__main__':
    unittest.main(verbosity=2)
