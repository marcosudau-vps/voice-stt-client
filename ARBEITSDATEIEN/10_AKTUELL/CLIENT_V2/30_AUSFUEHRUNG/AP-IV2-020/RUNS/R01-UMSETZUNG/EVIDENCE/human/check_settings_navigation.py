"""Check real Qt settings navigation without server, device or preference writes."""
from collections import Counter
import json
import os
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())
sys.path.insert(0, str(ROOT))
local_home = Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020/client'
os.environ['VOICESTT_CLIENT_HOME'] = str(local_home)
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QPushButton
from voice_stt_client.core.config import AppConfig
from voice_stt_client.core.settings_metadata import SETTING_DEFINITIONS
from voice_stt_client.ui.settings_dialog import SettingsDialog
from voice_stt_client.ui.v2_settings_dialog import V2SettingsDialog


class Port(QObject):
    replied = Signal(object)
    epoch = 1

    def open(self):
        pass

    def close(self):
        pass

    def request(self, *args, **kwargs):
        raise AssertionError('This navigation check must not submit settings requests')


def main():
    app = QApplication([])
    def forbidden(*args, **kwargs):
        raise AssertionError('No configuration apply allowed during navigation check')
    local = SettingsDialog(AppConfig(), forbidden, v2_local=True, audio_devices=())
    port = Port()
    root = V2SettingsDialog(port, local_dialog=local)
    root.show()
    root.timer.stop()
    app.processEvents()
    buttons = [b for b in root.findChildren(QPushButton)
               if b.text().startswith('Lokale Geräte, Verlauf,')]
    assert len(buttons) == 1 and buttons[0].isVisible()
    assert not local.isVisible()
    buttons[0].click()
    app.processEvents()
    assert local.isVisible()
    names = [local.tabs.tabText(i) for i in range(local.tabs.count())]
    required = ['Verlauf', 'Erscheinungsbild & Feedback', 'Logging & Diagnose']
    assert all(n in names for n in required)
    expected = {d.path for d in SETTING_DEFINITIONS if d.show_in_dialog
                and not d.path.startswith(('session.', 'dictation_window.', 'hotkey.', 'server.'))}
    missing = sorted(expected-set(local._editors))
    assert not missing, missing
    print(json.dumps(dict(result='PASS_NAVIGATION_ONLY',
        outerTabs=[root.tabs.tabText(i) for i in range(root.tabs.count())],
        navigationButton=buttons[0].text(),localDialogVisibleAfterActualClick=True,
        localTabs=names,expectedLocalSettingCount=len(expected),localEditorCount=len(local._editors),
        missingLocalSettings=missing,localFieldsByCategory=dict(Counter(
            d.category for d in SETTING_DEFINITIONS if d.path in expected)),
        boundaries='Actual Qt dialogs and button click with inert settings port; all current local metadata fields accounted for. No server, microphone, live-instance interaction, saved configuration changes, full V1 parity or logging-service functionality claim.'),
        ensure_ascii=True,indent=2))
    local.close();root.close()
    app.processEvents()


if __name__ == '__main__':
    main()
