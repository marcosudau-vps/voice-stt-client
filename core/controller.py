"""
UI-neutral core controller for RealtimeSTT Desktop Client.

Integrates STTSession, AudioCapture, TranscriptHistoryManager,
TextInjectionQueue, and TranscriptReinsertionService into a unified lifecycle.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
import math
import sys
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from core.config import AppConfig
from core.stt_session import STTSession, TransportState, ClientState, SessionState
from core.audio_capture import AudioCapture
from core.history import (
    TranscriptHistoryManager,
    HistoryEntry,
    HistoryAddStatus,
    HistoryAddResult,
)
from core.text_injector import (
    TextInjectionQueue,
    WindowsInjectionBackend,
    CtypesWindowsInjectionBackend,
    QueueState,
)
from core.reinsertion import (
    TranscriptReinsertionService,
    ReinsertionResult,
    ReinsertionStatus,
)
from core.event_protocol import EventProtocolResult
from core.event_models import CanonicalEventType
from core.event_normalizer import EventNormalizationError
from core.feedback_reducer import FeedbackDecision, FeedbackEngine
from core.observability.adapters.client_events import ClientEventEmitter
from core.observability.adapters.server_live import ServerLiveAdapter
from core.observability.ingress import NULL_INGRESS
from core.session_coordinator import DualSessionCoordinator, SessionContext

logger = logging.getLogger("controller")

# ARCH §8.6 / CONTRACTS §12.4: the record type under which the LoggingWorker
# publishes the merged capture-and-send counters every five seconds.
AUDIO_STATS_TYPE = "client.audio.stream_stats"


class FinalProcessingStatus(str, Enum):
    """Result status of processing a raw final transcript event."""

    QUEUED = "queued"
    DEDUPLICATED = "deduplicated"
    INVALID_FINAL = "invalid_final"
    HISTORY_UNAVAILABLE = "history_unavailable"
    QUEUE_UNAVAILABLE = "queue_unavailable"
    FAILED = "failed"


class AvailabilityState(str, Enum):
    """UI-neutral availability state of the controller."""

    STARTING = "starting"
    CONNECTING = "connecting"
    READY = "ready"
    NETWORK_UNAVAILABLE = "network_unavailable"
    SERVER_BUSY = "server_busy"
    SERVER_UNAVAILABLE = "server_unavailable"
    PROTOCOL_ERROR = "protocol_error"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"
    MICROPHONE_UNAVAILABLE = "microphone_unavailable"


class DictationState(str, Enum):
    """UI-neutral dictation state."""

    IDLE = "idle"
    STARTING = "starting"
    ACTIVE = "active"


class DictationWindowPhase(str, Enum):
    """Hotkey-mode phase driven by authoritative server timeline events."""

    INACTIVE = "inactive"
    WAITING_FIRST_SPEECH = "waiting_first_speech"
    SEGMENT_ACTIVE = "segment_active"
    FOLLOWUP_WAIT = "followup_wait"


class TransientEventType(str, Enum):
    """UI-neutral transient feedback event types."""

    ACTION_BLOCKED = "action_blocked"
    DICTATION_START_FAILED = "dictation_start_failed"
    DICTATION_INTERRUPTED = "dictation_interrupted"


@dataclass(frozen=True)
class TransientEvent:
    """UI-neutral transient feedback event payload."""

    event_type: TransientEventType
    reason: str
    description: str
    timestamp: float
    action: Optional[str] = None


@dataclass(frozen=True)
class ControllerStatusSnapshot:
    """Complete UI-neutral status snapshot for UI and diagnostics."""

    availability_state: AvailabilityState
    dictation_state: DictationState
    reason_code: str
    description: str
    reconnect_attempt: int
    next_retry_delay: Optional[float]
    session_id: Optional[str]
    generation: int
    revision: int
    is_running: bool
    is_closing: bool
    queue_size: int
    operating_mode: str = "hotkey"
    dictation_window_phase: DictationWindowPhase = DictationWindowPhase.INACTIVE
    server_status: SessionState = SessionState.IDLE


@dataclass(frozen=True)
class FinalProcessingResult:
    """UI-neutral result container for a processed final transcript event."""

    status: FinalProcessingStatus
    session_id: Optional[str] = None
    segment_id: Optional[int] = None
    text: Optional[str] = None
    entry_id: Optional[str] = None
    reason: Optional[str] = None
    error: Optional[str] = None
    is_conflict: bool = False


@dataclass(frozen=True)
class ControllerStatus:
    """UI-neutral snapshot of the controller's current state (AP4 backwards compat)."""

    is_running: bool
    is_closing: bool
    dictation_requested: bool
    transport_state: TransportState
    server_status: str
    queue_state: str
    queue_size: int
    history_enabled: bool


@dataclass(frozen=True)
class CommandResult:
    """UI-neutral result for semantic controller commands."""

    success: bool
    status: str
    message: Optional[str] = None


class _TriggerRejectedError(RuntimeError):
    """The server answered a manual trigger with ``accepted: false``.

    A rejection is a valid answer, not a transport fault, so it must not
    recycle the connection the way a failed command would.
    """

    def __init__(self, ack):
        super().__init__(f"trigger rejected: {ack.reason}")
        self.ack = ack


@dataclass
class _StartAttempt:
    """One session-bound start command and its asynchronous resolution."""

    token: int
    generation: int
    session_id: Optional[str]
    future: asyncio.Future
    send_task: asyncio.Task
    command_sent: bool = False
    pending_confirmation: Optional[SessionState] = None


_START_CONFIRM_STATES = frozenset(
    {
        SessionState.LISTENING,
        SessionState.WAKEWORD_WAIT,
        SessionState.WAKEWORD_DETECTED,
        SessionState.VOICE,
        SessionState.SILENCE,
        SessionState.RECORDING,
        SessionState.TRANSCRIBING,
    }
)
_MAX_PROCESSED_FINAL_IDENTITIES = 4096


