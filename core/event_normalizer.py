"""Normalize AP07 server, STT-fallback and local events without I/O."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from core.event_models import (
    CanonicalEventType,
    EventOrigin,
    FeedbackImpulse,
    FeedbackSource,
    FeedbackState,
    NormalizedFeedbackEvent,
)
from core.event_protocol import EventProtocolResult, EventResultKind


class EventNormalizationError(ValueError):
    """A known feedback event violates its required schema or session scope."""


@dataclass(frozen=True)
class _Semantic:
    event_type: CanonicalEventType
    state: Optional[FeedbackState]
    impulse: Optional[FeedbackImpulse]
    segment_required: bool = False


_SERVER_EVENTS: dict[str, _Semantic] = {
    "wakeword.detected": _Semantic(
        CanonicalEventType.SERVER_WAKE_WORD_DETECTED,
        FeedbackState.STARTING,
        FeedbackImpulse.WAKE_WORD_DETECTED,
    ),
    "transcription.recording_started": _Semantic(
        CanonicalEventType.SERVER_RECORDING_STARTED,
        FeedbackState.RECORDING,
        FeedbackImpulse.RECORDING_STARTED,
        True,
    ),
    "transcription.recording_ended": _Semantic(
        CanonicalEventType.SERVER_RECORDING_ENDED,
        FeedbackState.FINALIZING,
        FeedbackImpulse.RECORDING_ENDED,
        True,
    ),
    "transcription.started": _Semantic(
        CanonicalEventType.SERVER_TRANSCRIPTION_STARTED,
        FeedbackState.FINALIZING,
        None,
        True,
    ),
    "transcription.completed": _Semantic(
        CanonicalEventType.SERVER_TRANSCRIPTION_COMPLETED,
        FeedbackState.COMPLETED,
        FeedbackImpulse.TRANSCRIPTION_COMPLETED,
        True,
    ),
    "transcription.discarded": _Semantic(
        CanonicalEventType.SERVER_TRANSCRIPTION_DISCARDED,
        FeedbackState.IDLE,
        None,
        True,
    ),
    "transcription.failed": _Semantic(
        CanonicalEventType.SERVER_TRANSCRIPTION_FAILED,
        FeedbackState.FAILED,
        FeedbackImpulse.TRANSCRIPTION_FAILED,
    ),
    "transcription.cancelled": _Semantic(
        CanonicalEventType.SERVER_TRANSCRIPTION_CANCELLED,
        FeedbackState.INTERRUPTED,
        FeedbackImpulse.DICTATION_INTERRUPTED,
    ),
    "transcription.rejected": _Semantic(
        CanonicalEventType.SERVER_TRANSCRIPTION_REJECTED,
        FeedbackState.FAILED,
        FeedbackImpulse.TRANSCRIPTION_FAILED,
    ),
}

_TIMELINE_FALLBACK_EVENTS = {
    "wakeword_detected": "wakeword.detected",
    "recording_started": "transcription.recording_started",
    "recording_ended": "transcription.recording_ended",
    "transcription_started": "transcription.started",
    "final_transcript": "transcription.completed",
    "final_transcript_discarded": "transcription.discarded",
}

_STATUS_FALLBACK_EVENTS = {
    "wakeword_detected": "wakeword.detected",
}

_LOCAL_SEMANTICS: dict[CanonicalEventType, tuple[Optional[FeedbackState], Optional[FeedbackImpulse]]] = {
    CanonicalEventType.CLIENT_ACTION_BLOCKED: (
        None,
        FeedbackImpulse.ACTION_BLOCKED,
    ),
    CanonicalEventType.CLIENT_DICTATION_INTERRUPTED: (
        FeedbackState.INTERRUPTED,
        FeedbackImpulse.DICTATION_INTERRUPTED,
    ),
    CanonicalEventType.CLIENT_MICROPHONE_LOST: (
        FeedbackState.FAILED,
        FeedbackImpulse.MICROPHONE_LOST,
    ),
    CanonicalEventType.CLIENT_MICROPHONE_RECOVERED: (FeedbackState.IDLE, None),
    CanonicalEventType.CLIENT_INJECTION_FAILED: (
        FeedbackState.FAILED,
        FeedbackImpulse.INJECTION_FAILED,
    ),
    CanonicalEventType.CLIENT_CONFIGURATION_INVALID: (
        FeedbackState.FAILED,
        FeedbackImpulse.ACTION_BLOCKED,
    ),
}


class EventNormalizer:
    """Strictly map documented event identifiers to stable canonical facts."""

    def normalize_event_stream(
        self,
        result: EventProtocolResult,
        *,
        generation: int,
        session_id: str,
    ) -> Optional[NormalizedFeedbackEvent]:
        if result.kind is not EventResultKind.EVENT or result.event is None:
            raise EventNormalizationError("result must contain one log.event")
        envelope = result.event
        semantic = _SERVER_EVENTS.get(envelope.event)
        if semantic is None:
            return None
        if envelope.channel != "transcription":
            raise EventNormalizationError(
                "known feedback lifecycle event must use transcription channel"
            )
        if envelope.session_id != session_id:
            raise EventNormalizationError("event session does not match current session")
        self._validate_generation(generation)
        if semantic.segment_required and envelope.segment_id is None:
            raise EventNormalizationError(
                f"{envelope.event} requires segmentId"
            )
        reason = self._optional_string(envelope.data, "reason")
        if envelope.event == "transcription.discarded" and reason != "empty_final":
            raise EventNormalizationError(
                "transcription.discarded requires reason=empty_final"
            )
        origin = result.origin
        if origin not in {EventOrigin.LIVE, EventOrigin.REPLAY}:
            raise EventNormalizationError("log.event requires live or replay origin")
        impulse = semantic.impulse if origin is EventOrigin.LIVE else None
        correlation_id, aliases = self._correlation(
            semantic.event_type,
            generation=generation,
            session_id=session_id,
            segment_id=envelope.segment_id,
            transcription_id=envelope.transcription_id,
        )
        return NormalizedFeedbackEvent(
            event_type=semantic.event_type,
            origin=origin,
            source=FeedbackSource.EVENT_STREAM,
            state=semantic.state,
            impulse=impulse,
            event_id=envelope.event_id,
            correlation_id=correlation_id,
            details={
                "generation": generation,
                "sessionId": session_id,
                "segmentId": envelope.segment_id,
                "transcriptionId": envelope.transcription_id,
                "reason": reason,
                "correlationAliases": aliases,
            },
        )

    def normalize_stt_fallback(
        self,
        event_type: str,
        data: Mapping[str, Any],
        *,
        generation: int,
        session_id: str,
    ) -> Optional[NormalizedFeedbackEvent]:
        if not isinstance(data, Mapping):
            raise EventNormalizationError("STT fallback event must be a mapping")
        if data.get("sessionId") != session_id:
            return None
        self._validate_generation(generation)
        server_name: Optional[str] = None
        segment_id = data.get("segmentId")
        if segment_id is not None and (
            isinstance(segment_id, bool)
            or not isinstance(segment_id, int)
            or segment_id < 0
        ):
            raise EventNormalizationError("segmentId must be an integer >= 0")
        if event_type == "timeline":
            name = data.get("event")
            if isinstance(name, str):
                server_name = _TIMELINE_FALLBACK_EVENTS.get(name)
        elif event_type == "status":
            state = data.get("state")
            if isinstance(state, str):
                server_name = _STATUS_FALLBACK_EVENTS.get(state)
        elif event_type == "final":
            server_name = "transcription.completed"
        elif event_type == "error" and data.get("where") in {
            "main_engine",
            "realtime_engine",
            "recorder",
            "command",
            "audio",
        }:
            server_name = "transcription.failed"
        if server_name is None:
            return None
        semantic = _SERVER_EVENTS[server_name]
        if semantic.segment_required and segment_id is None:
            raise EventNormalizationError(f"{server_name} requires segmentId")
        reason = self._optional_string(data, "reason")
        if server_name == "transcription.discarded" and reason != "empty_final":
            raise EventNormalizationError(
                "final_transcript_discarded requires reason=empty_final"
            )
        correlation_id, aliases = self._correlation(
            semantic.event_type,
            generation=generation,
            session_id=session_id,
            segment_id=segment_id,
            transcription_id=None,
        )
        return NormalizedFeedbackEvent(
            event_type=semantic.event_type,
            origin=EventOrigin.LIVE,
            source=FeedbackSource.STT_FALLBACK,
            state=semantic.state,
            impulse=semantic.impulse,
            correlation_id=correlation_id,
            details={
                "generation": generation,
                "sessionId": session_id,
                "segmentId": segment_id,
                "reason": reason,
                "correlationAliases": aliases,
            },
        )

    def normalize_local(
        self,
        event_type: CanonicalEventType,
        *,
        generation: int,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        details: Optional[Mapping[str, Any]] = None,
    ) -> NormalizedFeedbackEvent:
        if not isinstance(event_type, CanonicalEventType):
            raise EventNormalizationError("local event type must be canonical")
        if not event_type.value.startswith("client."):
            raise EventNormalizationError("local events must use client.* namespace")
        self._validate_generation(generation)
        state, impulse = _LOCAL_SEMANTICS.get(event_type, (None, None))
        safe_details = dict(details or {})
        safe_details.update({"generation": generation, "sessionId": session_id})
        return NormalizedFeedbackEvent(
            event_type=event_type,
            origin=EventOrigin.LOCAL,
            source=FeedbackSource.LOCAL_ONLY,
            state=state,
            impulse=impulse,
            correlation_id=correlation_id,
            details=safe_details,
        )

    @staticmethod
    def _correlation(
        event_type: CanonicalEventType,
        *,
        generation: int,
        session_id: str,
        segment_id: Optional[int],
        transcription_id: Optional[str],
    ) -> tuple[Optional[str], tuple[str, ...]]:
        prefix = event_type.value
        aliases: list[str] = []
        if segment_id is not None:
            aliases.append(f"{prefix}|session:{session_id}|segment:{segment_id}")
        if transcription_id:
            primary = f"{prefix}|transcription:{transcription_id}"
        elif aliases:
            primary = aliases[0]
        else:
            return None, ()
        return primary, tuple(dict.fromkeys((primary, *aliases)))

    @staticmethod
    def _optional_string(data: Mapping[str, Any], key: str) -> Optional[str]:
        value = data.get(key)
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise EventNormalizationError(f"{key} must be a non-empty string")
        return value.strip()

    @staticmethod
    def _validate_generation(generation: int) -> None:
        if (
            isinstance(generation, bool)
            or not isinstance(generation, int)
            or generation < 0
        ):
            raise EventNormalizationError("generation must be an integer >= 0")
