"""Pure, session-bound server projection. Effects are data, never UI/I/O calls.

The owning core loop supplies monotonic receipt times. Snapshots repair only
snapshot domains; segment payloads and first-terminal guards survive resync.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from enum import StrEnum
import hashlib
import json
from types import MappingProxyType
from typing import Any

from . import protocol_v2 as p


def freeze(value):
    if isinstance(value, Mapping):
        return MappingProxyType({key: freeze(item) for key, item in value.items()})
    if isinstance(value, (tuple, list)):
        return tuple(freeze(item) for item in value)
    return value


EMPTY = MappingProxyType({})
SEGMENT_TERMINALS = frozenset(("completed", "discarded", "failed"))
ACTIVATION_TERMINALS = frozenset(("completed", "cancelled", "failed"))
SEGMENT_EVENTS = frozenset((p.EventType.RECORDING_STARTED, p.EventType.RECORDING_ENDED,
                           p.EventType.TRANSCRIPTION_ACCEPTED, p.EventType.INTERIM,
                           p.EventType.COMPLETED, p.EventType.DISCARDED, p.EventType.FAILED))
SESSION_EVENTS = frozenset((p.EventType.TRIGGER_SUPPRESSED, p.EventType.WAKE_AVAILABILITY,
                           p.EventType.SETTINGS_CHANGED))


class MirrorState(StrEnum):
    DISCONNECTED = "disconnected"
    READY = "ready"
    RESYNCING = "resyncing"
    RECONNECT_REQUIRED = "reconnect_required"


@dataclass(frozen=True)
class Deadline:
    unix_ms: int
    remaining_ms: int
    received_at: float

    def remaining(self, now: float) -> int:
        return max(0, self.remaining_ms - int(max(0, now - self.received_at) * 1000))


@dataclass(frozen=True)
class InputView:
    phase: p.InputPhase = p.InputPhase.IDLE
    activation_id: str | None = None
    primary_source: str | None = None
    deadline: Deadline | None = None
    close_requested: bool = False


@dataclass(frozen=True)
class ActivationView:
    activation_id: str
    sequence: int | None = None
    primary_source: str | None = None
    effective_settings: Mapping[str, Any] = field(default_factory=lambda: EMPTY, repr=False)
    input_closed: bool = False
    close_reason: str | None = None
    caused_by_command_id: str | None = None
    status: str = "open"
    accepted_count: int = 0
    terminal_count: int = 0
    incomplete: bool = False
    reason: str | None = None
    wake_word_id: str | None = None
    watchdog: Deadline | None = None


@dataclass(frozen=True)
class SegmentView:
    activation_id: str
    segment_id: str
    sequence: int
    status: str = "recording"
    preview: str | None = field(default=None, repr=False)
    text: str | None = field(default=None, repr=False)
    reason: str | None = None
    event_id: str | None = None
    event_seq: int | None = None


@dataclass(frozen=True)
class FinalResult:
    session_id: str
    activation_id: str
    segment_id: str
    segment_sequence: int
    text: str = field(repr=False)
    event_id: str
    event_seq: int


@dataclass(frozen=True)
class MirrorView:
    generation: int | None
    session_id: str | None
    state: MirrorState
    state_version: int
    last_event_seq: int
    settings_revision: int
    input: InputView
    activations: Mapping[str, ActivationView]
    segments: Mapping[str, SegmentView]
    trigger: Mapping[str, Any]
    audio_available: bool
    requested_settings: Mapping[str, Any] = field(repr=False)
    effective_settings: Mapping[str, Any] = field(repr=False)
    capabilities: Mapping[str, Any]
    incomplete: bool
    loss_reasons: tuple[str, ...]
    snapshot_pending: bool

    @property
    def operations_ready(self) -> bool:
        return self.state == MirrorState.READY

    @property
    def manual_available(self) -> bool:
        return (self.operations_ready and self.input.phase == p.InputPhase.IDLE
                and self.audio_available and self.trigger.get("effective", {}).get("manual", False))


@dataclass(frozen=True)
class Reduction:
    view: MirrorView
    finals: tuple[FinalResult, ...] = ()
    events: tuple[p.Event, ...] = ()
    effects: tuple[str, ...] = ()


@dataclass(frozen=True)
class MirrorLimits:
    max_events: int = 512
    max_bytes: int = 4 * 1024 * 1024
    snapshot_timeout: float = 5
    snapshot_attempts: int = 2
    retained_activations: int = 64
    max_records: int = 1024

    def __post_init__(self):
        if any(type(x) is not int or x < 1 for x in
               (self.max_events, self.max_bytes, self.snapshot_attempts,
                self.retained_activations, self.max_records)):
            raise ValueError("invalid mirror bounds")
        if self.retained_activations > self.max_records:
            raise ValueError("retention exceeds record budget")
        if (type(self.snapshot_timeout) not in (int, float)
                or not 0 < self.snapshot_timeout < float("inf")):
            raise ValueError("invalid snapshot timeout")


class ActivationMirror:
    """Deterministic reducer; public views own immutable copies of all maps.

    Call begin once on admission, consume only decoded events/snapshots, tick
    while snapshot_pending, and disconnect on binding loss. Ack is never state.
    Settled prefixes are compacted into session sequence watermarks. Unresolved
    records never expire by age; an exhausted record budget fails visibly.
    """

    def __init__(self, limits: MirrorLimits | None = None):
        self.limits = limits or MirrorLimits()
        self.generation = self.session_id = None
        self._reset()

    def _reset(self):
        self.state = MirrorState.DISCONNECTED
        self.state_version = self.last_event_seq = self.settings_revision = 0
        self.input = InputView()
        self.activations: dict[str, ActivationView] = {}
        self.segments: dict[str, SegmentView] = {}
        self.trigger = self.requested = self.effective = self.capabilities = EMPTY
        self.audio_available = False
        self._seen: dict[str, str] = {}
        self._sequences: dict[int, str] = {}
        self._buffer: dict[int, tuple[p.Event, float, int]] = {}
        self._buffer_bytes = 0
        self._deadline: float | None = None
        self._attempts = 0
        self._loss: set[str] = set()
        self._retired_activation_sequence = 0
        self._retired_segment_sequence = 0

    @property
    def view(self) -> MirrorView:
        return MirrorView(self.generation, self.session_id, self.state, self.state_version,
                          self.last_event_seq, self.settings_revision, self.input,
                          MappingProxyType(dict(self.activations)), MappingProxyType(dict(self.segments)),
                          self.trigger, self.audio_available, self.requested, self.effective,
                          self.capabilities, bool(self._loss) or any(a.incomplete for a in self.activations.values()),
                          tuple(sorted(self._loss)), self._deadline is not None)

    def _result(self, finals=(), events=(), effects=()):
        return Reduction(self.view, tuple(finals), tuple(events), tuple(dict.fromkeys(effects)))

    def _retain(self, finals):
        # Only retire a settled *prefix*. A late final, missing lifecycle or
        # unknown outcome pins everything behind it rather than losing guards.
        if self.state != MirrorState.READY or self._buffer:
            return
        ordered = sorted(self.activations.values(), key=lambda a: a.sequence or 0)
        publishing = {final.activation_id for final in finals}
        for a in ordered[:-self.limits.retained_activations]:
            segments = [s for s in self.segments.values() if s.activation_id == a.activation_id]
            if (a.activation_id in publishing or a.sequence is None
                    or a.status not in ACTIVATION_TERMINALS or a.incomplete
                    or not a.input_closed or self.input.activation_id == a.activation_id
                    or (a.status in ("cancelled", "failed") and not segments)
                    or any(s.status not in SEGMENT_TERMINALS for s in segments)
                    or len(segments) < max(a.accepted_count, a.terminal_count)):
                break
            ceiling = max((s.sequence for s in segments), default=self._retired_segment_sequence)
            # Segment sequences are session-global. Do not cross another
            # activation's still-held segment, even on a malformed ordering.
            if any(s.activation_id != a.activation_id and s.sequence <= ceiling for s in self.segments.values()):
                break
            self._retired_activation_sequence = max(self._retired_activation_sequence, a.sequence)
            self._retired_segment_sequence = max(self._retired_segment_sequence, ceiling)
            del self.activations[a.activation_id]
            for s in segments:
                del self.segments[s.segment_id]
                del self._sequences[s.sequence]

    def _remember(self, event_id, fingerprint):
        self._seen[event_id] = fingerprint
        # Buffered fingerprints must survive until snapshot salvage. The
        # consumed prefix is guarded permanently by last_event_seq instead.
        protected = {event.eventId for event, _, _ in self._buffer.values()}
        for key in tuple(self._seen):
            if len(self._seen) <= self.limits.max_records + len(protected):
                break
            if key not in protected:
                del self._seen[key]

    def _bounded_result(self, finals=(), events=(), effects=()):
        self._retain(finals)
        if max(len(self.activations), len(self.segments)) > self.limits.max_records:
            return self._fail("session_retention_overflow")
        return self._result(finals, events, effects)

    def _current(self, generation, session_id):
        return (generation == self.generation and session_id == self.session_id
                and self.state not in (MirrorState.DISCONNECTED, MirrorState.RECONNECT_REQUIRED))

    def begin(self, generation: int, snapshot: p.Snapshot, now: float) -> Reduction:
        if type(generation) is not int or generation < 1:
            raise ValueError("invalid generation")
        if self.generation is not None and generation <= self.generation:
            return self._result()
        self._reset()
        self.generation, self.session_id = generation, snapshot.sessionId
        self.state = MirrorState.READY
        return self.consume(generation, snapshot, now)

    def disconnect(self, generation: int) -> Reduction:
        if generation != self.generation or self.state == MirrorState.DISCONNECTED:
            return self._result()
        self._mark_loss("transport_lost")
        self.state = MirrorState.DISCONNECTED
        self._clear_wait()
        # Foreground was interrupted, never resumed in the new session.
        self.input = InputView()
        return self._result(effects=("interrupted",))

    def _clear_wait(self):
        self._deadline = None
        self._attempts = 0
        self._buffer.clear()
        self._buffer_bytes = 0

    def _request_snapshot(self, now, *, resync=False):
        if resync:
            self.state = MirrorState.RESYNCING
        if self._deadline is not None:
            return ()
        self._attempts = 1
        self._deadline = now + self.limits.snapshot_timeout
        return ("snapshot_required",)

    def clarify(self, generation: int, now: float) -> Reduction:
        if not self._current(generation, self.session_id):
            return self._result()
        return self._result(effects=self._request_snapshot(now))

    def protocol_fault(self, generation: int, now: float) -> Reduction:
        if not self._current(generation, self.session_id):
            return self._result()
        return self._result(effects=("protocol_fault", *self._request_snapshot(now, resync=True)))

    def tick(self, generation: int, now: float) -> Reduction:
        if not self._current(generation, self.session_id) or self._deadline is None or now < self._deadline:
            return self._result()
        if self._attempts >= self.limits.snapshot_attempts:
            return self._fail("snapshot_timeout")
        self._attempts += 1
        self._deadline = now + self.limits.snapshot_timeout
        return self._result(effects=("snapshot_required",))

    def snapshot_wait(self, now: float) -> float | None:
        """Monotonic remaining wait for an asyncio timer; never a domain timer."""
        return None if self._deadline is None else max(0, self._deadline - now)

    def _mark_loss(self, reason):
        for key, a in tuple(self.activations.items()):
            if a.status not in ACTIVATION_TERMINALS:
                self.activations[key] = replace(a, status="terminal_unknown", input_closed=True,
                                                incomplete=True, reason=reason)
        for key, s in tuple(self.segments.items()):
            if s.status not in SEGMENT_TERMINALS:
                self.segments[key] = replace(s, status="terminal_unknown", preview=None, reason=reason)
        if self.activations or self.segments:
            self._loss.add(reason)

    def _fail(self, reason):
        self._mark_loss(reason)
        self._loss.add(reason)
        self.state = MirrorState.RECONNECT_REQUIRED
        self._clear_wait()
        return self._result(effects=("incomplete", "reconnect_required"))

    def consume(self, generation: int, message: p.Event | p.Snapshot, now: float) -> Reduction:
        if not self._current(generation, message.sessionId):
            return self._result()
        if isinstance(message, p.Snapshot):
            return self._snapshot(message, now)
        wire = json.dumps(message.to_mapping(), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        fingerprint = hashlib.sha256(wire.encode("utf-8")).hexdigest()
        seen = self._seen.get(message.eventId)
        if seen is not None and seen != fingerprint:
            return self.protocol_fault(generation, now)
        if message.eventSeq <= self.last_event_seq:
            return self._result()
        if seen is not None:
            return self._result()
        if message.eventSeq in self._buffer:
            return self.protocol_fault(generation, now)
        if self.state == MirrorState.RESYNCING or message.eventSeq != self.last_event_seq + 1:
            effects = self._request_snapshot(now, resync=True)
            size = len(wire.encode("utf-8"))
            if len(self._buffer) >= self.limits.max_events or self._buffer_bytes + size > self.limits.max_bytes:
                return self._fail("resync_overflow")
            self._buffer[message.eventSeq] = (message, now, size)
            self._remember(message.eventId, fingerprint)
            self._buffer_bytes += size
            return self._result(effects=effects)
        self._remember(message.eventId, fingerprint)
        finals, effects = [], []
        if not self._reduce(message, now, finals, effects):
            effects.extend(self._request_snapshot(now, resync=True))
            return self._result(effects=effects)
        self.last_event_seq = message.eventSeq
        self.state_version = max(self.state_version, message.stateVersion)
        return self._bounded_result(finals, () if "retired_event" in effects else (message,), effects)

    def _activation(self, key):
        return self.activations.setdefault(key, ActivationView(key))

    def _deadline_view(self, data, now):
        if data.get("deadlineAtUnixMs") is None or data.get("remainingMs") is None:
            return None
        return Deadline(data["deadlineAtUnixMs"], data["remainingMs"], now)

    def _retired(self, event):
        return ((event.type in SEGMENT_EVENTS
                 and event.payload["segmentSequence"] <= self._retired_segment_sequence)
                or (event.type == p.EventType.ACTIVATION_STARTED
                    and event.payload["activationSequence"] <= self._retired_activation_sequence))

    def _reduce(self, event, now, finals, effects, *, historical=False):
        d, kind = event.payload, event.type
        if isinstance(event, p.UnknownEvent):
            effects.append("unknown_event")
            return True
        aid = None if kind in SESSION_EVENTS else d.get("activationId")
        if self._retired(event):
            effects.append("retired_event")
            return True
        # After compaction, unknown lifecycle IDs cannot safely be recreated:
        # they may name a retired cancelled activation. Snapshot salvage is
        # still allowed to recover payloads whose start was genuinely lost.
        if (aid and aid not in self.activations and self._retired_activation_sequence
                and kind != p.EventType.ACTIVATION_STARTED and not historical):
            effects.append("unknown_activation_after_retention")
            return False
        # Validate stable segment ownership before creating any activation.
        # A protocol finding must not leave a partially accepted phantom ID.
        if kind in SEGMENT_EVENTS:
            existing = self.segments.get(d["segmentId"])
            owner = self._sequences.get(d["segmentSequence"])
            if (existing and (existing.activation_id != aid or existing.sequence != d["segmentSequence"])
                    or owner not in (None, d["segmentId"])):
                effects.append("segment_identity_conflict")
                return False
        a = self._activation(aid) if aid else None
        if kind == p.EventType.ACTIVATION_STARTED:
            if (a.sequence is not None and a.sequence != d["activationSequence"]
                    or a.primary_source is not None and a.primary_source != d["primarySource"]):
                effects.append("activation_identity_conflict")
                return False
            self.activations[aid] = replace(a, sequence=d["activationSequence"], primary_source=d["primarySource"],
                                            effective_settings=a.effective_settings or freeze(d["effectiveSettings"]))
            if not historical and a.status not in ACTIVATION_TERMINALS and not a.input_closed:
                old = self.activations.get(self.input.activation_id)
                if old and old.activation_id != aid:
                    self.activations[old.activation_id] = replace(old, input_closed=True, status=(
                        old.status if old.status in ACTIVATION_TERMINALS else "draining"))
                self.input = InputView(p.InputPhase.WAITING_FIRST_SPEECH, aid, d["primarySource"])
                effects.extend(self._request_snapshot(now))
        elif kind == p.EventType.PHASE_CHANGED and not historical:
            if aid == self.input.activation_id:
                phase = p.InputPhase(d["inputPhase"])
                self.input = (InputView() if phase == p.InputPhase.IDLE else
                              replace(self.input, phase=phase, deadline=self._deadline_view(d, now),
                                      close_requested=phase == p.InputPhase.CLOSING_INPUT))
        elif kind == p.EventType.INPUT_CLOSED and not historical:
            self.activations[aid] = replace(a, input_closed=True, close_reason=d["reason"],
                                            caused_by_command_id=d["causedByCommandId"],
                                            accepted_count=max(a.accepted_count, d["acceptedSegmentCount"]),
                                            status=a.status if a.status in ACTIVATION_TERMINALS else "draining")
            if aid == self.input.activation_id:
                self.input = InputView()
        elif kind in (p.EventType.ACTIVATION_COMPLETED, p.EventType.ACTIVATION_CANCELLED, p.EventType.ACTIVATION_FAILED):
            status = kind.split(".")[1]
            if a.status not in ACTIVATION_TERMINALS:
                self.activations[aid] = replace(a, status=status, reason=d.get("reason"),
                                                accepted_count=max(a.accepted_count, d["acceptedSegmentCount"]),
                                                terminal_count=max(a.terminal_count, d["terminalSegmentCount"]))
            if status in ("cancelled", "failed"):
                for key, s in tuple(self.segments.items()):
                    if s.activation_id == aid and s.status not in SEGMENT_TERMINALS:
                        self.segments[key] = replace(s, preview=None)
        elif kind in SEGMENT_EVENTS:
            sid, seq = d["segmentId"], d["segmentSequence"]
            s = self.segments.get(sid)
            self._sequences[seq] = sid
            s = s or SegmentView(aid, sid, seq)
            if s.status in SEGMENT_TERMINALS:
                return True
            if kind in (p.EventType.COMPLETED, p.EventType.DISCARDED, p.EventType.FAILED):
                status, text, reason = kind.split(".")[1], d.get("text"), d.get("reason")
                if kind == p.EventType.COMPLETED and a.status in ("cancelled", "failed"):
                    status, text, reason = "discarded", None, "activation_" + a.status
                self.segments[sid] = replace(s, status=status, preview=None, text=text, reason=reason,
                                             event_id=event.eventId, event_seq=event.eventSeq)
                if status == "completed":
                    finals.append(FinalResult(self.session_id, aid, sid, seq, text, event.eventId, event.eventSeq))
            elif kind == p.EventType.INTERIM:
                if a.status not in ("cancelled", "failed"):
                    self.segments[sid] = replace(s, preview=event.preview_text)
            else:
                rank = {"recording": 0, "recorded": 1, "accepted": 2, "terminal_unknown": -1}
                status = {p.EventType.RECORDING_STARTED: "recording", p.EventType.RECORDING_ENDED: "recorded",
                          p.EventType.TRANSCRIPTION_ACCEPTED: "accepted"}[kind]
                self.segments[sid] = replace(s, status=status if rank[status] > rank[s.status] else s.status)
        elif kind == p.EventType.WATCHDOG_WARNING and not historical:
            self.activations[aid] = replace(a, watchdog=self._deadline_view(d, now))
        elif kind == p.EventType.WAKE_DETECTED:
            self.activations[aid] = replace(a, wake_word_id=d["wakeWordId"])
        elif kind == p.EventType.WAKE_AVAILABILITY and not historical:
            if d["catalogRevision"] >= self.capabilities.get("catalogRevision", 0):
                changed = d["catalogRevision"] != self.capabilities.get("catalogRevision")
                self.capabilities = freeze({key: d[key] for key in ("catalogRevision", "availableWakeWordIds")})
                if changed:
                    effects.append("catalog_required")
        elif kind == p.EventType.SETTINGS_CHANGED and not historical:
            self.settings_revision = max(self.settings_revision, d["settingsRevision"])
            effects.extend(("settings_required", *self._request_snapshot(now)))
        return True

    def _snapshot(self, snapshot, now):
        if (snapshot.stateVersion < self.state_version or snapshot.lastEventSeq < self.last_event_seq
                or snapshot.settingsRevision < self.settings_revision):
            return self._result(effects=("stale_snapshot", *self._request_snapshot(now)))
        d = snapshot.payload
        for item in d["pendingActivations"]:
            if item["activationSequence"] <= self._retired_activation_sequence:
                return self.protocol_fault(self.generation, now)
            known = self.activations.get(item["activationId"])
            if known and known.sequence is not None and known.sequence != item["activationSequence"]:
                return self.protocol_fault(self.generation, now)
        previous = set(self.activations)
        inp = d["input"]
        self.input = InputView(p.InputPhase(inp["phase"]), inp["activationId"], inp["primarySource"],
                               self._deadline_view(inp, now), inp["closeRequested"])
        visible = set()
        if self.input.activation_id:
            aid = self.input.activation_id
            a = self._activation(aid)
            visible.add(aid)
            self.activations[aid] = replace(a, primary_source=a.primary_source or self.input.primary_source,
                                            effective_settings=a.effective_settings or freeze(d["effectiveSettings"]))
        for item in d["pendingActivations"]:
            aid = item["activationId"]
            visible.add(aid)
            a = self._activation(aid)
            self.activations[aid] = replace(a, sequence=a.sequence or item["activationSequence"], input_closed=True,
                                            close_reason=item["inputClosedReason"],
                                            status=a.status if a.status in ACTIVATION_TERMINALS else "draining",
                                            accepted_count=max(a.accepted_count, item["acceptedSegmentCount"]),
                                            terminal_count=max(a.terminal_count, item["terminalSegmentCount"]))
        self.trigger = freeze(d["trigger"])
        self.audio_available = d["audioAvailable"]
        self.requested, self.effective = freeze(d["requestedSettings"]), freeze(d["effectiveSettings"])
        self.capabilities = freeze(d["wakeWordCapabilities"])
        self.settings_revision = max(self.settings_revision, snapshot.settingsRevision)
        self.state_version, self.last_event_seq = snapshot.stateVersion, snapshot.lastEventSeq
        buffered = sorted(self._buffer.items())
        self._clear_wait()
        self.state = MirrorState.READY
        finals, effects, events = [], [], []
        historical_ids = set()
        for seq, (event, received_at, size) in buffered:
            if seq <= snapshot.lastEventSeq:
                if event.payload.get("activationId"):
                    historical_ids.add(event.payload["activationId"])
                if not self._reduce(event, received_at, finals, effects, historical=True):
                    effects.extend(self._request_snapshot(now, resync=True))
            elif self.state == MirrorState.RESYNCING or seq != self.last_event_seq + 1:
                effects.extend(self._request_snapshot(now, resync=True))
                self._buffer[seq] = (event, received_at, size)
                self._buffer_bytes += size
            else:
                if self._reduce(event, received_at, finals, effects):
                    self.last_event_seq = seq
                    self.state_version = max(self.state_version, event.stateVersion)
                    if not self._retired(event):
                        events.append(event)
                else:
                    effects.extend(self._request_snapshot(now, resync=True))
        # Reconcile after salvaging all buffered payloads and tombstones.
        # New post-snapshot activations must not be classified as disappeared.
        for aid, a in tuple(self.activations.items()):
            known = sum(s.activation_id == aid and s.status in SEGMENT_TERMINALS for s in self.segments.values())
            vanished = (aid in previous | historical_ids and aid not in visible
                        and aid != self.input.activation_id and a.status not in ACTIVATION_TERMINALS)
            if vanished:
                a = replace(a, status="terminal_unknown", input_closed=True, incomplete=True)
                for sid, s in tuple(self.segments.items()):
                    if s.activation_id == aid and s.status not in SEGMENT_TERMINALS:
                        self.segments[sid] = replace(s, status="terminal_unknown", preview=None)
            if a.terminal_count > known:
                a = replace(a, incomplete=True)
            self.activations[aid] = a
            if a.incomplete:
                effects.append("incomplete")
        return self._bounded_result(finals, events, effects)
