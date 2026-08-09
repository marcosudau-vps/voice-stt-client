"""Native Win32 global hotkeys integrated through Qt's native event filter."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import logging
import sys
from typing import Callable, Optional, Protocol

from PySide6.QtCore import QAbstractNativeEventFilter, QCoreApplication

from core.config import normalize_hotkey_spec

logger = logging.getLogger("ui.hotkeys")

WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

HOTKEY_ID_TOGGLE = 0x5101
HOTKEY_ID_REINSERT_LAST = 0x5102
HOTKEY_ID_FINISH = 0x5103
HOTKEY_ID_CANCEL = 0x5104
HOTKEY_ID_OVERLAY_TOGGLE = 0x5105

_MODIFIER_BITS = {
    "Ctrl": MOD_CONTROL,
    "Alt": MOD_ALT,
    "Shift": MOD_SHIFT,
    "Win": MOD_WIN,
}
_NAMED_VIRTUAL_KEYS = {
    "Space": 0x20,
    "PageUp": 0x21,
    "PageDown": 0x22,
    "End": 0x23,
    "Home": 0x24,
    "Left": 0x25,
    "Up": 0x26,
    "Right": 0x27,
    "Down": 0x28,
    "Insert": 0x2D,
    "Delete": 0x2E,
    "Enter": 0x0D,
    "Tab": 0x09,
    "Escape": 0x1B,
    "Backspace": 0x08,
}


@dataclass(frozen=True)
class HotkeySpec:
    canonical: str
    modifiers: int
    virtual_key: int


def parse_hotkey(value: str) -> HotkeySpec:
    """Parse a validated config hotkey into Win32 modifier and key codes."""
    canonical = normalize_hotkey_spec(value)
    tokens = canonical.split("+")
    key_name = tokens[-1]
    modifiers = MOD_NOREPEAT
    for token in tokens[:-1]:
        modifiers |= _MODIFIER_BITS[token]

    if len(key_name) == 1 and key_name.isalnum():
        virtual_key = ord(key_name.upper())
    elif key_name.startswith("F") and key_name[1:].isdigit():
        virtual_key = 0x70 + int(key_name[1:]) - 1
    else:
        virtual_key = _NAMED_VIRTUAL_KEYS[key_name]

    return HotkeySpec(
        canonical=canonical,
        modifiers=modifiers,
        virtual_key=virtual_key,
    )


class HotkeyBackend(Protocol):
    def register(
        self, window_handle: int, hotkey_id: int, modifiers: int, virtual_key: int
    ) -> None: ...

    def unregister(self, window_handle: int, hotkey_id: int) -> None: ...


class CtypesHotkeyBackend:
    """Small checked wrapper around RegisterHotKey/UnregisterHotKey."""

    def __init__(self) -> None:
        if sys.platform != "win32":
            raise OSError("Native global hotkeys require Windows")
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.RegisterHotKey.argtypes = [
            wintypes.HWND,
            ctypes.c_int,
            wintypes.UINT,
            wintypes.UINT,
        ]
        user32.RegisterHotKey.restype = wintypes.BOOL
        user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.UnregisterHotKey.restype = wintypes.BOOL
        self._user32 = user32

    def register(
        self, window_handle: int, hotkey_id: int, modifiers: int, virtual_key: int
    ) -> None:
        if not self._user32.RegisterHotKey(
            window_handle, hotkey_id, modifiers, virtual_key
        ):
            error = ctypes.get_last_error()
            raise OSError(
                error,
                f"RegisterHotKey failed for id={hotkey_id}",
            )

    def unregister(self, window_handle: int, hotkey_id: int) -> None:
        if not self._user32.UnregisterHotKey(window_handle, hotkey_id):
            error = ctypes.get_last_error()
            if error:
                logger.debug(
                    "UnregisterHotKey returned false for id=%s (error=%s)",
                    hotkey_id,
                    error,
                )


class GlobalHotkeyManager(QAbstractNativeEventFilter):
    """Own two atomically registered application hotkeys."""

    def __init__(
        self,
        *,
        toggle_key: str,
        reinsert_last_key: str,
        on_toggle: Callable[[], None],
        on_reinsert_last: Callable[[], None],
        finish_key: Optional[str] = None,
        cancel_key: Optional[str] = None,
        overlay_toggle_key: Optional[str] = None,
        on_finish: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        on_overlay_toggle: Optional[Callable[[], None]] = None,
        enabled: bool = True,
        backend: Optional[HotkeyBackend] = None,
        application: Optional[QCoreApplication] = None,
    ) -> None:
        super().__init__()
        self.enabled = enabled
        self.toggle_spec = parse_hotkey(toggle_key)
        self.reinsert_last_spec = parse_hotkey(reinsert_last_key)
        self._specs: dict[int, HotkeySpec] = {
            HOTKEY_ID_TOGGLE: self.toggle_spec,
            HOTKEY_ID_REINSERT_LAST: self.reinsert_last_spec,
        }
        self._callbacks: dict[int, Callable[[], None]] = {
            HOTKEY_ID_TOGGLE: on_toggle,
            HOTKEY_ID_REINSERT_LAST: on_reinsert_last,
        }
        optional = (
            (HOTKEY_ID_FINISH, finish_key, on_finish),
            (HOTKEY_ID_CANCEL, cancel_key, on_cancel),
            (HOTKEY_ID_OVERLAY_TOGGLE, overlay_toggle_key, on_overlay_toggle),
        )
        for hotkey_id, value, callback in optional:
            if value is None or not value.strip():
                continue
            if callback is None:
                raise ValueError(f"callback missing for configured hotkey id={hotkey_id}")
            self._specs[hotkey_id] = parse_hotkey(value)
            self._callbacks[hotkey_id] = callback
        canonical = [spec.canonical for spec in self._specs.values()]
        if len(canonical) != len(set(canonical)):
            raise ValueError("all configured action hotkeys must differ")
        self._backend = backend
        self._application = application or QCoreApplication.instance()
        self._registered_ids: list[int] = []
        self._installed = False

    @property
    def is_registered(self) -> bool:
        return bool(self._registered_ids) or not self.enabled

    def register(self) -> bool:
        if not self.enabled:
            return True
        if self._registered_ids:
            return True
        if self._application is None:
            raise RuntimeError("QCoreApplication must exist before hotkeys register")
        if self._backend is None:
            self._backend = CtypesHotkeyBackend()

        registrations = tuple(self._specs.items())
        try:
            for hotkey_id, spec in registrations:
                self._backend.register(
                    0, hotkey_id, spec.modifiers, spec.virtual_key
                )
                self._registered_ids.append(hotkey_id)
            self._application.installNativeEventFilter(self)
            self._installed = True
            return True
        except Exception:
            logger.exception("Global hotkey registration failed.")
            self.unregister()
            return False

    def unregister(self) -> None:
        backend = self._backend
        for hotkey_id in reversed(self._registered_ids):
            try:
                if backend is not None:
                    backend.unregister(0, hotkey_id)
            except Exception:
                logger.exception(
                    "Failed to unregister global hotkey id=%s.", hotkey_id
                )
        self._registered_ids.clear()
        if self._installed and self._application is not None:
            self._application.removeNativeEventFilter(self)
        self._installed = False

    def dispatch_hotkey_id(self, hotkey_id: int) -> bool:
        """Dispatch an ID; public for deterministic native-event tests."""
        callback = self._callbacks.get(hotkey_id)
        if callback is None or hotkey_id not in self._registered_ids:
            return False
        try:
            callback()
        except Exception:
            logger.exception("Global hotkey callback failed for id=%s.", hotkey_id)
        return True

    def nativeEventFilter(self, event_type, message):  # noqa: N802 (Qt API)
        if sys.platform != "win32":
            return False, 0
        try:
            msg = wintypes.MSG.from_address(int(message))
            if msg.message == WM_HOTKEY:
                handled = self.dispatch_hotkey_id(int(msg.wParam))
                return handled, 0
        except Exception:
            logger.exception("Failed to decode native Windows message.")
        return False, 0
