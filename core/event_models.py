"""Transport-neutral models for the AP07 event and feedback pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


class EventConnectionState(str, Enum):
    UNAVAILABLE = "unavailable"
    CONNECTING = "connecting"
    SUBSCRIBING = "subscribing"
    REPLAYING = "replaying"
    LIVE = "live"
    DEGRADED = "degraded"
    BACKOFF = "backoff"
    STOPPED = "stopped"


class FeedbackSource(str, Enum):
    EVENT_STREAM = "event_stream"
    STT_FALLBACK = "stt_fallback"
    LOCAL_ONLY = "local_only"


class EventOrigin(str, Enum):
    LIVE = "live"
    REPLAY = "replay"
    LOCAL = "local"


class FeedbackState(str, Enum):
    IDLE = "idle"
    WAITING_FOR_WAKE_WORD = "waiting_for_wake_word"
    STARTING = "starting"
    RECORDING = "recording"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class FeedbackImpulse(str, Enum):
    WAKE_WORD_DETECTED = "wake_word_detected"
    RECORDING_STARTED = "recording_started"
    RECORDING_ENDED = "recording_ended"
    TRANSCRIPTION_COMPLETED = "transcription_completed"
    TRANSCRIPTION_FAILED = "transcription_failed"
    DICTATION_INTERRUPTED = "dictation_interrupted"
    MICROPHONE_LOST = "microphone_lost"
    INJECTION_FAILED = "injection_failed"
    ACTION_BLOCKED = "action_blocked"


class LogMessageType(str, Enum):
    HELLO = "log.hello"
    SUBSCRIBED = "log.subscribed"
    EVENT = "log.event"
    REPLAY_COMPLETED = "log.replay_completed"
    GAP = "log.gap"
    ERROR = "log.error"
    PONG = "log.pong"
    KEEPALIVE = "log.keepalive"


class CanonicalEventType(str, Enum):
    """Stable mapping keys shared by server and local client facts."""

    SERVER_WAKE_WORD_DETECTED = "server.wakeword.detected"
    SERVER_RECORDING_STARTED = "server.recording.started"
    SERVER_RECORDING_ENDED = "server.recording.ended"
    SERVER_TRANSCRIPTION_STARTED = "server.transcription.started"
    SERVER_TRANSCRIPTION_COMPLETED = "server.transcription.completed"
    SERVER_TRANSCRIPTION_DISCARDED = "server.transcription.discarded"
    SERVER_TRANSCRIPTION_FAILED = "server.transcription.failed"
    SERVER_TRANSCRIPTION_CANCELLED = "server.transcription.cancelled"
    SERVER_TRANSCRIPTION_REJECTED = "server.transcription.rejected"

    CLIENT_HOTKEY_ACCEPTED = "client.hotkey.accepted"
    CLIENT_ACTION_BLOCKED = "client.action.blocked"
    CLIENT_DICTATION_INTERRUPTED = "client.dictation.interrupted"
    CLIENT_TRANSPORT_DISCONNECTED = "client.transport.disconnected"
    CLIENT_EVENT_STREAM_CONNECTING = "client.event_stream.connecting"
    CLIENT_EVENT_STREAM_REPLAYING = "client.event_stream.replaying"
    CLIENT_EVENT_STREAM_LIVE = "client.event_stream.live"
    CLIENT_EVENT_STREAM_DEGRADED = "client.event_stream.degraded"
    CLIENT_MICROPHONE_LOST = "client.microphone.lost"
    CLIENT_MICROPHONE_RECOVERED = "client.microphone.recovered"
    CLIENT_INJECTION_ACCEPTED = "client.injection.accepted"
    CLIENT_INJECTION_SUCCEEDED = "client.injection.succeeded"
    CLIENT_INJECTION_FAILED = "client.injection.failed"
    CLIENT_TTS_STARTED = "client.tts.started"
    CLIENT_TTS_STOPPED = "client.tts.stopped"
    CLIENT_TTS_FAILED = "client.tts.failed"
    CLIENT_LED_UNAVAILABLE = "client.led.unavailable"
    CLIENT_SOUND_FAILED = "client.sound.failed"
    CLIENT_CONFIGURATION_INVALID = "client.configuration.invalid"
    CLIENT_LIFECYCLE_STARTED = "client.lifecycle.started"
    CLIENT_LIFECYCLE_STOPPING = "client.lifecycle.stopping"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


def _required_string(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _optional_string(data: Mapping[str, Any], key: str) -> Optional[str]:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be null or a non-empty string")
    return value


def _non_negative_integer(data: Mapping[str, Any], key: str) -> int:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{key} must be an integer >= 0")
    return value


@dataclass(frozen=True)
class EventEnvelope:
    schema_version: int
    event_id: str
    cursor: int
    timestamp: str
    channel: str
    event: str
    severity: str
    server_instance_id: str
    data: Mapping[str, Any] = field(default_factory=dict)
    transport: Optional[str] = None
    client_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    transcription_id: Optional[str] = None
    segment_id: Optional[int] = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "EventEnvelope":
        if not isinstance(raw, Mapping):
            raise ValueError("event envelope must be a mapping")
        schema_version = _non_negative_integer(raw, "schemaVersion")
        if schema_version < 1:
            raise ValueError("schemaVersion must be >= 1")
        segment_id = raw.get("segmentId")
        if segment_id is not None and (
            isinstance(segment_id, bool)
            or not isinstance(segment_id, int)
            or segment_id < 0
        ):
            raise ValueError("segmentId must be null or an integer >= 0")
        event_data = raw.get("data", {})
        if not isinstance(event_data, Mapping):
            raise ValueError("data must be a mapping")
        known = {
            "schemaVersion", "eventId", "cursor", "timestamp", "channel",
            "event", "severity", "serverInstanceId", "data", "transport",
            "clientId", "sessionId", "requestId", "transcriptionId", "segmentId",
        }
        return cls(
            schema_version=schema_version,
            event_id=_required_string(raw, "eventId"),
            cursor=_non_negative_integer(raw, "cursor"),
            timestamp=_required_string(raw, "timestamp"),
            channel=_required_string(raw, "channel"),
            event=_required_string(raw, "event"),
            severity=_required_string(raw, "severity"),
            server_instance_id=_required_string(raw, "serverInstanceId"),
            data=_freeze(event_data),
            transport=_optional_string(raw, "transport"),
            client_id=_optional_string(raw, "clientId"),
            session_id=_optional_string(raw, "sessionId"),
            request_id=_optional_string(raw, "requestId"),
            transcription_id=_optional_string(raw, "transcriptionId"),
            segment_id=segment_id,
            extra=_freeze({key: value for key, value in raw.items() if key not in known}),
        )


@dataclass(frozen=True)
class LogControlMessage:
    message_type: LogMessageType
    payload: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "LogControlMessage":
        if not isinstance(raw, Mapping):
            raise ValueError("log control message must be a mapping")
        raw_type = _required_string(raw, "type")
        try:
            message_type = LogMessageType(raw_type)
        except ValueError as exc:
            raise ValueError(f"unsupported log message type: {raw_type!r}") from exc
        return cls(
            message_type=message_type,
            payload=_freeze({key: value for key, value in raw.items() if key != "type"}),
        )


@dataclass(frozen=True)
class NormalizedFeedbackEvent:
    event_type: CanonicalEventType
    origin: EventOrigin
    source: FeedbackSource
    state: Optional[FeedbackState] = None
    impulse: Optional[FeedbackImpulse] = None
    event_id: Optional[str] = None
    correlation_id: Optional[str] = None
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.event_type, CanonicalEventType):
            raise TypeError("event_type must be CanonicalEventType")
        if not isinstance(self.origin, EventOrigin):
            raise TypeError("origin must be EventOrigin")
        if not isinstance(self.source, FeedbackSource):
            raise TypeError("source must be FeedbackSource")
        if self.state is not None and not isinstance(self.state, FeedbackState):
            raise TypeError("state must be null or FeedbackState")
        if self.impulse is not None and not isinstance(self.impulse, FeedbackImpulse):
            raise TypeError("impulse must be null or FeedbackImpulse")
        for name, value in (
            ("event_id", self.event_id),
            ("correlation_id", self.correlation_id),
        ):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise TypeError(f"{name} must be null or a non-empty string")
        if not isinstance(self.details, Mapping):
            raise TypeError("details must be a mapping")
        if self.origin == EventOrigin.REPLAY and self.impulse is not None:
            raise ValueError("replay events cannot contain an impulse")
        object.__setattr__(self, "details", _freeze(self.details))
