"""Launcher boundaries: no real server/process changes during regression."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import test_instance_launcher as subject


class Launcher(unittest.TestCase):
    def test_container_requires_exact_identity_label_and_loopback_binding(self):
        good = {'Image': subject.IMAGE, 'Config': {'Labels': {'voice-stt.qualification': 'AP-IV2-020'}},
                'HostConfig': {'PortBindings': {'8010/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '18020'}]}}}
        subject.validate_container(good)
        for field in ('image', 'label', 'binding'):
            bad = copy.deepcopy(good)
            if field == 'image': bad['Image'] = 'different'
            if field == 'label': bad['Config']['Labels'].clear()
            if field == 'binding': bad['HostConfig']['PortBindings']['8010/tcp'][0]['HostIp'] = '0.0.0.0'
            with self.subTest(field=field), self.assertRaises(ValueError):
                subject.validate_container(bad)

    def test_existing_instance_never_starts_server_or_another_client(self):
        with patch.object(subject, 'running', return_value=True), \
             patch.object(subject, 'ensure_server') as server, \
             patch.object(subject.subprocess, 'Popen') as child:
            subject.start_client(Mock())
            server.assert_not_called()
            child.assert_not_called()

    def test_external_profile_is_rejected_before_server_or_client_start(self):
        with tempfile.TemporaryDirectory() as directory:
            local = Path(directory)
            (local/'client-both.yaml').write_text('server:\n  url: wss://example.invalid/ws/v2\n')
            with patch.object(subject, 'LOCAL', local), patch.object(subject, 'running', return_value=False), \
                 patch.object(subject, 'ensure_server') as server, patch.object(subject.subprocess, 'Popen') as child:
                with self.assertRaises(ValueError): subject.start_client(Mock())
                server.assert_not_called()
                child.assert_not_called()

    def test_starts_project_python_with_isolated_adapter_and_local_log(self):
        with tempfile.TemporaryDirectory() as directory:
            local = Path(directory)
            (local/'client-both.yaml').write_text('server:\n  url: ws://127.0.0.1:18020/ws/v2\n')
            with patch.object(subject, 'LOCAL', local), \
                 patch.object(subject, 'running', side_effect=[False, False, True]), \
                 patch.object(subject, 'ensure_server') as server, \
                 patch.object(subject.subprocess, 'Popen', return_value=Mock(poll=Mock(return_value=None))) as child:
                subject.start_client(Mock())
                server.assert_called_once()
                args, options = child.call_args
                self.assertEqual(Path(args[0][0]), subject.ROOT/'venv/Scripts/python.exe')
                self.assertEqual(args[0][-2:], ['--mode', 'both'])
                self.assertTrue(args[0][2].endswith('explore_with_logging.py'))
                self.assertEqual(options['env']['QT_QPA_PLATFORM'], 'windows')
                self.assertEqual(options['creationflags'], subject.subprocess.CREATE_NO_WINDOW)
                self.assertEqual(len(list((local/'launcher-logs').glob('*.log'))), 1)

    def test_actual_qt_start_button_then_settings_without_process_side_effects(self):
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication, QPushButton
        app = QApplication.instance() or QApplication([])
        with patch.object(subject, 'running', return_value=False), \
             patch.object(subject, 'start_client') as start:
            def inspect():
                window = next(w for w in QApplication.topLevelWidgets() if w.windowTitle().startswith('V2-Testinstanz'))
                buttons = {b.text(): b for b in window.findChildren(QPushButton)}
                buttons['Testinstanz starten'].click()
                QTimer.singleShot(100, app.quit)
            QTimer.singleShot(100, inspect)
            self.assertEqual(subject.main(), 0)
            start.assert_called_once()


if __name__ == '__main__':
    unittest.main()
