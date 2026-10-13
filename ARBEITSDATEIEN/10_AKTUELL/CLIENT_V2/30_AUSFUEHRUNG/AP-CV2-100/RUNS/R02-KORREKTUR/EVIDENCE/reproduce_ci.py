"""Baseline and deterministic reproduction of the CI replay deadline failure."""
from pathlib import Path
import subprocess
import sys

EV = Path(__file__).resolve().parent
ROOT = EV.parents[7]
target = 'tests.test_event_stream.TestEventStreamTransport.test_cursor_write_failure_replays_without_duplicate_visible_impulse'
script = '''
import time
import unittest
from unittest.mock import patch
from voice_stt_client.core.event_cursor_store import EventCursorStore
original = EventCursorStore.commit
def slow_commit(self, *args, **kwargs):
    time.sleep(0.28)
    return original(self, *args, **kwargs)
with patch.object(EventCursorStore, 'commit', slow_commit):
    suite = unittest.defaultTestLoader.loadTestsFromName(%r)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful())
''' % target
for name, args, expected in [
    ('baseline-event-stream.txt', ['-m', 'unittest', 'tests.test_event_stream', '-v'], 0),
    ('replay-deadline-repro.txt', ['-c', script], 1),
]:
    command = [sys.executable, *args]
    run = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', timeout=60)
    (EV / name).write_text('Command: ' + repr(command) + '\nExit: ' + str(run.returncode) + '\n' + run.stdout.replace('\r\n', '\n'), encoding='utf-8', newline='\n')
    print(name, run.returncode, flush=True)
    assert run.returncode == expected
