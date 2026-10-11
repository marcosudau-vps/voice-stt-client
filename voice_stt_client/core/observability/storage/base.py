"""
Log store boundary (OBS-010).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §5.5 (``write_batch``) and
FD-S4 (``clear``). Storage knows only the model. Signatures only — OBS-030
implements ``SQLiteLogStore``.
"""

from __future__ import annotations

from typing import Protocol, Sequence

from ..models import CanonicalLogRecord


class LogStore(Protocol):
    """The single persistence write path: Ingress -> Worker -> Store (O-14).
    Providers never write."""

    def write_batch(
        self, records: Sequence[CanonicalLogRecord]
    ) -> tuple[int, int]:
        """Persist one batch. Returns ``(eingefuegt, dedupliziert)``."""
        ...

    def clear(self) -> int:
        """Delete all rows and checkpoint (Diagnosehistorie loeschen, FD-S4)."""
        ...