"""Generation-bound lifecycle coordination for STT and event WebSockets."""

from __future__ import annotations

import asyncio
import inspect
import logging
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable, Mapping, Optional, Union

from core.config import EventStreamConfig, ServerConfig
from core.event_cursor_store import EventCursorStore
from core.event_models import EventConnectionState
from core.event_protocol import (
    EXPECTED_DELIVERY_MODE,
    EXPECTED_LOG_PROTOCOL_VERSION,
    EventProtocolProcessor,
    EventProtocolResult,
    EventStreamAccess,
)
from core.event_stream import EventStreamTransport
from core.observability.adapters.client_events import ClientEventEmitter
from core.observability.ingress import NULL_INGRESS


logger = logging.getLogger(__name__)

DownstreamResult = Union[bool, Awaitable[bool]]
DownstreamCallback = Callable[["SessionContext", EventProtocolResult], DownstreamResult]
ContextCallback = Callable[["SessionContext"], None]
TransportFactory = Callable[..., EventStreamTransport]
ObservationCallback = Callable[["SessionContext", EventProtocolResult], None]


@dataclass(frozen=True)
class SessionContext:
    """Current STT generation and its optional, session-scoped log access."""

    generation: int = 0
    session_id: Optional[str] = None
    log_access: Optional[EventStreamAccess] = field(default=None, repr=False)
    event_state: EventConnectionState = EventConnectionState.STOPPED
    token_expires_at: Optional[datetime] = None
    unavailable_code: Optional[str] = None
    unavailable_reason: Optional[str] = None

    @property
    def event_available(self) -> bool:
        return self.log_access is not None and self.event_state not in {
            EventConnectionState.UNAVAILABLE,
            EventConnectionState.STOPPED,
        }

    def token_is_valid(self, now: Optional[datetime] = None) -> bool:
        if self.log_access is None or self.token_expires_at is None:
            return False
        current = now or datetime.now(timezone.utc)
        return current < self.token_expires_at


@dataclass(frozen=True)
class _DetachedTransport:
    transport: Optional[EventStreamTransport]
    run_task: Optional[asyncio.Task]
    expiry_task: Optional[asyncio.Task]


