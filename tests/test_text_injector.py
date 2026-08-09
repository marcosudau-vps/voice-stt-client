"""
Unit tests for the TextInjectionQueue and WindowsInjectionBackend.
"""

from __future__ import annotations

import ctypes
import os
import shutil
import tempfile
import threading
import time
import unittest
import uuid
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from core.config import AppConfig, HistoryConfig, HistoryMemoryConfig, HistoryPersistentConfig
from core.history import TranscriptHistoryManager, HistoryEntry
from core.text_injector import (
    TextInjectionQueue,
    WindowsInjectionBackend,
    CtypesWindowsInjectionBackend,
    InjectionJob,
    QueueState,
    INPUT,
    KEYBDINPUT
)

# -------------------------------------------------------------------
# Mock Backend for Testing
# -------------------------------------------------------------------

class MockInjectionBackend(WindowsInjectionBackend):
    def __init__(self) -> None:
        self.clipboard_data: Optional[str] = None
        self.clipboard_open = False
        self.sequence_number = 1
        self.foreground_window = 42
        self.pid = 999
        self.tid = 123
        self.send_input_result = 4  # Default to successful Ctrl+V (4 events)

        # Trackers / logs
        self.open_calls = 0
        self.successful_open_count = 0
        self.close_count = 0
        self.empty_calls = 0
        self.set_calls: List[str] = []
        self.send_input_calls: List[List[Tuple[int, bool]]] = []
        self.foreground_window_calls: List[float] = []
        self.is_format_available_result = True
        
        self.last_owner_passed: Optional[int] = None
        self.owner_window = 77777
        self.owner_created = False
        self.event_log: List[Tuple[str, any]] = []

        # Behavior controls / exception triggers
        self.open_fail_count = 0
        self.current_open_fails = 0
        
        self.exception_on_format_check = False
        self.exception_on_get_data = False
        self.exception_on_empty = False
        self.exception_on_set = False
        self.exception_on_send_input = False
        self.exception_on_seq_number = False

        self.set_fail = False
        self.exception_on_create_owner = False

    def create_owner_window(self) -> None:
        if self.exception_on_create_owner:
            raise RuntimeError("CreateWindowExW exception simulated")
        self.owner_created = True
        self.event_log.append(("create_owner_window", self.owner_window))

    def destroy_owner_window(self) -> None:
        self.owner_created = False
        self.event_log.append(("destroy_owner_window", self.owner_window))

    def get_owner_window(self) -> int:
        return self.owner_window if self.owner_created else 0

    def open_clipboard(self, hwnd: int) -> bool:
        self.open_calls += 1
        self.last_owner_passed = hwnd
        self.event_log.append(("open_clipboard", hwnd))
        if self.current_open_fails < self.open_fail_count:
            self.current_open_fails += 1
            return False
        self.clipboard_open = True
        self.successful_open_count += 1
        return True

    def close_clipboard(self) -> bool:
        self.close_count += 1
        self.clipboard_open = False
        self.event_log.append(("close_clipboard", None))
        return True

    def empty_clipboard(self) -> bool:
        if self.exception_on_empty:
            raise RuntimeError("Empty clipboard exception simulated")
        self.empty_calls += 1
        self.clipboard_data = None
        self.event_log.append(("empty_clipboard", None))
        return True

    def is_format_available(self, format_id: int) -> bool:
        if self.exception_on_format_check:
            raise RuntimeError("Format check exception simulated")
        return self.is_format_available_result

    def get_clipboard_data_unicode(self) -> Optional[str]:
        if self.exception_on_get_data:
            raise RuntimeError("Get clipboard data exception simulated")
        return self.clipboard_data

    def set_clipboard_data_unicode(self, text: str) -> bool:
        if self.exception_on_set:
            raise RuntimeError("Set clipboard data exception simulated")
        if self.set_fail and text != "user backup text":
            return False
        self.set_calls.append(text)
        self.clipboard_data = text
        self.sequence_number += 1
        self.event_log.append(("set_clipboard_data", text))
        return True

    def get_clipboard_sequence_number(self) -> int:
        self.seq_calls = getattr(self, "seq_calls", 0) + 1
        if self.exception_on_seq_number and self.seq_calls > 1:
            raise RuntimeError("Sequence number exception simulated")
        self.event_log.append(("get_sequence_number", self.sequence_number))
        return self.sequence_number

    def get_foreground_window(self) -> int:
        self.foreground_window_calls.append(time.time())
        self.event_log.append(("get_foreground_window", self.foreground_window))
        return self.foreground_window

    def get_window_thread_process_id(self, hwnd: int) -> Tuple[int, int]:
        self.event_log.append(("get_window_thread_process_id", hwnd))
        return self.tid, self.pid

    def send_input_keyboard(self, events: List[Tuple[int, bool]]) -> int:
        if self.exception_on_send_input:
            raise RuntimeError("SendInput exception simulated")
        self.send_input_calls.append(events)
        self.event_log.append(("send_input_keyboard", events))
        return self.send_input_result

