"""Test helper regression only; no product or Windows input side effects."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from editor_state import owned_editor_path, read_editor_state


class EditorReads(unittest.TestCase):
    def test_transient_permission_and_missing_file_then_fresh_state(self):
        with patch.object(Path, 'read_text', side_effect=[
                PermissionError(13, 'controlled sharing fault'),
                FileNotFoundError(), json.dumps({'operatorReady': True})]) as read:
            self.assertEqual(read_editor_state(Path('state.json')), {'operatorReady': True})
            self.assertEqual(read.call_count, 3)

    def test_persistent_permission_fails_closed_without_state(self):
        with patch.object(Path, 'read_text', side_effect=PermissionError(13, 'controlled')):
            with self.assertRaises(TimeoutError):
                read_editor_state(Path('state.json'), timeout=0)

    def test_unexpected_io_error_is_not_retried(self):
        with patch.object(Path, 'read_text', side_effect=OSError('controlled')) as read:
            with self.assertRaises(OSError):
                read_editor_state(Path('state.json'))
            self.assertEqual(read.call_count, 1)

    def test_guard_rejects_foreign_path_and_retains_logical_io_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            intended = root/'editors/123/state.json'
            # Path.resolve may name a Windows AppData alias. It is used solely
            # for the security comparison, not as a replacement I/O path.
            self.assertEqual(owned_editor_path(intended, root), intended.absolute())
            with self.assertRaises(ValueError):
                owned_editor_path(root/'foreign/state.json', root)


if __name__ == '__main__':
    unittest.main()
