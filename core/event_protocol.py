"""Strict protocol processing for the reliable AP07 ``/ws/logs`` stream."""

from __future__ import annotations

import json
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from core.event_cursor_store import EventCursorStore, normalize_endpoint
from core.event_models import (
    EventConnectionState,
    EventEnvelope,
    EventOrigin,
    LogControlMessage,
    LogMessageType,
)


EXPECTED_LOG_PROTOCOL_VERSION = 2
EXPECTED_DELIVERY_MODE = "sqlite_first"
SESSION_CHANNELS = frozenset({"audit", "performance", "transcription"})


class EventProtocolError(ValueError):
    """The server sent a frame that violates the documented log protocol."""


class EventResultKind(str, Enum):
    HELLO = "hello"
    SUBSCRIBED = "subscribed"
    EVENT = "event"
    REPLAY_COMPLETED = "replay_completed"
    GAP = "gap"
    ERROR = "error"
    PONG = "pong"
    KEEPALIVE = "keepalive"


class EventProtocolIssue(str, Enum):
    RETENTION_GAP = "retention_gap"
    CURSOR_AHEAD = "cursor_ahead"
    STORE_UNAVAILABLE = "store_unavailable"
    AUTHORIZATION = "authorization"
    INVALID_REQUEST = "invalid_request"
    LIVE_DISABLED = "live_disabled"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class EventStreamAccess:
    """In-memory session-scoped access handed over by ``hello.logAccess``."""

    endpoint: str
    session_id: str
    access_token: str = field(repr=False, compare=False)
    server_instance_id: str = ""
    protocol_version: int = EXPECTED_LOG_PROTOCOL_VERSION
    delivery_mode: str = EXPECTED_DELIVERY_MODE
    replay_available: bool = True
    oldest_cursor: int = 0
    latest_cursor: int = 0
    channels: tuple[str, ...] = ("transcription",)

    def __post_init__(self) -> None:
        object.__setattr__(self, "endpoint", normalize_endpoint(self.endpoint))
        if not isinstance(self.session_id, str) or not self.session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        if not isinstance(self.access_token, str) or not self.access_token:
            raise ValueError("access_token must be a non-empty string")
        if (
            not isinstance(self.server_instance_id, str)
            or not self.server_instance_id.strip()
        ):
            raise ValueError("server_instance_id must be a non-empty string")
        if self.protocol_version != EXPECTED_LOG_PROTOCOL_VERSION:
            raise ValueError("unsupported log protocol version")
        if self.delivery_mode != EXPECTED_DELIVERY_MODE:
            raise ValueError("unsupported log delivery mode")
        if self.replay_available is not True:
            raise ValueError("reliable event access requires replay support")
        for name, value in (
            ("oldest_cursor", self.oldest_cursor),
            ("latest_cursor", self.latest_cursor),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be an integer >= 0")
        if self.oldest_cursor > self.latest_cursor and self.latest_cursor != 0:
            raise ValueError("oldest_cursor cannot exceed latest_cursor")
        if not isinstance(self.channels, tuple) or not self.channels:
            raise ValueError("channels must be a non-empty tuple")
        normalized_channels = tuple(sorted(set(self.channels)))
        if any(channel not in SESSION_CHANNELS for channel in normalized_channels):
            raise ValueError("channels contain a value outside the session scope")
        object.__setattr__(self, "session_id", self.session_id.strip())
        object.__setattr__(
            self, "server_instance_id", self.server_instance_id.strip()
        )
        object.__setattr__(self, "channels", normalized_channels)

    def subscribe_payload(self, after_cursor: int) -> dict[str, Any]:
        if (
            isinstance(after_cursor, bool)
            or not isinstance(after_cursor, int)
            or after_cursor < 0
        ):
            raise ValueError("after_cursor must be an integer >= 0")
        return {
            "type": "subscribe",
            "accessToken": self.access_token,
            "sessionId": self.session_id,
            "channels": list(self.channels),
            "afterCursor": after_cursor,
        }


@dataclass(frozen=True)
class EventProtocolResult:
    kind: EventResultKind
    connection_state: EventConnectionState
    control: Optional[LogControlMessage] = None
    event: Optional[EventEnvelope] = None
    origin: Optional[EventOrigin] = None
    cursor: Optional[int] = None
    duplicate: bool = False
    issue: Optional[EventProtocolIssue] = None
    payload: Mapping[str, Any] = field(default_factory=dict)

    @property
    def event_id(self) -> Optional[str]:
        return self.event.event_id if self.event is not None else None


def _freeze_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({
            str(key): _freeze_value(item) for key, item in value.items()
        })
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_value(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze_value(item) for item in value)
    return value


def _freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return _freeze_value(value)


def _required_string(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise EventProtocolError(f"{key} must be a non-empty string")
    return value.strip()


def _required_int(data: Mapping[str, Any], key: str, *, minimum: int = 0) -> int:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise EventProtocolError(f"{key} must be an integer >= {minimum}")
    return value


def _required_bool(data: Mapping[str, Any], key: str) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise EventProtocolError(f"{key} must be a boolean")
    return value


class EventProtocolProcessor:
    """Validate ordering, cursors and acknowledgements for one log access."""

    def __init__(
        self,
        access: EventStreamAccess,
        *,
        cursor_store: Optional[EventCursorStore] = None,
        dedupe_limit: int = 2048,
    ) -> None:
        if isinstance(dedupe_limit, bool) or not isinstance(dedupe_limit, int):
            raise ValueError("dedupe_limit must be an integer")
        if dedupe_limit < 1:
            raise ValueError("dedupe_limit must be >= 1")
        self._access = access
        self._cursor_store = cursor_store
        self._dedupe_limit = dedupe_limit
        self._confirmed_ids: OrderedDict[str, int] = OrderedDict()
        self._pending_events: dict[str, int] = {}
        self._state = EventConnectionState.STOPPED
        self._hello_seen = False
        self._subscribed = False
        self._last_seen_cursor = 0
        self._resume_cursor = 0
        self._server_latest_cursor = access.latest_cursor

    @property
    def state(self) -> EventConnectionState:
        return self._state

    @property
    def access(self) -> EventStreamAccess:
        return self._access

    @property
    def resume_cursor(self) -> int:
        return self._resume_cursor

    @property
    def server_latest_cursor(self) -> int:
        return self._server_latest_cursor

    def reconfigure(self, access: EventStreamAccess) -> None:
        self._access = access
        self._confirmed_ids.clear()
        self._pending_events.clear()
        self._state = EventConnectionState.STOPPED
        self._resume_cursor = 0

    def begin_subscription(self) -> int:
        self._hello_seen = False
        self._subscribed = False
        self._pending_events.clear()
        self._last_seen_cursor = 0
        self._server_latest_cursor = self._access.latest_cursor
        if self._cursor_store is not None:
            self._resume_cursor = 0
            record = self._cursor_store.load(
                endpoint=self._access.endpoint,
                server_instance_id=self._access.server_instance_id,
                protocol_version=self._access.protocol_version,
            )
            if record is not None:
                self._resume_cursor = record.cursor
        self._last_seen_cursor = self._resume_cursor
        self._state = EventConnectionState.SUBSCRIBING
        return self._resume_cursor

    def stop(self) -> None:
        self._pending_events.clear()
        self._state = EventConnectionState.STOPPED

    def process_frame(self, frame: object) -> EventProtocolResult:
        if not isinstance(frame, str):
            raise EventProtocolError("/ws/logs must only send text frames")
        try:
            raw = json.loads(frame)
        except json.JSONDecodeError as exc:
            raise EventProtocolError("invalid JSON text frame") from exc
        if not isinstance(raw, Mapping):
            raise EventProtocolError("log message must be a JSON object")
        return self.process_mapping(raw)

    def process_mapping(self, raw: Mapping[str, Any]) -> EventProtocolResult:
        try:
            control = LogControlMessage.from_mapping(raw)
        except ValueError as exc:
            raise EventProtocolError(str(exc)) from exc
        message_type = control.message_type
        if message_type is LogMessageType.HELLO:
            return self._process_hello(raw, control)
        if message_type is LogMessageType.SUBSCRIBED:
            return self._process_subscribed(raw, control)
        if message_type is LogMessageType.EVENT:
            return self._process_event(raw, control)
        if message_type is LogMessageType.REPLAY_COMPLETED:
            return self._process_replay_completed(raw, control)
        if message_type is LogMessageType.GAP:
            return self._process_gap(raw, control)
        if message_type is LogMessageType.ERROR:
            return self._process_error(raw, control)
        if message_type is LogMessageType.PONG:
            return self._process_cursor_control(
                raw, control, EventResultKind.PONG
            )
        if message_type is LogMessageType.KEEPALIVE:
            return self._process_cursor_control(
                raw, control, EventResultKind.KEEPALIVE
            )
        raise EventProtocolError(f"unsupported message type: {message_type.value}")

    def confirm_event(self, result: EventProtocolResult) -> None:
        if result.kind is not EventResultKind.EVENT or result.event is None:
            raise ValueError("only event results can be confirmed")
        if result.duplicate:
            return
        event_id = result.event.event_id
        cursor = result.event.cursor
        if self._pending_events.get(event_id) != cursor:
            raise ValueError("event is not pending confirmation")
        if self._cursor_store is not None:
            self._cursor_store.commit(
                cursor,
                endpoint=self._access.endpoint,
                server_instance_id=self._access.server_instance_id,
                protocol_version=self._access.protocol_version,
            )
        self._resume_cursor = max(self._resume_cursor, cursor)
        self._pending_events.pop(event_id, None)
        self._confirmed_ids[event_id] = cursor
        self._confirmed_ids.move_to_end(event_id)
        while len(self._confirmed_ids) > self._dedupe_limit:
            self._confirmed_ids.popitem(last=False)

    def reject_event(self, result: EventProtocolResult) -> None:
        if result.event is not None:
            self._pending_events.pop(result.event.event_id, None)

    def _process_hello(
        self, raw: Mapping[str, Any], control: LogControlMessage
    ) -> EventProtocolResult:
        if self._state is not EventConnectionState.SUBSCRIBING or self._hello_seen:
            raise EventProtocolError("log.hello arrived out of order")
        schema = _required_int(raw, "schemaVersion", minimum=1)
        protocol = _required_int(raw, "logProtocolVersion", minimum=1)
        delivery_mode = _required_string(raw, "deliveryMode")
        replay_available = _required_bool(raw, "replayAvailable")
        server_instance = _required_string(raw, "serverInstanceId")
        oldest = _required_int(raw, "oldestCursor")
        latest = _required_int(raw, "latestCursor")
        retention = _required_int(raw, "retentionCursor")
        if schema != 1:
            raise EventProtocolError("unsupported log.hello schemaVersion")
        if protocol != self._access.protocol_version:
            raise EventProtocolError("logProtocolVersion does not match logAccess")
        if delivery_mode != self._access.delivery_mode:
            raise EventProtocolError("deliveryMode does not match logAccess")
        if replay_available is not True:
            raise EventProtocolError("log stream does not support replay")
        if server_instance != self._access.server_instance_id:
            raise EventProtocolError("serverInstanceId does not match logAccess")
        if oldest > latest and latest != 0:
            raise EventProtocolError("oldestCursor exceeds latestCursor")
        if retention > latest:
            raise EventProtocolError("retentionCursor exceeds latestCursor")
        self._server_latest_cursor = latest
        self._hello_seen = True
        return EventProtocolResult(
            kind=EventResultKind.HELLO,
            connection_state=self._state,
            control=control,
            cursor=latest,
            payload=_freeze_mapping(raw),
        )

    def _process_subscribed(
        self, raw: Mapping[str, Any], control: LogControlMessage
    ) -> EventProtocolResult:
        if not self._hello_seen or self._subscribed:
            raise EventProtocolError("log.subscribed arrived out of order")
        if _required_string(raw, "authorizationScope") != "session":
            raise EventProtocolError("desktop log access must remain session-scoped")
        if _required_bool(raw, "allSessions"):
            raise EventProtocolError("session subscription cannot include all sessions")
        if _required_bool(raw, "allChannels"):
            raise EventProtocolError("session subscription cannot include all channels")
        if _required_string(raw, "sessionId") != self._access.session_id:
            raise EventProtocolError("subscribed sessionId does not match logAccess")
        after_cursor = _required_int(raw, "afterCursor")
        if after_cursor != self._resume_cursor:
            raise EventProtocolError("server confirmed a different afterCursor")
        channels_raw = raw.get("channels")
        if not isinstance(channels_raw, list) or any(
            not isinstance(channel, str) or not channel for channel in channels_raw
        ):
            raise EventProtocolError("channels must be a list of non-empty strings")
        if set(channels_raw) != set(self._access.channels):
            raise EventProtocolError("effective channels do not match the request")
        self._subscribed = True
        self._state = EventConnectionState.REPLAYING
        return EventProtocolResult(
            kind=EventResultKind.SUBSCRIBED,
            connection_state=self._state,
            control=control,
            cursor=after_cursor,
            payload=_freeze_mapping(raw),
        )

    def _process_event(
        self, raw: Mapping[str, Any], control: LogControlMessage
    ) -> EventProtocolResult:
        if not self._subscribed or self._state not in {
            EventConnectionState.REPLAYING,
            EventConnectionState.LIVE,
        }:
            raise EventProtocolError("log.event arrived before subscription")
        replay = _required_bool(raw, "replay")
        expected_replay = self._state is EventConnectionState.REPLAYING
        if replay is not expected_replay:
            raise EventProtocolError("event replay flag contradicts stream phase")
        event_raw = raw.get("event")
        if not isinstance(event_raw, Mapping):
            raise EventProtocolError("log.event.event must be an object")
        try:
            event = EventEnvelope.from_mapping(event_raw)
        except ValueError as exc:
            raise EventProtocolError(str(exc)) from exc
        if event.session_id != self._access.session_id:
            raise EventProtocolError("event sessionId does not match subscription")
        if event.channel not in self._access.channels:
            raise EventProtocolError("event channel is outside the subscription")
        confirmed_cursor = self._confirmed_ids.get(event.event_id)
        if confirmed_cursor is not None:
            if confirmed_cursor != event.cursor:
                raise EventProtocolError("duplicate eventId changed its cursor")
            return EventProtocolResult(
                kind=EventResultKind.EVENT,
                connection_state=self._state,
                control=control,
                event=event,
                origin=EventOrigin.REPLAY if replay else EventOrigin.LIVE,
                cursor=event.cursor,
                duplicate=True,
                payload=_freeze_mapping(raw),
            )
        if event.event_id in self._pending_events:
            raise EventProtocolError("eventId repeated before confirmation")
        if event.cursor <= self._last_seen_cursor:
            raise EventProtocolError("event cursor is not monotonically increasing")
        self._last_seen_cursor = event.cursor
        self._pending_events[event.event_id] = event.cursor
        return EventProtocolResult(
            kind=EventResultKind.EVENT,
            connection_state=self._state,
            control=control,
            event=event,
            origin=EventOrigin.REPLAY if replay else EventOrigin.LIVE,
            cursor=event.cursor,
            payload=_freeze_mapping(raw),
        )

    def _process_replay_completed(
        self, raw: Mapping[str, Any], control: LogControlMessage
    ) -> EventProtocolResult:
        if self._state is not EventConnectionState.REPLAYING:
            raise EventProtocolError("log.replay_completed arrived out of order")
        cursor = _required_int(raw, "cursor")
        _required_int(raw, "count")
        if cursor < self._last_seen_cursor:
            raise EventProtocolError("replay watermark is behind an event cursor")
        if cursor > self._server_latest_cursor:
            raise EventProtocolError("replay watermark exceeds log.hello latestCursor")
        self._state = EventConnectionState.LIVE
        return EventProtocolResult(
            kind=EventResultKind.REPLAY_COMPLETED,
            connection_state=self._state,
            control=control,
            cursor=cursor,
            payload=_freeze_mapping(raw),
        )

    def _process_gap(
        self, raw: Mapping[str, Any], control: LogControlMessage
    ) -> EventProtocolResult:
        if not self._subscribed:
            raise EventProtocolError("log.gap arrived before subscription")
        if _required_string(raw, "reason") != "retention":
            raise EventProtocolError("unsupported log.gap reason")
        lost_from = _required_int(raw, "lostFromCursor")
        lost_to = _required_int(raw, "lostToCursor")
        if lost_to < lost_from:
            raise EventProtocolError("retention gap range is inverted")
        _required_int(raw, "oldestCursor")
        latest = _required_int(raw, "latestCursor")
        self._server_latest_cursor = max(self._server_latest_cursor, latest)
        return EventProtocolResult(
            kind=EventResultKind.GAP,
            connection_state=self._state,
            control=control,
            cursor=lost_to,
            issue=EventProtocolIssue.RETENTION_GAP,
            payload=_freeze_mapping(raw),
        )

    def _process_error(
        self, raw: Mapping[str, Any], control: LogControlMessage
    ) -> EventProtocolResult:
        code = raw.get("code")
        if code is not None and (not isinstance(code, str) or not code.strip()):
            raise EventProtocolError("log.error.code must be a non-empty string")
        mapping = {
            "cursor_ahead": EventProtocolIssue.CURSOR_AHEAD,
            "event_store_unavailable": EventProtocolIssue.STORE_UNAVAILABLE,
            "not_authorized": EventProtocolIssue.AUTHORIZATION,
            "invalid_cursor": EventProtocolIssue.INVALID_REQUEST,
            "invalid_request": EventProtocolIssue.INVALID_REQUEST,
            "log_live_disabled": EventProtocolIssue.LIVE_DISABLED,
        }
        issue = mapping.get(code, EventProtocolIssue.UNKNOWN)
        if code == "cursor_ahead":
            latest = _required_int(raw, "latestCursor")
            _required_string(raw, "serverInstanceId")
            self._server_latest_cursor = latest
        self._state = EventConnectionState.DEGRADED
        return EventProtocolResult(
            kind=EventResultKind.ERROR,
            connection_state=self._state,
            control=control,
            cursor=raw.get("latestCursor"),
            issue=issue,
            payload=_freeze_mapping(raw),
        )

    def _process_cursor_control(
        self,
        raw: Mapping[str, Any],
        control: LogControlMessage,
        kind: EventResultKind,
    ) -> EventProtocolResult:
        if self._state is not EventConnectionState.LIVE:
            raise EventProtocolError(f"log.{kind.value} arrived before live phase")
        cursor = _required_int(raw, "cursor")
        if cursor < self._last_seen_cursor:
            raise EventProtocolError("control cursor moved backwards")
        if kind is EventResultKind.PONG:
            server_time = raw.get("serverTime")
            if (
                isinstance(server_time, bool)
                or not isinstance(server_time, (int, float))
            ):
                raise EventProtocolError("serverTime must be numeric")
        else:
            _required_int(raw, "eventsSent")
        return EventProtocolResult(
            kind=kind,
            connection_state=self._state,
            control=control,
            cursor=cursor,
            payload=_freeze_mapping(raw),
        )
