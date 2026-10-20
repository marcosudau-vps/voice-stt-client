import unittest
from copy import deepcopy
from tests.manual.v2.verify_server_fix import check_identity,assess_rearm,cases,observed_event
from types import SimpleNamespace


class ProbeChecks(unittest.TestCase):
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
