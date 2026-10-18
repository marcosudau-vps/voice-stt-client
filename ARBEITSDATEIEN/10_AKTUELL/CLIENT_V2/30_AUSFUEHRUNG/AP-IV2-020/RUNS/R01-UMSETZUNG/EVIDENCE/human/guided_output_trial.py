"""Separate operator starts for native paste and the guided Wake phrases.

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
from editor_state import owned_editor_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    local = Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020'
    state = owned_editor_path(args.state, local)
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
        '• Danach den Sprachtest mit eigenem Knopf starten.\n'
        '• Bitte im Testfenster bleiben; nicht in den Chat wechseln.'))
    helpers = {name: hashlib.sha256((folder/name).read_bytes()).hexdigest()
               for name in ('guided_output_trial.py','probe_native_editor.py',
                            'observed_session.py','editor_state.py')}
    native = subprocess.run([sys.executable, str(folder/'probe_native_editor.py'),
        '--state', str(state), '--out', str(result_path), '--append-space',
        '--guided-continuation'], timeout=650)
    if native.returncode or not result_path.exists():
        raise RuntimeError('Native attempt did not complete; no retry and no speech client started')
    proof = json.loads(result_path.read_text(encoding='utf8'))
    if proof['result'] != 'PASS':
        raise RuntimeError('Native attempt failed; no retry and no speech client started')
    command(dict(action='prepare', buttonText='Sprachtest starten', text=
        'EINFÜGEPROBE BESTANDEN – SPRACHTEST NOCH NICHT GESTARTET\n'
        '• In Ruhe bereitmachen.\n'
        '• Erst „Sprachtest starten“ klicken.\n'
        '• Auf „CLIENT BEREIT“ warten, dann nur den angezeigten Satz sprechen.\n'
        '• Nach jedem Satz Strg+Umschalt+F9 drücken.'))
    voice = subprocess.run([sys.executable, str(folder/'stepped_wake_trial.py'),
        '--state',str(state), '--evidence',str(args.evidence/'wake-tasks')], timeout=4100)
    output = dict(nativeResult='PASS', voiceProcessExitCode=voice.returncode,
                  helperSha256=helpers, nativeEvidence=result_path.name,
                  boundaries=__doc__, voiceFunctionalResult='PENDING_TRACE_AND_HUMAN_EVALUATION')
    (args.evidence/'guided-output-trial.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf8')
    return voice.returncode


if __name__=='__main__':
    raise SystemExit(main())
