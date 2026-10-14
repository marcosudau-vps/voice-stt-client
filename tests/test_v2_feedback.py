"""AP090 phase parity, origin guards, bounded feedback and actual Qt outputs."""
from copy import deepcopy
from dataclasses import replace, FrozenInstanceError
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from types import SimpleNamespace

import yaml
from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.activation_mirror import ActivationMirror, Reduction, MirrorState
from voice_stt_client.core.config import DEFAULT_CONFIG_PATH, OverlayConfig
from voice_stt_client.core.event_models import CanonicalEventType as C, EventOrigin, EventConnectionState, FeedbackSource
from voice_stt_client.core.feedback_mapping import FeedbackMappingConfig, LedVerb, migrate_v2_feedback_mapping
from voice_stt_client.core.feedback_reducer import FeedbackEngine
from voice_stt_client.core.v2_feedback import V2FeedbackConnection
from voice_stt_client.core.observability.normalizer import from_client_event
from voice_stt_client.core.observability.adapters.client_events import ClientEventEmitter
from tests.test_v2_mirror import snapshot, msg, pending, A, B, S
from tests.test_event_normalizer import log_result


def mapping():
    return FeedbackMappingConfig.from_mapping(yaml.safe_load(DEFAULT_CONFIG_PATH.read_text(encoding='utf-8'))['feedback_mappings'])