class DualSessionCoordinator:
    """Own exactly one event transport for the current STT generation."""

    def __init__(
        self,
        server_config: ServerConfig,
        event_config: EventStreamConfig,
        *,
        cursor_store: Optional[EventCursorStore] = None,
        transport_factory: Optional[TransportFactory] = None,
        on_event: Optional[DownstreamCallback] = None,
        on_context_change: Optional[ContextCallback] = None,
        observability: Any = NULL_INGRESS,
    ) -> None:
        server_config.validate()
        event_config.validate()
        self._server_config = server_config
        self._event_config = event_config
        if cursor_store is not None:
            self._cursor_store = cursor_store
        elif event_config.cursor_persistence_enabled:
            path = (
                Path(event_config.cursor_path).expanduser()
                if event_config.cursor_path is not None
                else None
            )
            self._cursor_store = EventCursorStore(path)
        else:
            self._cursor_store = None
        # CONTRACTS §6, "Injektionsweg ueber die Default-Factory": an
        # externally supplied factory keeps the exact call shape it has today
        # (three positionals plus the three callbacks), while the default
        # factory closes over the observability ingress so the real transport
        # can carry the second observation point (§7.5). Without this, adding
        # a keyword to the factory call would break an existing test's own
        # factory — and "kein bestehender Test wird geaendert" (ARCH §12).
        self._transport_factory: TransportFactory = transport_factory or (
            lambda config, access, processor, **kwargs: EventStreamTransport(
                config, access, processor, observability=observability, **kwargs
            )
        )
        self.on_event = on_event
        self.on_context_change = on_context_change
        # ARCH §7.1: the fan-out hook. Set by the STTController to the
        # ServerLiveAdapter; ``None`` means nothing observes.
        self.on_observation: Optional[ObservationCallback] = None
        self._observe = ClientEventEmitter(observability, component="eventstream")
        self._context = SessionContext()
        self._transport: Optional[EventStreamTransport] = None
        self._transport_task: Optional[asyncio.Task] = None
        self._expiry_task: Optional[asyncio.Task] = None
        self._binding = 0
        self._lifecycle_lock = asyncio.Lock()
        self._shutdown = False
        self._transport_start_count = 0
        self._transport_stop_count = 0

    @property
    def context(self) -> SessionContext:
        return self._context

    @property
    def transport_start_count(self) -> int:
        return self._transport_start_count

    @property
    def transport_stop_count(self) -> int:
        return self._transport_stop_count

    @property
    def active_transport_count(self) -> int:
        return int(self._transport is not None)

    async def begin_generation(self, generation: int) -> bool:
        """Invalidate log access before a new STT handshake begins."""
        self._validate_generation(generation)
        async with self._lifecycle_lock:
            if self._shutdown or generation < self._context.generation:
                return False
            if (
                generation == self._context.generation
                and self._context.session_id is not None
            ):
                return False
            detached = self._detach_transport()
            self._set_context(SessionContext(generation=generation))
            await self._stop_detached(detached)
            return True

    async def invalidate_generation(self, generation: int) -> bool:
        """Stop log delivery as soon as its STT transport is no longer valid."""
        self._validate_generation(generation)
        async with self._lifecycle_lock:
            if self._shutdown or generation != self._context.generation:
                return False
            detached = self._detach_transport()
            self._set_context(SessionContext(generation=generation))
            await self._stop_detached(detached)
            return True

    async def adopt_hello(
        self,
        generation: int,
        hello: Mapping[str, Any],
    ) -> bool:
        """Adopt only a valid log access for the current STT session."""
        self._validate_generation(generation)
        if not isinstance(hello, Mapping):
            raise ValueError("hello must be a mapping")
        session_id = self._required_string(hello, "sessionId")
        raw_access = hello.get("logAccess")

        async with self._lifecycle_lock:
            if self._shutdown or generation != self._context.generation:
                return False

            detached = self._detach_transport()
            await self._stop_detached(detached)
            if self._shutdown or generation != self._context.generation:
                return False

            if not self._event_config.enabled:
                self._set_unavailable(
                    generation,
                    session_id,
                    "client_disabled",
                    "Event stream is disabled by client configuration",
                )
                return False
            if not isinstance(raw_access, Mapping):
                self._set_unavailable(
                    generation,
                    session_id,
                    "log_access_missing",
                    "Server hello did not provide logAccess",
                )
                return False

            available = raw_access.get("available")
            if not isinstance(available, bool):
                raise ValueError("logAccess.available must be a boolean")
            access_session_id = self._required_string(raw_access, "sessionId")
            if access_session_id != session_id:
                raise ValueError("logAccess session does not match STT hello session")
            if not available:
                self._set_unavailable(
                    generation,
                    session_id,
                    self._optional_string(raw_access, "code") or "log_unavailable",
                    self._optional_string(raw_access, "reason")
                    or "Server event stream is unavailable",
                )
                return False

            expires_at = self._parse_expiry(raw_access.get("expiresAt"))
            if expires_at <= datetime.now(timezone.utc):
                self._set_unavailable(
                    generation,
                    session_id,
                    "log_access_expired",
                    "Server log access token has already expired",
                )
                return False

            access = self._build_access(session_id, raw_access)
            processor = EventProtocolProcessor(
                access,
                cursor_store=self._cursor_store,
            )
            self._binding += 1
            binding = self._binding
            transport = self._transport_factory(
                self._event_config,
                access,
                processor,
                on_event=lambda result: self._handle_event(binding, result),
                on_control=lambda result: self._handle_control(binding, result),
                on_state_change=lambda state: self._handle_state(binding, state),
            )
            self._transport = transport
            self._set_context(
                SessionContext(
                    generation=generation,
                    session_id=session_id,
                    log_access=access,
                    event_state=EventConnectionState.CONNECTING,
                    token_expires_at=expires_at,
                )
            )
            self._transport_start_count += 1
            task = asyncio.create_task(
                transport.run(),
                name=f"event-stream-generation-{generation}",
            )
            self._transport_task = task
            task.add_done_callback(
                lambda completed: self._transport_finished(binding, completed)
            )
            self._expiry_task = asyncio.create_task(
                self._expire_at(binding, expires_at),
                name=f"event-token-expiry-{generation}",
            )
            return True

    async def update_config(
        self,
        server_config: ServerConfig,
        event_config: EventStreamConfig,
    ) -> None:
        """Use validated settings for the next session-bound event transport."""
        server_config.validate()
        event_config.validate()
        async with self._lifecycle_lock:
            if self._shutdown:
                return
            self._server_config = server_config
            self._event_config = event_config

    async def shutdown(self) -> None:
        """Idempotently stop the event side of the shared lifecycle once."""
        async with self._lifecycle_lock:
            if self._shutdown:
                return
            self._shutdown = True
            detached = self._detach_transport()
            self._set_context(
                replace(
                    self._context,
                    log_access=None,
                    event_state=EventConnectionState.STOPPED,
                    token_expires_at=None,
                )
            )
            await self._stop_detached(detached)

    def _build_access(
        self,
        session_id: str,
        raw: Mapping[str, Any],
    ) -> EventStreamAccess:
        endpoint = EventStreamConfig.build_url(
            self._server_config.url,
            self._required_string(raw, "websocketPath"),
        )
        return EventStreamAccess(
            endpoint=endpoint,
            session_id=session_id,
            access_token=self._required_string(raw, "accessToken"),
            server_instance_id=self._required_string(raw, "serverInstanceId"),
            protocol_version=self._required_int(raw, "logProtocolVersion"),
            delivery_mode=self._required_string(raw, "deliveryMode"),
            replay_available=self._required_bool(raw, "replayAvailable"),
            oldest_cursor=self._required_int(raw, "oldestCursor"),
            latest_cursor=self._required_int(raw, "latestCursor"),
            channels=("audit", "performance", "transcription"),
        )

    def _notify_observer(self, result: EventProtocolResult) -> None:
        """ARCH §7.1/§7.3: the fan-out. Return-value free, and the **last**
        line of defence against a throwing observer.

        The ``except`` body is deliberately empty. ``EventStreamTransport
        ._dispatch`` catches a propagating exception with ``except
        BaseException``, calls ``self._processor.reject_event(result)`` and
        re-raises — a throwing observer would therefore *actively discard* the
        event and recycle the connection. The visible, counted handling lives
        one level up in ``ServerLiveAdapter.observe`` (§7.3); putting a second
        report here would give the failure domain a second, unrelated voice.
        ``BaseException`` is not caught: ``asyncio.CancelledError`` must pass.
        """
        observer = self.on_observation
        if observer is None:
            return
        try:
            observer(self._context, result)
        except Exception:  # noqa: BLE001 - handling lives in the logging domain
            pass

    async def _handle_event(
        self,
        binding: int,
        result: EventProtocolResult,
    ) -> bool:
        self._notify_observer(result)
        context = self._context
        if (
            binding != self._binding
            or self._shutdown
            or context.log_access is None
            or result.event is None
            or result.event.session_id != context.session_id
            or not context.token_is_valid()
        ):
            return False
        callback = self.on_event
        if callback is not None:
            accepted = callback(context, result)
            if inspect.isawaitable(accepted):
                accepted = await accepted
            if accepted is not True:
                return False
        current = self._context
        return (
            binding == self._binding
            and not self._shutdown
            and current.generation == context.generation
            and current.session_id == context.session_id
            and current.log_access is context.log_access
            and current.token_is_valid()
        )

    def _handle_control(
        self,
        binding: int,
        result: EventProtocolResult,
    ) -> None:
        self._notify_observer(result)
        if binding != self._binding or self._shutdown:
            return
        if result.issue is not None:
            self._set_context(
                replace(
                    self._context,
                    unavailable_code=result.issue.value,
                    unavailable_reason=result.issue.value,
                )
            )

    def _handle_state(
        self,
        binding: int,
        state: EventConnectionState,
    ) -> None:
        if binding != self._binding or self._shutdown:
            return
        previous = self._context.event_state
        self._set_context(replace(self._context, event_state=state))
        # CONTRACTS §12.1: client.eventstream.state_changed, channel system.
        # After ``_set_context``, so the reported context is the one that is
        # now in force, and never before the runtime transition.
        if previous is not state:
            self._observe.system(
                "client.eventstream.state_changed",
                details={
                    "previous": previous.value,
                    "state": state.value,
                    "unavailable_code": self._context.unavailable_code,
                },
                session_id=self._context.session_id,
                generation=self._context.generation,
            )

    def _transport_finished(
        self,
        binding: int,
        task: asyncio.Task,
    ) -> None:
        if not task.cancelled():
            try:
                error = task.exception()
            except asyncio.CancelledError:
                error = None
            if error is not None:
                logger.warning("Event stream task ended: %s", error)
        if binding != self._binding or self._shutdown:
            return
        self._transport = None
        self._transport_task = None
        self._set_context(
            replace(
                self._context,
                event_state=EventConnectionState.DEGRADED,
                unavailable_code="event_stream_stopped",
                unavailable_reason="Event stream stopped unexpectedly",
            )
        )

    async def _expire_at(self, binding: int, expires_at: datetime) -> None:
        try:
            delay = max(
                0.0,
                (expires_at - datetime.now(timezone.utc)).total_seconds(),
            )
            await asyncio.sleep(delay)
            async with self._lifecycle_lock:
                if binding != self._binding or self._shutdown:
                    return
                detached = self._detach_transport()
                self._set_unavailable(
                    self._context.generation,
                    self._context.session_id or "",
                    "log_access_expired",
                    "Server log access token expired",
                )
                await self._stop_detached(detached)
        except asyncio.CancelledError:
            return

    def _detach_transport(self) -> _DetachedTransport:
        detached = _DetachedTransport(
            self._transport,
            self._transport_task,
            self._expiry_task,
        )
        if self._transport is not None:
            self._transport_stop_count += 1
        self._transport = None
        self._transport_task = None
        self._expiry_task = None
        self._binding += 1
        return detached

    async def _stop_detached(self, detached: _DetachedTransport) -> None:
        current = asyncio.current_task()
        if detached.expiry_task is not None and detached.expiry_task is not current:
            detached.expiry_task.cancel()
        if detached.transport is not None:
            await detached.transport.stop()
        waiters = [
            task
            for task in (detached.run_task, detached.expiry_task)
            if task is not None and task is not current and not task.done()
        ]
        if waiters:
            await asyncio.gather(*waiters, return_exceptions=True)

    def _set_unavailable(
        self,
        generation: int,
        session_id: str,
        code: str,
        reason: str,
    ) -> None:
        self._set_context(
            SessionContext(
                generation=generation,
                session_id=session_id or None,
                event_state=EventConnectionState.UNAVAILABLE,
                unavailable_code=code,
                unavailable_reason=reason,
            )
        )

    def _set_context(self, context: SessionContext) -> None:
        if context == self._context:
            return
        self._context = context
        callback = self.on_context_change
        if callback is not None:
            try:
                callback(context)
            except Exception:
                logger.exception("Session context callback failed")

    @staticmethod
    def _validate_generation(generation: int) -> None:
        if isinstance(generation, bool) or not isinstance(generation, int):
            raise ValueError("generation must be an integer")
        if generation < 0:
            raise ValueError("generation must be >= 0")

    @staticmethod
    def _required_string(data: Mapping[str, Any], key: str) -> str:
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} must be a non-empty string")
        return value.strip()

    @staticmethod
    def _optional_string(data: Mapping[str, Any], key: str) -> Optional[str]:
        value = data.get(key)
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} must be null or a non-empty string")
        return value.strip()

    @staticmethod
    def _required_int(data: Mapping[str, Any], key: str) -> int:
        value = data.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{key} must be an integer >= 0")
        return value

    @staticmethod
    def _required_bool(data: Mapping[str, Any], key: str) -> bool:
        value = data.get(key)
        if not isinstance(value, bool):
            raise ValueError(f"{key} must be a boolean")
        return value

    @staticmethod
    def _parse_expiry(value: Any) -> datetime:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("expiresAt must be a non-empty ISO timestamp")
        candidate = value.strip()
        if candidate.endswith("Z"):
            candidate = candidate[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(candidate)
        except ValueError as exc:
            raise ValueError("expiresAt must be a valid ISO timestamp") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("expiresAt must include a timezone")
        return parsed.astimezone(timezone.utc)
