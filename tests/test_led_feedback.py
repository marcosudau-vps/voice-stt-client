"""The LED worker: what it forwards, what it drops, and how it fails.

Nothing here touches USB or LEFX. The controller is a double, because what this
module decides is which thread calls, what may be coalesced and when a failure
is worth reporting — none of which needs a device to be answered.
"""

from __future__ import annotations

import threading
import time
import unittest

from core.config import LedConfig
from core.feedback_mapping import LedCall, LedVerb
from core.led_controller import LedConfigurationError, LedControllerError
from ui.led_feedback import MAX_PENDING, LedFeedback


def wait_until(predicate, timeout: float = 2.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.005)
    return bool(predicate())


def state(target: str, *, slot: str | None = None) -> LedCall:
    return LedCall(LedVerb.SET_STATE, target=target, slot=slot)


def event(target: str) -> LedCall:
    return LedCall(LedVerb.EMIT_EVENT, target=target)


class FakeController:
    """Records what it was asked to do, and can be made to stall or fail."""

    def __init__(self) -> None:
        self.calls: list[tuple] = []
        self.closed = False
        self.unknown: set[str] = set()
        self.fail_with: Exception | None = None
        self.gate: threading.Event | None = None
        self.entered = threading.Event()
        self.mute_reaches_device = True
        self.mute_fails = False
        self.mute_state: bool | None = False

    def _record(self, *item) -> None:
        self.entered.set()
        if self.gate is not None:
            self.gate.wait(5.0)
        if self.fail_with is not None:
            raise self.fail_with
        self.calls.append(item)

    def resolve(self, target: str) -> None:
        if target in self.unknown:
            raise LedControllerError(f"no such target {target!r}")

    def set_state(self, target, *, config=None, slot="primary", action="on") -> None:
        self._record("set_state", target, slot, action)

    def clear_state(self, *, slot="primary") -> None:
        self._record("clear_state", slot)

    def set_overlay(self, target, *, config=None, action="on") -> None:
        self._record("set_overlay", target, action)

    def emit_event(self, target, *, config=None, duration_ms=None, priority=None) -> None:
        self._record("emit_event", target, duration_ms)

    def set_output(self, *, brightness=None, enabled=None) -> None:
        self._record("set_output", brightness, enabled)

    def set_device_mute(self, muted: bool) -> bool:
        self.calls.append(("set_device_mute", muted))
        if self.mute_fails:
            raise LedControllerError("mute line unreachable")
        if self.mute_reaches_device:
            self.mute_state = muted
        return self.mute_reaches_device

    def device_mute(self):
        return self.mute_state

    def close(self) -> None:
        self.closed = True

    @property
    def verbs(self) -> list[str]:
        return [item[0] for item in self.calls]


def build(controller: FakeController, **overrides) -> LedFeedback:
    settings = {"enabled": True, "shutdown_timeout": 1.5}
    settings.update(overrides)
    return LedFeedback(LedConfig(**settings), controller_factory=lambda: controller)


