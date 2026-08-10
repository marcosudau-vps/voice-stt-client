"""Offscreen Qt tests for AP06 presentation, tray, and passive overlay."""

from __future__ import annotations

import os
import time
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from core.config import OverlayConfig
from core.event_models import (
    CanonicalEventType,
    EventOrigin,
    FeedbackSource,
    FeedbackState,
    NormalizedFeedbackEvent,
)
from core.feedback_mapping import AppActionId, AppEffect, FeedbackRule
from core.feedback_reducer import FeedbackDecision
from core.controller import (
    AvailabilityState,
    ControllerStatusSnapshot,
    DictationState,
    DictationWindowPhase,
    TransientEvent,
    TransientEventType,
)
from core.history import HistoryEntry
from core.stt_session import SessionState
from ui.overlay import TranscriptOverlay
from ui.presentation import (
    IndicatorColor,
    format_history_label,
    presentation_for_feedback_decision,
    presentation_for_feedback,
    presentation_for_mapped_action,
    presentation_for_snapshot,
)
from ui.tray import TrayController, create_status_icon


def snapshot(
    availability=AvailabilityState.READY,
    dictation=DictationState.IDLE,
    *,
    description="",
    next_retry_delay=None,
    operating_mode="hotkey",
    phase=DictationWindowPhase.INACTIVE,
    server_status=SessionState.IDLE,
):
    return ControllerStatusSnapshot(
        availability_state=availability,
        dictation_state=dictation,
        reason_code=availability.value,
        description=description,
        reconnect_attempt=0,
        next_retry_delay=next_retry_delay,
        session_id="session",
        generation=1,
        revision=1,
        is_running=True,
        is_closing=False,
        queue_size=0,
        operating_mode=operating_mode,
        dictation_window_phase=phase,
        server_status=server_status,
    )


class QtTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])


class TestPresentationMapping(unittest.TestCase):
    def test_all_availability_states_have_a_presentation(self):
        for availability in AvailabilityState:
            with self.subTest(availability=availability):
                result = presentation_for_snapshot(snapshot(availability))
                self.assertTrue(result.status_text)
                self.assertTrue(result.tooltip)

    def test_hotkey_mode_uses_dark_rimmed_and_bright_green_phases(self):
        idle = presentation_for_snapshot(snapshot())
        starting = presentation_for_snapshot(
            snapshot(dictation=DictationState.STARTING)
        )
        active = presentation_for_snapshot(
            snapshot(
                dictation=DictationState.ACTIVE,
                phase=DictationWindowPhase.SEGMENT_ACTIVE,
            )
        )
        followup = presentation_for_snapshot(
            snapshot(
                dictation=DictationState.ACTIVE,
                phase=DictationWindowPhase.FOLLOWUP_WAIT,
            )
        )
        self.assertEqual(idle.color, IndicatorColor.DARK_GREEN)
        self.assertIsNone(idle.border_color)
        self.assertEqual(starting.color, IndicatorColor.DARK_GREEN)
        self.assertEqual(starting.border_color, "#ffffff")
        self.assertEqual(starting.toggle_text, "Diktatzeit verlängern")
        self.assertEqual(active.color, IndicatorColor.GREEN)
        self.assertIsNone(active.border_color)
        self.assertEqual(active.status_text, "Sprache wird aufgenommen")
        self.assertEqual(followup.color, IndicatorColor.DARK_GREEN)
        self.assertEqual(followup.border_color, "#ffffff")

    def test_wake_word_mode_uses_dark_rimmed_and_bright_blue_phases(self):
        waiting = presentation_for_snapshot(
            snapshot(
                dictation=DictationState.ACTIVE,
                operating_mode="wake_word",
                server_status=SessionState.WAKEWORD_WAIT,
            )
        )
        detected = presentation_for_snapshot(
            snapshot(
                dictation=DictationState.ACTIVE,
                operating_mode="wake_word",
                server_status=SessionState.WAKEWORD_DETECTED,
            )
        )
        recording = presentation_for_snapshot(
            snapshot(
                dictation=DictationState.ACTIVE,
                operating_mode="wake_word",
                server_status=SessionState.RECORDING,
            )
        )
        self.assertEqual(waiting.color, IndicatorColor.DARK_BLUE)
        self.assertIsNone(waiting.border_color)
        self.assertEqual(detected.color, IndicatorColor.DARK_BLUE)
        self.assertEqual(detected.border_color, "#ffffff")
        self.assertEqual(recording.color, IndicatorColor.BLUE)
        self.assertIsNone(recording.border_color)

    def test_external_unavailability_is_yellow_and_protocol_is_red(self):
        external_states = {
            AvailabilityState.NETWORK_UNAVAILABLE,
            AvailabilityState.SERVER_BUSY,
            AvailabilityState.SERVER_UNAVAILABLE,
            AvailabilityState.MICROPHONE_UNAVAILABLE,
        }
        for availability in external_states:
            with self.subTest(availability=availability):
                self.assertEqual(
                    presentation_for_snapshot(snapshot(availability)).color,
                    IndicatorColor.YELLOW,
                )
        self.assertEqual(
            presentation_for_snapshot(
                snapshot(AvailabilityState.PROTOCOL_ERROR)
            ).color,
            IndicatorColor.RED,
        )

    def test_retry_delay_is_visible_only_in_tooltip(self):
        result = presentation_for_snapshot(
            snapshot(
                AvailabilityState.NETWORK_UNAVAILABLE,
                description="offline",
                next_retry_delay=2.5,
            )
        )
        self.assertIn("2.5 s", result.tooltip)

    def test_feedback_distinguishes_network_microphone_and_protocol(self):
        def event(reason):
            return TransientEvent(
                TransientEventType.ACTION_BLOCKED,
                reason,
                "",
                time.time(),
                "start_dictation",
            )

        self.assertEqual(
            presentation_for_feedback(event("transport_not_ready")).color,
            IndicatorColor.YELLOW,
        )
        self.assertEqual(
            presentation_for_feedback(event("microphone_unavailable")).color,
            IndicatorColor.YELLOW,
        )
        self.assertEqual(
            presentation_for_feedback(event("protocol_error")).color,
            IndicatorColor.RED,
        )

    def test_history_label_is_single_line_and_bounded(self):
        entry = HistoryEntry(
            id="id",
            session_id="s",
            segment_id=1,
            timestamp=0,
            text="Eine\nsehr   lange " + "Eingabe " * 20,
            text_length=200,
        )
        label = format_history_label(entry, 40)
        self.assertNotIn("\n", label)
        self.assertLessEqual(len(label.split("  ", 1)[1]), 40)
        self.assertTrue(label.endswith("…"))

    def test_mapped_app_action_preserves_operating_mode_color(self):
        hotkey = presentation_for_mapped_action(
            AppActionId.INDICATOR_RECORDING,
            operating_mode="hotkey",
        )
        wake_word = presentation_for_mapped_action(
            AppActionId.INDICATOR_RECORDING,
            operating_mode="wake_word",
        )

        self.assertEqual(hotkey.color, IndicatorColor.GREEN)
        self.assertEqual(wake_word.color, IndicatorColor.BLUE)

    def test_unpublished_decision_has_no_overlay_presentation(self):
        decision = FeedbackDecision(
            state=FeedbackState.RECORDING,
            source=FeedbackSource.EVENT_STREAM,
            rule=FeedbackRule(
                app=AppEffect(AppActionId.INDICATOR_RECORDING)
            ),
            publish=False,
            replay=True,
        )
        self.assertIsNone(
            presentation_for_feedback_decision(
                decision,
                operating_mode="hotkey",
            )
        )


