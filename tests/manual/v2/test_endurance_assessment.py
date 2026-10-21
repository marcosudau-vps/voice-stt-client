import copy
import unittest
from tests.manual.v2.endurance_assessment import assess,same_build


class Assessment(unittest.TestCase):
    def fixture(self):
        info=dict(schemaVersion=1,protocolVersion=2,serverVersion='2.0.0',serverCommit='pinned',
                  identityStatus='complete',build={'sourceTree':'tree','sourceDirty':False},
                  distribution={'name':'voicestt'},runtime={'krokoVariant':'pro'},serverInstanceId='before')
        after=copy.deepcopy(info);after['serverInstanceId']='after'
        report=dict(result='FAIL',measurementSeconds=1800,infoBefore=info,infoAfter=after,
                    hello=[{'serverCommit':'pinned'}],cleanupErrors=[],rows=[])
        events=[]
        for i in range(100):
            aid=str(i);sid='s'+aid
            report['rows'].append(dict(result='PASS_SCOPED',kind=('manual','alexa','hey_jarvis')[i%3],activationIds=[aid]))
            events.extend([dict(type='activation.started',activationId=aid),
                           dict(type='transcription.completed',activationId=aid,segmentId=sid),
                           dict(type='activation.completed',activationId=aid)])
        return report,events

    def test_instance_change_keeps_build_but_raw_failure_is_retained(self):
        report,events=self.fixture();result=assess(report,events)
        self.assertEqual(result['result'],'PASS_SCOPED');self.assertEqual(result['rawVerdict'],'FAIL')
        self.assertTrue(result['instanceChanged']);self.assertEqual(report['result'],'FAIL')

    def test_build_mismatch_missing_identity_dirty_and_unknown_hello_fail(self):
        report,events=self.fixture()
        for mutation in ('commit','tree','missing','dirty','hello'):
            r=copy.deepcopy(report)
            if mutation=='commit':r['infoAfter']['serverCommit']='other'
            if mutation=='tree':r['infoAfter']['build']['sourceTree']='other'
            if mutation=='missing':del r['infoAfter']['distribution']
            if mutation=='dirty':r['infoAfter']['build']['sourceDirty']=True
            if mutation=='hello':r['hello'][0]['serverCommit']='other'
            with self.subTest(mutation=mutation):self.assertEqual(assess(r,events)['result'],'FAIL')

    def test_no_duplicate_or_short_run_is_promoted(self):
        report,events=self.fixture()
        for mutation in ('short','duplicate','wrong-final','runtime-error'):
            r=copy.deepcopy(report);e=copy.deepcopy(events)
            if mutation=='short':r['measurementSeconds']=1799.999
            if mutation=='duplicate':e.append(e[0])
            if mutation=='wrong-final':e[1]['activationId']='other'
            if mutation=='runtime-error':r['errorType']='TimeoutError'
            with self.subTest(mutation=mutation):self.assertEqual(assess(r,e)['result'],'FAIL')