class TestLedFeedback(unittest.TestCase):
    def test_a_rule_reaches_the_controller_in_the_order_it_was_written(self) -> None:
        controller = FakeController()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        feedback.submit((event("wakeword_detected"), state("waiting")), live=True)
        self.assertTrue(wait_until(lambda: len(controller.calls) == 2))
        self.assertEqual(controller.verbs, ["emit_event", "set_state"])

    def test_a_timed_overlay_reaches_the_controller_worker(self) -> None:
        controller = FakeController()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        feedback.submit(
            (LedCall(LedVerb.SET_OVERLAY, target="countdown_ring"),),
            live=True,
        )

        self.assertTrue(wait_until(lambda: controller.calls))
        self.assertEqual(
            controller.calls,
            [("set_overlay", "countdown_ring", "on")],
        )

    def test_rebuilt_state_restores_but_never_re_announces(self) -> None:
        """A replay or a switch to live carries the rule that rebuilt the state.

        It must put the ring back where it belongs and must not fire the
        announcement that went with the original fact.
        """
        controller = FakeController()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        feedback.submit((event("success_event"), state("ready_state")), live=False)
        self.assertTrue(wait_until(lambda: controller.calls))
        self.assertEqual(controller.verbs, ["set_state"])

    def test_a_rule_of_only_announcements_is_dropped_entirely_when_not_live(self) -> None:
        controller = FakeController()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        self.assertFalse(feedback.submit((event("warn_event"),), live=False))
        self.assertFalse(feedback.is_running)

    def test_states_for_one_slot_are_coalesced_and_events_never_are(self) -> None:
        """Only the last state can be seen; every event has to be shown."""
        controller = FakeController()
        controller.gate = threading.Event()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        # Hold the worker inside the first call, then pile up behind it.
        feedback.submit((state("listening"),), live=True)
        self.assertTrue(controller.entered.wait(2.0))

        feedback.submit((state("thinking"),), live=True)
        feedback.submit((event("warn_event"),), live=True)
        feedback.submit((event("error_event"),), live=True)
        feedback.submit((state("ready_state"),), live=True)
        controller.gate.set()

        self.assertTrue(wait_until(lambda: len(controller.calls) == 4))
        self.assertEqual(
            controller.calls,
            [
                ("set_state", "listening", "primary", "on"),
                ("emit_event", "warn_event", None),
                ("emit_event", "error_event", None),
                ("set_state", "ready_state", "primary", "on"),
            ],
        )

    def test_a_background_state_does_not_supersede_a_primary_one(self) -> None:
        controller = FakeController()
        controller.gate = threading.Event()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        feedback.submit((state("listening"),), live=True)
        self.assertTrue(controller.entered.wait(2.0))
        feedback.submit((state("solid_fill", slot="background"),), live=True)
        feedback.submit((state("thinking"),), live=True)
        controller.gate.set()

        self.assertTrue(wait_until(lambda: len(controller.calls) == 3))
        self.assertEqual(
            [(item[1], item[2]) for item in controller.calls],
            [("listening", "primary"), ("solid_fill", "background"), ("thinking", "primary")],
        )

    def test_the_queue_is_bounded_when_nothing_is_being_consumed(self) -> None:
        controller = FakeController()
        controller.gate = threading.Event()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        feedback.submit((state("listening"),), live=True)
        self.assertTrue(controller.entered.wait(2.0))
        for index in range(MAX_PENDING + 20):
            feedback.submit((event(f"event_{index}"),), live=True)

        with feedback._condition:
            self.assertLessEqual(len(feedback._pending), MAX_PENDING)
        controller.gate.set()

    def test_a_failure_streak_is_reported_once(self) -> None:
        controller = FakeController()
        controller.fail_with = LedControllerError("device gone")
        reported: list[str] = []
        feedback = build(controller)
        feedback._on_failure = reported.append
        self.addCleanup(feedback.shutdown)

        for _ in range(4):
            feedback.submit((state("listening"),), live=True)
        self.assertTrue(wait_until(lambda: reported))
        time.sleep(0.1)
        self.assertEqual(reported, ["unavailable"])

    def test_recovery_arms_the_report_again(self) -> None:
        controller = FakeController()
        controller.fail_with = LedControllerError("device gone")
        reported: list[str] = []
        feedback = build(controller)
        feedback._on_failure = reported.append
        self.addCleanup(feedback.shutdown)

        feedback.submit((state("listening"),), live=True)
        self.assertTrue(wait_until(lambda: reported))

        controller.fail_with = None
        feedback.submit((state("thinking"),), live=True)
        self.assertTrue(wait_until(lambda: controller.calls))

        controller.fail_with = LedControllerError("gone again")
        feedback.submit((state("speaking"),), live=True)
        self.assertTrue(wait_until(lambda: len(reported) == 2))

    def test_the_sink_going_away_reports_through_the_same_debounce(self) -> None:
        controller = FakeController()
        reported: list[str] = []
        feedback = build(controller)
        feedback._on_failure = reported.append
        self.addCleanup(feedback.shutdown)

        feedback._on_sink_changed(False, "reSpeaker not connected")
        feedback._on_sink_changed(False, "reSpeaker not connected")
        self.assertEqual(reported, ["unavailable"])

        feedback._on_sink_changed(True, "")
        feedback._on_sink_changed(False, "gone again")
        self.assertEqual(reported, ["unavailable", "unavailable"])

    def test_a_disabled_output_starts_no_worker_and_forwards_nothing(self) -> None:
        controller = FakeController()
        feedback = build(controller, enabled=False)
        self.addCleanup(feedback.shutdown)

        self.assertFalse(feedback.submit((state("listening"),), live=True))
        self.assertFalse(feedback.is_running)
        self.assertEqual(controller.calls, [])

    def test_shutdown_mutes_the_output_and_closes_the_controller(self) -> None:
        controller = FakeController()
        feedback = build(controller)

        feedback.submit((state("listening"),), live=True)
        self.assertTrue(wait_until(lambda: controller.calls))
        self.assertTrue(feedback.shutdown())

        self.assertTrue(wait_until(lambda: controller.closed))
        self.assertIn(("set_output", None, False), controller.calls)

    def test_shutdown_without_a_worker_still_releases_the_controller(self) -> None:
        controller = FakeController()
        feedback = build(controller)

        self.assertTrue(feedback.shutdown())
        self.assertTrue(controller.closed)

    def test_shutdown_is_bounded_when_a_call_stalls(self) -> None:
        controller = FakeController()
        controller.gate = threading.Event()
        self.addCleanup(controller.gate.set)
        feedback = build(controller, shutdown_timeout=0.2)

        feedback.submit((state("listening"),), live=True)
        self.assertTrue(controller.entered.wait(2.0))

        started = time.monotonic()
        self.assertFalse(feedback.shutdown())
        self.assertLess(time.monotonic() - started, 2.0)
        # The controller is deliberately left open: the worker is still inside
        # a call that owns it.
        self.assertFalse(controller.closed)

    def test_submitting_after_shutdown_is_refused(self) -> None:
        controller = FakeController()
        feedback = build(controller)
        self.assertTrue(feedback.shutdown())
        self.assertFalse(feedback.submit((state("listening"),), live=True))


