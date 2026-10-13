"""V2 commands and transactional Qt ports on the retained CoreBridge thread."""
from __future__ import annotations

import asyncio
from concurrent.futures import Future
from copy import deepcopy
import threading
import time

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication

from voice_stt_client.core.v2_runtime import V2Runtime
from voice_stt_client.core.v2_controls import ControlSlot, plan_control
from voice_stt_client.core.controller import CommandResult
from voice_stt_client.core.settings_service import SettingsError
from voice_stt_client.core.observability.ingress import NULL_INGRESS
from voice_stt_client.core.audio_capture import AudioCapture
from .core_bridge import CoreBridge
from .v2_settings_bridge import V2SettingsBridge


class V2CoreBridge(CoreBridge):
    ui_transaction = Signal(str, object, object)
    audio_devices_received = Signal(object)

    def __init__(self, config, *, runtime_factory=None, observability=NULL_INGRESS, parent=None):
        def factory(cfg):
            runtime = (runtime_factory(cfg) if runtime_factory else V2Runtime(cfg, observability=observability))
            runtime.persist_profile = self._persist_profile
            return runtime
        super().__init__(deepcopy(config), factory, parent, observability)
        self._published_view = None
        self.snapshot_changed.connect(self._remember_view)

    def _remember_view(self, view):
        self._published_view = view

    async def _qt(self, operation, payload):
        reply = Future()
        self.ui_transaction.emit(operation, payload, reply)
        try:
            return await asyncio.wait_for(asyncio.wrap_future(reply), 5)
        finally:
            if not reply.done():
                reply.cancel()

    async def _persist_profile(self, profile):
        """Only native registration/config projection in Qt, disk on a worker."""
        token, candidate, old = await self._qt('profile_prepare', profile)
        saved = False
        try:
            await asyncio.to_thread(candidate.save_user)
            saved = True
            await self._qt('profile_commit', (token, candidate))
            self.config = deepcopy(candidate)
            if self._controller is not None:
                self._controller.config = deepcopy(candidate)
        except BaseException:
            if saved:
                await asyncio.to_thread(old.save_user)
            await self._qt('profile_rollback', token)
            raise

    def settings_bridge(self, parent=None):
        loop, runtime = self._get_target()
        if loop is None or runtime is None:
            return None
        return V2SettingsBridge(loop, runtime.settings_ui_session, parent)

    def request_audio_devices(self):
        loop, runtime = self._get_target()
        if loop is None or runtime is None:
            return False
        async def load():
            async def scan():
                return tuple(await asyncio.to_thread(AudioCapture.list_devices))
            try:
                devices = await runtime._transaction(scan)
                if not runtime.is_closing:
                    self.audio_devices_received.emit(devices)
            except Exception:
                self.audio_devices_received.emit(())
        try:
            asyncio.run_coroutine_threadsafe(load(), loop)
            return True
        except RuntimeError:
            return False

    def press_control(self, slot):
        """Bind physical impulses to the Qt-published generation/activation."""
        slot = ControlSlot(slot)
        command_id, correlation_id = self._new_command_ids()
        self._observe_command_requested('control', command_id, correlation_id)
        published = self._published_view
        loop, runtime = self._get_target()
        if loop is None or runtime is None or published is None or not published.ready:
            return self._reject_command('control', command_id, correlation_id)
        # Actions and IDs are captured here, never retargeted after queueing.
        intent = None if slot == ControlSlot.WAKE_PAUSE else plan_control(
            published.mirror, slot, published.controls)
        generation, session_id = published.generation, published.session_id
        async def invoke():
            b = runtime.session.binding
            if b is None or (b.generation, b.session_id) != (generation, session_id):
                return CommandResult(False, 'stale_control')
            return await runtime._control(lambda: runtime.controls.press(slot) if slot == ControlSlot.WAKE_PAUSE
                                          else runtime.controls.execute(intent))
        def schedule():
            task = loop.create_task(invoke())
            task.add_done_callback(lambda done: self._finish_async_command('control', done, command_id, correlation_id))
        try:
            loop.call_soon_threadsafe(schedule)
            return True
        except RuntimeError:
            return self._reject_command('control', command_id, correlation_id)

    def primary_dictation_action(self):
        return self.press_control(ControlSlot.PRIMARY)

    toggle_dictation = primary_dictation_action

    def apply_runtime_config(self, candidate, *, settings_correlation_id=None):
        return super().apply_runtime_config(deepcopy(candidate), settings_correlation_id=settings_correlation_id)

    def stop(self, timeout=10):
        """Keep Qt transaction replies flowing while its core shuts down."""
        with self._lock:
            self._stop_requested = True
            self._accepting_commands = False
            loop, runtime, thread = self._loop, self._controller, self._thread
        if loop is not None and runtime is not None and not loop.is_closed():
            coroutine = runtime.shutdown()
            try:
                asyncio.run_coroutine_threadsafe(coroutine, loop)
            except RuntimeError:
                coroutine.close()
        deadline = time.monotonic() + timeout
        app = QApplication.instance()
        while thread is not None and thread.is_alive() and time.monotonic() < deadline:
            if app is not None and threading.current_thread() is threading.main_thread():
                app.processEvents()
            thread.join(.01)
        return thread is None or not thread.is_alive()
