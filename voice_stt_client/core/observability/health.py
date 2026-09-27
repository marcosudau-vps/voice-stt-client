"""
Health state, counters and the rate-limited emergency stderr channel (OBS-020).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §11.2 (state enum, snapshot
dataclass) and ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §8.1 (recursion locks
G-2/G-4). All counters live under **one** ``threading.Lock``, including
``deduplicated`` (FD-R5). This module must never import ``core.event_models``
or ``core.feedback_reducer`` (ARCH §5.2 / Regel G-5): a logging-internal
failure is never routed through the feedback domain.
"""

from __future__ import annotations

import logging
import sys
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# --- G-2: dedicated, non-propagating logger for everything inside
# core/observability/. Guarded StreamHandler bound to sys.stderr, resolved
# fresh on every emission so a later ``sys.stderr = None`` is handled without
# raising (PyInstaller GUI build).

EMERGENCY_LOGGER_NAME = "observability.internal"

RATE_LIMIT_WINDOW_S = 60.0


class _EmergencyStreamHandler(logging.StreamHandler):
    """Writes to the *current* ``sys.stderr``; never raises (G-4)."""

    def emit(self, record: logging.LogRecord) -> None:  # noqa: D401
        stream = sys.stderr
        if stream is None:
            return
        self.stream = stream
        try:
            super().emit(record)
        except Exception:  # noqa: BLE001 - must never propagate
            pass

    def handleError(self, record: logging.LogRecord) -> None:  # noqa: D401
        # No traceback dump: a broken stderr must stay silent (G-4).
        pass