class TestDeviceMute(unittest.TestCase):
    """The device's own mute line, and the ring going dark with it."""

    def test_muting_pulls_the_line_and_silences_the_ring(self) -> None:
        controller = FakeController()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        self.assertTrue(feedback.set_device_mute(True))
        self.assertIn(("set_device_mute", True), controller.calls)
        self.assertIn(("set_output", None, False), controller.calls)

    def test_unmuting_restores_the_ring_without_rebuilding_a_state(self) -> None:
        """The output is re-enabled, not re-driven: whatever state was active is
        still active and simply becomes visible again."""
        controller = FakeController()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        feedback.set_device_mute(True)
        controller.calls.clear()
        feedback.set_device_mute(False)

        self.assertEqual(
            controller.calls,
            [("set_device_mute", False), ("set_output", None, True)],
        )

    def test_a_mute_that_cannot_reach_the_device_says_so(self) -> None:
        controller = FakeController()
        controller.mute_reaches_device = False
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        self.assertFalse(feedback.set_device_mute(True))
        # The ring is still silenced: the half that works still has to work.
        self.assertIn(("set_output", None, False), controller.calls)

    def test_a_failing_mute_line_is_not_swallowed(self) -> None:
        controller = FakeController()
        controller.mute_fails = True
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        with self.assertRaises(LedControllerError):
            feedback.set_device_mute(True)

    def test_the_mute_state_can_be_read_back(self) -> None:
        controller = FakeController()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        controller.mute_state = True
        self.assertIs(feedback.device_mute(), True)
        controller.mute_state = None
        self.assertIsNone(feedback.device_mute())


