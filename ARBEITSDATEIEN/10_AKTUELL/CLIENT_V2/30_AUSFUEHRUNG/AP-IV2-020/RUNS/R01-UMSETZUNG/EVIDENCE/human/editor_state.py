"""Bounded reads of the owned editor's atomically replaced diagnostic file.

This retries metadata reads only, never a Clipboard write or SendInput attempt.
Keep the caller's logical Windows path for I/O; resolve only for containment.
"""
import json
from pathlib import Path
import time


def owned_editor_path(path, local):
    logical = Path(path).absolute()
    if not logical.resolve().is_relative_to((Path(local)/'editors').resolve()):
        raise ValueError('Only the owned diagnostic editor state is allowed')
    return logical


def read_editor_state(path, timeout=2):
    deadline = time.monotonic()+timeout
    while True:
        try:
            return json.loads(path.read_text(encoding='utf8'))
        except (PermissionError, FileNotFoundError, json.JSONDecodeError) as error:
            # Windows can briefly deny a new open during replacement. Persistent
            # faults remain a failure; no stale or fabricated state is returned.
            if time.monotonic() >= deadline:
                raise TimeoutError('Owned editor diagnostic remained unreadable') from error
            time.sleep(.02)
