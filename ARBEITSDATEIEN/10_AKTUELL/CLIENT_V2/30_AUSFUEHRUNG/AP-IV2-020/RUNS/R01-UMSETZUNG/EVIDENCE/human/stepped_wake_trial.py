"""Preview + explicit Start for every task; client fully stops between tasks.

Real product and microphone only after that task's own click. The next preview
does not start recording. Two separate sessions are intentional; this alone
does not prove the complete same-session M02 or M12 qualification.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from editor_state import owned_editor_path, read_editor_state

CASES = (
    ('jarvis', 'Hey Jarvis der rote Ball liegt auf dem Boden.'),
    ('alexa', 'Alexa die gelbe Tasche steht vor der Tür.'),
    ('manual', 'Dies ist die manuelle Hotkeyprobe.'),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--arm-timeout', type=int, default=1800)
    parser.add_argument('--cases', choices=('jarvis','alexa','manual'), nargs='+', default=['jarvis','alexa'])
    args = parser.parse_args()
    if not 10 <= args.arm_timeout <= 1800:
        parser.error('--arm-timeout must be 10..1800')
    local = Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020'
    state = owned_editor_path(args.state, local)
    args.evidence.mkdir(parents=True, exist_ok=True)
    report_path = args.evidence/'stepped-trial.json'
    if report_path.exists():
        raise FileExistsError('Never overwrite a previous trial')
    report = dict(boundaries=__doc__, result='WAITING_FOR_HUMAN_START', tasks=[],
        helperSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    def save():
        report_path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf8')
    def control(value):
        path = state.parent/'command.json'
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(value), encoding='utf8')
        temporary.replace(path)
        deadline = time.monotonic()+5
        while path.exists():
            if time.monotonic()>deadline:
                raise TimeoutError('Editor did not acknowledge task preview')
            time.sleep(.05)
    save()
    cases = [(case, dict(CASES)[case]) for case in args.cases]
    for index, (case, phrase) in enumerate(cases, 1):
        task_id = args.evidence.name+'-'+case
        prior_start_sequence = read_editor_state(state)['startSequence']
        control(dict(action='prepare', taskId=task_id, clearOnStart=index==1,
            buttonText=f'Aufgabe {index} starten', text=
                f'AUFGABE {index} VON {len(cases)} – NOCH NICHT GESTARTET\n\n'
                f'Diesen Satz vorher in Ruhe lesen:\n„{phrase}“\n\n'
                f'• Wenn bereit: „Aufgabe {index} starten“ klicken.\n'
                '• Auf „CLIENT BEREIT“ warten.\n'
                + ('• Strg+Umschalt+F8 drücken; auf „F8 ANGEKOMMEN“ warten.\n'
                   '• Dann den Satz oben sprechen.\n' if case == 'manual' else
                   '• Dann den Satz ohne Pause zwischen Rufwort und Nutzsatz sprechen.\n') +
                '• DIREKT am Satzende Strg+Umschalt+F9 drücken.\n'
                '• Danach warten. Die nächste Aufgabe braucht wieder einen Klick.'))
        deadline = time.monotonic()+5
        while read_editor_state(state).get('taskId') != task_id:
            if time.monotonic()>deadline:
                raise TimeoutError('Own task preview was not published')
            time.sleep(.05)
        row = dict(taskId=task_id, case=case, phrase=phrase,
                   startSequenceBefore=prior_start_sequence, result='WAITING_FOR_HUMAN_START')
        report['tasks'].append(row)
        save()
        print('TASK_PREPARED', task_id, flush=True)
        child = subprocess.run([sys.executable, str(Path(__file__).with_name('observed_session.py')),
            '--mode','manual' if case == 'manual' else 'wake','--wait-for-editor-state',str(state), '--stop-after','1',
            '--editor-guided','--editor-case',case,'--expected-task-id',task_id,
            '--arm-timeout',str(args.arm_timeout)], timeout=args.arm_timeout+240)
        row['processExitCode'] = child.returncode
        row['result'] = 'PROCESS_COMPLETED_FUNCTIONAL_EVALUATION_PENDING' if child.returncode==0 else 'PROCESS_FAILED'
        active_path = local/'active-observation.json'
        if active_path.exists():
            active = json.loads(active_path.read_text(encoding='utf8'))
            if active.get('taskId') == task_id:
                row['observation'] = active['folder']
                row['observerSha256'] = active['helperSha256']
                row['actualStartSequence'] = active['initialEditorFocus'].get('startSequence')
        save()
        if child.returncode:
            report['result'] = 'STOPPED_AFTER_PROCESS_FAILURE'
            save()
            control(dict(action='instruction',text='TEST GESTOPPT\n• Bitte im Chat melden; keine automatische Wiederholung.'))
            return child.returncode
    report['result'] = 'PROCESSES_COMPLETED_FUNCTIONAL_EVALUATION_PENDING'
    save()
    final = 'FERTIG – TESTCLIENT BEENDET' if len(cases)==1 else 'FERTIG – BEIDE TESTCLIENTS BEENDET'
    control(dict(action='instruction',text=final+'\n• Jetzt bitte im Chat das Ergebnis melden.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
