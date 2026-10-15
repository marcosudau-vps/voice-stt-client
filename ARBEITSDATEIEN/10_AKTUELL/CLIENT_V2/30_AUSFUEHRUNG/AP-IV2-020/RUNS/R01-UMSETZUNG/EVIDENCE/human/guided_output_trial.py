"""One operator click: real native UX01 paste, then two guided Wake phrases.

Uses the unchanged product via existing test observers, never runs two clients
at once. Guarded own target only, bounded children, no automatic paste retry.
Full raw editor text stays local; reports retain explicit helper identities.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    local = Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020'
    state = args.state.resolve()
    if not state.is_relative_to((local/'editors').resolve()):
        parser.error('Only own diagnostic editor allowed')
    if not args.evidence.is_dir():
        parser.error('Evidence directory must already exist')
    folder = Path(__file__).resolve().parent
    result_path = args.evidence/'native-editor-spaced.json'
    if result_path.exists():
        raise FileExistsError('Never overwrite a completed native attempt')
    control = state.parent/'command.json'
    def command(value):
        control.write_text(json.dumps(value), encoding='utf8')
    command(dict(action='prepare', buttonText='Testblock starten', text=
        'KURZER TESTBLOCK\n• „Testblock starten“ klicken.\n'
        '• Die Einfügeprobe läuft automatisch.\n'
        '• Danach erscheint jeweils genau eine Sprechaufgabe.\n'
        '• Bitte im Testfenster bleiben; nicht in den Chat wechseln.'))
    helpers = {name: hashlib.sha256((folder/name).read_bytes()).hexdigest()
               for name in ('guided_output_trial.py','probe_native_editor.py','observed_session.py')}
    native = subprocess.run([sys.executable, str(folder/'probe_native_editor.py'),
        '--state', str(state), '--out', str(result_path), '--append-space',
        '--guided-continuation'], timeout=650)
    if native.returncode or not result_path.exists():
        raise RuntimeError('Native attempt did not complete; no retry and no speech client started')
    proof = json.loads(result_path.read_text(encoding='utf8'))
    if proof['result'] != 'PASS':
        raise RuntimeError('Native attempt failed; no retry and no speech client started')
    command(dict(action='clear'))
    deadline = time.monotonic()+3
    while json.loads(state.read_text(encoding='utf8'))['characters']:
        if time.monotonic()>deadline:
            raise TimeoutError('Editor clear was not observed')
        time.sleep(.05)
    voice = subprocess.run([sys.executable, str(folder/'observed_session.py'),
        '--mode','wake','--wait-for-editor-state',str(state),
        '--stop-after','2','--editor-guided'], timeout=310)
    output = dict(nativeResult='PASS', voiceProcessExitCode=voice.returncode,
                  helperSha256=helpers, nativeEvidence=result_path.name,
                  boundaries=__doc__, voiceFunctionalResult='PENDING_TRACE_AND_HUMAN_EVALUATION')
    (args.evidence/'guided-output-trial.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf8')
    return voice.returncode


if __name__=='__main__':
    raise SystemExit(main())
