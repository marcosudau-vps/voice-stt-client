"""Harness regressions. No real audio, HTTP, credentials or native injection."""
from pathlib import Path
import tempfile
import unittest

from tests.manual.v2.suite_plan import TASKS, DEFERRED, TARGET, SuiteRecord, owned_path, target_origin, select_tasks
from tests.manual.v2.suite_session import prepare_profile,hello_identity
from tests.manual.v2.suite_analysis import summarize, assess_led_fault
import json


class GuidedSuite(unittest.TestCase):
    def test_optional_live_wake_tasks_do_not_change_default_manual_plan(self):
        self.assertEqual(len(select_tasks()),11)
        selected=select_tasks(['wake_alexa','wake_jarvis','wake_silent'])
        self.assertEqual([t['sounds'] for t in selected],[True,True,False])
        self.assertEqual([t['phrase'] for t in selected],['Alexa','Hey Jarvis','Alexa'])
        with tempfile.TemporaryDirectory() as temp:
            config=prepare_profile(Path(temp),TARGET,selected[-1],5)
            self.assertFalse(config.v2_profile['manual'])
            self.assertTrue(config.v2_profile['wake_word'])
            self.assertEqual(config.v2_profile['wake_word_ids'],['hey_jarvis','alexa'])
            self.assertFalse(config.feedback.sounds_enabled)

    def test_hello_identity_never_exports_log_credentials(self):
        from types import SimpleNamespace
        record=hello_identity(SimpleNamespace(session_id='session',generation=2,
            accepted=SimpleNamespace(payload=dict(serverCommit='a'*40,serverVersion='2.0.0',logAccess='secret'))))
        self.assertEqual(record['serverCommit'],'a'*40)
        self.assertNotIn('secret',str(record))

    def test_wake_quiet_countdown_needs_real_close_and_rejects_extra_start(self):
        from tests.manual.v2.suite_progress import ObservedProgress,guide_progress
        progress=ObservedProgress()
        progress.observe('wire',now=1,event={'type':'activation.started','generation':1})
        self.assertEqual(guide_progress('wake_alexa',progress.snapshot(1),0)['active'],3)
        progress.observe('wire',now=10,event={'type':'activation.input_closed','generation':1,'reason':'timed_out'})
        waiting=guide_progress('wake_alexa',progress.snapshot(12),0)
        self.assertEqual(waiting['active'],4)
        self.assertEqual(waiting['waitRemaining'],3)
        done=guide_progress('wake_alexa',progress.snapshot(15),0)
        self.assertEqual(done['active'],5)
        self.assertIn(4,done['confirmed'])
        progress.observe('wire',now=16,event={'type':'activation.started','generation':1})
        extra=guide_progress('wake_alexa',progress.snapshot(16),0)
        self.assertNotIn(4,extra['confirmed'])
        self.assertIn('Mehrere Aktivierungen',extra['notice'])

    def test_native_led_loss_and_fast_recovery_remain_visible_between_polls(self):
        from tests.manual.v2.suite_progress import ObservedProgress
        progress = ObservedProgress()
        progress.observe('led.sink', available=False)
        progress.observe('led.sink', available=True)
        snapshot = progress.snapshot()
        self.assertEqual(snapshot['counts']['led.unavailable'], 1)
        self.assertEqual(snapshot['counts']['led.available'], 1)
        self.assertFalse(snapshot['audioLost'])

    def test_led_fault_needs_real_progress_unchanged_session_and_observations(self):
        before = dict(ready=True, audioAvailable=True, sessionId='session', generation=1, media={'sent':50})
        after = dict(ready=True, audioAvailable=True, sessionId='session', generation=1, media={'sent':200},
            localIssues=['led_unavailable'], operatorProgress={'counts':{}, 'audioLost':False})
        self.assertEqual(assess_led_fault(before, after, led_unavailable=True)['result'], 'PASS')
        for key, value in [('audioAvailable',False),('sessionId','other'),('localIssues',[]),('media',{'sent':50}),('operatorProgress',{})]:
            with self.subTest(key=key):
                changed = dict(after, **{key:value})
                self.assertEqual(assess_led_fault(before, changed, led_unavailable=True)['result'], 'FAIL')
        self.assertEqual(assess_led_fault(before,after,led_unavailable=False)['result'],'FAIL')

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
