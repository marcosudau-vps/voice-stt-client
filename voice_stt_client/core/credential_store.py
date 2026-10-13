"""Origin-bound Windows generic credentials; never a plaintext fallback."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import hashlib
import sys
from urllib.parse import urlsplit


class CredentialError(RuntimeError):
    def __init__(self):
        super().__init__("credential_store_unavailable")


def credential_target(origin: str) -> str:
    """Canonical HTTP origin only. No paths, userinfo, query or fragments."""
    try:
        parts = urlsplit(origin)
        if (parts.scheme not in ("http", "https") or not parts.hostname or parts.username
                or parts.password or parts.path not in ("", "/") or parts.query or parts.fragment):
            raise ValueError
        host = parts.hostname.lower().encode("idna").decode("ascii")
        port = parts.port or (443 if parts.scheme == "https" else 80)
        if parts.scheme == "http" and host not in ("localhost", "127.0.0.1", "::1"):
            raise ValueError
        normalized = f"{parts.scheme}://{host}:{port}"
    except (ValueError, UnicodeError):
        raise ValueError("invalid_credential_origin") from None
    return "VoiceSTTClient/v2/admin/" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class _Credential(ctypes.Structure):
    _fields_ = [("Flags", wintypes.DWORD), ("Type", wintypes.DWORD),
                ("TargetName", wintypes.LPWSTR), ("Comment", wintypes.LPWSTR),
                ("LastWritten", wintypes.FILETIME), ("CredentialBlobSize", wintypes.DWORD),
                ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)), ("Persist", wintypes.DWORD),
                ("AttributeCount", wintypes.DWORD), ("Attributes", ctypes.c_void_p),
                ("TargetAlias", wintypes.LPWSTR), ("UserName", wintypes.LPWSTR)]


class WindowsCredentialBackend:
    """CRED_TYPE_GENERIC, CRED_PERSIST_LOCAL_MACHINE in the current user vault."""
    def __init__(self):
        if sys.platform != "win32":
            raise CredentialError()
        self._api = ctypes.WinDLL("advapi32", use_last_error=True)
        self._api.CredWriteW.argtypes = [ctypes.POINTER(_Credential), wintypes.DWORD]
        self._api.CredWriteW.restype = wintypes.BOOL
        self._api.CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                       ctypes.POINTER(ctypes.POINTER(_Credential))]
        self._api.CredReadW.restype = wintypes.BOOL
        self._api.CredDeleteW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD]
        self._api.CredDeleteW.restype = wintypes.BOOL
        self._api.CredFree.argtypes = [ctypes.c_void_p]
        self._api.CredFree.restype = None

    def read(self, target):
        pointer = ctypes.POINTER(_Credential)()
        if not self._api.CredReadW(target, 1, 0, ctypes.byref(pointer)):
            if ctypes.get_last_error() == 1168:  # ERROR_NOT_FOUND
                return None
            raise CredentialError()
        try:
            value = pointer.contents
            return ctypes.string_at(value.CredentialBlob, value.CredentialBlobSize).decode("utf-16-le")
        except (ValueError, UnicodeError):
            raise CredentialError() from None
        finally:
            self._api.CredFree(pointer)

    def write(self, target, key):
        data = key.encode("utf-16-le")
        if not data or len(data) > 2560:
            raise CredentialError()
        blob = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
        value = _Credential(Type=1, TargetName=target, UserName="VoiceSTTClient",
                            CredentialBlobSize=len(data), CredentialBlob=blob, Persist=2)
        if not self._api.CredWriteW(ctypes.byref(value), 0):
            raise CredentialError()

    def delete(self, target):
        if not self._api.CredDeleteW(target, 1, 0) and ctypes.get_last_error() != 1168:
            raise CredentialError()


class CredentialStore:
    """Only explicit read/save/delete touch the vault. repr contains no secret.

    The caller owns process memory and optional nonsecret QSettings metadata.
    Backend exceptions are redacted, including arbitrary injected adapters.
    """
    def __init__(self, backend=None):
        self._backend = backend

    def _call(self, method, origin, *args):
        target = credential_target(origin)
        try:
            if self._backend is None:
                self._backend = WindowsCredentialBackend()
            return getattr(self._backend, method)(target, *args)
        except Exception:
            raise CredentialError() from None

    def read(self, origin):
        return self._call("read", origin)

    def save(self, origin, key):
        if not isinstance(key, str) or not key or "\n" in key or "\r" in key:
            raise CredentialError()
        self._call("write", origin, key)

    def delete(self, origin):
        self._call("delete", origin)

    def __repr__(self):
        return "CredentialStore(<redacted>)"
