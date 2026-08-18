"""
``LoggingWorker`` — the single dedicated daemon thread that turns queued
``CanonicalLogRecord``s into persisted rows (OBS-030).

Frozen source: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §5 (component picture),
§6.1/§6.2/§6.3/§6.4 (thread model, lifecycle, non-blocking invariant, daemon),
§7 (backpressure/priority/counters), §8 (failure domain, G-2/G-4/G-6),
``LOGGING_CONTRACTS_FREEZE_V1.md`` §5.4-§5.6 (connection ownership,
write_batch/dedupe, retention cadence), §8.2 (raw redaction happens here),
§11.1 (sink ordering after commit), §11.2 (health/recovery).

D-4 (OBS-000 correction): the store's SQLite connection is created **inside
this thread**'s ``run()``, never by the caller. The worker never blocks a
producer thread; ``ingress.drain()`` is the only thing that may block, and
only this thread.
"""

from __future__ import annotations

import dataclasses
import json
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Optional, Sequence
from uuid import uuid4

from .health import LoggingHealthState, LoggingInternalHealth, emergency
from .models import CanonicalLogRecord, level_rank
from .redaction import redact_mapping

MAX_RAW_BYTES = 64 * 1024
# ARCH §8.6: "Der Aggregatrecord entsteht im WORKER, der die Zaehler LIEST:
# client.audio.stream_stats, Channel 'performance', Level DEBUG, alle 5 s
# waehrend aktiven Streamings".
AGGREGATE_INTERVAL_S = 5.0
RETENTION_INTERVAL_S = 60.0
RETENTION_RECORD_INTERVAL = 2000
RETENTION_TIME_BUDGET_S = 0.2
STORE_FAILURE_THRESHOLD = 5
STORE_PAUSE_S = 60.0
# ARCH §8.3: "Kein Neustartversuch -- ein Worker, der zweimal stirbt, stirbt
# beim dritten Mal auch." Single failures are caught and the loop continues;
# after this many CONSECUTIVE loop failures the loop gives up for good and the
# ingress switches to "nur verwerfen und zaehlen" (FAILED_WORKER).
WORKER_FAILURE_THRESHOLD = 5
WATERMARK_HIGH_RATIO = 0.75
WATERMARK_RECOVERY_RATIO = 0.25
WATERMARK_RECOVERY_HOLD_S = 5.0
SHUTDOWN_FLUSH_DEFAULT_S = 2.0


def _now_iso() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond // 1000:03d}Z"


def _looks_like_disk_full(exc: Optional[BaseException]) -> bool:
    if exc is None:
        return False
    text = str(exc).lower()
    return "disk" in text and "full" in text


