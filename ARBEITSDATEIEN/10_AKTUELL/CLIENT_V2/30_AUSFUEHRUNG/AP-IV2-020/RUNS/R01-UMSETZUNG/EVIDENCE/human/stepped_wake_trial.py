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

from editor_state import owned_editor_path, read_editor_state, operator_started

CASES = (
    ('jarvis', 'Hey Jarvis der rote Ball liegt auf dem Boden.'),
    ('alexa', 'Alexa die gelbe Tasche steht vor der Tür.'),
    ('manual', 'Dies ist die manuelle Hotkeyprobe.'),
)


def requested(state, task_id, actions):
    """Old attempts can never abort, repeat or accept a new attempt."""
    return state.get('requestAction') if (state.get('requestTaskId') == task_id
        and state.get('requestAction') in actions) else None


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
        # Keep only previously accepted task text when repeating a later task.
        baseline = '' if index == 1 else read_editor_state(state)['testText']
        attempt = 0
        while True:
            attempt += 1
            task_id = f'{args.evidence.name}-{index}-{case}-attempt-{attempt:03d}'
            prior = read_editor_state(state)
            control(dict(action='prepare', taskId=task_id, restoreOnStart=baseline, phrase=phrase,
                buttonText=f'Aufgabe {index} starten – Versuch {attempt}', text=
                    f'AUFGABE {index} VON {len(cases)} · VERSUCH {attempt} · NOCH NICHT GESTARTET\n'
                    '• Satz im grünen Feld in Ruhe lesen; dann Start klicken.\n'
                    '• Auf „CLIENT BEREIT“ warten.\n'
                    + ('• Strg+Umschalt+F8 drücken; auf „F8 ANGEKOMMEN“ warten.\n'
                       '• Dann den grünen Satz sprechen.\n' if case == 'manual' else
                       '• Den grünen Satz ohne Pause zwischen Rufwort und Nutzsatz sprechen.\n') +
                    '• Direkt am Satzende Strg+Umschalt+F9 drücken.\n'
                    '• Misslungen? „Versuch abbrechen“ oder danach „Aufgabe wiederholen“.\n'
                    '• Nach dem Versuch selbst Wiederholen oder Übernehmen wählen.'))
            row = dict(taskId=task_id, case=case, phrase=phrase, attempt=attempt,
                startSequenceBefore=prior['startSequence'], result='WAITING_FOR_HUMAN_START')
            report['tasks'].append(row)
            save()
            print('TASK_PREPARED', task_id, flush=True)
            # Reading time has no task timer and starts no client or microphone.
            while not operator_started(read_editor_state(state), task_id):
                time.sleep(.1)
            row['actualStartSequence'] = read_editor_state(state)['startSequence']
            row['result'] = 'RUNNING'
            save()
            child = subprocess.Popen([sys.executable, str(Path(__file__).with_name('observed_session.py')),
                '--mode','manual' if case == 'manual' else 'wake','--wait-for-editor-state',str(state),
                '--stop-after','1','--editor-guided','--editor-case',case,'--expected-task-id',task_id,
                '--arm-timeout',str(args.arm_timeout)])
            aborted = False
            while child.poll() is None:
                aborted = aborted or requested(read_editor_state(state), task_id, ('abort',)) == 'abort'
                time.sleep(.1)
            row['processExitCode'] = child.returncode
            aborted = aborted or requested(read_editor_state(state), task_id, ('abort',)) == 'abort'
            row['result'] = ('ABORTED_BY_OPERATOR' if aborted else
                'PROCESS_COMPLETED_FUNCTIONAL_EVALUATION_PENDING' if child.returncode==0 else 'PROCESS_FAILED')
            active_path = local/'active-observation.json'
            if active_path.exists():
                active = json.loads(active_path.read_text(encoding='utf8'))
                if active.get('taskId') == task_id:
                    row['observation'] = active['folder']
                    row['observerSha256'] = active['helperSha256']
            current = read_editor_state(state)
            row['editorAfterAttempt'] = {k:current[k] for k in ('characters','sha256','startSequence')}
            save()  # Record every attempt before the next start can clear text.
            if aborted:
                row['operatorDecision'] = 'repeat_after_abort'
                save()
                continue  # Only preview; another explicit Start is required.
            control(dict(action='review', taskId=task_id,
                acceptText='Versuch übernehmen / Testblock abschließen' if index==len(cases) else 'Versuch übernehmen / nächste Aufgabe vorbereiten',
                text='VERSUCH BEENDET – TESTCLIENT AUS\n'
                     '• Satz ansehen: passt er?\n'
                     '• Bei Problemen „Aufgabe wiederholen“ wählen; danach wieder selbst Start klicken.\n'
                     '• Sonst „Versuch übernehmen“ wählen. Keine automatische Folgeaufgabe.\n'
                     '• Die technische Bewertung erfolgt separat anhand der Diagnosen.'))
            while True:
                decision = requested(read_editor_state(state), task_id, ('repeat','accept'))
                if decision:
                    break
                time.sleep(.1)
            row['operatorDecision'] = decision
            save()
            if decision == 'accept':
                break
    report['result'] = 'PROCESSES_COMPLETED_FUNCTIONAL_EVALUATION_PENDING'
    save()
    final = 'FERTIG – TESTCLIENT BEENDET' if len(cases)==1 else 'FERTIG – BEIDE TESTCLIENTS BEENDET'
    control(dict(action='complete',text=final+'\n• Jetzt bitte im Chat das Ergebnis melden.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
