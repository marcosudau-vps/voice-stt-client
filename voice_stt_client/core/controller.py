"""Shared immutable result and presentation types; no runtime controller."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .stt_session import SessionState


class FinalProcessingStatus(str, Enum):
    """Result status of processing a raw final transcript event."""

    QUEUED = "queued"
    DEDUPLICATED = "deduplicated"
    INVALID_FINAL = "invalid_final"
    HISTORY_UNAVAILABLE = "history_unavailable"
    QUEUE_UNAVAILABLE = "queue_unavailable"
    FAILED = "failed"


class AvailabilityState(str, Enum):
    """UI-neutral availability state of the controller."""

    STARTING = "starting"
    CONNECTING = "connecting"
    READY = "ready"
    NETWORK_UNAVAILABLE = "network_unavailable"
    SERVER_BUSY = "server_busy"
    SERVER_UNAVAILABLE = "server_unavailable"
    PROTOCOL_ERROR = "protocol_error"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"
    MICROPHONE_UNAVAILABLE = "microphone_unavailable"


class DictationState(str, Enum):
    """UI-neutral dictation state."""

    IDLE = "idle"
    STARTING = "starting"
    ACTIVE = "active"


class DictationWindowPhase(str, Enum):
    """Hotkey-mode phase driven by authoritative server timeline events."""

    INACTIVE = "inactive"
    WAITING_FIRST_SPEECH = "waiting_first_speech"
    SEGMENT_ACTIVE = "segment_active"
    FOLLOWUP_WAIT = "followup_wait"


class TransientEventType(str, Enum):
    """UI-neutral transient feedback event types."""

    ACTION_BLOCKED = "action_blocked"
    DICTATION_START_FAILED = "dictation_start_failed"
    DICTATION_INTERRUPTED = "dictation_interrupted"


@dataclass(frozen=True)
class TransientEvent:
    """UI-neutral transient feedback event payload."""

    event_type: TransientEventType
    reason: str
    description: str
    timestamp: float
    action: Optional[str] = None


@dataclass(frozen=True)
class ControllerStatusSnapshot:
    """Complete UI-neutral status snapshot for UI and diagnostics."""

    availability_state: AvailabilityState
    dictation_state: DictationState
    reason_code: str
    description: str
    reconnect_attempt: int
    next_retry_delay: Optional[float]
    session_id: Optional[str]
    generation: int
    revision: int
    is_running: bool
    is_closing: bool
    queue_size: int
    operating_mode: str = "hotkey"
    dictation_window_phase: DictationWindowPhase = DictationWindowPhase.INACTIVE
    server_status: SessionState = SessionState.IDLE


@dataclass(frozen=True)
class FinalProcessingResult:
    """UI-neutral result container for a processed final transcript event."""

    status: FinalProcessingStatus
    session_id: Optional[str] = None
    segment_id: int | str | None = None
    text: Optional[str] = None
    entry_id: Optional[str] = None
    reason: Optional[str] = None
    error: Optional[str] = None
    is_conflict: bool = False
    activation_id: str | None = None
    segment_sequence: int | None = None
    event_id: str | None = None
    event_seq: int | None = None
    generation: int | None = None


@dataclass(frozen=True)
class CommandResult:
    """UI-neutral result for semantic controller commands."""

    success: bool
    status: str
    message: Optional[str] = None
