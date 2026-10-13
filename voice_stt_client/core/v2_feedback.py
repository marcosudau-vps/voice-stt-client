"""Immutable V2 presentation and callback adapter for the existing engine.

No commands, timers, I/O or second lifecycle authority. The owner calls from
the core loop; Qt receives snapshots through its normal queued signal port.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from heapq import nlargest

from . import protocol_v2 as p
from .activation_mirror import Deadline, MirrorState, MirrorView, SEGMENT_TERMINALS
from .event_models import CanonicalEventType, EventConnectionState


@dataclass(frozen=True)
class SegmentPreview:
    activation_id: str
    segment_id: str
    sequence: int
    text: str = field(repr=False)


@dataclass(frozen=True)
class FeedbackSnapshot:
    generation: int
    session_id: str
    revision: int
    phase: p.InputPhase
    activation_id: str | None
    primary_source: str | None  # diagnostic only; never a style/mapping selector
    availability: str
    audio_available: bool
    manual_available: bool
    manual_suppressed: bool
    wake_suppressed: bool
    pending_count: int
    incomplete: bool
    diagnostics: tuple[str, ...]
    previews: tuple[SegmentPreview, ...] = field(repr=False)
    deadline: Deadline | None = None
    watchdog: Deadline | None = None

    def remaining_ms(self, now: float) -> int | None:
        deadline = self.watchdog or self.deadline
        return None if deadline is None else deadline.remaining(now)


PHASE_KEYS = {
    p.InputPhase.IDLE: CanonicalEventType.SERVER_INPUT_IDLE,
    p.InputPhase.WAITING_FIRST_SPEECH: CanonicalEventType.SERVER_INPUT_WAITING,
    p.InputPhase.SEGMENT_ACTIVE: CanonicalEventType.SERVER_RECORDING_STARTED,
    p.InputPhase.FOLLOWUP_WAIT: CanonicalEventType.SERVER_INPUT_FOLLOWUP,
    p.InputPhase.CLOSING_INPUT: CanonicalEventType.SERVER_INPUT_CLOSING,
}


def project_feedback(view: MirrorView, revision: int, *, log_state: EventConnectionState,
                     issues: tuple[str, ...] = ()) -> FeedbackSnapshot:
    """Bounded display copies; original result text remains in mirror/history."""
    diagnostics = list(issues)
    if view.state in (MirrorState.RESYNCING, MirrorState.RECONNECT_REQUIRED):
        diagnostics.append("resync")
    if view.incomplete:
        diagnostics.append("incomplete")
    if not view.audio_available:
        diagnostics.append("device_off")
    if log_state != EventConnectionState.LIVE:
        diagnostics.append("log_unavailable")
    suppressed = view.trigger.get("suppressed", {})
    if suppressed.get("manual"):
        diagnostics.append("manual_suppressed")
    if suppressed.get("wakeWord"):
        diagnostics.append("wake_suppressed")
    visible_segments = nlargest(128, (s for s in view.segments.values()
        if s.preview and s.status not in SEGMENT_TERMINALS and s.status != "terminal_unknown"),
        key=lambda s: s.sequence)
    previews = tuple(SegmentPreview(s.activation_id, s.segment_id, s.sequence, s.preview[:16384])
                     for s in visible_segments)
    active = view.activations.get(view.input.activation_id)
    return FeedbackSnapshot(
        view.generation, view.session_id, revision, view.input.phase, view.input.activation_id,
        view.input.primary_source, view.state.value, view.audio_available, view.manual_available,
        bool(suppressed.get("manual")), bool(suppressed.get("wakeWord")),
        sum(a.input_closed and a.status == "draining" for a in view.activations.values()),
        view.incomplete, tuple(dict.fromkeys(diagnostics)), previews, view.input.deadline,
        active.watchdog if active and view.input.phase == p.InputPhase.SEGMENT_ACTIVE
        and active.status not in ("completed", "cancelled", "failed") else None,
    )


class V2FeedbackConnection:
    """Attach after Controls/Results; preserve prior reduction callback order.

    install before transport.run. close detaches this port; it never stops the
    transport or touches audio. Consumers receive one persistent decision then
    deduplicated impulses, all carrying the same post-reduction snapshot.
    """
    def __init__(self, mirror, engine, *, observability=None):
        self.mirror, self.engine = mirror, engine
        self.on_decision = None
        self._closed = False
        self._previous = mirror.on_reduction
        self._previous_observation = engine.on_observation
        self._observation_callback = None
        if observability is not None:
            from .observability.adapters.client_events import ClientEventEmitter
            self._emitter = ClientEventEmitter(observability, component="core.feedback")
            self._observation_callback = self._emitter.system
            engine.on_observation = self._observation_callback

        def reduced(reduction):
            if self._previous:
                self._previous(reduction)
            if not self._closed:
                for decision in engine.handle_reduction(reduction):
                    self._publish(decision)
        self._callback = reduced
        mirror.on_reduction = reduced

    def _publish(self, decision):
        if self.on_decision:
            try:
                self.on_decision(decision)
            except Exception:
                # A downstream UI/adapter cannot fail the receiver/audio path.
                self.engine.adapter_failures += 1

    def close(self):
        self._closed = True
        if self.mirror.on_reduction is self._callback:
            self.mirror.on_reduction = self._previous
        if self._observation_callback is not None and self.engine.on_observation is self._observation_callback:
            self.engine.on_observation = self._previous_observation