# -------------------------------------------------------------------
# Test Cases
# -------------------------------------------------------------------

class TestTextInjector(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_injector.db")
        self.history_config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=10),
            persistent=HistoryPersistentConfig(enabled=True, store_all=True)
        )
        self.history = TranscriptHistoryManager(self.history_config, db_path=self.db_path)
        self.backend = MockInjectionBackend()

        # Default configuration
        self.config = AppConfig()
        self.config.text_injection.paste_delay_ms = 0
        self.config.clipboard.restore_delay_ms = 0
        self.config.clipboard.open_retries = 2
        self.config.clipboard.open_retry_delay_ms = 1
        
        self.queues_to_stop: List[TextInjectionQueue] = []

    def tearDown(self) -> None:
        # Clean shutdown of running queues to prevent leaks
        for q in self.queues_to_stop:
            try:
                q.stop(timeout=1.0)
            except Exception:
                pass
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass

    def _create_queue(self) -> TextInjectionQueue:
        q = TextInjectionQueue(self.config, self.history, self.backend)
        self.queues_to_stop.append(q)
        return q

    # 1. Native Win32-Strukturen exakt abbilden
    def test_win32_structure_sizes(self) -> None:
        if sys.platform != "win32":
            self.skipTest("Only run on Windows development environment.")
        
        is_64 = sys.maxsize > 2**32
        expected_input_size = 40 if is_64 else 28
        expected_keybd_size = 24 if is_64 else 16

        self.assertEqual(ctypes.sizeof(INPUT), expected_input_size)
        self.assertEqual(ctypes.sizeof(KEYBDINPUT), expected_keybd_size)

    # 2. ClipboardConfig deserialization & save/load checks
    def test_config_nested_deserialization(self) -> None:
        raw = {
            "clipboard": {
                "restore_previous": True,
                "restore_delay_ms": 150,
                "backup_max_bytes": 500,
                "open_retries": 10,
                "open_retry_delay_ms": 5
            }
        }
        config = AppConfig._from_dict(raw)
        self.assertTrue(config.clipboard.restore_previous)
        self.assertEqual(config.clipboard.restore_delay_ms, 150)
        self.assertEqual(config.clipboard.backup_max_bytes, 500)
        self.assertEqual(config.clipboard.open_retries, 10)
        self.assertEqual(config.clipboard.open_retry_delay_ms, 5)

    def test_config_save_load_roundtrip(self) -> None:
        config_path = os.path.join(self.temp_dir, "roundtrip.yaml")
        cfg = AppConfig()
        cfg.clipboard.restore_previous = True
        cfg.clipboard.restore_delay_ms = 400
        cfg.clipboard.backup_max_bytes = 2048
        cfg.clipboard.open_retries = 8
        cfg.clipboard.open_retry_delay_ms = 15

        cfg.save(Path(config_path))
        loaded = AppConfig.load(Path(config_path))

        self.assertTrue(loaded.clipboard.restore_previous)
        self.assertEqual(loaded.clipboard.restore_delay_ms, 400)
        self.assertEqual(loaded.clipboard.backup_max_bytes, 2048)
        self.assertEqual(loaded.clipboard.open_retries, 8)
        self.assertEqual(loaded.clipboard.open_retry_delay_ms, 15)

    # 3. start() ist idempotent.
    def test_start_idempotency(self) -> None:
        q = self._create_queue()
        q.start()
        thread_1 = q._worker_thread
        self.assertTrue(q.is_running())

        q.start()
        thread_2 = q._worker_thread
        self.assertEqual(thread_1, thread_2)
        q.stop()

    # 4. stop() ist idempotent.
    def test_stop_idempotency(self) -> None:
        q = self._create_queue()
        q.start()
        q.stop()
        self.assertFalse(q.is_running())
        q.stop()

    # 5. Mehrfaches start() erzeugt exakt einen Worker.
    def test_multiple_start_single_worker(self) -> None:
        q = self._create_queue()
        active_threads_before = threading.active_count()
        q.start()
        q.start()
        q.start()
        active_threads_after = threading.active_count()
        self.assertEqual(active_threads_after - active_threads_before, 1)
        q.stop()

    # 6. Mehrere Aufträge werden strikt in FIFO-Reihenfolge verarbeitet.
    # 7. Es ist niemals mehr als ein Auftrag gleichzeitig aktiv.
    def test_fifo_and_single_active_job(self) -> None:
        q = self._create_queue()
        q.start()

        reached_events = [threading.Event(), threading.Event(), threading.Event()]
        proceed_events = [threading.Event(), threading.Event(), threading.Event()]
        job_order = []

        original_get_fw = self.backend.get_foreground_window
        def sync_get_fw() -> int:
            original_get_fw()
            idx = len(job_order)
            job_order.append(idx)
            reached_events[idx].set()
            proceed_events[idx].wait()
            return self.backend.foreground_window

        self.backend.get_foreground_window = sync_get_fw

        e1 = self.history.add_entry("sess_1", 1, "First")
        e2 = self.history.add_entry("sess_1", 2, "Second")
        e3 = self.history.add_entry("sess_1", 3, "Third")

        q.enqueue(e1)
        q.enqueue(e2)
        q.enqueue(e3)

        # Wait until job 0 starts processing
        self.assertTrue(reached_events[0].wait(timeout=2.0))
        self.assertFalse(reached_events[1].is_set())

        # Release job 0
        proceed_events[0].set()

        # Wait until job 1 starts processing
        self.assertTrue(reached_events[1].wait(timeout=2.0))
        self.assertFalse(reached_events[2].is_set())

        # Release job 1
        proceed_events[1].set()

        # Wait until job 2 starts processing
        self.assertTrue(reached_events[2].wait(timeout=2.0))

        # Release job 2
        proceed_events[2].set()

        # Let queue worker finish
        q.stop()

        self.assertEqual(job_order, [0, 1, 2])

    # 8. Ein Fehler in einem Auftrag beendet den Worker nicht.
    def test_error_in_job_does_not_kill_worker(self) -> None:
        q = self._create_queue()
        q.start()

        original_set = self.backend.set_clipboard_data_unicode
        def faulty_set(text: str) -> bool:
            if text == "fail":
                raise RuntimeError("Clipboard error simulated")
            return original_set(text)
        self.backend.set_clipboard_data_unicode = faulty_set

        e_fail = self.history.add_entry("sess_1", 1, "fail")
        e_ok = self.history.add_entry("sess_1", 2, "ok")

        q.enqueue(e_fail)
        q.enqueue(e_ok)

        q.stop()

        attempts_fail = self.history.get_persistent_entries()[0].attempts
        attempts_ok = self.history.get_persistent_entries()[1].attempts

        self.assertEqual(attempts_fail[0].status, "failed")
        self.assertEqual(attempts_ok[0].status, "command_sent")

    # 9. Bereits angenommene Aufträge werden beim kontrollierten Stop vollständig abgearbeitet.
    def test_stop_drains_queue(self) -> None:
        q = self._create_queue()
        q.start()

        reached = threading.Event()
        blocker = threading.Event()

        original_get_fw = self.backend.get_foreground_window
        def blocked_fw() -> int:
            reached.set()
            blocker.wait()
            return original_get_fw()
        self.backend.get_foreground_window = blocked_fw

        e1 = self.history.add_entry("sess_1", 1, "Job 1")
        e2 = self.history.add_entry("sess_1", 2, "Job 2")

        q.enqueue(e1)
        q.enqueue(e2)

        reached.wait(timeout=2.0)
        q.stop(timeout=0.05) # start stop process, but timeout immediately to release blocker

        # Thread must still be alive because blocker is not set
        self.assertTrue(q._worker_thread.is_alive())

        blocker.set()
        q.stop() # Wait for final join

        attempts_1 = self.history.get_persistent_entries()[0].attempts
        attempts_2 = self.history.get_persistent_entries()[1].attempts
        self.assertEqual(attempts_1[0].status, "command_sent")
        self.assertEqual(attempts_2[0].status, "command_sent")

    # 10. Nach beendetem Stop werden keine neuen Aufträge akzeptiert.
    def test_no_new_jobs_accepted_after_stop(self) -> None:
        q = self._create_queue()
        q.start()
        q.stop()

        e = self.history.add_entry("sess_1", 1, "text")
        res = q.enqueue(e)
        self.assertFalse(res)

    # 11. Enqueue vor start() wird eindeutig abgelehnt
    def test_enqueue_before_start_rejected(self) -> None:
        q = self._create_queue()
        e = self.history.add_entry("sess_1", 1, "text")
        res = q.enqueue(e)
        self.assertFalse(res)
        self.assertEqual(q.queue_size(), 0)

    # 12. queue_size() zählt keinen Sentinel
    def test_queue_size_excludes_sentinel(self) -> None:
        q = self._create_queue()
        q.start()
        
        reached_active = threading.Event()
        blocker = threading.Event()
        
        original_fw = self.backend.get_foreground_window
        def blocked_fw() -> int:
            reached_active.set()
            blocker.wait()
            return original_fw()
        self.backend.get_foreground_window = blocked_fw

        e1 = self.history.add_entry("sess_1", 1, "Job 1")
        e2 = self.history.add_entry("sess_1", 2, "Job 2")
        q.enqueue(e1)
        q.enqueue(e2)

        # Wait deterministically until Job 1 is popped and active (blocked)
        self.assertTrue(reached_active.wait(timeout=2.0))

        # Stop enqueues the sentinel None
        q.stop(timeout=0.01)

        # queue_size should count exactly 1 (only Job 2; Job 1 is active, None is sentinel)
        self.assertEqual(q.queue_size(), 1)

        # Release and cleanup
        blocker.set()
        q.stop()

    # 13. Leerer Text wird als skipped behandelt
    def test_empty_text_skipped(self) -> None:
        q = self._create_queue()
        q.start()

        e = self.history.add_entry("sess_1", 1, "")
        q.enqueue(e)
        q.stop()

        attempts = self.history.get_persistent_entries()[0].attempts
        self.assertEqual(attempts[0].status, "skipped")
        self.assertEqual(attempts[0].error, "Empty text")

    # 14. Locked Clipboard succeeds on retry
    def test_clipboard_open_retry_success(self) -> None:
        q = self._create_queue()
        q.start()

        self.backend.open_fail_count = 1
        e = self.history.add_entry("sess_1", 1, "Retry success")
        q.enqueue(e)
        q.stop()

        attempts = self.history.get_persistent_entries()[0].attempts
        self.assertEqual(attempts[0].status, "command_sent")
        self.assertGreater(self.backend.open_calls, 1)

    # 15. Locked Clipboard fails on all retries
    def test_clipboard_open_retry_fail(self) -> None:
        q = self._create_queue()
        q.start()

        self.backend.open_fail_count = 3
        e = self.history.add_entry("sess_1", 1, "Retry fail")
        q.enqueue(e)
        q.stop()

        attempts = self.history.get_persistent_entries()[0].attempts
        self.assertEqual(attempts[0].status, "failed")

    # 16. Unicode-Text Unterstützung
    def test_unicode_support(self) -> None:
        q = self._create_queue()
        q.start()

        unicode_text = "Öl, Übergriff, 🌈 Emojis and Umlauts!"
        e = self.history.add_entry("sess_1", 1, unicode_text)
        q.enqueue(e)
        q.stop()

        self.assertEqual(self.backend.clipboard_data, unicode_text)

    # 17. restore_previous: false leaves transcript in clipboard
    def test_restore_previous_false(self) -> None:
        self.config.clipboard.restore_previous = False
        self.backend.clipboard_data = "initial"
        
        q = self._create_queue()
        q.start()

        e = self.history.add_entry("sess_1", 1, "new text")
        q.enqueue(e)
        q.stop()

        self.assertEqual(self.backend.clipboard_data, "new text")

    # 18. restore_previous: true restores clipboard
    def test_restore_previous_true_success(self) -> None:
        self.config.clipboard.restore_previous = True
        self.backend.clipboard_data = "initial clipboard"

        q = self._create_queue()
        q.start()

        e = self.history.add_entry("sess_1", 1, "new text")
        q.enqueue(e)
        q.stop()

        self.assertEqual(self.backend.clipboard_data, "initial clipboard")

    # 19. Clipboard content above backup_max_bytes is not restored
    def test_restore_max_bytes_exceeded(self) -> None:
        self.config.clipboard.restore_previous = True
        self.config.clipboard.backup_max_bytes = 10
        self.backend.clipboard_data = "too long content here"

        q = self._create_queue()
        q.start()

        e = self.history.add_entry("sess_1", 1, "new text")
        q.enqueue(e)
        q.stop()

        self.assertEqual(self.backend.clipboard_data, "new text")

    # 20. External clipboard sequence change prevents restore
    def test_sequence_number_prevents_restore(self) -> None:
        self.config.clipboard.restore_previous = True
        self.backend.clipboard_data = "initial text"

        q = self._create_queue()
        q.start()

        original_send_input = self.backend.send_input_keyboard
        def modifying_send_input(events: List[Tuple[int, bool]]) -> int:
            res = original_send_input(events)
            self.backend.sequence_number += 1
            return res
        self.backend.send_input_keyboard = modifying_send_input

        e = self.history.add_entry("sess_1", 1, "new text")
        q.enqueue(e)
        q.stop()

        self.assertEqual(self.backend.clipboard_data, "new text")

    # 21. Restore error doesn't change command_sent to failed
    def test_restore_failure_does_not_change_status(self) -> None:
        self.config.clipboard.restore_previous = True
        self.backend.clipboard_data = "initial text"

        q = self._create_queue()
        q.start()

        original_close = self.backend.close_clipboard
        def faulty_close() -> bool:
            if self.backend.open_calls > 2:
                raise RuntimeError("Failed to restore clipboard connection")
            return original_close()
        self.backend.close_clipboard = faulty_close

        e = self.history.add_entry("sess_1", 1, "new text")
        q.enqueue(e)
        q.stop()

        attempts = self.history.get_persistent_entries()[0].attempts
        self.assertEqual(attempts[0].status, "command_sent")

    # 22. Foreground Windowtiming check
    def test_foreground_window_timing(self) -> None:
        q = self._create_queue()
        q.start()

        e1 = self.history.add_entry("sess_1", 1, "First")
        e2 = self.history.add_entry("sess_1", 2, "Second")

        q.enqueue(e1)
        q.enqueue(e2)
        q.stop()

        self.assertEqual(len(self.backend.foreground_window_calls), 2)
        t1, t2 = self.backend.foreground_window_calls
        self.assertLessEqual(t1, t2)

    # 23. SendInput with incomplete events results in failed
    def test_send_input_failure(self) -> None:
        self.backend.send_input_result = 3

        q = self._create_queue()
        q.start()

        e = self.history.add_entry("sess_1", 1, "Text")
        q.enqueue(e)
        q.stop()

        attempts = self.history.get_persistent_entries()[0].attempts
        self.assertEqual(attempts[0].status, "failed")
        self.assertEqual(attempts[0].error, "SendInput failed")

    # 24. Successful SendInput creates command_sent
    def test_send_input_success_attempt(self) -> None:
        q = self._create_queue()
        q.start()

        e = self.history.add_entry("sess_1", 1, "Success text")
        q.enqueue(e)
        q.stop()

        attempts = self.history.get_persistent_entries()[0].attempts
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0].status, "command_sent")

    # 25. Job processed after failure
    def test_job_processed_after_failure(self) -> None:
        q = self._create_queue()
        q.start()

        call_count = [0]
        original_send = self.backend.send_input_keyboard
        def toggle_send(events: List[Tuple[int, bool]]) -> int:
            call_count[0] += 1
            if call_count[0] == 1:
                return 0
            return original_send(events)
        self.backend.send_input_keyboard = toggle_send

        e1 = self.history.add_entry("sess_1", 1, "Job 1")
        e2 = self.history.add_entry("sess_1", 2, "Job 2")

        q.enqueue(e1)
        q.enqueue(e2)
        q.stop()

        attempts_1 = self.history.get_persistent_entries()[0].attempts
        attempts_2 = self.history.get_persistent_entries()[1].attempts

        self.assertEqual(attempts_1[0].status, "failed")
        self.assertEqual(attempts_2[0].status, "command_sent")

    # 26. Enqueued job data is not modified by subsequent modifications
    def test_enqueue_copies_data(self) -> None:
        q = self._create_queue()
        blocker = threading.Event()
        original_open = self.backend.open_clipboard
        def blocked_open(hwnd: int) -> bool:
            blocker.wait()
            return original_open(hwnd)
        self.backend.open_clipboard = blocked_open

        q.start()
        e = self.history.add_entry("sess_1", 1, "original text")
        q.enqueue(e)

        e.text = "mutated text"

        blocker.set()
        q.stop()

        self.assertEqual(self.backend.clipboard_data, "original text")

    # 27. Gültigen Clipboard-Owner verwenden
    def test_valid_clipboard_owner(self) -> None:
        q = self._create_queue()
        q.start()
        
        e = self.history.add_entry("sess_1", 1, "test text")
        q.enqueue(e)
        q.stop()

        self.assertIsNotNone(self.backend.last_owner_passed)
        self.assertEqual(self.backend.last_owner_passed, self.backend.owner_window)
        self.assertNotEqual(self.backend.last_owner_passed, 0)
        self.assertNotEqual(self.backend.last_owner_passed, self.backend.foreground_window)

    # 28. Clipboard immer in finally schließen
    def test_clipboard_close_guarantees_on_exceptions(self) -> None:
        self.config.clipboard.restore_previous = True
        self.backend.clipboard_data = "initial data"
        self.backend.exception_on_format_check = True
        
        q = self._create_queue()
        q.start()
        e1 = self.history.add_entry("sess_1", 1, "text")
        q.enqueue(e1)
        q.stop()
        
        self.assertEqual(self.backend.successful_open_count, self.backend.close_count)
        
        self.backend = MockInjectionBackend()
        self.backend.exception_on_empty = True
        q = self._create_queue()
        q.start()
        e2 = self.history.add_entry("sess_1", 2, "text")
        q.enqueue(e2)
        q.stop()
        
        self.assertEqual(self.backend.successful_open_count, self.backend.close_count)

        self.backend = MockInjectionBackend()
        self.config.clipboard.restore_previous = True
        self.backend.clipboard_data = "initial data"
        
        original_empty = self.backend.empty_clipboard
        def restore_empty_fail() -> bool:
            if self.backend.open_calls > 2:
                raise RuntimeError("Empty exception in restore")
            return original_empty()
        self.backend.empty_clipboard = restore_empty_fail
        
        q = self._create_queue()
        q.start()
        e3 = self.history.add_entry("sess_1", 3, "text")
        q.enqueue(e3)
        q.stop()
        
        self.assertEqual(self.backend.successful_open_count, self.backend.close_count)

    # 29. Fehlgeschlagenes Schreiben darf das alte Clipboard nicht unnötig verlieren
    def test_failed_write_restores_backup(self) -> None:
        self.config.clipboard.restore_previous = True
        self.backend.clipboard_data = "user backup text"
        self.backend.set_fail = True
        
        q = self._create_queue()
        q.start()
        e = self.history.add_entry("sess_1", 1, "transcript text")
        q.enqueue(e)
        q.stop()

        self.assertEqual(self.backend.clipboard_data, "user backup text")
        
        attempts = self.history.get_persistent_entries()[0].attempts
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0].status, "failed")

    # 30. Genau einen finalen History-Attempt pro Job garantieren
    def test_guarantees_exactly_one_history_attempt(self) -> None:
        # Case A: command_sent, thereafter exception during restore seq lookup
        self.config.clipboard.restore_previous = True
        self.backend.clipboard_data = "backup"
        self.backend.exception_on_seq_number = True
        
        q = self._create_queue()
        q.start()
        e1 = self.history.add_entry("sess_1", 1, "command sent")
        q.enqueue(e1)
        q.stop()

        attempts_1 = self.history.get_persistent_entries()[0].attempts
        self.assertEqual(len(attempts_1), 1)
        self.assertEqual(attempts_1[0].status, "command_sent")

        # Case B: skipped (no foreground window), thereafter exception during restore
        self.backend = MockInjectionBackend()
        self.config.clipboard.restore_previous = True
        self.backend.clipboard_data = "backup"
        self.backend.foreground_window = 0
        self.backend.exception_on_seq_number = True

        q = self._create_queue()
        q.start()
        e2 = self.history.add_entry("sess_1", 2, "skipped text")
        q.enqueue(e2)
        q.stop()

        attempts_2 = self.history.get_persistent_entries()[1].attempts
        self.assertEqual(len(attempts_2), 1)
        self.assertEqual(attempts_2[0].status, "skipped")

        # Case C: failed (SendInput), thereafter exception during restore
        self.backend = MockInjectionBackend()
        self.config.clipboard.restore_previous = True
        self.backend.clipboard_data = "backup"
        self.backend.exception_on_send_input = True
        self.backend.exception_on_seq_number = True

        q = self._create_queue()
        q.start()
        e3 = self.history.add_entry("sess_1", 3, "failed text")
        q.enqueue(e3)
        q.stop()

        attempts_3 = self.history.get_persistent_entries()[2].attempts
        self.assertEqual(len(attempts_3), 1)
        self.assertEqual(attempts_3[0].status, "failed")

    # 31. Foreground- und SendInput-Reihenfolge stärker testen
    def test_foreground_and_send_input_order(self) -> None:
        q = self._create_queue()
        q.start()

        e = self.history.add_entry("sess_1", 1, "paste text")
        q.enqueue(e)
        q.stop()

        event_names = [name for name, _ in self.backend.event_log]
        
        set_idx = event_names.index("set_clipboard_data")
        seq_idx = event_names.index("get_sequence_number")
        fw_idx = event_names.index("get_foreground_window")
        pid_idx = event_names.index("get_window_thread_process_id")
        send_idx = event_names.index("send_input_keyboard")

        self.assertLess(set_idx, seq_idx)
        self.assertLess(seq_idx, fw_idx)
        self.assertLess(fw_idx, pid_idx)
        self.assertLess(pid_idx, send_idx)

        send_events = self.backend.event_log[send_idx][1]
        expected_events = [
            (0x11, False),  # Ctrl Down
            (0x56, False),  # V Down
            (0x56, True),   # V Up
            (0x11, True)    # Ctrl Up
        ]
        self.assertEqual(send_events, expected_events)

    # 32. HWND == 0 -> skipped, no SendInput
    def test_hwnd_zero_skipped(self) -> None:
        self.backend.foreground_window = 0
        q = self._create_queue()
        q.start()

        e = self.history.add_entry("sess_1", 1, "test text")
        q.enqueue(e)
        q.stop()

        attempts = self.history.get_persistent_entries()[0].attempts
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0].status, "skipped")
        self.assertEqual(attempts[0].error, "No foreground window")

        send_input_calls = [name for name, _ in self.backend.event_log if name == "send_input_keyboard"]
        self.assertEqual(len(send_input_calls), 0)

    # 33. Check SetForegroundWindow is never used in the module
    def test_no_forbidden_win32_calls(self) -> None:
        path = Path(__file__).resolve().parent.parent / "core" / "text_injector.py"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        forbidden = [
            "SetForegroundWindow",
            "AppActivate",
            "pyautogui",
            "pynput",
            "SendKeys"
        ]
        for term in forbidden:
            self.assertNotIn(term, content, f"Forbidden API or library '{term}' found in text_injector.py!")

    # 34. Owner Window Erstellung schlägt fehl (fail-closed)
    def test_init_fail_closed_owner_none(self) -> None:
        self.backend.exception_on_create_owner = True
        q = self._create_queue()
        
        # start() must raise the exception
        with self.assertRaises(RuntimeError):
            q.start()
            
        # Verify state is STOPPED
        self.assertEqual(q._state, QueueState.STOPPED)
        
        # Verify no job is accepted
        e = self.history.add_entry("sess_1", 1, "Should be rejected")
        self.assertFalse(q.enqueue(e))
        
        # Verify open_clipboard was never called with 0 (or not called at all)
        self.assertNotEqual(self.backend.last_owner_passed, 0)
        
        # Verify worker thread is not alive / running
        self.assertFalse(q.is_running())

    # 35. Transition to STOPPED automatically when worker finishes (after stop timeout)
    def test_queue_state_retains_stopping_until_worker_end(self) -> None:
        q = self._create_queue()
        q.start()
        
        reached_active = threading.Event()
        blocker = threading.Event()
        
        original_fw = self.backend.get_foreground_window
        def blocked_fw() -> int:
            reached_active.set()
            blocker.wait()
            return original_fw()
        self.backend.get_foreground_window = blocked_fw

        e = self.history.add_entry("sess_1", 1, "Job")
        q.enqueue(e)
        
        # Wait until job reaches blocked state
        self.assertTrue(reached_active.wait(timeout=2.0))
        
        # stop() with short timeout -> returns before thread ends
        q.stop(timeout=0.01)
        
        # State must be STOPPING, thread must be alive
        self.assertEqual(q._state, QueueState.STOPPING)
        self.assertTrue(q._worker_thread.is_alive())
        
        # Release blocker
        blocker.set()
        
        # Wait for thread to actually finish
        q._worker_thread.join(timeout=2.0)
        
        # State must now be STOPPED automatically, and thread not alive
        self.assertEqual(q._state, QueueState.STOPPED)
        self.assertFalse(q._worker_thread.is_alive())

    # 36. Parallel start() calls during INITIALIZING
    def test_parallel_start_calls_single_worker(self) -> None:
        q = self._create_queue()
        
        reached_init = threading.Event()
        block_init = threading.Event()

        original_create = self.backend.create_owner_window
        def blocking_create() -> None:
            reached_init.set()
            block_init.wait()
            original_create()
        self.backend.create_owner_window = blocking_create

        results = []
        errors = []

        def call_start():
            try:
                q.start()
                results.append(True)
            except Exception as e:
                errors.append(e)

        t1 = threading.Thread(target=call_start)
        t2 = threading.Thread(target=call_start)

        t1.start()
        self.assertTrue(reached_init.wait(timeout=2.0))
        
        t2.start()
        block_init.set()

        t1.join(timeout=2.0)
        t2.join(timeout=2.0)

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 2)
        self.assertEqual(q._state, QueueState.RUNNING)
        self.assertEqual(len([name for name, _ in self.backend.event_log if name == "create_owner_window"]), 1)
        self.assertFalse(t1.is_alive())
        self.assertFalse(t2.is_alive())
        
        q.stop()

    # 37. Parallel start() calls on initialization failure
    def test_parallel_start_calls_init_failure(self) -> None:
        self.backend.exception_on_create_owner = True
        q = self._create_queue()

        reached_init = threading.Event()
        block_init = threading.Event()

        create_calls = [0]
        original_create = self.backend.create_owner_window
        def blocking_failing_create() -> None:
            create_calls[0] += 1
            reached_init.set()
            block_init.wait()
            original_create()
        self.backend.create_owner_window = blocking_failing_create

        errors_t1 = []
        errors_t2 = []

        def call_start(err_list):
            try:
                q.start()
            except Exception as e:
                err_list.append(e)

        t1 = threading.Thread(target=call_start, args=(errors_t1,))
        t2 = threading.Thread(target=call_start, args=(errors_t2,))

        t1.start()
        self.assertTrue(reached_init.wait(timeout=2.0))

        t2.start()
        block_init.set()

        t1.join(timeout=2.0)
        t2.join(timeout=2.0)

        self.assertFalse(t1.is_alive())
        self.assertFalse(t2.is_alive())
        self.assertEqual(len(errors_t1), 1)
        self.assertEqual(len(errors_t2), 1)
        self.assertIsInstance(errors_t1[0], RuntimeError)
        self.assertIsInstance(errors_t2[0], RuntimeError)
        self.assertEqual(q._state, QueueState.STOPPED)
        self.assertFalse(q.is_running())
        self.assertEqual(create_calls[0], 1)

    # 38. create_owner_window() returns 0 without exception
    def test_init_owner_window_zero_fails(self) -> None:
        self.backend.owner_window = 0
        q = self._create_queue()

        with self.assertRaises(OSError):
            q.start()

        self.assertEqual(q._state, QueueState.STOPPED)
        e = self.history.add_entry("sess_1", 1, "test")
        self.assertFalse(q.enqueue(e))
        self.assertNotEqual(self.backend.last_owner_passed, 0)
        self.assertFalse(q.is_running())

    # 39. stop() during INITIALIZING
    def test_stop_during_initializing(self) -> None:
        q = self._create_queue()
        
        reached_init = threading.Event()
        block_init = threading.Event()

        original_create = self.backend.create_owner_window
        def blocking_create() -> None:
            reached_init.set()
            block_init.wait()
            original_create()
        self.backend.create_owner_window = blocking_create

        start_errors = []
        def call_start():
            try:
                q.start()
            except Exception as e:
                start_errors.append(e)

        t_start = threading.Thread(target=call_start)
        t_start.start()

        self.assertTrue(reached_init.wait(timeout=2.0))

        t_stop = threading.Thread(target=q.stop)
        t_stop.start()

        for _ in range(50):
            if q._state == QueueState.STOPPING:
                break
            time.sleep(0.01)

        self.assertEqual(q._state, QueueState.STOPPING)
        self.assertTrue(t_stop.is_alive())

        block_init.set()

        t_start.join(timeout=2.0)
        t_stop.join(timeout=2.0)

        self.assertFalse(t_start.is_alive())
        self.assertFalse(t_stop.is_alive())
        self.assertEqual(len(start_errors), 1)
        self.assertEqual(q._state, QueueState.STOPPED)
        e = self.history.add_entry("sess_1", 1, "test")
        self.assertFalse(q.enqueue(e))
        self.assertFalse(q.is_running())
        self.assertEqual(self.backend.open_calls, 0)

    # 40. Sequential start() idempotency
    def test_sequential_start_idempotent(self) -> None:
        q = self._create_queue()
        q.start()
        q.start()
        self.assertEqual(q._state, QueueState.RUNNING)
        self.assertEqual(len([name for name, _ in self.backend.event_log if name == "create_owner_window"]), 1)
        q.stop()

    # 41. Deterministic test for start() waiting until init cleanup completes
    def test_start_waits_for_init_cleanup_completion(self) -> None:
        self.backend.exception_on_create_owner = True
        q = self._create_queue()

        cleanup_started = threading.Event()
        cleanup_release = threading.Event()

        original_destroy = self.backend.destroy_owner_window
        def blocking_destroy() -> None:
            cleanup_started.set()
            cleanup_release.wait()
            original_destroy()
        self.backend.destroy_owner_window = blocking_destroy

        start_errors = []
        def call_start():
            try:
                q.start()
            except Exception as e:
                start_errors.append(e)

        t_start = threading.Thread(target=call_start)
        t_start.start()

        # Wait until destroy_owner_window has been reached and is blocked
        self.assertTrue(cleanup_started.wait(timeout=2.0))

        # At this point, destroy_owner_window is currently executing in worker thread.
        # start() MUST NOT have returned/raised yet!
        self.assertTrue(t_start.is_alive())
        self.assertTrue(q._worker_thread.is_alive())

        # Release cleanup
        cleanup_release.set()

        t_start.join(timeout=2.0)

        self.assertFalse(t_start.is_alive())
        self.assertFalse(q._worker_thread.is_alive())
        self.assertEqual(len(start_errors), 1)
        self.assertIsInstance(start_errors[0], RuntimeError)
        self.assertEqual(q._state, QueueState.STOPPED)
        e = self.history.add_entry("sess_1", 1, "test")
        self.assertFalse(q.enqueue(e))
        self.assertEqual(self.backend.open_calls, 0)


if __name__ == "__main__":
    unittest.main()
