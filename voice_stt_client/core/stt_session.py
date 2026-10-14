"""Legacy presentation enums, no socket or protocol implementation."""
from __future__ import annotations
from enum import Enum, auto


class TransportState(Enum):
    """WebSocket connection lifecycle states."""
    DISCONNECTED = auto()
    CONNECTING = auto()
    ADMITTED = auto()   # hello received
    READY = auto()      # ready(ok=true) received
    ERROR = auto()


class SessionState(Enum):
    """Server-reported session states, grouped for UI."""
    IDLE = "idle"
    LISTENING = "listening"
    VOICE = "voice"
    SILENCE = "silence"
    WAKEWORD_WAIT = "wakeword_wait"
    WAKEWORD_DETECTED = "wakeword_detected"
    WAKEWORD_TIMEOUT = "wakeword_timeout"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    CLOSED = "closed"
    UNKNOWN = "unknown"

    @classmethod
    def from_server(cls, value: str) -> SessionState:
        """Parse server state string, defaulting to UNKNOWN for forward compat."""
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN
