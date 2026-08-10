"""Pure AP07 feedback reduction and stateful orchestration without adapter I/O."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field, replace
from threading import RLock
from typing import Mapping, Optional

from core.event_models import (
    CanonicalEventType,
    EventConnectionState,
    EventOrigin,
    FeedbackImpulse,
    FeedbackSource,
    FeedbackState,
    NormalizedFeedbackEvent,
)
from core.event_normalizer import EventNormalizer
from core.event_protocol import EventProtocolResult
from core.feedback_mapping import FeedbackMappingConfig, FeedbackRule


DEFAULT_DEDUPE_LIMIT = 2048


@dataclass(frozen=True)
class FeedbackReducerState:
    generation: int = 0
    session_id: Optional[str] = None
    visible_state: FeedbackState = FeedbackState.IDLE
    event_state: FeedbackState = FeedbackState.IDLE
    fallback_state: FeedbackState = FeedbackState.IDLE
    source: FeedbackSource = FeedbackSource.LOCAL_ONLY
    event_connection: EventConnectionState = EventConnectionState.STOPPED
    stt_ready: bool = False
    local_fault: Optional[CanonicalEventType] = None
    uncertain: bool = False
    seen_event_ids: tuple[str, ...] = ()
    seen_correlations: tuple[str, ...] = ()
    event_rule: FeedbackRule = field(default_factory=FeedbackRule)
    fallback_rule: FeedbackRule = field(default_factory=FeedbackRule)
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


class FeedbackReducer:
    """Deterministic state transition functions; no devices or callbacks."""

    @classmethod
    def reduce(
        cls,
        state: FeedbackReducerState,
        event: NormalizedFeedbackEvent,
        rule: FeedbackRule,
        *,
        dedupe_limit: int = DEFAULT_DEDUPE_LIMIT,
    ) -> tuple[FeedbackReducerState, FeedbackDecision]:
        cls._validate_limit(dedupe_limit)
        event_ids, correlations = cls._identity_keys(event)
        duplicate_event = any(key in state.seen_event_ids for key in event_ids)
        duplicate_correlation = any(
            key in state.seen_correlations for key in correlations
        )
        duplicate = duplicate_event or duplicate_correlation

        next_state = replace(
            state,
            seen_event_ids=cls._append_bounded(
                state.seen_event_ids,
                event_ids,
                dedupe_limit,
            ),
            seen_correlations=cls._append_bounded(
                state.seen_correlations,
                correlations,
                dedupe_limit,
            ),
        )

        # An event-stream replay/live fact may duplicate a prior fallback fact.
        # It must still reconstruct the authoritative shadow state, but may not
        # emit the already represented impulse a second time.
        cross_source_duplicate = (
            duplicate
            and event.source
            in {FeedbackSource.EVENT_STREAM, FeedbackSource.STT_FALLBACK}
            and not duplicate_event
        )
        if duplicate and not cross_source_duplicate:
            return next_state, FeedbackDecision(
                state=state.visible_state,
                source=state.source,
                rule=FeedbackRule(),
                event=event,
                publish=False,
                duplicate=True,
                replay=event.origin is EventOrigin.REPLAY,
                uncertain=state.uncertain,
                revision=state.revision,
            )

        if event.source is FeedbackSource.EVENT_STREAM:
            next_state, decision_state = cls._apply_server_event(
                next_state,
                event,
                rule,
                event_stream=True,
            )
            selected = state.source is FeedbackSource.EVENT_STREAM
        elif event.source is FeedbackSource.STT_FALLBACK:
            next_state, decision_state = cls._apply_server_event(
                next_state,
                event,
                rule,
                event_stream=False,
            )
            selected = state.source is FeedbackSource.STT_FALLBACK
        else:
            return cls._apply_local_event(next_state, event, rule)

        is_replay = event.origin is EventOrigin.REPLAY
        publish = selected and not is_replay
        impulse = None if duplicate or is_replay else event.impulse
        decision_rule = rule if publish else FeedbackRule()
        visible_decision_state = (
            FeedbackState.FAILED
            if next_state.local_fault is not None
            else decision_state
        )
        if publish:
            next_state = replace(
                next_state,
                visible_state=(
                    FeedbackState.FAILED
                    if next_state.local_fault is not None
                    else cls._stable_state(decision_state)
                ),
                revision=next_state.revision + 1,
            )
        return next_state, FeedbackDecision(
            state=visible_decision_state,
            source=next_state.source,
            rule=decision_rule,
            event=event,
            impulse=impulse,
            publish=publish,
            duplicate=duplicate,
            replay=is_replay,
            uncertain=next_state.uncertain,
            revision=next_state.revision,
        )

    @classmethod
    def transition_connection(
        cls,
        state: FeedbackReducerState,
        connection: EventConnectionState,
        *,
        stt_ready: bool,
        technical_event: NormalizedFeedbackEvent,
        technical_rule: FeedbackRule,
        issue: Optional[str] = None,
    ) -> tuple[FeedbackReducerState, FeedbackDecision]:
        if not isinstance(connection, EventConnectionState):
            raise TypeError("connection must be EventConnectionState")
        if not isinstance(stt_ready, bool):
            raise TypeError("stt_ready must be a boolean")
        generation = technical_event.details.get("generation")
        session_id = technical_event.details.get("sessionId")
        if isinstance(generation, bool) or not isinstance(generation, int):
            raise TypeError("technical event generation must be an integer")
        base = state
        if generation != state.generation or session_id != state.session_id:
            base = replace(
                state,
                generation=generation,
                session_id=session_id if isinstance(session_id, str) else None,
                visible_state=(
                    FeedbackState.FAILED
                    if state.local_fault is not None
                    else FeedbackState.IDLE
                ),
                event_state=FeedbackState.IDLE,
                fallback_state=FeedbackState.IDLE,
                source=FeedbackSource.LOCAL_ONLY,
                event_connection=EventConnectionState.STOPPED,
                stt_ready=False,
                uncertain=False,
                event_rule=FeedbackRule(),
                fallback_rule=FeedbackRule(),
            )
        if not stt_ready:
            source = FeedbackSource.LOCAL_ONLY
            selected_state = FeedbackState.IDLE
            selected_rule = technical_rule
        elif connection is EventConnectionState.LIVE:
            source = FeedbackSource.EVENT_STREAM
            selected_state = base.event_state
            # Going LIVE publishes reconstructed persistent presentation only;
            # replayed one-shot sound cues must never fire at the switchover.
            selected_rule = replace(base.event_rule, sound=None)
        else:
            source = FeedbackSource.STT_FALLBACK
            selected_state = base.fallback_state
            selected_rule = technical_rule
        uncertain = base.uncertain or issue == "retention_gap"
        visible = (
            FeedbackState.FAILED
            if base.local_fault is not None
            else selected_state
        )
        next_state = replace(
            base,
            visible_state=visible,
            source=source,
            event_connection=connection,
            stt_ready=stt_ready,
            uncertain=uncertain,
            revision=state.revision + 1,
        )
        return next_state, FeedbackDecision(
            state=visible,
            source=source,
            rule=selected_rule,
            event=technical_event,
            publish=True,
            replay=False,
            uncertain=uncertain,
            revision=next_state.revision,
        )

    @classmethod
    def _apply_server_event(
        cls,
        state: FeedbackReducerState,
        event: NormalizedFeedbackEvent,
        rule: FeedbackRule,
        *,
        event_stream: bool,
    ) -> tuple[FeedbackReducerState, FeedbackState]:
        current = state.event_state if event_stream else state.fallback_state
        decision_state = event.state or current
        persistent = cls._stable_state(decision_state)
        persistent_rule = (
            rule
            if persistent
            in {
                FeedbackState.WAITING_FOR_WAKE_WORD,
                FeedbackState.STARTING,
                FeedbackState.RECORDING,
                FeedbackState.FINALIZING,
                FeedbackState.FAILED,
                FeedbackState.INTERRUPTED,
            }
            else FeedbackRule()
        )
        if event_stream:
            return replace(
                state,
                event_state=persistent,
                event_rule=persistent_rule,
            ), decision_state
        return replace(
            state,
            fallback_state=persistent,
            fallback_rule=persistent_rule,
        ), decision_state

    @classmethod
    def _apply_local_event(
        cls,
        state: FeedbackReducerState,
        event: NormalizedFeedbackEvent,
        rule: FeedbackRule,
    ) -> tuple[FeedbackReducerState, FeedbackDecision]:
        local_fault = state.local_fault
        if event.event_type is CanonicalEventType.CLIENT_MICROPHONE_LOST:
            local_fault = event.event_type
        elif event.event_type is CanonicalEventType.CLIENT_MICROPHONE_RECOVERED:
            local_fault = None
        stable_selected = cls._selected_server_state(state)
        if local_fault is not None:
            visible = FeedbackState.FAILED
        elif event.event_type is CanonicalEventType.CLIENT_DICTATION_INTERRUPTED:
            visible = FeedbackState.INTERRUPTED
        elif event.state is not None and event.impulse is not None:
            # Local one-shot failures are visible in the decision, but don't
            # erase the persistent authoritative server state.
            visible = event.state
        else:
            visible = stable_selected
        next_visible = (
            FeedbackState.FAILED if local_fault is not None else stable_selected
        )
        next_state = replace(
            state,
            local_fault=local_fault,
            visible_state=next_visible,
            revision=state.revision + 1,
        )
        return next_state, FeedbackDecision(
            state=visible,
            source=FeedbackSource.LOCAL_ONLY,
            rule=rule,
            event=event,
            impulse=event.impulse,
            publish=True,
            uncertain=state.uncertain,
            revision=next_state.revision,
        )

    @staticmethod
    def _selected_server_state(state: FeedbackReducerState) -> FeedbackState:
        if state.source is FeedbackSource.EVENT_STREAM:
            return state.event_state
        if state.source is FeedbackSource.STT_FALLBACK:
            return state.fallback_state
        return FeedbackState.IDLE

    @staticmethod
    def _stable_state(state: FeedbackState) -> FeedbackState:
        if state is FeedbackState.COMPLETED:
            return FeedbackState.IDLE
        return state

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
    """Own reducer state and normalize all three input sources consistently."""

    def __init__(
        self,
        mapping: FeedbackMappingConfig,
        *,
        dedupe_limit: int = DEFAULT_DEDUPE_LIMIT,
        normalizer: Optional[EventNormalizer] = None,
    ) -> None:
        mapping.validate()
        FeedbackReducer._validate_limit(dedupe_limit)
        self.mapping = mapping
        self.dedupe_limit = dedupe_limit
        self.normalizer = normalizer or EventNormalizer()
        self.state = FeedbackReducerState()
        self._unknown_events: OrderedDict[str, int] = OrderedDict()
        self._lock = RLock()

    @property
    def unknown_events(self) -> Mapping[str, int]:
        with self._lock:
            return dict(self._unknown_events)

    def handle_event_stream(
        self,
        result: EventProtocolResult,
        *,
        generation: int,
        session_id: str,
    ) -> Optional[FeedbackDecision]:
        with self._lock:
            event = self.normalizer.normalize_event_stream(
                result,
                generation=generation,
                session_id=session_id,
            )
            if event is None:
                name = result.event.event if result.event is not None else "unknown"
                self._remember_unknown(name)
                return None
            self.state, decision = FeedbackReducer.reduce(
                self.state,
                event,
                self.mapping.rule_for(event.event_type),
                dedupe_limit=self.dedupe_limit,
            )
            return decision

    def handle_stt_fallback(
        self,
        event_type: str,
        data: Mapping[str, object],
        *,
        generation: int,
        session_id: str,
    ) -> Optional[FeedbackDecision]:
        with self._lock:
            event = self.normalizer.normalize_stt_fallback(
                event_type,
                data,
                generation=generation,
                session_id=session_id,
            )
            if event is None:
                return None
            self.state, decision = FeedbackReducer.reduce(
                self.state,
                event,
                self.mapping.rule_for(event.event_type),
                dedupe_limit=self.dedupe_limit,
            )
            return decision

    def handle_local(
        self,
        event_type: CanonicalEventType,
        *,
        generation: int,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        details: Optional[Mapping[str, object]] = None,
    ) -> FeedbackDecision:
        with self._lock:
            event = self.normalizer.normalize_local(
                event_type,
                generation=generation,
                session_id=session_id,
                correlation_id=correlation_id,
                details=details,
            )
            self.state, decision = FeedbackReducer.reduce(
                self.state,
                event,
                self.mapping.rule_for(event.event_type),
                dedupe_limit=self.dedupe_limit,
            )
            return decision

    def update_connection(
        self,
        connection: EventConnectionState,
        *,
        stt_ready: bool,
        generation: int,
        session_id: Optional[str],
        issue: Optional[str] = None,
    ) -> FeedbackDecision:
        with self._lock:
            event_type = self._connection_event_type(connection)
            event = self.normalizer.normalize_local(
                event_type,
                generation=generation,
                session_id=session_id,
                details={"issue": issue},
            )
            self.state, decision = FeedbackReducer.transition_connection(
                self.state,
                connection,
                stt_ready=stt_ready,
                technical_event=event,
                technical_rule=self.mapping.rule_for(event_type),
                issue=issue,
            )
            return decision

    def reconfigure_mapping(self, mapping: FeedbackMappingConfig) -> None:
        mapping.validate()
        with self._lock:
            self.mapping = mapping

    def _remember_unknown(self, event_name: str) -> None:
        count = self._unknown_events.pop(event_name, 0) + 1
        self._unknown_events[event_name] = count
        while len(self._unknown_events) > 128:
            self._unknown_events.popitem(last=False)

    @staticmethod
    def _connection_event_type(
        connection: EventConnectionState,
    ) -> CanonicalEventType:
        if connection is EventConnectionState.LIVE:
            return CanonicalEventType.CLIENT_EVENT_STREAM_LIVE
        if connection is EventConnectionState.REPLAYING:
            return CanonicalEventType.CLIENT_EVENT_STREAM_REPLAYING
        if connection in {
            EventConnectionState.CONNECTING,
            EventConnectionState.SUBSCRIBING,
        }:
            return CanonicalEventType.CLIENT_EVENT_STREAM_CONNECTING
        return CanonicalEventType.CLIENT_EVENT_STREAM_DEGRADED
