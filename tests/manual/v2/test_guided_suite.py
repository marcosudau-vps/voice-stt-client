"""Harness regressions. No real audio, HTTP, credentials or native injection."""
from pathlib import Path
import tempfile
import unittest

from tests.manual.v2.suite_plan import TASKS, DEFERRED, SuiteRecord, owned_path, target_origin, select_tasks
from tests.manual.v2.suite_session import prepare_profile
from tests.manual.v2.suite_analysis import summarize
import json


class GuidedSuite(unittest.TestCase):
    def test_real_idle_effect_remains_white_above_the_requested_floor(self):
        import yaml
        from voice_stt_client.core.led_controller import InProcessLedController
        params = yaml.safe_load(Path(__file__).with_name('calibration.yaml').read_text(encoding='utf8'))['idle']
        with tempfile.TemporaryDirectory() as temp:
            controller = InProcessLedController(sink='null', state_file=Path(temp)/'led-state.json')
            try:
                runtime = controller._service.runtime
                runtime.set_state('ready_state', params, now=0.)
                levels = []
                for n in range(121):
                    frame = runtime.render_once((4/.45)*n/120)
                    self.assertEqual(len(frame.leds), 12)
                    for color in frame.leds:
                        red, green, blue = color >> 16 & 255, color >> 8 & 255, color & 255
                        self.assertEqual((red, green), (blue, blue))
                        self.assertGreaterEqual(red, 76)
                        levels.append(red)
                self.assertEqual(max(levels), 255)
                self.assertEqual(min(levels), 76)
            finally:
                controller.close()

    def test_targeted_repeat_preserves_order_and_requires_known_distinct_tasks(self):
        self.assertEqual([x['id'] for x in select_tasks(['usb','feedback'])], ['usb','feedback'])
        self.assertEqual(len(select_tasks()), 11)
        for value in ([], ['usb','usb'], ['unknown']):
            with self.subTest(value=value), self.assertRaises(ValueError):
                select_tasks(value)

    def test_target_is_explicit_tls_v2_without_credentials_or_redirect_origin(self):
        self.assertEqual(target_origin('wss://pro.v2.voice-stt-server.marcosudau.com/ws/v2'),
                         'https://pro.v2.voice-stt-server.marcosudau.com')
        for value in ('ws://pro.v2.voice-stt-server.marcosudau.com/ws/v2',
                      'wss://example.com/ws/v2',
                      'wss://pro.v2.voice-stt-server.marcosudau.com/ws/transcribe',
                      'wss://user:secret@pro.v2.voice-stt-server.marcosudau.com/ws/v2',
                      'wss://pro.v2.voice-stt-server.marcosudau.com/ws/v2?key=secret',
                      'wss://pro.v2.voice-stt-server.marcosudau.com:8443/ws/v2'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                target_origin(value)

    def test_runtime_containment_rejects_parent_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(owned_path(root/'attempt', root), (root/'attempt').resolve())
            with self.assertRaises(ValueError):
                owned_path(root/'../foreign', root)

    def test_next_repeat_and_abort_never_start_another_client(self):
        record = SuiteRecord()
        first = record.start('finish')
        with self.assertRaises(RuntimeError):
            record.start('cancel')
        with self.assertRaises(RuntimeError):
            record.decide('accept', 'passt', '')
        record.stopped(0)
        record.decide('repeat', 'Problem', 'noch einmal')
        self.assertIsNone(record.active)
        second = record.start('finish')
        self.assertNotEqual(first['attemptId'], second['attemptId'])
        record.stopped(0)
        record.decide('accept', 'passt', '')
        self.assertIsNone(record.active)
        self.assertEqual(record.attempts[0]['decision'], 'repeat')
        self.assertEqual(record.attempts[1]['evaluation'], 'NOT_PROVEN_PENDING_AGENT_REVIEW')

    def test_task_catalog_is_pre_readable_and_deferrals_not_passes(self):
        self.assertEqual(len({task['id'] for task in TASKS}), len(TASKS))
        for task in TASKS:
            self.assertTrue(task['steps'] and task['requirements'] and task['expected'])
            self.assertTrue(task['phrase'])
        self.assertTrue(any('W01' in item for item in DEFERRED))

    def test_generated_profile_has_real_paths_no_wake_and_calibrated_followup(self):
        from tests.manual.v2.suite_plan import TARGET
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            config = prepare_profile(folder, TARGET, TASKS[2], 5)
            self.assertFalse(config.v2_profile['wake_word'])
            self.assertEqual(config.v2_profile['wake_word_ids'], [])
            self.assertEqual(config.v2_profile['controls']['secondary_action'], 'cancel')
            self.assertEqual(config.v2_profile['desired_settings']['activation.followupTimeoutMs'], 5000)
            for path in (config.history.persistent.db_path, config.event_stream.cursor_path, config.logging.log_dir):
                self.assertTrue(Path(path).is_relative_to(folder))
            self.assertFalse(config.logging.observability.store_transcription_content)
            self.assertFalse(config.logging.observability.store_raw_payload)
            self.assertEqual(config.server.url, TARGET)
            idle = config.feedback_mappings.to_mapping()['events']['server.input.idle']['led']
            params = next(call['config'] for call in idle if call.get('set_state') == 'ready_state')
            self.assertEqual(params, dict(color='#FFFFFF', min_brightness=.30, brightness=1.0))

    def test_no_events_or_clicked_acceptance_are_never_a_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            summary = summarize(Path(temp))
            self.assertEqual(summary['wireEvents'], {})
            self.assertEqual(summary['evaluation'], 'NOT_PROVEN_PENDING_AGENT_REVIEW')
            self.assertIsNone(summary['maxTasks'])


if __name__ == '__main__':
    unittest.main()
