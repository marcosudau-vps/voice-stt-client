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

from core.config import AppConfig, OperatingMode, SessionConfig
from core.controller import STTController
from core.event_models import (
    CanonicalEventType,
    EventOrigin,
    FeedbackImpulse,
    FeedbackState,
)
from tests.test_controller import (
    FakeAudioCapture,
    FakeInjectionQueue,
    FakeSTTSession,
)
from tests.test_trigger_lifecycle import TriggerCapableSession


class ManualAcceptedComesFromTheAck(unittest.IsolatedAsyncioTestCase):
    """A hotkey press alone is a local intention and must stay silent."""

    async def _controller(self, session):
        config = AppConfig()
        config.history.persistent.enabled = False
        controller = STTController(
            config,
            session=session,
            audio=FakeAudioCapture(),
            injection_queue=FakeInjectionQueue(),
        )
        controller.start_queue()
        self.decisions = []
        controller.on_feedback_decision = self.decisions.append
        self.addCleanup(self._shutdown, controller)
        return controller

    def _shutdown(self, controller):
        import asyncio

        asyncio.run(controller.shutdown())

    def _accepted(self):
        return [
            decision
            for decision in self.decisions
            if decision.event.event_type
            is CanonicalEventType.CLIENT_HOTKEY_ACCEPTED
            and decision.publish
        ]

    async def test_an_accepted_trigger_produces_exactly_one_manual_impulse(self):
        session = TriggerCapableSession(accept=True)
        controller = await self._controller(session)

        result = await controller.start_dictation()

        self.assertTrue(result.success, result.message)
        self.assertEqual(
            len(self._accepted()),
            1,
            "an accepted trigger must produce exactly one manual impulse",
        )

    async def test_a_rejected_trigger_produces_no_manual_impulse(self):
        session = TriggerCapableSession(accept=False, reason="stream_not_started")
        controller = await self._controller(session)

        result = await controller.start_dictation()

        self.assertFalse(result.success)
        self.assertEqual(
            self._accepted(),
            [],
            "no accepted-feedback may fire before/without an accepted ack",
        )

    async def test_a_legacy_server_still_produces_the_manual_impulse(self):
        """The behaviour against a server without the contract is unchanged."""
        session = FakeSTTSession()
        controller = await self._controller(session)

        result = await controller.start_dictation()

        self.assertTrue(result.success, result.message)
        self.assertEqual(len(self._accepted()), 1)


class RepeatedAndReplayedEventsProduceNoSecondImpulse(unittest.IsolatedAsyncioTestCase):
    """Dedupe and replay suppression, the core of the existing feedback fix."""

    async def asyncSetUp(self) -> None:
        config = AppConfig()
        config.history.persistent.enabled = False
        self.session = FakeSTTSession()
        self.controller = STTController(
            config,
            session=self.session,
            audio=FakeAudioCapture(),
            injection_queue=FakeInjectionQueue(),
        )
        self.decisions = []
        self.controller.on_feedback_decision = self.decisions.append

    async def asyncTearDown(self) -> None:
        await self.controller.shutdown()

    def _emit(self, correlation_id, origin=EventOrigin.LOCAL):
        return self.controller.feedback_engine.handle_local(
            CanonicalEventType.CLIENT_HOTKEY_ACCEPTED,
            generation=self.session.generation,
            session_id=self.session.state.session_id,
            correlation_id=correlation_id,
            details={"action": "start_dictation"},
        )

    async def test_the_same_correlation_id_is_only_published_once(self):
        first = self._emit("trigger:cmd-1")
        second = self._emit("trigger:cmd-1")
        third = self._emit("trigger:cmd-1")

        self.assertTrue(first.publish)
        self.assertFalse(second.publish, "a repeated ack must not publish again")
        self.assertFalse(third.publish)
        self.assertTrue(second.duplicate)

    async def test_a_different_command_id_is_a_new_impulse(self):
        first = self._emit("trigger:cmd-1")
        second = self._emit("trigger:cmd-2")
        self.assertTrue(first.publish)
        self.assertTrue(second.publish)


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
        from core.feedback_mapping import SoundCueId

        for cue in SoundCueId:
            with self.subTest(cue=cue.value):
                path = self.asset_dir / f"{cue.value}.wav"
                self.assertTrue(path.is_file(), f"missing sound asset: {path}")

    def test_the_trigger_path_cues_are_actually_wired(self):
        from core.feedback_mapping import SoundCueId

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


