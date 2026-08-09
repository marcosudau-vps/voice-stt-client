"""
Unit tests for TranscriptReinsertionService (Arbeitspaket 3).

Verifies memory-first selection, persistent fallback, attempt logging,
defensive tuple copies, limit handling, exception resilience, and concurrency safety.
"""

from __future__ import annotations

import copy
import logging
import tempfile
import threading
import unittest
from pathlib import Path
from typing import List, Optional, Tuple

from core.config import AppConfig
from core.history import HistoryEntry, InjectionAttempt, TranscriptHistoryManager
from core.reinsertion import ReinsertionResult, ReinsertionStatus, TranscriptReinsertionService
from core.text_injector import TextInjectionQueue, WindowsInjectionBackend


class ControlledHistoryManager:
    """Test double for TranscriptHistoryManager to track call counts and inject controlled data/errors."""

    def __init__(
        self,
        memory_entries: Optional[List[HistoryEntry]] = None,
        persistent_entries: Optional[List[HistoryEntry]] = None,
    ):
        self._memory = list(memory_entries) if memory_entries is not None else []
        self._persistent = list(persistent_entries) if persistent_entries is not None else []
        self.get_memory_calls = 0
        self.get_persistent_calls = 0
        self.record_attempt_calls = []
        self.memory_exception = False
        self.persistent_exception = False
        self.record_exception = False

    def get_memory_entries(self) -> List[HistoryEntry]:
        self.get_memory_calls += 1
        if self.memory_exception:
            raise RuntimeError("Simulated memory history failure")
        return copy.deepcopy(self._memory)

    def get_persistent_entries(self, limit: Optional[int] = None) -> List[HistoryEntry]:
        self.get_persistent_calls += 1
        if self.persistent_exception:
            raise RuntimeError("Simulated persistent history failure")
        res = copy.deepcopy(self._persistent)
        if limit is not None and limit > 0:
            res = res[:limit]
        return res

    def record_injection_attempt(self, entry_id: str, status: str, error: Optional[str] = None):
        self.record_attempt_calls.append((entry_id, status, error))
        if self.record_exception:
            raise RuntimeError("Simulated record attempt failure")
        attempt = InjectionAttempt(
            id=f"att_{len(self.record_attempt_calls)}",
            entry_id=entry_id,
            status=status,
            error=error,
            timestamp=1000.0,
        )
        for e in self._memory:
            if e.id == entry_id:
                e.attempts.append(attempt)
        for e in self._persistent:
            if e.id == entry_id:
                e.attempts.append(attempt)


class RecordingInjectionQueue:
    """Test double for TextInjectionQueue that records enqueued entries without running worker threads."""

    def __init__(self, return_value: bool = True):
        self.return_value = return_value
        self.enqueued_entries: List[HistoryEntry] = []
        self.raise_exception = False
        self._lock = threading.Lock()

    def enqueue(self, entry: HistoryEntry) -> bool:
        if self.raise_exception:
            raise RuntimeError("Enqueue exception simulated")
        with self._lock:
            self.enqueued_entries.append(entry)
        return self.return_value


class MockInjectionBackend(WindowsInjectionBackend):
    """Fake injection backend for integration testing with real queue."""

    def __init__(self):
        self.owner_created = False

    def create_owner_window(self) -> None:
        self.owner_created = True

    def destroy_owner_window(self) -> None:
        self.owner_created = False

    def get_owner_window(self) -> int:
        return 77777 if self.owner_created else 0

    def open_clipboard(self, hwnd: int) -> bool:
        return True

    def close_clipboard(self) -> bool:
        return True

    def empty_clipboard(self) -> bool:
        return True

    def is_format_available(self, format_id: int) -> bool:
        return True

    def get_clipboard_data_unicode(self):
        return None

    def set_clipboard_data_unicode(self, text: str) -> bool:
        return True

    def get_clipboard_sequence_number(self) -> int:
        return 1

    def get_foreground_window(self) -> int:
        return 42

    def get_window_thread_process_id(self, hwnd: int):
        return (123, 999)

    def send_input_keyboard(self, events) -> int:
        return len(events)