class TestTranscriptOverlay(QtTestBase):
    def setUp(self):
        self.config = OverlayConfig(fade_after=0)
        self.overlay = TranscriptOverlay(self.config)
        self.addCleanup(self.overlay.close)

    def test_window_is_focus_and_input_transparent(self):
        flags = self.overlay.windowFlags()
        self.assertTrue(flags & Qt.WindowType.FramelessWindowHint)
        self.assertTrue(flags & Qt.WindowType.WindowStaysOnTopHint)
        self.assertTrue(flags & Qt.WindowType.WindowDoesNotAcceptFocus)
        self.assertTrue(flags & Qt.WindowType.WindowTransparentForInput)
        self.assertEqual(self.overlay.focusPolicy(), Qt.FocusPolicy.NoFocus)
        self.assertTrue(
            self.overlay.testAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents
            )
        )

    def test_realtime_replaces_text_and_final_fades(self):
        self.overlay.show_transcript("Erster Stand", False)
        self.overlay.show_transcript("Korrigierter Stand", False)
        self.assertEqual(self.overlay.label.text(), "Korrigierter Stand")
        self.assertTrue(self.overlay.isVisible())

        self.overlay.show_transcript("Finaler Text", True)
        QTest.qWait(350)
        self.assertEqual(self.overlay.label.text(), "Finaler Text")
        self.assertFalse(self.overlay.isVisible())

    def test_feedback_uses_requested_color(self):
        feedback = presentation_for_feedback(
            TransientEvent(
                TransientEventType.ACTION_BLOCKED,
                "microphone_unavailable",
                "Mikrofon fehlt",
                time.time(),
            )
        )
        self.overlay.show_feedback(feedback)
        self.assertIn(IndicatorColor.YELLOW.value, self.overlay.label.styleSheet())


