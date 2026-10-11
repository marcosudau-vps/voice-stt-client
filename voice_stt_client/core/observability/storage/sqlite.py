"""
``SQLiteLogStore`` — the V1 local persistence layer (OBS-030).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §5 (DDL, connections,
dedupe/write_batch, migration, retention SQL, ``clear()``) and
``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §8.3 (failure states), D-2/D-4 (OBS-000
corrections). Storage knows only the model (ARCH §5.2): this module imports
nothing from ``..redaction``/``..normalizer``/``..ingress``/``..worker``/
``..manager``. Everything here is generic JSON-encoding, never a redaction
policy decision — that boundary is enforced by
``tests/test_obs030_contracts.py``.

The single write connection is created **in the worker thread** by calling
``open()`` there (D-4), never in a constructor. ``check_same_thread`` is left
at the sqlite3 default (``True``): the connection must never leave its
thread (N-05).
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Mapping, NamedTuple, Optional, Sequence

from ..models import CanonicalLogRecord

SCHEMA_VERSION = 1
RETENTION_BLOCK_SIZE = 5000


class OpenResult(NamedTuple):
    ok: bool
    degraded: bool
    detail: str


def _json_default(value: Any) -> Any:
    """Generic JSON-encoding fallback (not a redaction rule): converts the
    remaining frozen container shapes (``MappingProxyType``, ``frozenset``)
    that ``CanonicalLogRecord.__post_init__`` always re-applies on
    construction. Tuples are already native JSON arrays and need no hook."""
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, (set, frozenset)):
        return sorted((str(item) for item in value))
    return str(value)


def _dumps(value: Optional[Mapping[str, Any]]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, Mapping) and len(value) == 0:
        return None
    payload = dict(value) if not isinstance(value, dict) else value
    return json.dumps(payload, default=_json_default, ensure_ascii=False)


_DDL_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS schema_meta (
        key    TEXT PRIMARY KEY,
        value  TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS logs (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,

        record_id         TEXT    NOT NULL,
        received_at       TEXT    NOT NULL,
        source_timestamp  TEXT,

        producer_kind     TEXT    NOT NULL,
        producer_id       TEXT    NOT NULL,
        instance_id       TEXT    NOT NULL,

        scope             TEXT    NOT NULL,
        channel           TEXT    NOT NULL,
        level             TEXT    NOT NULL,
        type              TEXT,
        component         TEXT,

        session_id        TEXT,
        generation        INTEGER,
        activation_id     TEXT,
        segment_id        INTEGER,
        transcription_id  TEXT,
        command_id        TEXT,
        event_id          TEXT,
        correlation_id    TEXT,
        server_cursor     INTEGER,

        replayed          INTEGER NOT NULL DEFAULT 0,

        message           TEXT,
        details_json      TEXT,
        raw_json          TEXT
    )
    """,
    """
    CREATE UNIQUE INDEX IF NOT EXISTS ux_logs_producer_event
        ON logs (producer_id, event_id)
        WHERE event_id IS NOT NULL
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_logs_session_id
        ON logs (session_id, id DESC)
        WHERE session_id IS NOT NULL
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_logs_received_at
        ON logs (received_at)
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_logs_channel_level
        ON logs (channel, level, id DESC)
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_logs_activation
        ON logs (activation_id, id DESC)
        WHERE activation_id IS NOT NULL
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_logs_correlation
        ON logs (correlation_id, id DESC)
        WHERE correlation_id IS NOT NULL
    """,
)

_INSERT_SQL = """
INSERT INTO logs (
    record_id, received_at, source_timestamp,
    producer_kind, producer_id, instance_id,
    scope, channel, level, type, component,
    session_id, generation, activation_id, segment_id,
    transcription_id, command_id, event_id, correlation_id,
    server_cursor, replayed, message, details_json, raw_json
) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
ON CONFLICT (producer_id, event_id) WHERE event_id IS NOT NULL DO NOTHING
"""


def _migrate_to_1(conn: sqlite3.Connection, *, created_by_version: str) -> None:
    for statement in _DDL_STATEMENTS:
        conn.execute(statement)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    conn.execute(
        "INSERT OR IGNORE INTO schema_meta (key, value) VALUES (?, ?)",
        ("created_at", now),
    )
    conn.execute(
        "INSERT OR IGNORE INTO schema_meta (key, value) VALUES (?, ?)",
        ("created_by_version", created_by_version),
    )
    conn.execute(
        "INSERT OR REPLACE INTO schema_meta (key, value) VALUES (?, ?)",
        ("last_migrated_at", now),
    )


