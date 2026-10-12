"""Real Windows RegisterHotKey/WM_HOTKEY/SendInput and Apply rollback smoke.

Uses temporarily reserved Ctrl+Alt+Shift+function keys, releases every key and
registration. No text, clipboard, microphone or production server operation.
"""

import ctypes
from ctypes import wintypes as w
from dataclasses import replace
import json
import os
from pathlib import Path
import platform
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication
from voice_stt_client.core.v2_controls import ControlConfig, ControlSlot
from voice_stt_client.ui.hotkeys import CtypesHotkeyBackend, V2HotkeyManager, parse_hotkey


def run():
    if sys.platform != 'win32': raise RuntimeError('Windows is required')
    app = QApplication.instance() or QApplication([])
    backend = CtypesHotkeyBackend()
    checks, calls = [], []
    def check(name, condition):
        if not condition: raise AssertionError(name)
        checks.append(name)
    keys = []
    for number in range(12, 4, -1):
        key = f'Ctrl+Alt+Shift+F{number}'
        spec = parse_hotkey(key)
        try: backend.register(0, 0x5F00, spec.modifiers, spec.virtual_key)
        except OSError: continue
        backend.unregister(0, 0x5F00); keys.append(key)
    if len(keys) < 6: raise RuntimeError('Not enough available smoke hotkeys')
    config = ControlConfig(primary_key=keys[0], secondary_key=keys[1], wake_pause_key=keys[2],
                           reinsert_last_key=keys[3], overlay_toggle_key=keys[4])
    manager = V2HotkeyManager(config, on_control=lambda role: calls.append(str(role)),
                             on_reinsert_last=lambda: calls.append('reinsert_last'),
                             on_overlay_toggle=lambda: calls.append('overlay_toggle'), backend=backend, application=app)
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    ptr = ctypes.c_size_t
    class Keyboard(ctypes.Structure):
        _fields_ = [('vk', w.WORD), ('scan', w.WORD), ('flags', w.DWORD), ('time', w.DWORD), ('extra', ptr)]
    class Mouse(ctypes.Structure):
        _fields_ = [('dx', w.LONG), ('dy', w.LONG), ('data', w.DWORD), ('flags', w.DWORD), ('time', w.DWORD), ('extra', ptr)]
    class Hardware(ctypes.Structure):
        _fields_ = [('message', w.DWORD), ('low', w.WORD), ('high', w.WORD)]
    class Payload(ctypes.Union):
        _fields_ = [('keyboard', Keyboard), ('mouse', Mouse), ('hardware', Hardware)]
    class Input(ctypes.Structure):
        _fields_ = [('type', w.DWORD), ('payload', Payload)]
    user32.SendInput.argtypes = [w.UINT, ctypes.POINTER(Input), ctypes.c_int]
    user32.SendInput.restype = w.UINT
    def send(vk, up=False):
        item = Input(type=1, payload=Payload(keyboard=Keyboard(vk, 0, 2 if up else 0, 0, 0)))
        if user32.SendInput(1, ctypes.byref(item), ctypes.sizeof(Input)) != 1:
            raise ctypes.WinError(ctypes.get_last_error())
    def pump(duration=.15):
        end = time.monotonic() + duration
        while time.monotonic() < end:
            app.processEvents(); time.sleep(.005)
    def impulse(key, repeat=False):
        vk = parse_hotkey(key).virtual_key
        held = [0x11, 0x12, 0x10, vk]
        try:
            for value in held: send(value)
            if repeat: send(vk)  # same held key; MOD_NOREPEAT must suppress this
            pump()
        finally:
            for value in reversed(held): send(value, True)
            pump(.05)
    try:
        check('native/all_roles_registered', manager.register())
        for role, key in zip([*map(str, ControlSlot), 'reinsert_last', 'overlay_toggle'], keys):
            before = len(calls)
            impulse(key, repeat=True)
            check('native/WM_HOTKEY_exactly_once/' + role, calls[before:] == [role])
        old_ids = manager.role_ids
        entered, release = threading.Event(), threading.Event()
        owner_result = []
        def occupy():
            owner = CtypesHotkeyBackend(); spec = parse_hotkey(keys[5])
            try:
                owner.register(0, 0x5F01, spec.modifiers, spec.virtual_key)
                owner_result.append('registered'); entered.set(); release.wait(10)
            except Exception as exc:
                owner_result.append(type(exc).__name__); entered.set()
            finally: owner.unregister(0, 0x5F01)
        thread = threading.Thread(target=occupy, name='AP050-foreign-hotkey-owner')
        thread.start()
        try:
            check('native/foreign_thread_owns_key', entered.wait(3) and owner_result == ['registered'])
            replacement = replace(config, secondary_key=keys[5])
            check('native/occupied_apply_rejected', not manager.apply(replacement))
            check('native/Win32_1409_recorded', manager.last_failure[1].errno == 1409)
            check('native/atomic_rollback', manager.config == config and manager.role_ids == old_ids and manager.rollback_failure is None)
            before = len(calls); impulse(keys[0])
            check('native/old_key_operates_after_rollback', calls[before:] == ['primary'])
        finally:
            release.set(); thread.join(3)
        check('native/foreign_owner_released', not thread.is_alive())
        check('native/apply_after_release', manager.apply(replacement))
        check('native/old_ids_invalid', not manager.dispatch_hotkey_id(old_ids['secondary']))
        before = len(calls); impulse(keys[5])
        check('native/new_key_routes_secondary', calls[before:] == ['secondary'])
        manager.unregister()
        before = len(calls); impulse(keys[0])
        check('native/unregister_stops_dispatch', len(calls) == before)
        return dict(result='PASS', checks=checks, checkCount=len(checks), calls=calls,
                    runtime=dict(python=sys.version, executable=sys.executable, platform=platform.platform(),
                                 tester='Codex on local Windows desktop', qt='offscreen',
                                 timeUtc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())),
                    boundaries='Real Win32 backend and Qt native filter; actual WM_HOTKEY generated by SendInput, including held repeated key, foreign thread collision and rollback. Synthetic OS input rather than human keyboard; no app/core/ASR or final-text injection.')
    finally:
        manager.unregister()


if __name__ == '__main__': print(json.dumps(run(), indent=2))
