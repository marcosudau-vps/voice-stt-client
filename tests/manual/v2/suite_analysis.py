"""Redacted observations for later agent assessment. Never converts clicks to PASS."""
from collections import Counter
import json


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
