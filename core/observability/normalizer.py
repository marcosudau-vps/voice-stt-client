"""
Normalizer with three inputs (OBS-010).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §3.
The normalizer **never raises**; in doubt it returns ``None`` and the caller
counts ``malformed``. Redaction runs at the end of every path (§3.3).
"""

from __future__ import annotations

import logging
import traceback
from datetime import datetime, timezone
from typing import Any, Mapping, Optional
from uuid import uuid4

from core.event_models import EventOrigin, EventEnvelope
from core.event_protocol import EventResultKind

from .models import CanonicalLogRecord, Level, ProducerKind, Scope
from .redaction import redact_mapping, redact_text

# ---------------------------------------------------------------------------
# Encoding (CONTRACTS §2.1): closed value sets vs. open namespaces.
# ---------------------------------------------------------------------------

DEFAULT_RECEIVED_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _encode_iso(dt: datetime) -> str:
    return dt.strftime(DEFAULT_RECEIVED_FORMAT) + f".{dt.microsecond // 1000:03d}Z"


def _received_at() -> str:
    return _encode_iso(datetime.now(timezone.utc))


def _from_created(created: float) -> str:
    return _encode_iso(datetime.fromtimestamp(created, tz=timezone.utc))


def _normalize_level(raw: Any, details: dict[str, Any]) -> str:
    """Closed level mapping with INFO fallback and ``source_severity``
    preservation (CONTRACTS §2.1). Never calls ``Level(value)`` unchecked."""
    if isinstance(raw, str):
        candidate = raw.upper()
        if candidate in Level._value2member_map_:
            return candidate
    details["source_severity"] = str(raw)
    return Level.INFO.value


def _normalize_scope(producer_kind: str, session_id: Optional[str]) -> str:
    """Complete scope derivation rule (CONTRACTS §1.3, FD-R6)."""
    if isinstance(session_id, str) and session_id.strip():
        return Scope.SESSION.value
    if producer_kind == ProducerKind.SERVER.value:
        return Scope.GLOBAL.value
    return Scope.INSTANCE.value


def _redact(details: Mapping[str, Any], *, store_transcription_content: bool,
            user_profile: Any) -> Mapping[str, Any]:
    return redact_mapping(
        details,
        store_transcription_content=store_transcription_content,
        user_profile=user_profile,
    )


# ---------------------------------------------------------------------------
# 1. Python ``LogRecord`` -> canonical (CONTRACTS §3.1)
# ---------------------------------------------------------------------------

# Verbindliche Fassung (CONTRACTS §3.1 / FD-R2): NUR "text" wird abgebildet;
# jeder andere Loggername ergibt "system". Aus einem Loggernamen entsteht
# NIE "performance" und NIE "audit".
LOGGER_CHANNEL_MAP: dict[str, str] = {
    "text": "transcription",
}


def from_log_record(
    record: logging.LogRecord,
    *,
    instance_id: str,
    session_id: Optional[str] = None,
    generation: Optional[int] = None,
    store_transcription_content: bool = False,
    user_profile: Any = None,
) -> Optional[CanonicalLogRecord]:
    """Python ``LogRecord`` -> canonical record.

    ``session_id``/``generation``/``segment_id`` source **exclusively** from
    ``record.__dict__`` — the existing ``extra`` contract (CONTRACTS §3.1 /
    FD-R8). The parameters are part of the frozen signature but are never
    used as a runtime-state source: the future handler neither queries nor
    holds a reference to session, controller or coordinator.
    """
    try:
        if not isinstance(record, logging.LogRecord):
            return None
        name = record.name
        channel = LOGGER_CHANNEL_MAP.get(name, "system")
        details: dict[str, Any] = {
            "logger": name,
            "func": record.funcName,
            "line": record.lineno,
            "thread": record.threadName,
        }
        if name.startswith("lefx."):
            producer_kind = ProducerKind.LED.value
            producer_id = "respeaker-led-controller"
        else:
            producer_kind = ProducerKind.CLIENT.value
            producer_id = "voice-stt-client"
        for key in ("session_id", "segment_id", "event_type", "detail"):
            value = record.__dict__.get(key)
            if value is not None:
                details[key] = value
        if record.exc_info and record.exc_info[0] is not None:
            try:
                details["exception"] = "".join(
                    traceback.format_exception(*record.exc_info)
                )
            except Exception:  # noqa: BLE001
                pass
        level = _normalize_level(record.levelname, details)
        return CanonicalLogRecord(
            record_id=uuid4().hex,
            received_at=_received_at(),
            producer_kind=producer_kind,
            producer_id=producer_id,
            instance_id=instance_id,
            scope=_normalize_scope(producer_kind, record.__dict__.get("session_id")),
            channel=channel,
            level=level,
            replayed=False,
            source_timestamp=_from_created(record.created),
            type=None,
            component=name,
            session_id=record.__dict__.get("session_id"),
            generation=record.__dict__.get("generation"),
            segment_id=record.__dict__.get("segment_id"),
            message=redact_text(
                record.getMessage(),
                store_transcription_content=store_transcription_content,
                user_profile=user_profile,
            ),
            details=_redact(
                details,
                store_transcription_content=store_transcription_content,
                user_profile=user_profile,
            ),
        )
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------------------
# 2. ``(SessionContext, EventProtocolResult)`` -> canonical (CONTRACTS §3.2)
# ---------------------------------------------------------------------------