class TestTranscriptReinsertionService(unittest.TestCase):
    """Test suite for TranscriptReinsertionService."""

    def make_entry(self, entry_id: str, text: str, timestamp: float = 100.0) -> HistoryEntry:
        return HistoryEntry(
            id=entry_id,
            session_id="sess_1",
            segment_id=1,
            timestamp=timestamp,
            text=text,
            text_length=len(text),
            attempts=[],
        )

    # 1. reinsert_last() bei leerem Verlauf
    def test_reinsert_last_empty_history(self) -> None:
        history = ControlledHistoryManager()
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_last()
        self.assertEqual(res.status, ReinsertionStatus.EMPTY_HISTORY)
        self.assertEqual(res.reason, "empty_history")
        self.assertIsNone(res.entry_id)
        self.assertEqual(len(queue.enqueued_entries), 0)
        self.assertEqual(len(history.record_attempt_calls), 0)

    # 2. reinsert_last() wählt den jüngsten Eintrag
    def test_reinsert_last_selects_youngest_entry(self) -> None:
        e1 = self.make_entry("id_1", "Oldest", timestamp=100.0)
        e2 = self.make_entry("id_2", "Youngest", timestamp=200.0)
        history = ControlledHistoryManager(memory_entries=[e1, e2])
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_last()
        self.assertEqual(res.status, ReinsertionStatus.QUEUED)
        self.assertEqual(res.entry_id, e2.id)

    # 3. Identische Zeitstempel: deterministischer ID-Tie-Breaker
    def test_identical_timestamps_deterministic_selection(self) -> None:
        # sorted reverse=True by (timestamp, id): ("id_b" > "id_a") -> id_b selected
        e_a = self.make_entry("id_a", "Alpha", timestamp=1000.0)
        e_b = self.make_entry("id_b", "Beta", timestamp=1000.0)
        history = ControlledHistoryManager(memory_entries=[e_a, e_b])
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        res1 = service.reinsert_last()
        res2 = service.reinsert_last()

        # Both calls must select id_b deterministically
        self.assertEqual(res1.entry_id, "id_b")
        self.assertEqual(res2.entry_id, "id_b")

    # 4. Memory-first order: reinsert_last() calls memory, does NOT call persistent
    def test_memory_first_reinsert_last_does_not_call_persistent(self) -> None:
        e1 = self.make_entry("id_mem", "Memory Text", timestamp=100.0)
        e2 = self.make_entry("id_db", "Persistent Text", timestamp=200.0)
        history = ControlledHistoryManager(memory_entries=[e1], persistent_entries=[e2])
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_last()
        self.assertEqual(res.status, ReinsertionStatus.QUEUED)
        self.assertEqual(res.entry_id, e1.id)
        self.assertEqual(history.get_memory_calls, 1)
        self.assertEqual(history.get_persistent_calls, 0)

    # 5. Empty memory fallback: reinsert_last() calls persistent when memory is empty
    def test_empty_memory_reinsert_last_calls_persistent_fallback(self) -> None:
        e_db = self.make_entry("id_db", "Persistent Fallback Text", timestamp=200.0)
        history = ControlledHistoryManager(memory_entries=[], persistent_entries=[e_db])
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_last()
        self.assertEqual(res.status, ReinsertionStatus.QUEUED)
        self.assertEqual(res.entry_id, e_db.id)
        self.assertEqual(history.get_memory_calls, 1)
        self.assertEqual(history.get_persistent_calls, 1)

    # 6. Memory-first order: reinsert_entry() calls memory, does NOT call persistent on hit
    def test_memory_first_reinsert_entry_does_not_call_persistent(self) -> None:
        e1 = self.make_entry("id_mem", "Memory Text", timestamp=100.0)
        e2 = self.make_entry("id_db", "Persistent Text", timestamp=200.0)
        history = ControlledHistoryManager(memory_entries=[e1], persistent_entries=[e2])
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_entry(e1.id)
        self.assertEqual(res.status, ReinsertionStatus.QUEUED)
        self.assertEqual(res.entry_id, e1.id)
        self.assertEqual(history.get_memory_calls, 1)
        self.assertEqual(history.get_persistent_calls, 0)

    # 7. Missing memory entry: reinsert_entry() falls back to persistent DB
    def test_missing_memory_reinsert_entry_calls_persistent_fallback(self) -> None:
        e1 = self.make_entry("id_mem", "Memory Text", timestamp=100.0)
        e2 = self.make_entry("id_db", "Persistent Text", timestamp=200.0)
        history = ControlledHistoryManager(memory_entries=[e1], persistent_entries=[e2])
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_entry(e2.id)
        self.assertEqual(res.status, ReinsertionStatus.QUEUED)
        self.assertEqual(res.entry_id, e2.id)
        self.assertEqual(history.get_memory_calls, 1)
        self.assertEqual(history.get_persistent_calls, 1)

    # 8. Memory read error: falls back to persistent DB successfully
    def test_memory_error_uses_persistent_fallback(self) -> None:
        e_db = self.make_entry("id_db", "Persistent Fallback Text", timestamp=200.0)
        history = ControlledHistoryManager(persistent_entries=[e_db])
        history.memory_exception = True
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_last()
        self.assertEqual(res.status, ReinsertionStatus.QUEUED)
        self.assertEqual(res.entry_id, e_db.id)
        self.assertEqual(history.get_memory_calls, 1)
        self.assertEqual(history.get_persistent_calls, 1)

    # 9. Persistent read error does NOT affect an existing memory hit
    def test_persistent_error_does_not_affect_memory_hit(self) -> None:
        e_mem = self.make_entry("id_mem", "Memory Text", timestamp=100.0)
        history = ControlledHistoryManager(memory_entries=[e_mem])
        history.persistent_exception = True
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_last()
        self.assertEqual(res.status, ReinsertionStatus.QUEUED)
        self.assertEqual(res.entry_id, e_mem.id)
        self.assertEqual(history.get_memory_calls, 1)
        self.assertEqual(history.get_persistent_calls, 0)

    # 10. Both sources failing returns FAILED
    def test_both_sources_failing_returns_failed(self) -> None:
        history = ControlledHistoryManager()
        history.memory_exception = True
        history.persistent_exception = True
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_last()
        self.assertEqual(res.status, ReinsertionStatus.FAILED)
        self.assertEqual(res.reason, "history_query_failed")

    # 11. Unknown entry_id returns ENTRY_NOT_FOUND
    def test_unknown_entry_id_returns_not_found(self) -> None:
        history = ControlledHistoryManager()
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_entry("non_existent_id")
        self.assertEqual(res.status, ReinsertionStatus.ENTRY_NOT_FOUND)
        self.assertEqual(res.reason, "entry_not_found")
        self.assertEqual(res.entry_id, "non_existent_id")
        self.assertEqual(len(queue.enqueued_entries), 0)
        self.assertEqual(len(history.record_attempt_calls), 0)

    # 12. Invalid entry_id rejected cleanly
    def test_invalid_entry_id_rejected(self) -> None:
        history = ControlledHistoryManager()
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        res1 = service.reinsert_entry("")
        self.assertEqual(res1.status, ReinsertionStatus.ENTRY_NOT_FOUND)
        self.assertEqual(res1.reason, "invalid_entry_id")

        res2 = service.reinsert_entry("   ")
        self.assertEqual(res2.status, ReinsertionStatus.ENTRY_NOT_FOUND)
        self.assertEqual(res2.reason, "invalid_entry_id")

    # 13. Successful enqueue: QUEUED, no service attempt logged
    def test_successful_enqueue_returns_queued_no_attempt_logged(self) -> None:
        e = self.make_entry("id_1", "Original Text")
        history = ControlledHistoryManager(memory_entries=[e])
        queue = RecordingInjectionQueue(return_value=True)
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_entry(e.id)
        self.assertEqual(res.status, ReinsertionStatus.QUEUED)
        self.assertEqual(res.entry_id, e.id)
        self.assertEqual(len(queue.enqueued_entries), 1)
        self.assertEqual(queue.enqueued_entries[0].id, e.id)
        self.assertEqual(queue.enqueued_entries[0].text, "Original Text")
        # Service must NOT record attempt on success
        self.assertEqual(len(history.record_attempt_calls), 0)

    # 14. Queue rejected: QUEUE_UNAVAILABLE, skipped Attempt
    def test_queue_rejected_returns_queue_unavailable_skipped_attempt(self) -> None:
        e = self.make_entry("id_1", "Text when queue stopped")
        history = ControlledHistoryManager(memory_entries=[e])
        queue = RecordingInjectionQueue(return_value=False)
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_entry(e.id)
        self.assertEqual(res.status, ReinsertionStatus.QUEUE_UNAVAILABLE)
        self.assertEqual(res.reason, "queue_not_running")

        # Exactly 1 skipped attempt recorded on existing entry
        self.assertEqual(len(history.record_attempt_calls), 1)
        entry_id, status, error = history.record_attempt_calls[0]
        self.assertEqual(entry_id, e.id)
        self.assertEqual(status, "skipped")
        self.assertIn("queue not running", error.lower())

    # 15. Queue exception: FAILED, failed Attempt, exception caught
    def test_queue_exception_returns_failed_failed_attempt(self) -> None:
        e = self.make_entry("id_1", "Text for exception")
        history = ControlledHistoryManager(memory_entries=[e])
        queue = RecordingInjectionQueue()
        queue.raise_exception = True
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_entry(e.id)
        self.assertEqual(res.status, ReinsertionStatus.FAILED)
        self.assertEqual(res.reason, "enqueue_exception")
        self.assertIn("Enqueue exception simulated", res.error_message)

        # Exactly 1 failed attempt recorded on existing entry
        self.assertEqual(len(history.record_attempt_calls), 1)
        entry_id, status, error = history.record_attempt_calls[0]
        self.assertEqual(entry_id, e.id)
        self.assertEqual(status, "failed")

    # 16. Attempt logging failure is non-fatal
    def test_history_attempt_logging_failure_non_fatal(self) -> None:
        e = self.make_entry("id_1", "Text for logging error")
        history = ControlledHistoryManager(memory_entries=[e])
        history.record_exception = True
        queue = RecordingInjectionQueue(return_value=False)
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_entry(e.id)
        self.assertEqual(res.status, ReinsertionStatus.QUEUE_UNAVAILABLE)

    # 17. Reinsertion does NOT create a new HistoryEntry
    def test_reinsert_does_not_create_new_history_entry(self) -> None:
        e = self.make_entry("id_1", "Single Entry Text")
        history = ControlledHistoryManager(memory_entries=[e])
        queue = RecordingInjectionQueue(return_value=True)
        service = TranscriptReinsertionService(history, queue)

        service.reinsert_last()
        service.reinsert_entry(e.id)

        self.assertEqual(len(history.get_memory_entries()), 1)

    # 18. get_recent_entries() returns immutable tuple
    def test_get_recent_entries_returns_immutable_tuple(self) -> None:
        e1 = self.make_entry("id_1", "E1")
        history = ControlledHistoryManager(memory_entries=[e1])
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        recent = service.get_recent_entries()
        self.assertIsInstance(recent, tuple)
        with self.assertRaises(AttributeError):
            recent.append(e1)  # type: ignore
        with self.assertRaises(AttributeError):
            recent.pop()  # type: ignore

    # 19. get_recent_entries() deduplication and memory preference
    def test_get_recent_entries_deduplication_and_memory_preference(self) -> None:
        e_db = self.make_entry("shared_id", "DB Version", timestamp=100.0)
        e_mem = self.make_entry("shared_id", "Memory Version", timestamp=100.0)
        history = ControlledHistoryManager(memory_entries=[e_mem], persistent_entries=[e_db])
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        recent = service.get_recent_entries()
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0].text, "Memory Version")

    # 20. get_recent_entries() resilience on single-source failure
    def test_get_recent_entries_single_source_failure_resilience(self) -> None:
        e_mem = self.make_entry("id_mem", "Memory Text")
        e_db = self.make_entry("id_db", "DB Text")

        # Memory fails, persistent works
        h1 = ControlledHistoryManager(persistent_entries=[e_db])
        h1.memory_exception = True
        s1 = TranscriptReinsertionService(h1, RecordingInjectionQueue())
        res1 = s1.get_recent_entries()
        self.assertEqual(len(res1), 1)
        self.assertEqual(res1[0].id, e_db.id)

        # Persistent fails, memory works
        h2 = ControlledHistoryManager(memory_entries=[e_mem])
        h2.persistent_exception = True
        s2 = TranscriptReinsertionService(h2, RecordingInjectionQueue())
        res2 = s2.get_recent_entries()
        self.assertEqual(len(res2), 1)
        self.assertEqual(res2[0].id, e_mem.id)

        # Both fail -> empty tuple
        h3 = ControlledHistoryManager()
        h3.memory_exception = True
        h3.persistent_exception = True
        s3 = TranscriptReinsertionService(h3, RecordingInjectionQueue())
        res3 = s3.get_recent_entries()
        self.assertEqual(res3, ())

    # 21. get_recent_entries() limits and defensive copies
    def test_get_recent_entries_limits_and_defensive_copies(self) -> None:
        e1 = self.make_entry("id_1", "E1", timestamp=100.0)
        e2 = self.make_entry("id_2", "E2", timestamp=200.0)
        history = ControlledHistoryManager(memory_entries=[e1, e2])
        service = TranscriptReinsertionService(history, RecordingInjectionQueue())

        self.assertEqual(len(service.get_recent_entries(limit=None)), 2)
        self.assertEqual(service.get_recent_entries(limit=0), ())
        self.assertEqual(len(service.get_recent_entries(limit=1)), 1)
        self.assertEqual(service.get_recent_entries(limit=1)[0].id, e2.id)

        with self.assertRaises(ValueError):
            service.get_recent_entries(limit=-1)

        # Defensive copy mutation test
        recent = service.get_recent_entries()
        recent[0].text = "MUTATED"
        self.assertEqual(history.get_memory_entries()[1].text, "E2")

    # 22. Concurrent reinsert calls with threading.Barrier
    def test_concurrent_reinsert_calls_no_duplicate_entries(self) -> None:
        e = self.make_entry("id_1", "Concurrent test text")
        history = ControlledHistoryManager(memory_entries=[e])
        queue = RecordingInjectionQueue(return_value=True)
        service = TranscriptReinsertionService(history, queue)

        barrier = threading.Barrier(5)
        results = []
        results_lock = threading.Lock()

        def worker():
            barrier.wait()
            res = service.reinsert_last()
            with results_lock:
                results.append(res)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=2.0)

        # 1. Nach join(timeout=...) darf kein Thread mehr alive sein
        for t in threads:
            self.assertFalse(t.is_alive())

        self.assertEqual(len(results), 5)
        for r in results:
            self.assertEqual(r.status, ReinsertionStatus.QUEUED)

        # 2. Die RecordingInjectionQueue muss exakt fünf Enqueues enthalten
        self.assertEqual(len(queue.enqueued_entries), 5)

        # 3. Alle fünf Enqueues müssen dieselbe vorhandene Entry-ID verwenden
        for enq_entry in queue.enqueued_entries:
            self.assertEqual(enq_entry.id, e.id)

        # 4. Es darf kein InjectionAttempt durch den Service erzeugt worden sein
        self.assertEqual(len(history.record_attempt_calls), 0)

        # Still only 1 HistoryEntry in memory
        self.assertEqual(len(history.get_memory_entries()), 1)

    # 25. reinsert_last(): Memory-Lesen schlägt fehl, Persistenz erfolgreich lesbar aber leer -> FAILED
    def test_reinsert_last_memory_error_persistent_empty_returns_failed(self) -> None:
        history = ControlledHistoryManager(persistent_entries=[])
        history.memory_exception = True
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_last()
        self.assertEqual(res.status, ReinsertionStatus.FAILED)
        self.assertEqual(res.reason, "history_query_failed")
        self.assertEqual(len(queue.enqueued_entries), 0)
        self.assertEqual(len(history.record_attempt_calls), 0)

    # 26. reinsert_entry(): Memory-Lesen schlägt fehl, Persistenz enthält anderen Eintrag aber nicht angeforderte ID -> FAILED
    def test_reinsert_entry_memory_error_persistent_has_other_entry_returns_failed(self) -> None:
        e_other = self.make_entry("id_other", "Other Text")
        history = ControlledHistoryManager(persistent_entries=[e_other])
        history.memory_exception = True
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        res = service.reinsert_entry("id_target")
        self.assertEqual(res.status, ReinsertionStatus.FAILED)
        self.assertEqual(res.reason, "history_query_failed")
        self.assertEqual(res.entry_id, "id_target")
        self.assertEqual(len(queue.enqueued_entries), 0)
        self.assertEqual(len(history.record_attempt_calls), 0)

    # 23. No transcript text in log
    def test_no_transcript_text_logged(self) -> None:
        secret_text = "SECRET_PASSWORD_98765"
        e = self.make_entry("id_secret", secret_text)
        history = ControlledHistoryManager(memory_entries=[e])
        queue = RecordingInjectionQueue()
        service = TranscriptReinsertionService(history, queue)

        with self.assertLogs("text", level="INFO") as cm:
            service.reinsert_entry(e.id)

        for log_line in cm.output:
            self.assertNotIn(secret_text, log_line, "Secret transcript text was found in log output!")

    # 24. Integration test with real TextInjectionQueue & TranscriptHistoryManager
    def test_integration_multiple_attempts_accumulate_with_real_components(self) -> None:
        tmp_dir = tempfile.TemporaryDirectory()
        try:
            db_path = Path(tmp_dir.name) / "test_integration.db"
            cfg = AppConfig()
            cfg.history.enabled = True
            cfg.history.persistent.enabled = True
            cfg.history.persistent.store_all = True
            cfg.history.persistent.min_characters = 0

            real_history = TranscriptHistoryManager(config=cfg.history, db_path=str(db_path))
            backend = MockInjectionBackend()
            real_queue = TextInjectionQueue(config=cfg, history_manager=real_history, backend=backend)
            service = TranscriptReinsertionService(history_manager=real_history, injection_queue=real_queue)

            real_queue.start()
            e = real_history.add_entry("sess_1", 1, "Integration Test Text")

            service.reinsert_last()
            service.reinsert_last()

            real_queue.stop()

            entry = real_history.get_persistent_entries()[0]
            self.assertEqual(len(entry.attempts), 2)
            self.assertEqual(entry.id, e.id)
        finally:
            tmp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
