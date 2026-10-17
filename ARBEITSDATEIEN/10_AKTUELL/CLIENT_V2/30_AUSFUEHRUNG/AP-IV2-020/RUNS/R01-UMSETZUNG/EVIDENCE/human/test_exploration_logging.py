"""Regression for complete test-launcher manager wiring and cleanup; no devices."""
import os
from pathlib import Path
import sys
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch

import explore_with_logging as subject


class Bootstrap(unittest.TestCase):
    def test_actual_launcher_passes_manager_to_logging_and_always_restores(self):
        local = Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020'
        with patch.dict(os.environ, {'VOICESTT_CLIENT_HOME': str(local/'client')}):
            from voice_stt_client.core import v2_runtime
            from voice_stt_client.ui import v2_core_bridge, v2_application
            originals = (v2_runtime.V2Runtime, v2_core_bridge.V2CoreBridge,
                         v2_application.V2DesktopApplication)
            for fail in (False, True):
                with self.subTest(session_failure=fail):
                    manager = NS(ingress=object(), start=Mock(), stop=Mock())
                    config = NS(server=NS(url='ws://127.0.0.1:18020/ws/v2'),
                        logging=NS(log_dir=str(local/'client/logs'), observability=NS(
                            store_transcription_content=False, store_raw_payload=False)),
                        history=NS(persistent=NS(db_path=str(local/'client/history-both.sqlite'))),
                        event_stream=NS(cursor_path=str(local/'client/cursor-both.json')))
                    def logging_setup(value, *, observability):
                        self.assertIs(value, config.logging)
                        self.assertIs(observability, manager)  # Not manager.ingress.
                    def session():
                        self.assertTrue(manager.start.called)
                        for active, original in zip((v2_runtime.V2Runtime, v2_core_bridge.V2CoreBridge,
                                                    v2_application.V2DesktopApplication), originals):
                            self.assertIsNot(active, original)
                            self.assertTrue(issubclass(active, original))
                        if fail:
                            raise RuntimeError('deliberate bounded test-session failure')
                    args = ['explore_with_logging.py', '--mode', 'both']
                    with patch.object(sys, 'argv', args), \
                         patch('voice_stt_client.core.config.AppConfig.load', return_value=config), \
                         patch('voice_stt_client.core.observability.manager.ObservabilityManager', return_value=manager), \
                         patch('voice_stt_client.core.logging_setup.setup_logging', side_effect=logging_setup) as setup, \
                         patch('tests.manual.v2.observed_session.main', side_effect=session):
                        if fail:
                            with self.assertRaisesRegex(RuntimeError, 'deliberate bounded'):
                                subject.main()
                        else:
                            self.assertEqual(subject.main(), 0)
                        self.assertIs(sys.argv, args)
                    manager.start.assert_called_once_with()
                    manager.stop.assert_called_once_with(2.0)
                    setup.assert_called_once()
                    self.assertEqual((v2_runtime.V2Runtime, v2_core_bridge.V2CoreBridge,
                                      v2_application.V2DesktopApplication), originals)


if __name__ == '__main__':
    unittest.main()
