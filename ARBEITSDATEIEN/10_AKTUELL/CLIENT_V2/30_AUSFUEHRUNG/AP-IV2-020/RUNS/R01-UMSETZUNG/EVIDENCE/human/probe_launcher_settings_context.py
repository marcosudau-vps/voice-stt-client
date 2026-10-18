"""Read-only launcher/UI diagnosis; output only inside this repository.

No real client, server, credentials, profile writes or native desktop windows.
The Qt surface uses offscreen and a fake bridge, explicitly labelled below.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
from unittest.mock import Mock, patch

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.output.absolute().is_relative_to(ROOT)
    spec = importlib.util.spec_from_file_location('context_launcher', Path(__file__).with_name('test_instance_launcher.py'))
    subject = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subject)
    missing = args.output.parent/'nonexistent-profile-probe'
    assert not missing.exists()
    with patch.object(subject, 'LOCAL', missing), patch.object(subject, 'running', return_value=False), \
            patch.object(subject, 'ensure_server') as server, patch.object(subject.subprocess, 'Popen') as process:
        try:
            subject.start_client(Mock())
        except FileNotFoundError as error:
            assert error.filename == str(missing/'client-both.yaml')
        else:
            raise AssertionError('Missing profile did not fail')
        server.assert_not_called()
        process.assert_not_called()

    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    from PySide6.QtCore import QObject, Signal
    from PySide6.QtWidgets import QApplication
    from voice_stt_client.ui.v2_settings_dialog import V2SettingsDialog
    from voice_stt_client.ui.v2_settings_bridge import UIReply

    class Bridge(QObject):
        replied = Signal(object)
        epoch = 1
        busy = False
        def open(self):
            pass
        def close(self):
            pass
        def request(self, *args, **kwargs):
            return 1

    app = QApplication.instance() or QApplication([])
    bridge = Bridge()
    dialog = V2SettingsDialog(bridge)
    dialog.show()
    dialog.timer.stop()
    app.processEvents()
    initial = dialog.origin_label.text()
    assert initial == ''
    dialog._receive(UIReply(1, 1, 'load', error='connection_changed'))
    failed = dialog.origin_label.text()
    assert failed == ''
    assert dialog.status.text()
    failure_status = dialog.status.text()
    dialog.close()

    value = {
        'missingProfile': 'REPRODUCED: FileNotFoundError before server/client side effects',
        'serverOrClientStarted': False,
        'initialOriginLabel': initial,
        'originLabelAfterFailedFirstLoadWithoutView': failed,
        'visibleErrorAfterFailedFirstLoad': failure_status,
        'uiResult': 'REPRODUCED: origin remains blank when no view was loaded',
        'boundary': 'Actual helper and Qt dialog with simulated missing profile/failed bridge reply. Not a live server outage or observation of the human settings window.'
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
    print('PASS: missing-profile fail-fast and blank-origin failure path reproduced without external writes/startup')


if __name__ == '__main__':
    main()
