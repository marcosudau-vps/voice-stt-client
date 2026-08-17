"""
``JsonlSink`` — the V1 optional JSONL sink (OBS-030).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §11.1 (schemaVersion first,
daily rotation, size limit, worker-order: store commit first). Sinks know
only the model (ARCH §5.2) — no ``sqlite3``, no redaction policy import.

Runs exclusively inside the worker thread (ARCH §6.4: no extra thread per
sink). A write failure disables the sink permanently for this process and is
reported to Health **once** by the caller (worker.py); the store is left
untouched (ARCH §8.3).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence, TextIO

from ..models import CanonicalLogRecord

SCHEMA_VERSION = 1
DEFAULT_MAX_BYTES = 10 * 1024 * 1024


def _json_default(value: Any) -> Any:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, (set, frozenset)):
        return sorted((str(item) for item in value))
    return str(value)


def _line_for(record: CanonicalLogRecord) -> str:
    entry = {
        "schemaVersion": SCHEMA_VERSION,
        "record_id": record.record_id,
        "received_at": record.received_at,
        "source_timestamp": record.source_timestamp,
        "producer_kind": record.producer_kind,
        "producer_id": record.producer_id,
        "instance_id": record.instance_id,
        "scope": record.scope,
        "channel": record.channel,
        "level": record.level,
        "type": record.type,
        "component": record.component,
        "session_id": record.session_id,
        "generation": record.generation,
        "activation_id": record.activation_id,
        "segment_id": record.segment_id,
        "transcription_id": record.transcription_id,
        "command_id": record.command_id,
        "event_id": record.event_id,
        "correlation_id": record.correlation_id,
        "server_cursor": record.server_cursor,
        "replayed": record.replayed,
        "message": record.message,
        "details": dict(record.details) if record.details else {},
        "raw": dict(record.raw) if record.raw is not None else None,
    }
    return json.dumps(entry, default=_json_default, ensure_ascii=False)


class JsonlSink:
    """One JSON line per record. Tagesrotation über den Dateinamen
    (``observability-YYYY-MM-DD.jsonl``), zusätzliche Größengrenze je Datei
    (``observability-YYYY-MM-DD.<n>.jsonl``)."""

    def __init__(self, directory: Path, *, max_bytes: int = DEFAULT_MAX_BYTES) -> None:
        self._directory = Path(directory)
        self._max_bytes = max(1, int(max_bytes))
        self._disabled = False
        self._current_date: Optional[str] = None
        self._current_index = 0
        self._handle: Optional[TextIO] = None

    @property
    def disabled(self) -> bool:
        return self._disabled

    def write_batch(self, records: Sequence[CanonicalLogRecord]) -> None:
        if self._disabled or not records:
            return
        try:
            self._directory.mkdir(parents=True, exist_ok=True)
            for record in records:
                line = _line_for(record)
                encoded_len = len(line.encode("utf-8")) + 1
                self._ensure_handle_for(encoded_len)
                self._handle.write(line)
                self._handle.write("\n")
            self._handle.flush()
        except Exception:
            self._disabled = True
            self._close_quietly()
            raise

    def _ensure_handle_for(self, incoming_bytes: int) -> None:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if today != self._current_date:
            self._current_date = today
            self._current_index = 0
            self._open_new_handle()
            return
        if self._handle is None:
            self._open_new_handle()
            return
        if self._handle.tell() + incoming_bytes > self._max_bytes:
            self._current_index += 1
            self._open_new_handle()

    def _path_for_current(self) -> Path:
        suffix = "" if self._current_index == 0 else f".{self._current_index}"
        return self._directory / f"observability-{self._current_date}{suffix}.jsonl"

    def _open_new_handle(self) -> None:
        self._close_quietly()
        path = self._path_for_current()
        while path.exists() and path.stat().st_size >= self._max_bytes:
            self._current_index += 1
            path = self._path_for_current()
        self._handle = open(path, "a", encoding="utf-8")

    def _close_quietly(self) -> None:
        if self._handle is not None:
            try:
                self._handle.close()
            except Exception:  # noqa: BLE001
                pass
            self._handle = None

    def close(self) -> None:
        self._close_quietly()
