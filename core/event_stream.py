"""Isolated reconnecting transport for the reliable AP07 ``/ws/logs`` feed."""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import math
import random
from typing import Awaitable, Callable, Optional, Union

from websockets.asyncio.client import ClientConnection, connect as ws_connect
from websockets.exceptions import ConnectionClosed

from core.config import EventStreamConfig
from core.event_models import EventConnectionState
from core.event_protocol import (
    EventProtocolIssue,
    EventProtocolProcessor,
    EventProtocolResult,
    EventResultKind,
    EventStreamAccess,
)
from core.observability.adapters.client_events import ClientEventEmitter
from core.observability.ingress import NULL_INGRESS


logger = logging.getLogger("event_stream")

CallbackResult = Union[None, bool, Awaitable[Union[None, bool]]]
EventCallback = Callable[[EventProtocolResult], CallbackResult]
StateCallback = Callable[[EventConnectionState], None]


class EventProcessingRejected(RuntimeError):
    """The downstream path didn't confirm successful event processing."""


class EventAccessInvalid(RuntimeError):
    """The current access token/session cannot be retried unchanged."""


class EventStreamTransport:
    """Connect, subscribe, replay and reconnect without any UI dependency."""

    def __init__(
        self,
        config: EventStreamConfig,
        access: EventStreamAccess,
        processor: EventProtocolProcessor,
        *,
        on_event: EventCallback,
        on_control: Optional[EventCallback] = None,
        on_state_change: Optional[StateCallback] = None,
        connect_factory=ws_connect,
        observability=NULL_INGRESS,
    ) -> None:
        config.validate()
        if processor.access != access:
            raise ValueError("processor access does not match transport access")
        if not callable(on_event):
            raise ValueError("on_event must be callable")
        self._config = config
        self._access = access
        self._processor = processor
        self._on_event = on_event
        self._on_control = on_control
        self._on_state_change = on_state_change
        self._connect_factory = connect_factory
        self._observe = ClientEventEmitter(observability, component="eventstream")
        self._state = EventConnectionState.STOPPED
        self._ws: Optional[ClientConnection] = None
        self._running = False
        self._generation = 0
        self._backoff_attempt = 0
        self._backoff_sleep_task: Optional[asyncio.Task] = None
        self._connect_task: Optional[asyncio.Future] = None
        self._access_changed = asyncio.Event()
        self._last_error: Optional[str] = None
        self._blocked_for_access = False

    @property
    def state(self) -> EventConnectionState:
        return self._state

    @property
    def generation(self) -> int:
        return self._generation

    @property
    def reconnect_attempt(self) -> int:
        return self._backoff_attempt

    @property
    def last_error(self) -> Optional[str]:
        return self._last_error

    @property
    def access(self) -> EventStreamAccess:
        return self._access

    async def run(self) -> None:
        if self._running:
            raise RuntimeError("event stream is already running")
        self._running = True
        self._blocked_for_access = False
        self._access_changed.clear()
        try:
            while self._running:
                if self._blocked_for_access:
                    self._set_state(EventConnectionState.UNAVAILABLE)
                    await self._access_changed.wait()
                    self._access_changed.clear()
                    if not self._running:
                        break
                    self._blocked_for_access = False
                try:
                    await self._connect_once()
                except asyncio.CancelledError:
                    if self._running:
                        raise
                    break
                except EventAccessInvalid as exc:
                    self._last_error = str(exc)
                    self._blocked_for_access = True
                    continue
                except Exception as exc:
                    if not self._running:
                        break
                    self._last_error = str(exc)
                    logger.warning("Event stream attempt failed: %s", exc)
                    self._observe_protocol_error(exc)
                if not self._running or self._blocked_for_access:
                    continue
                self._backoff_attempt += 1
                self._set_state(EventConnectionState.BACKOFF)
                delay = self._backoff_delay()
                try:
                    self._backoff_sleep_task = asyncio.create_task(
                        asyncio.sleep(delay)
                    )
                    await self._backoff_sleep_task
                except asyncio.CancelledError:
                    if self._running:
                        raise
                    break
                finally:
                    self._backoff_sleep_task = None
        finally:
            await self._close_socket()
            self._processor.stop()
            self._running = False
            self._set_state(EventConnectionState.STOPPED)

    def _observe_protocol_error(self, exc: BaseException) -> None:
        """The second observation point (FD-R3 / CONTRACTS §7.5, ARCH §8.5
        GRENZE 1).

        The coordinator hook sees every successfully **validated** result, not
        every frame — a server that violates the protocol never reaches the
        dispatch. This is the one place where that case becomes structured
        instead of an unstructured WARNING text. Deliberately **without** the
        raw frame: it no longer exists here (FD-R3). No additional control
        flow: one call next to the existing ``logger.warning``.
        """
        self._observe.system(
            "client.eventstream.protocol_error",
            level="WARNING",
            details={"error_type": type(exc).__name__, "message": str(exc)},
            session_id=self._access.session_id,
        )

    async def stop(self) -> None:
        """Idempotently interrupt connect, receive and backoff waits."""
        was_running = self._running
        self._running = False
        self._blocked_for_access = False
        self._access_changed.set()
        current = asyncio.current_task()
        waiters = []
        if self._backoff_sleep_task is not None and not self._backoff_sleep_task.done():
            self._backoff_sleep_task.cancel()
            if self._backoff_sleep_task is not current:
                waiters.append(self._backoff_sleep_task)
        if self._connect_task is not None and not self._connect_task.done():
            self._connect_task.cancel()
            if self._connect_task is not current:
                waiters.append(self._connect_task)
        await self._close_socket()
        if waiters:
            await asyncio.gather(*waiters, return_exceptions=True)
        if not was_running:
            self._processor.stop()
            self._set_state(EventConnectionState.STOPPED)

    async def reconfigure(self, access: EventStreamAccess) -> None:
        """Replace an expired/session-bound access object without persisting it."""
        was_blocked = self._blocked_for_access
        self._access = access
        self._processor.reconfigure(access)
        self._last_error = None
        self._blocked_for_access = False
        if was_blocked:
            self._access_changed.set()
        else:
            self._access_changed.clear()
        await self._close_socket(code=1000, reason="event_access_changed")

    async def _connect_once(self) -> None:
        self._generation += 1
        self._set_state(EventConnectionState.CONNECTING)
        resume_cursor = self._processor.begin_subscription()
        try:
            self._connect_task = asyncio.ensure_future(
                self._connect_factory(
                    self._access.endpoint,
                    max_size=self._config.max_message_size,
                    max_queue=self._config.queue_maxsize,
                    ping_interval=None,
                    ping_timeout=None,
                    close_timeout=5,
                    proxy=None,
                )
            )
            self._ws = await asyncio.wait_for(
                self._connect_task,
                timeout=self._config.connect_timeout,
            )
            self._connect_task = None
            self._set_state(EventConnectionState.SUBSCRIBING)
            await self._ws.send(
                json.dumps(self._access.subscribe_payload(resume_cursor))
            )
            await self._run_handshake()
            await self._run_replay()
            if self._running:
                await self._run_live()
        except ConnectionClosed as exc:
            code = self._connection_close_code(exc)
            if code == 1008 and self._last_error:
                raise EventAccessInvalid(self._last_error) from exc
            raise
        finally:
            self._connect_task = None
            await self._close_socket()

    async def _run_handshake(self) -> None:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + self._config.handshake_timeout
        while self._processor.state is EventConnectionState.SUBSCRIBING:
            remaining = deadline - loop.time()
            if remaining <= 0:
                raise asyncio.TimeoutError("event stream handshake timed out")
            result = await self._receive_result(remaining)
            await self._dispatch(result)
        if not self._running:
            return
        if self._processor.state is not EventConnectionState.REPLAYING:
            raise RuntimeError("event stream did not enter replay phase")
        self._set_state(EventConnectionState.REPLAYING)

    async def _run_replay(self) -> None:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + self._config.replay_timeout
        while self._processor.state is EventConnectionState.REPLAYING:
            remaining = deadline - loop.time()
            if remaining <= 0:
                raise asyncio.TimeoutError("event stream replay timed out")
            result = await self._receive_result(remaining)
            await self._dispatch(result)
        if not self._running:
            return
        if self._processor.state is not EventConnectionState.LIVE:
            raise RuntimeError("event stream did not enter live phase")
        self._backoff_attempt = 0
        self._last_error = None
        self._set_state(EventConnectionState.LIVE)

    async def _run_live(self) -> None:
        while self._running and self._processor.state is EventConnectionState.LIVE:
            try:
                result = await self._receive_result(self._config.message_timeout)
            except asyncio.TimeoutError:
                await self._ws.send(json.dumps({"type": "ping"}))
                result = await self._receive_result(self._config.message_timeout)
            await self._dispatch(result)

    async def _receive_result(self, timeout: float) -> EventProtocolResult:
        frame = await asyncio.wait_for(self._ws.recv(), timeout=timeout)
        return self._processor.process_frame(frame)

    async def _dispatch(self, result: EventProtocolResult) -> None:
        self._set_state(result.connection_state)
        if result.kind is EventResultKind.EVENT:
            if result.duplicate:
                await self._call(self._on_control, result)
                return
            try:
                accepted = await self._call(self._on_event, result)
                if accepted is not True:
                    raise EventProcessingRejected(
                        "event processing wasn't explicitly confirmed"
                    )
                self._processor.confirm_event(result)
            except BaseException:
                self._processor.reject_event(result)
                raise
            return

        await self._call(self._on_control, result)
        if result.kind is EventResultKind.ERROR:
            self._last_error = (
                result.issue.value if result.issue is not None else "log_error"
            )
            if result.issue in {
                EventProtocolIssue.AUTHORIZATION,
                EventProtocolIssue.CURSOR_AHEAD,
                EventProtocolIssue.INVALID_REQUEST,
                EventProtocolIssue.LIVE_DISABLED,
            }:
                raise EventAccessInvalid(self._last_error)
            raise RuntimeError(self._last_error)

    @staticmethod
    async def _call(
        callback: Optional[EventCallback], result: EventProtocolResult
    ) -> Union[None, bool]:
        if callback is None:
            return None
        value = callback(result)
        if inspect.isawaitable(value):
            value = await value
        return value

    async def _close_socket(
        self, code: int = 1000, reason: str = ""
    ) -> None:
        ws = self._ws
        self._ws = None
        if ws is None:
            return
        try:
            await ws.close(code=code, reason=reason)
        except Exception:
            logger.debug("Failed to close event WebSocket cleanly", exc_info=True)

    def _set_state(self, state: EventConnectionState) -> None:
        if self._state is state:
            return
        self._state = state
        if self._on_state_change is not None:
            try:
                self._on_state_change(state)
            except Exception:
                logger.exception("Event stream state callback failed")

    def _backoff_delay(self) -> float:
        exponent = max(self._backoff_attempt - 1, 0)
        minimum = self._config.reconnect_min_delay
        maximum = self._config.reconnect_max_delay
        if minimum >= maximum:
            base = maximum
        else:
            steps_to_cap = max(
                0,
                math.ceil(math.log2(maximum) - math.log2(minimum)),
            )
            base = (
                maximum
                if exponent >= steps_to_cap
                else min(math.ldexp(minimum, exponent), maximum)
            )
        jitter = base * self._config.reconnect_jitter * random.random()
        return min(base + jitter, maximum)

    @staticmethod
    def _connection_close_code(exc: BaseException) -> Optional[int]:
        direct = getattr(exc, "code", None)
        if direct is not None:
            try:
                return int(direct)
            except (TypeError, ValueError):
                pass
        received = getattr(exc, "rcvd", None)
        nested = getattr(received, "code", None)
        if nested is not None:
            try:
                return int(nested)
            except (TypeError, ValueError):
                pass
        return None
