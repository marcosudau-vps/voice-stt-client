"""Thread-safe bridge between the Qt main thread and the asyncio core."""

from __future__ import annotations

import asyncio
from concurrent.futures import Future
import logging
import threading
from typing import Callable, Optional

from PySide6.QtCore import QObject, Signal

from core.config import AppConfig
from core.controller import CommandResult, STTController
from core.reinsertion import ReinsertionResult, ReinsertionStatus

logger = logging.getLogger("ui.core_bridge")

ControllerFactory = Callable[[AppConfig], STTController]


class CoreBridge(QObject):
    """Own the Core thread and expose queued Qt signals and semantic commands."""

    snapshot_changed = Signal(object)
    feedback_received = Signal(object)
    text_received = Signal(int, str, bool)
    transport_changed = Signal(object)
    command_completed = Signal(str, object)
    history_received = Signal(object)
    core_started = Signal(int)
    core_stopped = Signal()
    fatal_error = Signal(str)

    def __init__(
        self,
        config: AppConfig,
        controller_factory: Optional[ControllerFactory] = None,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self.config = config
        self._controller_factory = controller_factory or STTController
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._controller: Optional[STTController] = None
        self._startup_event = threading.Event()
        self._stopped_event = threading.Event()
        self._accepting_commands = False
        self._stop_requested = False
        self._worker_thread_id: Optional[int] = None

    @property
    def worker_thread_id(self) -> Optional[int]:
        with self._lock:
            return self._worker_thread_id

    @property
    def is_running(self) -> bool:
        with self._lock:
            return (
                self._accepting_commands
                and self._thread is not None
                and self._thread.is_alive()
            )

    def start(self, timeout: float = 5.0) -> bool:
        """Start exactly one non-daemon Core thread and await loop creation."""
        with self._lock:
            if self._thread is not None:
                return self._thread.is_alive()
            self._startup_event.clear()
            self._stopped_event.clear()
            self._stop_requested = False
            thread = threading.Thread(
                target=self._thread_main,
                name="RealtimeSTT-AsyncCore",
                daemon=False,
            )
            self._thread = thread
            thread.start()

        if not self._startup_event.wait(timeout):
            logger.error("Core thread did not initialize within %.1f seconds.", timeout)
            return False
        return self.is_running

    def _thread_main(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        controller: Optional[STTController] = None
        error_message: Optional[str] = None
        try:
            controller = self._controller_factory(self.config)
            if self.config.hotkey.auto_start:
                controller.request_initial_auto_start()
            controller.on_snapshot_change = self.snapshot_changed.emit
            controller.on_feedback_event = self.feedback_received.emit
            controller.on_text = self.text_received.emit
            controller.on_transport_change = self.transport_changed.emit

            with self._lock:
                self._loop = loop
                self._controller = controller
                self._worker_thread_id = threading.get_ident()
                self._accepting_commands = not self._stop_requested
                worker_id = self._worker_thread_id
            self._startup_event.set()
            self.core_started.emit(worker_id)
            self.snapshot_changed.emit(controller.get_snapshot())

            if self._stop_requested:
                loop.run_until_complete(controller.shutdown())
            else:
                loop.run_until_complete(controller.run())
        except Exception as exc:
            error_message = str(exc)
            logger.exception("Core thread terminated with an error.")
        finally:
            self._startup_event.set()
            if controller is not None and not controller.is_closing:
                try:
                    loop.run_until_complete(controller.shutdown())
                except Exception:
                    logger.exception("Final Core cleanup failed.")

            pending = [task for task in asyncio.all_tasks(loop) if not task.done()]
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
            asyncio.set_event_loop(None)

            with self._lock:
                self._accepting_commands = False
                self._loop = None
                self._controller = None
                self._worker_thread_id = None
            self._stopped_event.set()
            if error_message and not self._stop_requested:
                self.fatal_error.emit(error_message)
            self.core_stopped.emit()

    def _get_target(
        self,
    ) -> tuple[Optional[asyncio.AbstractEventLoop], Optional[STTController]]:
        with self._lock:
            if not self._accepting_commands:
                return None, None
            return self._loop, self._controller

    def _reject_command(self, name: str) -> bool:
        self.command_completed.emit(
            name,
            CommandResult(
                success=False,
                status="core_unavailable",
                message="Core is not accepting commands",
            ),
        )
        return False

    def _submit_coroutine(self, name: str, method_name: str) -> bool:
        loop, controller = self._get_target()
        if loop is None or controller is None or loop.is_closed():
            return self._reject_command(name)

        def invoke() -> None:
            try:
                method = getattr(controller, method_name)
                task = loop.create_task(method())
                task.add_done_callback(
                    lambda finished: self._finish_async_command(name, finished)
                )
            except Exception as exc:
                logger.exception("Failed to schedule Core command %s.", name)
                self.command_completed.emit(
                    name,
                    CommandResult(False, "schedule_failed", str(exc)),
                )

        try:
            loop.call_soon_threadsafe(invoke)
            return True
        except RuntimeError:
            logger.info("Core loop closed while scheduling %s.", name)
            return self._reject_command(name)

    def _finish_async_command(self, name: str, task: asyncio.Task) -> None:
        try:
            result = task.result()
        except asyncio.CancelledError:
            result = CommandResult(False, "cancelled", "Command was cancelled")
        except Exception as exc:
            logger.exception("Core command %s failed.", name)
            result = CommandResult(False, "error", str(exc))
        self.command_completed.emit(name, result)

    def toggle_dictation(self) -> bool:
        return self._submit_coroutine("toggle_dictation", "toggle_dictation")

    def primary_dictation_action(self) -> bool:
        return self._submit_coroutine(
            "primary_dictation_action", "primary_dictation_action"
        )

    def start_dictation(self) -> bool:
        return self._submit_coroutine("start_dictation", "start_dictation")

    def stop_dictation(self) -> bool:
        return self._submit_coroutine("stop_dictation", "stop_dictation")

    def cancel_dictation(self) -> bool:
        return self._submit_coroutine("cancel_dictation", "cancel_dictation")

    def apply_runtime_config(self, candidate: AppConfig) -> bool:
        loop, controller = self._get_target()
        if loop is None or controller is None or loop.is_closed():
            return self._reject_command("apply_runtime_config")

        def invoke() -> None:
            task = loop.create_task(controller.apply_runtime_config(candidate))
            task.add_done_callback(
                lambda finished: self._finish_async_command(
                    "apply_runtime_config", finished
                )
            )

        try:
            loop.call_soon_threadsafe(invoke)
            return True
        except RuntimeError:
            return self._reject_command("apply_runtime_config")

    def _submit_sync(
        self,
        name: str,
        callback: Callable[[STTController], object],
        *,
        history_result: bool = False,
    ) -> bool:
        loop, controller = self._get_target()
        if loop is None or controller is None or loop.is_closed():
            if history_result:
                self.history_received.emit(())
                return False
            return self._reject_command(name)

        def invoke() -> None:
            try:
                result = callback(controller)
            except Exception as exc:
                logger.exception("Synchronous Core command %s failed.", name)
                if history_result:
                    self.history_received.emit(())
                    return
                result = ReinsertionResult(
                    status=ReinsertionStatus.FAILED,
                    reason="command_exception",
                    error_message=str(exc),
                )
            if history_result:
                self.history_received.emit(result)
            else:
                self.command_completed.emit(name, result)

        try:
            loop.call_soon_threadsafe(invoke)
            return True
        except RuntimeError:
            logger.info("Core loop closed while scheduling %s.", name)
            if history_result:
                self.history_received.emit(())
                return False
            return self._reject_command(name)

    def reinsert_last(self) -> bool:
        return self._submit_sync(
            "reinsert_last", lambda controller: controller.reinsert_last()
        )

    def reinsert_entry(self, entry_id: str) -> bool:
        return self._submit_sync(
            "reinsert_entry",
            lambda controller: controller.reinsert_entry(entry_id),
        )

    def request_history(self, limit: int = 10) -> bool:
        return self._submit_sync(
            "get_recent_entries",
            lambda controller: controller.get_recent_entries(limit),
            history_result=True,
        )

    def delete_history_entry(self, entry_id: str) -> bool:
        return self._submit_sync(
            "delete_history_entry",
            lambda controller: controller.delete_history_entry(entry_id),
        )

    def clear_history(self) -> bool:
        return self._submit_sync(
            "clear_history", lambda controller: controller.clear_history()
        )

    def stop(self, timeout: float = 10.0) -> bool:
        """Request Core shutdown once and wait a bounded amount of time."""
        with self._lock:
            self._stop_requested = True
            self._accepting_commands = False
            loop = self._loop
            controller = self._controller
            thread = self._thread

        shutdown_future: Optional[Future] = None
        if (
            loop is not None
            and controller is not None
            and not loop.is_closed()
            and thread is not None
            and thread.is_alive()
        ):
            try:
                shutdown_future = asyncio.run_coroutine_threadsafe(
                    controller.shutdown(), loop
                )
                shutdown_future.result(timeout=max(0.1, timeout * 0.7))
            except Exception:
                logger.exception("Core shutdown request did not complete cleanly.")

        if thread is not None and thread.is_alive():
            thread.join(timeout=max(0.1, timeout * 0.3))

        stopped = thread is None or not thread.is_alive()
        if not stopped:
            logger.error("Core thread did not stop within %.1f seconds.", timeout)
        return stopped