class DomainFeedback(unittest.TestCase):
    def setUp(self):
        self.engine = FeedbackEngine(mapping())
        self.m = ActivationMirror()
        self.seq = 0
        self.last = self.engine.handle_reduction(self.m.begin(1, snapshot(), 10))

    def send(self, kind, **values):
        self.seq += 1
        self.reduction = self.m.consume(1, msg(kind, self.seq, **values), 10)
        self.last = self.engine.handle_reduction(self.reduction)
        return self.last

    def start(self, aid=A, source='manual', sequence=1):
        return self.send(p.EventType.ACTIVATION_STARTED, aid=aid, primarySource=source, activationSequence=sequence)

    def phase(self, phase, aid=A):
        return self.send(p.EventType.PHASE_CHANGED, aid=aid, inputPhase=phase,
                         deadlineAtUnixMs=100000, remainingMs=10000)

    def test_all_manual_wake_phases_have_identical_ui_and_persistent_rules(self):
        from voice_stt_client.ui.presentation import presentation_for_v2_snapshot
        for phase in p.InputPhase:
            projections=[]
            for source in ('manual', 'wake_word'):
                self.setUp()
                if phase != p.InputPhase.IDLE:
                    self.start(source=source)
                    self.phase(phase)
                decision=self.last[0]
                projections.append((presentation_for_v2_snapshot(decision.snapshot, now=10), self.engine._v2_persistent_rule))
            self.assertEqual(projections[0],projections[1],phase)

    def test_activation_cue_is_source_neutral_and_wake_detection_is_diagnostic(self):
        rules=[]
        for source in ('manual','wake_word'):
            self.setUp()
            decisions=self.start(source=source)
            rules.append(decisions[1].rule)
            if source=='wake_word':
                self.assertEqual(len(self.send(p.EventType.WAKE_DETECTED)),1)
        self.assertEqual(rules[0],rules[1])

    def test_idle_with_multiple_drains_remains_trigger_ready(self):
        reduction=self.m.consume(1,snapshot(1,1,pending=[pending(A),pending(B,seq=2)]),10)
        value=self.engine.handle_reduction(reduction)[0].snapshot
        self.assertEqual(value.pending_count,2)
        self.assertTrue(value.manual_available)
        self.assertEqual(value.phase,p.InputPhase.IDLE)

    def test_old_complete_cannot_change_new_recording_or_persistent_led(self):
        self.start()
        self.phase('segment_active')
        self.send(p.EventType.RECORDING_STARTED)
        self.send(p.EventType.INPUT_CLOSED, acceptedSegmentCount=1)
        self.start(B,sequence=2)
        self.phase('segment_active',B)
        self.send(p.EventType.RECORDING_STARTED,aid=B,sid=p.new_id(),segment_sequence=2)
        decisions=self.send(p.EventType.COMPLETED,text='synthetic A final')
        self.assertEqual(decisions[0].snapshot.activation_id,B)
        self.assertEqual(decisions[0].state.value,'recording')
        self.assertTrue(all(c.is_event for c in decisions[1].rule.led))
        self.assertEqual(decisions[1].rule.sound.cue.value,'complete')
        from voice_stt_client.ui.presentation import presentation_for_feedback_decision
        self.assertIsNone(presentation_for_feedback_decision(decisions[1],operating_mode='wake_word'))

    def test_old_complete_cannot_change_new_followup(self):
        self.start()
        self.send(p.EventType.RECORDING_STARTED)
        self.send(p.EventType.INPUT_CLOSED,acceptedSegmentCount=1)
        self.start(B,sequence=2)
        self.phase('followup_wait',B)
        value=self.send(p.EventType.COMPLETED,text='synthetic')[0].snapshot
        self.assertEqual(value.phase,p.InputPhase.FOLLOWUP_WAIT)
        self.assertEqual(value.activation_id,B)

    def test_domain_log_replay_and_repeated_reduction_complete_once(self):
        self.start()
        self.send(p.EventType.RECORDING_STARTED)
        decisions=self.send(p.EventType.COMPLETED,text='synthetic')
        self.assertEqual(sum(d.rule.sound is not None for d in decisions),1)
        for origin in (EventOrigin.LIVE,EventOrigin.REPLAY):
            self.assertIsNone(self.engine.handle_event_stream(log_result('transcription.completed',origin=origin),generation=1,session_id=self.m.session_id))
        self.assertFalse(hasattr(self.engine, 'handle_stt_fallback'))
        replay=self.engine.handle_reduction(self.reduction)
        self.assertEqual(len(replay),1)
        self.assertFalse(replay[0].rule.led)

    def test_late_interim_and_recording_cannot_revive_terminal_preview_or_cue(self):
        self.start()
        self.send(p.EventType.COMPLETED,text='synthetic')
        self.send(p.EventType.INTERIM,text='late interim')
        self.assertFalse(self.last[0].snapshot.previews)
        self.assertEqual(len(self.send(p.EventType.RECORDING_STARTED)),1)

    def test_replace_preview_displaytext_and_missing_stabilization(self):
        self.start()
        self.send(p.EventType.INTERIM,text='first')
        self.send(p.EventType.INTERIM,text='replacement',displayText='display')
        self.assertEqual(self.last[0].snapshot.previews[0].text,'display')
        self.send(p.EventType.INTERIM,text='minimal')
        self.assertEqual(self.last[0].snapshot.previews[0].text,'minimal')

    def test_terminal_only_removes_its_own_preview(self):
        self.start()
        self.send(p.EventType.INTERIM,text='A')
        self.send(p.EventType.INPUT_CLOSED,acceptedSegmentCount=1)
        self.start(B,sequence=2)
        sid=p.new_id()
        self.send(p.EventType.INTERIM,aid=B,sid=sid,segment_sequence=2,text='B')
        self.send(p.EventType.COMPLETED,text='A final')
        self.assertEqual([(x.segment_id,x.text) for x in self.last[0].snapshot.previews],[(sid,'B')])

    def test_cancelled_activation_does_not_announce_late_completed(self):
        self.start()
        self.send(p.EventType.INTERIM,text='A')
        self.send(p.EventType.ACTIVATION_CANCELLED)
        self.assertFalse(self.last[0].snapshot.previews)
        self.assertEqual(len(self.send(p.EventType.COMPLETED,text='forbidden')),1)

    def test_watchdog_repeated_new_event_ids_emit_one_warning(self):
        self.start()
        first=self.send(p.EventType.WATCHDOG_WARNING,remainingMs=30000,deadlineAtUnixMs=900000)
        again=self.send(p.EventType.WATCHDOG_WARNING,remainingMs=29000,deadlineAtUnixMs=900000)
        self.assertEqual(len(first),2)
        self.assertEqual(len(again),1)
        self.assertEqual(first[1].rule.led[0].config['duration_ms'],30000)

    def test_relative_countdown_does_not_mutate_mirror_or_issue_commands(self):
        self.start()
        self.phase('waiting_first_speech')
        value=self.last[0].snapshot
        before=self.m.view
        self.assertEqual(value.remaining_ms(11),9000)
        self.assertEqual(value.remaining_ms(-999999),10000)
        self.assertEqual(value.remaining_ms(999999),0)
        self.assertEqual(self.m.view,before)

    def test_background_warning_is_silent(self):
        self.start()
        self.send(p.EventType.INPUT_CLOSED,acceptedSegmentCount=1)
        self.start(B,sequence=2)
        self.assertEqual(len(self.send(p.EventType.WATCHDOG_WARNING)),1)

    def test_watchdog_countdown_ends_with_foreground_recording_phase(self):
        self.start()
        self.phase('segment_active')
        self.send(p.EventType.WATCHDOG_WARNING)
        self.assertIsNotNone(self.last[0].snapshot.watchdog)
        self.phase('followup_wait')
        self.assertIsNone(self.last[0].snapshot.watchdog)
        self.assertEqual(self.last[0].snapshot.remaining_ms(11),9000)

    def test_resync_incomplete_device_and_log_have_distinct_diagnostics(self):
        self.start()
        self.seq+=1  # real event gap
        self.send(p.EventType.RECORDING_STARTED)
        self.assertIn('resync',self.last[0].snapshot.diagnostics)
        value=self.engine.handle_reduction(self.m.disconnect(1))[0].snapshot
        self.assertIn('incomplete',value.diagnostics)
        self.assertIn('log_unavailable',value.diagnostics)
        self.assertIn('device_off',self.engine.handle_reduction(Reduction(replace(self.m.view,audio_available=False)))[0].snapshot.diagnostics)

    def test_local_faults_secondary_and_repeated_without_warning_loop(self):
        self.start()
        self.phase('segment_active')
        for kind in (C.CLIENT_SOUND_FAILED,C.CLIENT_LED_UNAVAILABLE,C.CLIENT_INJECTION_FAILED):
            for _ in range(2):
                decision=self.engine.handle_local(kind,generation=1,session_id=self.m.session_id,details={'accessToken':'synthetic-secret'})
                self.assertEqual(decision.snapshot.phase,p.InputPhase.SEGMENT_ACTIVE)
                self.assertIsNone(decision.rule.sound)
        self.assertEqual(set(decision.snapshot.diagnostics)&{'sound_failed','led_unavailable','injection_failed'},
                         {'sound_failed','led_unavailable','injection_failed'})

    def test_key_reject_and_history_fault_visible_and_explicitly_clearable(self):
        value=self.engine.update_v2_issues(('key_rejected','history_unavailable'))
        from voice_stt_client.ui.presentation import presentation_for_v2_snapshot
        text=presentation_for_v2_snapshot(value.snapshot,now=10).tooltip
        self.assertIn('Admin-Schlüssel abgelehnt',text)
        self.assertIn('Verlauf nicht verfügbar',text)
        self.assertNotIn('key_rejected',self.engine.update_v2_issues().snapshot.diagnostics)
        with self.assertRaises(ValueError): self.engine.update_v2_issues(('raw-secret',))

    def test_log_connection_loss_does_not_change_recording(self):
        self.start()
        self.phase('segment_active')
        for connection in EventConnectionState:
            result=self.engine.update_connection(connection,stt_ready=True,generation=1,session_id=self.m.session_id)
            self.assertEqual(result.source,FeedbackSource.DOMAIN)
            self.assertEqual(result.snapshot.phase,p.InputPhase.SEGMENT_ACTIVE)
            self.assertIsNone(result.rule.sound)

    def test_suppression_combinations_are_visible(self):
        for manual,wake in ((True,False),(False,True),(True,True),(False,False)):
            self.setUp()
            data=snapshot().to_mapping()
            data['trigger']['suppressed'].update(manual=manual,wakeWord=wake)
            data['trigger']['effective'].update(manual=not manual,wakeWord=not wake)
            result=self.engine.handle_reduction(self.m.consume(1,p.parse_snapshot(data),10))[0].snapshot
            self.assertEqual(result.manual_suppressed,manual)
            self.assertEqual(result.wake_suppressed,wake)

    def test_reconnect_resets_preview_and_old_generation_cannot_return(self):
        self.start()
        self.send(p.EventType.INTERIM,text='old')
        old=self.reduction
        self.engine.handle_reduction(self.m.disconnect(1))
        self.assertEqual(self.engine.handle_reduction(old),())
        data=snapshot().to_mapping(); data['sessionId']=p.new_id()
        fresh=self.engine.handle_reduction(self.m.begin(2,p.parse_snapshot(data),20))[0]
        self.assertFalse(fresh.snapshot.previews)
        self.assertEqual(self.engine.handle_reduction(old),())

    def test_wrong_session_reduction_and_status_are_rejected(self):
        wrong=Reduction(replace(self.m.view,session_id=p.new_id()))
        self.assertEqual(self.engine.handle_reduction(wrong),())
        self.assertFalse(self.engine.update_connection(EventConnectionState.LIVE,stt_ready=True,generation=1,session_id='other').publish)

    def test_older_state_version_with_same_sequence_cannot_replace_projection(self):
        self.start()
        self.phase('segment_active')
        stale=Reduction(replace(self.m.view,state_version=self.m.view.state_version-1))
        self.assertEqual(self.engine.handle_reduction(stale),())

    def test_snapshot_counts_do_not_generate_missing_final_cues(self):
        self.start()
        self.send(p.EventType.INPUT_CLOSED,acceptedSegmentCount=1)
        result=self.engine.handle_reduction(self.m.consume(1,snapshot(self.seq,self.seq),10))
        self.assertEqual(len(result),1)
        self.assertTrue(result[0].snapshot.incomplete)
        self.assertIsNone(result[0].rule.sound)

    def test_frozen_snapshot_redacts_repr_and_bounds_display_text(self):
        self.start()
        self.send(p.EventType.INTERIM,text='sensitive-synthetic'+'x'*20000)
        value=self.last[0].snapshot
        self.assertNotIn('sensitive-synthetic',repr(value))
        self.assertEqual(len(value.previews[0].text),16384)
        with self.assertRaises(FrozenInstanceError): value.phase=p.InputPhase.IDLE

    def test_one_shot_and_observation_memory_bounded(self):
        self.engine.dedupe_limit=32
        for _ in range(150): self.send(p.EventType.TRIGGER_SUPPRESSED)
        self.assertLessEqual(len(self.engine.state.seen_event_ids),32)
        self.assertLessEqual(len(self.engine.state.seen_correlations),32)
        self.assertLessEqual(len(self.engine._v2_observed),32)

    def test_callback_chain_order_failure_isolation_and_close(self):
        order=[]
        fake=SimpleNamespace(on_reduction=lambda r: order.append('prior'))
        port=V2FeedbackConnection(fake,self.engine)
        def output(d): order.append('feedback'); raise RuntimeError('synthetic')
        port.on_decision=output
        fake.on_reduction(Reduction(self.m.view))
        self.assertEqual(order,['prior','feedback'])
        self.assertEqual(self.engine.adapter_failures,1)
        port.close(); fake.on_reduction(Reduction(self.m.view))
        self.assertEqual(order[-1],'prior')

    def test_uuid_command_hooks_and_secrets_at_actual_normalizer(self):
        records=[]
        class Ingress:
            def event(self,kind,**kwargs):
                records.append(from_client_event(kind,instance_id='synthetic-client',**kwargs))
        self.engine=FeedbackEngine(mapping(),on_observation=ClientEventEmitter(Ingress(),component='core.feedback').system)
        self.engine.handle_reduction(Reduction(self.m.view))
        self.start()
        self.send(p.EventType.RECORDING_STARTED,accessToken='synthetic-token',secret='synthetic-secret')
        command=p.new_id()
        self.send(p.EventType.INPUT_CLOSED,acceptedSegmentCount=1,causedByCommandId=command)
        self.assertTrue(all(x is not None for x in records))
        self.assertTrue(any(x.segment_id==S and x.activation_id==A and x.session_id==self.m.session_id for x in records))
        self.assertTrue(any(x.command_id==command for x in records))
        self.assertNotIn('synthetic-token',repr(records))
        self.assertNotIn('synthetic-secret',repr(records))

    def test_failed_observability_cannot_fail_domain_output(self):
        class Ingress:
            def event(self,*a,**kw): raise RuntimeError('synthetic')
        self.engine=FeedbackEngine(mapping(),on_observation=ClientEventEmitter(Ingress(),component='core.feedback').system)
        self.assertEqual(len(self.start()),2)


