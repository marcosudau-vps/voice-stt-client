import unittest
from tests.manual.v2.native_refresh_probe import owned_releases,assess_native,same_context
from types import SimpleNamespace


class NativeRefreshChecks(unittest.TestCase):
    def test_partial_input_releases_only_own_keys_still_held(self):
        self.assertEqual(owned_releases(0),[])
        self.assertEqual(owned_releases(1),[(0x11,True)])
        self.assertEqual(owned_releases(4),[(0x10,True),(0x11,True)])
        self.assertEqual(owned_releases(6),[])

    def test_native_proof_needs_six_callbacks_in_correct_phases_and_bindings(self):
        calls=[dict(phase=phase,slot='primary',source='WM_HOTKEY',activationId=None if phase=='idle' else aid,sessionId=aid,generation=1)
            for aid in ('a','b') for phase in ('idle','followup_wait','followup_wait')]
        self.assertTrue(assess_native(calls))
        self.assertFalse(assess_native(calls[:-1]))
        for field,value in [('phase','segment_active'),('source','direct_callback'),('activationId','wrong'),('sessionId','other'),('generation',2)]:
            changed=[dict(c) for c in calls];changed[2][field]=value
            self.assertFalse(assess_native(changed))

    def test_native_delivery_cannot_retarget_a_later_context(self):
        view=SimpleNamespace(generation=1,session_id='s',input=SimpleNamespace(phase='followup_wait',activation_id='a'))
        self.assertTrue(same_context((1,'s','followup_wait','a'),view))
        for context in ((2,'s','followup_wait','a'),(1,'other','followup_wait','a'),(1,'s','idle',None),(1,'s','followup_wait','b')):
            self.assertFalse(same_context(context,view))
