import unittest
from copy import deepcopy
from tests.manual.v2.verify_server_fix import check_identity,assess_rearm,cases,observed_event,recovery_cases,manual_boundary_cases
from types import SimpleNamespace


class ProbeChecks(unittest.TestCase):
    def test_wake_variants_are_real_registry_settings_with_strict_types(self):
        from tests.manual.v2.verify_server_fix import wake_settings
        self.assertEqual(wake_settings(.9,3),{'wakeWord.sensitivity':.9,'wakeWord.minConsecutivePredictionFrames':3})
        for threshold,frames in [(True,3),(.9,True),(.9,0),(-1,3),(float('nan'),3)]:
            with self.subTest(threshold=threshold,frames=frames),self.assertRaises(ValueError):wake_settings(threshold,frames)

    def test_watchdog_binds_to_its_segment_and_requires_every_existing_final(self):
        from tests.manual.v2.verify_server_fix import assess_watchdog
        events=[dict(type='activation.started',activationId='a')]
        for sid,start,end in [('one',0,30),('two',30,90)]:
            events.extend([dict(type='segment.recording_started',activationId='a',segmentId=sid,timeSeconds=start),
                dict(type='segment.recording_ended',activationId='a',segmentId=sid,timeSeconds=end)])
        events.extend([dict(type='watchdog.warning',activationId='a',segmentId='two',timeSeconds=85),
            dict(type='activation.input_closed',activationId='a',reason='segment_watchdog_timeout',timeSeconds=90)])
        finals=[dict(activationId='a',segmentId=sid,textLength=3) for sid in ('one','two')]
        self.assertTrue(all(assess_watchdog(events,finals)[0].values()))
        self.assertFalse(all(assess_watchdog(events,finals[:-1])[0].values()))
        changed=deepcopy(events);changed[-2]['segmentId']='one'
        self.assertFalse(all(assess_watchdog(changed,finals)[0].values()))

    def test_continuity_stimulus_preserves_a_real_crop_and_rejects_short_input(self):
        from tests.manual.v2.verify_server_fix import voiced_loop
        from array import array
        pcm=array('h',[0]*16000+[400]*16000).tobytes()
        value,metadata=voiced_loop(pcm)
        self.assertEqual(value,array('h',[400]*16000).tobytes()*65)
        self.assertEqual(metadata['startSample'],16000)
        with self.assertRaises(ValueError):voiced_loop(b'\0'*100)

    def test_manual_boundary_diagnostic_covers_both_words_and_silent_controls(self):
        rows=manual_boundary_cases()
        self.assertEqual(len(rows),6)
        for word in ('alexa','hey_jarvis'):
            self.assertEqual({r[3] for r in rows if r[2]==word},{'cancel','finish','silent_cancel'})
        immediate=manual_boundary_cases(True)
        self.assertEqual(len(immediate),4)
        self.assertEqual({r[3] for r in immediate},{'immediate_cancel','immediate_finish'})

    def test_recovery_matrix_covers_both_real_selected_wake_models(self):
        self.assertEqual(recovery_cases(),[('alexa_pause','pause_recovery','alexa','cancel'),
            ('jarvis_direct','pause_recovery','hey_jarvis','cancel')])
        self.assertEqual(len(cases()),13)

    def test_snapshot_with_its_own_session_id_preserves_both_identities(self):
        record=observed_event(SimpleNamespace(generation=1,session_id='session'),
            SimpleNamespace(type='snapshot',payload={'sessionId':'session','logAccess':'excluded'}),1.25)
        self.assertEqual(record['sessionId'],'session')
        self.assertEqual(record['bindingSessionId'],'session')
        self.assertNotIn('logAccess',record)

    def test_incomplete_wrong_dirty_or_wrong_variant_identity_rejected(self):
        info=dict(schemaVersion=1,protocolVersion=2,identityStatus='complete',serverCommit='a'*40,
            build=dict(sourceTree='b'*40,sourceDirty=False),runtime=dict(krokoVariant='pro'))
        self.assertTrue(check_identity(info,'a'*40))
        self.assertFalse(check_identity(dict(info,serverCommit=None),None))
        self.assertFalse(check_identity(dict(info,serverCommit='unknown'),'unknown'))
        self.assertFalse(check_identity(dict(info,schemaVersion=True),'a'*40))
        for key,value in [('identityStatus','unknown'),('serverCommit','c'*40),('build',dict(sourceTree='b'*40,sourceDirty=True)),
                ('runtime',dict(krokoVariant='community'))]:
            changed=deepcopy(info);changed[key]=value
            self.assertFalse(check_identity(changed,'a'*40))

    def test_extra_wake_activation_wrong_word_or_wrong_closure_rejected(self):
        events=[]
        for aid in ('a','b'):
            events.extend([dict(type='wakeword.detected',wakeWordId='alexa',activationId=aid),
                dict(type='activation.started',activationId=aid),dict(type='activation.input_closed',activationId=aid)])
        self.assertTrue(all(assess_rearm(events,'alexa').values()))
        for extra in [dict(type='activation.started',activationId='c'),dict(type='wakeword.detected',wakeWordId='alexa',activationId='c'),
                dict(type='activation.input_closed',activationId='c')]:
            self.assertFalse(all(assess_rearm(events+[extra],'alexa').values()))
        changed=deepcopy(events);changed[-1]['activationId']='old'
        self.assertFalse(all(assess_rearm(changed,'alexa').values()))
        self.assertFalse(all(assess_rearm(events,'hey_jarvis').values()))

    def test_matrix_retains_both_wake_ids_all_closes_negatives_and_direct_speech(self):
        rows=cases()
        self.assertEqual(len(rows),13)
        self.assertEqual({r[3] for r in rows if r[1]=='rearm'},{'finish','cancel','timeout','reconnect'})
        self.assertEqual({r[2] for r in rows if r[1]=='rearm'},{'alexa','hey_jarvis'})
        self.assertEqual(sum(r[1]=='negative' for r in rows),3)
        self.assertEqual(sum(r[1]=='speech' for r in rows),2)