class MappingMigration(unittest.TestCase):
    def test_observability_uuid_storage_filter_and_mixed_sort_pagination(self):
        from voice_stt_client.core.observability.storage.sqlite import SQLiteLogStore
        from voice_stt_client.core.observability.query.local import LocalLogProvider
        from voice_stt_client.core.observability.query.base import QueryFilter, ProviderState
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'diagnostic.sqlite'
            store=SQLiteLogStore(path); self.assertTrue(store.open().ok)
            values=[None,2,10,S,p.new_id()]
            records=[from_client_event('client.feedback.decision',channel='system',instance_id='synthetic',segment_id=v) for v in values]
            self.assertTrue(all(x is not None for x in records))
            self.assertEqual(store.write_batch(records)[0],5)
            store.close()
            provider=LocalLogProvider(path)
            page=provider.query(QueryFilter(segment_id=S))
            self.assertEqual(len(page.records),1); self.assertEqual(page.records[0].segment_id,S)
            for descending in (True,False):
                items=[]; cursor=None
                for _ in range(10):
                    page=provider.query(QueryFilter(sort_by='segment_id',sort_descending=descending),cursor=cursor,limit=1)
                    self.assertEqual(page.status.state,ProviderState.AVAILABLE)
                    items.extend(x.segment_id for x in page.records)
                    cursor=page.next_cursor
                    if cursor is None: break
                expected=[None,2,10,*sorted(values[3:])]
                self.assertEqual(items,list(reversed(expected)) if descending else expected)

    def test_custom_rules_retained_reported_and_new_keys_win(self):
        raw={'schema_version':2,'events':{
            C.CLIENT_HOTKEY_ACCEPTED.value:{'sound':{'cue':'start','volume':.3},'led':{'set_state':'custom_user_effect','config':{'speed':2}}},
            C.SERVER_WAKE_WORD_DETECTED.value:{'sound':{'cue':'wake_word','volume':.7}},
            C.SERVER_INPUT_FOLLOWUP.value:{'led':{'clear_state':'primary'}}}}
        original=deepcopy(raw)
        value=FeedbackMappingConfig.from_mapping(raw)
        self.assertEqual(raw,original)
        self.assertEqual(value.rule_for(C.SERVER_ACTIVATION_STARTED),value.rule_for(C.CLIENT_HOTKEY_ACCEPTED))
        self.assertEqual(value.rule_for(C.SERVER_INPUT_FOLLOWUP).led[0].verb,LedVerb.CLEAR_STATE)
        self.assertEqual(value.rule_for(C.SERVER_WAKE_WORD_DETECTED).sound.volume,.7)
        self.assertTrue(value.migration_report)

    def test_roundtrip_idempotent_and_schema1_requires_visible_repair(self):
        original=mapping()
        self.assertEqual(migrate_v2_feedback_mapping(original).to_mapping(),original.to_mapping())
        self.assertEqual(FeedbackMappingConfig.from_mapping(original.to_mapping()).to_mapping(),original.to_mapping())
        with self.assertRaisesRegex(ValueError,'schema_version 1'):
            FeedbackMappingConfig.from_mapping({'schema_version':1,'events':{}})

    def test_profile_file_migration_preserves_user_feedback_bytes_in_backup(self):
        from voice_stt_client.core.v2_profile import migrate_config_file
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'config.yaml'
            raw={'feedback_mappings':mapping().to_mapping(),'feedback':{'sounds_enabled':False,'start_sound':'custom.wav'},'session':{'mode':'hotkey'}}
            original=yaml.safe_dump(raw).encode(); path.write_bytes(original)
            migrate_config_file(path)
            after=yaml.safe_load(path.read_text())
            self.assertEqual(after['feedback_mappings'],raw['feedback_mappings'])
            self.assertEqual(after['feedback'],raw['feedback'])
            self.assertEqual(path.with_name('config.yaml.pre-v2.bak').read_bytes(),original)
            migrated=path.read_bytes(); migrate_config_file(path)
            self.assertEqual(path.read_bytes(),migrated)


