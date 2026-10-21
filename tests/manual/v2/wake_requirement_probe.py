"""Session-only Wake threshold/frame comparison; no persistent default changes."""
import argparse
import asyncio
from datetime import UTC,datetime
import hashlib
from pathlib import Path
import json
import sys
from tests.manual.v2.suite_plan import ROOT
from tests.manual.v2.suite_session import save
from tests.manual.v2.verify_server_fix import run_case,read_info,check_identity,wake_settings


def variants():
    return [(0.85,3),(0.90,3),(0.95,5)]


async def main(args):
    from scripts.qualify_v2_real import identity
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'build').resolve()):raise ValueError('Output must remain in project build')
    out.mkdir(parents=True,exist_ok=False)
    before=await asyncio.to_thread(read_info)
    if not check_identity(before,args.expected_server_commit):raise ValueError('Unexpected server identity')
    report=dict(result='RUNNING',timeUtc=datetime.now(UTC).isoformat(),identity=identity(),infoBefore=before,
        helperSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        replayHelperSha256=hashlib.sha256((ROOT/'tests/manual/v2/verify_server_fix.py').read_bytes()).hexdigest(),
        thresholdMeaning='score >= sensitivity, more consecutive qualifying frames increases requirements',
        persistentChanges=False,rows=[],concurrentLoad='Independent automated30min runtime test on same existing server')
    save(out/'result.json',report)
    selected=([(float(args.single[0]),int(args.single[1]))] if args.single else
        [( .75,2),(.85,2)] if args.two_frames else variants())
    for threshold,frames in selected:
        requested=wake_settings(threshold,frames)
        for name,kind,word,close_mode in [('alexa_pause','pause_manual_boundary','alexa','cancel'),
                ('alexa_direct','speech','alexa','natural'),('jarvis_direct','speech','hey_jarvis','natural'),
                ('negative_speech','negative',None,'none')]:
            print(json.dumps(dict(state='START',threshold=threshold,frames=frames,kind=kind,fixture=name)),flush=True)
            result=await run_case(name,kind,word,close_mode,args.expected_server_commit,wake_requirements=requested)
            report['rows'].append(dict(threshold=threshold,frames=frames,**result))
            save(out/'result.json',report)
            print(json.dumps(dict(threshold=threshold,frames=frames,case=result['case'],result=result['result'],error=result.get('error'))),flush=True)
    after=await asyncio.to_thread(read_info)
    report.update(infoAfter=after,identityStable=before==after,
        result='COMPARISON_COMPLETED' if before==after else 'FAIL',
        conclusion='Individual PASS/FAIL and positive misses must be evaluated against unchanged baseline; no claim of causal W02 fix')
    save(out/'result.json',report)
    return 0 if before==after else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--expected-server-commit',required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--two-frames',action='store_true',help='Compare .75/2 and .85/2 when three frames reject a real positive')
    p.add_argument('--single',nargs=2,metavar=('THRESHOLD','FRAMES'),help='One explicit validated session-only comparison')
    args=p.parse_args()
    if args.single and args.two_frames:p.error('--single and --two-frames are mutually exclusive')
    raise SystemExit(asyncio.run(main(args)))
