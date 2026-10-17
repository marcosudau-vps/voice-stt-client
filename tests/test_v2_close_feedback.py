"""Input-close feedback is domain-driven, foreground-scoped and exactly once."""
import unittest

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.activation_mirror import Reduction
from voice_stt_client.core.event_models import CanonicalEventType as C
from voice_stt_client.core.feedback_mapping import FeedbackMappingConfig, SoundCueId
from voice_stt_client.core.feedback_reducer import FeedbackEngine
from tests import test_v2_feedback as feedback_tests
from tests.test_v2_mirror import A, B, snapshot


def sounds(decisions):
    return [d.rule.sound.cue for d in decisions if d.rule.sound is not None]


class InputClose(unittest.TestCase):
    def setUp(self):
        self.domain = feedback_tests.DomainFeedback()
        self.domain.setUp()

    def test_finish_and_timeout_without_speech_sound_for_both_trigger_sources(self):
        for source in ('manual', 'wake_word'):
            for reason in ('finished', 'timed_out'):
                with self.subTest(source=source, reason=reason):
                    self.setUp()
                    self.domain.start(source=source)
                    # Actual server order: terminal can precede input_closed.
                    self.assertEqual(sounds(self.domain.send(p.EventType.ACTIVATION_COMPLETED)), [])
                    decisions = self.domain.send(p.EventType.INPUT_CLOSED, reason=reason, acceptedSegmentCount=0)
                    self.assertEqual(sounds(decisions), [SoundCueId.STOP])
                    self.assertEqual(decisions[0].snapshot.phase, p.InputPhase.IDLE)

    def test_same_close_reduction_and_snapshot_never_repeat_the_sound(self):
        self.domain.start()
        first = self.domain.send(p.EventType.INPUT_CLOSED, reason='finished', acceptedSegmentCount=0)
        self.assertEqual(sounds(first), [SoundCueId.STOP])
        self.assertEqual(sounds(self.domain.engine.handle_reduction(self.domain.reduction)), [])
        self.assertEqual(sounds(self.domain.engine.handle_reduction(Reduction(self.domain.m.view))), [])
        self.assertEqual(sounds(self.domain.send(p.EventType.ACTIVATION_COMPLETED)), [])

    def test_background_close_never_announces_end_of_new_foreground(self):
        self.domain.start()
        self.domain.start(B, sequence=2)
        self.assertEqual(sounds(self.domain.send(p.EventType.INPUT_CLOSED, aid=A, reason='finished', acceptedSegmentCount=0)), [])
        self.assertEqual(self.domain.last[0].snapshot.activation_id, B)
        self.assertEqual(sounds(self.domain.send(p.EventType.INPUT_CLOSED, aid=B, reason='finished', acceptedSegmentCount=0)), [SoundCueId.STOP])

    def test_cancel_failure_watchdog_and_unknown_reasons_do_not_add_a_stop_tone(self):
        for terminal, reason, cue in ((p.EventType.ACTIVATION_CANCELLED, 'cancelled', SoundCueId.CANCEL),
                (p.EventType.ACTIVATION_FAILED, 'segment_watchdog_timeout', SoundCueId.ERROR)):
            with self.subTest(terminal=terminal):
                self.setUp(); self.domain.start()
                self.assertEqual(sounds(self.domain.send(terminal, reason=reason)), [cue])
                self.assertEqual(sounds(self.domain.send(p.EventType.INPUT_CLOSED, reason=reason, acceptedSegmentCount=0)), [])
        self.setUp(); self.domain.start()
        self.assertEqual(sounds(self.domain.send(p.EventType.INPUT_CLOSED, reason='future_recovery_reason', acceptedSegmentCount=0)), [])

    def test_old_generation_close_cannot_sound_after_reconnect(self):
        self.domain.start()
        self.domain.send(p.EventType.INPUT_CLOSED, reason='finished', acceptedSegmentCount=0)
        old = self.domain.reduction
        fresh = snapshot().to_mapping(); fresh['sessionId'] = p.new_id()
        self.domain.engine.handle_reduction(self.domain.m.begin(2, p.parse_snapshot(fresh), 20))
        self.assertEqual(sounds(self.domain.engine.handle_reduction(old)), [])

    def test_close_during_resync_is_not_replayed_as_live_feedback(self):
        self.domain.start()
        # Missing events mean no inferred lifecycle cue from resynchronisation.
        self.domain.seq += 1
        self.domain.send(p.EventType.PHASE_CHANGED, inputPhase='waiting_first_speech', deadlineAtUnixMs=100000, remainingMs=5000)
        self.assertEqual(sounds(self.domain.send(p.EventType.INPUT_CLOSED, reason='timed_out', acceptedSegmentCount=0)), [])

    def test_existing_custom_stop_sound_and_explicit_close_rule_are_preserved(self):
        custom = FeedbackMappingConfig.from_mapping({'schema_version': 2, 'events': {
            C.SERVER_RECORDING_ENDED.value: {'sound': {'cue': 'stop', 'volume': .3},
                                           'app': {'action': 'indicator.finalizing'}}}})
        self.domain.engine = FeedbackEngine(custom)
        self.domain.engine.handle_reduction(Reduction(self.domain.m.view))
        self.domain.start()
        close = self.domain.send(p.EventType.INPUT_CLOSED, reason='finished', acceptedSegmentCount=0)[-1]
        self.assertEqual(close.rule.sound.volume, .3)
        self.assertIsNone(close.rule.app)
        explicit = FeedbackMappingConfig.from_mapping({'schema_version': 2, 'events': {
            'server.input.closed': {}, C.SERVER_RECORDING_ENDED.value: {'sound': {'cue': 'stop'}}}})
        self.domain.engine = FeedbackEngine(explicit)
        self.domain.engine.handle_reduction(Reduction(self.domain.m.view))
        self.domain.start(B, sequence=2)
        self.assertEqual(sounds(self.domain.send(p.EventType.INPUT_CLOSED, aid=B, reason='finished', acceptedSegmentCount=0)), [])


if __name__ == '__main__':
    unittest.main()
