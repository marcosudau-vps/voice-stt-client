"""
Manual smoke test for TextInjectionQueue.
This script performs real OS clipboard modification and keystroke emulation.
Must be run manually; ignored by automatic unittest discovery.
"""

import sys
import time

from core.config import AppConfig, HistoryConfig, HistoryMemoryConfig, HistoryPersistentConfig
from core.history import TranscriptHistoryManager
from core.text_injector import TextInjectionQueue, CtypesWindowsInjectionBackend

def main() -> None:
    if sys.platform != "win32":
        print("This manual test is only supported on Windows.")
        return

    print("=" * 60)
    print("  MANUAL SMOKE TEST: Text Injection Queue")
    print("=" * 60)
    print()
    print("WARNING: This test modifies your clipboard and emulates keystrokes.")
    print("Please follow these steps:")
    print("1. Open an editor like Notepad.")
    print("2. Confirm you want to proceed by typing 'y'.")
    print("3. You will have 5 seconds to switch focus to the Notepad editor.")
    print("4. The test will paste 'Hello from RealtimeSTT!' at the text cursor,")
    print("   and then restore your previous clipboard content.")
    print()

    choice = input("Do you want to proceed? [y/N]: ").strip().lower()
    if choice != "y":
        print("Manual test aborted.")
        return

    print()
    for i in range(5, 0, -1):
        print(f"Starting in {i} seconds... (Focus your editor now!)")
        time.sleep(1)

    print("\nRunning test...")

    # Configure with clipboard restoration enabled
    config = AppConfig()
    config.clipboard.restore_previous = True
    config.text_injection.paste_delay_ms = 100
    config.clipboard.restore_delay_ms = 300

    import tempfile
    import os
    import shutil

    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "manual_test.db")
    history_cfg = HistoryConfig(
        enabled=True,
        memory=HistoryMemoryConfig(max_entries=5),
        persistent=HistoryPersistentConfig(enabled=True, store_all=True)
    )
    history = TranscriptHistoryManager(history_cfg, db_path=db_path)

    backend = CtypesWindowsInjectionBackend()
    queue_mgr = TextInjectionQueue(config, history, backend)

    queue_mgr.start()

    # Create and enqueue a segment
    entry = history.add_entry("manual_sess", 1, "Hello from RealtimeSTT!")
    queue_mgr.enqueue(entry)

    # Call stop() which blocks until the worker thread has completely finished processing the job.
    print("Stopping queue (waiting for worker to finish)...")
    queue_mgr.stop()
    print("Queue stopped successfully.")

    # Read the history attempt results
    entries = history.get_persistent_entries()
    attempts = entries[0].attempts if entries else []
    status = attempts[0].status if attempts else None
    error = attempts[0].error if attempts else None

    print()
    print("Attempt results in database:")
    print(f"  Status: {status}")
    print(f"  Error:  {error}")
    print()

    if status == "command_sent":
        print("✓ The paste command was successfully sent.")
    else:
        print("❌ [WARNING] The paste command was NOT successfully sent to the application!")

    # Clean up the database only after the worker thread has finished and we read the results
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Warning: could not delete temporary directory {temp_dir}: {e}")

    print()
    print("Test completed.")
    print("Please check:")
    print("1. Did 'Hello from RealtimeSTT!' appear in the editor?")
    print("2. Is your previous clipboard content still present (try pasting manually)?")
    print("=" * 60)

if __name__ == "__main__":
    main()