class LoggingWorker(threading.Thread):
    """``threading.Thread("RealtimeSTT-Observability", daemon=True)``
    (ARCH §6.1). Owns the sole SQLite write connection and the optional
    sink. ``stop(timeout)`` is the only explicit flush guarantee (G-7: the
    Python logging handler's ``flush()``/``close()`` are no-ops)."""

    def __init__(
        self,
        ingress: Any,
        store: Any,
        *,
        health: Optional[LoggingInternalHealth] = None,
        sink: Optional[Any] = None,
        batch_size: int = 200,
        flush_interval_s: float = 0.5,
        retention_days: int = 14,
        max_entries: int = 200_000,
        max_db_bytes: Optional[int] = None,
        queue_size: int = 8192,
        store_transcription_content: bool = False,
        user_profile: Any = None,
        watermark_recovery_hold_s: float = WATERMARK_RECOVERY_HOLD_S,
    ) -> None:
        super().__init__(name="RealtimeSTT-Observability", daemon=True)
        self._ingress = ingress
        self._store = store
        self._health = health if health is not None else getattr(ingress, "health", None) or LoggingInternalHealth()
        self._sink = sink
        self._batch_size = max(1, int(batch_size))
        self._flush_interval_s = max(0.01, float(flush_interval_s))
        self._retention_days = retention_days
        self._max_entries = max_entries
        self._max_db_bytes = max_db_bytes
        self._queue_size = max(1, int(queue_size))
        self._store_transcription_content = store_transcription_content
        self._user_profile = user_profile
        self._watermark_recovery_hold_s = max(0.0, float(watermark_recovery_hold_s))

        self._stop_event = threading.Event()
        self._stopped = threading.Event()
        self._shutdown_deadline: Optional[float] = None

        self._records_since_retention = 0
        self._last_retention_at = 0.0
        self._retention_suspended = False
        self._structural_degraded = False

        self._consecutive_store_failures = 0
        self._store_paused_until: Optional[float] = None
        self._below_recovery_since: Optional[float] = None
        self._consecutive_loop_failures = 0
        self._worker_failed = False
        self._retention_pressure_active = False
        self._last_aggregate_at = 0.0

        # CONTRACTS §10.3 (OBS-050): retention_days, max_entries and the file
        # sink are IMMEDIATE settings, but they live on this thread. A caller
        # from the Qt thread therefore only *deposits* them; the worker picks
        # them up at the top of its own loop, so a sink is never opened or
        # closed underneath a write in progress.
        self._settings_lock = threading.Lock()
        self._pending_settings: dict[str, Any] = {}

        self._clear_lock = threading.Lock()
        self._clear_pending = False
        self._clear_done = threading.Event()
        self._clear_result = 0
        self._clear_error: Optional[BaseException] = None

    # -- lifecycle -----------------------------------------------------------

    def run(self) -> None:
        """Every step is inside a guard. An exception escaping ``run()``
        would reach ``threading``'s excepthook, which dumps a **full,
        unfiltered and unrate-limited traceback to stderr** — exactly the
        output path G-2/G-4 exclude for everything under
        ``core/observability/``. ARCH §8.3 for the loop itself: a single
        exception is caught, ``worker_errors++``, the loop continues."""
        try:
            self._open_store()
        except Exception as exc:  # noqa: BLE001 - failure isolation boundary
            self._record_loop_failure("worker_open_failed", exc)
        try:
            self._run_retention_if_due(force=True)
        except Exception as exc:  # noqa: BLE001
            self._record_loop_failure("worker_retention_failed", exc)
        try:
            while not self._stop_event.is_set():
                try:
                    self._iteration()
                except Exception as exc:  # noqa: BLE001 - ARCH §8.3
                    if self._record_loop_failure("worker_loop_failed", exc):
                        break
                else:
                    self._consecutive_loop_failures = 0
        finally:
            self._finish()

    def _record_loop_failure(self, code: str, exc: BaseException) -> bool:
        """``worker_errors++`` through the observability-internal error path
        (G-2/G-4 via ``LoggingInternalHealth.record_worker_error`` →
        rate-limited ``emergency()``). Returns ``True`` when the loop must
        give up (ARCH §8.3: "Kein Neustartversuch")."""
        self._consecutive_loop_failures += 1
        try:
            self._health.record_worker_error(code, str(exc)[:200])
        except Exception:  # noqa: BLE001 - the error path itself never raises
            pass
        if self._consecutive_loop_failures >= WORKER_FAILURE_THRESHOLD:
            self._worker_failed = True
            return True
        return False

    def _finish(self) -> None:
        """Runs on every exit path of ``run()``. Never raises."""
        if self._worker_failed:
            # ARCH §8.3: "Bricht sie dennoch ab: Ingress wechselt in 'nur
            # verwerfen und zaehlen'." Set BEFORE the flush, so from this
            # moment on ``Ingress.is_failed()`` is true and no producer is
            # ever told "accepted" for a record that would then strand in a
            # queue nobody drains any more.
            try:
                self._health.set_state(
                    LoggingHealthState.FAILED_WORKER,
                    "worker loop aborted after repeated failures; no restart (ARCH §8.3)",
                )
            except Exception:  # noqa: BLE001
                pass
        try:
            self._shutdown_flush()
        except Exception as exc:  # noqa: BLE001
            self._record_loop_failure("worker_shutdown_failed", exc)
        try:
            self._store.close()
        except Exception:  # noqa: BLE001 - shutdown must never raise
            pass
        if self._sink is not None:
            try:
                self._sink.close()
            except Exception:  # noqa: BLE001
                pass
        self._stopped.set()

    def stop(self, timeout: float = SHUTDOWN_FLUSH_DEFAULT_S) -> bool:
        """Signal shutdown, wait up to ``timeout`` for the flush to finish.
        Beyond the deadline, unflushed records are dropped and counted
        (``dropped_shutdown``) rather than blocking the process exit. A
        worker that was never ``start()``-ed is trivially "stopped" — but its
        queue content is still dropped **and counted**, never silently lost."""
        budget = max(0.0, float(timeout))
        self._shutdown_deadline = time.monotonic() + budget
        self._stop_event.set()
        if not self.ident and not self.is_alive():
            self._drain_and_count_leftovers()
            return True
        self.join(timeout=budget + 1.0)
        return not self.is_alive()

    # -- store open / migration -------------------------------------------

    def _open_store(self) -> None:
        try:
            result = self._store.open()
        except Exception as exc:  # noqa: BLE001 - failure isolation boundary
            self._health.set_state(LoggingHealthState.FAILED_STORE, str(exc)[:200])
            emergency("store_open_failed", str(exc)[:200])
            return
        if result.ok and not result.degraded:
            self._health.set_state(LoggingHealthState.OK)
        elif result.degraded:
            self._structural_degraded = True
            self._health.set_state(LoggingHealthState.DEGRADED_STORE, result.detail)
        else:
            self._health.set_state(LoggingHealthState.FAILED_STORE, result.detail)
            emergency("store_open_failed", result.detail)

    # -- main loop -----------------------------------------------------------

    def _iteration(self) -> None:
        self._apply_pending_settings()
        records = self._ingress.drain(self._batch_size, self._flush_interval_s)
        if records:
            self._process_batch(records)
        if self._clear_pending:
            self._handle_clear_request()
        self._emit_aggregates_if_due()
        self._run_retention_if_due(force=False)
        self._check_backpressure_state()

    def _shutdown_flush(self) -> None:
        deadline = self._shutdown_deadline
        if deadline is None:
            deadline = time.monotonic() + SHUTDOWN_FLUSH_DEFAULT_S
        while time.monotonic() < deadline:
            try:
                records = self._ingress.drain(self._batch_size, 0.0)
            except Exception as exc:  # noqa: BLE001 - a broken drain must not
                # turn the shutdown into an unhandled thread exception.
                self._record_loop_failure("worker_drain_failed", exc)
                break
            if not records:
                break
            try:
                self._process_batch(records)
            except Exception as exc:  # noqa: BLE001
                self._record_loop_failure("worker_flush_failed", exc)
                self._health.record_dropped_shutdown(len(records))
                break
        if self._clear_pending:
            self._handle_clear_request()
        self._drain_and_count_leftovers()

    def _drain_and_count_leftovers(self) -> None:
        """Whatever is still queued when the worker goes away is dropped
        **and counted** (``dropped_shutdown``) plus exactly one rate-limited
        stderr line (ARCH §8.3, Shutdown-Zeile). Never raises."""
        try:
            leftover = len(self._ingress.drain(1_000_000, 0.0))
        except Exception:  # noqa: BLE001 - if even draining is broken, fall
            # back to the queue depth: the records are lost either way, and
            # losing them *uncounted* is exactly the blind spot §7.3/§8 rule
            # out.
            leftover = self._safe_qsize()
        if leftover:
            self._health.record_dropped_shutdown(leftover)
            emergency("shutdown_flush_incomplete", f"{leftover} records dropped at shutdown")

    # -- batch processing ------------------------------------------------

    def _process_batch(self, records: Sequence[CanonicalLogRecord]) -> None:
        prepared = [self._prepare_record(record) for record in records]
        inserted, deduplicated, ok = self._write_with_policy(prepared)
        if ok:
            self._health.record_written(inserted)
            self._health.record_deduplicated(deduplicated)
            # CONTRACTS §5.6: retention is due "alle 2000 **geschriebenen**
            # Records" — drawn records that never reached the store do not
            # count (gate finding W-7).
            self._records_since_retention += inserted
        # O-05 / ARCH §8.3: the JSONL sink is its own failure domain. §11.1
        # fixes the ORDER ("write_batch ZUERST, Sink DANACH -- damit ein
        # Sink-Fehler nie einen SQLite-Rollback ausloest"), not a condition.
        # A degraded, suspended or read-only store must not silently take the
        # intact sink down with it (gate finding W-1).
        self._write_sink(prepared)

    def _prepare_record(self, record: CanonicalLogRecord) -> CanonicalLogRecord:
        """ARCH §8.2: raw payloads of incoming server events are unfrozen,
        redacted and size-capped **here**, in the worker — never in the
        producer thread. ``details`` is already redacted at ingress time by
        the normalizer (CONTRACTS §3.3) and needs no further processing."""
        if record.raw is None:
            return record
        try:
            redacted = redact_mapping(
                record.raw,
                store_transcription_content=self._store_transcription_content,
                user_profile=self._user_profile,
            )
            serialized = json.dumps(redacted, ensure_ascii=False)
            size = len(serialized.encode("utf-8"))
            if size > MAX_RAW_BYTES:
                redacted = {"_truncated": True, "_bytes": size}
            # ``dataclasses.replace`` stays INSIDE the guard: it is a real
            # exit path out of the protected region (gate finding B-1) — it
            # raises for anything that is not a plain dataclass instance and
            # re-runs ``__post_init__``, which re-freezes the mapping.
            return dataclasses.replace(record, raw=redacted)
        except Exception:  # noqa: BLE001 - never let a bad raw payload crash the worker
            self._health.record_malformed()
        try:
            return dataclasses.replace(record, raw={"_truncated": True, "_bytes": -1})
        except Exception:  # noqa: BLE001 - last resort: pass the record through
            return record

    # -- store write policy: retry-once, circuit breaker, disk-full -----

    def _write_with_policy(self, records: Sequence[CanonicalLogRecord]) -> tuple[int, int, bool]:
        if self._structural_degraded:
            return (0, 0, False)
        if self._store_paused_until is not None:
            if time.monotonic() < self._store_paused_until:
                return (0, 0, False)
            # ARCH §8.3: after the 60 s suspension the store is re-checked
            # "mit einem leeren Testschreibvorgang" — a probe, so a still
            # broken store costs a probe and not this batch (W-4).
            if not self._probe_store():
                self._store_paused_until = time.monotonic() + STORE_PAUSE_S
                return (0, 0, False)
            self._store_paused_until = None

        last_exc: Optional[BaseException] = None
        for _attempt in range(2):
            try:
                inserted, deduplicated = self._store.write_batch(records)
            except Exception as exc:  # noqa: BLE001 - O-05 failure isolation
                last_exc = exc
                continue
            self._on_store_write_success()
            return (inserted, deduplicated, True)

        self._on_store_write_failure(last_exc)
        return (0, 0, False)

    def _probe_store(self) -> bool:
        """The empty test write of ARCH §8.3. A store double without
        ``probe_write`` (or one that raises) is treated as "probe passed",
        so the pause behaves exactly as before for such a store instead of
        never resuming."""
        probe = getattr(self._store, "probe_write", None)
        if probe is None:
            return True
        try:
            return bool(probe())
        except Exception:  # noqa: BLE001 - O-05 failure isolation
            return False

    def _on_store_write_success(self) -> None:
        was_paused = self._store_paused_until is not None
        self._consecutive_store_failures = 0
        self._store_paused_until = None
        self._retention_suspended = False
        if self._health.state in (LoggingHealthState.DEGRADED_STORE, LoggingHealthState.FAILED_STORE):
            self._health.set_state(LoggingHealthState.OK)
            self._emit_recovery_record()
        elif was_paused:
            self._emit_recovery_record()

    def _on_store_write_failure(self, exc: Optional[BaseException]) -> None:
        self._consecutive_store_failures += 1
        disk_full = _looks_like_disk_full(exc)
        detail = str(exc)[:200] if exc is not None else "unknown store error"
        code = "store_disk_full" if disk_full else "store_write_failed"
        self._health.record_store_error(code, detail)
        if disk_full:
            self._retention_suspended = True
            self._store_paused_until = time.monotonic() + STORE_PAUSE_S
            self._health.set_state(LoggingHealthState.FAILED_STORE, detail)
        elif self._consecutive_store_failures >= STORE_FAILURE_THRESHOLD:
            self._store_paused_until = time.monotonic() + STORE_PAUSE_S
            self._health.set_state(LoggingHealthState.FAILED_STORE, detail)
        else:
            self._health.set_state(LoggingHealthState.DEGRADED_STORE, detail)

    def _emit_recovery_record(self) -> None:
        snapshot = self._health.snapshot(queue_depth=self._safe_qsize())
        record = self._build_internal_record(
            type_="logging.recovered",
            details={
                "store_errors": snapshot.store_errors,
                "sink_errors": snapshot.sink_errors,
                "worker_errors": snapshot.worker_errors,
            },
        )
        self._write_direct(record)

    # -- sink -------------------------------------------------------------

    def _write_sink(self, records: Sequence[CanonicalLogRecord]) -> None:
        if self._sink is None:
            return
        try:
            self._sink.write_batch(records)
        except Exception as exc:  # noqa: BLE001 - O-05 failure isolation
            self._health.record_sink_error("sink_write_failed", str(exc)[:200])
            self._health.set_state(LoggingHealthState.DEGRADED_SINK, str(exc)[:200])
            self._sink = None

    # -- backpressure state + recovery record (ARCH §7.1-§7.3) -----------

    def _check_backpressure_state(self) -> None:
        qsize = self._safe_qsize()
        high = self._queue_size * WATERMARK_HIGH_RATIO
        low = self._queue_size * WATERMARK_RECOVERY_RATIO
        now = time.monotonic()

        if qsize >= high:
            self._below_recovery_since = None
            if self._health.state == LoggingHealthState.OK:
                self._health.set_state(LoggingHealthState.DROPPING, "queue at/above watermark")
            return

        if qsize >= low:
            self._below_recovery_since = None
            return

        if self._below_recovery_since is None:
            self._below_recovery_since = now
            return
        if now - self._below_recovery_since < self._watermark_recovery_hold_s:
            return

        if self._health.state == LoggingHealthState.DROPPING:
            self._health.set_state(LoggingHealthState.OK)
        watermark, queue_full = self._health.reset_drop_counters()
        if watermark or queue_full:
            record = self._build_internal_record(
                type_="logging.records_dropped",
                details={"dropped_watermark": watermark, "dropped_queue_full": queue_full},
            )
            self._write_direct(record)

    def _safe_qsize(self) -> int:
        try:
            return int(self._ingress.qsize())
        except Exception:  # noqa: BLE001
            return 0

    # -- hot-path aggregates (ARCH §8.6, CONTRACTS §12.4) ------------------

    def _emit_aggregates_if_due(self) -> None:
        """Read the registered producer counters and write one aggregate record
        per source, at most every ``AGGREGATE_INTERVAL_S`` seconds.

        This is the whole reason the hot path may stay at *"ausschliesslich
        einfache int-Attribute erhoehen"* (ARCH §8.6): at 40 ms chunks a record
        per chunk would be ~90.000 records per hour of dictation. A source that
        returns ``None``/empty reports nothing, which is how *"waehrend aktiven
        Streamings"* is expressed — an idle producer produces no record instead
        of a stream of zeroes.

        Written directly to store and sink, bypassing handler and queue (G-6),
        because the worker is the producer here. The ingress **level** still
        applies (ARCH §8.7: *"Ingress-Level gilt fuer strukturierte
        Clientevents"*), so the frozen ``DEBUG`` level of these records is
        filtered exactly as it would be on the normal path — a default
        ``level: INFO`` installation does not silently collect DEBUG stats.
        Never raises: an exception here would be a worker loop failure over a
        diagnostic aggregate.
        """
        now = time.monotonic()
        if now - self._last_aggregate_at < AGGREGATE_INTERVAL_S:
            return
        self._last_aggregate_at = now
        collect = getattr(self._ingress, "collect_aggregates", None)
        if collect is None:
            return
        try:
            collected = collect()
        except Exception:  # noqa: BLE001 - O-05 failure isolation
            return
        if not collected:
            return
        if level_rank("DEBUG") < level_rank(getattr(self._ingress, "level", "INFO")):
            return
        for type_, component, values in collected:
            try:
                record = self._build_aggregate_record(type_, component, values)
            except Exception:  # noqa: BLE001
                self._health.record_malformed()
                continue
            self._write_direct(record)

    def _build_aggregate_record(
        self, type_: str, component: Optional[str], values: Mapping[str, Any]
    ) -> CanonicalLogRecord:
        """Channel ``performance``, level ``DEBUG`` (ARCH §8.6).

        ``is_internal`` stays ``False``: the record describes the *client*, not
        the logging subsystem, and §1.5 reserves the internal flag (and with it
        unconditional ``HIGH`` priority) for logging's own records. Priority is
        therefore derived normally — ``type`` is set, so an unreplayed
        aggregate is ``HIGH`` anyway.
        """
        instance_id = getattr(self._ingress, "instance_id", None) or "unknown"
        return CanonicalLogRecord(
            record_id=uuid4().hex,
            received_at=_now_iso(),
            producer_kind="client",
            producer_id="voice-stt-client",
            instance_id=instance_id,
            scope="instance",
            channel="performance",
            level="DEBUG",
            replayed=False,
            type=type_,
            component=component,
            details=dict(values),
        )

    # -- retention (CONTRACTS §5.6) ---------------------------------------

    def _run_retention_if_due(self, *, force: bool) -> None:
        if self._retention_suspended or self._structural_degraded:
            return
        now = time.monotonic()
        due = (
            force
            or (now - self._last_retention_at >= RETENTION_INTERVAL_S)
            or (self._records_since_retention >= RETENTION_RECORD_INTERVAL)
        )
        if not due:
            return
        self._last_retention_at = now
        self._records_since_retention = 0

        cutoff_iso = None
        if self._retention_days and self._retention_days > 0:
            cutoff_dt = datetime.now(timezone.utc) - timedelta(days=self._retention_days)
            cutoff_iso = cutoff_dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{cutoff_dt.microsecond // 1000:03d}Z"
        max_entries = self._max_entries if self._max_entries and self._max_entries > 0 else None

        try:
            self._store.run_retention(
                cutoff_iso=cutoff_iso,
                max_entries=max_entries,
                time_budget_s=RETENTION_TIME_BUDGET_S,
            )
        except Exception as exc:  # noqa: BLE001 - O-05 failure isolation
            self._health.record_retention_error("retention_failed", str(exc)[:200])
            return

        try:
            db_bytes = self._store.measure_db_bytes()
        except Exception:  # noqa: BLE001
            db_bytes = None
        self._health.set_db_bytes(db_bytes)
        self._report_retention_pressure(db_bytes)

    def _report_retention_pressure(self, db_bytes: Optional[int]) -> None:
        """FD-D8 / CONTRACTS §5.6: exceeding ``max_db_bytes`` is a pure
        warning signal — measure, never intervene. §12.4 lists
        ``logging.retention_pressure`` alongside ``logging.records_dropped``
        and ``logging.recovered`` as a structured record **produced by the
        worker**; a stderr line alone was the inconsistency W-2. Written
        directly, bypassing handler and queue (G-6), and edge-triggered so a
        persistently oversized database cannot produce a record per retention
        run."""
        over = (
            db_bytes is not None
            and bool(self._max_db_bytes)
            and self._max_db_bytes > 0
            and db_bytes > self._max_db_bytes
        )
        if not over:
            self._retention_pressure_active = False
            return
        if self._retention_pressure_active:
            return
        self._retention_pressure_active = True
        emergency(
            "retention_pressure",
            f"db_bytes={db_bytes} exceeds max_db_bytes={self._max_db_bytes}",
        )
        self._write_direct(
            self._build_internal_record(
                type_="logging.retention_pressure",
                details={"db_bytes": db_bytes, "max_db_bytes": self._max_db_bytes},
                level="WARNING",
            )
        )

    # -- runtime settings (CONTRACTS §10.3, IMMEDIATE) ---------------------

    def request_settings(self, **settings: Any) -> None:
        """Deposit worker-owned settings for the worker to pick up itself.

        Accepted keys: ``retention_days``, ``max_entries`` and ``sink`` (a
        sink instance, or ``None`` to switch the file sink off). Only keys
        that are actually passed are changed, so "switch the sink off" and
        "leave the sink alone" stay distinguishable. Thread-safe, never
        raises, returns nothing — the caller is an apply chain that must not
        be influenced by the logging domain (§10.4, O-01).
        """
        try:
            with self._settings_lock:
                self._pending_settings.update(settings)
        except Exception:  # noqa: BLE001 - O-05 boundary
            pass

    def _apply_pending_settings(self) -> None:
        """Runs on the worker thread only. A sink replaced here is closed
        here, by the thread that owns it (ARCH §6.4: sinks write in the
        worker, never in a thread of their own)."""
        with self._settings_lock:
            if not self._pending_settings:
                return
            pending = self._pending_settings
            self._pending_settings = {}
        if "retention_days" in pending:
            self._retention_days = pending["retention_days"]
        if "max_entries" in pending:
            self._max_entries = pending["max_entries"]
        if "max_db_bytes" in pending:
            self._max_db_bytes = pending["max_db_bytes"]
        if "store_transcription_content" in pending:
            self._store_transcription_content = bool(
                pending["store_transcription_content"]
            )
        if "sink" in pending:
            new_sink = pending["sink"]
            old_sink = self._sink
            if new_sink is not old_sink:
                self._sink = new_sink
                if old_sink is not None:
                    try:
                        old_sink.close()
                    except Exception:  # noqa: BLE001 - closing must never
                        # take the loop down; the file handle is released by
                        # the interpreter at the latest.
                        pass

    # -- "Diagnosehistorie loeschen" (FD-S4) -------------------------------

    def request_clear(self, timeout: float = 5.0) -> int:
        """Thread-safe request to run ``store.clear()``. Executes on this
        (the worker) thread — the sole owner of the write connection
        (CONTRACTS §5.4) — never on the caller's thread."""
        with self._clear_lock:
            self._clear_done.clear()
            self._clear_error = None
            self._clear_pending = True
        completed = self._clear_done.wait(timeout=max(0.0, timeout))
        if not completed:
            raise TimeoutError("clear_history did not complete in time")
        if self._clear_error is not None:
            raise self._clear_error
        return self._clear_result

    def _handle_clear_request(self) -> None:
        with self._clear_lock:
            self._clear_pending = False
        try:
            self._clear_result = self._store.clear()
            self._clear_error = None
        except Exception as exc:  # noqa: BLE001 - O-05 failure isolation
            self._clear_error = exc
            self._clear_result = 0
            self._health.record_store_error("store_clear_failed", str(exc)[:200])
        finally:
            self._clear_done.set()

    # -- internal records (G-6: written directly, bypassing the queue) ----

    def _build_internal_record(
        self, *, type_: str, details: Mapping[str, Any], level: str = "INFO"
    ) -> CanonicalLogRecord:
        instance_id = getattr(self._ingress, "instance_id", None) or "unknown"
        return CanonicalLogRecord(
            record_id=uuid4().hex,
            received_at=_now_iso(),
            producer_kind="client",
            producer_id="voice-stt-client",
            instance_id=instance_id,
            scope="instance",
            channel="performance",
            level=level,
            replayed=False,
            type=type_,
            component="observability.worker",
            details=details,
            is_internal=True,
        )

    def _write_direct(self, record: CanonicalLogRecord) -> None:
        try:
            self._store.write_batch([record])
        except Exception:  # noqa: BLE001 - internal records must never crash the worker
            pass
        if self._sink is not None:
            try:
                self._sink.write_batch([record])
            except Exception:  # noqa: BLE001
                pass
