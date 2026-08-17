"""Thread-safe bridge between the Qt main thread and the asyncio core."""

from __future__ import annotations

import asyncio
from concurrent.futures import Future
import logging
import threading
import uuid
from typing import Callable, Optional

from PySide6.QtCore import QObject, Signal

from core.config import AppConfig
from core.controller import CommandResult, STTController
from core.event_models import CanonicalEventType
from core.observability.adapters.client_events import ClientEventEmitter
from core.observability.ingress import NULL_INGRESS
from core.reinsertion import ReinsertionResult, ReinsertionStatus

logger = logging.getLogger("ui.core_bridge")

ControllerFactory = Callable[[AppConfig], STTController]


class CoreBridge(QObject):
    """Own the Core thread and expose queued Qt signals and semantic commands."""

    snapshot_changed = Signal(object)
    feedback_received = Signal(object)
    feedback_decision_received = Signal(object)
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
        observability=NULL_INGRESS,
    ) -> None:
        super().__init__(parent)
        self.config = config
        self._observability = observability
        self._observe = ClientEventEmitter(observability, component="ui.core_bridge")
        # CONTRACTS §6: the default factory carries the ingress into the
        # controller, so ``ControllerFactory`` stays ``Callable[[AppConfig],
        # STTController]`` and an externally supplied factory keeps being
        # called with exactly one argument. Such a factory's controller then
        # holds NULL_INGRESS -- which is the documented, intended outcome.
        self._controller_factory = controller_factory or (
            lambda cfg: STTController(cfg, observability=observability)
        )
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
            controller.on_feedback_decision = self.feedback_decision_received.emit
            controller.on_text = self.text_received.emit
            controller.on_transport_change = self.transport_changed.emit

            with self._lock:
                self._loop = loop
                self._controller = controller
                self._worker_thread_id = threading.get_ident()
                self._accepting_commands = not self._stop_requested
                worker_id = self._worker_thread_id
            self._startup_event.set()
            # CONTRACTS §12.1: client.core.thread_started (P+S). The existing
            # logger lines stay untouched; this adds the structured half.
            self._observe.system(
                "client.core.thread_started",
                details={"thread_id": worker_id},
            )
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
            # Before the signals: this is the last statement of the Core
            # thread, and the record must exist even if a Qt slot on the other
            # side of ``core_stopped`` throws.
            self._observe.system(
                "client.core.thread_stopped",
                level="WARNING" if error_message else "INFO",
                details={
                    "requested": bool(self._stop_requested),
                    "failed": bool(error_message),
                },
            )
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

    # -- CONTRACTS §12.2: client.command.requested / .completed -----------
    #
    # One ``command_id`` per user command plus the derived ``correlation_id``
    # ``"command:<command_id>"`` (§1.1: a correlation id is always
    # "<namensraum>:<wert>"). Both records carry the same pair, which is what
    # makes "requested but never completed" a query rather than a guess.

    @staticmethod
    def _new_command_ids() -> tuple[str, str]:
        command_id = f"cmd-{uuid.uuid4().hex[:12]}"
        return command_id, f"command:{command_id}"

    def _observe_command_requested(
        self, name: str, command_id: str, correlation_id: str
    ) -> None:
        self._observe.audit(
            "client.command.requested",
            details={"command": name},
            command_id=command_id,
            correlation_id=correlation_id,
        )

    def _observe_command_completed(
        self,
        name: str,
        command_id: Optional[str],
        correlation_id: Optional[str],
        result: object,
    ) -> None:
        if command_id is None or correlation_id is None:
            return
        status = getattr(result, "status", None)
        status_text = getattr(status, "value", status)
        success = getattr(result, "success", None)
        if success is None:
            # ReinsertionResult has no ``success``; its status enum carries it.
            success = status_text == "queued"
        self._observe.audit(
            "client.command.completed",
            level="INFO" if success else "WARNING",
            details={
                "command": name,
                "status": str(status_text) if status_text is not None else None,
                "success": bool(success),
            },
            command_id=command_id,
            correlation_id=correlation_id,
        )

    def _reject_command(
        self,
        name: str,
        command_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> bool:
        result = CommandResult(
            success=False,
            status="core_unavailable",
            message="Core is not accepting commands",
        )
        self._observe_command_completed(name, command_id, correlation_id, result)
        self.command_completed.emit(name, result)
        return False

    def _submit_coroutine(self, name: str, method_name: str) -> bool:
        command_id, correlation_id = self._new_command_ids()
        self._observe_command_requested(name, command_id, correlation_id)
        loop, controller = self._get_target()
        if loop is None or controller is None or loop.is_closed():
            return self._reject_command(name, command_id, correlation_id)

        def invoke() -> None:
            try:
                method = getattr(controller, method_name)
                task = loop.create_task(method())
                task.add_done_callback(
                    lambda finished: self._finish_async_command(
                        name, finished, command_id, correlation_id
                    )
                )
            except Exception as exc:
                logger.exception("Failed to schedule Core command %s.", name)
                result = CommandResult(False, "schedule_failed", str(exc))
                self._observe_command_completed(
                    name, command_id, correlation_id, result
                )
                self.command_completed.emit(name, result)

        try:
            loop.call_soon_threadsafe(invoke)
            return True
        except RuntimeError:
            logger.info("Core loop closed while scheduling %s.", name)
            return self._reject_command(name, command_id, correlation_id)

    def _finish_async_command(
        self,
        name: str,
        task: asyncio.Task,
        command_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        try:
            result = task.result()
        except asyncio.CancelledError:
            result = CommandResult(False, "cancelled", "Command was cancelled")
        except Exception as exc:
            logger.exception("Core command %s failed.", name)
            result = CommandResult(False, "error", str(exc))
        self._observe_command_completed(name, command_id, correlation_id, result)
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

    def apply_runtime_config(
        self,
        candidate: AppConfig,
        *,
        settings_correlation_id: Optional[str] = None,
    ) -> bool:
        """``settings_correlation_id`` is the UI's per-attempt id from
        ``client.settings.apply_started``; it travels to the controller purely
        so ``client.settings.runtime_apply`` can carry the same value
        (CONTRACTS §12.2). It changes nothing about the apply."""
        command_id, correlation_id = self._new_command_ids()
        self._observe_command_requested(
            "apply_runtime_config", command_id, correlation_id
        )
        loop, controller = self._get_target()
        if loop is None or controller is None or loop.is_closed():
            return self._reject_command(
                "apply_runtime_config", command_id, correlation_id
            )

        def invoke() -> None:
            # The keyword is only passed when there is something to correlate,
            # so a controller double with the pre-OBS-040 one-argument
            # signature keeps working unchanged.
            task = loop.create_task(
                controller.apply_runtime_config(
                    candidate, correlation_id=settings_correlation_id
                )
                if settings_correlation_id is not None
                else controller.apply_runtime_config(candidate)
            )
            task.add_done_callback(
                lambda finished: self._finish_async_command(
                    "apply_runtime_config", finished, command_id, correlation_id
                )
            )

        try:
            loop.call_soon_threadsafe(invoke)
            return True
        except RuntimeError:
            return self._reject_command(
                "apply_runtime_config", command_id, correlation_id
            )

    def _submit_sync(
        self,
        name: str,
        callback: Callable[[STTController], object],
        *,
        history_result: bool = False,
    ) -> bool:
        # A history read is a query, not an intentional user action, so it is
        # not an audit command (CONTRACTS §2.2: audit is "vom Nutzer oder vom
        # Client absichtlich ausgeloeste Handlungen").
        command_id: Optional[str] = None
        correlation_id: Optional[str] = None
        if not history_result:
            command_id, correlation_id = self._new_command_ids()
            self._observe_command_requested(name, command_id, correlation_id)
        loop, controller = self._get_target()
        if loop is None or controller is None or loop.is_closed():
            if history_result:
                self.history_received.emit(())
                return False
            return self._reject_command(name, command_id, correlation_id)

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
                self._observe_command_completed(
                    name, command_id, correlation_id, result
                )
                self.command_completed.emit(name, result)

        try:
            loop.call_soon_threadsafe(invoke)
            return True
        except RuntimeError:
            logger.info("Core loop closed while scheduling %s.", name)
            if history_result:
                self.history_received.emit(())
                return False
            return self._reject_command(name, command_id, correlation_id)

    def set_microphone_muted(self, muted: bool) -> bool:
        return self._submit_sync(
            "set_microphone_muted",
            lambda controller: controller.set_microphone_muted(muted),
        )

    def reconnect_server(self) -> bool:
        command_id, correlation_id = self._new_command_ids()
        self._observe_command_requested("reconnect_server", command_id, correlation_id)
        loop, controller = self._get_target()
        if loop is None or controller is None or loop.is_closed():
            return self._reject_command("reconnect_server", command_id, correlation_id)

        def invoke() -> None:
            task = loop.create_task(controller.reconnect_server())
            task.add_done_callback(
                lambda finished: self._finish_async_command(
                    "reconnect_server", finished, command_id, correlation_id
                )
            )

        try:
            loop.call_soon_threadsafe(invoke)
            return True
        except RuntimeError:
            return self._reject_command("reconnect_server", command_id, correlation_id)

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

    def report_local_feedback(
        self,
        event_type: CanonicalEventType,
        details: Optional[dict[str, object]] = None,
        *,
        wait_timeout: Optional[float] = None,
    ) -> bool:
        """Queue a local fact, optionally waiting until the Core processed it."""
        loop, controller = self._get_target()
        if loop is None or controller is None or loop.is_closed():
            return False
        completed = threading.Event() if wait_timeout is not None else None
        succeeded = True

        def invoke() -> None:
            nonlocal succeeded
            try:
                controller.report_local_feedback(event_type, details)
            except Exception:
                succeeded = False
                logger.exception("Failed to report local feedback %s.", event_type)
            finally:
                if completed is not None:
                    completed.set()

        if threading.get_ident() == self.worker_thread_id:
            invoke()
            return succeeded

        try:
            loop.call_soon_threadsafe(invoke)
        except RuntimeError:
            logger.info("Core loop closed while reporting local feedback.")
            return False
        if completed is None:
            return True
        if not completed.wait(max(0.0, float(wait_timeout))):
            logger.warning(
                "Timed out reporting local feedback %s.", event_type.value
            )
            return False
        return succeeded

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
