"""V2 domain feedback and bounded impulse identities without adapter I/O."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field, replace
from threading import RLock
from typing import Mapping, Optional

from voice_stt_client.core.event_models import (
    CanonicalEventType,
    EventConnectionState,
    EventOrigin,
    FeedbackImpulse,
    FeedbackSource,
    FeedbackState,
    NormalizedFeedbackEvent,
)
from voice_stt_client.core.event_normalizer import EventNormalizer
from voice_stt_client.core.event_protocol import EventProtocolResult
from voice_stt_client.core.feedback_mapping import FeedbackMappingConfig, FeedbackRule
from .feedback_mapping import LedVerb, migrate_v2_feedback_mapping
from .v2_feedback import FeedbackSnapshot, PHASE_KEYS, project_feedback
from .activation_mirror import MirrorState, SEGMENT_TERMINALS
from . import protocol_v2 as p


DEFAULT_DEDUPE_LIMIT = 2048


@dataclass(frozen=True)
class FeedbackReducerState:
    generation: int = 0
    session_id: Optional[str] = None
    visible_state: FeedbackState = FeedbackState.IDLE
    source: FeedbackSource = FeedbackSource.LOCAL_ONLY
    event_connection: EventConnectionState = EventConnectionState.STOPPED
    seen_event_ids: tuple[str, ...] = ()
    seen_correlations: tuple[str, ...] = ()
    revision: int = 0


@dataclass(frozen=True)
class FeedbackDecision:
    state: FeedbackState
    source: FeedbackSource
    rule: FeedbackRule
    event: Optional[NormalizedFeedbackEvent] = None
    impulse: Optional[FeedbackImpulse] = None
    publish: bool = True
    duplicate: bool = False
    replay: bool = False
    uncertain: bool = False
    revision: int = 0
    snapshot: FeedbackSnapshot | None = None
    persistent: bool = False


class FeedbackReducer:
    """Pure bounded identity helpers; no lifecycle or fallback state authority."""







    @staticmethod
    def _identity_keys(
        event: NormalizedFeedbackEvent,
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        event_ids = (event.event_id,) if event.event_id is not None else ()
        aliases = event.details.get("correlationAliases", ())
        if not isinstance(aliases, tuple):
            aliases = ()
        correlations = tuple(
            dict.fromkeys(
                key
                for key in (event.correlation_id, *aliases)
                if isinstance(key, str) and key
            )
        )
        return event_ids, correlations

    @staticmethod
    def _append_bounded(
        existing: tuple[str, ...],
        additions: tuple[str, ...],
        limit: int,
    ) -> tuple[str, ...]:
        ordered = OrderedDict((item, None) for item in existing)
        for item in additions:
            ordered.pop(item, None)
            ordered[item] = None
        while len(ordered) > limit:
            ordered.popitem(last=False)
        return tuple(ordered)

    @staticmethod
    def _validate_limit(limit: int) -> None:
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("dedupe_limit must be an integer >= 1")


class FeedbackEngine:
    """Project V2 mirror state; logs remain diagnostic inputs."""

    def __init__(
        self,
        mapping: FeedbackMappingConfig,
        *,
        dedupe_limit: int = DEFAULT_DEDUPE_LIMIT,
        normalizer: Optional[EventNormalizer] = None,
        on_observation=None,
    ) -> None:
        mapping.validate()
        FeedbackReducer._validate_limit(dedupe_limit)
        self.mapping = migrate_v2_feedback_mapping(mapping)
        self.dedupe_limit = dedupe_limit
        self.normalizer = normalizer or EventNormalizer()
        self.state = FeedbackReducerState()
        self._unknown_events: OrderedDict[str, int] = OrderedDict()
        self._lock = RLock()
        self._v2_view = None
        self._v2_snapshot = None
        self._v2_persistent_rule = FeedbackRule()
        self._v2_issues = ()
        self._v2_observed = ()
        self.adapter_failures = 0
        self.domain_events = 0
        self.diagnostic_events = 0
        self.on_observation = on_observation

    def _observe(self, event_type, **details):
        """Optional non-throwing structured callback; the port owns its sink."""
        if self.on_observation is not None:
            try:
                self.on_observation(event_type, **details)
            except Exception:
                self.adapter_failures += 1

    @staticmethod
    def _persistent(rule):
        return FeedbackRule(led=tuple(c for c in rule.led if not c.is_event), app=rule.app)

    def _v2_project(self):
        self.state = replace(self.state, revision=self.state.revision + 1)
        snapshot = project_feedback(self._v2_view, self.state.revision,
            log_state=self.state.event_connection, issues=self._v2_issues)
        self._v2_snapshot = snapshot
        phase = snapshot.phase
        visible = (FeedbackState.RECORDING if phase == p.InputPhase.SEGMENT_ACTIVE
                   else FeedbackState.IDLE if phase == p.InputPhase.IDLE else FeedbackState.STARTING)
        self.state = replace(self.state, source=FeedbackSource.DOMAIN, visible_state=visible)
        rule = self._persistent(self.mapping.rule_for(PHASE_KEYS[phase]))
        if snapshot.availability != MirrorState.READY or not snapshot.audio_available:
            rule = self._persistent(self.mapping.rule_for(CanonicalEventType.CLIENT_MICROPHONE_LOST
                if not snapshot.audio_available else CanonicalEventType.CLIENT_TRANSPORT_DISCONNECTED))
        # Avoid continuously resetting lasting LED effects on every interim,
        # log keepalive or background result. UI always gets the fresh snapshot.
        emitted = rule if rule != self._v2_persistent_rule else FeedbackRule()
        self._v2_persistent_rule = rule
        return FeedbackDecision(visible, FeedbackSource.DOMAIN, emitted,
            revision=self.state.revision, uncertain=snapshot.incomplete, snapshot=snapshot, persistent=True)

    def handle_reduction(self, reduction) -> tuple[FeedbackDecision, ...]:
        """V2 domain input: snapshot authority plus bounded one-shot identities.

        Call only after mirror validation. Log/fallback ports become diagnostics
        permanently once this engine has accepted a V2 mirror generation.
        """
        with self._lock:
            view = reduction.view
            if view.generation is None or view.session_id is None:
                return ()
            if self._v2_view is not None:
                if (view.generation < self._v2_view.generation
                    or view.generation == self._v2_view.generation and (
                        view.session_id != self._v2_view.session_id
                        or view.last_event_seq < self._v2_view.last_event_seq
                        or view.state_version < self._v2_view.state_version
                        or self._v2_view.state == MirrorState.DISCONNECTED and view.state != MirrorState.DISCONNECTED)):
                    return ()
            fresh = self._v2_view is None or view.generation != self._v2_view.generation
            if fresh:
                self.state = FeedbackReducerState(generation=view.generation, session_id=view.session_id)
                self._v2_persistent_rule = FeedbackRule()
                self._v2_issues = ()
                self._v2_observed = ()
            self._v2_view = view
            decisions = [self._v2_project()]
            finals = {f.event_id for f in reduction.finals}
            events = list(reduction.events)
            # Salvaged final payloads from resync are not lifecycle replay; only
            # real first terminals can announce completion, never snapshot counts.
            for final in reduction.finals:
                if final.event_id not in {e.eventId for e in events}:
                    events.append(p.decode_server_message(dict(type='transcription.completed', protocolVersion=2,
                        sessionId=final.session_id,eventId=final.event_id,eventSeq=final.event_seq,
                        stateVersion=view.state_version,occurredAtUnixMs=0,activationId=final.activation_id,
                        segmentId=final.segment_id,segmentSequence=final.segment_sequence,text=final.text)))
            for raw in events:
                if raw.eventId not in self._v2_observed:
                    self._v2_observed = FeedbackReducer._append_bounded(self._v2_observed, (raw.eventId,), self.dedupe_limit)
                    segment_kind = raw.type in (p.EventType.RECORDING_STARTED, p.EventType.RECORDING_ENDED,
                        p.EventType.TRANSCRIPTION_ACCEPTED, p.EventType.INTERIM, p.EventType.COMPLETED,
                        p.EventType.DISCARDED, p.EventType.FAILED, p.EventType.WATCHDOG_WARNING)
                    self._observe('client.domain.observed', generation=view.generation, session_id=view.session_id,
                        activation_id=raw.payload.get('activationId') if raw.type in p.EventType and raw.type not in (
                            p.EventType.SETTINGS_CHANGED, p.EventType.WAKE_AVAILABILITY, p.EventType.TRIGGER_SUPPRESSED) else None,
                        segment_id=raw.payload.get('segmentId') if segment_kind else None,
                        command_id=raw.payload.get('causedByCommandId') if raw.type == p.EventType.INPUT_CLOSED else None,
                        details=dict(eventId=raw.eventId, eventSeq=raw.eventSeq,
                            eventType=raw.type if raw.type in p.EventType else 'unknown',
                            phase=view.input.phase.value, pendingCount=self._v2_snapshot.pending_count))
                self.domain_events += 1
                event = self.normalizer.normalize_domain(raw, generation=view.generation)
                if event is None:
                    continue
                if raw.type == p.EventType.COMPLETED and raw.eventId not in finals:
                    continue
                segment = view.segments.get(raw.payload.get('segmentId'))
                if raw.type in (p.EventType.RECORDING_STARTED, p.EventType.RECORDING_ENDED):
                    if (not segment or segment.status in SEGMENT_TERMINALS
                        or segment.activation_id != view.input.activation_id):
                        continue
                if raw.type == p.EventType.WATCHDOG_WARNING and raw.payload['activationId'] != view.input.activation_id:
                    continue
                ids, keys = FeedbackReducer._identity_keys(event)
                duplicate = any(k in self.state.seen_event_ids for k in ids) or any(k in self.state.seen_correlations for k in keys)
                self.state = replace(self.state,
                    seen_event_ids=FeedbackReducer._append_bounded(self.state.seen_event_ids, ids, self.dedupe_limit),
                    seen_correlations=FeedbackReducer._append_bounded(self.state.seen_correlations, keys, self.dedupe_limit))
                if duplicate:
                    continue
                rule = self.mapping.rule_for(event.event_type)
                # Lasting state belongs exclusively to the foreground projection.
                # A-complete may pulse over B but must settle back into B.
                rule = replace(rule, led=tuple(c for c in rule.led if c.is_event), app=rule.app)
                if raw.type == p.EventType.WATCHDOG_WARNING:
                    remaining = raw.payload['remainingMs']
                    rule = replace(rule, led=tuple(replace(c, config=dict(c.config, duration_ms=max(1, remaining)))
                        if c.verb == LedVerb.SET_OVERLAY else c for c in rule.led))
                decision = FeedbackDecision(self.state.visible_state, FeedbackSource.DOMAIN, rule,
                    event=event, impulse=event.impulse, revision=self.state.revision, snapshot=self._v2_snapshot)
                self._observe('client.feedback.decision', generation=view.generation, session_id=view.session_id,
                    activation_id=event.details.get('activationId'), segment_id=event.details.get('segmentId'),
                    command_id=event.details.get('commandId'), correlation_id=event.correlation_id,
                    details=dict(eventId=event.event_id, eventSeq=event.details.get('eventSeq'), phase=view.input.phase.value,
                                 source='domain', pendingCount=self._v2_snapshot.pending_count))
                decisions.append(decision)
            return tuple(decisions)

    def update_v2_issues(self, issues=()) -> FeedbackDecision | None:
        """UI/output status only; explicit stable categories, no raw errors."""
        known = {'history_unavailable', 'injection_failed', 'key_rejected', 'sound_failed', 'led_unavailable', 'action_blocked'}
        if any(x not in known for x in issues):
            raise ValueError('unknown feedback issue')
        with self._lock:
            self._v2_issues = tuple(dict.fromkeys(issues))
            return None if self._v2_view is None else self._v2_project()

    @property
    def unknown_events(self) -> Mapping[str, int]:
        with self._lock:
            return dict(self._unknown_events)

    def handle_event_stream(self, result, *, generation, session_id):
        """Logs remain diagnostics, including before the first V2 snapshot."""
        with self._lock:
            self.diagnostic_events += 1
            return None

    def handle_local(self, event_type, *, generation, session_id=None,
                     correlation_id=None, details=None):
        with self._lock:
            if self._v2_view is None or generation != self.state.generation or session_id != self.state.session_id:
                return FeedbackDecision(self.state.visible_state, FeedbackSource.DOMAIN, FeedbackRule(), publish=False)
            categories = {CanonicalEventType.CLIENT_INJECTION_FAILED: 'injection_failed',
                CanonicalEventType.CLIENT_ACTION_BLOCKED: 'action_blocked',
                CanonicalEventType.CLIENT_SOUND_FAILED: 'sound_failed',
                CanonicalEventType.CLIENT_LED_UNAVAILABLE: 'led_unavailable'}
            category = categories.get(event_type)
            if category:
                self._v2_issues = tuple(dict.fromkeys((*self._v2_issues, category)))
            return self._v2_project()

    def update_connection(self, connection, *, stt_ready, generation, session_id, issue=None):
        with self._lock:
            if self._v2_view is None:
                self.state = replace(self.state, event_connection=connection)
                return FeedbackDecision(self.state.visible_state, FeedbackSource.DOMAIN, FeedbackRule(), publish=False)
            if generation != self.state.generation or session_id != self.state.session_id:
                return FeedbackDecision(self.state.visible_state, FeedbackSource.DOMAIN, FeedbackRule(), publish=False)
            self.state = replace(self.state, event_connection=connection)
            return self._v2_project()

    def reconfigure_mapping(self, mapping: FeedbackMappingConfig) -> None:
        mapping.validate()
        with self._lock:
            self.mapping = migrate_v2_feedback_mapping(mapping)

    def _remember_unknown(self, event_name: str) -> None:
        count = self._unknown_events.pop(event_name, 0) + 1
        self._unknown_events[event_name] = count
        while len(self._unknown_events) > 128:
            self._unknown_events.popitem(last=False)
