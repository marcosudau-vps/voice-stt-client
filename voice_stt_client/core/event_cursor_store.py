"""Atomic persistence for the last successfully processed AP07 event cursor."""

from __future__ import annotations

import json
import logging
import os
import tempfile
import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit, urlunsplit


logger = logging.getLogger(__name__)
CURSOR_SCHEMA_VERSION = 1
DEFAULT_CURSOR_PATH = (
    Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
    / "RealtimeSTT Client"
    / "event_cursor.json"
)


def normalize_endpoint(endpoint: str) -> str:
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise ValueError("endpoint must be a non-empty string")
    parts = urlsplit(endpoint.strip())
    if parts.scheme not in {"ws", "wss"} or not parts.netloc:
        raise ValueError("endpoint must be an absolute ws:// or wss:// URL")
    if parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("endpoint must not contain credentials, query or fragment")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, "", ""))


@dataclass(frozen=True)
class CursorRecord:
    schema_version: int
    endpoint: str
    server_instance_id: str
    protocol_version: int
    cursor: int
    updated_at: str


class EventCursorStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path is not None else DEFAULT_CURSOR_PATH
        self._lock = threading.RLock()

    def load(
        self,
        *,
        endpoint: str,
        server_instance_id: str,
        protocol_version: int,
        latest_cursor: Optional[int] = None,
    ) -> Optional[CursorRecord]:
        binding = self._validate_binding(
            endpoint, server_instance_id, protocol_version, latest_cursor
        )
        with self._lock:
            if not self.path.is_file():
                return None
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                record = self._parse_record(raw)
            except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                logger.warning("Ignoring invalid event cursor file %s: %s", self.path, exc)
                return None
            expected_endpoint, expected_instance, expected_protocol, maximum = binding
            if (
                record.endpoint != expected_endpoint
                or record.server_instance_id != expected_instance
                or record.protocol_version != expected_protocol
            ):
                logger.info("Ignoring event cursor with a different server binding")
                return None
            if maximum is not None and record.cursor > maximum:
                logger.warning(
                    "Ignoring event cursor %s ahead of server cursor %s",
                    record.cursor,
                    maximum,
                )
                return None
            return record

    def commit(
        self,
        cursor: int,
        *,
        endpoint: str,
        server_instance_id: str,
        protocol_version: int,
    ) -> CursorRecord:
        normalized_endpoint, instance, protocol, _ = self._validate_binding(
            endpoint, server_instance_id, protocol_version, None
        )
        if isinstance(cursor, bool) or not isinstance(cursor, int) or cursor < 0:
            raise ValueError("cursor must be an integer >= 0")
        record = CursorRecord(
            schema_version=CURSOR_SCHEMA_VERSION,
            endpoint=normalized_endpoint,
            server_instance_id=instance,
            protocol_version=protocol,
            cursor=cursor,
            updated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path: Optional[Path] = None
            try:
                with tempfile.NamedTemporaryFile(
                    "w",
                    encoding="utf-8",
                    dir=self.path.parent,
                    prefix=f".{self.path.name}.",
                    suffix=".tmp",
                    delete=False,
                ) as handle:
                    json.dump(asdict(record), handle, ensure_ascii=False, indent=2)
                    handle.write("\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                    temporary_path = Path(handle.name)
                os.replace(temporary_path, self.path)
            finally:
                if temporary_path is not None and temporary_path.exists():
                    temporary_path.unlink()
        return record

    @staticmethod
    def _validate_binding(
        endpoint: str,
        server_instance_id: str,
        protocol_version: int,
        latest_cursor: Optional[int],
    ) -> tuple[str, str, int, Optional[int]]:
        normalized_endpoint = normalize_endpoint(endpoint)
        if not isinstance(server_instance_id, str) or not server_instance_id.strip():
            raise ValueError("server_instance_id must be a non-empty string")
        if (
            isinstance(protocol_version, bool)
            or not isinstance(protocol_version, int)
            or protocol_version < 1
        ):
            raise ValueError("protocol_version must be an integer >= 1")
        if latest_cursor is not None and (
            isinstance(latest_cursor, bool)
            or not isinstance(latest_cursor, int)
            or latest_cursor < 0
        ):
            raise ValueError("latest_cursor must be null or an integer >= 0")
        return (
            normalized_endpoint,
            server_instance_id.strip(),
            protocol_version,
            latest_cursor,
        )

    @staticmethod
    def _parse_record(raw: object) -> CursorRecord:
        if not isinstance(raw, dict):
            raise ValueError("cursor root must be an object")
        expected = {
            "schema_version", "endpoint", "server_instance_id",
            "protocol_version", "cursor", "updated_at",
        }
        if set(raw) != expected:
            raise ValueError("cursor fields do not match schema version 1")
        if raw["schema_version"] != CURSOR_SCHEMA_VERSION:
            raise ValueError("unsupported cursor schema version")
        endpoint = normalize_endpoint(raw["endpoint"])
        instance = raw["server_instance_id"]
        updated_at = raw["updated_at"]
        protocol = raw["protocol_version"]
        cursor = raw["cursor"]
        if not isinstance(instance, str) or not instance.strip():
            raise ValueError("invalid server_instance_id")
        if not isinstance(updated_at, str) or not updated_at.strip():
            raise ValueError("invalid updated_at")
        if isinstance(protocol, bool) or not isinstance(protocol, int) or protocol < 1:
            raise ValueError("invalid protocol_version")
        if isinstance(cursor, bool) or not isinstance(cursor, int) or cursor < 0:
            raise ValueError("invalid cursor")
        return CursorRecord(
            schema_version=CURSOR_SCHEMA_VERSION,
            endpoint=endpoint,
            server_instance_id=instance.strip(),
            protocol_version=protocol,
            cursor=cursor,
            updated_at=updated_at,
        )