class ManualDuringWakeWordActivation(unittest.IsolatedAsyncioTestCase):
    """GATE 8: a manual trigger inside a running wake-word activation."""

    async def asyncSetUp(self) -> None:
        config = AppConfig(
            session=SessionConfig(
                manual_trigger_enabled=True, wake_word_trigger_enabled=True
            )
        )
        config.history.persistent.enabled = False
        self.session = FakeSTTSession()
        self.controller = STTController(
            config,
            session=self.session,
            audio=FakeAudioCapture(),
            injection_queue=FakeInjectionQueue(),
        )
        self.decisions = []
        self.controller.on_feedback_decision = self.decisions.append

    async def asyncTearDown(self) -> None:
        await self.controller.shutdown()

    def _timeline(self, event, **fields):
        payload = {
            "type": "timeline",
            "sessionId": self.session.state.session_id,
            "_clientGeneration": self.session.generation,
            "event": event,
        }
        payload.update(fields)
        self.controller.handle_server_event("timeline", payload)

    async def test_a_manual_trigger_inside_a_wake_word_turn_adds_no_second_sequence(self):
        # The wake word opened the activation on the server.
        self._timeline("wakeword_detected", wakeWord="hey_jarvis")
        self._timeline(
            "recording_started",
            activationId="w-1",
            primarySource="wake_word",
            sources=["wake_word"],
        )
        # The user now also presses the hotkey; the server merges it.
        self._timeline(
            "recording_started",
            activationId="w-1",
            primarySource="wake_word",
            sources=["wake_word", "manual"],
        )
        self._timeline(
            "recording_ended",
            activationId="w-1",
            primarySource="wake_word",
            sources=["wake_word", "manual"],
        )

        starts = [
            decision
            for decision in self.decisions
            if decision.publish
            and decision.event.impulse is FeedbackImpulse.RECORDING_STARTED
        ]
        self.assertLessEqual(
            len(starts),
            1,
            "a merged manual trigger must not start a second recording sequence",
        )


class WakeWordDuringManualActivation(unittest.IsolatedAsyncioTestCase):
    """A wake word inside a running manual activation: impulse, but no second turn."""

    async def asyncSetUp(self) -> None:
        config = AppConfig(
            session=SessionConfig(
                manual_trigger_enabled=True, wake_word_trigger_enabled=True
            )
        )
        config.history.persistent.enabled = False
        self.session = FakeSTTSession()
        self.controller = STTController(
            config,
            session=self.session,
            audio=FakeAudioCapture(),
            injection_queue=FakeInjectionQueue(),
        )
        self.decisions = []
        self.controller.on_feedback_decision = self.decisions.append

    async def asyncTearDown(self) -> None:
        await self.controller.shutdown()

    def _timeline(self, event, **fields):
        payload = {
            "type": "timeline",
            "sessionId": self.session.state.session_id,
            "_clientGeneration": self.session.generation,
            "event": event,
        }
        payload.update(fields)
        self.controller.handle_server_event("timeline", payload)

    async def test_one_activation_yields_one_recording_sequence(self):
        await self.controller.start_dictation()

        # The server reports a wake word inside the same activation, then a
        # single recording sequence for it.
        self._timeline("wakeword_detected", wakeWord="hey_jarvis")
        self._timeline(
            "recording_started",
            activationId="a-1",
            primarySource="manual",
            sources=["manual", "wake_word"],
        )
        self._timeline(
            "recording_ended",
            activationId="a-1",
            primarySource="manual",
            sources=["manual", "wake_word"],
        )

        starts = [
            decision
            for decision in self.decisions
            if decision.publish
            and decision.event.impulse is FeedbackImpulse.RECORDING_STARTED
        ]
        self.assertLessEqual(
            len(starts),
            1,
            "a wake word inside a manual activation must not start a second "
            "recording sequence",
        )


if __name__ == "__main__":
    unittest.main()
