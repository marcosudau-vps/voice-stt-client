"""Assessment rejects incomplete or unsafe idle evidence, without hardware."""
from copy import deepcopy
import unittest

from tests.manual.v2.autonomous_rest import assess_idle_samples


def samples():
    rows=[]
    for i,name in enumerate(('initial','manual-paused','both-paused','manual-reconnect-1',
            'manual-reconnect-2','socket-loss','mute-signal','unmute-signal',
            'wake-mask-only','both-paused-final','fresh-runtime')):
        mask = [True,True]
        if name in ('initial','fresh-runtime'): mask=[False,False]
        if name=='manual-paused': mask=[True,False]
        if name=='wake-mask-only': mask=[False,True]
        rows.append(dict(name=name, desired=mask,confirmed=mask,sessionId=str(i),
            generation=i+1,ready=True,followupMs=5000,pending=0,
            sent=i*30,
            audioAvailable=name!='mute-signal'))
    return rows


class IdleAssessment(unittest.TestCase):
    def test_complete_observations_pass(self):
        self.assertEqual(assess_idle_samples(samples(),0,0)['result'],'PASS')

    def test_missing_or_unconfirmed_observations_fail(self):
        for change in ('missing','unconfirmed','old-session','old-generation','no-audio-progress','pending','not-ready','preferences','mute','restart-pause'):
            with self.subTest(change=change):
                rows=deepcopy(samples())
                if change=='missing': rows.pop()
                elif change=='unconfirmed': rows[3]['confirmed']=[None,None]
                elif change=='old-session': rows[3]['sessionId']=rows[2]['sessionId']
                elif change=='old-generation': rows[3]['generation']=rows[2]['generation']
                elif change=='no-audio-progress': rows[3]['sent']=rows[2]['sent']
                elif change=='pending': rows[3]['pending']=1
                elif change=='not-ready': rows[3]['ready']=False
                elif change=='preferences': rows[3]['followupMs']=3000
                elif change=='mute': rows[6]['audioAvailable']=True
                elif change=='restart-pause': rows[-1]['confirmed']=[True,True]
                self.assertEqual(assess_idle_samples(rows,0,0)['result'],'FAIL')

    def test_unexpected_activation_or_paste_fails(self):
        for activation,paste in ((1,0),(0,1)):
            self.assertEqual(assess_idle_samples(samples(),activation,paste)['result'],'FAIL')


if __name__=='__main__': unittest.main()