def _build_emergency_logger() -> logging.Logger:
    logger = logging.getLogger(EMERGENCY_LOGGER_NAME)
    logger.propagate = False
    logger.setLevel(logging.ERROR)
    if not any(isinstance(h, _EmergencyStreamHandler) for h in logger.handlers):
        handler = _EmergencyStreamHandler(sys.stderr if sys.stderr is not None else sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    return logger


_EMERGENCY_LOGGER = _build_emergency_logger()


class _RateLimiter:
    """Hard upper bound: at most one line per code and 60s (G-4), with a
    repeat counter, independent of the actual error count."""

    def __init__(self, window_s: float = RATE_LIMIT_WINDOW_S) -> None:
        self._window = window_s
        self._lock = threading.Lock()
        self._last_emit: dict[str, float] = {}
        self._suppressed_since: dict[str, int] = {}

    def should_emit(self, code: str) -> tuple[bool, int]:
        now = time.monotonic()
        with self._lock:
            last = self._last_emit.get(code)
            if last is None or (now - last) >= self._window:
                count = self._suppressed_since.pop(code, 0) + 1
                self._last_emit[code] = now
                return True, count
            self._suppressed_since[code] = self._suppressed_since.get(code, 0) + 1
            return False, 0


def emergency(code: str, detail: str, *, limiter: Optional[_RateLimiter] = None) -> None:
    """Rate-limited emergency stderr line: ``[observability] <code> (xN): <detail>``.

    At most one line per ``code`` and 60s, unabhaengig von der Fehlerzahl, mit
    Wiederholungszaehler (G-4). Never raises.
    """
    active_limiter = limiter if limiter is not None else _DEFAULT_LIMITER
    try:
        should_emit, count = active_limiter.should_emit(code)
        if not should_emit:
            return
        suffix = f" (x{count})" if count > 1 else ""
        message = f"[observability] {code}{suffix}: {detail}"
        try:
            _EMERGENCY_LOGGER.error(message)
        except Exception:  # noqa: BLE001 - G-4: never let this raise
            pass
    except Exception:  # noqa: BLE001 - defense in depth
        pass


_DEFAULT_LIMITER = _RateLimiter()


# ---------------------------------------------------------------------------
# Health state and snapshot (CONTRACTS §11.2)
# ---------------------------------------------------------------------------


class LoggingHealthState(str, Enum):
    OK = "ok"
    DROPPING = "dropping"
    DEGRADED_SINK = "degraded_sink"
    DEGRADED_STORE = "degraded_store"
    FAILED_STORE = "failed_store"
    FAILED_WORKER = "failed_worker"
    DISABLED = "disabled"


_FAILED_STATES = frozenset({LoggingHealthState.FAILED_STORE, LoggingHealthState.FAILED_WORKER})


@dataclass(frozen=True)
class LoggingHealthSnapshot:
    state: LoggingHealthState
    since: Optional[float]  # time.monotonic()
    detail: str  # kurz, REDIGIERT
    enqueued: int
    written: int
    deduplicated: int
    dropped_watermark: int
    dropped_queue_full: int
    dropped_shutdown: int
    malformed: int
    store_errors: int
    sink_errors: int
    retention_errors: int
    worker_errors: int
    queue_depth: int
    db_bytes: Optional[int]


class LoggingInternalHealth:
    """All counters live under **one** lock (WP-OBS-020 Implementierungsschritt 4).

    ``written``/``deduplicated``/``store_errors``/``sink_errors``/
    ``retention_errors``/``db_bytes`` are fed by the future worker (OBS-030);
    this class already carries them so the snapshot never needs a shape
    change. Nothing here writes to stderr except through the rate-limited
    ``emergency()`` path (G-4); routine drops (watermark/queue-full) are
    counter-only, never logged (ARCH §8.3).
    """

    def __init__(self, *, limiter: Optional[_RateLimiter] = None) -> None:
        self._lock = threading.Lock()
        self._limiter = limiter if limiter is not None else _RateLimiter()
        self._state = LoggingHealthState.OK
        self._since: Optional[float] = None
        self._detail = ""
        self._enqueued = 0
        self._written = 0
        self._deduplicated = 0
        self._dropped_watermark = 0
        self._dropped_queue_full = 0
        self._dropped_shutdown = 0
        self._malformed = 0
        self._store_errors = 0
        self._sink_errors = 0
        self._retention_errors = 0
        self._worker_errors = 0
        self._queue_depth_fn = None
        self._db_bytes: Optional[int] = None

    # -- state -----------------------------------------------------------

    @property
    def state(self) -> LoggingHealthState:
        with self._lock:
            return self._state

    def is_failed(self) -> bool:
        with self._lock:
            return self._state in _FAILED_STATES

    def set_state(self, state: LoggingHealthState, detail: str = "") -> None:
        with self._lock:
            if state != self._state:
                self._since = time.monotonic()
            self._state = state
            self._detail = detail

    # -- counters ----------------------------------------------------------

    def record_enqueued(self) -> None:
        with self._lock:
            self._enqueued += 1

    def record_dropped_watermark(self) -> None:
        with self._lock:
            self._dropped_watermark += 1

    def record_dropped_queue_full(self) -> None:
        with self._lock:
            self._dropped_queue_full += 1

    def reset_drop_counters(self) -> tuple[int, int]:
        """Snapshot-and-reset ``dropped_watermark``/``dropped_queue_full``,
        used by the worker's backpressure-recovery record (ARCH §7.3)."""
        with self._lock:
            watermark, queue_full = self._dropped_watermark, self._dropped_queue_full
            self._dropped_watermark = 0
            self._dropped_queue_full = 0
            return watermark, queue_full

    def record_dropped_shutdown(self, count: int = 1) -> None:
        with self._lock:
            self._dropped_shutdown += count

    def record_malformed(self) -> None:
        with self._lock:
            self._malformed += 1

    def record_written(self, count: int = 1) -> None:
        with self._lock:
            self._written += count

    def record_deduplicated(self, count: int = 1) -> None:
        with self._lock:
            self._deduplicated += count

    def record_worker_error(self, code: str = "worker_error", detail: str = "") -> None:
        with self._lock:
            self._worker_errors += 1
        emergency(code, detail, limiter=self._limiter)

    def record_store_error(self, code: str = "store_error", detail: str = "") -> None:
        with self._lock:
            self._store_errors += 1
        emergency(code, detail, limiter=self._limiter)

    def record_sink_error(self, code: str = "sink_error", detail: str = "") -> None:
        with self._lock:
            self._sink_errors += 1
        emergency(code, detail, limiter=self._limiter)

    def record_retention_error(self, code: str = "retention_error", detail: str = "") -> None:
        with self._lock:
            self._retention_errors += 1
        emergency(code, detail, limiter=self._limiter)

    def set_db_bytes(self, value: Optional[int]) -> None:
        with self._lock:
            self._db_bytes = value

    # -- snapshot ------------------------------------------------------------

    def snapshot(self, *, queue_depth: int = 0) -> LoggingHealthSnapshot:
        with self._lock:
            return LoggingHealthSnapshot(
                state=self._state,
                since=self._since,
                detail=self._detail,
                enqueued=self._enqueued,
                written=self._written,
                deduplicated=self._deduplicated,
                dropped_watermark=self._dropped_watermark,
                dropped_queue_full=self._dropped_queue_full,
                dropped_shutdown=self._dropped_shutdown,
                malformed=self._malformed,
                store_errors=self._store_errors,
                sink_errors=self._sink_errors,
                retention_errors=self._retention_errors,
                worker_errors=self._worker_errors,
                queue_depth=queue_depth,
                db_bytes=self._db_bytes,
            )
