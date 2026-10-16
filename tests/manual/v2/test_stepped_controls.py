"""Controller regressions with explicit fake editor/process boundaries.

No microphone, model, Windows input or real M-case qualification.
"""
from copy import deepcopy
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tests.manual.v2 import stepped_wake_trial as trial


class SteppedControls(unittest.TestCase):
    def test_request_from_previous_attempt_cannot_control_new_attempt(self):
        state = dict(requestTaskId='old', requestAction='abort')
        self.assertIsNone(trial.requested(state, 'new', ('abort',)))
        self.assertEqual(trial.requested(state, 'old', ('abort',)), 'abort')
        self.assertIsNone(trial.requested(state, 'old', ('accept',)))

    def test_repeat_abort_accept_have_distinct_attempts_and_explicit_starts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_path = root/'editor/state.json'
            state_path.parent.mkdir()
            output = root/'evidence'
            state = dict(taskId=None, startSequence=0, operatorReady=False,
                         foreground=True, editorHasFocus=True, testText='', phase='preparing')
            previews, children = [], []
            ticks = 0
            sequence = ('repeat','abort','accept')

            def read(_):
                state['timeUtc'] = datetime.now(UTC).isoformat()
                state['characters'] = len(state['testText'])
                state['sha256'] = hashlib.sha256(state['testText'].encode()).hexdigest()
                return deepcopy(state)

            def tick(_):
                nonlocal ticks
                command = state_path.parent/'command.json'
                if command.exists():
                    value = json.loads(command.read_text())
                    command.unlink()
                    if value['action']=='prepare':
                        previews.append(value)
                        state.update(taskId=value['taskId'], operatorReady=False,phase='preview')
                        ticks = 0
                    elif value['action']=='review':
                        state.update(phase='review',operatorReady=False)
                    elif value['action']=='complete':
                        state.update(phase='done',operatorReady=False)
                    return
                ticks += 1
                if state['phase']=='preview' and ticks == 3:
                    # Fake a deliberate click after reading, never on prepare.
                    self.assertEqual(len(children), len(previews)-1)
                    state.update(operatorReady=True,phase='running',
                        startSequence=state['startSequence']+1,testText=previews[-1]['restoreOnStart'])
                elif state['phase']=='review':
                    state.update(requestTaskId=state['taskId'],requestAction=sequence[len(children)-1],phase='preparing')
                elif state['phase']=='running' and sequence[len(children)-1]=='abort':
                    state.update(requestTaskId=state['taskId'],requestAction='abort',operatorReady=False,phase='stopping')

            owner = self
            class FakeChild:
                def __init__(self, argv):
                    owner.assertTrue(state['operatorReady'])
                    if children:
                        owner.assertTrue(children[-1].ended, 'Previous process must end before repeat')
                    owner.assertEqual(state['testText'], '', 'Repeat restores task baseline; no duplicate old attempt')
                    owner.assertIn(state['taskId'], argv)
                    self.ended = False
                    self.first_poll = True
                    self.returncode = None
                    children.append(self)
                    state['testText'] = 'Agreed simulated output '

                def poll(self):
                    if self.first_poll and sequence[len(children)-1]=='abort':
                        self.first_poll = False
                        return None
                    self.ended = True
                    self.returncode = 0
                    return 0

            argv = ['trial','--state',str(state_path),'--evidence',str(output),'--cases','manual']
            with patch.object(trial.sys,'argv',argv), patch.dict(trial.os.environ,LOCALAPPDATA=str(root)), \
                 patch.object(trial,'owned_editor_path',side_effect=lambda p,_:p), \
                 patch.object(trial,'read_editor_state',side_effect=read), \
                 patch.object(trial.time,'sleep',side_effect=tick), \
                 patch.object(trial.subprocess,'Popen',FakeChild):
                self.assertEqual(trial.main(),0)
            report = json.loads((output/'stepped-trial.json').read_text())
            rows = report['tasks']
            self.assertEqual(len(rows),3)
            self.assertEqual(len({r['taskId'] for r in rows}),3)
            self.assertEqual([r['actualStartSequence'] for r in rows],[1,2,3])
            self.assertEqual([r['operatorDecision'] for r in rows],['repeat','repeat_after_abort','accept'])
            self.assertEqual(rows[1]['result'],'ABORTED_BY_OPERATOR')
            self.assertEqual(report['result'],'PROCESSES_COMPLETED_FUNCTIONAL_EVALUATION_PENDING')
            self.assertEqual(state['phase'],'done')
            self.assertTrue(all(p['phrase']=='Dies ist die manuelle Hotkeyprobe.' for p in previews))


if __name__=='__main__':
    unittest.main()
