"""Pure codec for the ada13b0 V2 contract; no transport or lifecycle authority.

Decode once, then dispatch by model/type. Wire names are preserved in immutable
``payload`` mappings. Unknown events carry a validated sequence envelope only.
Malformed known messages raise ProtocolError; unrelated unknown messages return
None. Session/generation/order guards belong to the consuming transport/mirror.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
import json
import math
import struct
from types import MappingProxyType
from typing import Any
from uuid import UUID, uuid4


PROTOCOL_VERSION = 2
WEBSOCKET_PATH = "/ws/v2"
MAX_METADATA_BYTES = 65536
DEFAULT_MAX_AUDIO_PACKET_BYTES = 524288


class CommandType(StrEnum):
    ACTIVATION = "activation.command"
    SUPPRESSION = "trigger_suppression.set"
    AUDIO_AVAILABILITY = "audio_availability.set"
    SETTINGS_PATCH = "session_settings.patch"
    SNAPSHOT_REQUEST = "session.snapshot.request"


class ActivationAction(StrEnum):
    ACTIVATE = "activate"
    REFRESH = "refresh"
    FINISH = "finish"
    CANCEL = "cancel"


class InputPhase(StrEnum):
    IDLE = "idle"
    WAITING_FIRST_SPEECH = "waiting_first_speech"
    SEGMENT_ACTIVE = "segment_active"
    FOLLOWUP_WAIT = "followup_wait"
    CLOSING_INPUT = "closing_input"


class AckResult(StrEnum):
    APPLIED = "applied"
    NO_CHANGE = "no_change"
    ACTIVATION_LOCKED = "activation_locked"
    NOT_ACTIVE = "not_active"
    INVALID_PHASE = "invalid_phase"
    CLOSING_INPUT = "closing_input"
    STALE_SESSION = "stale_session"
    STALE_ACTIVATION = "stale_activation"
    COMMAND_ID_CONFLICT = "command_id_conflict"
    INVALID_PAYLOAD = "invalid_payload"
    TRIGGER_SUPPRESSED = "trigger_suppressed"
    AUDIO_UNAVAILABLE = "audio_unavailable"
    SETTINGS_REVISION_CONFLICT = "settings_revision_conflict"
    SETTINGS_REJECTED = "settings_rejected"
    INTERNAL_ERROR = "internal_error"


class EventType(StrEnum):
    ACTIVATION_STARTED = "activation.started"
    PHASE_CHANGED = "activation.phase_changed"
    INPUT_CLOSED = "activation.input_closed"
    ACTIVATION_COMPLETED = "activation.completed"
    ACTIVATION_CANCELLED = "activation.cancelled"
    ACTIVATION_FAILED = "activation.failed"
    TRIGGER_SUPPRESSED = "activation.trigger_suppressed"
    RECORDING_STARTED = "segment.recording_started"
    RECORDING_ENDED = "segment.recording_ended"
    TRANSCRIPTION_ACCEPTED = "transcription.accepted"
    INTERIM = "transcription.interim"
    COMPLETED = "transcription.completed"
    DISCARDED = "transcription.discarded"
    FAILED = "transcription.failed"
    WATCHDOG_WARNING = "watchdog.warning"
    WAKE_DETECTED = "wakeword.detected"
    WAKE_AVAILABILITY = "wakeword.availability_changed"
    SETTINGS_CHANGED = "settings.changed"


class ApplyPolicy(StrEnum):
    LIVE = "live"
    NEXT_ACTIVATION = "next_activation"
    NEXT_SESSION = "next_session"
    SERVER_RESTART = "server_restart"


class ProtocolError(ValueError):
    """Invalid wire shape. Messages never include supplied field values."""


def new_id() -> str:
    return str(uuid4())


def is_canonical_uuid(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 36:
        return False
    try:
        return str(UUID(value)) == value
    except ValueError:
        return False


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _json_value(value: Any) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float) and math.isfinite(value):
        return
    if isinstance(value, list):
        for item in value:
            _json_value(item)
        return
    if isinstance(value, Mapping) and all(isinstance(key, str) for key in value):
        for item in value.values():
            _json_value(item)
        return
    raise ProtocolError("expected finite JSON values")


def _object(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ProtocolError(f"{name} must be an object")
    return value


def _field(data: Mapping, key: str, kind: str, *, nullable: bool = False,
           minimum: int = 0) -> Any:
    if key not in data:
        raise ProtocolError(f"missing {key}")
    value = data[key]
    if nullable and value is None:
        return None
    valid = {
        "uuid": lambda: is_canonical_uuid(value),
        "str": lambda: isinstance(value, str) and bool(value.strip()),
        "text": lambda: isinstance(value, str),
        "int": lambda: type(value) is int and value >= minimum,
        "bool": lambda: type(value) is bool,
        "number": lambda: type(value) is int or (type(value) is float and math.isfinite(value)),
        "object": lambda: isinstance(value, Mapping),
        "list": lambda: isinstance(value, list),
        "strings": lambda: isinstance(value, list) and all(
            isinstance(item, str) and item.strip() for item in value),
    }[kind]()
    if not valid:
        raise ProtocolError(f"invalid {key} ({kind})")
    return value


def _enum(data: Mapping, key: str, values: Any, *, nullable: bool = False) -> Any:
    value = _field(data, key, "str", nullable=nullable)
    if value is not None and value not in values:
        raise ProtocolError(f"invalid {key} vocabulary")
    return value


def _version(data: Mapping) -> None:
    if _field(data, "protocolVersion", "int") != PROTOCOL_VERSION:
        raise ProtocolError("unsupported protocolVersion")


def _identity(data: Mapping) -> None:
    _version(data)
    # The pinned server's public settings read allows serverVersion="".
    _field(data, "serverVersion", "text")
    _field(data, "serverCommit", "str")


def _mask(data: Any) -> None:
    data = _object(data, "trigger mask")
    _field(data, "manual", "bool")
    _field(data, "wakeWord", "bool")


def _errors(data: Mapping, *, required: bool = False) -> None:
    if not required and "errors" not in data:
        return
    for error in _field(data, "errors", "list"):
        error = _object(error, "error")
        for key in ("field", "code", "message"):
            _field(error, key, "str")


@dataclass(frozen=True)
class WireMessage:
    type: str
    payload: Mapping[str, Any] = field(repr=False)

    def to_mapping(self) -> dict[str, Any]:
        """Explicit fresh JSON copy. May contain text; never log blindly."""
        return _thaw(self.payload)


@dataclass(frozen=True)
class Hello(WireMessage):
    clientRunId: str


@dataclass(frozen=True)
class Command(WireMessage):
    sessionId: str
    commandId: str


@dataclass(frozen=True)
class CommandAck(WireMessage):
    sessionId: str
    commandId: str
    accepted: bool
    result: AckResult
    activationId: str | None
    inputPhase: InputPhase
    stateVersion: int
    settingsRevision: int


@dataclass(frozen=True)
class Event(WireMessage):
    sessionId: str
    eventId: str
    eventSeq: int
    stateVersion: int
    occurredAtUnixMs: int

    @property
    def preview_text(self) -> str | None:
        if self.type != EventType.INTERIM:
            return None
        display = self.payload.get("displayText")
        return display if isinstance(display, str) else self.payload["text"]


@dataclass(frozen=True)
class UnknownEvent(Event):
    """Valid envelope for sequencing, no known domain effect."""


@dataclass(frozen=True)
class Snapshot(WireMessage):
    sessionId: str
    stateVersion: int
    lastEventSeq: int
    settingsRevision: int


@dataclass(frozen=True)
class LogAccess:
    available: bool
    # Token and all supplied strings stay out of repr, including failure reason.
    payload: Mapping[str, Any] = field(repr=False)

    @property
    def accessToken(self) -> str | None:
        return self.payload.get("accessToken") if self.available else None


@dataclass(frozen=True)
class HelloAccepted(WireMessage):
    sessionId: str
    snapshot: Snapshot
    logAccess: LogAccess

    def to_mapping(self) -> dict[str, Any]:
        data = super().to_mapping()
        data["logAccess"] = _thaw(self.logAccess.payload)
        return data


@dataclass(frozen=True)
class HandshakeRejected(WireMessage):
    pass


def parse_client_message(data: Mapping[str, Any]) -> Hello | Command:
    _object(data, "message")
    _json_value(data)
    message_type = _field(data, "type", "str")
    if message_type == "hello":
        versions = _field(data, "supportedProtocolVersions", "list")
        if not versions or any(type(version) is not int for version in versions) or 2 not in versions:
            raise ProtocolError("invalid supportedProtocolVersions")
        for key in ("clientVersion", "clientCommit"):
            _field(data, key, "str")
        run_id = _field(data, "clientRunId", "uuid")
        requested = _field(data, "requestedSession", "object")
        trigger = _field(requested, "trigger", "object")
        _mask(trigger)
        ids = _field(requested, "wakeWordIds", "strings")
        if not (trigger["manual"] or trigger["wakeWord"]):
            raise ProtocolError("activation_trigger_required")
        if bool(ids) != trigger["wakeWord"]:
            raise ProtocolError("wake_word_selection_required_or_not_allowed")
        _mask(_field(data, "runtimeSuppression", "object"))
        return Hello(message_type, _freeze(data), run_id)
    if message_type not in CommandType:
        raise ProtocolError("unknown client command type")
    _version(data)
    session = _field(data, "sessionId", "uuid")
    command_id = _field(data, "commandId", "uuid")
    if message_type == CommandType.ACTIVATION:
        action = _enum(data, "action", ActivationAction)
        if action == ActivationAction.ACTIVATE:
            if "activationId" in data:
                raise ProtocolError("activate forbids activationId")
            _enum(data, "source", ("manual",))
        else:
            if "source" in data:
                raise ProtocolError("control forbids source")
            _field(data, "activationId", "uuid")
    elif message_type == CommandType.SUPPRESSION:
        _mask(data)
    elif message_type == CommandType.AUDIO_AVAILABILITY:
        _field(data, "audioAvailable", "bool")
    elif message_type == CommandType.SETTINGS_PATCH:
        _patch_request(data)
    return Command(message_type, _freeze(data), session, command_id)


def build_hello(*, clientVersion: str, clientCommit: str, clientRunId: str,
                manual: bool, wakeWord: bool, wakeWordIds: list[str],
                suppressManual: bool, suppressWakeWord: bool) -> Hello:
    return parse_client_message({
        "type": "hello", "supportedProtocolVersions": [2],
        "clientVersion": clientVersion, "clientCommit": clientCommit,
        "clientRunId": clientRunId,
        "requestedSession": {"trigger": {"manual": manual, "wakeWord": wakeWord},
                             "wakeWordIds": wakeWordIds},
        "runtimeSuppression": {"manual": suppressManual, "wakeWord": suppressWakeWord},
    })


def build_command(command_type: CommandType | str, sessionId: str, *,
                  commandId: str | None = None, **fields: Any) -> Command:
    return parse_client_message({**fields, "type": command_type, "protocolVersion": 2,
                                 "sessionId": sessionId,
                                 "commandId": new_id() if commandId is None else commandId})


def encode_client_message(message: Hello | Command | Mapping[str, Any]) -> str:
    """Validate and encode once; transport must store this string for retry."""
    data = message.to_mapping() if isinstance(message, (Hello, Command)) else message
    parsed = parse_client_message(data)
    return json.dumps(parsed.to_mapping(), ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _patch_request(data: Mapping) -> None:
    _field(data, "baseSettingsRevision", "int")
    if not _field(data, "changes", "object"):
        raise ProtocolError("changes must not be empty")


# Pinned registry value types; this is decoding, not settings policy authority.
SESSION_SETTING_TYPES = MappingProxyType({
    **{f"activation.{key}": "int" for key in (
        "initialSpeechTimeoutMs", "followupTimeoutMs", "segmentWatchdogInitialMs",
        "segmentWatchdogRefreshMs", "segmentWatchdogWarningMs", "closingRecoveryTimeoutMs")},
    "wakeWord.sensitivity": "number", "wakeWord.minConsecutivePredictionFrames": "int",
    "wakeWord.cooldownMs": "int", "wakeWord.preRollMs": "int", "wakeWord.detectorGain": "number",
    "wakeWord.noiseSuppressionEnabled": "bool", "wakeWord.vadThreshold": "number",
    "wakeWord.selection": "strings", "runtimeSuppression.manual": "bool",
    "runtimeSuppression.wakeWord": "bool",
})


def _settings_map(data: Any, *, complete: bool = False) -> None:
    data = _object(data, "settings map")
    if complete and not SESSION_SETTING_TYPES.keys() <= data.keys():
        raise ProtocolError("snapshot requires all 16 Sessionkeys")
    for key, kind in SESSION_SETTING_TYPES.items():
        if key in data:
            _field(data, key, kind)
    if "wakeWord.inferenceBackend" in data:
        _enum(data, "wakeWord.inferenceBackend", ("auto", "onnx", "tflite"))
    if "wakeWord.globalDisabledIds" in data:
        _field(data, "wakeWord.globalDisabledIds", "strings")


def _capabilities(data: Any) -> None:
    data = _object(data, "wakeWordCapabilities")
    _field(data, "catalogRevision", "int")
    _field(data, "availableWakeWordIds", "strings")


def parse_snapshot(data: Mapping[str, Any], *, embedded: bool = False) -> Snapshot:
    _object(data, "snapshot")
    _json_value(data)
    if embedded:
        if "type" in data:
            raise ProtocolError("embedded snapshot forbids type")
    elif data.get("type") != "session.snapshot":
        raise ProtocolError("expected session.snapshot")
    _identity(data)
    session = _field(data, "sessionId", "uuid")
    state = _field(data, "stateVersion", "int")
    seq = _field(data, "lastEventSeq", "int")
    revision = _field(data, "settingsRevision", "int")
    input_data = _field(data, "input", "object")
    phase = _enum(input_data, "phase", InputPhase)
    activation = _field(input_data, "activationId", "uuid", nullable=True)
    source = _enum(input_data, "primarySource", ("manual", "wake_word"), nullable=True)
    deadline = _field(input_data, "deadlineAtUnixMs", "int", nullable=True)
    remaining = _field(input_data, "remainingMs", "int", nullable=True)
    closed = _field(input_data, "closeRequested", "bool")
    if (deadline is None) != (remaining is None):
        raise ProtocolError("deadline fields must share nullability")
    if phase == InputPhase.IDLE:
        if any(value is not None for value in (activation, source, deadline, remaining)) or closed:
            raise ProtocolError("idle input must have null identities/deadline")
    elif activation is None or source is None or closed != (phase == InputPhase.CLOSING_INPUT):
        raise ProtocolError("inconsistent open input")
    pending_ids, sequences = set(), []
    for item in _field(data, "pendingActivations", "list"):
        item = _object(item, "pendingActivation")
        pending_id = _field(item, "activationId", "uuid")
        if pending_id in pending_ids or pending_id == activation:
            raise ProtocolError("duplicate/open pending activation")
        pending_ids.add(pending_id)
        sequences.append(_field(item, "activationSequence", "int", minimum=1))
        _field(item, "inputClosedReason", "str")
        _enum(item, "processingState", ("draining",))
        _field(item, "acceptedSegmentCount", "int")
        _field(item, "terminalSegmentCount", "int")
    if sequences != sorted(set(sequences)):
        raise ProtocolError("pendingActivations must be strictly sequence sorted")
    trigger = _field(data, "trigger", "object")
    for key in ("configured", "suppressed", "effective"):
        _mask(_field(trigger, key, "object"))
    _field(data, "audioAvailable", "bool")
    _settings_map(_field(data, "requestedSettings", "object"), complete=True)
    _settings_map(_field(data, "effectiveSettings", "object"), complete=True)
    _capabilities(_field(data, "wakeWordCapabilities", "object"))
    return Snapshot("session.snapshot", _freeze(data), session, state, seq, revision)


def parse_log_access(data: Mapping[str, Any], *, sessionId: str) -> LogAccess:
    _object(data, "logAccess")
    _json_value(data)
    available = _field(data, "available", "bool")
    if not available:
        for key in ("code", "reason"):
            _field(data, key, "str")
        if "accessToken" in data:
            raise ProtocolError("unavailable logAccess forbids token")
    else:
        for key in ("accessToken", "serverInstanceId"):
            _field(data, key, "str")
        for key in ("websocketPath", "historyPath"):
            path = _field(data, key, "str")
            if not path.startswith("/") or path.startswith("//") or "\\" in path or "?" in path or "#" in path:
                raise ProtocolError("logAccess paths must be origin-relative")
        if _field(data, "sessionId", "uuid") != sessionId:
            raise ProtocolError("logAccess sessionId mismatch")
        if _field(data, "logProtocolVersion", "int") != 2:
            raise ProtocolError("unsupported logProtocolVersion")
        _enum(data, "deliveryMode", ("sqlite_first",))
        if _field(data, "replayAvailable", "bool") is not True:
            raise ProtocolError("logAccess requires replay")
        oldest = _field(data, "oldestCursor", "int")
        latest = _field(data, "latestCursor", "int")
        if oldest > latest and latest != 0:
            raise ProtocolError("invalid logAccess cursors")
        expires = _field(data, "expiresAt", "str")
        try:
            if datetime.fromisoformat(expires.replace("Z", "+00:00")).utcoffset() is None:
                raise ValueError
        except ValueError:
            raise ProtocolError("invalid expiresAt") from None
    return LogAccess(available, _freeze(data))


def _event_fields(data: Mapping, event_type: str) -> None:
    if event_type in (EventType.WAKE_AVAILABILITY, EventType.SETTINGS_CHANGED,
                      EventType.TRIGGER_SUPPRESSED):
        if event_type == EventType.WAKE_AVAILABILITY:
            _capabilities(data)
        elif event_type == EventType.SETTINGS_CHANGED:
            _field(data, "settingsRevision", "int")
            _enum(data, "scope", ("session",))
            keys = _field(data, "changedKeys", "strings")
            if keys != sorted(set(keys)):
                raise ProtocolError("changedKeys must be sorted and unique")
            _enum(data, "applyPolicy", ApplyPolicy)
        else:
            _enum(data, "source", ("manual",))
            _enum(data, "reason", ("trigger_suppressed",))
        return
    _field(data, "activationId", "uuid", nullable=event_type == EventType.PHASE_CHANGED)
    if event_type == EventType.ACTIVATION_STARTED:
        _field(data, "activationSequence", "int", minimum=1)
        _enum(data, "primarySource", ("manual", "wake_word"))
        _enum(data, "inputPhase", (InputPhase.WAITING_FIRST_SPEECH,))
        _settings_map(_field(data, "effectiveSettings", "object"))
    elif event_type == EventType.PHASE_CHANGED:
        for key in ("previousPhase", "inputPhase"):
            _enum(data, key, InputPhase)
        for key in ("deadlineAtUnixMs", "remainingMs"):
            _field(data, key, "int", nullable=True)
    elif event_type == EventType.INPUT_CLOSED:
        _field(data, "reason", "str")
        _field(data, "causedByCommandId", "uuid", nullable=True)
        _field(data, "acceptedSegmentCount", "int")
    elif event_type in (EventType.ACTIVATION_COMPLETED, EventType.ACTIVATION_CANCELLED,
                        EventType.ACTIVATION_FAILED):
        for key in ("acceptedSegmentCount", "terminalSegmentCount"):
            _field(data, key, "int")
        if event_type != EventType.ACTIVATION_COMPLETED:
            _field(data, "reason", "str")
    elif event_type == EventType.WAKE_DETECTED:
        _field(data, "wakeWordId", "str")
        _field(data, "score", "number", nullable=True)
        _enum(data, "primarySource", ("wake_word",))
    else:
        nullable = event_type == EventType.WATCHDOG_WARNING
        segment = _field(data, "segmentId", "uuid", nullable=nullable)
        sequence = _field(data, "segmentSequence", "int", minimum=1, nullable=nullable)
        if nullable and (segment is None) != (sequence is None):
            raise ProtocolError("segment identity fields must share nullability")
        if event_type == EventType.WATCHDOG_WARNING:
            for key in ("deadlineAtUnixMs", "remainingMs"):
                _field(data, key, "int", nullable=True)
        elif event_type in (EventType.RECORDING_ENDED, EventType.DISCARDED, EventType.FAILED):
            _field(data, "reason", "str")
        elif event_type in (EventType.INTERIM, EventType.COMPLETED):
            _field(data, "text", "text")
            # Optional stabilizer fields are advisory. Keep even novel/wrong
            # types for diagnostics; preview_text falls back to mandatory text.


def _load_object(frame: str | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(frame, str):
        try:
            frame = json.loads(frame)
        except (ValueError, RecursionError):
            raise ProtocolError("invalid JSON text frame") from None
    data = _object(frame, "text frame")
    _json_value(data)
    return data


def decode_server_message(frame: str | Mapping[str, Any]) -> WireMessage | None:
    data = _load_object(frame)
    event_type = _field(data, "type", "str")
    if event_type == "session.snapshot":
        return parse_snapshot(data)
    if event_type == "hello.accepted":
        _identity(data)
        session = _field(data, "sessionId", "uuid")
        snapshot = parse_snapshot(_field(data, "snapshot", "object"), embedded=True)
        if snapshot.sessionId != session or any(data[key] != snapshot.payload[key]
                                                 for key in ("protocolVersion", "serverVersion", "serverCommit")):
            raise ProtocolError("hello/snapshot identity mismatch")
        access = parse_log_access(_field(data, "logAccess", "object"), sessionId=session)
        # Token appears only once in memory, in the dedicated redacted model.
        return HelloAccepted(event_type, _freeze({key: value for key, value in data.items()
                                                  if key != "logAccess"}), session, snapshot, access)
    if event_type in ("protocol.incompatible", "session.rejected"):
        for key in ("reason", "serverCommit"):
            _field(data, key, "str")
        _field(data, "serverVersion", "text")
        versions = _field(data, "supportedProtocolVersions", "list")
        if not versions or any(type(version) is not int for version in versions):
            raise ProtocolError("invalid supportedProtocolVersions")
        if "sessionId" in data:
            raise ProtocolError("refusal cannot identify an admitted session")
        _errors(data, required=event_type == "session.rejected")
        return HandshakeRejected(event_type, _freeze(data))
    if event_type == "command.ack":
        _version(data)
        result = AckResult(_enum(data, "result", AckResult))
        accepted = _field(data, "accepted", "bool")
        if accepted != (result in (AckResult.APPLIED, AckResult.NO_CHANGE)):
            raise ProtocolError("accepted/result mismatch")
        _errors(data)
        return CommandAck(event_type, _freeze(data), _field(data, "sessionId", "uuid"),
                          _field(data, "commandId", "uuid"), accepted, result,
                          _field(data, "activationId", "uuid", nullable=True),
                          InputPhase(_enum(data, "inputPhase", InputPhase)),
                          _field(data, "stateVersion", "int"), _field(data, "settingsRevision", "int"))
    known = event_type in EventType
    if not known and not any(key in data for key in ("eventId", "eventSeq")):
        return None
    _version(data)
    session = _field(data, "sessionId", "uuid")
    event_id = _field(data, "eventId", "uuid")
    seq = _field(data, "eventSeq", "int", minimum=1)
    state = _field(data, "stateVersion", "int")
    occurred = _field(data, "occurredAtUnixMs", "int")
    if known:
        _event_fields(data, event_type)
    model = Event if known else UnknownEvent
    return model(event_type, _freeze(data), session, event_id, seq, state, occurred)


class RevisionScope(StrEnum):
    SESSION = "session"
    SERVER = "server"


@dataclass(frozen=True)
class SettingsSchema:
    payload: Mapping[str, Any] = field(repr=False)


@dataclass(frozen=True)
class ServerSettings:
    settingsRevision: int
    payload: Mapping[str, Any] = field(repr=False)
    revisionScope: RevisionScope = field(default=RevisionScope.SERVER, init=False)


@dataclass(frozen=True)
class SettingsPatchResponse:
    settingsRevision: int
    revisionScope: RevisionScope
    accepted: bool
    result: AckResult
    payload: Mapping[str, Any] = field(repr=False)


def _setting_value(data: Mapping, key: str, setting_type: str) -> None:
    kinds = {"int": "int", "float": "number", "bool": "bool", "string": "text", "string_list": "strings"}
    _field(data, key, kinds[setting_type], minimum=-(2**63))


def _setting_entry(data: Any) -> str:
    data = _object(data, "setting")
    _field(data, "key", "str")
    _enum(data, "scope", ("session", "server", "client_local"))
    _enum(data, "auth", ("session", "admin"))
    kind = _enum(data, "type", ("int", "float", "bool", "string", "string_list"))
    _field(data, "constraints", "object")
    _enum(data, "applyPolicy", ApplyPolicy)
    return kind


def decode_settings_schema(frame: str | Mapping[str, Any]) -> SettingsSchema:
    data = _load_object(frame)
    _identity(data)
    if _field(data, "secretsExposed", "bool") is not False:
        raise ProtocolError("schema must not expose secrets")
    seen = set()
    for entry in _field(data, "settings", "list"):
        kind = _setting_entry(entry)
        if entry["key"] in seen:
            raise ProtocolError("duplicate setting key")
        seen.add(entry["key"])
        _setting_value(entry, "defaultValue", kind)
    return SettingsSchema(_freeze(data))


def decode_server_settings(frame: str | Mapping[str, Any]) -> ServerSettings:
    data = _load_object(frame)
    _identity(data)
    revision = _field(data, "settingsRevision", "int")
    seen = set()
    for entry in _field(data, "settings", "list"):
        kind = _setting_entry(entry)
        if entry["key"] in seen:
            raise ProtocolError("duplicate setting key")
        seen.add(entry["key"])
        for key in ("requestedValue", "effectiveValue"):
            _setting_value(entry, key, kind)
    return ServerSettings(revision, _freeze(data))


def encode_server_settings_patch(baseSettingsRevision: int, changes: Mapping[str, Any]) -> str:
    data = {"baseSettingsRevision": baseSettingsRevision, "changes": changes}
    _json_value(data)
    _patch_request(data)
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def decode_settings_patch_response(frame: str | Mapping[str, Any], *,
                                   revisionScope: RevisionScope) -> SettingsPatchResponse:
    data = _load_object(frame)
    scope = RevisionScope(revisionScope)
    revision = _field(data, "settingsRevision", "int")
    result = AckResult(_enum(data, "result", (
        "applied", "no_change", "settings_revision_conflict", "settings_rejected", "internal_error")))
    accepted = _field(data, "accepted", "bool")
    if accepted != (result in (AckResult.APPLIED, AckResult.NO_CHANGE)):
        raise ProtocolError("accepted/result mismatch")
    keys = _field(data, "changedKeys", "strings")
    if keys != sorted(set(keys)):
        raise ProtocolError("changedKeys must be sorted and unique")
    for key in ("values", "effectiveValues"):
        _settings_map(_field(data, key, "object"))
    policies = _field(data, "applyPolicies", "object")
    for policy in policies.values():
        if policy not in ApplyPolicy:
            raise ProtocolError("invalid applyPolicies")
    _errors(data)
    if "requiresRestart" in data:
        _field(data, "requiresRestart", "bool")
    return SettingsPatchResponse(revision, scope, accepted, result, _freeze(data))


def encode_audio_packet(pcm_data: bytes | bytearray | memoryview, sample_rate: int,
                        channels: int = 1, frames: int | None = None, *,
                        max_audio_packet_bytes: int = DEFAULT_MAX_AUDIO_PACKET_BYTES) -> bytes:
    """Existing uint32LE + JSON + PCM16LE layout, validated before allocation.

    Input is already signed int16 little-endian (capture does this today).
    Float conversion/clamping belongs to the capture adapter, not this codec.
    """
    metadata = {"sampleRate": sample_rate, "channels": channels, "format": "pcm_s16le"}
    if frames is not None:
        metadata["frames"] = frames
    if not isinstance(pcm_data, (bytes, bytearray, memoryview)):
        raise ProtocolError("PCM must be bytes-like")
    size = pcm_data.nbytes if isinstance(pcm_data, memoryview) else len(pcm_data)
    _validate_audio(metadata, size, max_audio_packet_bytes)
    # Match the pre-existing client encoder, including metadata whitespace.
    encoded = json.dumps(metadata, allow_nan=False).encode("utf-8")
    if len(encoded) > MAX_METADATA_BYTES:
        raise ProtocolError("audio metadata exceeds limit")
    return struct.pack("<I", len(encoded)) + encoded + bytes(pcm_data)


def _validate_audio(metadata: Mapping, size: int, limit: int) -> None:
    _field(metadata, "sampleRate", "int", minimum=1)
    channels = _field(metadata, "channels", "int", minimum=1) if "channels" in metadata else 1
    if channels > 8:
        raise ProtocolError("channels exceeds 8")
    if metadata.get("format", "pcm_s16le") != "pcm_s16le":
        raise ProtocolError("unsupported audio format")
    if type(limit) is not int or limit < 0:
        raise ProtocolError("invalid max_audio_packet_bytes")
    if size > limit or size % (channels * 2):
        raise ProtocolError("PCM size exceeds limit or channel alignment")
    if "frames" in metadata and _field(metadata, "frames", "int", minimum=1) * channels * 2 != size:
        raise ProtocolError("frames does not match PCM size")


@dataclass(frozen=True)
class AudioPacket:
    metadata: Mapping[str, Any]
    pcm: bytes = field(repr=False)


def decode_audio_packet(frame: bytes | bytearray | memoryview, *,
                        max_audio_packet_bytes: int = DEFAULT_MAX_AUDIO_PACKET_BYTES) -> AudioPacket:
    if not isinstance(frame, (bytes, bytearray, memoryview)):
        raise ProtocolError("audio frame must be binary")
    if type(max_audio_packet_bytes) is not int or max_audio_packet_bytes < 0:
        raise ProtocolError("invalid max_audio_packet_bytes")
    frame_size = frame.nbytes if isinstance(frame, memoryview) else len(frame)
    if frame_size > 4 + MAX_METADATA_BYTES + max_audio_packet_bytes:
        raise ProtocolError("audio frame exceeds maximum total size")
    data = bytes(frame)
    if len(data) < 4:
        raise ProtocolError("missing metadata length")
    size = struct.unpack("<I", data[:4])[0]
    if size > MAX_METADATA_BYTES or len(data) < 4 + size:
        raise ProtocolError("metadata exceeds limit or is incomplete")
    try:
        metadata = _load_object(data[4:4 + size].decode("utf-8"))
    except UnicodeDecodeError:
        raise ProtocolError("invalid metadata UTF-8") from None
    pcm = data[4 + size:]
    _validate_audio(metadata, len(pcm), max_audio_packet_bytes)
    return AudioPacket(_freeze(metadata), pcm)
