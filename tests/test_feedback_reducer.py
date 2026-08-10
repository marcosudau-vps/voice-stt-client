from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import unittest

from core.event_models import (
    CanonicalEventType,
    EventConnectionState,
    EventOrigin,
    FeedbackImpulse,
    FeedbackSource,
    FeedbackState,
)
from core.feedback_mapping import (
    FeedbackMappingConfig,
    FeedbackRule,
    SoundCueId,
    SoundEffect,
)
from core.feedback_reducer import FeedbackEngine
from tests.test_event_normalizer import log_result


class FeedbackReducerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = FeedbackEngine(FeedbackMappingConfig())

    def connect(
        self,
        state: EventConnectionState,
        *,
        stt_ready: bool = True,
        issue: str | None = None,
    ):
        return self.engine.update_connection(
            state,
            stt_ready=stt_ready,
            generation=1,
            session_id="session-1",
            issue=issue,
        )

    def event(
        self,
        name: str,
        *,
        origin: EventOrigin = EventOrigin.LIVE,
        segment_id: int | None = 1,
        event_id: str = "event-1",
        data: dict | None = None,
    ):
        return self.engine.handle_event_stream(
            log_result(
                name,
                origin=origin,
                segment_id=segment_id,
                event_id=event_id,
                transcription_id=(
                    f"session-1:1:{segment_id}" if segment_id is not None else None
                ),
                data=data,
            ),
            generation=1,
            session_id="session-1",
        )

    def fallback(self, event: str, segment_id: int = 1):
        return self.engine.handle_stt_fallback(
            "timeline",
            {
                "type": "timeline",
                "event": event,
                "sessionId": "session-1",
                "segmentId": segment_id,
                **(
                    {"reason": "empty_final"}
                    if event == "final_transcript_discarded"
                    else {}
                ),
            },
            generation=1,
            session_id="session-1",
        )

    def test_hotkey_live_lifecycle_has_one_impulse_per_phase(self) -> None:
        self.connect(EventConnectionState.LIVE)

        started = self.event("transcription.recording_started", event_id="start")
        ended = self.event("transcription.recording_ended", event_id="end")
        processing = self.event("transcription.started", event_id="processing")
        completed = self.event("transcription.completed", event_id="complete")

        self.assertEqual(started.impulse, FeedbackImpulse.RECORDING_STARTED)
        self.assertEqual(ended.impulse, FeedbackImpulse.RECORDING_ENDED)
        self.assertIsNone(processing.impulse)
        self.assertEqual(completed.impulse, FeedbackImpulse.TRANSCRIPTION_COMPLETED)
        self.assertEqual(completed.state, FeedbackState.COMPLETED)
        self.assertEqual(self.engine.state.visible_state, FeedbackState.IDLE)

    def test_wake_word_lifecycle_is_supported(self) -> None:
        self.connect(EventConnectionState.LIVE)

        wake = self.event(
            "wakeword.detected",
            segment_id=None,
            event_id="wake-1",
        )
        recording = self.event(
            "transcription.recording_started",
            event_id="record-1",
        )

        self.assertEqual(wake.impulse, FeedbackImpulse.WAKE_WORD_DETECTED)
        self.assertEqual(wake.state, FeedbackState.STARTING)
        self.assertEqual(recording.state, FeedbackState.RECORDING)

    def test_replay_reconstructs_without_impulses_and_publishes_at_live(self) -> None:
        self.connect(EventConnectionState.REPLAYING)

        replay = self.event(
            "transcription.recording_started",
            origin=EventOrigin.REPLAY,
            event_id="replay-start",
        )

        self.assertFalse(replay.publish)
        self.assertIsNone(replay.impulse)
        self.assertEqual(self.engine.state.event_state, FeedbackState.RECORDING)
        live = self.connect(EventConnectionState.LIVE)
        self.assertTrue(live.publish)
        self.assertEqual(live.source, FeedbackSource.EVENT_STREAM)
        self.assertEqual(live.state, FeedbackState.RECORDING)

    def test_live_switchover_never_replays_stored_sound_cue(self) -> None:
        self.engine = FeedbackEngine(
            FeedbackMappingConfig(
                events={
                    CanonicalEventType.SERVER_RECORDING_STARTED.value: FeedbackRule(
                        sound=SoundEffect(SoundCueId.START)
                    )
                }
            )
        )
        self.connect(EventConnectionState.REPLAYING)
        self.event(
            "transcription.recording_started",
            origin=EventOrigin.REPLAY,
            event_id="stored-start",
        )

        live = self.connect(EventConnectionState.LIVE)

        self.assertIsNone(live.rule.sound)

    def test_replay_of_completed_operation_settles_to_idle_without_impulse(self) -> None:
        self.connect(EventConnectionState.REPLAYING)
        replay = self.event(
            "transcription.completed",
            origin=EventOrigin.REPLAY,
            event_id="old-complete",
        )

        live = self.connect(EventConnectionState.LIVE)

        self.assertFalse(replay.publish)
        self.assertEqual(live.state, FeedbackState.IDLE)
        self.assertIsNone(live.impulse)
        self.assertEqual(live.rule, FeedbackRule())

    def test_fallback_remains_active_through_replay_then_switches_atomically(self) -> None:
        self.connect(EventConnectionState.UNAVAILABLE)
        fallback = self.fallback("recording_started")
        self.assertTrue(fallback.publish)
        self.assertEqual(fallback.source, FeedbackSource.STT_FALLBACK)

        replaying = self.connect(EventConnectionState.REPLAYING)
        replay = self.event(
            "transcription.recording_started",
            origin=EventOrigin.REPLAY,
            event_id="server-start",
        )
        self.assertEqual(replaying.source, FeedbackSource.STT_FALLBACK)
        self.assertFalse(replay.publish)

        live = self.connect(EventConnectionState.LIVE)
        self.assertEqual(live.source, FeedbackSource.EVENT_STREAM)
        self.assertEqual(live.state, FeedbackState.RECORDING)

    def test_recovery_deduplicates_fallback_semantic_event(self) -> None:
        self.connect(EventConnectionState.UNAVAILABLE)
        fallback = self.fallback("recording_started")
        self.connect(EventConnectionState.REPLAYING)
        replay = self.event(
            "transcription.recording_started",
            origin=EventOrigin.REPLAY,
            event_id="durable-start",
        )
        self.connect(EventConnectionState.LIVE)
        duplicate_live = self.event(
            "transcription.recording_started",
            event_id="second-id-same-fact",
        )

        self.assertEqual(fallback.impulse, FeedbackImpulse.RECORDING_STARTED)
        self.assertTrue(replay.duplicate)
        self.assertIsNone(replay.impulse)
        self.assertTrue(duplicate_live.duplicate)
        self.assertIsNone(duplicate_live.impulse)

    def test_fallback_is_silent_while_event_stream_is_live(self) -> None:
        self.connect(EventConnectionState.LIVE)

        decision = self.fallback("recording_started")

        self.assertFalse(decision.publish)
        self.assertEqual(self.engine.state.source, FeedbackSource.EVENT_STREAM)

    def test_failure_before_recording_during_recording_and_finalizing_uses_shadow(self) -> None:
        scenarios = (
            (None, None, FeedbackState.IDLE),
            (
                "transcription.recording_started",
                "recording_started",
                FeedbackState.RECORDING,
            ),
            (
                "transcription.recording_ended",
                "recording_ended",
                FeedbackState.FINALIZING,
            ),
        )
        for server_name, fallback_name, expected in scenarios:
            with self.subTest(expected=expected):
                self.engine = FeedbackEngine(FeedbackMappingConfig())
                self.connect(EventConnectionState.LIVE)
                if server_name is not None:
                    self.event(server_name, event_id=f"event-{expected.value}")
                    shadow = self.fallback(fallback_name)
                    self.assertFalse(shadow.publish)

                degraded = self.connect(EventConnectionState.BACKOFF)

                self.assertEqual(degraded.source, FeedbackSource.STT_FALLBACK)
                self.assertEqual(degraded.state, expected)

    def test_both_connections_down_results_in_local_only(self) -> None:
        decision = self.engine.update_connection(
            EventConnectionState.BACKOFF,
            stt_ready=False,
            generation=1,
            session_id=None,
        )

        self.assertEqual(decision.source, FeedbackSource.LOCAL_ONLY)

        stale_live = self.engine.update_connection(
            EventConnectionState.LIVE,
            stt_ready=False,
            generation=1,
            session_id="session-1",
        )
        self.assertEqual(stale_live.source, FeedbackSource.LOCAL_ONLY)

    def test_retention_gap_remains_visible_as_uncertainty(self) -> None:
        gap = self.connect(
            EventConnectionState.REPLAYING,
            issue="retention_gap",
        )
        live = self.connect(EventConnectionState.LIVE)

        self.assertTrue(gap.uncertain)
        self.assertTrue(live.uncertain)

    def test_retention_replay_rebuilds_finalizing_without_historical_impulse(self) -> None:
        self.connect(EventConnectionState.UNAVAILABLE)
        fallback = self.fallback("recording_started")
        self.connect(
            EventConnectionState.REPLAYING,
            issue="retention_gap",
        )
        replay = self.event(
            "transcription.recording_ended",
            origin=EventOrigin.REPLAY,
            event_id="replayed-end",
        )
        live = self.connect(EventConnectionState.LIVE)
        completed = self.event(
            "transcription.completed",
            event_id="new-live-complete",
        )

        self.assertEqual(fallback.impulse, FeedbackImpulse.RECORDING_STARTED)
        self.assertFalse(replay.publish)
        self.assertIsNone(replay.impulse)
        self.assertTrue(live.uncertain)
        self.assertEqual(live.state, FeedbackState.FINALIZING)
        self.assertIsNone(live.impulse)
        self.assertIsNone(live.rule.sound)
        self.assertEqual(
            completed.impulse,
            FeedbackImpulse.TRANSCRIPTION_COMPLETED,
        )

    def test_new_generation_resets_old_server_shadow_state(self) -> None:
        self.connect(EventConnectionState.LIVE)
        self.event("transcription.recording_started", event_id="old-recording")

        next_generation = self.engine.update_connection(
            EventConnectionState.CONNECTING,
            stt_ready=False,
            generation=2,
            session_id=None,
        )
        fallback = self.engine.update_connection(
            EventConnectionState.UNAVAILABLE,
            stt_ready=True,
            generation=2,
            session_id="session-2",
        )

        self.assertEqual(next_generation.state, FeedbackState.IDLE)
        self.assertEqual(fallback.state, FeedbackState.IDLE)
        self.assertEqual(self.engine.state.event_state, FeedbackState.IDLE)
        self.assertEqual(self.engine.state.fallback_state, FeedbackState.IDLE)

    def test_local_microphone_fault_has_priority_over_server_failure(self) -> None:
        self.connect(EventConnectionState.LIVE)
        self.event("transcription.failed", event_id="server-failure")
        microphone = self.engine.handle_local(
            CanonicalEventType.CLIENT_MICROPHONE_LOST,
            generation=1,
            session_id="session-1",
            correlation_id="microphone:lost",
        )
        self.event("transcription.recording_started", event_id="new-recording")

        self.assertEqual(microphone.source, FeedbackSource.LOCAL_ONLY)
        self.assertEqual(self.engine.state.visible_state, FeedbackState.FAILED)
        recovered = self.engine.handle_local(
            CanonicalEventType.CLIENT_MICROPHONE_RECOVERED,
            generation=1,
            session_id="session-1",
            correlation_id="microphone:recovered",
        )
        self.assertEqual(recovered.state, FeedbackState.RECORDING)

    def test_paste_failure_is_local_and_does_not_erase_server_state(self) -> None:
        self.connect(EventConnectionState.LIVE)
        self.event("transcription.recording_started", event_id="recording")

        failed = self.engine.handle_local(
            CanonicalEventType.CLIENT_INJECTION_FAILED,
            generation=1,
            session_id="session-1",
            correlation_id="injection:entry-1",
        )

        self.assertEqual(failed.impulse, FeedbackImpulse.INJECTION_FAILED)
        self.assertEqual(failed.state, FeedbackState.FAILED)
        self.assertEqual(self.engine.state.visible_state, FeedbackState.RECORDING)

    def test_empty_final_discard_is_terminal_without_impulse(self) -> None:
        self.connect(EventConnectionState.LIVE)

        discarded = self.event(
            "transcription.discarded",
            event_id="discard",
            data={"reason": "empty_final"},
        )

        self.assertEqual(discarded.state, FeedbackState.IDLE)
        self.assertIsNone(discarded.impulse)

    def test_dedupe_memory_is_bounded_after_more_than_ten_thousand_events(self) -> None:
        self.engine = FeedbackEngine(FeedbackMappingConfig(), dedupe_limit=256)
        self.connect(EventConnectionState.LIVE)
        for index in range(10050):
            self.engine.handle_event_stream(
                log_result(
                    "transcription.recording_started",
                    segment_id=index,
                    event_id=f"event-{index}",
                    transcription_id=f"session-1:1:{index}",
                ),
                generation=1,
                session_id="session-1",
            )

        self.assertLessEqual(len(self.engine.state.seen_event_ids), 256)
        self.assertLessEqual(len(self.engine.state.seen_correlations), 256)

    def test_unknown_event_catalog_is_bounded(self) -> None:
        for index in range(200):
            self.engine.handle_event_stream(
                log_result(f"unknown.{index}", event_id=f"unknown-{index}"),
                generation=1,
                session_id="session-1",
            )

        self.assertEqual(len(self.engine.unknown_events), 128)

    def test_stateful_engine_serializes_parallel_inputs(self) -> None:
        self.connect(EventConnectionState.LIVE)

        def submit(index: int) -> None:
            self.engine.handle_event_stream(
                log_result(
                    "transcription.recording_started",
                    segment_id=index,
                    event_id=f"parallel-{index}",
                    transcription_id=f"session-1:1:{index}",
                ),
                generation=1,
                session_id="session-1",
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(submit, range(200)))

        self.assertEqual(len(self.engine.state.seen_event_ids), 200)
        self.assertEqual(len(self.engine.state.seen_correlations), 400)


if __name__ == "__main__":
    unittest.main()
