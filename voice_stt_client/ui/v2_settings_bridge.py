"""Explicit Qt -> existing core-loop port; no extra thread or Qt in core."""
from __future__ import annotations

import asyncio
from concurrent.futures import CancelledError
from dataclasses import dataclass
import threading

from PySide6.QtCore import QObject, Signal

from voice_stt_client.core.command_tracker import CommandFailure
from voice_stt_client.core.credential_store import CredentialError
from voice_stt_client.core.settings_service import SettingsError


@dataclass(frozen=True)
class UIReply:
    epoch: int
    request_id: int
    operation: str
    view: object = None
    error: str | None = None


class V2SettingsBridge(QObject):
    """One dialog lease, bounded request stream, safe queued replies.

    loop is the application's existing asyncio core loop. factory() executes
    there and returns SettingsUISession using its real services. Reopen creates
    a new lease; close invalidates before cancellation and drops old replies.
    """
    replied = Signal(object)

    def __init__(self, loop, factory, parent=None):
        super().__init__(parent)
        self._loop, self._factory = loop, factory
        self._epoch = 0
        self._request_id = 0
        self._session = None
        self._future = None
        self._open = False
        self._lease_lock = threading.RLock()

    @property
    def epoch(self):
        return self._epoch

    @property
    def busy(self):
        return self._future is not None and not self._future.done()

    def open(self):
        self.close()
        self._open = True
        self.request("load")

    def close(self):
        with self._lease_lock:
            self._open = False
            self._epoch += 1
            session, self._session = self._session, None
            if session is not None:
                # Lease invalidation precedes task cancellation.
                session.invalidate()
        if self._future is not None:
            self._future.cancel()
            self._future = None

    def request(self, operation, **payload):
        if not self._open or self.busy or operation not in (
                "load", "inspect", "load_credential", "verify", "delete_credential", "patch_server", "apply_profile"):
            return None
        self._request_id += 1
        epoch, request_id = self._epoch, self._request_id

        async def invoke():
            with self._lease_lock:
                session = self._session
                if epoch != self._epoch or not self._open:
                    return UIReply(epoch, request_id, operation, error="dialog_closed")
                if session is None:
                    session = self._factory()
                    self._session = session
            try:
                session._guard()
                if operation == "inspect":
                    view = session.view()
                else:
                    view = await getattr(session, operation)(**payload)
                return UIReply(epoch, request_id, operation, view=view)
            except (SettingsError, CredentialError, CommandFailure) as error:
                code = error.code if isinstance(error, SettingsError) else (
                    "credential_store_unavailable" if isinstance(error, CredentialError) else "connection_changed")
                view = None
                if session.active:
                    try:
                        view = session.view()
                    except (SettingsError, CommandFailure):
                        pass
                return UIReply(epoch, request_id, operation, view=view, error=code)
            except asyncio.CancelledError:
                raise
            except Exception:
                # Never emit/log str(exc), payload, key or HTTP body.
                return UIReply(epoch, request_id, operation, error="settings_operation_failed")

        coroutine = invoke()
        try:
            future = asyncio.run_coroutine_threadsafe(coroutine, self._loop)
        except RuntimeError:
            coroutine.close()
            self.replied.emit(UIReply(epoch, request_id, operation, error="core_unavailable"))
            return None
        self._future = future

        def finished(result):
            try:
                reply = result.result()
            except CancelledError:
                return
            except Exception:
                reply = UIReply(epoch, request_id, operation, error="settings_operation_failed")
            self.replied.emit(reply)

        future.add_done_callback(finished)
        return request_id
