"""
Client observation entry-point contract and concrete ingress (OBS-010/OBS-020).

Signature source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §6. OBS-010 froze the
``Ingress`` protocol; OBS-020 adds the concrete, thread-safe
``ObservabilityIngress`` plus the behaviorally-equivalent ``NullIngress``
no-op and its module constant ``NULL_INGRESS``.

``submit`` is the non-blocking, non-throwing boundary every producer thread
crosses (ARCH §5, §6.3): order is Health ``FAILED``? -> enabled/level? ->
watermark rule (ARCH §7.1/§7.2) -> ``put_nowait``.

OBS-040 adds two things, both additive and both required by the frozen
contracts:

* ``emit_record_rejected`` — the substitute record ``logging.record_rejected``
  that ``ARCH §8.3`` (row *"Normalizer-Ausnahme"*) and ``CONTRACTS §12.4``
  demand and that no OBS-010..030 path produced (gate observation N-1).
* the aggregate-source registry — ``ARCH §8.6`` requires that the hot path
  only increment plain ``int`` attributes on the producer and that *"der
  Aggregatrecord entsteht im WORKER, der die Zaehler LIEST"*. The worker lives
  in the observability domain and may not import ``core.audio_capture``
  (§5.2), so the producers register a **read-only** callable here and the
  worker reads through it. No counter is added to ``LoggingHealthSnapshot``
  (§7.3 is frozen); these are the producer's own counters, not logging's.
"""

from __future__ import annotations

import queue
import threading
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Mapping, Optional, Protocol, Tuple
from uuid import uuid4

from .health import LoggingInternalHealth
from .models import CanonicalLogRecord, Level, RecordPriority, level_rank
from .normalizer import from_client_event, from_server_result

AggregateSource = Callable[[], Optional[Mapping[str, Any]]]


class Ingress(Protocol):
    """The structured client observation API. Exactly one call per call site."""

    def event(
        self,
        type: str,
        *,
        channel: str,
        level: str = "INFO",
        component: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Mapping[str, Any]] = None,
        session_id: Optional[str] = None,
        generation: Optional[int] = None,
        activation_id: Optional[str] = None,
        segment_id: Optional[int] = None,
        command_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        transcription_id: Optional[str] = None,
    ) -> None: ...


DEFAULT_QUEUE_SIZE = 8192
WATERMARK_RATIO = 0.75
# The closed level set (CONTRACTS §2.1). A runtime apply with an unknown
# level keeps the current one instead of silently falling back to INFO.
_LEVEL_NAMES = frozenset(level.value for level in Level)


