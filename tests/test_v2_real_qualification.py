"""Qualification tooling must reject remote/wrong servers and retain failures."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import qualify_v2_real as q


class QualificationGuards(unittest.TestCase):
    def test_runner_does_not_override_unit_fixture_profile_roots(self):
        import os
        import sys
        identity={'commit':'candidate','sourceSha256':{'x':'a'}}
        with tempfile.TemporaryDirectory() as folder, patch.object(q,'identity',return_value=identity), \
                patch.dict(os.environ,{'VOICESTT_CLIENT_HOME':'inherited-profile'}):
            result=q.command('environment',[sys.executable,'-c',
                "import os;assert 'VOICESTT_CLIENT_HOME' not in os.environ"],folder)
            self.assertEqual(result['result'],'PASS')

    def test_profiles_are_isolated_and_existing_calibration_is_preserved(self):
        from scripts import qualify_v2_session as session
        from voice_stt_client.core.audio_capture import AudioCapture
        import yaml
        with tempfile.TemporaryDirectory() as folder, patch.object(session,'LOCAL',Path(folder)), \
                patch.object(AudioCapture,'list_devices',return_value=[dict(name='ReSpeaker fixture',index=7)]):
            session.prepare()
            for mode in ('manual','wake','both'):
                d=yaml.safe_load((Path(folder)/('client-'+mode+'.yaml')).read_text(encoding='utf8'))
                self.assertEqual(d['server']['url'],'ws://127.0.0.1:18020/ws/v2')
                self.assertTrue(Path(d['history']['persistent']['db_path']).is_relative_to(folder))
                self.assertEqual(d['v2_profile']['wake_word'],mode!='manual')
            p=Path(folder)/'client-manual.yaml'
            p.write_text('preserved calibration',encoding='utf8')
            session.prepare()
            self.assertEqual(p.read_text(),'preserved calibration')

    def test_loopback_guard_rejects_production_auth_and_ambiguous_urls(self):
        for value in ('https://stt.voice.marcosudau.com', 'http://example.com',
                      'http://127.0.0.1@example.com', 'http://user@localhost',
                      'http://127.0.0.1/?key=value', 'http://localhost/api',
                      'http://localhost/#fragment'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                q.loopback_origin(value)
        self.assertEqual(q.loopback_origin('http://127.0.0.1:18020/'), 'http://127.0.0.1:18020')

    def test_wrong_server_never_writes_qualification_inventory(self):
        with tempfile.TemporaryDirectory() as folder:
            for schema in ({'serverCommit':'wrong','secretsExposed':False},
                           {'serverCommit':q.SERVER,'secretsExposed':True}):
                with patch.object(q, 'get_json', return_value=schema), self.assertRaises(RuntimeError):
                    q.server_inventory('http://localhost:18020', folder)
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_failed_command_keeps_complete_log_and_failure(self):
        import gzip
        import sys
        identity={'commit':'candidate','sourceSha256':{'x':'a'}}
        with tempfile.TemporaryDirectory() as folder, patch.object(q, 'identity', return_value=identity):
            result=q.command('failure', [sys.executable,'-c',"print('retained');raise SystemExit(3)"], folder)
            self.assertEqual((result['result'],result['exitCode']), ('FAIL',3))
            self.assertIn(b'retained',gzip.decompress((Path(folder)/result['log']).read_bytes()))
            self.assertEqual(json.loads((Path(folder)/'failure.json').read_text())['exitCode'],3)

    def test_green_exit_with_source_change_is_not_pass(self):
        import sys
        before={'commit':'a','sourceSha256':{'x':'a'}}
        after={'commit':'a','sourceSha256':{'x':'b'}}
        with tempfile.TemporaryDirectory() as folder, patch.object(q,'identity',side_effect=[before,after]):
            result=q.command('changed',[sys.executable,'-c','pass'],folder)
        self.assertEqual(result['result'],'FAIL')


if __name__ == '__main__':
    unittest.main()
