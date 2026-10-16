"""Temporarily register only the isolated test keys, without sending any input."""
import json
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())
sys.path.insert(0,str(ROOT))
from voice_stt_client.ui.hotkeys import CtypesHotkeyBackend, parse_hotkey


def main():
    backend = CtypesHotkeyBackend()
    registered, rows = [], []
    try:
        for key_id, key in enumerate(('Ctrl+Shift+F8','Ctrl+Shift+F9'), 0x5D40):
            spec = parse_hotkey(key)
            try:
                backend.register(0,key_id,spec.modifiers,spec.virtual_key)
            except OSError as error:
                rows.append(dict(key=key,result='BLOCKED',errno=error.errno))
            else:
                registered.append(key_id)
                rows.append(dict(key=key,result='AVAILABLE'))
    finally:
        for key_id in registered:
            backend.unregister(0,key_id)
    passed = all(r['result']=='AVAILABLE' for r in rows)
    print(json.dumps(dict(result='PASS' if passed else 'BLOCKED',keys=rows,
        boundaries='Actual RegisterHotKey, then UnregisterHotKey. No SendInput, clipboard, microphone, foreign registration changes or human-keyboard proof.')))
    return 0 if passed else 1


if __name__=='__main__':
    raise SystemExit(main())
