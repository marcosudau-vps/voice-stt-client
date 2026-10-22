"""Offline qualification of one contiguous run; retain the raw runner verdict.

A server instance may change during recovery. Exact build identity must not.
No time or successful activations from separate attempts are combined.
"""
from collections import Counter


def same_build(before, after):
    required=('schemaVersion','protocolVersion','serverVersion','serverCommit',
              'identityStatus','build','distribution','runtime')
    return (all(k in before and k in after for k in required)
            and before.get('identityStatus')=='complete'
            and before.get('build',{}).get('sourceDirty') is False
            and all(before[k]==after[k] for k in required))


def assess(report, events):
    rows=report.get('rows',[])
    starts=[e for e in events if e['type']=='activation.started']
    finals=[e for e in events if e['type']=='transcription.completed']
    completed=[e for e in events if e['type']=='activation.completed']
    started_ids=[e.get('activationId') for e in starts]
    final_ids=[(e.get('activationId'),e.get('segmentId')) for e in finals]
    row_ids=[v for r in rows for v in r.get('activationIds',[])]
    before=report.get('infoBefore',{});after=report.get('infoAfter',{})
    checks=dict(
        continuousMeasurement=report.get('measurementSeconds',0)>=1800,
        exactly100SuccessfulRows=len(rows)==100 and all(r.get('result')=='PASS_SCOPED' for r in rows),
        mixedSources=Counter(r.get('kind') for r in rows)==dict(manual=34,alexa=33,hey_jarvis=33),
        exactly100DistinctStarts=len(starts)==100 and len(set(started_ids))==100 and None not in started_ids,
        allRowsBoundToStarts=Counter(row_ids)==Counter(started_ids),
        exactly100DistinctFinals=len(finals)==100 and len(set(final_ids))==100 and all(all(v) for v in final_ids),
        allFinalsBoundToStarts=Counter(e.get('activationId') for e in finals)==Counter(started_ids),
        allActivationsCompleted=Counter(e.get('activationId') for e in completed)==Counter(started_ids),
        sameQualifiedBuild=same_build(before,after),
        allHelloCommitsMatch=bool(report.get('hello')) and all(h.get('serverCommit')==before.get('serverCommit') for h in report.get('hello',[])),
        cleanShutdown=report.get('cleanupErrors')==[],
        noRuntimeException='errorType' not in report)
    return dict(result='PASS_SCOPED' if all(checks.values()) else 'FAIL',checks=checks,
        rawVerdict=report.get('result'),instanceChanged=before.get('serverInstanceId')!=after.get('serverInstanceId'),
        method='Offline assessment of this single run; exact build stable, instance change allowed during recovery',
        fullPhysicalM12='NOT_PROVEN')
