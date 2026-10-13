"""AP8 – the feedback contract for server-authoritative activations.

The chain under test:

```text
Server trigger_ack / Server Event
    -> Client Normalizer
    -> Canonical Event
    -> Feedback Reducer
    -> Feedback Mapping
    -> Sound / LEFX
```

The existing feedback repair (commit ``178d32b``) is binding and must survive,
so these tests check the new behaviour *and* that the established impulses are
still produced exactly as before.
"""

from __future__ import annotations

import unittest

from voice_stt_client.core.config import AppConfig, OperatingMode, SessionConfig
from voice_stt_client.core.event_models import (
    CanonicalEventType,
    EventOrigin,
    FeedbackImpulse,
    FeedbackState,
)






class FeedbackMappingCoversTheContract(unittest.TestCase):
    """Every event of the trigger path must reach a sound or an LED target."""

    def setUp(self):
        self.mappings = AppConfig.load().feedback_mappings

    def test_the_events_of_the_trigger_path_all_have_a_rule(self):
        for event_type in (
            CanonicalEventType.CLIENT_HOTKEY_ACCEPTED,
            CanonicalEventType.SERVER_WAKE_WORD_DETECTED,
            CanonicalEventType.SERVER_RECORDING_STARTED,
            CanonicalEventType.SERVER_RECORDING_ENDED,
            CanonicalEventType.SERVER_TRANSCRIPTION_STARTED,
            CanonicalEventType.SERVER_TRANSCRIPTION_COMPLETED,
            CanonicalEventType.SERVER_TRANSCRIPTION_FAILED,
            CanonicalEventType.SERVER_TRANSCRIPTION_CANCELLED,
            CanonicalEventType.CLIENT_DICTATION_INTERRUPTED,
        ):
            with self.subTest(event=event_type.value):
                rule = self.mappings.rule_for(event_type)
                self.assertTrue(
                    rule.led or rule.sound or rule.app,
                    f"{event_type.value} has no feedback target at all",
                )

    def test_the_countdown_and_the_timeout_sound_are_still_configured(self):
        rule = self.mappings.rule_for(
            CanonicalEventType.CLIENT_DICTATION_TIMEOUT_WARNING
        )
        self.assertTrue(rule.led, "the countdown ring must stay configured")
        self.assertIsNotNone(rule.sound, "the timeout tick must stay configured")

    def test_manual_accepted_still_produces_a_sound_and_an_led_effect(self):
        """The existing feedback repair is binding and must not be undone."""
        rule = self.mappings.rule_for(CanonicalEventType.CLIENT_HOTKEY_ACCEPTED)
        self.assertTrue(rule.led)
        self.assertIsNotNone(rule.sound)

    def test_every_named_led_target_is_a_non_empty_name(self):
        targets = self.mappings.led_targets()
        self.assertTrue(targets, "no LED targets configured at all")
        for target in targets:
            with self.subTest(target=target):
                self.assertIsInstance(target, str)
                self.assertTrue(target.strip())


class EveryConfiguredSoundCueHasAnAsset(unittest.TestCase):
    """GATE 8: "bestehende Sounds vollständig" - checked, not assumed."""

    def setUp(self):
        from pathlib import Path

        self.mappings = AppConfig.load().feedback_mappings
        self.asset_dir = (
            Path(__file__).resolve().parents[1]
            / "voice_stt_client"
            / "assets"
            / "feedback_sounds"
            / "debug"
        )

    def test_every_cue_named_by_a_mapping_has_a_sound_file(self):
        used = {
            rule.sound.cue
            for rule in self.mappings.events.values()
            if rule.sound is not None
        }
        self.assertTrue(used, "no sound cues configured at all")
        for cue in sorted(used, key=lambda item: item.value):
            with self.subTest(cue=cue.value):
                path = self.asset_dir / f"{cue.value}.wav"
                self.assertTrue(path.is_file(), f"missing sound asset: {path}")

    def test_every_declared_cue_has_a_sound_file(self):
        from voice_stt_client.core.feedback_mapping import SoundCueId

        for cue in SoundCueId:
            with self.subTest(cue=cue.value):
                path = self.asset_dir / f"{cue.value}.wav"
                self.assertTrue(path.is_file(), f"missing sound asset: {path}")

    def test_the_trigger_path_cues_are_actually_wired(self):
        from voice_stt_client.core.feedback_mapping import SoundCueId

        expected = {
            CanonicalEventType.CLIENT_HOTKEY_ACCEPTED: SoundCueId.WAKE_WORD,
            CanonicalEventType.SERVER_RECORDING_STARTED: SoundCueId.START,
            CanonicalEventType.SERVER_RECORDING_ENDED: SoundCueId.STOP,
            CanonicalEventType.SERVER_TRANSCRIPTION_COMPLETED: SoundCueId.COMPLETE,
            CanonicalEventType.CLIENT_DICTATION_TIMEOUT_WARNING: SoundCueId.TIMEOUT_TICK,
        }
        for event_type, cue in expected.items():
            with self.subTest(event=event_type.value):
                rule = self.mappings.rule_for(event_type)
                self.assertIsNotNone(rule.sound, f"{event_type.value} has no sound")
                self.assertEqual(rule.sound.cue, cue)






if __name__ == "__main__":
    unittest.main()
