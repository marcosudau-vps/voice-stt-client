"""Launch the reusable, isolated Windows V2 manual test UI."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
from urllib.parse import urlsplit
import yaml


def isolated_profile(path):
    data=yaml.safe_load(path.read_text(encoding='utf8'))
    server=data.get('server',{})
    for key,scheme in (('url','ws'),('health_url','http')):
        value=urlsplit(server.get(key,''))
        if (value.scheme != scheme or value.hostname not in ('127.0.0.1','localhost','::1')
                or value.port != 18020 or value.username or value.password or value.query or value.fragment):
            return False
    return True


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases',nargs='+',choices=('manual','jarvis','alexa'),default=['manual'])
    parser.add_argument('--prepare-seconds',type=int,default=8)
    parser.add_argument('--evidence',type=Path)
    parser.add_argument('--self-check',action='store_true')
    parser.add_argument('--preview',action='store_true',help='UI preview only; no client, microphone or model')
    args=parser.parse_args()
    if not 0 <= args.prepare_seconds <= 30:parser.error('--prepare-seconds must be 0..30')
    if args.self_check or args.preview:
        from tests.manual.v2.human_test_editor import run
        return run(args.self_check,preview=args.preview)
    local=Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020'
    for mode in {'manual' if case=='manual' else 'wake' for case in args.cases}:
        path=local/f'client-{mode}.yaml'
        if not path.exists():
            parser.error('Isolated profile missing. See tests/manual/v2/README.md; no V1 profile is used.')
        if not isolated_profile(path):
            parser.error('Only isolated loopback profiles on port18020 are allowed; no external server is contacted.')
    evidence=args.evidence or local/'trials'/(datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8])
    if evidence.exists():parser.error('Use a new evidence directory for every block')
    editor=subprocess.Popen([sys.executable,'-u','-m','tests.manual.v2.human_test_editor'],stdout=subprocess.PIPE,text=True)
    announcement=editor.stdout.readline()
    if not announcement:
        raise RuntimeError('Test editor did not start')
    state=Path(json.loads(announcement)['state'])
    command=[sys.executable,'-u','-m','tests.manual.v2.stepped_wake_trial','--state',str(state),
        '--evidence',str(evidence),'--prepare-seconds',str(args.prepare_seconds),'--cases',*args.cases]
    child=subprocess.Popen(command)
    print(json.dumps(dict(editorState=str(state),evidence=str(evidence))),flush=True)
    while child.poll() is None:
        if editor.poll() is not None:
            # The editor defers Close while a trial is running/aborting. Once
            # closed here the controller only waits for another operator click.
            child.terminate()
            child.wait(timeout=5)
            return 1
        time.sleep(.2)
    return child.returncode


if __name__=='__main__':
    raise SystemExit(main())
