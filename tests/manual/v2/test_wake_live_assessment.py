import unittest
from copy import deepcopy
from tests.manual.v2.wake_live_assessment import assess

def observations(quiet):
    rows=[dict(type='hello.accepted',monotonic=0,sessionId='s',serverCommit='a'*40)]
    for kind,at in [('activation.started',1),('wakeword.detected',1),('activation.completed',16),('activation.input_closed',16)]:
        rows.append(dict(type='wire',monotonic=at,event=dict(type=kind,sessionId='s',activationId='a',wakeWordId='alexa',reason='timed_out')))
    rows.append(dict(type='metrics',monotonic=16+quiet,audioAvailable=True,injectionQueue=0,media={'sent':500}))
    rows.append(dict(type='operator.command',monotonic=16+quiet+.2,action='stop'))
    return rows

def result(rows,**extra):
    options=dict(expected_commit='a'*40,expected_word='alexa',expected_sound=False,actual_sound=False,human_accepted=True)
    options.update(extra)
    return assess(rows,**options)

class LiveAssessment(unittest.TestCase):
    def test_complete_native_quiet_window_passes(self):
        self.assertEqual(result(observations(7))['result'],'PASS_SCOPED')
    def test_early_stop_is_not_proven_despite_human_acceptance(self):
        value=result(observations(1.875))
        self.assertEqual(value['result'],'NOT_PROVEN')
        self.assertFalse(value['checks']['observedFiveSeconds'])
    def test_second_activation_identity_or_sound_mismatch_fails(self):
        rows=observations(7)
        extra=deepcopy(rows[1]);extra['event']['activationId']='extra'
        self.assertEqual(result(rows+[extra])['result'],'FAIL')
        self.assertEqual(result(rows,expected_commit='b'*40)['result'],'FAIL')
        self.assertEqual(result(rows,actual_sound=True)['result'],'FAIL')
    def test_shutdown_time_cannot_extend_real_audio_observation(self):
        rows=observations(2)
        rows.append(dict(type='desktop.stopped',monotonic=99))
        self.assertEqual(result(rows)['result'],'NOT_PROVEN')
        self.assertEqual(result(observations(7),human_accepted=False)['result'],'NOT_PROVEN')
