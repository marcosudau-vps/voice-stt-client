import os
import shutil
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

from core.config import HistoryConfig, HistoryMemoryConfig, HistoryPersistentConfig, AppConfig
from core.history import TranscriptHistoryManager, HistoryEntry, InjectionAttempt, InjectionStatus


class TestTranscriptHistoryManager(unittest.TestCase):
    def setUp(self):
        # Create a temp directory for DB testing
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_history.db")
        # Mock LOCALAPPDATA to prevent writing to user's real app data
        self.original_localappdata = os.environ.get("LOCALAPPDATA")
        os.environ["LOCALAPPDATA"] = os.path.join(self.temp_dir, "mock_localappdata")

    def tearDown(self):
        # Clean up temp files
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
        if self.original_localappdata is not None:
            os.environ["LOCALAPPDATA"] = self.original_localappdata
        elif "LOCALAPPDATA" in os.environ:
            del os.environ["LOCALAPPDATA"]

    def test_disabled_history(self):
        # When history is disabled, it should do nothing and return None
        config = HistoryConfig(enabled=False)
        manager = TranscriptHistoryManager(config, db_path=self.db_path)

        entry = manager.add_entry("sess_1", 1, "hello world")
        self.assertIsNone(entry)
        self.assertEqual(len(manager.get_memory_entries()), 0)
        self.assertEqual(len(manager.get_persistent_entries()), 0)

        attempt = manager.record_injection_attempt("some_id", "command_sent")
        self.assertIsNone(attempt)

        res_disabled = manager.add_entry_with_status("sess_1", 1, "hello world")
        self.assertIsNone(res_disabled.entry)
        self.assertEqual(res_disabled.status.value, "unavailable")

    def test_add_entry_with_status_new_and_already_exists(self):
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(enabled=False),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)

        res1 = manager.add_entry_with_status("sess_1", 10, "First text")
        self.assertIsNotNone(res1.entry)
        self.assertEqual(res1.status.value, "new")
        self.assertEqual(res1.entry.text, "First text")

        res2 = manager.add_entry_with_status("sess_1", 10, "Second text")
        self.assertIsNotNone(res2.entry)
        self.assertEqual(res2.status.value, "already_exists")
        self.assertEqual(res2.entry.id, res1.entry.id)

    def test_add_entry_in_memory(self):
        # Check basic in-memory entry insertion
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(enabled=False),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)

        entry = manager.add_entry("sess_1", 1, "hello world")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.session_id, "sess_1")
        self.assertEqual(entry.segment_id, 1)
        self.assertEqual(entry.text, "hello world")
        self.assertEqual(entry.text_length, 11)

        mem_entries = manager.get_memory_entries()
        self.assertEqual(len(mem_entries), 1)
        self.assertEqual(mem_entries[0].id, entry.id)

    def test_in_memory_limit(self):
        # Verify in-memory list respects max_entries
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=3),
            persistent=HistoryPersistentConfig(enabled=False),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)

        for i in range(5):
            manager.add_entry("sess_1", i, f"text {i}")

        mem_entries = manager.get_memory_entries()
        self.assertEqual(len(mem_entries), 3)
        self.assertEqual(mem_entries[0].text, "text 2")
        self.assertEqual(mem_entries[1].text, "text 3")
        self.assertEqual(mem_entries[2].text, "text 4")

    def test_unlimited_in_memory(self):
        # Verify max_entries=0 means unlimited
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=0),
            persistent=HistoryPersistentConfig(enabled=False),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)

        for i in range(10):
            manager.add_entry("sess_1", i, f"text {i}")

        mem_entries = manager.get_memory_entries()
        self.assertEqual(len(mem_entries), 10)

    def test_deduplication(self):
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(enabled=True, store_all=True),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)

        # 1. Add normal entry
        entry1 = manager.add_entry("sess_1", 1, "hello")
        self.assertIsNotNone(entry1)

        # 2. Add duplicate (same session, same segment)
        entry2 = manager.add_entry("sess_1", 1, "hello duplicate")
        # Deduplication should return the original entry
        self.assertEqual(entry1.id, entry2.id)
        self.assertEqual(entry2.text, "hello")

        # 3. Add different segment, same session
        entry3 = manager.add_entry("sess_1", 2, "world")
        self.assertNotEqual(entry1.id, entry3.id)

        # 4. Add same segment ID, different session
        entry4 = manager.add_entry("sess_2", 1, "different session")
        self.assertNotEqual(entry1.id, entry4.id)

        # Verify database uniqueness constraint works and doesn't crash on SQL insert
        # Even if we try to force-insert in DB via internal methods, uniqueness is protected
        self.assertEqual(len(manager.get_persistent_entries()), 3)

    def test_persistent_min_characters(self):
        # Only persist entries with len(text) >= min_characters unless store_all is True
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(
                enabled=True, store_all=False, min_characters=10
            ),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)

        # Short text (length 5) -> should NOT persist
        entry_short = manager.add_entry("sess_1", 1, "short")
        # Long text (length 11) -> should persist
        entry_long = manager.add_entry("sess_1", 2, "longer text")

        # In-memory has both
        self.assertEqual(len(manager.get_memory_entries()), 2)
        # Database only has long text
        db_entries = manager.get_persistent_entries()
        self.assertEqual(len(db_entries), 1)
        self.assertEqual(db_entries[0].id, entry_long.id)

    def test_persistent_limit(self):
        # Database should respect max_entries limit
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=10),
            persistent=HistoryPersistentConfig(
                enabled=True, store_all=True, max_entries=3
            ),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)

        for i in range(5):
            manager.add_entry("sess_1", i, f"text {i}")
            # Ensure different timestamps so sorting is reliable
            time.sleep(0.01)

        db_entries = manager.get_persistent_entries()
        self.assertEqual(len(db_entries), 3)
        # Verify oldest was cleaned up, leaving latest 3 sorted chronologically
        self.assertEqual(db_entries[0].text, "text 2")
        self.assertEqual(db_entries[1].text, "text 3")
        self.assertEqual(db_entries[2].text, "text 4")

    def test_persistent_unlimited_and_no_retention(self):
        # max_entries=0 and retention_days=0 should not delete anything
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=20),
            persistent=HistoryPersistentConfig(
                enabled=True, store_all=True, max_entries=0, retention_days=0
            ),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)

        for i in range(10):
            manager.add_entry("sess_1", i, f"text {i}")

        db_entries = manager.get_persistent_entries()
        self.assertEqual(len(db_entries), 10)

    def test_age_based_cleanup(self):
        # retention_days > 0 should clean up entries older than cutoff
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=10),
            persistent=HistoryPersistentConfig(
                enabled=True, store_all=True, max_entries=0, retention_days=1
            ),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)

        # Insert old entry (mocking 2 days ago)
        old_time = time.time() - (2 * 86400)
        manager.add_entry("sess_1", 1, "old entry", timestamp=old_time)

        # Insert new entry
        manager.add_entry("sess_1", 2, "new entry")

        db_entries = manager.get_persistent_entries()
        # Old entry should be deleted, leaving only the new one
        self.assertEqual(len(db_entries), 1)
        self.assertEqual(db_entries[0].text, "new entry")

    def test_reloading_on_restart(self):
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=3),
            persistent=HistoryPersistentConfig(enabled=True, store_all=True),
        )
        manager1 = TranscriptHistoryManager(config, db_path=self.db_path)
        manager1.add_entry("sess_1", 1, "first text")
        time.sleep(0.01)
        manager1.add_entry("sess_1", 2, "second text")
        time.sleep(0.01)
        manager1.add_entry("sess_1", 3, "third text")
        time.sleep(0.01)
        manager1.add_entry("sess_1", 4, "fourth text")

        # Start a new manager on the same DB path.
        # It should load the latest 3 entries from the DB into memory, sorted chronologically.
        manager2 = TranscriptHistoryManager(config, db_path=self.db_path)
        mem_entries = manager2.get_memory_entries()

        self.assertEqual(len(mem_entries), 3)
        self.assertEqual(mem_entries[0].text, "second text")
        self.assertEqual(mem_entries[1].text, "third text")
        self.assertEqual(mem_entries[2].text, "fourth text")

    def test_record_injection_attempts(self):
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(enabled=True, store_all=True),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)

        entry = manager.add_entry("sess_1", 1, "hello")
        self.assertIsNotNone(entry)

        # Record first attempt
        att1 = manager.record_injection_attempt(entry.id, "command_sent")
        self.assertIsNotNone(att1)
        self.assertEqual(att1.status, "command_sent")
        self.assertIsNone(att1.error)

        # Record second attempt
        time.sleep(0.01)
        att2 = manager.record_injection_attempt(entry.id, "failed", error="Clipboard locked")
        self.assertIsNotNone(att2)
        self.assertEqual(att2.status, "failed")
        self.assertEqual(att2.error, "Clipboard locked")

        # Check in memory representation
        mem_entries = manager.get_memory_entries()
        self.assertEqual(len(mem_entries[0].attempts), 2)
        self.assertEqual(mem_entries[0].attempts[0].status, "command_sent")
        self.assertEqual(mem_entries[0].attempts[1].status, "failed")

        # Check DB representation
        db_entries = manager.get_persistent_entries()
        self.assertEqual(len(db_entries[0].attempts), 2)
        self.assertEqual(db_entries[0].attempts[0].status, "command_sent")
        self.assertEqual(db_entries[0].attempts[1].status, "failed")
        self.assertEqual(db_entries[0].attempts[1].error, "Clipboard locked")

    def test_failed_injection_triggers_persistence(self):
        # Entry text is short (5 chars), which is below min_characters (10).
        # It should not persist initially. But when a failed injection attempt is recorded,
        # it should trigger persistence.
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(
                enabled=True, store_all=False, min_characters=10, store_failed_injections=True
            ),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)

        entry = manager.add_entry("sess_1", 1, "short")
        self.assertIsNotNone(entry)
        self.assertEqual(len(manager.get_persistent_entries()), 0)  # Not persisted initially

        # Record a failed attempt
        manager.record_injection_attempt(entry.id, "failed", error="timeout")

        # Now it must be persisted!
        db_entries = manager.get_persistent_entries()
        self.assertEqual(len(db_entries), 1)
        self.assertEqual(db_entries[0].text, "short")
        self.assertEqual(len(db_entries[0].attempts), 1)
        self.assertEqual(db_entries[0].attempts[0].status, "failed")

    def test_database_error_handling(self):
        # We test robustness in case SQLite encounters errors.
        # Pass an invalid database path that cannot be created because its parent is a regular file.
        parent_file_path = os.path.join(self.temp_dir, "parent_is_a_file")
        with open(parent_file_path, "w", encoding="utf-8") as f:
            f.write("I am a file, not a directory")
            
        invalid_db_path = os.path.join(parent_file_path, "history.db")

        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(enabled=True, store_all=True),
        )
        # Initializing with invalid path should fallback to in-memory mode and NOT crash.
        manager = TranscriptHistoryManager(config, db_path=invalid_db_path)

        self.assertFalse(manager._db_enabled)

        # Manager should still work in-memory
        entry = manager.add_entry("sess_1", 1, "hello")
        self.assertIsNotNone(entry)
        self.assertEqual(len(manager.get_memory_entries()), 1)
        self.assertEqual(len(manager.get_persistent_entries()), 0)

        # Record attempts should also not crash
        att = manager.record_injection_attempt(entry.id, "command_sent")
        self.assertIsNotNone(att)
        self.assertEqual(len(manager.get_memory_entries()[0].attempts), 1)

    def test_get_entries_chronological_ordering(self):
        # Check that get_memory_entries() and get_persistent_entries() return oldest first, newest last.
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=10),
            persistent=HistoryPersistentConfig(enabled=True, store_all=True),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)

        manager.add_entry("sess_1", 1, "oldest", timestamp=100.0)
        manager.add_entry("sess_1", 2, "middle", timestamp=200.0)
        manager.add_entry("sess_1", 3, "newest", timestamp=300.0)

        # Memory order
        mem = manager.get_memory_entries()
        self.assertEqual(mem[0].text, "oldest")
        self.assertEqual(mem[1].text, "middle")
        self.assertEqual(mem[2].text, "newest")

        # Persistent order
        db_entries = manager.get_persistent_entries()
        self.assertEqual(db_entries[0].text, "oldest")
        self.assertEqual(db_entries[1].text, "middle")
        self.assertEqual(db_entries[2].text, "newest")

    def test_default_db_path_outside_repo(self):
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(enabled=True),
        )
        # Using constructor default (db_path=None)
        manager = TranscriptHistoryManager(config)
        resolved_path = manager.db_path

        # Verify it resolves outside current repository directory
        repo_dir = Path(__file__).resolve().parent.parent
        resolved_path_abs = resolved_path.resolve()

        # Check that the DB path is not inside the repo_dir
        self.assertFalse(resolved_path_abs.is_relative_to(repo_dir))

    def test_deduplication_after_in_memory_rotation(self):
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=2),
            persistent=HistoryPersistentConfig(
                enabled=True, store_all=False, min_characters=20, store_failed_injections=False
            ),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)
        
        # 1. Add short entry (length 5) -> not persisted, only in memory
        entry1 = manager.add_entry("sess_1", 1, "short")
        self.assertIsNotNone(entry1)
        
        # 2. Add two other entries to push entry1 out of the memory list (max_entries=2)
        manager.add_entry("sess_1", 2, "another short")
        manager.add_entry("sess_1", 3, "yet another short")
        
        # Verify entry1 is no longer in memory recent history
        self.assertNotIn(entry1.id, [e.id for e in manager.get_memory_entries()])
        # Verify entry1 is not in SQLite either
        self.assertEqual(len(manager.get_persistent_entries()), 0)
        
        # 3. Receive the same session/segment again.
        # Since it is in process deduplication cache but not in memory or DB,
        # it should return None and not create a new entry.
        duplicate_entry = manager.add_entry("sess_1", 1, "short duplicate")
        self.assertIsNone(duplicate_entry)

    def test_atomic_joint_persistence(self):
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(
                enabled=True, store_all=False, min_characters=20, max_entries=2, store_failed_injections=True
            ),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)
        
        # Add short entry -> not persisted initially
        entry = manager.add_entry("sess_1", 1, "short text")
        self.assertEqual(len(manager.get_persistent_entries()), 0)
        
        # Record a failed injection attempt
        # This triggers atomic joint transaction saving both parent and child
        attempt = manager.record_injection_attempt(entry.id, "failed", error="some error")
        self.assertIsNotNone(attempt)
        
        # Verify both are stored in DB
        db_entries = manager.get_persistent_entries()
        self.assertEqual(len(db_entries), 1)
        self.assertEqual(db_entries[0].id, entry.id)
        self.assertEqual(len(db_entries[0].attempts), 1)
        self.assertEqual(db_entries[0].attempts[0].id, attempt.id)

    def test_stable_id_on_conflict(self):
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(enabled=True, store_all=True),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)
        
        # Save a segment
        entry = manager.add_entry("sess_1", 1, "original text")
        self.assertIsNotNone(entry)
        original_id = entry.id
        
        # Record attempt on it
        attempt = manager.record_injection_attempt(original_id, "failed")
        self.assertIsNotNone(attempt)
        
        # Force a database save with a DIFFERENT entry having the same session/segment
        # but a new UUID to simulate a conflict
        conflict_entry = HistoryEntry(
            id="new_uuid_different_id",
            session_id="sess_1",
            segment_id=1,
            timestamp=time.time(),
            text="duplicate text",
            text_length=14,
            attempts=[]
        )
        
        # Calling _save_to_db with conflict_entry should NOT change the database row's ID
        # and should update conflict_entry.id with the stable original_id
        manager._save_to_db(conflict_entry)
        self.assertEqual(conflict_entry.id, original_id)
        
        # Verify ID and attempts in database remain unchanged
        db_entries = manager.get_persistent_entries()
        self.assertEqual(len(db_entries), 1)
        self.assertEqual(db_entries[0].id, original_id)
        self.assertEqual(len(db_entries[0].attempts), 1)
        self.assertEqual(db_entries[0].attempts[0].id, attempt.id)

    def test_db_lookup_does_not_modify_memory(self):
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=2),
            persistent=HistoryPersistentConfig(enabled=True, store_all=True),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)
        
        # 1. Add entry 1 (persisted because store_all=True)
        entry1 = manager.add_entry("sess_1", 1, "entry 1")
        time.sleep(0.01)
        
        # 2. Add entry 2 and 3 to push entry 1 out of memory recent-history (max_entries=2)
        entry2 = manager.add_entry("sess_1", 2, "entry 2")
        time.sleep(0.01)
        entry3 = manager.add_entry("sess_1", 3, "entry 3")
        
        # Confirm entry1 is rotated out of memory but exists in persistent
        self.assertNotIn(entry1.id, [e.id for e in manager.get_memory_entries()])
        self.assertIn(entry1.id, [e.id for e in manager.get_persistent_entries()])
        
        # 3. Perform a lookup / record attempt for entry1 (which is in DB only)
        manager.record_injection_attempt(entry1.id, "command_sent")
        
        # Verify entry1 was NOT appended to memory entries
        mem_ids = [e.id for e in manager.get_memory_entries()]
        self.assertNotIn(entry1.id, mem_ids)
        self.assertEqual(len(mem_ids), 2)

    def test_status_validation(self):
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(enabled=False),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)
        entry = manager.add_entry("sess_1", 1, "hello")
        
        # Allowed status values should work
        for allowed in ["pending", "command_sent", "failed", "skipped"]:
            attempt = manager.record_injection_attempt(entry.id, allowed)
            self.assertIsNotNone(attempt)
            self.assertEqual(attempt.status, allowed)
            
        # Unknown status should raise ValueError and NOT be saved
        with self.assertRaises(ValueError):
            manager.record_injection_attempt(entry.id, "unknown_status")

    def test_db_error_after_init(self):
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(enabled=True, store_all=True),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)
        self.assertTrue(manager._db_enabled)
        
        # Mock _get_connection to raise sqlite3.OperationalError
        def faulty_connection():
            raise sqlite3.OperationalError("Database connection lost")
        manager._get_connection = faulty_connection
        
        # Component must still function in memory
        entry = manager.add_entry("sess_1", 1, "hello error")
        self.assertIsNotNone(entry)
        self.assertEqual(len(manager.get_memory_entries()), 1)
        
        att = manager.record_injection_attempt(entry.id, "failed")
        self.assertIsNotNone(att)
        self.assertEqual(len(manager.get_memory_entries()[0].attempts), 1)

    def test_locked_write_operation(self):
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(enabled=True, store_all=True),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)
        
        original_get_conn = manager._get_connection
        class LockedConnection:
            def __init__(self, real_conn):
                self._real_conn = real_conn
            def __getattr__(self, name):
                return getattr(self._real_conn, name)
            def execute(self, *args, **kwargs):
                if any(x in args[0].lower() for x in ("insert", "update", "delete")):
                    raise sqlite3.OperationalError("database is locked")
                return self._real_conn.execute(*args, **kwargs)
            def cursor(self, *args, **kwargs):
                return self._real_conn.cursor(*args, **kwargs)
            def __enter__(self):
                self._real_conn.__enter__()
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                return self._real_conn.__exit__(exc_type, exc_val, exc_tb)
                
        def locked_conn():
            return LockedConnection(original_get_conn())
            
        manager._get_connection = locked_conn
        
        # Component should not crash, functions in memory
        entry = manager.add_entry("sess_1", 1, "hello locked")
        self.assertIsNotNone(entry)
        self.assertEqual(len(manager.get_memory_entries()), 1)

    def test_corrupted_db_file_at_start(self):
        # Write garbage to the DB path
        with open(self.db_path, "w", encoding="utf-8") as f:
            f.write("CONCORDE_CORRUPT_SQLITE_GARBAGE")
            
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(enabled=True, store_all=True),
        )
        # Initialization should fail gracefully and fall back to in-memory
        manager = TranscriptHistoryManager(config, db_path=self.db_path)
        self.assertFalse(manager._db_enabled)
        
        # Component must work in memory
        entry = manager.add_entry("sess_1", 1, "hello corrupt")
        self.assertIsNotNone(entry)
        self.assertEqual(len(manager.get_memory_entries()), 1)

    def test_defensive_copies(self):
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(enabled=False),
        )
        manager = TranscriptHistoryManager(config, db_path=self.db_path)
        
        entry = manager.add_entry("sess_1", 1, "original text")
        manager.record_injection_attempt(entry.id, "pending")
        
        mem_entries = manager.get_memory_entries()
        self.assertEqual(len(mem_entries), 1)
        
        # Modify the returned objects
        mem_entries[0].text = "mutated text"
        mem_entries[0].attempts[0].status = "failed"
        
        # Check that the internal state remains unchanged
        mem_entries_second = manager.get_memory_entries()
        self.assertEqual(mem_entries_second[0].text, "original text")
        self.assertEqual(mem_entries_second[0].attempts[0].status, "pending")
    def test_database_connections_are_closed(self):
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=5),
            persistent=HistoryPersistentConfig(enabled=True, store_all=True),
        )
        # We will mock sqlite3.connect to track connection creation and closing
        original_connect = sqlite3.connect
        connections = []
        
        class SpyConnection:
            def __init__(self, real_conn, tracker):
                self._real_conn = real_conn
                self._tracker = tracker
            def __getattr__(self, name):
                return getattr(self._real_conn, name)
            def close(self):
                self._tracker["closed"] = True
                return self._real_conn.close()
            def __enter__(self):
                self._real_conn.__enter__()
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                return self._real_conn.__exit__(exc_type, exc_val, exc_tb)

        def spy_connect(*args, **kwargs):
            conn = original_connect(*args, **kwargs)
            closed_tracker = {"closed": False}
            spy_conn = SpyConnection(conn, closed_tracker)
            connections.append((spy_conn, closed_tracker))
            return spy_conn
            
        import unittest.mock
        with unittest.mock.patch("sqlite3.connect", side_effect=spy_connect):
            manager = TranscriptHistoryManager(config, db_path=self.db_path)
            # Add an entry (which should trigger a write and save to DB)
            manager.add_entry("sess_1", 1, "hello")
            
        # Verify that all connections that were opened have been closed
        self.assertGreater(len(connections), 0)
        for conn, tracker in connections:
            self.assertTrue(tracker["closed"], "SQLite connection was not closed!")

    def test_database_path_priorities(self):
        # Setup mock LOCALAPPDATA
        mock_localappdata = os.path.join(self.temp_dir, "mock_localappdata")
        
        # Priority 1: Constructor parameter
        config_p1 = HistoryConfig(
            enabled=True,
            persistent=HistoryPersistentConfig(enabled=True, db_path="config_path.db")
        )
        manager_p1 = TranscriptHistoryManager(config_p1, db_path="param_path.db")
        self.assertEqual(manager_p1.db_path, Path("param_path.db").resolve())
        
        # Priority 2: Config value
        config_p2 = HistoryConfig(
            enabled=True,
            persistent=HistoryPersistentConfig(enabled=True, db_path="config_path.db")
        )
        manager_p2 = TranscriptHistoryManager(config_p2)
        self.assertEqual(manager_p2.db_path, Path("config_path.db").resolve())
        
        # Priority 3: Default path
        config_p3 = HistoryConfig(
            enabled=True,
            persistent=HistoryPersistentConfig(enabled=True, db_path=None)
        )
        manager_p3 = TranscriptHistoryManager(config_p3)
        expected_default = Path(mock_localappdata) / "RealtimeSTT_Client" / "transcript_history.db"
        self.assertEqual(manager_p3.db_path.resolve(), expected_default.resolve())


class TestHistoryConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.yaml"

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass

    def test_nested_deserialization_and_defaults(self):
        raw_data = {
            "history": {
                "enabled": True,
                "memory": {
                    "max_entries": 10
                },
                "persistent": {
                    "enabled": True,
                    "max_entries": 250,
                    "retention_days": 14,
                    "min_characters": 500,
                    "store_failed_injections": False,
                    "store_all": True,
                    "db_path": "/tmp/custom.db"
                }
            }
        }
        config = AppConfig._from_dict(raw_data)
        
        self.assertIsInstance(config.history, HistoryConfig)
        self.assertIsInstance(config.history.memory, HistoryMemoryConfig)
        self.assertIsInstance(config.history.persistent, HistoryPersistentConfig)
        
        self.assertTrue(config.history.enabled)
        self.assertEqual(config.history.memory.max_entries, 10)
        self.assertTrue(config.history.persistent.enabled)
        self.assertEqual(config.history.persistent.max_entries, 250)
        self.assertEqual(config.history.persistent.retention_days, 14)
        self.assertEqual(config.history.persistent.min_characters, 500)
        self.assertFalse(config.history.persistent.store_failed_injections)
        self.assertTrue(config.history.persistent.store_all)
        self.assertEqual(config.history.persistent.db_path, "/tmp/custom.db")

    def test_save_and_load_roundtrip(self):
        original_config = AppConfig()
        original_config.history.enabled = False
        original_config.history.memory.max_entries = 99
        original_config.history.persistent.enabled = True
        original_config.history.persistent.max_entries = 999
        original_config.history.persistent.retention_days = 9
        original_config.history.persistent.min_characters = 9999
        original_config.history.persistent.store_failed_injections = False
        original_config.history.persistent.store_all = True
        original_config.history.persistent.db_path = "some_test_path.db"
        
        original_config.save(self.config_path)
        loaded_config = AppConfig.load(self.config_path)
        
        self.assertIsInstance(loaded_config.history, HistoryConfig)
        self.assertIsInstance(loaded_config.history.memory, HistoryMemoryConfig)
        self.assertIsInstance(loaded_config.history.persistent, HistoryPersistentConfig)
        
        self.assertEqual(loaded_config.history.enabled, original_config.history.enabled)
        self.assertEqual(loaded_config.history.memory.max_entries, original_config.history.memory.max_entries)
        self.assertEqual(loaded_config.history.persistent.enabled, original_config.history.persistent.enabled)
        self.assertEqual(loaded_config.history.persistent.max_entries, original_config.history.persistent.max_entries)
        self.assertEqual(loaded_config.history.persistent.retention_days, original_config.history.persistent.retention_days)
        self.assertEqual(loaded_config.history.persistent.min_characters, original_config.history.persistent.min_characters)
        self.assertEqual(loaded_config.history.persistent.store_failed_injections, original_config.history.persistent.store_failed_injections)
        self.assertEqual(loaded_config.history.persistent.store_all, original_config.history.persistent.store_all)
        self.assertEqual(loaded_config.history.persistent.db_path, original_config.history.persistent.db_path)
    def test_default_values_correctness(self):
        config_default = AppConfig()
        self.assertEqual(config_default.history.memory.max_entries, 5)


if __name__ == "__main__":
    unittest.main()
