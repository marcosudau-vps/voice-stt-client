"""
Sink boundary (OBS-010).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §11.1 and ARCH §5.1/§6.
Sinks know only the model and run inside the worker thread; a sink failure
must never trigger a SQLite rollback (store batch runs first).
"""

from __future__ import annotations

from typing import Protocol, Sequence

from ..models import CanonicalLogRecord


class Sink(Protocol):
    """An optional serialization target for canonical records."""

    def write_batch(self, records: Sequence[CanonicalLogRecord]) -> None:
        """Persist one batch (e.g. one JSONL line per record)."""
        ...

    def close(self) -> None:
        """Release resources. No-ops are allowed."""
        ...