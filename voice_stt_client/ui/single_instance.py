"""Windows single-instance guard backed by a named local mutex."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from enum import Enum
import logging
import sys
from typing import Optional, Protocol, Tuple

logger = logging.getLogger("ui.single_instance")

ERROR_ALREADY_EXISTS = 183
DEFAULT_MUTEX_NAME = r"Local\RealtimeSTT_Client_7F51A2C9"


class InstanceAcquireStatus(str, Enum):
    ACQUIRED = "acquired"
    ALREADY_RUNNING = "already_running"
    ERROR = "error"


@dataclass(frozen=True)
class InstanceAcquireResult:
    status: InstanceAcquireStatus
    error: Optional[str] = None

    @property
    def acquired(self) -> bool:
        return self.status == InstanceAcquireStatus.ACQUIRED


class MutexBackend(Protocol):
    def create(self, name: str) -> Tuple[int, bool]: ...

    def close(self, handle: int) -> None: ...


class CtypesMutexBackend:
    def __init__(self) -> None:
        if sys.platform != "win32":
            raise OSError("Single-instance mutex requires Windows")
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateMutexW.argtypes = [
            wintypes.LPVOID,
            wintypes.BOOL,
            wintypes.LPCWSTR,
        ]
        kernel32.CreateMutexW.restype = wintypes.HANDLE
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        self._kernel32 = kernel32

    def create(self, name: str) -> Tuple[int, bool]:
        ctypes.set_last_error(0)
        handle = self._kernel32.CreateMutexW(None, False, name)
        error = ctypes.get_last_error()
        if not handle:
            raise OSError(error, "CreateMutexW failed")
        return int(handle), error == ERROR_ALREADY_EXISTS

    def close(self, handle: int) -> None:
        if handle and not self._kernel32.CloseHandle(handle):
            error = ctypes.get_last_error()
            raise OSError(error, "CloseHandle failed for instance mutex")


class SingleInstanceGuard:
    """Acquire before QApplication/Core startup and hold until final shutdown."""

    def __init__(
        self,
        name: str = DEFAULT_MUTEX_NAME,
        backend: Optional[MutexBackend] = None,
    ) -> None:
        self.name = name
        self._backend = backend
        self._handle: Optional[int] = None
        self._acquired = False

    @property
    def is_acquired(self) -> bool:
        return self._acquired

    def acquire(self) -> InstanceAcquireResult:
        if self._acquired:
            return InstanceAcquireResult(InstanceAcquireStatus.ACQUIRED)
        try:
            if self._backend is None:
                self._backend = CtypesMutexBackend()
            handle, already_exists = self._backend.create(self.name)
            if already_exists:
                self._backend.close(handle)
                return InstanceAcquireResult(
                    InstanceAcquireStatus.ALREADY_RUNNING
                )
            self._handle = handle
            self._acquired = True
            return InstanceAcquireResult(InstanceAcquireStatus.ACQUIRED)
        except Exception as exc:
            logger.exception("Failed to acquire single-instance mutex.")
            return InstanceAcquireResult(
                InstanceAcquireStatus.ERROR,
                error=str(exc),
            )

    def release(self) -> None:
        handle = self._handle
        self._handle = None
        self._acquired = False
        if handle is None:
            return
        try:
            assert self._backend is not None
            self._backend.close(handle)
        except Exception:
            logger.exception("Failed to release single-instance mutex.")

    def __enter__(self) -> SingleInstanceGuard:
        result = self.acquire()
        if not result.acquired:
            raise RuntimeError(result.error or result.status.value)
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.release()