# ``(target_version, migration_fn)``. V1 has exactly one step: bootstrap.
# Future schema changes append here without touching the dispatch logic.
_MIGRATIONS: tuple[tuple[int, Any], ...] = (
    (1, _migrate_to_1),
)


class SQLiteLogStore:
    """The single local persistence write path (O-14): Ingress -> Worker ->
    Store. Reads use their own short-lived connections (query layer, OBS-050)
    with ``PRAGMA query_only = ON`` — never ``mode=ro`` (D-2)."""

    def __init__(self, path: Path, *, created_by_version: str = "OBS-030") -> None:
        self._path = Path(path)
        self._created_by_version = created_by_version
        self._connection: Optional[sqlite3.Connection] = None
        self._degraded_readonly = False

    @property
    def path(self) -> Path:
        return self._path

    @property
    def is_open(self) -> bool:
        return self._connection is not None

    @property
    def is_degraded(self) -> bool:
        return self._degraded_readonly

    # -- lifecycle (D-4: called from the worker thread, never __init__) ----

    def open(self) -> OpenResult:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self._path), timeout=5.0)
        except Exception as exc:  # noqa: BLE001 - failure isolation boundary
            return OpenResult(False, False, f"open failed: {exc}")
        try:
            # CONTRACTS §5.2 prescribes exactly this order.
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA busy_timeout = 5000")
            conn.execute("PRAGMA foreign_keys = ON")
            version = conn.execute("PRAGMA user_version").fetchone()[0]
        except Exception as exc:  # noqa: BLE001
            self._close_connection(conn)
            return OpenResult(False, False, f"pragma setup failed: {exc}")

        if version > SCHEMA_VERSION:
            self._connection = conn
            self._degraded_readonly = True
            try:
                conn.execute("PRAGMA query_only = ON")
            except Exception:  # noqa: BLE001
                pass
            return OpenResult(
                True, True,
                f"user_version {version} newer than supported {SCHEMA_VERSION}: read-only",
            )

        if version < SCHEMA_VERSION:
            ok, detail = self._migrate(conn, version)
            if not ok:
                self._close_connection(conn)
                return OpenResult(False, False, detail)

        self._connection = conn
        self._degraded_readonly = False
        return OpenResult(True, False, "")

    def _migrate(self, conn: sqlite3.Connection, from_version: int) -> tuple[bool, str]:
        steps = [step for step in _MIGRATIONS if step[0] > from_version]
        for target_version, fn in steps:
            try:
                conn.execute("BEGIN")
                fn(conn, created_by_version=self._created_by_version)
                conn.execute(f"PRAGMA user_version = {int(target_version)}")
                conn.commit()
            except Exception as exc:  # noqa: BLE001 - migration must never
                # leave the file half-migrated or the app crashed (§5.5).
                try:
                    conn.rollback()
                except Exception:  # noqa: BLE001
                    pass
                return False, f"migration to {target_version} failed, rolled back: {exc}"
        return True, ""

    def close(self) -> None:
        if self._connection is not None:
            self._close_connection(self._connection)
            self._connection = None

    @staticmethod
    def _close_connection(conn: sqlite3.Connection) -> None:
        try:
            conn.close()
        except Exception:  # noqa: BLE001
            pass

    # -- writes (O-14: the only write path) ---------------------------------

    def write_batch(self, records: Sequence[CanonicalLogRecord]) -> tuple[int, int]:
        """Persist one batch in a single transaction. Returns
        ``(eingefuegt, dedupliziert)`` (CONTRACTS §5.5, FD-R5). Raises the
        underlying ``sqlite3.Error`` on failure — the caller (worker.py) owns
        the retry/circuit-breaker policy (ARCH §8.3)."""
        if self._connection is None or self._degraded_readonly or not records:
            return (0, 0)
        conn = self._connection
        rows = [self._to_row(record) for record in records]
        before = conn.total_changes
        try:
            conn.execute("BEGIN")
            conn.executemany(_INSERT_SQL, rows)
            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception:  # noqa: BLE001
                pass
            raise
        inserted = conn.total_changes - before
        deduplicated = max(0, len(records) - inserted)
        return (inserted, deduplicated)

    @staticmethod
    def _to_row(record: CanonicalLogRecord) -> tuple:
        return (
            record.record_id,
            record.received_at,
            record.source_timestamp,
            record.producer_kind,
            record.producer_id,
            record.instance_id,
            record.scope,
            record.channel,
            record.level,
            record.type,
            record.component,
            record.session_id,
            record.generation,
            record.activation_id,
            record.segment_id,
            record.transcription_id,
            record.command_id,
            record.event_id,
            record.correlation_id,
            record.server_cursor,
            1 if record.replayed else 0,
            record.message,
            _dumps(record.details),
            _dumps(record.raw),
        )

    def probe_write(self) -> bool:
        """ARCH §8.3: after the 60 s suspension the store is re-checked
        "mit einem leeren Testschreibvorgang" — a write transaction that
        carries **no** rows. ``BEGIN IMMEDIATE`` takes the writer lock (so a
        locked, read-only or otherwise unwritable database still fails) and
        the commit costs nothing when there is nothing to write. Returns
        ``False`` instead of raising: this is a probe, not a batch, and a
        failing probe must never cost a batch (that was the defect W-4)."""
        if self._connection is None or self._degraded_readonly:
            return False
        conn = self._connection
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.commit()
            return True
        except Exception:  # noqa: BLE001 - failure isolation boundary
            try:
                conn.rollback()
            except Exception:  # noqa: BLE001
                pass
            return False

    # -- deletion (FD-S4) -----------------------------------------------

    def clear(self) -> int:
        """``DELETE FROM logs`` + ``wal_checkpoint(TRUNCATE)`` (CONTRACTS
        §5.8). Must run on the worker thread (same connection ownership)."""
        if self._connection is None or self._degraded_readonly:
            return 0
        conn = self._connection
        try:
            cursor = conn.execute("DELETE FROM logs")
            deleted = cursor.rowcount if cursor.rowcount and cursor.rowcount > 0 else 0
            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception:  # noqa: BLE001
                pass
            raise
        try:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        except Exception:  # noqa: BLE001 - best-effort checkpoint only
            pass
        return deleted

    # -- retention (CONTRACTS §5.6) --------------------------------------

    def run_retention(
        self,
        *,
        cutoff_iso: Optional[str],
        max_entries: Optional[int],
        time_budget_s: float = 0.2,
    ) -> tuple[int, int]:
        """Blockweise (5000er Bloecke), zeitbudgetiert. Returns
        ``(deleted_by_age, deleted_by_count)``. NIE ``VACUUM``/
        ``auto_vacuum``/``incremental_vacuum`` (FD-D8)."""
        if self._connection is None or self._degraded_readonly:
            return (0, 0)
        conn = self._connection
        deadline = time.monotonic() + max(0.0, time_budget_s)
        deleted_age = 0
        if cutoff_iso:
            while time.monotonic() < deadline:
                cursor = conn.execute(
                    "DELETE FROM logs WHERE id IN ("
                    "SELECT id FROM logs WHERE received_at < ? ORDER BY id LIMIT ?)",
                    (cutoff_iso, RETENTION_BLOCK_SIZE),
                )
                conn.commit()
                changed = cursor.rowcount if cursor.rowcount and cursor.rowcount > 0 else 0
                deleted_age += changed
                if changed < RETENTION_BLOCK_SIZE:
                    break
        deleted_count = 0
        if max_entries is not None and max_entries > 0 and time.monotonic() < deadline:
            floor_row = conn.execute(
                "SELECT id FROM logs ORDER BY id DESC LIMIT 1 OFFSET ?",
                (max_entries - 1,),
            ).fetchone()
            if floor_row is not None:
                floor_id = floor_row[0]
                while time.monotonic() < deadline:
                    cursor = conn.execute(
                        "DELETE FROM logs WHERE id IN ("
                        "SELECT id FROM logs WHERE id < ? ORDER BY id LIMIT ?)",
                        (floor_id, RETENTION_BLOCK_SIZE),
                    )
                    conn.commit()
                    changed = cursor.rowcount if cursor.rowcount and cursor.rowcount > 0 else 0
                    deleted_count += changed
                    if changed < RETENTION_BLOCK_SIZE:
                        break
        return (deleted_age, deleted_count)

    def measure_db_bytes(self) -> Optional[int]:
        """``page_count * page_size`` — MESSEN, nicht eingreifen (§5.6.3)."""
        if self._connection is None:
            return None
        try:
            page_count = self._connection.execute("PRAGMA page_count").fetchone()[0]
            page_size = self._connection.execute("PRAGMA page_size").fetchone()[0]
            return int(page_count) * int(page_size)
        except Exception:  # noqa: BLE001
            return None

    def row_count(self) -> Optional[int]:
        """Test/diagnostic helper only — not part of the frozen contract."""
        if self._connection is None:
            return None
        try:
            return int(self._connection.execute("SELECT COUNT(*) FROM logs").fetchone()[0])
        except Exception:  # noqa: BLE001
            return None
