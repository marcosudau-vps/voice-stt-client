"""Normalize AP07 server, STT-fallback and local events without I/O."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from voice_stt_client.core.event_models import (
    CanonicalEventType,
    EventOrigin,
    FeedbackImpulse,
    FeedbackSource,
    FeedbackState,
    NormalizedFeedbackEvent,
)
from voice_stt_client.core.event_protocol import EventProtocolResult, EventResultKind


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

    def normalize_domain(self, event, *, generation: int) -> Optional[NormalizedFeedbackEvent]:
        """Normalize only events accepted by ActivationMirror, never raw frames.

        Details are an explicit correlation allowlist, excluding text, settings,
        credentials and arbitrary additive fields even with a test ingress.
        """
        from . import protocol_v2 as p
        semantics = {
            p.EventType.ACTIVATION_STARTED: (CanonicalEventType.SERVER_ACTIVATION_STARTED, FeedbackImpulse.WAKE_WORD_DETECTED),
            p.EventType.RECORDING_STARTED: (CanonicalEventType.SERVER_RECORDING_STARTED, FeedbackImpulse.RECORDING_STARTED),
            p.EventType.RECORDING_ENDED: (CanonicalEventType.SERVER_RECORDING_ENDED, FeedbackImpulse.RECORDING_ENDED),
            p.EventType.COMPLETED: (CanonicalEventType.SERVER_TRANSCRIPTION_COMPLETED, FeedbackImpulse.TRANSCRIPTION_COMPLETED),
            p.EventType.DISCARDED: (CanonicalEventType.SERVER_TRANSCRIPTION_DISCARDED, None),
            p.EventType.FAILED: (CanonicalEventType.SERVER_TRANSCRIPTION_FAILED, FeedbackImpulse.TRANSCRIPTION_FAILED),
            p.EventType.ACTIVATION_CANCELLED: (CanonicalEventType.SERVER_TRANSCRIPTION_CANCELLED, FeedbackImpulse.DICTATION_INTERRUPTED),
            p.EventType.ACTIVATION_FAILED: (CanonicalEventType.SERVER_TRANSCRIPTION_FAILED, FeedbackImpulse.TRANSCRIPTION_FAILED),
            p.EventType.WATCHDOG_WARNING: (CanonicalEventType.CLIENT_DICTATION_TIMEOUT_WARNING, FeedbackImpulse.ACTION_BLOCKED),
            p.EventType.TRIGGER_SUPPRESSED: (CanonicalEventType.CLIENT_ACTION_BLOCKED, FeedbackImpulse.ACTION_BLOCKED),
        }
        semantic = semantics.get(event.type)
        if semantic is None:
            return None
        self._validate_generation(generation)
        d = event.payload
        kind, impulse = semantic
        segment_kinds = {p.EventType.RECORDING_STARTED, p.EventType.RECORDING_ENDED,
                         p.EventType.COMPLETED, p.EventType.DISCARDED, p.EventType.FAILED, p.EventType.WATCHDOG_WARNING}
        aid = None if event.type == p.EventType.TRIGGER_SUPPRESSED else d.get('activationId')
        sid = d.get('segmentId') if event.type in segment_kinds else None
        sequence = d.get('segmentSequence') if event.type in segment_kinds else None
        identity = sid or aid or event.eventId
        if event.type == p.EventType.WATCHDOG_WARNING:
            identity = f"{d['activationId']}:{d.get('segmentId')}:{d['deadlineAtUnixMs']}"
        correlation = f"{kind.value}|session:{event.sessionId}|identity:{identity}"
        return NormalizedFeedbackEvent(kind, EventOrigin.LIVE, FeedbackSource.DOMAIN,
            impulse=impulse, event_id=event.eventId, correlation_id=correlation,
            details={"generation": generation, "sessionId": event.sessionId,
                     "activationId": aid, "segmentId": sid,
                     "segmentSequence": sequence, "commandId": None,
                     "eventSeq": event.eventSeq})

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
