"""Headless V2 transport. Application composition switches in AP-CV2-100.

All entry points and synchronous callbacks run on the owning asyncio loop.
The injected bootstrap service supplies settings/audio policy; the transport
restores desired suppression last. It never invents activation/domain state.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import StrEnum
import random
from urllib.parse import urlsplit

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed, InvalidHandshake, InvalidStatus, InvalidURI

from . import protocol_v2 as p
from .command_tracker import CommandCompletion, CommandTracker, CommandTimeout, TransportLost
from .observability.adapters.client_events import ClientEventEmitter
from .observability.ingress import NULL_INGRESS


DEFAULT_V2_URL = "wss://stt.voice.marcosudau.com/ws/v2"
# Import once per process, shared by all transport objects and reconnects.
CLIENT_RUN_ID = p.new_id()


class V2TransportState(StrEnum):
    CLOSED = "closed"
    CONNECTING = "connecting"
    ACCEPTING = "accepting"
    CONFIGURING = "configuring"
    READY = "ready"
    BACKOFF = "backoff"
    BLOCKED = "blocked"
    STOPPING = "stopping"


@dataclass(frozen=True)
class TransportStatus:
    state: V2TransportState
    generation: int
    reason: str = ""
    retry_delay: float | None = None


@dataclass(frozen=True)
class SessionBinding:
    generation: int
    accepted: p.HelloAccepted = field(repr=False)

    @property
    def session_id(self):
        return self.accepted.sessionId


@dataclass(frozen=True)
class V2TransportConfig:
    url: str = DEFAULT_V2_URL
    client_version: str = "2.0.0-desktop"
    client_commit: str = "unknown"
    manual: bool = True
    wake_word: bool = False
    wake_word_ids: tuple[str, ...] = ()
    suppress_manual: bool = False
    suppress_wake_word: bool = False
    connect_timeout: float = 15
    admission_timeout: float = 30
    bootstrap_timeout: float = 30
    ack_timeout: float = 5
    close_timeout: float = 3
    ping_interval: float = 20
    ping_timeout: float = 20
    backoff_initial: float = .5
    backoff_max: float = 30
    capacity_min: float = 10
    command_retries: int = 1
    max_pending: int = 16

    def __post_init__(self):
        for key in ("connect_timeout", "admission_timeout", "bootstrap_timeout", "ack_timeout",
                    "close_timeout", "ping_interval", "ping_timeout", "backoff_initial", "backoff_max",
                    "capacity_min"):
            value = getattr(self, key)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 < value < float("inf"):
                raise ValueError("invalid transport timeout/backoff")
        if self.backoff_initial > self.backoff_max or self.capacity_min < 10:
            raise ValueError("invalid reconnect bounds")
        if self.command_retries not in (0, 1) or type(self.max_pending) is not int or self.max_pending < 1:
            raise ValueError("invalid command bounds")

    @property
    def endpoint_issue(self) -> str | None:
        try:
            url = urlsplit(self.url)
            if url.scheme not in ("ws", "wss") or not url.hostname or url.username or url.password or url.fragment:
                return "invalid_endpoint"
            if url.path != p.WEBSOCKET_PATH:
                return "legacy_endpoint_requires_migration"
        except ValueError:
            return "invalid_endpoint"
        return None


class _Blocked(RuntimeError):
    pass


class _Refusal(RuntimeError):
    def __init__(self, message: p.HandshakeRejected):
        self.message = message


Bootstrap = Callable[["V2STTSession", SessionBinding], Awaitable[None]]


class V2STTSession:
    """Bounded socket lifecycle with typed, receive-ordered publication.

    A bootstrap is required: absence blocks after admission and sends no PCM
    or user command. The service must complete required configuration via
    bootstrap_command; failed acks must raise. No implicit settings success.
    """

    def __init__(self, config: V2TransportConfig | None = None, *, bootstrap: Bootstrap | None = None,
                 connector=connect, jitter=random.uniform, observability=NULL_INGRESS):
        self.config = config or V2TransportConfig()
        self.bootstrap = bootstrap
        self._connector, self._jitter = connector, jitter
        self._observe = ClientEventEmitter(observability, component="connection")
        self.client_run_id = CLIENT_RUN_ID
        self.generation = 0
        self.binding: SessionBinding | None = None
        self.status = TransportStatus(V2TransportState.CLOSED, 0)
        self.on_status: Callable[[TransportStatus], None] | None = None
        self.on_accepted: Callable[[SessionBinding], None] | None = None
        self.on_message: Callable[[SessionBinding, p.Event | p.Snapshot], None] | None = None
        self.on_completion: Callable[[CommandCompletion], None] | None = None
        self.on_rejected: Callable[[p.HandshakeRejected], None] | None = None
        self.on_lost: Callable[[SessionBinding], None] | None = None
        self._ws = None
        self._tracker: CommandTracker | None = None
        self._runner: asyncio.Task | None = None
        self._receiver: asyncio.Task | None = None
        self._stop = asyncio.Event()
        self._silent_failures = 0
        self._attempt = 0
        self._desired_suppression = (self.config.suppress_manual, self.config.suppress_wake_word)
        self._closing_activation = None

    @property
    def is_ready(self):
        return self.status.state == V2TransportState.READY and self.binding is not None

    @property
    def pending_count(self):
        return self._tracker.pending_count if self._tracker else 0

    def _state(self, state, reason="", delay=None):
        self.status = TransportStatus(state, self.generation, reason, delay)
        self._observe.system("client.v2.transport_state", generation=self.generation,
                             details={"state": str(state), "reason": reason, "retryDelay": delay})
        if self.on_status:
            self.on_status(self.status)

    def _current(self, binding):
        return binding is not None and binding is self.binding and not self._stop.is_set()

    async def run(self):
        if self._runner is not None:
            raise RuntimeError("transport already running")
        self._runner = asyncio.current_task()
        self._stop.clear()
        try:
            issue = self.config.endpoint_issue
            if issue:
                raise _Blocked(issue)
            while not self._stop.is_set():
                delay, reason = None, "network_lost"
                try:
                    await self._connection()
                except _Blocked:
                    raise
                except _Refusal as exc:
                    if exc.message.type == "protocol.incompatible":
                        raise _Blocked("protocol_incompatible") from None
                    if exc.message.payload["reason"] != "session_limit_reached":
                        raise _Blocked("session_configuration_rejected") from None
                    reason, delay = "session_limit_reached", self._delay(capacity=True)
                except InvalidStatus as exc:
                    # Upgrade failures happen before a WebSocket/session exists.
                    # Publish only the status code, never response bodies/headers.
                    code = exc.response.status_code
                    reason = f"http_upgrade_{code}"
                    if code == 429:
                        delay = self._delay(capacity=True)
                    elif code != 408 and not 500 <= code < 600:
                        raise _Blocked(reason) from None
                except InvalidHandshake:
                    raise _Blocked("invalid_websocket_handshake") from None
                except InvalidURI:
                    raise _Blocked("invalid_endpoint") from None
                except ConnectionClosed as exc:
                    code = exc.rcvd.code if exc.rcvd is not None else None
                    if code in (4400, 4406, 4409):
                        raise _Blocked(f"close_{code}") from None
                    if code == 4408:
                        self._silent_failures += 1
                        if self._silent_failures > 1:
                            raise _Blocked("repeated_hello_timeout") from None
                        reason = "hello_timeout"
                    elif code == 1013:
                        reason, delay = "capacity_close", self._delay(capacity=True)
                    elif code == 1011:
                        reason = "server_restart"
                except p.ProtocolError:
                    raise _Blocked("invalid_server_protocol") from None
                except (OSError, TimeoutError, TransportLost):
                    pass
                finally:
                    await self._cleanup()
                if not self._stop.is_set():
                    delay = self._delay() if delay is None else delay
                    self._state(V2TransportState.BACKOFF, reason, delay)
                    try:
                        await asyncio.wait_for(self._stop.wait(), delay)
                    except TimeoutError:
                        pass
        except _Blocked as exc:
            self._state(V2TransportState.BLOCKED, str(exc))
        finally:
            await self._cleanup()
            if self.status.state != V2TransportState.BLOCKED:
                self._state(V2TransportState.CLOSED)
            self._runner = None

    def _delay(self, *, capacity=False):
        base = min(self.config.backoff_max, self.config.backoff_initial * 2 ** min(self._attempt, 16))
        self._attempt = min(self._attempt + 1, 16)
        delay = min(self.config.backoff_max, base * self._jitter(.7, 1.3))
        return max(self.config.capacity_min, delay) if capacity else delay

    async def _connection(self):
        self.generation += 1
        self._state(V2TransportState.CONNECTING)
        c = self.config
        self._ws = await asyncio.wait_for(self._connector(
            c.url, open_timeout=c.connect_timeout, close_timeout=c.close_timeout,
            ping_interval=c.ping_interval, ping_timeout=c.ping_timeout,
            max_size=4 * 1024 * 1024, max_queue=16), c.connect_timeout)
        self._state(V2TransportState.ACCEPTING)
        hello = p.build_hello(clientVersion=c.client_version, clientCommit=c.client_commit,
                              clientRunId=self.client_run_id, manual=c.manual, wakeWord=c.wake_word,
                              wakeWordIds=list(c.wake_word_ids), suppressManual=True, suppressWakeWord=True)
        await asyncio.wait_for(self._ws.send(p.encode_client_message(hello)), c.ack_timeout)
        accepted = p.decode_server_message(await asyncio.wait_for(self._ws.recv(), c.admission_timeout))
        if isinstance(accepted, p.HandshakeRejected):
            if self.on_rejected:
                self.on_rejected(accepted)
            raise _Refusal(accepted)
        if not isinstance(accepted, p.HelloAccepted):
            raise p.ProtocolError("expected hello.accepted")
        binding = self.binding = SessionBinding(self.generation, accepted)
        self._tracker = CommandTracker(binding.session_id, binding.generation,
                                       ack_timeout=c.ack_timeout, retries=c.command_retries,
                                       max_pending=c.max_pending, on_completion=self._completion)
        self._tracker.observe(accepted.snapshot.stateVersion, accepted.snapshot.settingsRevision)
        self._state(V2TransportState.CONFIGURING)
        if self.on_accepted:
            self.on_accepted(binding)
        self._receiver = asyncio.create_task(self._receive(binding, self._ws), name="v2-receive")
        if self.bootstrap is None:
            raise _Blocked("bootstrap_service_required")
        configuring = asyncio.create_task(self._configure(binding), name="v2-bootstrap")
        try:
            done, _ = await asyncio.wait((configuring, self._receiver), return_when=asyncio.FIRST_COMPLETED)
            if self._receiver in done:
                await self._receiver
            await configuring
            if not self._current(binding):
                raise TransportLost("transport_lost")
            self._attempt = 0
            # Admission alone isn't success: only a completed bootstrap separates
            # hello-timeout episodes and grants a fresh single 4408 retry.
            self._silent_failures = 0
            self._state(V2TransportState.READY)
            await self._receiver
        finally:
            configuring.cancel()
            await asyncio.gather(configuring, return_exceptions=True)

    async def _configure(self, binding):
        try:
            await asyncio.wait_for(self.bootstrap(self, binding), self.config.bootstrap_timeout)
            if not self._current(binding):
                raise TransportLost("transport_lost")
            completion = await self._command(binding, p.CommandType.SUPPRESSION,
                                             manual=self._desired_suppression[0], wakeWord=self._desired_suppression[1])
            if not completion.ack.accepted:
                raise _Blocked("suppression_bootstrap_rejected")
        except (CommandTimeout, TimeoutError):
            raise _Blocked("bootstrap_outcome_unknown") from None
        except (p.ProtocolError, ValueError):
            raise _Blocked("bootstrap_configuration_error") from None

    async def _receive(self, binding, ws):
        while self._current(binding):
            frame = await ws.recv()
            if not self._current(binding):
                return
            if not isinstance(frame, str):
                raise p.ProtocolError("server binary frame forbidden")
            self.dispatch(p.decode_server_message(frame), binding)

    def dispatch(self, message, binding: SessionBinding) -> bool:
        """Generationguard for socket/test adapters. Unknown unrelated frames ignored."""
        if not self._current(binding) or message is None:
            return False
        if isinstance(message, p.CommandAck):
            return self._tracker.resolve(message, binding.generation)
        if isinstance(message, (p.Event, p.Snapshot)):
            if message.sessionId != binding.session_id:
                return False
            self._tracker.observe(message.stateVersion, message.payload.get("settingsRevision"))
            if self.on_message:
                self.on_message(binding, message)
            return True
        raise p.ProtocolError("unexpected handshake after admission")

    def _completion(self, completion):
        if completion.ack.result == p.AckResult.CLOSING_INPUT:
            self._closing_activation = completion.command.payload.get("activationId")
        self._observe.audit("client.v2.command_completed", generation=completion.generation,
                            session_id=completion.ack.sessionId, command_id=completion.ack.commandId,
                            details={"result": str(completion.ack.result), "projectable": completion.projectable})
        if self.on_completion:
            self.on_completion(completion)

    async def _command(self, binding, kind, **fields):
        if not self._current(binding):
            raise TransportLost("transport_lost")
        tracker, ws = self._tracker, self._ws
        if any(key in fields for key in ("commandId", "sessionId", "protocolVersion", "type")):
            raise p.ProtocolError("command envelope is owned by transport")
        if (kind == p.CommandType.ACTIVATION and fields.get("action") == "refresh"
                and fields.get("activationId") == self._closing_activation):
            raise TransportLost("refresh is blocked for closing input")
        command = p.build_command(kind, binding.session_id, **fields)
        return await tracker.request(command, ws.send)

    async def bootstrap_command(self, binding, kind, **fields):
        if self.status.state != V2TransportState.CONFIGURING or kind not in (
                p.CommandType.AUDIO_AVAILABILITY, p.CommandType.SETTINGS_PATCH, p.CommandType.SNAPSHOT_REQUEST):
            raise TransportLost("command is not permitted during bootstrap")
        completion = await self._command(binding, kind, **fields)
        if not completion.ack.accepted:
            raise _Blocked("configuration_command_rejected")
        return completion

    async def request(self, kind, *, binding: SessionBinding | None = None, **fields):
        current = self.binding if binding is None else binding
        if not self.is_ready or not self._current(current):
            raise TransportLost("transport is not ready for commands")
        # Callers cannot supply IDs or session envelopes: every logical command
        # gets a new UUID. Retries exist only inside this request's tracker.
        if any(key in fields for key in ("commandId", "sessionId", "protocolVersion", "type")):
            raise p.ProtocolError("command envelope is owned by transport")
        try:
            completion = await self._command(current, kind, **fields)
            if kind == p.CommandType.SUPPRESSION and completion.ack.accepted:
                self._desired_suppression = (fields["manual"], fields["wakeWord"])
            return completion
        except (CommandTimeout, TimeoutError, asyncio.CancelledError, OSError, ConnectionClosed):
            # Outcome is uncertain: invalidate synchronously before queued callers
            # can send another mutation. Reconnect never resends the old command.
            if self._tracker:
                self._tracker.close()
            self._state(V2TransportState.BACKOFF, "command_outcome_unknown")
            await self._close_socket()
            raise

    async def send_audio(self, pcm: bytes, sample_rate: int, channels: int = 1,
                         frames: int | None = None, *, binding: SessionBinding | None = None) -> bool:
        current = self.binding if binding is None else binding
        if not self.is_ready or not self._current(current):
            return False
        # No audio queue here; AP040 owns the bounded capture/send adapter.
        wire = p.encode_audio_packet(pcm, sample_rate, channels, frames)
        try:
            await asyncio.wait_for(self._ws.send(wire), self.config.ack_timeout)
        except (TimeoutError, asyncio.CancelledError, OSError, ConnectionClosed):
            if self._tracker:
                self._tracker.close()
            self._state(V2TransportState.BACKOFF, "audio_send_failed")
            await self._close_socket()
            raise
        return self._current(current)

    async def _close_socket(self):
        ws = self._ws
        if ws is not None:
            try:
                await asyncio.wait_for(ws.close(), self.config.close_timeout)
            except (TimeoutError, OSError, ConnectionClosed):
                transport = getattr(ws, "transport", None)
                if transport is not None:
                    transport.abort()

    async def _cleanup(self):
        binding, self.binding = self.binding, None
        if self._tracker:
            self._tracker.close()
        if self._receiver:
            self._receiver.cancel()
            await asyncio.gather(self._receiver, return_exceptions=True)
            self._receiver = None
        await self._close_socket()
        self._ws = None
        self._tracker = None
        self._closing_activation = None
        if binding and self.on_lost:
            self.on_lost(binding)

    async def stop(self):
        self._stop.set()
        runner = self._runner
        if runner and runner is not asyncio.current_task():
            if self.status.state != V2TransportState.STOPPING:
                self._state(V2TransportState.STOPPING)
                runner.cancel()
            await asyncio.shield(asyncio.gather(runner, return_exceptions=True))
