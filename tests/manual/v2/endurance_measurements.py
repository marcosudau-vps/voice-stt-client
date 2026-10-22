"""Recompute safe timing/resource summaries from one saved endurance run."""
import argparse,json,statistics
from collections import Counter
from pathlib import Path
from tests.manual.v2.suite_plan import ROOT
from tests.manual.v2.suite_session import save


def distribution(values):
    values=sorted(values)
    if not values:return None
    return dict(min=min(values),max=max(values),median=statistics.median(values),
                p95=values[min(len(values)-1,int(len(values)*.95))],p95Method='higher order statistic')


def summarize(report,events,metrics):
    if not metrics:raise ValueError('No resource samples')
    warm=[m for m in metrics if m['timeUtc']>=report['measurementStartedAtUtc']]
    if not warm:raise ValueError('No post-bootstrap resource samples')
    finals=[e for e in events if e['type']=='transcription.completed']
    final_latency=[];preview_latency=[]
    for final in finals:
        bound=[e for e in events if (e.get('sessionId'),e.get('activationId'),e.get('segmentId'))==
               (final['sessionId'],final['activationId'],final['segmentId'])]
        starts=[e for e in bound if e['type']=='segment.recording_started']
        ends=[e for e in bound if e['type']=='segment.recording_ended']
        interims=[e for e in bound if e['type']=='transcription.interim']
        if ends:final_latency.append(final['timeSeconds']-ends[-1]['timeSeconds'])
        if starts and interims:preview_latency.append(interims[0]['timeSeconds']-starts[0]['timeSeconds'])
    def memory(samples):
        return {k:dict(first=samples[0][k],last=samples[-1][k],min=min(m[k] for m in samples),
                       max=max(m[k] for m in samples)) for k in ('privateBytes','workingSetBytes')}
    return dict(measurementSeconds=report.get('measurementSeconds'),
        activationKinds=Counter(r['kind'] for r in report['rows']),eventCounts=Counter(e['type'] for e in events),
        helloCount=len(report.get('hello',[])),samples=len(metrics),
        tasksRange=[min(m['tasks'] for m in metrics),max(m['tasks'] for m in metrics)],
        warmTasksRange=[min(m['tasks'] for m in warm),max(m['tasks'] for m in warm)],
        memory=memory(metrics),warmMemory=memory(warm),maxPending=max(m['pendingCommands'] for m in metrics),
        maxRetainedActivations=max(m['activationsRetained'] for m in metrics),
        maxRetainedTerminals=max(m['resultTerminalsRetained'] for m in metrics),
        finalAfterRecordingStoppedSeconds=distribution(final_latency),
        firstPreviewAfterRecordingStartedSeconds=distribution(preview_latency),
        slotDurationSeconds=distribution([r['elapsedSeconds'] for r in report['rows']]),
        wakeScoreById={word:distribution([e['score'] for e in events if e['type']=='wakeword.detected'
                        and e.get('wakeWordId')==word]) for word in ('alexa','hey_jarvis')},
        lastMedia=metrics[-1]['media'],lastCapture=metrics[-1]['capture'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--folder',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    folder=args.folder.resolve();out=args.output.resolve()
    if not folder.is_relative_to(ROOT.resolve()) or not out.is_relative_to((ROOT/'build').resolve()):
        raise ValueError('Read project data only; write summary to project build')
    report=json.loads((folder/'result.json').read_text(encoding='utf8'))
    def lines(name):return [json.loads(s) for s in (folder/name).read_text(encoding='utf8').splitlines()]
    save(out,summarize(report,lines('events.jsonl'),lines('metrics.jsonl')))


if __name__=='__main__':main()
