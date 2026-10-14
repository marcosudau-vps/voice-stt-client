"""Run from project root with venv/Scripts/python.exe; no product writes."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import tests.test_v2_release as release

old = subprocess.check_output([
    'git', '-C', str(release.ROOT), 'show',
    '24c50a7c845086b03e1b8027365edddde1440f7a:.gitattributes',
])
original = Path.read_bytes
name = 'test_windows_checkout_keeps_pinned_resource_bytes'


def old_attributes(path):
    if path.resolve() == (release.ROOT / '.gitattributes').resolve():
        return old
    return original(path)


print('OLD ATTRIBUTES: expected exactly one assertion failure', flush=True)
with patch.object(Path, 'read_bytes', old_attributes):
    red = unittest.TextTestRunner(verbosity=2).run(
        unittest.TestSuite([release.RuntimeRetirement(name)]))
print('CURRENT ATTRIBUTES: expected success', flush=True)
green = unittest.TextTestRunner(verbosity=2).run(
    unittest.TestSuite([release.RuntimeRetirement(name)]))
sys.exit(0 if len(red.failures) == 1 and not red.errors and green.wasSuccessful() else 1)
