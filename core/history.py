"""
Transcript history management for final transcripts and injection attempts.

Handles in-memory limits and optional SQLite persistence, with thread-safe
short-lived database connections and robust error fallback.
"""

from __future__ import annotations

import contextlib
import copy
from enum import Enum
import logging
import os
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set, Tuple

from core.config import HistoryConfig

class InjectionStatus(str, Enum):
    PENDING = "pending"
    COMMAND_SENT = "command_sent"
    FAILED = "failed"
    SKIPPED = "skipped"


class HistoryAddStatus(str, Enum):
    NEW = "new"
    ALREADY_EXISTS = "already_exists"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class HistoryAddResult:
    entry: Optional[HistoryEntry]
    status: HistoryAddStatus


logger = logging.getLogger("text")


@dataclass
class InjectionAttempt:
    """An attempt to inject a final transcript into the active application."""

    id: str
    entry_id: str
    status: str  # "pending", "command_sent", "failed", "skipped"
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class HistoryEntry:
    """A completed transcript segment with timestamps and injection attempt history."""

    id: str
    session_id: str
    segment_id: int
    timestamp: float
    text: str
    text_length: int
    attempts: List[InjectionAttempt] = field(default_factory=list)


class TranscriptHistoryManager:
    """
    Manages final transcript history both in memory and optionally in SQLite.

    Guarantees thread-safe access and robust error handling.
    """

    def __init__(self, config: HistoryConfig, db_path: Optional[str] = None):
        self.config = config
        self._memory_entries: List[HistoryEntry] = []
        self._processed_segments: Set[Tuple[str, int]] = set()
        self._lock = threading.Lock()
        self._db_enabled = False

        if not self.config.enabled:
            logger.info("Transcript history component is disabled by configuration.")
            return

        # Resolve DB path with priority:
        # 1. db_path constructor parameter
        # 2. config.persistent.db_path
        # 3. default _resolve_db_path()
        resolved_path = None
        if db_path:
            resolved_path = Path(db_path)
        elif self.config.persistent.db_path:
            resolved_path = Path(self.config.persistent.db_path)

        if resolved_path:
            self.db_path = resolved_path.resolve()
        else:
            self.db_path = self._resolve_db_path()

        # Initialize SQLite if persistence is enabled
        if self.config.persistent.enabled:
            self._init_db()
            if self._db_enabled:
                self._load_dedup_cache()
                self._load_from_db()

    def _resolve_db_path(self) -> Path:
        """Resolve platform-specific local application data path."""
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            base_dir = Path(local_app_data) / "RealtimeSTT_Client"
        else:
            base_dir = Path.home() / ".realtimestt_client"
        return base_dir / "transcript_history.db"

    def _get_connection(self) -> sqlite3.Connection:
        """Get a short-lived SQLite connection configured with constraints."""
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @contextlib.contextmanager
    def _db_session(self):
        """Context manager to handle connection lifecycle, transaction commits/rollbacks, and closing."""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _init_db(self) -> None:
        """Initialize DB tables and UNIQUE constraints."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with self._db_session() as conn:
                # Create history entries table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS history_entries (
                        id TEXT PRIMARY KEY,
                        session_id TEXT,
                        segment_id INTEGER,
                        timestamp REAL,
                        text TEXT,
                        text_length INTEGER,
                        UNIQUE(session_id, segment_id)
                    )
                """)
                # Create injection attempts table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS injection_attempts (
                        id TEXT PRIMARY KEY,
                        entry_id TEXT,
                        status TEXT,
                        error TEXT,
                        timestamp REAL,
                        FOREIGN KEY(entry_id) REFERENCES history_entries(id) ON DELETE CASCADE
                    )
                """)
            self._db_enabled = True
            logger.info("SQLite database initialized successfully at %s", self.db_path)
        except Exception as e:
            logger.error("Failed to initialize SQLite database: %s. Falling back to in-memory mode.", e, exc_info=True)
            self._db_enabled = False

    def _load_dedup_cache(self) -> None:
        """Load segment keys from database to populate in-process deduplication cache."""
        if not self._db_enabled:
            return
        try:
            with self._db_session() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT session_id, segment_id FROM history_entries")
                for row in cursor.fetchall():
                    self._processed_segments.add((row["session_id"], row["segment_id"]))
            logger.debug("Loaded %d segment keys into deduplication cache.", len(self._processed_segments))
        except Exception as e:
            logger.error("Failed to load deduplication cache from DB: %s", e)

    def _load_from_db(self) -> None:
        """Load latest persistent entries into in-memory storage up to the limit."""
        if not self._db_enabled:
            return
        try:
            max_mem = self.config.memory.max_entries
            if max_mem > 0:
                query = """
                    SELECT * FROM (
                        SELECT * FROM history_entries ORDER BY timestamp DESC LIMIT ?
                    ) ORDER BY timestamp ASC
                """
                args = (max_mem,)
            else:
                query = "SELECT * FROM history_entries ORDER BY timestamp ASC"
                args = ()

            with self._db_session() as conn:
                cursor = conn.cursor()
                cursor.execute(query, args)
                rows = cursor.fetchall()

                for row in rows:
                    entry_id = row["id"]
                    cursor.execute(
                        "SELECT * FROM injection_attempts WHERE entry_id = ? ORDER BY timestamp ASC",
                        (entry_id,)
                    )
                    attempts = []
                    for att_row in cursor.fetchall():
                        attempts.append(InjectionAttempt(
                            id=att_row["id"],
                            entry_id=att_row["entry_id"],
                            status=att_row["status"],
                            error=att_row["error"],
                            timestamp=att_row["timestamp"],
                        ))

                    entry = HistoryEntry(
                        id=row["id"],
                        session_id=row["session_id"],
                        segment_id=row["segment_id"],
                        timestamp=row["timestamp"],
                        text=row["text"],
                        text_length=row["text_length"],
                        attempts=attempts,
                    )
                    self._memory_entries.append(entry)
            logger.info("Loaded %d recent history entries from SQLite database.", len(self._memory_entries))
        except Exception as e:
            logger.error("Failed to load history entries from DB: %s", e, exc_info=True)

    def _fetch_entry_from_db(self, session_id: str, segment_id: int) -> Optional[HistoryEntry]:
        """Query database for a specific segment and construct its HistoryEntry."""
        if not self._db_enabled:
            return None
        try:
            with self._db_session() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM history_entries WHERE session_id = ? AND segment_id = ?",
                    (session_id, segment_id)
                )
                row = cursor.fetchone()
                if row:
                    entry_id = row["id"]
                    cursor.execute(
                        "SELECT * FROM injection_attempts WHERE entry_id = ? ORDER BY timestamp ASC",
                        (entry_id,)
                    )
                    attempts = []
                    for att_row in cursor.fetchall():
                        attempts.append(InjectionAttempt(
                            id=att_row["id"],
                            entry_id=att_row["entry_id"],
                            status=att_row["status"],
                            error=att_row["error"],
                            timestamp=att_row["timestamp"],
                        ))
                    return HistoryEntry(
                        id=row["id"],
                        session_id=row["session_id"],
                        segment_id=row["segment_id"],
                        timestamp=row["timestamp"],
                        text=row["text"],
                        text_length=row["text_length"],
                        attempts=attempts,
                    )
        except Exception as e:
            logger.error("Failed to fetch entry from DB: %s", e)
        return None

    def _fetch_entry_from_db_by_id(self, entry_id: str) -> Optional[HistoryEntry]:
        """Query database for an entry by its ID and construct the HistoryEntry."""
        if not self._db_enabled:
            return None
        try:
            with self._db_session() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM history_entries WHERE id = ?", (entry_id,))
                row = cursor.fetchone()
                if row:
                    cursor.execute(
                        "SELECT * FROM injection_attempts WHERE entry_id = ? ORDER BY timestamp ASC",
                        (entry_id,)
                    )
                    attempts = []
                    for att_row in cursor.fetchall():
                        attempts.append(InjectionAttempt(
                            id=att_row["id"],
                            entry_id=att_row["entry_id"],
                            status=att_row["status"],
                            error=att_row["error"],
                            timestamp=att_row["timestamp"],
                        ))
                    return HistoryEntry(
                        id=row["id"],
                        session_id=row["session_id"],
                        segment_id=row["segment_id"],
                        timestamp=row["timestamp"],
                        text=row["text"],
                        text_length=row["text_length"],
                        attempts=attempts,
                    )
        except Exception as e:
            logger.error("Failed to fetch entry by ID from DB: %s", e)
        return None

    def _add_to_memory(self, entry: HistoryEntry) -> None:
        """Add entry to the in-memory list, respecting configured limit."""
        if any(e.id == entry.id for e in self._memory_entries):
            return
        self._memory_entries.append(entry)
        max_mem = self.config.memory.max_entries
        if max_mem > 0 and len(self._memory_entries) > max_mem:
            self._memory_entries.pop(0)

    def _should_persist(self, entry: HistoryEntry) -> bool:
        """Determine if the entry should be persisted in SQLite."""
        if not self.config.persistent.enabled:
            return False

        if self.config.persistent.store_all:
            return True

        if len(entry.text) >= self.config.persistent.min_characters:
            return True

        if self.config.persistent.store_failed_injections:
            if any(att.status in ("failed", "skipped") for att in entry.attempts):
                return True

        return False

    def _save_to_db(self, entry: HistoryEntry) -> None:
        """Persist a HistoryEntry in SQLite without changing the ID on conflict."""
        if not self._db_enabled:
            return
        try:
            with self._db_session() as conn:
                cursor = conn.execute("""
                    INSERT INTO history_entries (id, session_id, segment_id, timestamp, text, text_length)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(session_id, segment_id) DO NOTHING
                """, (entry.id, entry.session_id, entry.segment_id, entry.timestamp, entry.text, entry.text_length))
                if cursor.rowcount == 0:
                    cursor = conn.execute(
                        "SELECT id FROM history_entries WHERE session_id = ? AND segment_id = ?",
                        (entry.session_id, entry.segment_id)
                    )
                    row = cursor.fetchone()
                    if row:
                        entry.id = row["id"]
            
            # Execute cleanup best-effort in a separate query
            try:
                self.cleanup()
            except Exception as e:
                logger.error("Database cleanup error (non-fatal): %s", e)
        except Exception as e:
            logger.error("Failed to save history entry to DB: %s", e, exc_info=True)

    def _save_attempt_to_db(self, attempt: InjectionAttempt) -> None:
        """Insert an InjectionAttempt into SQLite."""
        if not self._db_enabled:
            return
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO injection_attempts (id, entry_id, status, error, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (attempt.id, attempt.entry_id, attempt.status, attempt.error, attempt.timestamp))
        except Exception as e:
            logger.error("Failed to save injection attempt to DB: %s", e, exc_info=True)

    # -------------------------------------------------------------------
    # Public APIs
    # -------------------------------------------------------------------

    def add_entry_with_status(
        self, session_id: str, segment_id: int, text: str, timestamp: Optional[float] = None
    ) -> HistoryAddResult:
        """
        Add a final transcript entry and return a HistoryAddResult detailing whether
        the entry is newly created (NEW), already existed (ALREADY_EXISTS), or history
        is disabled/unavailable (UNAVAILABLE).
        """
        if not self.config.enabled:
            return HistoryAddResult(entry=None, status=HistoryAddStatus.UNAVAILABLE)

        t = timestamp if timestamp is not None else time.time()

        with self._lock:
            # Deduplication
            if (session_id, segment_id) in self._processed_segments:
                # Match in memory first
                for entry in self._memory_entries:
                    if entry.session_id == session_id and entry.segment_id == segment_id:
                        return HistoryAddResult(entry=entry, status=HistoryAddStatus.ALREADY_EXISTS)
                # Match in DB
                entry = self._fetch_entry_from_db(session_id, segment_id)
                if entry:
                    return HistoryAddResult(entry=entry, status=HistoryAddStatus.ALREADY_EXISTS)
                # Processed before, but rotated out of memory and not in DB
                return HistoryAddResult(entry=None, status=HistoryAddStatus.ALREADY_EXISTS)

            # Match in DB in case segment pre-exists in persistent DB from previous runs
            existing_db_entry = self._fetch_entry_from_db(session_id, segment_id)
            if existing_db_entry:
                self._processed_segments.add((session_id, segment_id))
                self._add_to_memory(existing_db_entry)
                return HistoryAddResult(entry=existing_db_entry, status=HistoryAddStatus.ALREADY_EXISTS)

            # Create new
            entry = HistoryEntry(
                id=uuid.uuid4().hex,
                session_id=session_id,
                segment_id=segment_id,
                timestamp=t,
                text=text,
                text_length=len(text),
                attempts=[]
            )

            # Update deduplication cache
            self._processed_segments.add((session_id, segment_id))

            # Add to memory
            self._add_to_memory(entry)

            # Save to SQLite if rules match
            if self._db_enabled and self._should_persist(entry):
                self._save_to_db(entry)

            return HistoryAddResult(entry=entry, status=HistoryAddStatus.NEW)

    def add_entry(
        self, session_id: str, segment_id: int, text: str, timestamp: Optional[float] = None
    ) -> Optional[HistoryEntry]:
        """
        Add a final transcript entry. Deduplicates by session_id and segment_id.

        If the segment has already been processed but the corresponding entry is
        no longer in memory and was not persisted to the database, this method
        returns None to prevent duplicate processing.
        """
        res = self.add_entry_with_status(session_id, segment_id, text, timestamp)
        return res.entry

    def record_injection_attempt(
        self, entry_id: str, status: str, error: Optional[str] = None, timestamp: Optional[float] = None
    ) -> Optional[InjectionAttempt]:
        """
        Record a new injection attempt for an entry.
        """
        if not self.config.enabled:
            return None

        # Validate status using central Enum
        try:
            valid_status = InjectionStatus(status)
        except ValueError:
            raise ValueError(f"Invalid injection status: {status}")

        t = timestamp if timestamp is not None else time.time()

        with self._lock:
            # Find in memory
            entry = None
            for e in self._memory_entries:
                if e.id == entry_id:
                    entry = e
                    break

            # Find in DB
            if not entry and self._db_enabled:
                entry = self._fetch_entry_from_db_by_id(entry_id)

            if not entry:
                logger.warning("History entry %s not found for recording injection attempt.", entry_id)
                return None

            attempt = InjectionAttempt(
                id=uuid.uuid4().hex,
                entry_id=entry.id,
                status=valid_status.value,
                error=error,
                timestamp=t
            )

            entry.attempts.append(attempt)

            if self._db_enabled:
                # Determine if parent should be persisted
                should_persist = self._should_persist(entry)
                
                # Check if parent already exists in DB
                parent_exists = False
                try:
                    with self._db_session() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1 FROM history_entries WHERE id = ?", (entry.id,))
                        parent_exists = cursor.fetchone() is not None
                except Exception as e:
                    logger.error("Failed to check if parent exists in DB: %s", e)
                
                if should_persist or parent_exists:
                    try:
                        with self._db_session() as conn:
                            # Start joint atomic transaction block
                            if should_persist and not parent_exists:
                                cursor = conn.execute("""
                                    INSERT INTO history_entries (id, session_id, segment_id, timestamp, text, text_length)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                    ON CONFLICT(session_id, segment_id) DO NOTHING
                                """, (entry.id, entry.session_id, entry.segment_id, entry.timestamp, entry.text, entry.text_length))
                                
                                if cursor.rowcount == 0:
                                    # Conflict, read existing row's stable ID
                                    cursor = conn.execute(
                                        "SELECT id FROM history_entries WHERE session_id = ? AND segment_id = ?",
                                        (entry.session_id, entry.segment_id)
                                    )
                                    row = cursor.fetchone()
                                    if row:
                                        entry.id = row["id"]
                                        attempt.entry_id = row["id"]
                            
                            conn.execute("""
                                INSERT INTO injection_attempts (id, entry_id, status, error, timestamp)
                                VALUES (?, ?, ?, ?, ?)
                            """, (attempt.id, attempt.entry_id, attempt.status, attempt.error, attempt.timestamp))
                        
                        # Cleanup is only called AFTER successful commit of the joint transaction!
                        if should_persist and not parent_exists:
                            try:
                                self.cleanup()
                            except Exception as e:
                                logger.error("Database cleanup error (non-fatal): %s", e)
                    except Exception as e:
                        logger.error("Failed to save history entry and attempt atomar in DB: %s", e, exc_info=True)

            return attempt

    def cleanup(self) -> None:
        """
        Performs database cleanup. Deletes old entries exceeding max_entries or retention_days.
        """
        if not self._db_enabled or not self.config.persistent.enabled:
            return

        try:
            # 1. Age-based cleanup
            retention_days = self.config.persistent.retention_days
            if retention_days > 0:
                cutoff = time.time() - (retention_days * 86400)
                with self._db_session() as conn:
                    cursor = conn.execute("DELETE FROM history_entries WHERE timestamp < ?", (cutoff,))
                    if cursor.rowcount > 0:
                        logger.info("Deleted %d expired history entries.", cursor.rowcount)
 
            # 2. Count-based cleanup
            max_entries = self.config.persistent.max_entries
            if max_entries > 0:
                with self._db_session() as conn:
                    # SQLite delete with subquery
                    cursor = conn.execute("""
                        DELETE FROM history_entries WHERE id NOT IN (
                            SELECT id FROM (
                                SELECT id FROM history_entries ORDER BY timestamp DESC LIMIT ?
                            )
                        )
                    """, (max_entries,))
                    if cursor.rowcount > 0:
                        logger.info("Enforced persistent history limit: deleted %d entries.", cursor.rowcount)
        except Exception as e:
            logger.warning("Database cleanup failed (non-fatal): %s", e)

    def get_memory_entries(self) -> List[HistoryEntry]:
        """
        Retrieve all loaded in-memory entries, ordered chronologically (oldest first).
        Returns a deep copy of the entries to prevent external mutation of the internal state.
        """
        with self._lock:
            return copy.deepcopy(self._memory_entries)

    def delete_entry(self, entry_id: str) -> bool:
        """Delete one history entry while retaining its session dedupe identity."""
        if not isinstance(entry_id, str) or not entry_id:
            return False
        with self._lock:
            exists = any(entry.id == entry_id for entry in self._memory_entries)
        if self._db_enabled and self.config.persistent.enabled:
            try:
                with self._db_session() as conn:
                    cursor = conn.execute(
                        "DELETE FROM history_entries WHERE id = ?", (entry_id,)
                    )
                    exists = exists or cursor.rowcount > 0
            except Exception:
                logger.exception("Failed to delete history entry %s.", entry_id)
                return False
        if exists:
            with self._lock:
                self._memory_entries = [
                    entry for entry in self._memory_entries if entry.id != entry_id
                ]
        return exists

    def clear_entries(self) -> int:
        """Delete all visible entries but keep in-process dedupe reservations."""
        with self._lock:
            memory_count = len(self._memory_entries)
        database_count = 0
        if self._db_enabled and self.config.persistent.enabled:
            try:
                with self._db_session() as conn:
                    cursor = conn.execute("DELETE FROM history_entries")
                    database_count = max(0, cursor.rowcount)
            except Exception:
                logger.exception("Failed to clear transcript history.")
                return 0
        with self._lock:
            self._memory_entries.clear()
        return max(memory_count, database_count)

    def get_persistent_entries(self, limit: Optional[int] = None) -> List[HistoryEntry]:
        """
        Retrieve entries directly from SQLite database, ordered chronologically (oldest first).
        """
        if not self._db_enabled or not self.config.persistent.enabled:
            return []

        try:
            query = "SELECT * FROM history_entries ORDER BY timestamp ASC"
            args = ()
            if limit is not None and limit > 0:
                query = """
                    SELECT * FROM (
                        SELECT * FROM history_entries ORDER BY timestamp DESC LIMIT ?
                    ) ORDER BY timestamp ASC
                """
                args = (limit,)

            with self._db_session() as conn:
                cursor = conn.cursor()
                cursor.execute(query, args)
                rows = cursor.fetchall()

                entries = []
                for row in rows:
                    entry_id = row["id"]
                    cursor.execute(
                        "SELECT * FROM injection_attempts WHERE entry_id = ? ORDER BY timestamp ASC",
                        (entry_id,)
                    )
                    attempts = []
                    for att_row in cursor.fetchall():
                        attempts.append(InjectionAttempt(
                            id=att_row["id"],
                            entry_id=att_row["entry_id"],
                            status=att_row["status"],
                            error=att_row["error"],
                            timestamp=att_row["timestamp"],
                        ))

                    entries.append(HistoryEntry(
                        id=row["id"],
                        session_id=row["session_id"],
                        segment_id=row["segment_id"],
                        timestamp=row["timestamp"],
                        text=row["text"],
                        text_length=row["text_length"],
                        attempts=attempts,
                    ))
                return entries
        except Exception as e:
            logger.error("Failed to query persistent entries from DB: %s", e, exc_info=True)
            return []