class STTController:
    """
    UI-neutral controller orchestrating all STT components.
    """

    def __init__(
        self,
        config: AppConfig,
        session: Optional[STTSession] = None,
        audio: Optional[AudioCapture] = None,
        history_manager: Optional[TranscriptHistoryManager] = None,
        injection_queue: Optional[TextInjectionQueue] = None,
        reinsertion_service: Optional[TranscriptReinsertionService] = None,
        backend: Optional[WindowsInjectionBackend] = None,
        session_coordinator: Optional[DualSessionCoordinator] = None,
        feedback_engine: Optional[FeedbackEngine] = None,
        observability=NULL_INGRESS,
    ):
        self.config = config
        # CONTRACTS §6: constructor injection, no module singleton. A freely
        # instantiated controller (as in most tests) therefore observes
        # nothing at all, which is what keeps test runs uncoupled.
        self.observability = observability
        self._observe = ClientEventEmitter(observability, component="controller")

        # Shared component initialization
        self.history = history_manager or TranscriptHistoryManager(config.history)

        if injection_queue is not None:
            self.queue = injection_queue
        else:
            win_backend = backend
            if win_backend is None and sys.platform == "win32":
                win_backend = CtypesWindowsInjectionBackend()
            self.queue = TextInjectionQueue(
                config, self.history, win_backend, observability=observability
            )

        queue_history = getattr(self.queue, "history_manager", None)
        if queue_history is not None and queue_history is not self.history:
            raise ValueError(
                "Injection queue and controller must share the same history manager."
            )

        self.reinsertion = reinsertion_service or TranscriptReinsertionService(
            self.history, self.queue
        )
        reinsertion_history = getattr(self.reinsertion, "history_manager", None)
        reinsertion_queue = getattr(self.reinsertion, "injection_queue", None)
        if (
            reinsertion_history is not None
            and reinsertion_history is not self.history
        ):
            raise ValueError(
                "Reinsertion service and controller must share the same history manager."
            )
        if reinsertion_queue is not None and reinsertion_queue is not self.queue:
            raise ValueError(
                "Reinsertion service and controller must share the same injection queue."
            )

        self.session = session or STTSession(
            config.server,
            config.session,
            require_session_contract=True,
            observability=observability,
        )
        self.audio = audio or AudioCapture(config.audio, observability=observability)
        self.session_coordinator = session_coordinator or DualSessionCoordinator(
            config.server,
            config.event_stream,
            observability=observability,
        )
        self.feedback_engine = feedback_engine or FeedbackEngine(
            config.feedback_mappings
        )

        # Event loop and audio bridge state
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._audio_send_queue: asyncio.Queue[
            Tuple[bytes, int, int, int, int]
        ] = asyncio.Queue(maxsize=300)
        self._coordinator_tasks: set[asyncio.Task] = set()

        # Thread safety & lifecycle state
        self._lock = threading.Lock()
        self._transition_lock: Optional[asyncio.Lock] = None
        self._started = False
        self._closing = False
        self._shutdown_completed = False
        self._shutdown_error: Optional[Exception] = None
        self._shutdown_task: Optional[asyncio.Task] = None
        self._queue_cleanup_done = False
        self._dictation_requested = False

        # AP05 state attributes
        self._availability_state = AvailabilityState.STARTING
        self._dictation_state = DictationState.IDLE
        self._dictation_generation = 0
        self._reason_code = "initializing"
        self._reason_description = "Controller is initializing"
        self._status_revision = 0
        self._last_published_server_status = self.session.state.server_status
        self._start_attempt: Optional[_StartAttempt] = None
        self._start_attempt_token = 0
        self._initial_auto_start_requested = False
        self._initial_auto_start_done = False
        self._server_error_counts: Dict[str, int] = {}
        self._window_phase = DictationWindowPhase.INACTIVE
        self._window_timer_task: Optional[asyncio.Task] = None
        self._window_timer_token = 0
        self._window_deadline: Optional[float] = None
        self._pending_window_extension = 0.0
        self._timeout_warning_task: Optional[asyncio.Task] = None
        self._timeout_warning_token = 0
        self._timeout_warning_active = False
        self._discard_finals = False
        self._wake_mode_desired = (
            config.session.effective_wake_word_trigger_enabled
        )
        self._last_accepted_trigger = None
        self._wake_maintenance_suspended = False

        # In-memory deduplication index pro session: (session_id, segment_id) -> text
        self._processed_finals: OrderedDict[Tuple[str, int], str] = (
            OrderedDict()
        )

        # ARCH §8.6 hot-path counters of the send path. Plain ``int``, no lock,
        # written by ``_enqueue_audio_packet`` and read by the LoggingWorker.
        self.chunks_dropped_send_queue = 0
        self.max_send_queue_depth = 0

        # Callbacks exposed for UI or orchestrator
        self.on_text: Optional[Callable[[int, str, bool], None]] = None
        self.on_transport_change: Optional[Callable[[TransportState], None]] = None
        self.on_state_change: Optional[Callable[[ClientState], None]] = None
        self.on_final_result: Optional[Callable[[FinalProcessingResult], None]] = None
        self.on_snapshot_change: Optional[Callable[[ControllerStatusSnapshot], None]] = None
        self.on_feedback_event: Optional[Callable[[TransientEvent], None]] = None
        self.on_event_stream_event: Optional[
            Callable[[SessionContext, EventProtocolResult], Any]
        ] = None
        self.on_session_context_change: Optional[
            Callable[[SessionContext], None]
        ] = None
        self.on_feedback_decision: Optional[
            Callable[[FeedbackDecision], None]
        ] = None

        # Internal callback wiring
        self.session.on_event = self.handle_server_event
        self.session.on_transport_change = self._handle_transport_change
        self.session.on_state_change = self._handle_state_change
        self.session.on_text = self._handle_session_text
        self.audio.on_audio_packet = self._on_audio_packet_from_thread
        self.session_coordinator.on_event = self._handle_event_stream_event
        self.session_coordinator.on_context_change = (
            self._handle_session_context_change
        )
        # CONTRACTS §6/§7.1: the fan-out. ``on_event`` (feedback) and
        # ``on_observation`` (logging) are two INDEPENDENT branches of the same
        # dispatch; logging neither owns nor steers the feedback branch (O-02).
        self.server_live_adapter = ServerLiveAdapter(observability)
        self.session_coordinator.on_observation = self.server_live_adapter
        # ARCH §8.6: register the read-only counter source the worker polls.
        self._register_audio_stats_source()

    # -------------------------------------------------------------------
    # ARCH §8.6 / CONTRACTS §12.4: the 5-second audio aggregate
    # -------------------------------------------------------------------

    def _register_audio_stats_source(self) -> None:
        register = getattr(self.observability, "register_aggregate_source", None)
        if register is None:
            return
        try:
            register(AUDIO_STATS_TYPE, self._collect_audio_stats, component="audio")
        except Exception:  # noqa: BLE001 - O-05: logging setup never breaks the core
            pass

    def _unregister_audio_stats_source(self) -> None:
        register = getattr(self.observability, "register_aggregate_source", None)
        if register is None:
            return
        try:
            register(AUDIO_STATS_TYPE, None)
        except Exception:  # noqa: BLE001
            pass

    def _collect_audio_stats(self) -> Optional[Dict[str, Any]]:
        """Read the hot-path counters. **Runs on the LoggingWorker thread.**

        Returns ``None`` while nothing is streaming — ARCH §8.6 asks for the
        aggregate *"alle 5 s waehrend aktiven Streamings"*, and a stopped stream
        must not produce a record per interval for the rest of the process's
        life. Reads only plain ``int`` attributes and takes no controller lock:
        a lock held by the Qt or PortAudio path must never be waited on by the
        logging worker (O-03/O-05).
        """
        if not getattr(self.session, "is_streaming", False):
            return None
        stats: Dict[str, Any] = {
            "chunks_dropped_send_queue": self.chunks_dropped_send_queue,
            "max_send_queue_depth": self.max_send_queue_depth,
            "send_queue_depth": self._audio_send_queue.qsize(),
        }
        capture = getattr(self.audio, "capture_counters", None)
        if capture is not None:
            values = capture()
            if isinstance(values, dict):
                stats.update(values)
        send = getattr(self.session, "send_counters", None)
        if send is not None:
            values = send()
            if isinstance(values, dict):
                stats.update(values)
        return stats

    def _get_transition_lock(self) -> asyncio.Lock:
        if self._transition_lock is None:
            self._transition_lock = asyncio.Lock()
        return self._transition_lock

    @property
    def is_running(self) -> bool:
        """Whether the controller is currently active and not closing."""
        with self._lock:
            return self._started and not self._closing

    @property
    def is_closing(self) -> bool:
        """Whether the controller is in the process of shutting down."""
        with self._lock:
            return self._closing

    @property
    def dictation_requested(self) -> bool:
        """Whether dictation is requested by user/auto-start."""
        with self._lock:
            return self._dictation_requested

    def request_initial_auto_start(self) -> None:
        """Arm the existing one-shot startup path before ``run()`` begins."""
        with self._lock:
            if self._started or self._closing:
                raise RuntimeError(
                    "Initial auto-start must be requested before controller run."
                )
            self._dictation_requested = True
            self._initial_auto_start_requested = True

    @property
    def availability_state(self) -> AvailabilityState:
        """Current UI-neutral availability state."""
        with self._lock:
            return self._availability_state

    @property
    def dictation_state(self) -> DictationState:
        """Current UI-neutral dictation state."""
        with self._lock:
            return self._dictation_state

    def get_snapshot(self) -> ControllerStatusSnapshot:
        """Query complete UI-neutral controller status snapshot."""
        with self._lock:
            avail = self._availability_state
            dict_st = self._dictation_state
            reason = self._reason_code
            desc = self._reason_description
            rev = self._status_revision
            is_run = self._started and not self._closing
            is_close = self._closing

        sess_state = self.session.state
        return ControllerStatusSnapshot(
            availability_state=avail,
            dictation_state=dict_st,
            reason_code=reason,
            description=desc,
            reconnect_attempt=getattr(
                self.session,
                "reconnect_attempt",
                getattr(self.session, "_backoff_attempt", 0),
            ),
            next_retry_delay=getattr(self.session, "next_retry_delay", None),
            session_id=sess_state.session_id,
            generation=getattr(sess_state, "generation", 0),
            revision=rev,
            is_running=is_run,
            is_closing=is_close,
            queue_size=self.queue.queue_size(),
            operating_mode=self.config.session.presentation_mode,
            dictation_window_phase=self._window_phase,
            server_status=sess_state.server_status,
        )

    def _update_availability(self, state: AvailabilityState, reason: str = "", description: str = "") -> None:
        with self._lock:
            if self._availability_state == state and self._reason_code == reason:
                return
            self._availability_state = state
            self._reason_code = reason
            self._reason_description = description
            self._status_revision += 1

        self._publish_snapshot()

    def _update_dictation_state(
        self,
        state: DictationState,
        *,
        requested: Optional[bool] = None,
    ) -> None:
        with self._lock:
            changed = self._dictation_state != state
            if requested is not None and self._dictation_requested != requested:
                self._dictation_requested = requested
                changed = True
            self._dictation_state = state
            if not changed:
                return
            self._status_revision += 1

        self._publish_snapshot()

    def _publish_snapshot(self) -> None:
        snapshot = self.get_snapshot()
        if self.on_snapshot_change:
            try:
                self.on_snapshot_change(snapshot)
            except Exception:
                logger.exception("Error in on_snapshot_change callback.")

    # CONTRACTS §12.2: three of the audit hooks share this one site, because
    # this is where the client decides that an intended action did not happen.
    _TRANSIENT_OBSERVATION_TYPES = {
        TransientEventType.ACTION_BLOCKED: "client.action.blocked",
        TransientEventType.DICTATION_START_FAILED: "client.dictation.failed",
        TransientEventType.DICTATION_INTERRUPTED: "client.dictation.interrupted",
    }

    def _emit_feedback_event(self, event_type: TransientEventType, reason: str, description: str, action: Optional[str] = None) -> None:
        event = TransientEvent(
            event_type=event_type,
            reason=reason,
            description=description,
            timestamp=time.time(),
            action=action,
        )
        observation_type = self._TRANSIENT_OBSERVATION_TYPES.get(event_type)
        if observation_type is not None:
            self._observe.audit(
                observation_type,
                level="WARNING",
                message=description,
                details={"reason": reason, "action": action},
                session_id=self.session.state.session_id,
                generation=getattr(self.session, "generation", 0),
                correlation_id=f"client:{event_type.value}:{event.timestamp}",
            )
        if self.on_feedback_event:
            try:
                self.on_feedback_event(event)
            except Exception:
                logger.exception("Error in on_feedback_event callback.")
        canonical = {
            TransientEventType.ACTION_BLOCKED: CanonicalEventType.CLIENT_ACTION_BLOCKED,
            TransientEventType.DICTATION_START_FAILED: CanonicalEventType.CLIENT_ACTION_BLOCKED,
            TransientEventType.DICTATION_INTERRUPTED: CanonicalEventType.CLIENT_DICTATION_INTERRUPTED,
        }[event_type]
        decision = self.feedback_engine.handle_local(
            canonical,
            generation=getattr(self.session, "generation", 0),
            session_id=self.session.state.session_id,
            correlation_id=f"client:{event_type.value}:{event.timestamp}",
            details={"reason": reason, "action": action},
        )
        self._publish_feedback_decision(decision)

    def _publish_feedback_decision(self, decision: FeedbackDecision) -> None:
        if not decision.publish or self.on_feedback_decision is None:
            return
        try:
            self.on_feedback_decision(decision)
        except Exception:
            logger.exception("Error in on_feedback_decision callback.")

    def report_local_feedback(
        self,
        event_type: CanonicalEventType,
        details: Optional[Dict[str, object]] = None,
    ) -> FeedbackDecision:
        """Feed a UI/device-local fact back through the canonical reducer."""
        if (
            not isinstance(event_type, CanonicalEventType)
            or not event_type.value.startswith("client.")
        ):
            raise ValueError("local feedback must use a canonical client.* event")
        decision = self.feedback_engine.handle_local(
            event_type,
            generation=getattr(self.session, "generation", 0),
            session_id=self.session.state.session_id,
            details=details,
        )
        self._publish_feedback_decision(decision)
        return decision

    def get_status(self) -> ControllerStatus:
        """Query current UI-neutral controller status (AP4 backwards compat)."""
        with self._lock:
            is_run = self._started and not self._closing
            is_close = self._closing
            dict_req = self._dictation_requested

        q_state = getattr(self.queue, "_state", None)
        q_state_str = q_state.value if isinstance(q_state, QueueState) else str(q_state)
        srv_status = self.session.state.server_status.value if hasattr(self.session.state.server_status, "value") else str(self.session.state.server_status)

        return ControllerStatus(
            is_running=is_run,
            is_closing=is_close,
            dictation_requested=dict_req,
            transport_state=self.session.state.transport,
            server_status=srv_status,
            queue_state=q_state_str,
            queue_size=self.queue.queue_size(),
            history_enabled=self.history.config.enabled,
        )

    # -------------------------------------------------------------------
    # Semantic Dictation Commands (Serialized Async Transitions)
    # -------------------------------------------------------------------

    async def start_dictation(self) -> CommandResult:
        """Start one session-bound dictation and await server confirmation."""
        async with self._get_transition_lock():
            immediate, attempt = self._begin_start_locked()
        if immediate is not None:
            return immediate
        assert attempt is not None
        return await self._await_start_attempt(attempt)

    def _begin_start_locked(
        self,
    ) -> Tuple[Optional[CommandResult], Optional[_StartAttempt]]:
        with self._lock:
            if self._closing:
                return (
                    CommandResult(
                        success=False,
                        status="closing",
                        message="Controller is shutting down",
                    ),
                    None,
                )

            blocked_availability = self._availability_state in {
                AvailabilityState.NETWORK_UNAVAILABLE,
                AvailabilityState.SERVER_BUSY,
                AvailabilityState.SERVER_UNAVAILABLE,
                AvailabilityState.PROTOCOL_ERROR,
                AvailabilityState.SHUTTING_DOWN,
                AvailabilityState.STOPPED,
            }

        if not self.session.is_ready or blocked_availability:
            with self._lock:
                self._dictation_state = DictationState.IDLE
                self._dictation_requested = False

            self._emit_feedback_event(
                TransientEventType.ACTION_BLOCKED,
                reason="transport_not_ready",
                description=f"Transport not ready (current: {self.session.state.transport.name})",
                action="start_dictation",
            )
            return (
                CommandResult(
                    success=False,
                    status="transport_not_ready",
                    message=f"Transport not ready (current: {self.session.state.transport.name})",
                ),
                None,
            )

        with self._lock:
            if self._dictation_state == DictationState.ACTIVE:
                return (
                    CommandResult(
                        success=True,
                        status="already_started",
                        message="Dictation already active",
                    ),
                    None,
                )
            if self._dictation_state == DictationState.STARTING:
                return (
                    CommandResult(
                        success=False,
                        status="start_in_progress",
                        message="Dictation start is already in progress",
                    ),
                    None,
                )

            loop = asyncio.get_running_loop()
            self._start_attempt_token += 1
            future = loop.create_future()
            # `start` is and stays a *stream* command. A manual trigger is an
            # additional command on top of the running stream and must never
            # replace it, otherwise the audio stream would never begin.
            send_task = loop.create_task(
                self._begin_stream_and_trigger(source="manual")
            )
            attempt = _StartAttempt(
                token=self._start_attempt_token,
                generation=getattr(self.session, "generation", 0),
                session_id=self.session.state.session_id,
                future=future,
                send_task=send_task,
            )
            self._start_attempt = attempt
            self._dictation_state = DictationState.STARTING
            self._dictation_requested = True
            self._dictation_generation = attempt.generation
            self._status_revision += 1

        # CONTRACTS §12.2: client.dictation.start_attempt (S). Outside the
        # lock, and after the attempt exists -- the correlation id is derived
        # from generation and token, which is the same identity the accepted
        # feedback uses (``_manual_accept_correlation``).
        self._observe.audit(
            "client.dictation.start_attempt",
            details={
                "token": attempt.token,
                "server_owns_activation": self._server_owns_activation,
            },
            session_id=attempt.session_id,
            generation=attempt.generation,
            correlation_id=f"hotkey:{attempt.generation}:{attempt.token}",
        )

        try:
            self.audio.start()
        except Exception as e:
            with self._lock:
                if self._start_attempt is attempt:
                    self._start_attempt = None
                self._dictation_state = DictationState.IDLE
                self._dictation_requested = False
                self._status_revision += 1
            send_task.cancel()
            logger.error("Error starting audio capture: %s", e)
            self._publish_snapshot()
            self._emit_feedback_event(
                TransientEventType.DICTATION_START_FAILED,
                reason="audio_start_failed",
                description="Audio capture could not be started",
                action="start_dictation",
            )
            return (
                CommandResult(
                    success=False,
                    status="audio_start_failed",
                    message=str(e),
                ),
                None,
            )

        self._publish_snapshot()
        return None, attempt

    @property
    def _server_owns_activation(self) -> bool:
        """Whether this server announced the activation trigger contract."""
        return bool(getattr(self.session, "supports_activation_triggers", False))

    @property
    def _client_owns_dictation_window(self) -> bool:
        """Whether the client still has to time the dictation window itself.

        Only against a server without the activation contract. As soon as the
        server owns the activation, a second local window would be a competing
        authority that could end a turn the server still holds open.
        """
        return (
            self.config.session.effective_manual_trigger_enabled
            and not self._server_owns_activation
        )

    async def _begin_stream_and_trigger(self, source: str = "manual") -> None:
        """Start the audio stream, then ask the server to open an activation.

        Against a server without the trigger capability this is exactly the old
        behaviour: only `start` is sent and the server decides on its own.
        """
        if not self.session.state.streaming_requested:
            await self.session.send_start()
        if not self._server_owns_activation:
            return
        ack = await self.session.request_trigger(action="activate", source=source)
        if not ack.accepted:
            logger.info(
                "Server rejected the manual trigger: reason=%s commandId=%s",
                ack.reason, ack.command_id,
            )
            raise _TriggerRejectedError(ack)
        self._last_accepted_trigger = ack

    def _manual_accept_correlation(self, attempt: "_StartAttempt") -> str:
        """The id that makes manual-accepted feedback idempotent.

        With a server-owned activation the ``commandId`` is the natural key:
        the same command can never be accepted twice, so a repeated ack cannot
        turn into a second impulse.
        """
        ack = self._last_accepted_trigger
        if ack is not None and self._server_owns_activation:
            return f"trigger:{ack.command_id}"
        return f"hotkey:{attempt.generation}:{attempt.token}"

    async def _await_start_attempt(self, attempt: _StartAttempt) -> CommandResult:
        timeout = self.config.server.start_confirmation_timeout
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout

        try:
            done, _ = await asyncio.wait(
                {attempt.send_task, attempt.future},
                timeout=max(0.0, deadline - loop.time()),
                return_when=asyncio.FIRST_COMPLETED,
            )
            if not done:
                return await self._fail_start_attempt(
                    attempt,
                    status="start_confirmation_timeout",
                    reason="start_confirmation_timeout",
                    message=f"Server did not confirm start within {timeout}s",
                    recycle_connection=True,
                )

            if attempt.future in done:
                resolution, confirmed_state = attempt.future.result()
                if resolution != "confirmed":
                    if not attempt.send_task.done():
                        attempt.send_task.cancel()
                        await asyncio.gather(attempt.send_task, return_exceptions=True)
                    return self._start_resolution_result(resolution)

            if attempt.send_task in done:
                try:
                    attempt.send_task.result()
                except asyncio.CancelledError:
                    if attempt.future.done():
                        resolution, _ = attempt.future.result()
                        return self._start_resolution_result(resolution)
                    return self._start_resolution_result("cancelled")
                except _TriggerRejectedError as rejected:
                    # The server said no. That is an answer, not a fault, so
                    # the connection stays up and no accepted-feedback fires.
                    return await self._fail_start_attempt(
                        attempt,
                        status="trigger_rejected",
                        reason=f"trigger_rejected:{rejected.ack.reason}",
                        message=(
                            "Der Server hat den Trigger abgelehnt: "
                            f"{rejected.ack.reason}"
                        ),
                        recycle_connection=False,
                    )
                except Exception as exc:
                    return await self._fail_start_attempt(
                        attempt,
                        status="start_command_failed",
                        reason="start_command_failed",
                        message=str(exc),
                        recycle_connection=True,
                    )

                pending_state = None
                with self._lock:
                    if self._start_attempt is attempt:
                        attempt.command_sent = True
                        pending_state = attempt.pending_confirmation
                        if pending_state is None and self._server_owns_activation:
                            # An accepted trigger_ack *is* the confirmation for
                            # an activation. There is no additional stream
                            # status to wait for: the server only accepts a
                            # trigger while the stream is running, and from the
                            # second activation onwards no `start` is sent, so
                            # no status transition would ever arrive.
                            pending_state = SessionState.LISTENING
                if pending_state is not None and not attempt.future.done():
                    attempt.future.set_result(("confirmed", pending_state))

            if not attempt.future.done():
                try:
                    await asyncio.wait_for(
                        asyncio.shield(attempt.future),
                        timeout=max(0.0, deadline - loop.time()),
                    )
                except asyncio.TimeoutError:
                    return await self._fail_start_attempt(
                        attempt,
                        status="start_confirmation_timeout",
                        reason="start_confirmation_timeout",
                        message=f"Server did not confirm start within {timeout}s",
                        recycle_connection=True,
                    )

            resolution, confirmed_state = attempt.future.result()
            if resolution != "confirmed":
                return self._start_resolution_result(resolution)

            async with self._get_transition_lock():
                with self._lock:
                    still_current = (
                        self._start_attempt is attempt
                        and self._dictation_state == DictationState.STARTING
                        and attempt.generation
                        == getattr(self.session, "generation", 0)
                        and self.session.is_ready
                        and not self._closing
                    )
                    if still_current:
                        self._start_attempt = None
                        self._dictation_state = DictationState.ACTIVE
                        self._dictation_requested = True
                        self._status_revision += 1

                if not still_current:
                    return self._start_resolution_result("interrupted")

                self.session.set_streaming(True)
                self._discard_finals = False
                if self._client_owns_dictation_window:
                    with self._lock:
                        initial_extension = self._pending_window_extension
                        self._pending_window_extension = 0.0
                    self._arm_dictation_window(
                        DictationWindowPhase.WAITING_FIRST_SPEECH,
                        self.config.dictation_window.initial_speech_timeout
                        + initial_extension,
                    )
                else:
                    self._publish_snapshot()

                # Manual-accepted feedback fires exactly once per accepted
                # trigger. Against a trigger-capable server we are only here
                # because the server acknowledged with accepted=true, so this
                # is the "after the ack" point the specification requires. The
                # correlation id is the commandId, which makes a repeated ack
                # collapse into the same decision instead of a second impulse.
                self._publish_feedback_decision(
                    self.feedback_engine.handle_local(
                        CanonicalEventType.CLIENT_HOTKEY_ACCEPTED,
                        generation=attempt.generation,
                        session_id=attempt.session_id,
                        correlation_id=self._manual_accept_correlation(attempt),
                        details={"action": "start_dictation"},
                    )
                )
                state_name = (
                    confirmed_state.value
                    if isinstance(confirmed_state, SessionState)
                    else "listening"
                )
                # CONTRACTS §12.2: client.dictation.confirmed (S). The same
                # correlation id as the accepted feedback decision, so a
                # confirmed dictation, its trigger ack and its feedback impulse
                # are one query rather than three.
                self._observe.audit(
                    "client.dictation.confirmed",
                    details={"state": state_name, "token": attempt.token},
                    session_id=attempt.session_id,
                    generation=attempt.generation,
                    correlation_id=self._manual_accept_correlation(attempt),
                )
                return CommandResult(
                    success=True,
                    status=state_name,
                    message="Dictation started",
                )
        except asyncio.CancelledError:
            await self._fail_start_attempt(
                attempt,
                status="start_cancelled",
                reason="start_cancelled",
                message="Dictation start was cancelled",
                recycle_connection=attempt.command_sent,
                emit_feedback=False,
            )
            raise

    async def _fail_start_attempt(
        self,
        attempt: _StartAttempt,
        *,
        status: str,
        reason: str,
        message: str,
        recycle_connection: bool,
        emit_feedback: bool = True,
    ) -> CommandResult:
        async with self._get_transition_lock():
            with self._lock:
                if self._start_attempt is not attempt:
                    if attempt.future.done():
                        resolution, _ = attempt.future.result()
                        return self._start_resolution_result(resolution)
                    return self._start_resolution_result("cancelled")
                self._start_attempt = None
                self._dictation_state = DictationState.IDLE
                self._dictation_requested = False
                self._status_revision += 1

            if not attempt.send_task.done():
                attempt.send_task.cancel()
                await asyncio.gather(attempt.send_task, return_exceptions=True)
            if not attempt.future.done():
                attempt.future.set_result(("failed", None))

            self.session.set_streaming(False)
            try:
                self.audio.stop()
            except Exception:
                logger.debug("Audio stop failed during start rollback.", exc_info=True)
            self._clear_audio_queue()
            self._publish_snapshot()

            if emit_feedback:
                self._emit_feedback_event(
                    TransientEventType.DICTATION_START_FAILED,
                    reason=reason,
                    description=message,
                    action="start_dictation",
                )

            if recycle_connection:
                invalidate = getattr(self.session, "invalidate_connection", None)
                if invalidate is not None:
                    try:
                        await invalidate(reason)
                    except Exception:
                        logger.debug(
                            "Failed to recycle ambiguous start connection.",
                            exc_info=True,
                        )

            return CommandResult(success=False, status=status, message=message)

    @staticmethod
    def _start_resolution_result(resolution: str) -> CommandResult:
        mapping = {
            "interrupted": (
                "dictation_interrupted",
                "Dictation start was interrupted by transport loss",
            ),
            "stopped": ("start_cancelled", "Dictation start was stopped"),
            "shutdown": ("closing", "Controller is shutting down"),
            "failed": ("start_failed", "Dictation start failed"),
            "command_error": (
                "start_command_rejected",
                "Server rejected the start command",
            ),
            "cancelled": ("start_cancelled", "Dictation start was cancelled"),
        }
        status, message = mapping.get(
            resolution, ("start_cancelled", "Dictation start did not complete")
        )
        return CommandResult(success=False, status=status, message=message)

    async def stop_dictation(self) -> CommandResult:
        """Deactivate dictation desired state asynchronously with transition lock."""
        async with self._get_transition_lock():
            return await self._stop_dictation_locked()

    async def _stop_dictation_locked(self) -> CommandResult:
        self._cancel_dictation_window()
        with self._lock:
            if self._closing:
                return CommandResult(success=False, status="closing", message="Controller is shutting down")
            attempt = self._start_attempt
            self._start_attempt = None
            self._initial_auto_start_requested = False
            self._dictation_requested = False
            changed = self._dictation_state != DictationState.IDLE
            self._dictation_state = DictationState.IDLE
            if changed:
                self._status_revision += 1

        if attempt is not None:
            if not attempt.send_task.done():
                attempt.send_task.cancel()
            if not attempt.future.done():
                attempt.future.set_result(("stopped", None))

        try:
            self.audio.stop()
            self.session.set_streaming(False)
            self._clear_audio_queue()
            if self.session.is_ready:
                try:
                    if self._server_owns_activation:
                        # Finish the activation, but leave the stream running:
                        # `stop` is a stream command and the session keeps
                        # streaming so the next trigger can take effect at once.
                        await self.session.send_trigger(
                            action="finish", source="manual"
                        )
                    else:
                        await self.session.send_stop()
                except Exception:
                    logger.info(
                        "Remote stop could not be sent; local dictation is already stopped.",
                        exc_info=True,
                    )
            if changed:
                self._publish_snapshot()
            return CommandResult(success=True, status="stopped", message="Dictation stopped")
        except Exception as e:
            logger.error("Error stopping audio dictation: %s", e)
            return CommandResult(success=False, status="error", message=str(e))

    async def toggle_dictation(self) -> CommandResult:
        """Toggle dictation desired state asynchronously with transition lock."""
        async with self._get_transition_lock():
            if self.dictation_requested:
                return await self._stop_dictation_locked()
            immediate, attempt = self._begin_start_locked()
        if immediate is not None:
            return immediate
        assert attempt is not None
        return await self._await_start_attempt(attempt)

    async def primary_dictation_action(self) -> CommandResult:
        """Arm/disarm the stream, or extend a running manual activation."""
        if not self.config.session.effective_manual_trigger_enabled:
            # Wake-word only: the primary action arms or disarms the stream,
            # because there is no manual activation to extend.
            if self.dictation_requested:
                self._wake_mode_desired = False
                return await self.stop_dictation()
            self._wake_mode_desired = True
            return await self.start_dictation()
        if self.dictation_requested:
            return self.extend_dictation_window()
        return await self.toggle_dictation()

    def extend_dictation_window(self) -> CommandResult:
        """Extend only the currently active hotkey dictation generation."""
        if not self.config.session.effective_manual_trigger_enabled:
            return CommandResult(
                False,
                "manual_trigger_disabled",
                "Window extension requires the manual trigger",
            )
        with self._lock:
            if (
                self._dictation_state
                not in {DictationState.STARTING, DictationState.ACTIVE}
                or not self._dictation_requested
            ):
                return CommandResult(
                    False, "not_active", "No active hotkey dictation to extend"
                )
            state = self._dictation_state
            phase = self._window_phase

        extension = self.config.dictation_window.extension_seconds
        if state == DictationState.STARTING:
            with self._lock:
                self._pending_window_extension += extension
            return CommandResult(
                True, "extension_armed", "Initial dictation window extended"
            )
        if phase == DictationWindowPhase.SEGMENT_ACTIVE:
            with self._lock:
                self._pending_window_extension += extension
            return CommandResult(True, "extension_armed", "Follow-up window extended")
        if phase in {
            DictationWindowPhase.WAITING_FIRST_SPEECH,
            DictationWindowPhase.FOLLOWUP_WAIT,
        }:
            loop = asyncio.get_running_loop()
            remaining = max(0.0, (self._window_deadline or loop.time()) - loop.time())
            self._arm_dictation_window(phase, remaining + extension)
            if self._server_owns_activation and self.session.is_ready:
                loop.create_task(
                    self.session.send_trigger(action="extend", source="manual")
                )
            return CommandResult(True, "extended", "Dictation window extended")
        return CommandResult(False, "not_active", "Dictation window is inactive")

    async def cancel_dictation(self) -> CommandResult:
        """Stop the current dictation and discard late finals until the next start."""
        self._discard_finals = True
        result = await self.stop_dictation()
        if self.session.is_ready:
            try:
                if self._server_owns_activation:
                    await self.session.send_trigger(
                        action="cancel", source="manual"
                    )
                await self.session.send_clear()
            except Exception:
                logger.info("Remote clear after cancel could not be sent.", exc_info=True)
        return CommandResult(result.success, "cancelled", result.message)

    # -------------------------------------------------------------------
    # Microphone mute and manual reconnects
    # -------------------------------------------------------------------

    @property
    def microphone_muted(self) -> bool:
        return self.audio.muted

    def set_microphone_muted(self, muted: bool) -> CommandResult:
        """Mute or unmute the microphone in this client.

        Deliberately not a device command. The reSpeaker's own mute button
        drives a firmware function that the documented control interface does
        not expose -- there is no MUTE parameter and no way to light the mute
        LED. Muting here is the part that actually matters and is the part that
        can be guaranteed: nothing captured leaves this machine.
        """
        self.audio.set_muted(muted)
        return CommandResult(
            True,
            "muted" if muted else "unmuted",
            "Mikrofon stummgeschaltet" if muted else "Mikrofon wieder aktiv",
        )

    async def reconnect_server(self) -> CommandResult:
        """Drop the server connection so the session rebuilds it now.

        The session reconnects on its own schedule with a backoff that grows to
        half a minute. That is right for an outage nobody is watching and wrong
        for somebody who has just fixed the network and is looking at the tray.
        """
        try:
            await self.session.invalidate_connection("manual_reconnect")
        except Exception as exc:
            logger.exception("Manual server reconnect failed.")
            return CommandResult(False, "reconnect_failed", str(exc))
        return CommandResult(True, "reconnecting", "Verbindung wird neu aufgebaut")

    async def apply_runtime_config(
        self,
        candidate: AppConfig,
        *,
        correlation_id: Optional[str] = None,
    ) -> CommandResult:
        """Validate and atomically activate one complete candidate config.

        ``correlation_id`` is purely observational (CONTRACTS §12.2: the
        runtime apply carries *"dieselbe correlation_id"* as the UI's
        ``client.settings.apply_started``/``.apply_completed``). It never
        influences the apply itself, and ``None`` simply means "not called
        from a settings dialog" — O-01 holds.
        """
        try:
            candidate.validate()
        except Exception as exc:
            # CONTRACTS §12.1: client.config.validation_failed (P+S), the core
            # half of the pair the settings dialog also reports. Only the
            # exception text, never a config value.
            self._observe.system(
                "client.config.validation_failed",
                level="WARNING",
                details={
                    "source": "apply_runtime_config",
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                },
                correlation_id=correlation_id,
            )
            raise
        old_config = self.config
        old_wake_mode_desired = self._wake_mode_desired
        session_changed = (
            candidate.server != old_config.server
            or candidate.session != old_config.session
        )
        audio_changed = candidate.audio != old_config.audio
        mode_changed = candidate.session.mode != old_config.session.mode
        candidate_wake_mode_desired = (
            True
            if mode_changed and candidate.session.mode == "wake_word"
            else (
                old_wake_mode_desired
                if candidate.session.mode == "wake_word"
                else False
            )
        )

        if session_changed:
            self._wake_maintenance_suspended = True

        try:
            if audio_changed and candidate.audio.device is not None:
                devices = {
                    int(device["index"]): device
                    for device in AudioCapture.list_devices()
                    if int(device.get("channels", 0)) > 0
                }
                if candidate.audio.device not in devices:
                    return CommandResult(
                        False,
                        "audio_device_unavailable",
                        "Selected input device is not currently available",
                    )

            if (session_changed or audio_changed) and self.dictation_requested:
                stopped = await self.stop_dictation()
                if not stopped.success:
                    return stopped

            old_audio = self.audio
            if audio_changed:
                replacement = AudioCapture(
                    candidate.audio, observability=self.observability
                )
                replacement.on_audio_packet = self._on_audio_packet_from_thread
                self.audio = replacement

            self._install_runtime_config(
                candidate,
                self.audio,
                candidate_wake_mode_desired,
            )
            # CONTRACTS §10.4: exactly here, directly after
            # _install_runtime_config. The observability settings are the only
            # ones whose change must set NONE of session_changed/audio_changed/
            # mode_changed -- they are computed above from server/session/audio
            # alone, so a pure logging change triggers neither a reconnect nor
            # an audio restart.
            self._apply_observability_config(candidate.logging.observability)
            await self.session_coordinator.update_config(
                candidate.server,
                candidate.event_stream,
            )
            self.feedback_engine.reconfigure_mapping(
                candidate.feedback_mappings
            )
            # CONTRACTS §12.2: client.settings.runtime_apply (S). §10.4's hard
            # rule is that a pure observability change sets none of
            # session_changed/audio_changed/mode_changed; those three flags are
            # therefore exactly what this record carries -- it makes the rule
            # checkable from the stored history instead of only from a test.
            self._observe.audit(
                "client.settings.runtime_apply",
                details={
                    "session_changed": bool(session_changed),
                    "audio_changed": bool(audio_changed),
                    "mode_changed": bool(mode_changed),
                },
                session_id=self.session.state.session_id,
                generation=getattr(self.session, "generation", 0),
                correlation_id=correlation_id,
            )

            if not session_changed:
                return CommandResult(True, "applied", "Configuration applied")

            reconfigure = getattr(self.session, "reconfigure", None)
            if reconfigure is None:
                self._install_runtime_config(
                    old_config,
                    old_audio,
                    old_wake_mode_desired,
                )
                return CommandResult(
                    False,
                    "reconnect_unsupported",
                    "Current session implementation cannot be reconfigured",
                )

            previous_generation = getattr(self.session, "generation", 0)
            try:
                await reconfigure(candidate.session, candidate.server)
            except Exception as exc:
                logger.exception("Could not request the new session configuration.")
                restored = await self._restore_runtime_config(
                    old_config,
                    old_audio,
                    old_wake_mode_desired,
                    reconfigure,
                )
                suffix = "" if restored else "; previous configuration restore failed"
                return CommandResult(
                    False,
                    "session_reconfigure_failed",
                    f"{exc}{suffix}",
                )

            reconnected = await self._wait_for_reconfigured_session(
                previous_generation,
                candidate.server,
            )
            if reconnected:
                if candidate_wake_mode_desired:
                    armed = await self.start_dictation()
                    if not armed.success:
                        restored = await self._restore_runtime_config(
                            old_config,
                            old_audio,
                            old_wake_mode_desired,
                            reconfigure,
                        )
                        suffix = (
                            ""
                            if restored
                            else "; previous configuration restore failed"
                        )
                        return CommandResult(
                            False,
                            "wake_word_arm_failed",
                            f"Wake-word stream could not be armed: "
                            f"{armed.message}{suffix}",
                        )
                return CommandResult(
                    True,
                    "reconnected",
                    "Configuration applied, confirmed and activated",
                )

            restored = await self._restore_runtime_config(
                old_config,
                old_audio,
                old_wake_mode_desired,
                reconfigure,
            )
            suffix = "" if restored else "; previous configuration restore failed"
            return CommandResult(
                False,
                "session_configuration_rejected",
                "Server did not confirm the requested session configuration"
                f"{suffix}",
            )
        finally:
            if session_changed:
                self._wake_maintenance_suspended = False

    def _apply_observability_config(self, observability_config: Any) -> None:
        """CONTRACTS §10.4: *"apply_config ist NICHT werfend und liefert
        nichts zurueck; ein Fehler dort darf das Apply-Ergebnis nicht
        beeinflussen."*

        The concrete ingress honours that itself. The guard exists because
        ``self.observability`` is typed as an ``Ingress`` and may be any
        implementation of it — a test double or a future adapter — and O-01
        forbids the logging domain from deciding whether an apply succeeded.
        Same reasoning as the single ``try/except`` in ``ClientEventEmitter``;
        ``BaseException`` stays uncaught so ``asyncio.CancelledError`` keeps
        travelling (ARCH §7.3).
        """
        apply_config = getattr(self.observability, "apply_config", None)
        if apply_config is None:
            return
        try:
            apply_config(observability_config)
        except Exception:  # noqa: BLE001 - the logging domain stops here
            pass

    def _install_runtime_config(
        self,
        config: AppConfig,
        audio: AudioCapture,
        wake_mode_desired: bool,
    ) -> None:
        """Install one internally consistent runtime configuration."""
        self.config = config
        self.audio = audio
        self._wake_mode_desired = wake_mode_desired
        if hasattr(self.queue, "config"):
            self.queue.config = config
        self.history.config = config.history

    async def _wait_for_reconfigured_session(
        self,
        previous_generation: int,
        server_config: Any,
    ) -> bool:
        """Wait until a newer generation is ready or deterministically rejected."""
        deadline = asyncio.get_running_loop().time() + (
            server_config.hello_timeout + server_config.ready_timeout + 5
        )
        while asyncio.get_running_loop().time() < deadline:
            if getattr(self.session, "configuration_blocked", False):
                return False
            if (
                getattr(self.session, "generation", 0) > previous_generation
                and self.session.is_ready
            ):
                return True
            if self.is_closing:
                return False
            await asyncio.sleep(0.05)
        return False

    async def _restore_runtime_config(
        self,
        config: AppConfig,
        audio: AudioCapture,
        wake_mode_desired: bool,
        reconfigure: Callable[..., Any],
    ) -> bool:
        """Restore and confirm the last working runtime after a failed apply."""
        if self.dictation_requested:
            stopped = await self.stop_dictation()
            if not stopped.success:
                logger.error(
                    "Could not stop failed candidate before configuration rollback: %s",
                    stopped.message,
                )

        self._install_runtime_config(config, audio, wake_mode_desired)
        await self.session_coordinator.update_config(
            config.server,
            config.event_stream,
        )
        self.feedback_engine.reconfigure_mapping(config.feedback_mappings)
        previous_generation = getattr(self.session, "generation", 0)
        try:
            await reconfigure(config.session, config.server)
        except Exception:
            logger.exception("Failed to restore previous session configuration.")
            return False

        restored = await self._wait_for_reconfigured_session(
            previous_generation,
            config.server,
        )
        if not restored:
            logger.error("Previous session configuration was not restored to READY.")
            return False

        if config.session.effective_wake_word_trigger_enabled and wake_mode_desired:
            armed = await self.start_dictation()
            if not armed.success:
                logger.error(
                    "Previous wake-word stream could not be restored: %s",
                    armed.message,
                )
                return False
        return True

    def _cancel_dictation_window(self) -> None:
        self._window_timer_token += 1
        task = self._window_timer_task
        self._window_timer_task = None
        self._window_deadline = None
        self._pending_window_extension = 0.0
        self._window_phase = DictationWindowPhase.INACTIVE
        self._cancel_timeout_warning()
        if task is not None and not task.done() and task is not asyncio.current_task():
            task.cancel()

    def _cancel_timeout_warning(self) -> None:
        self._timeout_warning_token += 1
        task = self._timeout_warning_task
        self._timeout_warning_task = None
        was_active = self._timeout_warning_active
        self._timeout_warning_active = False
        if task is not None and not task.done() and task is not asyncio.current_task():
            task.cancel()
        if was_active:
            self.report_local_feedback(
                CanonicalEventType.CLIENT_DICTATION_TIMEOUT_WARNING_CLEARED
            )

    def _schedule_timeout_warning(self, delay: float, *, phase: str) -> None:
        self._cancel_timeout_warning()
        loop = asyncio.get_running_loop()
        self._timeout_warning_token += 1
        token = self._timeout_warning_token
        generation = getattr(self.session, "generation", 0)
        session_id = self.session.state.session_id
        warning_seconds = min(
            delay,
            self.config.dictation_window.timeout_warning_seconds,
        )
        self._timeout_warning_task = loop.create_task(
            self._run_timeout_warning(
                token,
                generation,
                session_id,
                phase,
                delay,
                warning_seconds,
            )
        )

    async def _run_timeout_warning(
        self,
        token: int,
        generation: int,
        session_id: Optional[str],
        phase: str,
        delay: float,
        warning_seconds: float,
    ) -> None:
        try:
            await asyncio.sleep(max(0.0, delay - warning_seconds))
            with self._lock:
                current = (
                    token == self._timeout_warning_token
                    and generation == getattr(self.session, "generation", 0)
                    and session_id == self.session.state.session_id
                    and self._dictation_requested
                    and self._dictation_state == DictationState.ACTIVE
                )
                if current:
                    self._timeout_warning_active = True
            if not current:
                return
            self.report_local_feedback(
                CanonicalEventType.CLIENT_DICTATION_TIMEOUT_WARNING,
                {
                    "phase": phase,
                    "remainingSeconds": warning_seconds,
                },
            )
            await asyncio.sleep(warning_seconds)
            if token == self._timeout_warning_token:
                self._cancel_timeout_warning()
        except asyncio.CancelledError:
            return

    def _arm_dictation_window(
        self, phase: DictationWindowPhase, delay: float
    ) -> None:
        loop = asyncio.get_running_loop()
        old_task = self._window_timer_task
        if old_task is not None and not old_task.done() and old_task is not asyncio.current_task():
            old_task.cancel()
        self._window_timer_token += 1
        token = self._window_timer_token
        generation = getattr(self.session, "generation", 0)
        session_id = self.session.state.session_id
        self._window_phase = phase
        self._window_deadline = loop.time() + delay
        self._window_timer_task = loop.create_task(
            self._dictation_window_timeout(
                token, generation, session_id, phase, delay
            )
        )
        if phase is DictationWindowPhase.FOLLOWUP_WAIT:
            self._schedule_timeout_warning(delay, phase=phase.value)
        else:
            self._cancel_timeout_warning()
        with self._lock:
            self._status_revision += 1
        self._publish_snapshot()

    async def _dictation_window_timeout(
        self,
        token: int,
        generation: int,
        session_id: Optional[str],
        phase: DictationWindowPhase,
        delay: float,
    ) -> None:
        try:
            await asyncio.sleep(delay)
            with self._lock:
                current = (
                    token == self._window_timer_token
                    and phase == self._window_phase
                    and generation == getattr(self.session, "generation", 0)
                    and session_id == self.session.state.session_id
                    and self._dictation_requested
                    and self._dictation_state == DictationState.ACTIVE
                )
            if current:
                self._cancel_timeout_warning()
                await self.stop_dictation()
        except asyncio.CancelledError:
            return

    # -------------------------------------------------------------------
    # Lifecycle: Start & Shutdown
    # -------------------------------------------------------------------

    def start_queue(self) -> None:
        """
        Start the injection queue worker thread before accepting callbacks.
        Atomic and thread-safe.
        """
        with self._lock:
            if self._closing:
                raise RuntimeError("Cannot start controller while shutting down.")
            if self._started:
                return

            try:
                self.queue.start()
                if not self.queue.is_running():
                    raise RuntimeError("TextInjectionQueue failed to enter RUNNING state.")
                self._queue_cleanup_done = False
                self._started = True
            except Exception:
                queue_cleanup_done = False
                try:
                    self.queue.stop(timeout=1.0)
                except Exception:
                    pass
                else:
                    try:
                        queue_cleanup_done = not self.queue.is_running()
                    except Exception:
                        queue_cleanup_done = False
                self._queue_cleanup_done = queue_cleanup_done
                raise

    async def shutdown(self) -> None:
        """
        Gracefully shut down all components in deterministic order.
        Guarantees each component is stopped EXACTLY ONCE across repeated or concurrent calls.
        Shielded against caller cancellation so cleanup continues un-interrupted.
        """
        shutdown_task = None
        announce_shutdown = False
        with self._lock:
            if self._shutdown_completed:
                if self._shutdown_error:
                    raise self._shutdown_error
                return

            if self._shutdown_task is not None:
                shutdown_task = self._shutdown_task
            else:
                try:
                    loop = asyncio.get_running_loop()
                    shutdown_task = loop.create_task(self._do_shutdown())
                except RuntimeError:
                    shutdown_task = None

                self._shutdown_task = shutdown_task
                self._closing = True
                announce_shutdown = True

        if announce_shutdown:
            self._update_availability(
                AvailabilityState.SHUTTING_DOWN,
                "shutting_down",
                "Controller is shutting down",
            )

        if shutdown_task is not None:
            await asyncio.shield(shutdown_task)
            with self._lock:
                if self._shutdown_error:
                    raise self._shutdown_error
        else:
            await self._do_shutdown()

    async def _do_shutdown(self) -> None:
        self._cancel_dictation_window()
        queue_error: Optional[Exception] = None

        # Serialize teardown against every dictation transition. ``shutdown()``
        # has already set ``_closing``, so new transitions are rejected while
        # an in-flight transition is allowed to reach a consistent boundary.
        async with self._get_transition_lock():
            with self._lock:
                attempt = self._start_attempt
                self._start_attempt = None
                dictation_changed = self._dictation_state != DictationState.IDLE
                self._dictation_state = DictationState.IDLE
                self._dictation_requested = False
                if dictation_changed:
                    self._status_revision += 1

            if attempt is not None:
                if not attempt.future.done():
                    attempt.future.set_result(("shutdown", None))
                if not attempt.send_task.done():
                    attempt.send_task.cancel()
                    await asyncio.gather(
                        attempt.send_task, return_exceptions=True
                    )

            # 1. Stop audio capture
            try:
                self.audio.stop()
            except Exception as e:
                logger.error("Error stopping audio capture: %s", e)

            # 2. Stop the session-bound event WebSocket before invalidating
            # its owning transcription session.
            try:
                await self.session_coordinator.shutdown()
            except Exception as e:
                logger.error("Error stopping event session: %s", e)

            pending_coordinator_tasks = tuple(self._coordinator_tasks)
            if pending_coordinator_tasks:
                await asyncio.gather(
                    *pending_coordinator_tasks,
                    return_exceptions=True,
                )

            # 3. Stop transcription WebSocket session
            try:
                await self.session.stop()
            except Exception as e:
                logger.error("Error stopping session: %s", e)

            # 4. Stop injection queue worker thread. A failed queue start
            # already performed its own rollback and must not be stopped twice.
            with self._lock:
                queue_cleanup_done = self._queue_cleanup_done
            if not queue_cleanup_done:
                try:
                    self.queue.stop(timeout=2.0)
                    if self.queue.is_running():
                        queue_error = TimeoutError(
                            "TextInjectionQueue worker did not stop within timeout."
                        )
                        logger.error("%s", queue_error)
                except Exception as e:
                    queue_error = e
                    logger.error("Error stopping TextInjectionQueue: %s", e)
                finally:
                    with self._lock:
                        self._queue_cleanup_done = True

        # 5. Cleanup transcript history
        try:
            self.history.cleanup()
        except Exception as e:
            logger.error("Error cleaning up transcript history: %s", e)

        # The worker outlives this controller (its lifetime belongs to
        # app.py::main), so the counter source has to go with the controller.
        # Otherwise a second controller would leave the first one's counters
        # registered and the aggregate would report a dead object.
        self._unregister_audio_stats_source()

        with self._lock:
            self._started = False
            self._shutdown_completed = True
            self._shutdown_error = queue_error
            self._availability_state = AvailabilityState.STOPPED
            self._reason_code = "stopped"
            self._reason_description = "Controller is stopped"
            self._status_revision += 1

        self._publish_snapshot()

        if queue_error:
            raise queue_error

    # -------------------------------------------------------------------
    # Event Router & Final Processing
    # -------------------------------------------------------------------

    def handle_server_event(self, event_type: str, event_data: dict) -> Optional[FinalProcessingResult]:
        """
        Main entry point for raw server WebSocket events.
        Only event_type == 'final' is the authoritative source for history and auto-enqueue.
        """
        if self.is_closing:
            logger.debug("Ignoring event received during shutdown: %s", event_type)
            return None

        event_generation = event_data.get("_clientGeneration")
        if (
            event_generation is not None
            and event_generation != getattr(self.session, "generation", 0)
        ):
            logger.debug(
                "Ignoring stale server event %s from generation %s.",
                event_type,
                event_generation,
            )
            return None

        if event_type in {"status", "timeline", "final", "error"}:
            current_session_id = self.session.state.session_id
            if isinstance(current_session_id, str) and current_session_id:
                try:
                    fallback_decision = self.feedback_engine.handle_stt_fallback(
                        event_type,
                        event_data,
                        generation=getattr(self.session, "generation", 0),
                        session_id=current_session_id,
                    )
                except EventNormalizationError as exc:
                    logger.warning("Invalid STT fallback event ignored: %s", exc)
                else:
                    if fallback_decision is not None:
                        self._publish_feedback_decision(fallback_decision)

        if event_type == "hello":
            session_id = event_data.get("sessionId")
            with self._lock:
                # Persistence remains the authority for duplicate detection;
                # the fast in-memory reservation map is session-local.
                self._processed_finals = OrderedDict(
                    (key, text)
                    for key, text in self._processed_finals.items()
                    if key[0] == session_id
                )
                self._server_error_counts.clear()
            self._schedule_coordinator_operation(
                self.session_coordinator.adopt_hello(
                    event_generation
                    if isinstance(event_generation, int)
                    and not isinstance(event_generation, bool)
                    else getattr(self.session, "generation", 0),
                    dict(event_data),
                )
            )
            return None

        if event_type == "status":
            self._handle_status_event(event_data)
            return None

        if event_type == "ready":
            if event_data.get("ok") is False:
                self._update_availability(
                    AvailabilityState.SERVER_UNAVAILABLE,
                    "server_not_ready",
                    "Server is not ready",
                )
            return None

        if event_type == "timeline":
            self._handle_timeline_event(event_data)
            return None

        if event_type == "error":
            self._handle_error_event(event_data)
            return None

        if event_type != "final":
            return None

        if self._discard_finals:
            logger.info(
                "Discarding final segment %r after explicit dictation cancel.",
                event_data.get("segmentId"),
            )
            return FinalProcessingResult(
                status=FinalProcessingStatus.DEDUPLICATED,
                session_id=event_data.get("sessionId"),
                segment_id=event_data.get("segmentId"),
                reason="dictation_cancelled",
            )

        return self.process_raw_final_event(event_data)

    def _handle_timeline_event(self, event_data: dict) -> None:
        if event_data.get("sessionId") != self.session.state.session_id:
            return
        name = event_data.get("event")

        # The wake-word follow-up countdown is a *display* of a window the
        # server owns: its duration comes from the server event. It is keyed on
        # the trigger flag, not on the old operating mode.
        if self.config.session.effective_wake_word_trigger_enabled:
            if name == "wakeword_followup_started":
                duration = event_data.get("durationSeconds")
                if (
                    isinstance(duration, (int, float))
                    and not isinstance(duration, bool)
                    and math.isfinite(duration)
                    and duration > 0
                ):
                    self._schedule_timeout_warning(
                        float(duration), phase="wake_word_followup"
                    )
            elif name in {"recording_started", "wakeword_followup_timeout"}:
                self._cancel_timeout_warning()
            if not self.config.session.effective_manual_trigger_enabled:
                return

        if self._server_owns_activation:
            # The server is the activation authority. The client must not run a
            # second window that could stop a dictation the server still holds
            # open; it only mirrors what the server reports.
            if name == "activation_closed":
                self._cancel_timeout_warning()
            return

        if not self.config.session.effective_manual_trigger_enabled:
            return
        with self._lock:
            if (
                self._dictation_state != DictationState.ACTIVE
                or not self._dictation_requested
            ):
                return
        if name == "recording_started":
            self._cancel_timeout_warning()
            task = self._window_timer_task
            self._window_timer_token += 1
            self._window_timer_task = None
            self._window_deadline = None
            self._window_phase = DictationWindowPhase.SEGMENT_ACTIVE
            if task is not None and not task.done():
                task.cancel()
            with self._lock:
                self._status_revision += 1
            self._publish_snapshot()
        elif name == "recording_ended":
            with self._lock:
                if self._window_phase != DictationWindowPhase.SEGMENT_ACTIVE:
                    return
                extra = self._pending_window_extension
                self._pending_window_extension = 0.0
            self._arm_dictation_window(
                DictationWindowPhase.FOLLOWUP_WAIT,
                self.config.dictation_window.followup_timeout + extra,
            )

    def _handle_status_event(self, event_data: dict) -> None:
        event_session_id = event_data.get("sessionId")
        current_session_id = self.session.state.session_id
        if (
            current_session_id is not None
            and event_session_id != current_session_id
        ):
            logger.debug(
                "Ignoring status for stale session %r (current %r).",
                event_session_id,
                current_session_id,
            )
            return

        state = SessionState.from_server(event_data.get("state", "unknown"))
        future_to_resolve = None
        with self._lock:
            attempt = self._start_attempt
            if (
                attempt is not None
                and self._dictation_state == DictationState.STARTING
                and attempt.generation == getattr(self.session, "generation", 0)
                and state in _START_CONFIRM_STATES
            ):
                if attempt.command_sent:
                    future_to_resolve = attempt.future
                else:
                    attempt.pending_confirmation = state

            availability = self._availability_state

        if future_to_resolve is not None and not future_to_resolve.done():
            future_to_resolve.set_result(("confirmed", state))

        if (
            self.session.is_ready
            and availability == AvailabilityState.SERVER_UNAVAILABLE
            and state not in {SessionState.CLOSED, SessionState.UNKNOWN}
        ):
            self._update_availability(
                AvailabilityState.READY,
                "ready",
                "Transport and recorder are ready",
            )

    def _handle_error_event(self, event_data: dict) -> None:
        where = str(event_data.get("where") or "unknown")
        message = str(event_data.get("message") or "Server error")
        with self._lock:
            self._server_error_counts[where] = (
                self._server_error_counts.get(where, 0) + 1
            )
            count = self._server_error_counts[where]
            dictation_state = self._dictation_state

        self._observe_error_classified(where, message, count, dictation_state)

        if where == "admission":
            self._update_availability(
                AvailabilityState.SERVER_BUSY,
                "server_busy",
                "Server capacity reached",
            )
            if dictation_state in (DictationState.STARTING, DictationState.ACTIVE):
                self._handle_dictation_interrupted("server_busy")
            return

        if where in ("main_engine", "realtime_engine"):
            self._update_availability(
                AvailabilityState.SERVER_UNAVAILABLE,
                where,
                "Speech recognition engine is unavailable",
            )
            if dictation_state in (DictationState.STARTING, DictationState.ACTIVE):
                self._handle_dictation_interrupted(where)
            return

        if where == "recorder":
            self._update_availability(
                AvailabilityState.SERVER_UNAVAILABLE,
                "recorder_error",
                "Server recorder is unavailable",
            )
            if dictation_state in (DictationState.STARTING, DictationState.ACTIVE):
                self._handle_dictation_interrupted("recorder_error")
            return

        if where == "command":
            self._update_availability(
                AvailabilityState.PROTOCOL_ERROR,
                "command_error",
                "Server rejected a client command",
            )
            if dictation_state == DictationState.STARTING:
                self._reject_start_from_server_error(
                    "command_error",
                    "Server rejected the start command",
                )
            return

        if where == "session_config":
            self._update_availability(
                AvailabilityState.PROTOCOL_ERROR,
                "session_configuration_error",
                message,
            )
            if dictation_state in (
                DictationState.STARTING,
                DictationState.ACTIVE,
            ):
                self._handle_dictation_interrupted(
                    "session_configuration_error"
                )
            return

        if where == "audio_packet" and count >= 3:
            self._update_availability(
                AvailabilityState.PROTOCOL_ERROR,
                "repeated_audio_packet_error",
                "Repeated invalid audio packets",
            )
            if dictation_state in (DictationState.STARTING, DictationState.ACTIVE):
                self._handle_dictation_interrupted(
                    "repeated_audio_packet_error"
                )
            return

        if where == "audio" and count >= 3:
            self._update_availability(
                AvailabilityState.SERVER_UNAVAILABLE,
                "repeated_audio_error",
                "Repeated server audio processing errors",
            )
            if dictation_state in (DictationState.STARTING, DictationState.ACTIVE):
                self._handle_dictation_interrupted("repeated_audio_error")
            return

        logger.warning(
            "Server error classified without transport reset: where=%s count=%d message=%s",
            where,
            count,
            message,
        )

    def _observe_error_classified(
        self, where: str, message: str, count: int, dictation_state: DictationState
    ) -> None:
        """CONTRACTS §12.5: client.server.error_classified (P+S).

        What no existing log line records is the pair ``(where, count)``: the
        same ``where`` leads to a different availability state and a different
        dictation consequence depending on how often it has already been seen
        (``audio_packet`` and ``audio`` only act from the third occurrence).
        With the count and the dictation state at classification time, the
        branch this error took is reconstructable from the history — and unlike
        the existing ``logger.warning``, which only fires for the *unclassified*
        tail, this record exists for **every** classified error.

        Emitted once, at the single point all branches pass through, rather than
        once per branch: one fact, one record, and no chance of the eight
        branches drifting apart.
        """
        self._observe.system(
            "client.server.error_classified",
            level="ERROR",
            message=message,
            details={
                "where": where,
                "count": count,
                "dictation_state": dictation_state.value,
            },
            session_id=self.session.state.session_id,
            generation=getattr(self.session, "generation", 0),
        )

    def _reject_start_from_server_error(
        self, reason: str, description: str
    ) -> None:
        with self._lock:
            attempt = self._start_attempt
            if attempt is None or self._dictation_state != DictationState.STARTING:
                return
            self._start_attempt = None
            self._dictation_state = DictationState.IDLE
            self._dictation_requested = False
            self._status_revision += 1

        current_task = asyncio.current_task()
        if not attempt.send_task.done() and attempt.send_task is not current_task:
            attempt.send_task.cancel()
        if not attempt.future.done():
            attempt.future.set_result(("command_error", None))
        self.session.set_streaming(False)
        try:
            self.audio.stop()
        except Exception:
            logger.debug("Audio stop failed after command error.", exc_info=True)
        self._clear_audio_queue()
        self._publish_snapshot()
        self._emit_feedback_event(
            TransientEventType.DICTATION_START_FAILED,
            reason=reason,
            description=description,
            action="start_dictation",
        )

    def process_raw_final_event(self, event_data: dict) -> FinalProcessingResult:
        """
        Validates, deduplicates, records in history, and enqueues raw final events.
        Logically-atomically reserves identity under lock before calling history.
        """
        if self.is_closing:
            res = FinalProcessingResult(
                status=FinalProcessingStatus.INVALID_FINAL,
                session_id=event_data.get("sessionId"),
                segment_id=event_data.get("segmentId"),
                text=event_data.get("text"),
                reason="closing",
                error="Controller is shutting down",
            )
            self._emit_final_result(res)
            return res

        # 1. Field validation
        session_id = event_data.get("sessionId")
        segment_id = event_data.get("segmentId")
        text = event_data.get("text")

        is_valid_session = isinstance(session_id, str) and bool(session_id.strip())
        is_valid_segment = (
            isinstance(segment_id, int)
            and not isinstance(segment_id, bool)
            and segment_id >= 0
        )
        is_valid_text = isinstance(text, str) and bool(text.strip())

        if not (is_valid_session and is_valid_segment and is_valid_text):
            logger.warning(
                "Invalid final event fields: sessionId=%r, segmentId=%r, text=%r",
                session_id, segment_id, text
            )
            res = FinalProcessingResult(
                status=FinalProcessingStatus.INVALID_FINAL,
                session_id=session_id if isinstance(session_id, str) else None,
                segment_id=segment_id if isinstance(segment_id, int) and not isinstance(segment_id, bool) else None,
                text=text if isinstance(text, str) else None,
                reason="validation_failed",
                error="Invalid sessionId, segmentId, or text in final event",
            )
            self._emit_final_result(res)
            return res

        clean_session_id = session_id.strip()
        clean_text = text.strip()
        key = (clean_session_id, segment_id)

        # 2. Logically-atomic key reservation under lock BEFORE calling history
        closing_res = None
        dup_res = None
        with self._lock:
            # Recheck closing atomically with identity reservation. Shutdown
            # may have started while the event fields were being validated.
            if self._closing:
                closing_res = FinalProcessingResult(
                    status=FinalProcessingStatus.INVALID_FINAL,
                    session_id=clean_session_id,
                    segment_id=segment_id,
                    text=clean_text,
                    reason="closing",
                    error="Controller is shutting down",
                )
            elif key in self._processed_finals:
                existing_text = self._processed_finals[key]
                self._processed_finals.move_to_end(key)
                is_conflict = (existing_text != clean_text)
                if is_conflict:
                    logger.warning(
                        "Contradictory duplicate final event for %s: existing=%r, new=%r",
                        key, existing_text, clean_text
                    )
                else:
                    logger.info("Identical duplicate final event for %s ignored.", key)

                dup_res = FinalProcessingResult(
                    status=FinalProcessingStatus.DEDUPLICATED,
                    session_id=clean_session_id,
                    segment_id=segment_id,
                    text=clean_text,
                    reason="duplicate",
                    is_conflict=is_conflict,
                )
            else:
                # Reserve key immediately under lock
                self._remember_final_identity_locked(key, clean_text)

        if closing_res is not None:
            self._emit_final_result(closing_res)
            return closing_res

        if dup_res is not None:
            self._emit_final_result(dup_res)
            return dup_res

        # 3. History-before-enqueue via add_entry_with_status
        try:
            hist_res = self.history.add_entry_with_status(clean_session_id, segment_id, clean_text)
        except Exception as e:
            logger.error("Failed to add history entry for %s: %s", key, e, exc_info=True)
            hist_res = HistoryAddResult(entry=None, status=HistoryAddStatus.UNAVAILABLE)

        if hist_res.status == HistoryAddStatus.UNAVAILABLE:
            logger.warning("HistoryEntry unavailable for %s. Auto-enqueue skipped.", key)
            res = FinalProcessingResult(
                status=FinalProcessingStatus.HISTORY_UNAVAILABLE,
                session_id=clean_session_id,
                segment_id=segment_id,
                text=clean_text,
                reason="history_unavailable",
                error="Failed to create or resolve HistoryEntry",
            )
            self._emit_final_result(res)
            return res

        if hist_res.status == HistoryAddStatus.ALREADY_EXISTS:
            if hist_res.entry is None:
                # Evicted duplicate from memory/DB retention limit
                logger.info("Duplicate final event for %s (entry evicted from retention).", key)
                res = FinalProcessingResult(
                    status=FinalProcessingStatus.DEDUPLICATED,
                    session_id=clean_session_id,
                    segment_id=segment_id,
                    text=clean_text,
                    reason="duplicate_entry_evicted",
                    is_conflict=False,
                )
                self._emit_final_result(res)
                return res
            else:
                existing_text = hist_res.entry.text
                is_conflict = (existing_text != clean_text)
                with self._lock:
                    self._remember_final_identity_locked(key, existing_text)

                if is_conflict:
                    logger.warning(
                        "Contradictory pre-existing history entry for %s: existing=%r, new=%r",
                        key, existing_text, clean_text
                    )
                else:
                    logger.info("Identical pre-existing history entry for %s resolved.", key)

                res = FinalProcessingResult(
                    status=FinalProcessingStatus.DEDUPLICATED,
                    session_id=clean_session_id,
                    segment_id=segment_id,
                    text=existing_text,
                    entry_id=hist_res.entry.id,
                    reason="preexisting_duplicate",
                    is_conflict=is_conflict,
                )
                self._emit_final_result(res)
                return res

        # Entry is NEW
        entry = hist_res.entry

        # 4. Enqueue to TextInjectionQueue
        try:
            enqueued = self.queue.enqueue(entry)
        except Exception as e:
            logger.exception("Enqueue exception for %s: %s", key, e)
            try:
                self.history.record_injection_attempt(entry.id, status="failed", error=str(e))
            except Exception as att_err:
                logger.error("Failed to record attempt for %s: %s", entry.id, att_err)

            res = FinalProcessingResult(
                status=FinalProcessingStatus.FAILED,
                session_id=clean_session_id,
                segment_id=segment_id,
                text=clean_text,
                entry_id=entry.id,
                reason="enqueue_exception",
                error=str(e),
            )
            self._emit_final_result(res)
            return res

        if not enqueued:
            logger.warning("Injection queue rejected entry for %s (not running/stopping)", key)
            try:
                self.history.record_injection_attempt(entry.id, status="skipped", error="Queue unavailable")
            except Exception as att_err:
                logger.error("Failed to record attempt for %s: %s", entry.id, att_err)

            res = FinalProcessingResult(
                status=FinalProcessingStatus.QUEUE_UNAVAILABLE,
                session_id=clean_session_id,
                segment_id=segment_id,
                text=clean_text,
                entry_id=entry.id,
                reason="queue_unavailable",
                error="TextInjectionQueue is not running or rejected job",
            )
            self._emit_final_result(res)
            return res

        # 5. Successfully enqueued
        logger.info("Successfully enqueued final segment %s (entry_id=%s)", key, entry.id)
        res = FinalProcessingResult(
            status=FinalProcessingStatus.QUEUED,
            session_id=clean_session_id,
            segment_id=segment_id,
            text=clean_text,
            entry_id=entry.id,
        )
        self._emit_final_result(res)
        return res

    def _observe_final_result(self, result: FinalProcessingResult) -> None:
        """CONTRACTS §12.3: the three transcription-channel hooks.

        ``client.injection.enqueued`` / ``.rejected`` and
        ``client.final.deduplicated``. The last one is marked
        **redaktionspflichtig** in §12.3 because the existing code logs both
        full texts on WARNING when they contradict each other. Here **no text
        is passed at all** — only its character count. That is stricter than
        R-10 requires (which keeps ``[redacted:<n> chars]``) and needs no
        dependency on ``store_transcription_content`` being off: the fact worth
        keeping is *that* a conflict happened and *how far apart* the two
        versions were, not what was said.
        """
        status = result.status
        if status is FinalProcessingStatus.QUEUED:
            type_ = "client.injection.enqueued"
            level = "INFO"
        elif status is FinalProcessingStatus.DEDUPLICATED:
            type_ = "client.final.deduplicated"
            level = "WARNING" if result.is_conflict else "INFO"
        elif status in {
            FinalProcessingStatus.FAILED,
            FinalProcessingStatus.QUEUE_UNAVAILABLE,
            FinalProcessingStatus.HISTORY_UNAVAILABLE,
            FinalProcessingStatus.INVALID_FINAL,
        }:
            type_ = "client.injection.rejected"
            level = "WARNING"
        else:  # pragma: no cover - the enum is closed
            return
        details: Dict[str, Any] = {
            "status": status.value,
            "reason": result.reason,
            "entry_id": result.entry_id,
            "text_length": len(result.text) if isinstance(result.text, str) else None,
        }
        if status is FinalProcessingStatus.DEDUPLICATED:
            details["conflict"] = bool(result.is_conflict)
        if result.error:
            details["error"] = result.error
        identity = result.entry_id or (
            f"{result.session_id}:{result.segment_id}:{status.value}"
        )
        self._observe.transcription(
            type_,
            level=level,
            details=details,
            session_id=result.session_id,
            generation=getattr(self.session, "generation", 0),
            segment_id=(
                result.segment_id
                if isinstance(result.segment_id, int)
                and not isinstance(result.segment_id, bool)
                and result.segment_id >= 0
                else None
            ),
            correlation_id=f"injection:{identity}",
        )

    def _remember_final_identity_locked(
        self, key: Tuple[str, int], text: str
    ) -> None:
        """Remember a recent final identity without unbounded session growth."""
        self._processed_finals[key] = text
        self._processed_finals.move_to_end(key)
        while len(self._processed_finals) > _MAX_PROCESSED_FINAL_IDENTITIES:
            self._processed_finals.popitem(last=False)

    def _emit_final_result(self, result: FinalProcessingResult) -> None:
        """Emits final result callback OUTSIDE of internal locks."""
        self._observe_final_result(result)
        if self.on_final_result:
            try:
                self.on_final_result(result)
            except Exception:
                logger.exception("Error in on_final_result callback.")
        canonical = None
        if result.status is FinalProcessingStatus.QUEUED:
            canonical = CanonicalEventType.CLIENT_INJECTION_ACCEPTED
        elif result.status in {
            FinalProcessingStatus.FAILED,
            FinalProcessingStatus.QUEUE_UNAVAILABLE,
        }:
            canonical = CanonicalEventType.CLIENT_INJECTION_FAILED
        if canonical is not None:
            identity = result.entry_id or (
                f"{result.session_id}:{result.segment_id}:{result.status.value}"
            )
            decision = self.feedback_engine.handle_local(
                canonical,
                generation=getattr(self.session, "generation", 0),
                session_id=result.session_id,
                correlation_id=f"injection:{identity}:{canonical.value}",
                details={
                    "entryId": result.entry_id,
                    "segmentId": result.segment_id,
                    "status": result.status.value,
                    "reason": result.reason,
                },
            )
            self._publish_feedback_decision(decision)

    # -------------------------------------------------------------------
    # Reinsertion API
    # -------------------------------------------------------------------

    def reinsert_last(self) -> ReinsertionResult:
        """Reinsert the most recent final transcript via ReinsertionService."""
        if self.is_closing:
            return ReinsertionResult(
                status=ReinsertionStatus.FAILED,
                reason="closing",
                error_message="Controller is shutting down",
            )
        return self.reinsertion.reinsert_last()

    def reinsert_entry(self, entry_id: str) -> ReinsertionResult:
        """Reinsert a specific transcript entry by ID via ReinsertionService."""
        if self.is_closing:
            return ReinsertionResult(
                status=ReinsertionStatus.FAILED,
                entry_id=entry_id if isinstance(entry_id, str) else None,
                reason="closing",
                error_message="Controller is shutting down",
            )
        return self.reinsertion.reinsert_entry(entry_id)

    def get_recent_entries(self, limit: Optional[int] = None) -> Tuple[HistoryEntry, ...]:
        """Retrieve recent transcript entries ordered newest first."""
        return self.reinsertion.get_recent_entries(limit)

    def delete_history_entry(self, entry_id: str) -> bool:
        return self.history.delete_entry(entry_id)

    def clear_history(self) -> int:
        return self.history.clear_entries()

    # -------------------------------------------------------------------
    # Internal Callbacks & Audio Thread Bridge
    # -------------------------------------------------------------------

    def _schedule_coordinator_operation(self, operation: Any) -> None:
        """Run one coordinator transition on the controller's asyncio loop."""
        loop = self._loop
        if loop is None or loop.is_closed() or self.is_closing:
            close = getattr(operation, "close", None)
            if close is not None:
                close()
            return
        task = loop.create_task(operation)
        self._coordinator_tasks.add(task)

        def completed(done: asyncio.Task) -> None:
            self._coordinator_tasks.discard(done)
            if done.cancelled():
                return
            try:
                error = done.exception()
            except asyncio.CancelledError:
                return
            if error is not None:
                logger.error(
                    "Session coordinator operation failed: %s",
                    error,
                    exc_info=(type(error), error, error.__traceback__),
                )

        task.add_done_callback(completed)

    async def _handle_event_stream_event(
        self,
        context: SessionContext,
        result: EventProtocolResult,
    ) -> bool:
        """Normalize/reduce one current-session event before cursor confirmation."""
        if (
            self.is_closing
            or context.generation != getattr(self.session, "generation", 0)
            or context.session_id != self.session.state.session_id
        ):
            return False
        callback = self.on_event_stream_event
        if callback is not None:
            accepted = callback(context, result)
            if inspect.isawaitable(accepted):
                accepted = await accepted
            if accepted is not True:
                return False
        decision = self.feedback_engine.handle_event_stream(
            result,
            generation=context.generation,
            session_id=context.session_id,
        )
        if decision is not None:
            self._publish_feedback_decision(decision)
        return True

    def _handle_session_context_change(self, context: SessionContext) -> None:
        decision = self.feedback_engine.update_connection(
            context.event_state,
            stt_ready=self.session.is_ready,
            generation=context.generation,
            session_id=context.session_id,
            issue=context.unavailable_code,
        )
        self._publish_feedback_decision(decision)
        callback = self.on_session_context_change
        if callback is not None:
            try:
                callback(context)
            except Exception:
                logger.exception("Error in session context callback.")

    def _handle_transport_change(self, new_state: TransportState) -> None:
        if self.is_closing:
            if self.on_transport_change:
                try:
                    self.on_transport_change(new_state)
                except Exception:
                    logger.exception("Error in transport change callback.")
            return

        generation = getattr(self.session, "generation", 0)
        if new_state == TransportState.CONNECTING:
            self._schedule_coordinator_operation(
                self.session_coordinator.begin_generation(generation)
            )
        elif new_state in (TransportState.DISCONNECTED, TransportState.ERROR):
            self._schedule_coordinator_operation(
                self.session_coordinator.invalidate_generation(generation)
            )

        if new_state in (TransportState.CONNECTING, TransportState.ADMITTED):
            self._update_availability(AvailabilityState.CONNECTING, "connecting", "Connecting to server")
        elif new_state == TransportState.READY:
            self._update_availability(AvailabilityState.READY, "ready", "Transport is ready")
        elif new_state in (TransportState.DISCONNECTED, TransportState.ERROR):
            with self._lock:
                current_availability = self._availability_state
            failure_reason = getattr(self.session, "last_failure_reason", "")
            server_busy = getattr(
                self.session,
                "is_server_busy",
                getattr(self.session, "_is_server_busy", False),
            )
            if (
                new_state == TransportState.ERROR
                and current_availability
                in {
                    AvailabilityState.SERVER_BUSY,
                    AvailabilityState.SERVER_UNAVAILABLE,
                    AvailabilityState.PROTOCOL_ERROR,
                }
            ):
                pass
            elif server_busy or failure_reason == "server_busy":
                self._update_availability(
                    AvailabilityState.SERVER_BUSY,
                    "server_busy",
                    "Server capacity reached",
                )
            elif failure_reason in {
                "server_unavailable",
                "recorder_unavailable",
                "handshake_timeout",
            }:
                self._update_availability(
                    AvailabilityState.SERVER_UNAVAILABLE,
                    failure_reason,
                    "Server is temporarily unavailable",
                )
            else:
                self._update_availability(
                    AvailabilityState.NETWORK_UNAVAILABLE,
                    failure_reason or "disconnected",
                    "Transport disconnected",
                )

            if self._dictation_state in (DictationState.STARTING, DictationState.ACTIVE):
                self._handle_dictation_interrupted("transport_loss")

        context = getattr(self.session_coordinator, "context", None)
        if isinstance(context, SessionContext):
            source_decision = self.feedback_engine.update_connection(
                context.event_state,
                stt_ready=new_state is TransportState.READY,
                generation=context.generation,
                session_id=context.session_id,
                issue=context.unavailable_code,
            )
            self._publish_feedback_decision(source_decision)

        if self.on_transport_change:
            try:
                self.on_transport_change(new_state)
            except Exception:
                logger.exception("Error in transport change callback.")

    def _handle_state_change(self, state: ClientState) -> None:
        publish_snapshot = False
        with self._lock:
            if state.server_status != self._last_published_server_status:
                self._last_published_server_status = state.server_status
                self._status_revision += 1
                publish_snapshot = True
        if publish_snapshot:
            self._publish_snapshot()
        if self.on_state_change:
            try:
                self.on_state_change(state)
            except Exception:
                logger.exception("Error in state change callback.")

    def _handle_dictation_interrupted(self, reason: str) -> None:
        self._cancel_dictation_window()
        with self._lock:
            if self._dictation_state == DictationState.IDLE:
                return
            attempt = self._start_attempt
            self._start_attempt = None
            self._dictation_state = DictationState.IDLE
            self._dictation_requested = False
            self._status_revision += 1

        logger.warning("Dictation interrupted (reason: %s).", reason)
        self.session.set_streaming(False)

        if attempt is not None:
            current_task = asyncio.current_task()
            if (
                not attempt.send_task.done()
                and attempt.send_task is not current_task
            ):
                attempt.send_task.cancel()
            if not attempt.future.done():
                attempt.future.set_result(("interrupted", None))

        try:
            self.audio.stop()
        except Exception:
            pass

        self._clear_audio_queue()
        self._publish_snapshot()

        self._emit_feedback_event(
            TransientEventType.DICTATION_INTERRUPTED,
            reason=reason,
            description="Dictation interrupted by transport loss",
            action="dictation",
        )

    def _handle_session_text(self, segment_id: int, text: str, is_final: bool) -> None:
        if self.on_text:
            try:
                self.on_text(segment_id, text, is_final)
            except Exception:
                logger.exception("Error in text callback.")

    def _on_audio_packet_from_thread(
        self, pcm_data: bytes, sample_rate: int, channels: int, frames: int
    ) -> None:
        """Schedules audio packet handoff from recording thread to async event loop."""
        loop = self._loop
        if loop is None or loop.is_closed():
            return

        with self._lock:
            if (
                not self.session.is_streaming
                or self._dictation_state != DictationState.ACTIVE
            ):
                return
            generation = getattr(self.session, "generation", 0)

        try:
            loop.call_soon_threadsafe(
                self._enqueue_audio_packet,
                (pcm_data, sample_rate, channels, frames, generation),
            )
        except RuntimeError:
            pass

    def _enqueue_audio_packet(
        self, packet: Tuple[Any, ...]
    ) -> None:
        """Enqueues audio packet on loop thread."""
        if len(packet) != 5:
            return
        pcm, sr, ch, fr, gen = packet

        with self._lock:
            if (
                not self.session.is_streaming
                or self._dictation_state != DictationState.ACTIVE
            ):
                return
            if gen != getattr(self.session, "generation", 0):
                return
        try:
            self._audio_send_queue.put_nowait((pcm, sr, ch, fr, gen))
        except asyncio.QueueFull:
            # ARCH §8.6: hot path -- int increment only, no log line.
            self.chunks_dropped_send_queue += 1
            return
        depth = self._audio_send_queue.qsize()
        if depth > self.max_send_queue_depth:
            self.max_send_queue_depth = depth

    def _clear_audio_queue(self) -> None:
        """Empties pending audio packets."""
        while not self._audio_send_queue.empty():
            try:
                self._audio_send_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

    async def _audio_sender(self) -> None:
        """Drains audio queue and sends to WebSocket."""
        while True:
            (
                pcm_data,
                sample_rate,
                channels,
                frames,
                generation,
            ) = await self._audio_send_queue.get()
            try:
                with self._lock:
                    can_send = (
                        self._dictation_state == DictationState.ACTIVE
                        and self.session.is_streaming
                        and generation == getattr(self.session, "generation", 0)
                    )
                if not can_send:
                    continue
                await self.session.send_audio(pcm_data, sample_rate, channels, frames)
            except Exception:
                logger.debug("Audio send error", exc_info=True)

    async def _auto_start_when_ready(self) -> None:
        """Initial headless auto-start when server is ready (executed at most once on startup)."""
        while True:
            await asyncio.sleep(0.05)
            if self.is_closing:
                return
            if self._initial_auto_start_done:
                return
            if self.session.is_ready:
                async with self._get_transition_lock():
                    if self._initial_auto_start_done:
                        return
                    if not self._initial_auto_start_requested:
                        self._initial_auto_start_done = True
                        return
                    if not self.session.is_ready:
                        continue
                    logger.info("Initial headless auto-start – starting dictation.")
                    self._initial_auto_start_requested = False
                    self._initial_auto_start_done = True
                    immediate, attempt = self._begin_start_locked()
                if immediate is not None:
                    if not immediate.success:
                        raise RuntimeError(f"Auto-start failed: {immediate.message}")
                    return
                assert attempt is not None
                res = await self._await_start_attempt(attempt)
                if not res.success:
                    logger.warning(
                        "Initial headless auto-start did not complete: %s",
                        res.message,
                    )
                return

    async def _maintain_wake_word_mode(self) -> None:
        """Persistently re-arm wake-word streaming across modes and reconnects."""
        while True:
            await asyncio.sleep(0.1)
            if (
                self.is_closing
                or self._wake_maintenance_suspended
                or not self.config.session.effective_wake_word_trigger_enabled
            ):
                continue
            if (
                self._wake_mode_desired
                and self.session.is_ready
                and not self.dictation_requested
            ):
                result = await self.start_dictation()
                if not result.success:
                    logger.info(
                        "Wake-word background stream not armed yet: %s",
                        result.status,
                    )
                    await asyncio.sleep(1.0)

    # -------------------------------------------------------------------
    # Main Async Run Loop
    # -------------------------------------------------------------------

    async def run(self) -> None:
        """Start all components and run until session finishes or is cancelled."""
        self._loop = asyncio.get_running_loop()
        tasks: List[asyncio.Task] = []

        try:
            self.start_queue()

            # CONTRACTS §12.1: client.controller.run_started (S). After
            # ``start_queue()``, because a controller whose injection queue
            # refused to start never ran -- the failure surfaces as the
            # exception this line is deliberately placed behind.
            self._observe.system(
                "client.controller.run_started",
                details={
                    "operating_mode": self.config.session.presentation_mode,
                    "wake_word_enabled": (
                        self.config.session.effective_wake_word_trigger_enabled
                    ),
                    "manual_trigger_enabled": (
                        self.config.session.effective_manual_trigger_enabled
                    ),
                },
            )

            session_task = asyncio.create_task(self.session.run())
            tasks.append(session_task)

            audio_sender_task = asyncio.create_task(self._audio_sender())
            tasks.append(audio_sender_task)

            auto_start_task = asyncio.create_task(self._auto_start_when_ready())
            tasks.append(auto_start_task)

            wake_mode_task = asyncio.create_task(
                self._maintain_wake_word_mode(),
                name="wake-word-maintainer",
            )
            tasks.append(wake_mode_task)

            monitored_tasks = set(tasks)
            while monitored_tasks:
                done, pending = await asyncio.wait(
                    monitored_tasks,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in done:
                    monitored_tasks.remove(task)
                    if task.cancelled():
                        if task == session_task:
                            monitored_tasks.clear()
                            break
                        raise RuntimeError(
                            f"Helper task {task.get_name()!r} was cancelled unexpectedly."
                        )

                    task_error = task.exception()
                    if task == auto_start_task:
                        if task_error is not None:
                            logger.error("Auto-start task failed: %s", task_error)
                            raise task_error
                    elif task == session_task:
                        if task_error is not None:
                            logger.error("Session run task failed: %s", task_error)
                            raise task_error
                        monitored_tasks.clear()
                        break
                    else:
                        if task_error is not None:
                            logger.error("Helper task failed: %s", task_error)
                            raise task_error
                        else:
                            logger.warning("Helper task %s finished unexpectedly.", task)
                            raise RuntimeError(f"Helper task {task} finished unexpectedly.")
        except asyncio.CancelledError:
            pass
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            try:
                await self.shutdown()
            finally:
                self._loop = None
