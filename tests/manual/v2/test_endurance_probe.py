import unittest
from tests.manual.v2.endurance_probe import schedule,new_activation_starts

class EndurancePlan(unittest.TestCase):
    def test_immediate_event_before_ack_is_not_lost_to_timestamp_rounding(self):
        exact_trigger=100.000004
        event=dict(type='activation.started',activationId='new',timeSeconds=round(100.000011,4))
        self.assertLess(event['timeSeconds'],exact_trigger)
        old=dict(type='activation.started',activationId='old',timeSeconds=99)
        self.assertEqual(new_activation_starts([old,event],{'old'}),[event])
    def test_real_gate_plan_is_spread_over_thirty_minutes(self):
        p=schedule();self.assertEqual(len(p),100);self.assertEqual(p[-1]['atSeconds'],1782)
        self.assertEqual({x['kind'] for x in p},{'manual','alexa','hey_jarvis'})
    def test_short_or_overloaded_runs_cannot_be_called_qualification(self):
        for n,s in [(99,1800),(100,1799),(120,1800),(True,1800)]:
            with self.subTest(n=n,s=s),self.assertRaises(ValueError):schedule(n,s)
