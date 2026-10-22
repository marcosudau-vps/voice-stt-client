"""Redacted observations for later agent assessment. Never converts clicks to PASS."""
from collections import Counter
import json


def assess_led_fault(before, after, *, led_unavailable, preserve_input=False):
    checks = dict(nativeLedLossObserved=led_unavailable,
        readyBefore=before.get('ready') is True and before.get('audioAvailable') is True,
        observationsPresent=isinstance(after.get('operatorProgress',{}).get('counts'), dict),
        coreReceivedLedIssue='led_unavailable' in after.get('localIssues', []),
        sessionUnchanged=bool(before.get('sessionId')) and before.get('sessionId') == after.get('sessionId'),
        generationUnchanged=before.get('generation') == after.get('generation'),
        audioStillAvailable=after.get('audioAvailable') is True,
        stillReady=after.get('ready') is True,
        noAudioLoss=after.get('operatorProgress',{}).get('audioLost') is False,
        realAudioProgress=after.get('media',{}).get('sent',0) >= before.get('media',{}).get('sent',0)+50,
        activationPreserved=(bool(before.get('activationId')) and before.get('activationId')==after.get('activationId'))
            if preserve_input else not after.get('operatorProgress',{}).get('counts',{}).get('activation.started',0))
    return dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
        beforeSent=before.get('media',{}).get('sent'), afterSent=after.get('media',{}).get('sent'),
        scope='Controlled native LED-only transport stop with real microphone/server; '+
            ('open input preserved' if preserve_input else 'idle only')+'; no physical cable or frozen claim')


def summarize(folder):
    path = folder/'events.jsonl'
    records = [json.loads(line) for line in path.read_text(encoding='utf8').splitlines()] if path.exists() else []
    wire = [row['event'] for row in records if row['type'] == 'wire']
    kinds = Counter(row['type'] for row in wire)
    completed = [row for row in records if row['type'] == 'command.completed']
    metrics = [row for row in records if row['type'] == 'metrics']
    return dict(evaluation='NOT_PROVEN_PENDING_AGENT_REVIEW', wireEvents=dict(kinds),
        activationIds=sorted({row['activationId'] for row in wire if row.get('activationId')}),
        commands=completed, metricSamples=len(metrics),
        maxTasks=max((row['tasks'] for row in metrics), default=None),
        maxInjectionQueue=max((row['injectionQueue'] for row in metrics), default=None),
        maxPrivateBytes=max((row['memory']['privateBytes'] for row in metrics), default=None),
        boundaries='Counts are observations, not complete M-case verdicts. Human and identity evidence require evaluation.')