_CONTROL_KINDS = frozenset({
    "hello",
    "subscribed",
    "gap",
    "error",
    "replay_completed",
    "pong",
    "keepalive",
})

# Whitelist for log.hello (R-6): never store raw hello; only these fields.
_HELLO_WHITELIST_TOP = ("sessionId", "sessionConfig", "activationConfig",
                        "sessionCapabilities")
_HELLO_WHITELIST_LOGACCESS = (
    "available", "code", "reason", "expiresAt", "logProtocolVersion",
    "serverInstanceId", "oldestCursor", "latestCursor",
)


def _hello_whitelist(payload: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in _HELLO_WHITELIST_TOP:
        if key in payload:
            out[key] = payload[key]
    log_access = payload.get("logAccess")
    if isinstance(log_access, Mapping):
        subset: dict[str, Any] = {}
        for key in _HELLO_WHITELIST_LOGACCESS:
            if key in log_access:
                subset[key] = log_access[key]
        if subset:
            out["logAccess"] = subset
    return out


def _type_prefix(event_type: str) -> Optional[str]:
    if not isinstance(event_type, str) or not event_type:
        return None
    return event_type.split(".", 1)[0]


def _kinds_match(result_kind: Any, expected: EventResultKind) -> bool:
    value = result_kind.value if hasattr(result_kind, "value") else result_kind
    return value == expected.value


def from_server_result(
    context: Any,
    result: Any,
    *,
    client_instance_id: Optional[str] = None,
    store_raw_payload: bool = True,
    store_transcription_content: bool = False,
    user_profile: Any = None,
) -> Optional[CanonicalLogRecord]:
    """``(SessionContext, EventProtocolResult)`` -> canonical record.

    Contributes the EVENT mapping (producer ``server``) and the CONTROL
    mapping (producer ``client``, CONTRACTS §3.2). ``client_instance_id`` is
    injected by the future ServerLiveAdapter; control frames need it.
    """
    try:
        if result is None or not hasattr(result, "kind"):
            return None
        kind = result.kind
        if _kinds_match(kind, EventResultKind.EVENT):
            if result.event is None:
                return None
            if bool(getattr(result, "duplicate", False)):
                return _map_control(
                    context, result, client_instance_id,
                    store_raw_payload=store_raw_payload,
                    store_transcription_content=store_transcription_content,
                    user_profile=user_profile,
                )
            return _map_server_event(
                context, result,
                store_raw_payload=store_raw_payload,
                store_transcription_content=store_transcription_content,
                user_profile=user_profile,
            )
        value = kind.value if hasattr(kind, "value") else str(kind)
        if value in _CONTROL_KINDS:
            return _map_control(
                context, result, client_instance_id,
                store_raw_payload=store_raw_payload,
                store_transcription_content=store_transcription_content,
                user_profile=user_profile,
            )
        return None
    except Exception:  # noqa: BLE001
        return None


def _map_server_event(
    context: Any,
    result: Any,
    *,
    store_raw_payload: bool,
    store_transcription_content: bool,
    user_profile: Any,
) -> Optional[CanonicalLogRecord]:
    envelope: Optional[EventEnvelope] = result.event
    if envelope is None:
        return None
    details = dict(envelope.data or {})
    level = _normalize_level(envelope.severity, details)
    message = None
    extra = envelope.extra or {}
    if isinstance(extra, Mapping) and isinstance(extra.get("meldung"), str):
        message = redact_text(
            extra.get("meldung"),
            store_transcription_content=store_transcription_content,
            user_profile=user_profile,
        )
    raw = None
    if store_raw_payload and envelope.channel != "performance":
        raw = result.payload
    return CanonicalLogRecord(
        record_id=uuid4().hex,
        received_at=_received_at(),
        producer_kind=ProducerKind.SERVER.value,
        producer_id="voice-stt-server",
        instance_id=envelope.server_instance_id,
        scope=_normalize_scope(ProducerKind.SERVER.value, envelope.session_id),
        channel=envelope.channel,
        level=level,
        replayed=bool(result.origin is EventOrigin.REPLAY),
        source_timestamp=envelope.timestamp,
        type=envelope.event,
        component=_type_prefix(envelope.event),
        session_id=envelope.session_id,
        generation=getattr(context, "generation", None),
        activation_id=envelope.data.get("activationId") if envelope.data else None,
        segment_id=envelope.segment_id,
        transcription_id=envelope.transcription_id,
        event_id=envelope.event_id,
        server_cursor=envelope.cursor,
        message=message,
        details=_redact(
            details,
            store_transcription_content=store_transcription_content,
            user_profile=user_profile,
        ),
        raw=raw,
    )


def _map_control(
    context: Any,
    result: Any,
    client_instance_id: Optional[str],
    *,
    store_raw_payload: bool,
    store_transcription_content: bool,
    user_profile: Any,
) -> Optional[CanonicalLogRecord]:
    value = result.kind.value if hasattr(result.kind, "value") else str(result.kind)
    instance_id = client_instance_id
    if not isinstance(instance_id, str) or not instance_id.strip():
        return None
    payload = result.payload or {}
    details: Mapping[str, Any]
    if value == "hello":
        details = _hello_whitelist(payload)
        raw = None
    else:
        details = dict(payload)
        raw = result.payload if store_raw_payload else None
    for key in ("lostFromCursor", "lostToCursor"):
        if value == "gap" and key in payload:
            details[key] = payload[key]
    session_id = getattr(context, "session_id", None)
    generation = getattr(context, "generation", None)
    level = "WARNING" if value in ("error", "gap") else "INFO"
    return CanonicalLogRecord(
        record_id=uuid4().hex,
        received_at=_received_at(),
        producer_kind=ProducerKind.CLIENT.value,
        producer_id="voice-stt-client",
        instance_id=instance_id,
        scope=_normalize_scope(ProducerKind.CLIENT.value, session_id),
        channel="system",
        level=level,
        replayed=False,
        type=f"client.eventstream.{value}",
        component="eventstream",
        session_id=session_id,
        generation=generation,
        message=None,
        details=_redact(
            details,
            store_transcription_content=store_transcription_content,
            user_profile=user_profile,
        ),
        raw=raw,
    )


# ---------------------------------------------------------------------------
# 3. Structured client observations (CONTRACTS §3.3 / §6 ``Ingress.event``)
# ---------------------------------------------------------------------------

def from_client_event(
    type: str,
    *,
    channel: str,
    level: str = "INFO",
    component: Optional[str] = None,
    message: Optional[str] = None,
    details: Optional[Mapping[str, Any]] = None,
    instance_id: str,
    store_transcription_content: bool = False,
    user_profile: Any = None,
    **ids: Any,
) -> Optional[CanonicalLogRecord]:
    """Structured client observation -> canonical record.

    ``**ids`` carries the correlation/id fields used by the observation API:
    ``session_id``, ``generation``, ``activation_id``, ``segment_id``,
    ``command_id``, ``correlation_id``, ``transcription_id``.
    """
    try:
        session_id = ids.get("session_id")
        generation = ids.get("generation")
        activation_id = ids.get("activation_id")
        segment_id = ids.get("segment_id")
        command_id = ids.get("command_id")
        correlation_id = ids.get("correlation_id")
        transcription_id = ids.get("transcription_id")
        normalized_details = details if details is not None else {}
        message_redacted = None
        if message is not None:
            message_redacted = redact_text(
                message,
                store_transcription_content=store_transcription_content,
                user_profile=user_profile,
            )
        return CanonicalLogRecord(
            record_id=uuid4().hex,
            received_at=_received_at(),
            producer_kind=ProducerKind.CLIENT.value,
            producer_id="voice-stt-client",
            instance_id=instance_id,
            scope=_normalize_scope(ProducerKind.CLIENT.value, session_id),
            channel=channel,
            level=(level.upper() if isinstance(level, str) else level),
            replayed=False,
            type=type,
            component=component,
            session_id=session_id,
            generation=generation,
            activation_id=activation_id,
            segment_id=segment_id,
            command_id=command_id,
            correlation_id=correlation_id,
            transcription_id=transcription_id,
            message=message_redacted,
            details=_redact(
                normalized_details,
                store_transcription_content=store_transcription_content,
                user_profile=user_profile,
            ),
        )
    except Exception:  # noqa: BLE001
        return None