"""Progress follows observed events; clocks/clicks never manufacture proof."""
import unittest
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
from tests.manual.v2.suite_progress import ObservedProgress, guide_progress
from tests.manual.v2.suite_session import save


class LiveProgress(unittest.TestCase):
    def test_finish_moves_after_activation_without_operator_next(self):
        progress = ObservedProgress()
        progress.observe('wire', event=dict(type='activation.started', generation=1, activationId='a'))
        value = guide_progress('finish', progress.snapshot(), 0)
        self.assertEqual(value['active'], 3)
        self.assertIn(2, value['confirmed'])
        self.assertNotIn(3, value['confirmed'])

    def test_transient_phases_between_polls_and_real_finish_are_retained(self):
        progress = ObservedProgress()
        for kind in ('activation.started','segment.recording_started','segment.recording_ended'):
            progress.observe('wire', event=dict(type=kind,generation=1,activationId='a'))
        progress.observe('control.received', slot='secondary', ready=True, phase='followup')
        self.assertEqual(guide_progress('finish',progress.snapshot(),0)['active'],4)
        progress.observe('wire',event=dict(type='activation.input_closed',generation=1,reason='finished'))
        progress.observe('wire',event=dict(type='activation.completed',generation=1))
        self.assertEqual(guide_progress('finish',progress.snapshot(),0)['active'],4)
        value=guide_progress('finish',progress.snapshot(),1)
        self.assertEqual(value['active'],5)
        self.assertIn(3,value['confirmed'])

    def test_timeout_without_f9_does_not_check_finish_instruction(self):
        progress=ObservedProgress()
        for kind in ('activation.started','segment.recording_started','activation.input_closed','activation.completed'):
            progress.observe('wire',event=dict(type=kind,generation=1,reason='timed_out'))
        value=guide_progress('finish',progress.snapshot(),1)
        self.assertNotIn(3,value['confirmed'])
        self.assertIn('F9',value['notice'])

    def test_followup_waits_for_first_segment_then_second_finish(self):
        progress=ObservedProgress()
        progress.observe('wire',event=dict(type='activation.started',generation=1))
        self.assertEqual(guide_progress('followup',progress.snapshot(),0)['active'],2)
        progress.observe('wire',event=dict(type='segment.recording_ended',generation=1))
        self.assertEqual(guide_progress('followup',progress.snapshot(),0)['active'],3)

    def test_stale_generation_is_ignored(self):
        progress=ObservedProgress()
        progress.observe('wire',event=dict(type='session.snapshot',generation=2))
        progress.observe('wire',event=dict(type='activation.started',generation=1))
        self.assertEqual(guide_progress('finish',progress.snapshot(),0)['active'],2)

    def test_cancel_and_none_waits_use_real_observation_time(self):
        progress=ObservedProgress()
        progress.observe('wire',event=dict(type='activation.cancelled',generation=1),now=10)
        self.assertGreater(progress.snapshot(now=12)['cancelWaitRemaining'],0)
        self.assertEqual(progress.snapshot(now=20)['cancelWaitRemaining'],0)
        progress.observe('control.received',slot='secondary',ready=True,phase='waiting_first_speech',now=20)
        self.assertGreater(progress.snapshot(now=21)['noneWaitRemaining'],0)
        self.assertEqual(progress.snapshot(now=23)['noneWaitRemaining'],0)

    def test_settings_and_perception_remain_explicit_human_actions(self):
        value=guide_progress('settings',ObservedProgress().snapshot(),0)
        self.assertTrue(value['manualAllowed'])
        value=guide_progress('finish',ObservedProgress().snapshot(),0)
        self.assertFalse(value['manualAllowed'])

    def test_duplicate_event_and_unspoken_finish_do_not_confirm_speech(self):
        progress=ObservedProgress()
        for _ in range(2):
            progress.observe('wire',event=dict(type='activation.started',generation=1,eventId='same'))
        self.assertEqual(progress.snapshot()['counts']['activation.started'],1)
        progress.observe('control.received',slot='secondary',ready=True,phase='waiting_first_speech')
        self.assertNotIn(3,guide_progress('finish',progress.snapshot(),0)['confirmed'])

    def test_usb_recovery_keeps_the_preparation_wait(self):
        progress=ObservedProgress()
        progress.observe('metrics',audioAvailable=True,now=0)
        progress.observe('metrics',audioAvailable=False,now=1)
        progress.observe('metrics',audioAvailable=True,now=2)
        progress.observe('runtime.view',ready=True,generation=1)
        self.assertEqual(guide_progress('usb',progress.snapshot(now=3),0)['active'],3)
        self.assertEqual(guide_progress('usb',progress.snapshot(now=11),0)['active'],4)

    def test_atomic_snapshot_retries_a_sharing_failure_without_partial_target(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'state.json'
            path.write_text('{"old":true}')
            original=Path.replace
            attempts=[]
            def replace(source,target):
                attempts.append(1)
                self.assertEqual(json.loads(path.read_text()),{'old':True})
                if len(attempts)==1:
                    raise PermissionError('controlled sharing violation')
                return original(source,target)
            with patch.object(Path,'replace',replace):
                save(path,{'new':True})
            self.assertEqual(len(attempts),2)
            self.assertEqual(json.loads(path.read_text()),{'new':True})

    def test_permanent_snapshot_permission_error_is_bounded_and_not_success(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'state.json'
            path.write_text('{"old":true}')
            with patch.object(Path,'replace',side_effect=PermissionError('controlled')) as replace, \
                 patch('tests.manual.v2.suite_session.time.monotonic',side_effect=[0,3]):
                with self.assertRaises(PermissionError):
                    save(path,{'new':True})
            self.assertEqual(replace.call_count,1)
            self.assertEqual(json.loads(path.read_text()),{'old':True})


if __name__=='__main__':
    unittest.main()