class TestAvailabilityClock(unittest.TestCase):
    """How long the output has been unreachable, which decides what is offered."""

    def test_a_standing_sink_fault_survives_commands_that_return(self) -> None:
        """Neither sink raises from a frame, so a call completing proves nothing.

        If it cleared the fault, the clock would reset on every piece of
        feedback and an unreachable ring would never look unreachable for long.
        """
        controller = FakeController()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        feedback._on_sink_changed(False, "no ring window connected")
        first = feedback.unavailable_seconds
        self.assertGreaterEqual(first, 0.0)

        feedback.submit((state("listening"),), live=True)
        self.assertTrue(wait_until(lambda: controller.calls))
        time.sleep(0.05)
        self.assertGreater(feedback.unavailable_seconds, first)

    def test_the_clock_stops_when_the_sink_comes_back(self) -> None:
        controller = FakeController()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        feedback._on_sink_changed(False, "gone")
        self.assertGreater(feedback.unavailable_seconds, -1.0)
        feedback._on_sink_changed(True, "")
        self.assertEqual(feedback.unavailable_seconds, 0.0)

    def test_a_working_output_reports_no_wait(self) -> None:
        controller = FakeController()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)
        self.assertEqual(feedback.unavailable_seconds, 0.0)


class TestTargetVerification(unittest.TestCase):
    def test_every_unknown_target_is_named_at_once(self) -> None:
        controller = FakeController()
        controller.unknown = {"nonesuch", "also_missing"}
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)

        with self.assertRaises(LedConfigurationError) as caught:
            feedback.verify_targets(["listening", "nonesuch", "also_missing"])
        message = str(caught.exception)
        self.assertIn("nonesuch", message)
        self.assertIn("also_missing", message)
        self.assertNotIn("  listening:", message)

    def test_a_complete_mapping_passes_quietly(self) -> None:
        controller = FakeController()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)
        feedback.verify_targets(["listening", "thinking"])
        self.assertFalse(feedback.is_running)


if __name__ == "__main__":
    unittest.main()


class TestFollowingTheDeviceMuteLine(unittest.TestCase):
    """X0D30 is the mute function, not the button.

    It reads the same whether this application pulled it or somebody pressed the
    device, so the client follows the line rather than owning it.
    """

    def build_watching(self, controller: FakeController):
        seen: list[bool] = []
        feedback = LedFeedback(
            LedConfig(enabled=True, shutdown_timeout=1.5),
            controller_factory=lambda: controller,
            on_device_mute_changed=seen.append,
        )
        self.addCleanup(feedback.shutdown)
        return feedback, seen

    def test_a_line_that_moves_on_its_own_is_reported(self) -> None:
        controller = FakeController()
        controller.mute_state = False
        feedback, seen = self.build_watching(controller)
        feedback.watch_device_mute()

        self.assertTrue(wait_until(lambda: feedback._known_device_mute is False))
        controller.mute_state = True
        self.assertTrue(wait_until(lambda: seen == [True], timeout=4.0))

    def test_a_quiet_device_says_nothing(self) -> None:
        """The first reading only establishes what unchanged means."""
        controller = FakeController()
        controller.mute_state = False
        feedback, seen = self.build_watching(controller)
        feedback.watch_device_mute()

        self.assertTrue(wait_until(lambda: feedback._known_device_mute is False))
        time.sleep(1.5)
        self.assertEqual(seen, [])

    def test_a_device_already_muted_when_found_announces_itself(self) -> None:
        controller = FakeController()
        controller.mute_state = True
        feedback, seen = self.build_watching(controller)
        feedback.watch_device_mute()
        self.assertTrue(wait_until(lambda: seen == [True], timeout=4.0))

    def test_what_we_set_ourselves_is_not_reported_back(self) -> None:
        controller = FakeController()
        controller.mute_state = False
        feedback, seen = self.build_watching(controller)
        feedback.watch_device_mute()
        self.assertTrue(wait_until(lambda: feedback._known_device_mute is False))

        feedback.set_device_mute(True)
        controller.mute_state = True
        feedback.note_device_mute(True)

        time.sleep(1.5)
        self.assertEqual(seen, [])

    def test_an_unreadable_line_is_not_a_change(self) -> None:
        controller = FakeController()
        controller.mute_state = None
        feedback, seen = self.build_watching(controller)
        feedback.watch_device_mute()
        time.sleep(1.5)
        self.assertEqual(seen, [])
        self.assertIsNone(feedback._known_device_mute)

    def test_watching_is_not_started_without_a_listener(self) -> None:
        controller = FakeController()
        feedback = build(controller)
        self.addCleanup(feedback.shutdown)
        feedback.watch_device_mute()
        self.assertFalse(feedback.is_running)
