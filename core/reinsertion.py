"""
Transcript reinsertion service for re-injecting historical transcripts.

Provides a UI-neutral interface for requesting re-injection of the last or a
specific transcript entry via TextInjectionQueue, without creating new history entries.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
import logging
import threading
from typing import List, Optional, Tuple

from core.history import HistoryEntry, TranscriptHistoryManager
from core.text_injector import TextInjectionQueue

logger = logging.getLogger("text")


class ReinsertionStatus(str, Enum):
    """Possible outcome statuses of a reinsertion request."""

    QUEUED = "queued"
    EMPTY_HISTORY = "empty_history"
    ENTRY_NOT_FOUND = "entry_not_found"
    QUEUE_UNAVAILABLE = "queue_unavailable"
    FAILED = "failed"


@dataclass(frozen=True)
class ReinsertionResult:
    """Immutable result container for a reinsertion request."""

    status: ReinsertionStatus
    entry_id: Optional[str] = None
    reason: Optional[str] = None
    error_message: Optional[str] = None


class TranscriptReinsertionService:
    """
    UI-neutral service for reinserting transcript entries into active applications.

    Delegates history resolution to TranscriptHistoryManager and asynchronous
    text injection to TextInjectionQueue.
    """

    def __init__(
        self,
        history_manager: TranscriptHistoryManager,
        injection_queue: TextInjectionQueue,
    ) -> None:
        self.history_manager = history_manager
        self.injection_queue = injection_queue
        self._lock = threading.Lock()

    def get_recent_entries(self, limit: Optional[int] = None) -> Tuple[HistoryEntry, ...]:
        """
        Retrieve recent transcript entries ordered newest first.

        Reads both memory and persistent sources independently best-effort.

        :param limit: Optional maximum number of entries to return.
                      None returns all entries.
                      0 returns an empty tuple.
                      Negative values raise ValueError.
        :return: Immutable tuple of defensively copied HistoryEntry objects.
        """
        if limit is not None:
            if limit < 0:
                raise ValueError("Limit cannot be negative.")
            if limit == 0:
                return ()

        with self._lock:
            memory_entries: Optional[List[HistoryEntry]] = None
            persistent_entries: Optional[List[HistoryEntry]] = None
            memory_error = False
            persistent_error = False

            try:
                memory_entries = self.history_manager.get_memory_entries()
            except Exception as e:
                logger.error("Failed to read memory entries in get_recent_entries: %s", e)
                memory_error = True

            try:
                persistent_entries = self.history_manager.get_persistent_entries()
            except Exception as e:
                logger.error("Failed to read persistent entries in get_recent_entries: %s", e)
                persistent_error = True

            if memory_error and persistent_error:
                logger.error("Both memory and persistent history queries failed in get_recent_entries.")
                return ()

            entry_map = {}
            if persistent_entries:
                for entry in persistent_entries:
                    entry_map[entry.id] = entry
            if memory_entries:
                for entry in memory_entries:
                    entry_map[entry.id] = entry

            combined = list(entry_map.values())
            combined.sort(key=lambda e: (e.timestamp, e.id), reverse=True)

            if limit is not None:
                combined = combined[:limit]

            return tuple(copy.deepcopy(combined))

    def reinsert_last(self) -> ReinsertionResult:
        """
        Reinsert the most recent final transcript entry.

        Uses memory-first order: tries memory history first, falling back to
        persistent DB only if memory is empty or unreadable.

        :return: ReinsertionResult indicating the outcome of the request.
        """
        with self._lock:
            memory_entries: Optional[List[HistoryEntry]] = None
            memory_error = False
            try:
                memory_entries = self.history_manager.get_memory_entries()
            except Exception as e:
                logger.warning("Failed to read memory history entries (will try persistent fallback): %s", e)
                memory_error = True

            if memory_entries:
                memory_entries.sort(key=lambda e: (e.timestamp, e.id), reverse=True)
                return self._enqueue_entry(memory_entries[0])

            # Fallback to persistent entries if memory is empty or failed
            persistent_entries: Optional[List[HistoryEntry]] = None
            persistent_error = False
            try:
                persistent_entries = self.history_manager.get_persistent_entries()
            except Exception as e:
                logger.error("Failed to query persistent transcript history: %s", e, exc_info=True)
                persistent_error = True

            if persistent_entries:
                persistent_entries.sort(key=lambda e: (e.timestamp, e.id), reverse=True)
                return self._enqueue_entry(persistent_entries[0])

            if memory_error or persistent_error:
                return ReinsertionResult(
                    status=ReinsertionStatus.FAILED,
                    reason="history_query_failed",
                    error_message="Failed to query transcript history.",
                )

            logger.info("reinsert_last requested but history is empty in memory and persistence.")
            return ReinsertionResult(
                status=ReinsertionStatus.EMPTY_HISTORY,
                reason="empty_history",
                error_message="No transcript history available.",
            )

    def reinsert_entry(self, entry_id: str) -> ReinsertionResult:
        """
        Reinsert a specific transcript entry by its ID.

        Uses memory-first order: searches memory history first, falling back to
        persistent DB search only if the entry is not found in memory.

        :param entry_id: The unique ID of the HistoryEntry to reinsert.
        :return: ReinsertionResult indicating the outcome of the request.
        """
        if not entry_id or not isinstance(entry_id, str) or not entry_id.strip():
            logger.warning("reinsert_entry called with invalid entry_id: %r", entry_id)
            return ReinsertionResult(
                status=ReinsertionStatus.ENTRY_NOT_FOUND,
                entry_id=entry_id if isinstance(entry_id, str) else None,
                reason="invalid_entry_id",
                error_message="Invalid entry ID provided.",
            )

        with self._lock:
            memory_entries: Optional[List[HistoryEntry]] = None
            memory_error = False
            try:
                memory_entries = self.history_manager.get_memory_entries()
            except Exception as e:
                logger.warning("Failed to read memory history entries: %s", e)
                memory_error = True

            if memory_entries:
                selected_entry = next((e for e in memory_entries if e.id == entry_id), None)
                if selected_entry is not None:
                    return self._enqueue_entry(selected_entry)

            # Fallback to persistent entries if not found in memory (or memory read failed)
            persistent_entries: Optional[List[HistoryEntry]] = None
            persistent_error = False
            try:
                persistent_entries = self.history_manager.get_persistent_entries()
            except Exception as e:
                logger.error("Failed to query persistent history for entry %s: %s", entry_id, e, exc_info=True)
                persistent_error = True

            if persistent_entries:
                selected_entry = next((e for e in persistent_entries if e.id == entry_id), None)
                if selected_entry is not None:
                    return self._enqueue_entry(selected_entry)

            if persistent_error or memory_error:
                return ReinsertionResult(
                    status=ReinsertionStatus.FAILED,
                    entry_id=entry_id,
                    reason="history_query_failed",
                    error_message=f"Failed to query transcript history for entry '{entry_id}'.",
                )

            logger.warning("reinsert_entry requested for unknown entry_id: %s", entry_id)
            return ReinsertionResult(
                status=ReinsertionStatus.ENTRY_NOT_FOUND,
                entry_id=entry_id,
                reason="entry_not_found",
                error_message=f"Entry '{entry_id}' not found in history.",
            )

    def _enqueue_entry(self, entry: HistoryEntry) -> ReinsertionResult:
        """
        Helper to enqueue a resolved entry into TextInjectionQueue and record attempts on failure.
        Must be called while holding self._lock.
        """
        text_len = len(entry.text) if entry.text else 0
        logger.info(
            "Attempting reinsertion for entry %s (session: %s, segment: %s, text_length: %d)",
            entry.id,
            entry.session_id,
            entry.segment_id,
            text_len,
        )

        try:
            entry_copy = copy.deepcopy(entry)
            accepted = self.injection_queue.enqueue(entry_copy)
        except Exception as ex:
            logger.exception("Unexpected exception during enqueue for entry %s: %s", entry.id, ex)
            try:
                self.history_manager.record_injection_attempt(
                    entry.id, status="failed", error=f"Enqueue exception: {ex}"
                )
            except Exception as hist_err:
                logger.error("Failed to log injection attempt for entry %s: %s", entry.id, hist_err)

            return ReinsertionResult(
                status=ReinsertionStatus.FAILED,
                entry_id=entry.id,
                reason="enqueue_exception",
                error_message=str(ex),
            )

        if accepted:
            logger.info("Reinsertion request queued for entry %s", entry.id)
            return ReinsertionResult(
                status=ReinsertionStatus.QUEUED,
                entry_id=entry.id,
            )
        else:
            logger.warning("Reinsertion rejected: TextInjectionQueue unavailable for entry %s", entry.id)
            try:
                self.history_manager.record_injection_attempt(
                    entry.id, status="skipped", error="Injection queue not running"
                )
            except Exception as hist_err:
                logger.error("Failed to log injection attempt for entry %s: %s", entry.id, hist_err)

            return ReinsertionResult(
                status=ReinsertionStatus.QUEUE_UNAVAILABLE,
                entry_id=entry.id,
                reason="queue_not_running",
                error_message="TextInjectionQueue is not running.",
            )
