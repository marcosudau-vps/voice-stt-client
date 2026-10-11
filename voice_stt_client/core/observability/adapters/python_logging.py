"""
``UnifiedLogHandler`` — the third, additive ``logging.Handler`` (OBS-020).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §3.1/§6 and
``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §8.1 (recursion locks G-1/G-3/G-7).
``emit`` never calls ``format()`` and performs no I/O of its own: it only
normalizes the ``LogRecord`` and hands the canonical record to the ingress,
which itself never blocks and never raises.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Callable, Optional

from ..health import LoggingInternalHealth
from ..models import CanonicalLogRecord

# G-2/redundancy: records from the emergency logger itself must never be
# re-normalized and re-submitted, even though it already has
# ``propagate = False``. Filtering here is cheap insurance against a future
# ``propagate`` regression.
INTERNAL_LOGGER_NAME = "observability.internal"


class _InternalLoggerFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        name = record.name
        return name != INTERNAL_LOGGER_NAME and not name.startswith(
            INTERNAL_LOGGER_NAME + "."
        )


class UnifiedLogHandler(logging.Handler):
    """Normalizes every accepted ``LogRecord`` and submits it to the ingress.

    ``normalize`` is a ``Callable[[logging.LogRecord],
    Optional[CanonicalLogRecord]]`` bound by the caller (``core/logging_setup.py``)
    to a fixed ``instance_id``/``store_transcription_content``/``user_profile``
    — the handler itself holds no runtime state and queries none (CONTRACTS
    §3.1 / FD-R8).
    """

    def __init__(
        self,
        ingress: Any,
        normalize: Callable[[logging.LogRecord], Optional[CanonicalLogRecord]],
        *,
        health: Optional[LoggingInternalHealth] = None,
    ) -> None:
        super().__init__()
        self._ingress = ingress
        self._normalize = normalize
        self._health = health if health is not None else getattr(ingress, "health", None)
        self._reentrant = threading.local()
        self.addFilter(_InternalLoggerFilter())

    def emit(self, record: logging.LogRecord) -> None:
        # G-1: reentrancy lock. Covers "Weg 1" (Store -> logs -> root logger
        # -> this handler -> queue -> worker -> Store ...) and "Weg 3"
        # (normalizer raises -> logger.exception -> same path).
        if getattr(self._reentrant, "active", False):
            return
        self._reentrant.active = True
        try:
            try:
                canonical = self._normalize(record)
            except Exception as exc:  # noqa: BLE001 - the normalizer must never break the app
                self._handle_exception(record, exc)
                return
            if canonical is None:
                if self._health is not None:
                    self._health.record_malformed()
                return
            try:
                self._ingress.submit(canonical)
            except Exception as exc:  # noqa: BLE001
                self._handle_exception(record, exc)
        finally:
            self._reentrant.active = False

    def handleError(self, record: logging.LogRecord) -> None:
        # G-3: report to Health instead of stderr. Counter-only, no
        # emergency stderr line here (ARCH §8.3 names no stderr row for a
        # normalizer/handler-level failure; Health stays OK and only
        # ``malformed`` increases).
        if self._health is not None:
            self._health.record_malformed()

    def _handle_exception(self, record: logging.LogRecord, exc: BaseException) -> None:
        """``handleError`` plus the substitute record ``ARCH §8.3`` requires.

        The stdlib signature of ``handleError`` carries no exception, so the
        substitute record — which must name the exception **type** and nothing
        from the original record — is produced here (gate observation N-1).
        """
        self.handleError(record)
        reject = getattr(self._ingress, "emit_record_rejected", None)
        if reject is None:
            return
        try:
            reject("observability.adapters.python_logging", exc)
        except Exception:  # noqa: BLE001 - the error path itself never raises
            pass

    def flush(self) -> None:
        # G-7: no-op. ``logging.shutdown()`` runs via ``atexit`` and calls
        # flush()+close() on every handler; the daemon worker may already be
        # frozen by then. A waiting flush would be a shutdown deadlock.
        pass

    def close(self) -> None:
        # G-7: no-op, for the same reason. The real flush happens exclusively
        # through the future ``manager.stop()`` (OBS-030).
        pass