class QtOutput(unittest.TestCase):
    """Each Qt case owns a fresh lifetime, as in the qualified AP080 suite."""
    def __init__(self,methodName='runTest'):
        super().__init__(methodName)
        if os.environ.get('VOICE_STT_FEEDBACK_QT_CHILD')!='1':
            setattr(self,methodName,self._isolated)

    def _isolated(self):
        child=subprocess.run([sys.executable,'-X','faulthandler','-W','error','-m','unittest',
            'tests.test_v2_feedback.QtOutput.'+self._testMethodName,'-v'],
            cwd=Path(__file__).resolve().parents[1],env=dict(os.environ,VOICE_STT_FEEDBACK_QT_CHILD='1',QT_QPA_PLATFORM='offscreen',PYTHONUTF8='1'),
            capture_output=True,text=True,encoding='utf-8',timeout=30)
        self.assertEqual(child.returncode,0,child.stdout+child.stderr)
        self.assertIn('Ran 1 test',child.stderr)

    def setUp(self):
        if os.environ.get('VOICE_STT_FEEDBACK_QT_CHILD')!='1': return
        from PySide6.QtWidgets import QApplication
        from voice_stt_client.ui.overlay import TranscriptOverlay
        from voice_stt_client.ui.tray import TrayController
        from voice_stt_client.ui.feedback import V2FeedbackOutput
        self.app=QApplication.instance() or QApplication([])
        self.overlay=TranscriptOverlay(OverlayConfig())
        self.tray=TrayController(on_toggle=lambda:None,on_reinsert_last=lambda:None,on_reinsert_entry=lambda x:None,on_request_history=lambda:None,on_quit=lambda:None)
        self.sounds=[]; self.leds=[]
        self.port=V2FeedbackOutput(tray=self.tray,overlay=self.overlay,
            sound=SimpleNamespace(play=self.sounds.append),led=SimpleNamespace(submit=lambda calls,**kw:self.leds.append((calls,kw))))
        self.addCleanup(self.port.close); self.addCleanup(self.overlay.close); self.addCleanup(self.tray.tray.hide)
        self.domain=DomainFeedback(); self.domain.setUp()

    def apply(self,decisions):
        for decision in decisions: self.port.apply(decision)

    def test_foreground_preview_survives_background_final_and_plain_text(self):
        d=self.domain
        self.apply(d.start())
        self.apply(d.send(p.EventType.INTERIM,text='A'))
        self.apply(d.send(p.EventType.INPUT_CLOSED,acceptedSegmentCount=1))
        self.apply(d.start(B,sequence=2)); self.apply(d.phase('segment_active',B))
        sid=p.new_id()
        self.apply(d.send(p.EventType.INTERIM,aid=B,sid=sid,segment_sequence=2,text='<b>B plain</b>'))
        self.apply(d.send(p.EventType.COMPLETED,text='old A'))
        self.assertEqual(self.overlay.label.text(),'<b>B plain</b>')
        self.assertIn('Sprache wird aufgenommen',self.overlay.status_label.text())
        self.assertEqual(self.tray.status_action.text(),'Sprache wird aufgenommen')
        from PySide6.QtCore import Qt
        self.assertEqual(self.overlay.label.textFormat(),Qt.TextFormat.PlainText)

    def test_terminal_removes_preview_and_late_interim_cannot_restore_it(self):
        d=self.domain
        self.apply(d.start()); self.apply(d.send(p.EventType.INTERIM,text='synthetic'))
        self.assertEqual(self.overlay.label.text(),'synthetic')
        self.apply(d.send(p.EventType.DISCARDED,reason='empty_final'))
        self.assertEqual(self.overlay.label.text(),'')
        self.apply(d.send(p.EventType.INTERIM,text='late'))
        self.assertEqual(self.overlay.label.text(),'')

    def test_independent_sound_led_failures_and_duplicate_output(self):
        def fail(*args,**kwargs): raise RuntimeError('synthetic-secret')
        self.port.sound=SimpleNamespace(play=fail); self.port.led=SimpleNamespace(submit=fail)
        failures=[]; self.port.failure.connect(failures.append)
        decisions=self.domain.start(); self.apply(decisions); self.apply(decisions)
        self.assertEqual(set(failures),{'sound_failed','led_unavailable'})
        self.assertEqual(len(failures),2)
        self.assertEqual(self.tray.status_action.text(),'Wartet auf Sprache')

    def test_queued_foreign_thread_delivers_only_on_main_and_close_invalidates(self):
        decisions=self.domain.start()
        main=threading.get_ident(); touched=[]
        original=self.port.tray.update_feedback_decision
        self.port.tray.update_feedback_decision=lambda d:(touched.append(threading.get_ident()),original(d))
        thread=threading.Thread(target=lambda:[self.port.decision_received.emit(d) for d in decisions])
        thread.start(); thread.join()
        self.assertEqual(touched,[])
        self.app.processEvents()
        self.assertTrue(touched); self.assertTrue(all(t==main for t in touched))
        before=len(touched); self.port.close(); self.port.decision_received.emit(decisions[0]); self.app.processEvents()
        self.assertEqual(len(touched),before)

    def test_stale_generation_snapshot_is_rejected(self):
        old=self.domain.start()[0]
        value=replace(old,snapshot=replace(old.snapshot,generation=2,session_id=p.new_id(),revision=1))
        self.port.apply(value)
        self.port.apply(old)
        self.assertEqual(self.port._identity[0],2)

    def test_countdown_clock_drift_never_finishes_or_hides_preview(self):
        d=self.domain
        self.apply(d.start()); self.apply(d.phase('waiting_first_speech'))
        self.overlay._alert_timer.stop(); self.overlay._clock=lambda:999999
        self.overlay._update_v2_status()
        self.assertIn('0.0 s',self.overlay.status_label.text())
        self.assertEqual(d.m.view.input.phase,p.InputPhase.WAITING_FIRST_SPEECH)


    def test_diagnostic_uuid_context_filter_and_mixed_sort_match_sqlite(self):
        from PySide6.QtCore import Qt
        from voice_stt_client.ui.logs.log_filter_bar import LogFilterBar
        from voice_stt_client.ui.logs.log_table_model import LogTableModel
        from voice_stt_client.core.observability.storage.sqlite import SQLiteLogStore
        from voice_stt_client.core.observability.query.local import LocalLogProvider
        from voice_stt_client.core.observability.query.base import QueryFilter
        bar=LogFilterBar(); self.addCleanup(bar.close)
        bar.apply_context(segment_id=S)
        self.assertEqual(bar.current_filter().segment_id,S)
        bar.segment_edit.setText('2'); self.assertEqual(bar.current_filter().segment_id,2)
        bar.segment_edit.setText('-'); self.assertIsNone(bar.current_filter().segment_id)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'viewer.sqlite'
            store=SQLiteLogStore(path); self.assertTrue(store.open().ok)
            values=[None,2,10,S,p.new_id()]
            store.write_batch([from_client_event('client.feedback.decision',channel='system',instance_id='synthetic',segment_id=v) for v in values])
            store.close(); provider=LocalLogProvider(path); model=LogTableModel()
            bar.apply_context(segment_id=S)
            self.assertEqual(provider.query(bar.current_filter()).records[0].segment_id,S)
            for descending,order in ((False,Qt.SortOrder.AscendingOrder),(True,Qt.SortOrder.DescendingOrder)):
                page=provider.query(QueryFilter(sort_by='segment_id',sort_descending=descending))
                model.set_records(page.records); model.set_sort('segment_id',order)
                self.assertEqual([x.segment_id for x in model.records()],[x.segment_id for x in page.records])


if __name__=='__main__': unittest.main()