class TestTrayController(QtTestBase):
    def setUp(self):
        self.calls = []
        self.tray = TrayController(
            on_toggle=lambda: self.calls.append("toggle"),
            on_reinsert_last=lambda: self.calls.append("last"),
            on_reinsert_entry=lambda entry_id: self.calls.append(entry_id),
            on_request_history=lambda: self.calls.append("history"),
            on_quit=lambda: self.calls.append("quit"),
        )
        self.addCleanup(self.tray.tray.hide)

    def test_snapshot_updates_status_toggle_and_tooltip(self):
        self.tray.update_snapshot(
            snapshot(
                dictation=DictationState.ACTIVE,
                phase=DictationWindowPhase.SEGMENT_ACTIVE,
            )
        )
        self.assertEqual(
            self.tray.status_action.text(), "Sprache wird aufgenommen"
        )
        self.assertEqual(
            self.tray.toggle_action.text(), "Diktatzeit verlängern"
        )
        self.assertIn("Sprache wird aufgenommen", self.tray.tray.toolTip())

    def test_event_stream_degradation_is_secondary_and_keeps_mode_color(self):
        self.tray.update_snapshot(
            snapshot(
                dictation=DictationState.ACTIVE,
                phase=DictationWindowPhase.SEGMENT_ACTIVE,
            )
        )
        before = self.tray.status_action.text()
        decision = FeedbackDecision(
            state=FeedbackState.RECORDING,
            source=FeedbackSource.STT_FALLBACK,
            rule=FeedbackRule(
                app=AppEffect(AppActionId.INDICATOR_WARNING)
            ),
            event=NormalizedFeedbackEvent(
                event_type=CanonicalEventType.CLIENT_EVENT_STREAM_DEGRADED,
                origin=EventOrigin.LOCAL,
                source=FeedbackSource.LOCAL_ONLY,
            ),
        )

        self.tray.update_feedback_decision(decision)

        self.assertEqual(self.tray.status_action.text(), before)
        self.assertIn("STT-Fallback aktiv", self.tray.tray.toolTip())

    def test_status_icon_renders_requested_white_border(self):
        image = create_status_icon(
            IndicatorColor.DARK_GREEN,
            border_color="#ffffff",
        ).pixmap(32, 32).toImage()
        self.assertEqual(image.pixelColor(16, 4).name(), "#ffffff")
        self.assertEqual(
            image.pixelColor(16, 16).name(),
            IndicatorColor.DARK_GREEN.value,
        )

    def test_history_actions_are_id_bound_and_empty_state_is_honest(self):
        entries = [
            HistoryEntry("new", "s", 2, 2.0, "Neuer Text", 10),
            HistoryEntry("old", "s", 1, 1.0, "Alter Text", 10),
        ]
        self.tray.set_history_entries(entries)
        actions = self.tray.history_menu.actions()
        self.assertEqual([action.data() for action in actions], ["new", "old"])
        actions[1].trigger()
        self.assertEqual(self.calls, ["old"])

        self.tray.set_history_entries(())
        empty = self.tray.history_menu.actions()[0]
        self.assertFalse(empty.isEnabled())
        self.assertIn("keine", empty.text().casefold())

    def test_about_to_show_requests_fresh_history(self):
        self.tray._request_history()
        self.assertEqual(self.calls, ["history"])
        self.assertIn(
            "geladen",
            self.tray.history_menu.actions()[0].text().casefold(),
        )


if __name__ == "__main__":
    unittest.main()


class TestMappedActionCatalogueIsComplete(QtTestBase):
    """Every in-app action a rule may name has to produce a presentation.

    ``presentation_for_mapped_action`` ends in a dict lookup, so an action
    without an entry raises KeyError while feedback is being shown rather than
    degrading to something dull. Parametrised over the enum, in both operating
    modes, because the mapping branches on the mode.
    """

    def test_every_action_renders_in_both_modes(self) -> None:
        for action in AppActionId:
            for mode in ("hotkey", "wake_word"):
                with self.subTest(action=action, mode=mode):
                    presentation = presentation_for_mapped_action(
                        action, operating_mode=mode
                    )
                    self.assertTrue(presentation.status_text.strip())
                    self.assertIsInstance(presentation.color, IndicatorColor)

    def test_transient_actions_say_how_long_they_last(self) -> None:
        """Success, warning and error announce something and then give the
        indicator back; the lasting ones must not carry a duration."""
        transient = {
            AppActionId.INDICATOR_SUCCESS,
            AppActionId.INDICATOR_WARNING,
            AppActionId.INDICATOR_ERROR,
        }
        for action in AppActionId:
            with self.subTest(action=action):
                presentation = presentation_for_mapped_action(
                    action, operating_mode="hotkey"
                )
                if action in transient:
                    self.assertIsNotNone(presentation.duration_ms)
                    self.assertGreater(presentation.duration_ms, 0)
                else:
                    self.assertIsNone(presentation.duration_ms)

    def test_the_mode_changes_the_colour_but_never_the_vocabulary(self) -> None:
        for action in AppActionId:
            with self.subTest(action=action):
                hotkey = presentation_for_mapped_action(action, operating_mode="hotkey")
                wake = presentation_for_mapped_action(action, operating_mode="wake_word")
                self.assertEqual(hotkey.duration_ms, wake.duration_ms)
