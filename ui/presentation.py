"""Pure presentation mapping for the AP06 tray and overlay."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from core.controller import (
    AvailabilityState,
    ControllerStatusSnapshot,
    DictationState,
    DictationWindowPhase,
    TransientEvent,
    TransientEventType,
)
from core.history import HistoryEntry
from core.event_models import (
    CanonicalEventType,
    FeedbackImpulse,
)
from core.feedback_mapping import AppActionId
from core.feedback_reducer import FeedbackDecision
from core.stt_session import SessionState


class IndicatorColor(str, Enum):
    DARK_GREEN = "#176b3a"
    GREEN = "#35c759"
    DARK_BLUE = "#174a7e"
    BLUE = "#3b9cff"
    YELLOW = "#f4c542"
    RED = "#ef4444"
    GRAY = "#7f8c8d"


@dataclass(frozen=True)
class TrayPresentation:
    color: IndicatorColor
    status_text: str
    tooltip: str
    toggle_text: str
    toggle_enabled: bool
    border_color: str | None = None


@dataclass(frozen=True)
class FeedbackPresentation:
    color: IndicatorColor
    text: str
    duration_ms: int = 1000


@dataclass(frozen=True)
class MappedAppPresentation:
    color: IndicatorColor
    status_text: str
    border_color: str | None = None
    duration_ms: int | None = None


_AVAILABILITY_PRESENTATION = {
    AvailabilityState.STARTING: (IndicatorColor.YELLOW, "Startet"),
    AvailabilityState.CONNECTING: (IndicatorColor.YELLOW, "Verbindet"),
    AvailabilityState.READY: (IndicatorColor.DARK_GREEN, "Bereit"),
    AvailabilityState.NETWORK_UNAVAILABLE: (
        IndicatorColor.YELLOW,
        "Netzwerk nicht verfügbar",
    ),
    AvailabilityState.SERVER_BUSY: (
        IndicatorColor.YELLOW,
        "Server ausgelastet",
    ),
    AvailabilityState.SERVER_UNAVAILABLE: (
        IndicatorColor.YELLOW,
        "Server nicht verfügbar",
    ),
    AvailabilityState.PROTOCOL_ERROR: (
        IndicatorColor.RED,
        "Protokollfehler",
    ),
    AvailabilityState.MICROPHONE_UNAVAILABLE: (
        IndicatorColor.YELLOW,
        "Mikrofon nicht verfügbar",
    ),
    AvailabilityState.SHUTTING_DOWN: (IndicatorColor.GRAY, "Wird beendet"),
    AvailabilityState.STOPPED: (IndicatorColor.GRAY, "Beendet"),
}


def presentation_for_snapshot(
    snapshot: ControllerStatusSnapshot,
) -> TrayPresentation:
    """Map one immutable controller snapshot to stable tray presentation."""
    color, text = _AVAILABILITY_PRESENTATION[snapshot.availability_state]
    border_color = None

    if snapshot.availability_state == AvailabilityState.READY:
        if snapshot.operating_mode == "wake_word":
            if snapshot.dictation_state == DictationState.IDLE:
                color, text = IndicatorColor.GRAY, "Wake Word pausiert"
            elif snapshot.dictation_state == DictationState.STARTING:
                color, text = IndicatorColor.DARK_BLUE, "Wake Word startet"
                border_color = "#ffffff"
            elif snapshot.server_status in {
                SessionState.VOICE,
                SessionState.SILENCE,
                SessionState.RECORDING,
            }:
                color, text = IndicatorColor.BLUE, "Sprache wird aufgenommen"
            elif snapshot.server_status in {
                SessionState.LISTENING,
                SessionState.WAKEWORD_DETECTED,
            }:
                color, text = IndicatorColor.DARK_BLUE, "Wartet auf Sprache"
                border_color = "#ffffff"
            elif snapshot.server_status == SessionState.TRANSCRIBING:
                color, text = IndicatorColor.DARK_BLUE, "Transkribiert"
            else:
                color, text = IndicatorColor.DARK_BLUE, "Wartet auf Wake Word"
        else:
            if snapshot.dictation_state == DictationState.IDLE:
                color, text = IndicatorColor.DARK_GREEN, "Wartet auf Hotkey"
            elif (
                snapshot.dictation_state == DictationState.ACTIVE
                and snapshot.dictation_window_phase
                == DictationWindowPhase.SEGMENT_ACTIVE
            ):
                color, text = IndicatorColor.GREEN, "Sprache wird aufgenommen"
            else:
                color = IndicatorColor.DARK_GREEN
                border_color = "#ffffff"
                if (
                    snapshot.dictation_window_phase
                    == DictationWindowPhase.FOLLOWUP_WAIT
                ):
                    text = "Wartet auf Fortsetzung"
                else:
                    text = "Wartet auf Sprache"

    toggle_active = snapshot.dictation_state in {
        DictationState.STARTING,
        DictationState.ACTIVE,
    }
    if snapshot.operating_mode == "wake_word":
        toggle_text = "Wake Word pausieren" if toggle_active else "Wake Word aktivieren"
    elif toggle_active:
        toggle_text = "Diktatzeit verlängern"
    else:
        toggle_text = "Diktat starten"
    toggle_enabled = (
        not snapshot.is_closing
        and snapshot.availability_state
        not in {AvailabilityState.SHUTTING_DOWN, AvailabilityState.STOPPED}
    )

    tooltip_parts = [f"RealtimeSTT – {text}"]
    if snapshot.next_retry_delay is not None:
        tooltip_parts.append(
            f"Nächster Verbindungsversuch in {snapshot.next_retry_delay:.1f} s"
        )

    return TrayPresentation(
        color=color,
        status_text=text,
        tooltip="\n".join(tooltip_parts),
        toggle_text=toggle_text,
        toggle_enabled=toggle_enabled,
        border_color=border_color,
    )


def presentation_for_feedback(event: TransientEvent) -> FeedbackPresentation:
    """Create one non-modal, short-lived feedback presentation."""
    reason = event.reason.casefold()
    if "microphone" in reason or "audio_device" in reason:
        color = IndicatorColor.YELLOW
        text = "Mikrofon derzeit nicht verfügbar"
    elif any(
        marker in reason
        for marker in (
            "network",
            "transport",
            "not_ready",
            "connection",
            "ping",
            "server_busy",
            "server_unavailable",
            "timeout",
        )
    ):
        color = IndicatorColor.YELLOW
        text = "Diktat derzeit nicht verfügbar"
    else:
        color = IndicatorColor.RED
        text = event.description.strip() or "Aktion fehlgeschlagen"

    if event.event_type == TransientEventType.DICTATION_INTERRUPTED:
        text = "Diktat wurde wegen einer Verbindungsstörung beendet"
    elif event.event_type == TransientEventType.DICTATION_START_FAILED:
        if "audio" in reason or "microphone" in reason:
            color = IndicatorColor.YELLOW
            text = "Mikrofon konnte nicht gestartet werden"
        elif "timeout" in reason:
            text = "Server hat den Diktatstart nicht bestätigt"
        else:
            text = "Diktat konnte nicht gestartet werden"
    return FeedbackPresentation(color=color, text=text)


def presentation_for_mapped_action(
    action: AppActionId,
    *,
    operating_mode: str,
) -> MappedAppPresentation:
    """Translate a configured in-app action without inspecting server strings."""
    mode_color = (
        IndicatorColor.DARK_BLUE
        if operating_mode == "wake_word"
        else IndicatorColor.DARK_GREEN
    )
    active_color = (
        IndicatorColor.BLUE
        if operating_mode == "wake_word"
        else IndicatorColor.GREEN
    )
    mapped = {
        AppActionId.INDICATOR_IDLE: MappedAppPresentation(
            mode_color,
            "Wartet auf Wake Word" if operating_mode == "wake_word" else "Wartet auf Hotkey",
        ),
        AppActionId.INDICATOR_WAITING_FOR_WAKE_WORD: MappedAppPresentation(
            mode_color,
            "Wartet auf Wake Word",
        ),
        AppActionId.INDICATOR_WAITING_FOR_SPEECH: MappedAppPresentation(
            mode_color,
            "Wartet auf Sprache",
            border_color="#ffffff",
        ),
        AppActionId.INDICATOR_RECORDING: MappedAppPresentation(
            active_color,
            "Sprache wird aufgenommen",
        ),
        AppActionId.INDICATOR_FINALIZING: MappedAppPresentation(
            mode_color,
            "Transkribiert",
        ),
        AppActionId.INDICATOR_SUCCESS: MappedAppPresentation(
            active_color,
            "Transkription abgeschlossen",
            duration_ms=900,
        ),
        AppActionId.INDICATOR_WARNING: MappedAppPresentation(
            IndicatorColor.YELLOW,
            "Feedback eingeschränkt",
            duration_ms=1200,
        ),
        AppActionId.INDICATOR_ERROR: MappedAppPresentation(
            IndicatorColor.RED,
            "Aktion fehlgeschlagen",
            duration_ms=1400,
        ),
    }
    return mapped[action]


def presentation_for_feedback_decision(
    decision: FeedbackDecision,
    *,
    operating_mode: str,
) -> FeedbackPresentation | None:
    """Create optional overlay feedback from one already mapped decision."""
    if not decision.publish or decision.replay or decision.rule.app is None:
        return None
    mapped = presentation_for_mapped_action(
        decision.rule.app.action,
        operating_mode=operating_mode,
    )
    text = mapped.status_text
    if decision.event is not None:
        if (
            decision.event.event_type
            is CanonicalEventType.CLIENT_EVENT_STREAM_DEGRADED
        ):
            text = "Event-Feedback vorübergehend eingeschränkt"
        elif decision.event.impulse is not None:
            text = {
                FeedbackImpulse.WAKE_WORD_DETECTED: "Wake Word erkannt",
                FeedbackImpulse.RECORDING_STARTED: "Aufnahme läuft",
                FeedbackImpulse.RECORDING_ENDED: "Transkription wird verarbeitet",
                FeedbackImpulse.TRANSCRIPTION_COMPLETED: "Transkription abgeschlossen",
                FeedbackImpulse.TRANSCRIPTION_FAILED: "Transkription fehlgeschlagen",
                FeedbackImpulse.DICTATION_INTERRUPTED: "Diktat wurde unterbrochen",
                FeedbackImpulse.MICROPHONE_LOST: "Mikrofon derzeit nicht verfügbar",
                FeedbackImpulse.INJECTION_FAILED: "Text konnte nicht eingefügt werden",
                FeedbackImpulse.ACTION_BLOCKED: "Aktion derzeit nicht verfügbar",
            }[decision.event.impulse]
    return FeedbackPresentation(
        color=mapped.color,
        text=text,
        duration_ms=mapped.duration_ms or 1000,
    )


def format_history_label(entry: HistoryEntry, max_characters: int = 72) -> str:
    """Format a one-line, bounded label while preserving the entry identity."""
    if max_characters < 12:
        raise ValueError("max_characters must be >= 12")
    text = " ".join((entry.text or "").split())
    if not text:
        text = "(Leerer Text)"
    if len(text) > max_characters:
        text = text[: max_characters - 1].rstrip() + "…"
    timestamp = datetime.fromtimestamp(entry.timestamp).strftime("%H:%M")
    return f"{timestamp}  {text}"
