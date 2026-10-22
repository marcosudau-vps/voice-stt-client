"""Final consumer for authoritative V2 mirror reductions, never log replay.

The core calls consume synchronously in publication order. The consumer holds
only current-session terminal identities, independently of optional history.
Clipboard work remains on the existing serial worker, with reserved attempts.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging
import threading
import time
import uuid

from . import protocol_v2 as p
from .activation_mirror import FinalResult, MirrorState, Reduction, SEGMENT_TERMINALS
from .history import HistoryAddStatus, HistoryEntry, TranscriptHistoryManager
from .text_injector import TextInjectionQueue

logger = logging.getLogger('text')


@dataclass(frozen=True)
class ResultOutcome:
    status: str
    final: FinalResult
    generation: int
    entry_id: str | None = None
    reason: str | None = None
    is_conflict: bool = False


class V2ResultService:
    def __init__(self, history: TranscriptHistoryManager, queue: TextInjectionQueue, connection=None):
        if queue.history_manager is not history:
            raise ValueError('Results and injection queue must share history')
        if connection is not None and (connection.session.binding is not None
                                       or getattr(connection, '_result_service', None) is not None):
            raise RuntimeError('Attach one result service before admission')
        self.history, self.queue, self.connection = history, queue, connection
        self.on_result = None
        self.on_attempt_result = None
        self._lock = threading.Lock()
        self._generation = 0
        self._lost_generation = 0
        self._session_id = None
        self._terminals: dict[str, tuple] = {}
        self._last_final_event_seq = 0
        self._closed = False
        old_attempt = queue.on_attempt_result

        def attempt_result(attempt):
            for callback in (old_attempt, self.on_attempt_result):
                self._notify(callback, attempt)

        queue.on_attempt_result = attempt_result
        if connection is not None:
            connection._result_service = self
            old_reduction = connection.on_reduction

            def reduction(value):
                self.consume(value)
                self._notify(old_reduction, value)

            connection.on_reduction = reduction

    @staticmethod
    def _notify(callback, value):
        if callback:
            try:
                callback(value)
            except Exception:
                logger.exception('Result publication callback failed')

    def consume(self, reduction: Reduction) -> tuple[ResultOutcome, ...]:
        """Consume emitted finals only, guarding binding and first terminal.

        Snapshot segment maps are guards, never a source of inferred results.
        A gap-recovered FinalResult emitted by the mirror is a valid source.
        """
        view = reduction.view
        outcomes = []
        with self._lock:
            if self._closed:
                return ()
            if self.connection is not None:
                current = self.connection.mirror.view
                if (view.generation, view.session_id) != (current.generation, current.session_id):
                    return ()
                if current.state in (MirrorState.DISCONNECTED, MirrorState.RECONNECT_REQUIRED):
                    self._lost_generation = max(self._lost_generation, current.generation or 0)
                    return ()
            if view.state in (MirrorState.DISCONNECTED, MirrorState.RECONNECT_REQUIRED):
                self._lost_generation = max(self._lost_generation, view.generation or 0)
                return ()
            if (view.generation is None or view.generation < self._generation
                    or view.generation <= self._lost_generation):
                return ()
            if view.generation > self._generation:
                self._generation, self._session_id = view.generation, view.session_id
                self._terminals.clear()
                self._last_final_event_seq = 0
            if view.session_id != self._session_id:
                return ()
            # Mirror retirement removes settled segment details. A publication
            # watermark independently rejects old Reduction objects, including
            # after history deletion/disablement or an unknown paste outcome.
            self._terminals = {key: value for key, value in self._terminals.items()
                               if key in view.segments}
            # A reduction may emit several salvaged results; preserve event publication order.
            for final in sorted(reduction.finals, key=lambda f: f.event_seq):
                segment = view.segments.get(final.segment_id)
                if (not isinstance(final, FinalResult)
                        or not all(p.is_canonical_uuid(v) for v in
                                   (final.session_id, final.activation_id, final.segment_id, final.event_id))
                        or final.session_id != view.session_id
                        or type(final.segment_sequence) is not int or final.segment_sequence < 1
                        or type(final.event_seq) is not int or final.event_seq < 1
                        or not isinstance(final.text, str)
                        or segment is None or segment.status != 'completed'
                        or (segment.activation_id, segment.sequence, segment.event_id, segment.event_seq, segment.text)
                        != (final.activation_id, final.segment_sequence, final.event_id, final.event_seq, final.text)):
                    logger.warning('Ignoring final without an authoritative segment identity')
                    continue
                identity = (final.activation_id, final.segment_sequence, 'completed', final.text)
                previous = self._terminals.get(final.segment_id)
                if previous is not None:
                    outcomes.append(ResultOutcome('deduplicated', final, view.generation,
                                                  reason='duplicate', is_conflict=previous != identity))
                    continue
                if final.event_seq <= self._last_final_event_seq:
                    outcomes.append(ResultOutcome('deduplicated', final, view.generation,
                                                  reason='retired_publication'))
                    continue
                self._last_final_event_seq = final.event_seq
                # Reserve before text checks/storage; an empty first terminal is final too.
                self._terminals[final.segment_id] = identity
                if not final.text.strip():
                    outcomes.append(ResultOutcome('empty', final, view.generation, reason='empty_final'))
                    continue
                activation = view.activations.get(final.activation_id)
                fields = dict(protocol_version=2, activation_id=final.activation_id,
                              segment_sequence=final.segment_sequence, event_id=final.event_id,
                              event_seq=final.event_seq, primary_source=activation.primary_source if activation else None,
                              activation_sequence=activation.sequence if activation else None)
                try:
                    added = self.history.add_entry_with_status(final.session_id, final.segment_id, final.text, **fields)
                    if added.status == HistoryAddStatus.ALREADY_EXISTS:
                        outcomes.append(ResultOutcome('deduplicated', final, view.generation,
                                                      added.entry.id if added.entry else None, 'persisted_duplicate',
                                                      added.entry is not None and added.entry.text != final.text))
                        continue
                    entry = added.entry
                    if entry is None and not self.history.config.enabled:
                        # Output works with history off; dedup and attempts are process-local.
                        entry = HistoryEntry(uuid.uuid4().hex, final.session_id, final.segment_id,
                                             time.time(), final.text, len(final.text), **fields)
                    if entry is None:
                        outcomes.append(ResultOutcome('history_unavailable', final, view.generation,
                                                      reason='history_unavailable'))
                        continue
                    accepted = self.queue.enqueue_reserved(entry)
                    outcomes.append(ResultOutcome('queued' if accepted else 'queue_unavailable', final,
                                                  view.generation, entry.id,
                                                  None if accepted else self.queue.last_error))
                except Exception:
                    logger.exception('Final output failed; audio and mirror remain available')
                    outcomes.append(ResultOutcome('failed', final, view.generation, reason='result_processing_failed'))
            for segment in view.segments.values():
                if segment.status in SEGMENT_TERMINALS:
                    self._terminals.setdefault(segment.segment_id,
                        (segment.activation_id, segment.sequence, segment.status, segment.text))
        for outcome in outcomes:
            self._notify(self.on_result, outcome)
        return tuple(outcomes)

    def close(self):
        """Reject subsequent reductions; accepted queue work still drains normally."""
        with self._lock:
            self._closed = True
            self._terminals.clear()