def _utc_now_iso() -> str:
    """ISO-8601 UTC with a ``Z`` suffix and millisecond precision — the same
    encoding the normalizer uses for ``received_at`` (CONTRACTS §1.1)."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond // 1000:03d}Z"


class ObservabilityIngress:
    """Thread-safe ingress boundary in front of **one** bounded ``queue.Queue``
    (ARCH §7.1). ``submit`` never blocks and never raises."""

    def __init__(
        self,
        *,
        instance_id: str,
        enabled: bool = True,
        level: str = "INFO",
        queue_size: int = DEFAULT_QUEUE_SIZE,
        watermark_ratio: float = WATERMARK_RATIO,
        store_raw_payload: bool = True,
        store_transcription_content: bool = False,
        user_profile: Any = None,
        health: Optional[LoggingInternalHealth] = None,
    ) -> None:
        self._instance_id = instance_id
        self._enabled = enabled
        self._level = level if isinstance(level, str) and level else "INFO"
        self._queue: "queue.Queue[CanonicalLogRecord]" = queue.Queue(maxsize=max(1, queue_size))
        self._watermark = max(0, int(max(1, queue_size) * watermark_ratio))
        self._store_raw_payload = store_raw_payload
        self._store_transcription_content = store_transcription_content
        self._user_profile = user_profile
        self.health = health if health is not None else LoggingInternalHealth()
        # ARCH §8.6: registered by producers, read by the worker. Guarded by
        # its own lock because registration happens on the Qt/core threads
        # while the read happens on the worker thread.
        self._aggregate_lock = threading.Lock()
        self._aggregate_sources: Dict[str, Tuple[Optional[str], AggregateSource]] = {}
        # CONTRACTS §10.4 (OBS-050): the runtime apply chain reaches the
        # ingress, but the ingress owns only four of the nine settings. The
        # rest belong to the worker and the sink, which the ingress must not
        # import (ARCH §5.2, import direction ``ingress <- worker``). So the
        # composition root registers a listener here and applies its own half
        # itself; the ingress never learns what a worker is.
        self._config_listeners: List[Callable[[Any], None]] = []

    # -- read-only config, used by the future normalizer callable
    # (core/logging_setup.py) so nothing besides ``ingress``/``level`` needs
    # to be invented on the future ``observability`` composition root.

    @property
    def instance_id(self) -> str:
        return self._instance_id

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def level(self) -> str:
        return self._level

    @property
    def store_transcription_content(self) -> bool:
        return self._store_transcription_content

    @property
    def user_profile(self) -> Any:
        return self._user_profile

    def qsize(self) -> int:
        return self._queue.qsize()

    def submit(self, record: Any) -> bool:
        """Thread-safe. Never blocks, never raises.

        ``False`` = not accepted (disabled, filtered, dropped).
        """
        if not isinstance(record, CanonicalLogRecord):
            return False
        if self.health.is_failed():
            return False
        if not self._enabled:
            return False
        if level_rank(record.level) < level_rank(self._level):
            return False
        if self._queue.qsize() >= self._watermark and record.priority is not RecordPriority.HIGH:
            self.health.record_dropped_watermark()
            return False
        try:
            self._queue.put_nowait(record)
        except queue.Full:
            self.health.record_dropped_queue_full()
            return False
        self.health.record_enqueued()
        return True

    def observe_server_result(self, context: Any, result: Any) -> None:
        """The fan-out entry point of the ``ServerLiveAdapter`` (OBS-040).

        ``raw`` is taken over as the already frozen reference the protocol
        processor produced — not copied, not serialised, not redacted here
        (ARCH §8.2); the worker does all three.
        """
        if not self._enabled:
            return
        try:
            record = from_server_result(
                context,
                result,
                client_instance_id=self._instance_id,
                store_raw_payload=self._store_raw_payload,
                store_transcription_content=self._store_transcription_content,
                user_profile=self._user_profile,
            )
        except Exception as exc:  # noqa: BLE001 - the ingress boundary never raises
            self.health.record_malformed()
            self.emit_record_rejected("observability.normalizer.server", exc)
            return
        if record is None:
            return
        self.submit(record)

    def event(
        self,
        type: str,
        *,
        channel: str,
        level: str = "INFO",
        component: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Mapping[str, Any]] = None,
        session_id: Optional[str] = None,
        generation: Optional[int] = None,
        activation_id: Optional[str] = None,
        segment_id: Optional[int] = None,
        command_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        transcription_id: Optional[str] = None,
    ) -> None:
        """The structured client observation API. Exactly one call per call site."""
        if not self._enabled:
            return
        try:
            record = from_client_event(
                type,
                channel=channel,
                level=level,
                component=component,
                message=message,
                details=details,
                instance_id=self._instance_id,
                store_transcription_content=self._store_transcription_content,
                user_profile=self._user_profile,
                session_id=session_id,
                generation=generation,
                activation_id=activation_id,
                segment_id=segment_id,
                command_id=command_id,
                correlation_id=correlation_id,
                transcription_id=transcription_id,
            )
        except Exception as exc:  # noqa: BLE001 - the ingress boundary never raises
            self.health.record_malformed()
            self.emit_record_rejected("observability.normalizer.client", exc)
            return
        if record is None:
            # CONTRACTS §3: *"Der Normalizer wirft nie. Im Zweifel liefert er
            # ``None``, und der AUFRUFER zaehlt ``malformed``."* On this path
            # ``None`` has exactly one meaning: ``from_client_event`` caught
            # its own exception and gave up — its only ``return None`` sits in
            # its ``except`` branch. Without this line that case was completely
            # invisible: no counter, no health signal, nothing (OBS-060
            # finding B-2). The server path is deliberately NOT treated this
            # way; there ``None`` also means *"this result kind maps to no
            # record"*, which is a decision and not a doubt.
            self.health.record_malformed()
            return
        self.submit(record)

    # -- ARCH §8.3 / CONTRACTS §12.4: logging.record_rejected -------------

    def emit_record_rejected(self, component: str, exc: BaseException) -> None:
        """One substitute record for a record that could not be normalised.

        ``ARCH §8.3``, row *"Normalizer-Ausnahme"*: *"Record verworfen; **ein**
        Ersatzrecord ``logging.record_rejected`` mit Komponente und
        Ausnahmetyp, **ohne** Originaldaten"*, Health stays ``OK`` and
        ``malformed`` has already been raised by the caller.

        ``is_internal=True`` makes it ``HIGH`` (CONTRACTS §1.5), so the record
        that explains a gap survives exactly the overload in which the gap
        appears. Carries no original payload, no message and no correlation
        field — there is nothing trustworthy left to carry, and copying from a
        structure that just broke the normalizer is how an unredacted value
        would escape. Never raises.
        """
        try:
            record = CanonicalLogRecord(
                record_id=uuid4().hex,
                received_at=_utc_now_iso(),
                producer_kind="client",
                producer_id="voice-stt-client",
                instance_id=self._instance_id,
                scope="instance",
                channel="performance",
                level="WARNING",
                replayed=False,
                type="logging.record_rejected",
                component="observability.ingress",
                details={
                    "component": str(component),
                    "exception": type(exc).__name__,
                },
                is_internal=True,
            )
        except Exception:  # noqa: BLE001 - the error path itself never raises
            return
        try:
            self.submit(record)
        except Exception:  # noqa: BLE001
            pass

    # -- CONTRACTS §10.3/§10.4: runtime settings --------------------------

    def register_config_listener(self, listener: Callable[[Any], None]) -> None:
        """Register one callable that receives the same
        ``LoggingObservabilityConfig`` ``apply_config`` receives.

        Used by ``ObservabilityManager`` for the settings the ingress does not
        own (retention, entry limit, file sink, handler level). Registration is
        idempotent per callable so a re-registration cannot install the same
        listener twice.
        """
        if listener is None or listener in self._config_listeners:
            return
        self._config_listeners.append(listener)

    def apply_config(self, config: Any) -> None:
        """CONTRACTS §10.4: called from ``STTController.apply_runtime_config``.

        *"apply_config ist NICHT werfend und liefert nichts zurueck; ein
        Fehler dort darf das Apply-Ergebnis nicht beeinflussen."* The four
        settings applied here are the ones this object owns — ``enabled``,
        ``level`` (ARCH §8.7: the ingress half of the single level value),
        ``store_raw_payload`` and ``store_transcription_content``. Everything
        else is forwarded to the registered listeners.

        ``store_enabled`` and ``db_path`` are deliberately **not** applied:
        §10.3 marks them ``APP_RESTART`` because a running worker holds an
        open SQLite connection, and swapping it at runtime would need flush,
        close, reopen and migration — *"ein Fehlerpfad, den V1 nicht
        braucht"*.
        """
        try:
            enabled = getattr(config, "enabled", None)
            if isinstance(enabled, bool):
                self._enabled = enabled
            level = getattr(config, "level", None)
            if isinstance(level, str) and level.upper() in _LEVEL_NAMES:
                self._level = level.upper()
            store_raw = getattr(config, "store_raw_payload", None)
            if isinstance(store_raw, bool):
                self._store_raw_payload = store_raw
            store_transcripts = getattr(config, "store_transcription_content", None)
            if isinstance(store_transcripts, bool):
                self._store_transcription_content = store_transcripts
        except Exception:  # noqa: BLE001 - O-01: never influence the apply result
            pass
        for listener in list(self._config_listeners):
            try:
                listener(config)
            except Exception:  # noqa: BLE001 - O-05 boundary
                pass

    # -- ARCH §8.6: hot-path counters are read here, by the worker --------

    def register_aggregate_source(
        self,
        type: str,
        source: Optional[AggregateSource],
        *,
        component: Optional[str] = None,
    ) -> None:
        """Register (or, with ``source=None``, remove) one counter reader.

        ``source`` is called **on the worker thread** at most every
        ``LoggingWorker.AGGREGATE_INTERVAL_S`` seconds and must only read plain
        ``int`` attributes and return either ``None`` (nothing to report right
        now, e.g. no active stream) or a mapping of counters. It must not
        block and must not touch the ingress. Registration is keyed by record
        ``type``, so a re-registration replaces its predecessor instead of
        accumulating readers across controller lifetimes.
        """
        with self._aggregate_lock:
            if source is None:
                self._aggregate_sources.pop(type, None)
            else:
                self._aggregate_sources[type] = (component, source)

    def unregister_aggregate_source(self, type: str) -> None:
        self.register_aggregate_source(type, None)

    def collect_aggregates(self) -> List[Tuple[str, Optional[str], Mapping[str, Any]]]:
        """Only for the worker. Returns ``(type, component, counters)`` for
        every source that had something to report. A raising source is skipped
        and counted as ``malformed`` — a broken counter reader must never take
        the worker loop down (O-05)."""
        with self._aggregate_lock:
            registered = list(self._aggregate_sources.items())
        collected: List[Tuple[str, Optional[str], Mapping[str, Any]]] = []
        for type_, (component, source) in registered:
            try:
                values = source()
            except Exception:  # noqa: BLE001 - O-05 failure isolation
                self.health.record_malformed()
                continue
            if isinstance(values, Mapping) and values:
                collected.append((type_, component, values))
        return collected

    def drain(self, max_items: int, timeout: float) -> List[CanonicalLogRecord]:
        """Only for the worker (OBS-030)."""
        items: List[CanonicalLogRecord] = []
        if max_items <= 0:
            return items
        try:
            items.append(self._queue.get(timeout=max(0.0, timeout)))
        except queue.Empty:
            return items
        while len(items) < max_items:
            try:
                items.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return items


class NullIngress(ObservabilityIngress):
    """Behaviorally equivalent no-op (CONTRACTS §6)."""

    def __init__(self) -> None:
        super().__init__(instance_id="null", enabled=False, level="INFO", queue_size=1)

    def submit(self, record: Any) -> bool:  # noqa: D401
        return False

    def observe_server_result(self, context: Any, result: Any) -> None:
        return None

    def event(
        self,
        type: str,
        *,
        channel: str,
        level: str = "INFO",
        component: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Mapping[str, Any]] = None,
        session_id: Optional[str] = None,
        generation: Optional[int] = None,
        activation_id: Optional[str] = None,
        segment_id: Optional[int] = None,
        command_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        transcription_id: Optional[str] = None,
    ) -> None:
        return None

    def drain(self, max_items: int, timeout: float) -> List[CanonicalLogRecord]:
        return []

    def emit_record_rejected(self, component: str, exc: BaseException) -> None:
        return None

    def apply_config(self, config: Any) -> None:
        """A no-op ingress stays a no-op: re-enabling it through a settings
        apply would turn the "observability is off" wiring into a live one
        without a manager, a worker or a store behind it."""
        return None

    def register_config_listener(self, listener: Callable[[Any], None]) -> None:
        return None

    def register_aggregate_source(
        self,
        type: str,
        source: Optional[AggregateSource],
        *,
        component: Optional[str] = None,
    ) -> None:
        return None

    def collect_aggregates(self) -> List[Tuple[str, Optional[str], Mapping[str, Any]]]:
        return []


NULL_INGRESS = NullIngress()