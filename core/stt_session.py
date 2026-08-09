"""
WebSocket session management for the RealtimeSTT server protocol.

Implements:
- Connection lifecycle: connect → hello → ready → start → streaming
- Event reducer following the pattern from the server docs (05-client-zustandsmodell.md)
- Two separate state machines: transport + session/recorder
- Automatic reconnection with exponential backoff + jitter
- Ping/pong health monitoring
- Callback-based interface for upper layers

This module has ZERO UI dependencies and can be tested headless.
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import struct
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional

from websockets.asyncio.client import ClientConnection, connect as ws_connect
from websockets.exceptions import ConnectionClosed

from core.config import SessionConfig

logger = logging.getLogger("connection")


# ---------------------------------------------------------------------------
# Transport state machine
# ---------------------------------------------------------------------------

class TransportState(Enum):
    """WebSocket connection lifecycle states."""
    DISCONNECTED = auto()
    CONNECTING = auto()
    ADMITTED = auto()   # hello received
    READY = auto()      # ready(ok=true) received
    ERROR = auto()      # ready(ok=false) or fatal error


# ---------------------------------------------------------------------------
# Session / recorder state (as reported by the server's status events)
# ---------------------------------------------------------------------------

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
            logger.debug("Unknown server state: %s", value)
            return cls.UNKNOWN


# ---------------------------------------------------------------------------
# Transcript segment model
# ---------------------------------------------------------------------------

@dataclass
class TranscriptSegment:
    """A single speech segment with realtime updates and final text."""
    segment_id: int
    text: str = ""
    is_final: bool = False
    last_sequence: Optional[int] = None
    raw_text: Optional[str] = None
    stable_text: Optional[str] = None
    unstable_text: Optional[str] = None
    display_text: Optional[str] = None
    updated_at: Optional[float] = None


# ---------------------------------------------------------------------------
# Client state (the full reducer state)
# ---------------------------------------------------------------------------

@dataclass
class ClientState:
    """Complete client-side state, updated by the event reducer."""
    transport: TransportState = TransportState.DISCONNECTED
    generation: int = 0
    session_id: Optional[str] = None
    ready_ok: bool = False
    server_status: SessionState = SessionState.IDLE
    streaming_requested: bool = False
    settings: Optional[dict] = None
    limits: Optional[dict] = None
    models: Optional[dict] = None
    segments: dict[int, TranscriptSegment] = field(default_factory=dict)
    segment_order: list[int] = field(default_factory=list)
    last_warning: Optional[dict] = None
    last_error: Optional[dict] = None
    ping_started_at: Optional[float] = None
    round_trip_ms: Optional[float] = None
    # Counters from status events
    active_sessions: int = 0
    active_speakers: int = 0

    def fresh_session(self) -> ClientState:
        """Return a state with session-specific fields reset."""
        return ClientState(
            transport=self.transport,
            generation=self.generation,
            settings=self.settings,
            limits=self.limits,
        )


# ---------------------------------------------------------------------------
# Callback type hints
# ---------------------------------------------------------------------------

EventCallback = Callable[[str, dict], None]  # (event_type, event_data)
StateCallback = Callable[[ClientState], None]
TextCallback = Callable[[int, str, bool], None]  # (segment_id, text, is_final)


class _AdmissionRejectedError(RuntimeError):
    """Admission failed and the server will close with 1013."""


class _ServerUnavailableError(RuntimeError):
    """The server/engine is temporarily unable to serve the session."""


class _RecorderUnavailableError(RuntimeError):
    """Repeated recorder failures require a fresh session."""


class SessionConfigurationError(RuntimeError):
    """The requested session configuration cannot be activated safely."""


# ---------------------------------------------------------------------------
# Audio packet encoder
# ---------------------------------------------------------------------------

def encode_audio_packet(
    pcm_data: bytes,
    sample_rate: int,
    channels: int = 1,
    frames: Optional[int] = None,
) -> bytes:
    """
    Encode a binary audio packet per the server protocol.

    Layout: 4-byte LE metadata length + UTF-8 JSON metadata + PCM s16le data.
    """
    metadata = {
        "sampleRate": sample_rate,
        "channels": channels,
        "format": "pcm_s16le",
    }
    if frames is not None:
        metadata["frames"] = frames

    meta_bytes = json.dumps(metadata).encode("utf-8")
    length_prefix = struct.pack("<I", len(meta_bytes))
    return length_prefix + meta_bytes + pcm_data


# ---------------------------------------------------------------------------
# Event reducer (pure function)
# ---------------------------------------------------------------------------

def reduce(state: ClientState, event: dict) -> ClientState:
    """
    Apply a server event to the client state.

    This is a pure function following the reducer pattern from
    05-client-zustandsmodell.md. It does NOT mutate the input state.
    """
    event_type = event.get("type", "")

    if event_type == "hello":
        new_state = state.fresh_session()
        new_state.transport = TransportState.ADMITTED
        new_state.session_id = event.get("sessionId")
        new_state.settings = event.get("settings")
        new_state.limits = event.get("limits")
        return new_state

    elif event_type == "ready":
        ok = event.get("ok", False)
        return ClientState(
            transport=TransportState.READY if ok else TransportState.ERROR,
            generation=state.generation,
            session_id=state.session_id,
            ready_ok=ok,
            streaming_requested=state.streaming_requested,
            settings=event.get("settings", state.settings),
            limits=event.get("limits", state.limits),
            models=event.get("models", state.models),
            segments=state.segments,
            segment_order=state.segment_order,
        )

    elif event_type == "status":
        server_state = SessionState.from_server(event.get("state", "unknown"))
        return ClientState(
            transport=state.transport,
            generation=state.generation,
            session_id=state.session_id,
            ready_ok=state.ready_ok,
            server_status=server_state,
            streaming_requested=state.streaming_requested,
            settings=state.settings,
            limits=state.limits,
            models=state.models,
            segments=state.segments,
            segment_order=state.segment_order,
            last_warning=state.last_warning,
            last_error=state.last_error,
            active_sessions=event.get("activeSessions", state.active_sessions),
            active_speakers=event.get("activeSpeakers", state.active_speakers),
        )

    elif event_type == "realtime":
        return _upsert_realtime(state, event)

    elif event_type == "final":
        return _upsert_final(state, event)

    elif event_type == "clear":
        return ClientState(
            transport=state.transport,
            generation=state.generation,
            session_id=state.session_id,
            ready_ok=state.ready_ok,
            server_status=state.server_status,
            streaming_requested=state.streaming_requested,
            settings=state.settings,
            limits=state.limits,
            models=state.models,
            segments={},
            segment_order=[],
            active_sessions=state.active_sessions,
            active_speakers=state.active_speakers,
        )

    elif event_type == "pong":
        rtt = None
        if state.ping_started_at is not None:
            rtt = (time.monotonic() - state.ping_started_at) * 1000
        return ClientState(
            transport=state.transport,
            generation=state.generation,
            session_id=state.session_id,
            ready_ok=state.ready_ok,
            server_status=state.server_status,
            streaming_requested=state.streaming_requested,
            settings=state.settings,
            limits=state.limits,
            models=state.models,
            segments=state.segments,
            segment_order=state.segment_order,
            ping_started_at=None,
            round_trip_ms=rtt,
            active_sessions=state.active_sessions,
            active_speakers=state.active_speakers,
        )

    elif event_type == "warning":
        return ClientState(
            transport=state.transport,
            generation=state.generation,
            session_id=state.session_id,
            ready_ok=state.ready_ok,
            server_status=state.server_status,
            streaming_requested=state.streaming_requested,
            settings=state.settings,
            limits=state.limits,
            models=state.models,
            segments=state.segments,
            segment_order=state.segment_order,
            last_warning=event,
            last_error=state.last_error,
            active_sessions=state.active_sessions,
            active_speakers=state.active_speakers,
        )

    elif event_type == "error":
        return _classify_error(state, event)

    elif event_type == "metrics":
        # Metrics are observational, don't change core state
        return state

    elif event_type == "timeline":
        # Timeline events are for diagnostics, not for the transcript reducer
        return state

    else:
        # Forward compatibility: unknown events are ignored
        logger.debug("Ignoring unknown event type: %s", event_type)
        return state


def _upsert_realtime(state: ClientState, event: dict) -> ClientState:
    """Update or insert a realtime transcript segment."""
    seg_id = event.get("segmentId")
    if seg_id is None:
        return state

    previous = state.segments.get(seg_id)

    # Don't overwrite a finalized segment
    if previous is not None and previous.is_final:
        return state

    # Sequence ordering guard
    seq = event.get("sequence")
    if (
        seq is not None
        and previous is not None
        and previous.last_sequence is not None
        and seq < previous.last_sequence
    ):
        return state

    display = event.get("displayText") or event.get("text", "")

    segment = TranscriptSegment(
        segment_id=seg_id,
        text=display,
        is_final=False,
        last_sequence=seq if seq is not None else (previous.last_sequence if previous else None),
        raw_text=event.get("rawText"),
        stable_text=event.get("committedStableText") or event.get("stableText"),
        unstable_text=event.get("visualUnstableText") or event.get("unstableText"),
        display_text=display,
        updated_at=event.get("timestamp"),
    )

    new_segments = dict(state.segments)
    new_segments[seg_id] = segment

    new_order = list(state.segment_order)
    if seg_id not in new_order:
        new_order.append(seg_id)

    return ClientState(
        transport=state.transport,
        generation=state.generation,
        session_id=state.session_id,
        ready_ok=state.ready_ok,
        server_status=state.server_status,
        streaming_requested=state.streaming_requested,
        settings=state.settings,
        limits=state.limits,
        models=state.models,
        segments=new_segments,
        segment_order=new_order,
        last_warning=state.last_warning,
        last_error=state.last_error,
        active_sessions=state.active_sessions,
        active_speakers=state.active_speakers,
    )


def _upsert_final(state: ClientState, event: dict) -> ClientState:
    """Finalize a transcript segment."""
    seg_id = event.get("segmentId")
    if seg_id is None:
        return state

    text = event.get("text", "")
    previous = state.segments.get(seg_id)

    segment = TranscriptSegment(
        segment_id=seg_id,
        text=text,
        is_final=True,
        last_sequence=previous.last_sequence if previous else None,
        updated_at=event.get("timestamp"),
    )

    new_segments = dict(state.segments)
    new_segments[seg_id] = segment

    new_order = list(state.segment_order)
    if seg_id not in new_order:
        new_order.append(seg_id)

    return ClientState(
        transport=state.transport,
        generation=state.generation,
        session_id=state.session_id,
        ready_ok=state.ready_ok,
        server_status=state.server_status,
        streaming_requested=state.streaming_requested,
        settings=state.settings,
        limits=state.limits,
        models=state.models,
        segments=new_segments,
        segment_order=new_order,
        last_warning=state.last_warning,
        last_error=state.last_error,
        active_sessions=state.active_sessions,
        active_speakers=state.active_speakers,
    )


def _classify_error(state: ClientState, event: dict) -> ClientState:
    """Classify error by 'where' field and update state accordingly."""
    where = event.get("where", "")

    new_transport = state.transport
    if where == "admission":
        new_transport = TransportState.ERROR
    elif where in ("main_engine", "realtime_engine"):
        new_transport = TransportState.ERROR

    return ClientState(
        transport=new_transport,
        generation=state.generation,
        session_id=state.session_id,
        ready_ok=state.ready_ok,
        server_status=state.server_status,
        streaming_requested=state.streaming_requested,
        settings=state.settings,
        limits=state.limits,
        models=state.models,
        segments=state.segments,
        segment_order=state.segment_order,
        last_warning=state.last_warning,
        last_error=event,
        active_sessions=state.active_sessions,
        active_speakers=state.active_speakers,
    )


# ---------------------------------------------------------------------------
# STTSession – the async WebSocket client
# ---------------------------------------------------------------------------

class STTSession:
    """
    Manages the WebSocket connection to the RealtimeSTT server.

    Usage:
        session = STTSession(config.server)
        session.on_state_change = my_callback
        session.on_text = my_text_callback
        await session.run()  # blocks, handles reconnection internally
    """

    def __init__(
        self,
        server_config,
        session_config: Optional[SessionConfig] = None,
        *,
        require_session_contract: bool = False,
    ):
        self._config = server_config
        self._session_config = session_config or SessionConfig()
        self._session_config.validate()
        self._require_session_contract = require_session_contract
        self._state = ClientState()
        self._ws: Optional[ClientConnection] = None
        self._running = False
        self._streaming = False
        self._backoff_attempt = 0
        self._generation = 0
        self._ping_pending = False
        self._consecutive_misses = 0
        self._first_pong_received = False
        self._is_server_busy = False
        self._backoff_sleep_task: Optional[asyncio.Task] = None
        self._next_retry_delay: Optional[float] = None
        self._last_failure_reason = ""
        self._requested_disconnect_reason: Optional[str] = None
        self._ping_generation: Optional[int] = None
        self._recorder_error_count = 0
        self._configuration_blocked = False
        self._configuration_changed = asyncio.Event()
        self._effective_session_config: Optional[dict] = None
        self._session_capabilities: Optional[dict] = None

        # Task references for cleanup
        self._ping_task: Optional[asyncio.Task] = None
        self._recv_task: Optional[asyncio.Task] = None

        # Callbacks (set by upper layers)
        self.on_state_change: Optional[StateCallback] = None
        self.on_text: Optional[TextCallback] = None
        self.on_event: Optional[EventCallback] = None
        self.on_transport_change: Optional[Callable[[TransportState], None]] = None

    @property
    def state(self) -> ClientState:
        return self._state

    @property
    def generation(self) -> int:
        return self._generation

    @property
    def reconnect_attempt(self) -> int:
        return self._backoff_attempt

    @property
    def next_retry_delay(self) -> Optional[float]:
        return self._next_retry_delay

    @property
    def last_failure_reason(self) -> str:
        return self._last_failure_reason

    @property
    def is_server_busy(self) -> bool:
        return self._is_server_busy

    @property
    def effective_session_config(self) -> Optional[dict]:
        return (
            dict(self._effective_session_config)
            if self._effective_session_config is not None
            else None
        )

    @property
    def session_capabilities(self) -> Optional[dict]:
        return (
            dict(self._session_capabilities)
            if self._session_capabilities is not None
            else None
        )

    @property
    def configuration_blocked(self) -> bool:
        return self._configuration_blocked

    @property
    def is_connected(self) -> bool:
        return (
            self._state.transport
            in (TransportState.ADMITTED, TransportState.READY)
            and self._ws_is_open()
        )

    @property
    def is_ready(self) -> bool:
        return (
            self._state.transport == TransportState.READY
            and self._state.ready_ok
            and self._ws_is_open()
        )

    @property
    def is_streaming(self) -> bool:
        return self._streaming

    def set_streaming(self, streaming: bool) -> None:
        """Set audio streaming active state (called when confirmed by server status)."""
        self._streaming = streaming
        self._state.streaming_requested = streaming

    # -------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------

    async def run(self) -> None:
        """
        Main loop: connect, process events, reconnect on failure.
        Runs until stop() is called.
        """
        self._running = True
        logger.info("STTSession starting, target: %s", self._config.url)

        while self._running:
            if self._configuration_blocked:
                logger.warning(
                    "Reconnect paused until the invalid session configuration changes."
                )
                self._update_transport(TransportState.ERROR)
                await self._configuration_changed.wait()
                self._configuration_changed.clear()
                if not self._running:
                    break
            try:
                await self._connect_and_run()
            except asyncio.CancelledError:
                logger.info("STTSession cancelled.")
                break
            except Exception:
                logger.exception("Connection loop error.")

            if not self._running:
                break
            if self._configuration_blocked:
                continue

            # Reconnect with backoff
            delay = self._backoff_delay()
            self._next_retry_delay = delay
            logger.info("Reconnecting in %.1fs (attempt %d, gen %d)...", delay, self._backoff_attempt, self._generation)
            self._update_transport(TransportState.DISCONNECTED)
            try:
                self._backoff_sleep_task = asyncio.create_task(asyncio.sleep(delay))
                await self._backoff_sleep_task
            except asyncio.CancelledError:
                break
            finally:
                self._backoff_sleep_task = None
                self._next_retry_delay = None

        logger.info("STTSession stopped.")

    async def stop(self) -> None:
        """Gracefully stop the session."""
        self._running = False
        self._streaming = False
        self._next_retry_delay = None
        self._configuration_changed.set()
        cancelled_tasks = []
        current_task = asyncio.current_task()
        if self._backoff_sleep_task and not self._backoff_sleep_task.done():
            self._backoff_sleep_task.cancel()
            if self._backoff_sleep_task is not current_task:
                cancelled_tasks.append(self._backoff_sleep_task)
        if self._ping_task and not self._ping_task.done():
            self._ping_task.cancel()
            if self._ping_task is not current_task:
                cancelled_tasks.append(self._ping_task)
        if cancelled_tasks:
            await asyncio.gather(*cancelled_tasks, return_exceptions=True)
        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
        self._update_transport(TransportState.DISCONNECTED)

    async def invalidate_connection(self, reason: str = "connection_recycle") -> None:
        """Recycle only the current WebSocket while keeping the reconnect loop alive."""
        self._streaming = False
        self._state.streaming_requested = False
        self._requested_disconnect_reason = reason
        ws = self._ws
        if ws is not None and self._ws_is_open():
            try:
                await ws.close(1011, reason[:120])
            except Exception:
                logger.debug("Failed to close invalidated connection cleanly.", exc_info=True)

    async def reconfigure(
        self,
        session_config: SessionConfig,
        server_config=None,
    ) -> None:
        """Apply a validated session profile and recycle the current socket."""
        session_config.validate()
        if server_config is not None:
            server_config.validate()
            self._config = server_config
        self._session_config = session_config
        self._configuration_blocked = False
        self._effective_session_config = None
        self._session_capabilities = None
        self._configuration_changed.set()
        await self.invalidate_connection("session_configuration_changed")

    # -------------------------------------------------------------------
    # Commands
    # -------------------------------------------------------------------

    async def send_start(self) -> None:
        """Send the start command to begin audio streaming."""
        if not self.is_ready:
            raise ConnectionError(
                f"Cannot start: transport is not READY (current: {self._state.transport.name})"
            )
        await self._send_json({"type": "start"})
        self._state.streaming_requested = True
        logger.info("Sent start command.")

    async def send_stop(self) -> None:
        """Send the stop command. Final events may still arrive after this."""
        if self._ws_is_open():
            await self._send_json({"type": "stop"})
            self._streaming = False
            self._state.streaming_requested = False
            logger.info("Sent stop command.")

    async def send_clear(self) -> None:
        """Send clear to reset server-side session state."""
        if self._ws_is_open():
            await self._send_json({"type": "clear"})
            logger.info("Sent clear command.")

    async def send_audio(self, pcm_data: bytes, sample_rate: int, channels: int = 1, frames: Optional[int] = None) -> None:
        """Send a binary audio packet to the server."""
        if not self._streaming or not self._ws_is_open():
            return
        packet = encode_audio_packet(pcm_data, sample_rate, channels, frames)
        try:
            await self._ws.send(packet)
        except ConnectionClosed:
            logger.warning("Connection closed while sending audio.")
            self._streaming = False

    async def send_ping(self) -> bool:
        """Send one application-level ping if none is already outstanding."""
        if self._ping_pending:
            return False
        if not self._ws_is_open():
            raise ConnectionError("Cannot ping: WebSocket is not open")

        self._ping_pending = True
        self._ping_generation = self._generation
        self._state.ping_started_at = time.monotonic()
        try:
            await self._send_json({"type": "ping"})
        except Exception:
            self._ping_pending = False
            self._ping_generation = None
            self._state.ping_started_at = None
            raise
        return True

    def _ws_is_open(self) -> bool:
        """Check if the WebSocket connection is open (v16 compatible)."""
        if self._ws is None:
            return False
        try:
            from websockets.protocol import State
            return self._ws.state is State.OPEN
        except (AttributeError, ImportError):
            # Fallback for API variations
            return self._ws is not None

    # -------------------------------------------------------------------
    # Internal: connection
    # -------------------------------------------------------------------

    async def _connect_and_run(self) -> None:
        """Single connection attempt: connect, handshake, process messages."""
        self._generation += 1
        self._state = ClientState(
            transport=self._state.transport,
            generation=self._generation,
            settings=self._state.settings,
            limits=self._state.limits,
        )
        self._ping_pending = False
        self._ping_generation = None
        self._consecutive_misses = 0
        self._first_pong_received = False
        self._recorder_error_count = 0
        self._requested_disconnect_reason = None
        self._update_transport(TransportState.CONNECTING)
        self._streaming = False

        target_url = self._session_config.build_url(self._config.url)
        try:
            self._ws = await asyncio.wait_for(
                ws_connect(
                    target_url,
                    max_size=2**20,  # 1 MB max incoming message
                    ping_interval=None,  # we handle pings at app level
                    ping_timeout=None,
                    close_timeout=5,
                    proxy=None,  # v16: disable automatic proxy detection
                ),
                timeout=self._config.hello_timeout + 5,
            )
        except asyncio.TimeoutError:
            logger.error("Connection timeout to %s", target_url)
            self._record_failure("network_timeout")
            return
        except Exception as e:
            logger.error("Connection failed: %s", e)
            self._record_failure("network_unavailable")
            return

        logger.info("WebSocket connected to %s (gen %d)", target_url, self._generation)

        try:
            # Wait for hello
            await self._wait_for_hello()
            # Wait for ready
            await self._wait_for_ready()

            # Note: Backoff is NOT reset here! Backoff resets on first valid pong.

            # Start ping loop
            self._ping_task = asyncio.create_task(self._ping_loop())

            # Process messages until disconnect
            await self._message_loop()
            if self._running:
                self._record_failure(
                    self._requested_disconnect_reason or "connection_closed"
                )

        except asyncio.TimeoutError as e:
            logger.error("Handshake timeout: %s", e)
            self._record_failure("handshake_timeout")
        except _AdmissionRejectedError as e:
            logger.warning("Session admission rejected: %s", e)
            self._record_failure("server_busy", server_busy=True)
        except _ServerUnavailableError as e:
            logger.warning("Server unavailable: %s", e)
            self._record_failure("server_unavailable")
        except _RecorderUnavailableError as e:
            logger.warning("Recorder unavailable: %s", e)
            self._record_failure("recorder_unavailable")
        except SessionConfigurationError as e:
            logger.error("Session configuration rejected: %s", e)
            self._configuration_blocked = True
            self._record_failure("session_configuration_error")
        except ConnectionClosed as e:
            code = self._connection_close_code(e)
            logger.warning("Connection closed: code=%s reason=%s", code, getattr(e, 'reason', "") if hasattr(e, 'reason') else "")
            reason = self._requested_disconnect_reason or "connection_closed"
            self._record_failure(
                "server_busy" if code == 1013 else reason,
                server_busy=(code == 1013),
            )
        except Exception:
            logger.exception("Error during session.")
            self._record_failure("session_error")
        finally:
            if self._ping_task and not self._ping_task.done():
                self._ping_task.cancel()
                try:
                    await self._ping_task
                except asyncio.CancelledError:
                    pass
            if self._ws:
                try:
                    await self._ws.close()
                except Exception:
                    pass
                self._ws = None
            self._streaming = False
            self._ping_pending = False
            self._ping_generation = None
            self._state.ping_started_at = None

    async def _wait_for_hello(self) -> None:
        """Wait for the hello event after connection."""
        msg = await asyncio.wait_for(
            self._ws.recv(),
            timeout=self._config.hello_timeout,
        )
        event = json.loads(msg)
        if event.get("type") == "error":
            self._apply_event(event)
            if event.get("where") == "session_config":
                raise SessionConfigurationError(
                    event.get("message") or "session configuration rejected"
                )
            if event.get("where") == "admission":
                raise _AdmissionRejectedError(event.get("message") or "admission rejected")
            raise ValueError(
                f"Error before hello: {event.get('where')}: {event.get('message')}"
            )
        if event.get("type") != "hello":
            logger.error("Expected hello, got: %s", event.get("type"))
            raise ValueError(f"Expected hello event, got {event.get('type')}")

        self._apply_event(event)
        self._verify_session_contract(event)
        logger.info(
            "Session admitted: id=%s (gen %d)",
            self._state.session_id,
            self._generation,
        )

    async def _wait_for_ready(self) -> None:
        """Wait for the ready event. May arrive directly or as broadcast."""
        deadline = time.monotonic() + self._config.ready_timeout

        while time.monotonic() < deadline:
            remaining = deadline - time.monotonic()
            try:
                msg = await asyncio.wait_for(self._ws.recv(), timeout=remaining)
            except asyncio.TimeoutError:
                raise asyncio.TimeoutError("Timed out waiting for ready event")

            event = json.loads(msg)
            self._apply_event(event)
            if event.get("type") in ("hello", "ready"):
                self._verify_session_contract(event)

            if event.get("type") == "ready":
                if event.get("ok"):
                    logger.info("Server ready (gen %d).", self._generation)
                    return
                else:
                    logger.error("Server reported ready with ok=false")
                    raise _ServerUnavailableError("Server not ready (ok=false)")

            if event.get("type") == "error":
                where = event.get("where", "")
                if where == "admission":
                    raise _AdmissionRejectedError(
                        f"Admission error: {event.get('message')}"
                    )
                if where in ("main_engine", "realtime_engine"):
                    raise _ServerUnavailableError(
                        event.get("message") or f"{where} unavailable"
                    )
                if where == "session_config":
                    raise SessionConfigurationError(
                        event.get("message") or "session configuration rejected"
                    )
                logger.warning(
                    "Error during startup: where=%s msg=%s",
                    where, event.get("message")
                )

    async def _message_loop(self) -> None:
        """Process incoming messages until disconnect."""
        async for message in self._ws:
            if isinstance(message, str):
                try:
                    event = json.loads(message)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON from server: %s", message[:200])
                    continue
                self._apply_event(event)
                if event.get("type") == "error":
                    where = event.get("where", "")
                    if where == "session_config":
                        raise SessionConfigurationError(
                            event.get("message")
                            or "session configuration rejected"
                        )
                    if where in ("main_engine", "realtime_engine"):
                        raise _ServerUnavailableError(
                            event.get("message") or f"{where} unavailable"
                        )
                    if where == "recorder":
                        self._recorder_error_count += 1
                        if self._recorder_error_count >= 2:
                            raise _RecorderUnavailableError(
                                event.get("message") or "repeated recorder failure"
                            )
            else:
                logger.debug("Ignoring binary frame from server (%d bytes)", len(message))

    def _verify_session_contract(self, event: dict) -> None:
        """Record and verify the authoritative effective handshake contract."""
        session_config = event.get("sessionConfig")
        if session_config is None:
            if not self._require_session_contract:
                return
            raise SessionConfigurationError(
                f"{event.get('type')} omitted required sessionConfig"
            )
        if not isinstance(session_config, dict):
            raise SessionConfigurationError("sessionConfig must be an object")
        effective = session_config.get("effectiveWakeWordEnabled")
        expected = self._session_config.wake_word_enabled
        if not isinstance(effective, bool) or effective is not expected:
            raise SessionConfigurationError(
                "server effectiveWakeWordEnabled contradicts requested mode "
                f"(expected {expected!r}, got {effective!r})"
            )
        warnings = session_config.get("warnings") or []
        fallbacks = session_config.get("fallbacks") or []
        ignored = session_config.get("ignoredFields") or []
        if warnings:
            logger.warning("Session configuration warnings: %s", warnings)
        if fallbacks:
            logger.warning("Session configuration fallbacks: %s", fallbacks)
        if ignored:
            logger.info("Ignored session configuration fields: %s", ignored)
        self._effective_session_config = dict(session_config)
        capabilities = event.get("sessionCapabilities")
        if isinstance(capabilities, dict):
            self._session_capabilities = dict(capabilities)

    # -------------------------------------------------------------------
    # Internal: event processing
    # -------------------------------------------------------------------

    def _apply_event(self, event: dict) -> None:
        """Apply event through the reducer and fire callbacks."""
        event_type = event.get("type", "unknown")
        old_transport = self._state.transport
        old_segments = dict(self._state.segments)

        if event_type == "hello":
            # Admission succeeded. Keep the accumulated failure count until a
            # valid pong proves stability, but do not continue labelling the
            # newly admitted session as capacity-blocked.
            self._is_server_busy = False

        # A pong is a health acknowledgement only for the one outstanding ping
        # of this connection generation. Unsolicited/stale pongs must not reset
        # backoff or miss counters.
        if event_type == "pong":
            event_session_id = event.get("sessionId")
            valid_pong = (
                self._ping_pending
                and self._ping_generation == self._generation
                and (
                    event_session_id is None
                    or event_session_id == self._state.session_id
                )
            )
            if not valid_pong:
                logger.debug(
                    "Ignoring unsolicited/stale pong (gen=%d, pending_gen=%s, session=%r).",
                    self._generation,
                    self._ping_generation,
                    event_session_id,
                )
                self._fire_event_callback(event_type, event, valid_pong=False)
                return

            self._ping_pending = False
            self._ping_generation = None
            self._consecutive_misses = 0
            if not self._first_pong_received:
                self._first_pong_received = True
                self._backoff_attempt = 0
                self._is_server_busy = False
                self._last_failure_reason = ""

        # Reduce
        self._state = reduce(self._state, event)

        callback_fired = False
        if event_type in ("error", "ready"):
            # Error/availability classification must be visible to the
            # controller before the derived transport callback can collapse it
            # into a generic disconnect reason.
            self._fire_event_callback(event_type, event, valid_pong=True)
            callback_fired = True

        # Transport change callback
        if self._state.transport != old_transport:
            self._fire_transport_change(self._state.transport)

        # State change callback
        if self.on_state_change:
            try:
                self.on_state_change(self._state)
            except Exception:
                logger.exception("Error in state change callback.")

        # Text callback for new/updated segments
        if event_type in ("realtime", "final") and self.on_text:
            seg_id = event.get("segmentId")
            if seg_id is not None and seg_id in self._state.segments:
                seg = self._state.segments[seg_id]
                is_new_or_changed = (
                    seg_id not in old_segments
                    or old_segments[seg_id].text != seg.text
                    or old_segments[seg_id].is_final != seg.is_final
                )
                if is_new_or_changed:
                    try:
                        self.on_text(seg.segment_id, seg.text, seg.is_final)
                    except Exception:
                        logger.exception("Error in text callback.")

        # Generic event callback
        if not callback_fired:
            self._fire_event_callback(event_type, event, valid_pong=True)

        # Log interesting events
        if event_type == "warning":
            logger.warning("Server warning: %s", event.get("message"))
        elif event_type == "error":
            logger.error(
                "Server error: where=%s msg=%s",
                event.get("where"), event.get("message")
            )
        elif event_type == "final":
            logger.info(
                "Final [seg=%s]: %s",
                event.get("segmentId"), event.get("text", "")[:80]
            )
        elif event_type == "realtime":
            text = event.get("displayText") or event.get("text", "")
            logger.debug(
                "Realtime [seg=%s]: %s",
                event.get("segmentId"), text[:80]
            )

    def _fire_event_callback(
        self, event_type: str, event: dict, *, valid_pong: bool
    ) -> None:
        if not self.on_event:
            return
        callback_event = dict(event)
        callback_event["_clientGeneration"] = self._generation
        if event_type == "pong":
            callback_event["_validPong"] = valid_pong
        try:
            self.on_event(event_type, callback_event)
        except Exception:
            logger.exception("Error in event callback.")

    def _update_transport(self, new_state: TransportState) -> None:
        """Update transport state and fire callback."""
        if self._state.transport != new_state:
            self._state.transport = new_state
            self._fire_transport_change(new_state)
            if self.on_state_change:
                try:
                    self.on_state_change(self._state)
                except Exception:
                    logger.exception("Error in state change callback.")

    def _fire_transport_change(self, new_state: TransportState) -> None:
        if self.on_transport_change:
            try:
                self.on_transport_change(new_state)
            except Exception:
                logger.exception("Error in transport change callback.")
        logger.info("Transport state: %s", new_state.name)

    # -------------------------------------------------------------------
    # Internal: ping loop
    # -------------------------------------------------------------------

    async def _ping_loop(self) -> None:
        """Periodically send application-level pings."""
        generation = self._generation
        while (
            self._running
            and generation == self._generation
            and self._ws_is_open()
        ):
            try:
                await asyncio.sleep(self._config.ping_interval)
                if generation != self._generation or not self._ws_is_open():
                    break

                if self._ping_pending:
                    self._consecutive_misses += 1
                    logger.debug("Ping miss #%d (gen %d)", self._consecutive_misses, self._generation)
                    if self._consecutive_misses >= self._config.ping_timeout_count:
                        logger.warning(
                            "Ping timeout after %d consecutive misses, closing connection (gen %d).",
                            self._consecutive_misses,
                            self._generation,
                        )
                        await self.invalidate_connection("ping_timeout")
                        break
                    # There is no ping ID. Keep the same ping outstanding and
                    # never create an overlapping measurement.
                    continue

                await self.send_ping()

            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.warning(
                    "Ping loop failed; recycling connection: %s", exc
                )
                await self.invalidate_connection("ping_send_error")
                break

    # -------------------------------------------------------------------
    # Internal: backoff
    # -------------------------------------------------------------------

    def _backoff_delay(self) -> float:
        """Calculate reconnection delay with exponential backoff and jitter."""
        min_delay = self._config.reconnect_min_delay
        if self._is_server_busy:
            min_delay = max(min_delay, self._config.server_busy_min_delay)

        # _backoff_attempt counts failed connections. The first failure uses
        # the configured minimum, subsequent failures double from there.
        exponent = max(self._backoff_attempt - 1, 0)
        base = min(
            min_delay * (2 ** exponent),
            self._config.reconnect_max_delay,
        )
        jitter = base * self._config.reconnect_jitter * random.random()
        total_delay = base + jitter
        return min(total_delay, self._config.reconnect_max_delay)

    def _record_failure(self, reason: str, *, server_busy: bool = False) -> None:
        self._backoff_attempt += 1
        self._last_failure_reason = reason
        if server_busy:
            self._is_server_busy = True

    @staticmethod
    def _connection_close_code(exc: BaseException) -> Optional[int]:
        """Extract close code across supported websockets exception shapes."""
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

    # -------------------------------------------------------------------
    # Internal: send helpers
    # -------------------------------------------------------------------

    async def _send_json(self, data: dict) -> None:
        """Send a JSON text frame."""
        if not self._ws_is_open():
            raise ConnectionError("WebSocket is not open")
        await self._ws.send(json.dumps(data))
