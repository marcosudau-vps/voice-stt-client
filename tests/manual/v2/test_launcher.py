"""Reusable launcher never falls back to V1 or an external server profile."""
from pathlib import Path
import tempfile
import unittest
from tests.manual.v2.__main__ import isolated_profile


class LauncherIsolation(unittest.TestCase):
    def test_loopback_test_profile_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'profile.yaml'
            path.write_text('server:\n  url: ws://127.0.0.1:18020/ws/v2\n  health_url: http://127.0.0.1:18020/health\n')
            self.assertTrue(isolated_profile(path))

    def test_external_wrong_port_or_credential_url_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'profile.yaml'
            for url in ('ws://example.invalid:18020/ws/v2','ws://127.0.0.1:8010/ws/v2',
                        'ws://test:secret@127.0.0.1:18020/ws/v2'):
                path.write_text('server:\n  url: '+url+'\n  health_url: http://127.0.0.1:18020/health\n')
                self.assertFalse(isolated_profile(path))
