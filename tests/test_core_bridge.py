"""Threading and lifecycle tests for the Qt/asyncio Core bridge."""

from __future__ import annotations

import asyncio
import os
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, Qt, Slot
from PySide6.QtWidgets import QApplication

from core.config import AppConfig
from core.controller import (
    AvailabilityState,
    CommandResult,
    ControllerStatusSnapshot,
    DictationState,
    TransientEvent,
    TransientEventType,
)
from core.history import HistoryEntry
from core.event_models import CanonicalEventType, FeedbackSource, FeedbackState
from core.feedback_mapping import FeedbackRule
from core.feedback_reducer import FeedbackDecision
from core.reinsertion import ReinsertionResult, ReinsertionStatus
from ui.core_bridge import CoreBridge


def make_snapshot(revision=1):
    return ControllerStatusSnapshot(
        availability_state=AvailabilityState.READY,
        dictation_state=DictationState.IDLE,
        reason_code="ready",
        description="Ready",
        reconnect_attempt=0,
        next_retry_delay=None,
        session_id="session",
        generation=1,
        revision=revision,
        is_running=True,
        is_closing=False,
        queue_size=0,
    )


class FakeController:
    instances = []

    def __init__(self, config):
        self.config = config
        self.on_snapshot_change = None
        self.on_feedback_event = None
        self.on_feedback_decision = None
        self.on_text = None
        self.on_transport_change = None
        self._stop_event = asyncio.Event()
        self._closing = False
        self.initial_auto_start_requested = False
        self.thread_calls = []
        type(self).instances.append(self)

    @property
    def is_closing(self):
        return self._closing

    def get_snapshot(self):
        return make_snapshot()

    def request_initial_auto_start(self):
        self.initial_auto_start_requested = True

    async def run(self):
        self.thread_calls.append(("run", threading.get_ident()))
        if self.on_snapshot_change:
            self.on_snapshot_change(make_snapshot(2))
        if self.on_feedback_event:
            self.on_feedback_event(
                TransientEvent(
                    TransientEventType.ACTION_BLOCKED,
                    "transport_not_ready",
                    "blocked",
                    time.time(),
                )
            )
        if self.on_feedback_decision:
            self.on_feedback_decision(
                FeedbackDecision(
                    state=FeedbackState.IDLE,
                    source=FeedbackSource.LOCAL_ONLY,
                    rule=FeedbackRule(),
                )
            )
        if self.on_text:
            self.on_text(1, "Text", False)
        await self._stop_event.wait()

    async def shutdown(self):
        self.thread_calls.append(("shutdown", threading.get_ident()))
        self._closing = True
        self._stop_event.set()

    async def toggle_dictation(self):
        self.thread_calls.append(("toggle", threading.get_ident()))
        return CommandResult(True, "toggled")

    async def start_dictation(self):
        self.thread_calls.append(("start", threading.get_ident()))
        return CommandResult(True, "started")

    async def stop_dictation(self):
        self.thread_calls.append(("stop", threading.get_ident()))
        return CommandResult(True, "stopped")

    def reinsert_last(self):
        self.thread_calls.append(("reinsert_last", threading.get_ident()))
        return ReinsertionResult(ReinsertionStatus.QUEUED, entry_id="entry")

    def reinsert_entry(self, entry_id):
        self.thread_calls.append(("reinsert_entry", threading.get_ident()))
        return ReinsertionResult(ReinsertionStatus.QUEUED, entry_id=entry_id)

    def get_recent_entries(self, limit):
        self.thread_calls.append(("history", threading.get_ident()))
        return (
            HistoryEntry("entry", "s", 1, 1.0, "Text", 4),
        )[:limit]

    def report_local_feedback(self, event_type, details=None):
        self.thread_calls.append(
            ("local_feedback", threading.get_ident(), event_type, details)
        )


class Receiver(QObject):
    def __init__(self):
        super().__init__()
        self.snapshots = []
        self.feedback = []
        self.feedback_decisions = []
        self.text = []
        self.commands = []
        self.history = []
        self.callback_threads = []

    def _record(self):
        self.callback_threads.append(threading.get_ident())

    @Slot(object)
    def on_snapshot(self, value):
        self._record()
        self.snapshots.append(value)

    @Slot(object)
    def on_feedback(self, value):
        self._record()
        self.feedback.append(value)

    @Slot(object)
    def on_feedback_decision(self, value):
        self._record()
        self.feedback_decisions.append(value)

    @Slot(int, str, bool)
    def on_text(self, segment, text, final):
        self._record()
        self.text.append((segment, text, final))

    @Slot(str, object)
    def on_command(self, name, result):
        self._record()
        self.commands.append((name, result))

    @Slot(object)
    def on_history(self, entries):
        self._record()
        self.history.append(entries)


class TestCoreBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])
        cls.main_thread_id = threading.get_ident()

    def setUp(self):
        FakeController.instances.clear()
        self.bridge = CoreBridge(AppConfig(), controller_factory=FakeController)
        self.receiver = Receiver()
        queued = Qt.ConnectionType.QueuedConnection
        self.bridge.snapshot_changed.connect(self.receiver.on_snapshot, queued)
        self.bridge.feedback_received.connect(self.receiver.on_feedback, queued)
        self.bridge.feedback_decision_received.connect(
            self.receiver.on_feedback_decision,
            queued,
        )
        self.bridge.text_received.connect(self.receiver.on_text, queued)
        self.bridge.command_completed.connect(self.receiver.on_command, queued)
        self.bridge.history_received.connect(self.receiver.on_history, queued)

    def tearDown(self):
        self.bridge.stop(timeout=2.0)
        self.application.processEvents()

    def wait_until(self, predicate, timeout=2.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.application.processEvents()
            if predicate():
                return True
            time.sleep(0.005)
        self.application.processEvents()
        return bool(predicate())

    def test_controller_loop_is_worker_owned_and_signals_arrive_in_main(self):
        self.assertTrue(self.bridge.start())
        self.assertTrue(
            self.wait_until(
                lambda: self.receiver.snapshots
                and self.receiver.feedback
                and self.receiver.feedback_decisions
                and self.receiver.text
            )
        )
        controller = FakeController.instances[0]
        run_thread = dict(controller.thread_calls)["run"]

        self.assertEqual(run_thread, self.bridge.worker_thread_id)
        self.assertNotEqual(run_thread, self.main_thread_id)
        self.assertTrue(
            all(
                thread_id == self.main_thread_id
                for thread_id in self.receiver.callback_threads
            )
        )

    def test_async_and_sync_commands_execute_in_worker_loop(self):
        self.assertTrue(self.bridge.start())
        self.assertTrue(self.bridge.toggle_dictation())
        self.assertTrue(self.bridge.reinsert_last())
        self.assertTrue(self.bridge.reinsert_entry("chosen"))
        self.assertTrue(self.bridge.request_history(5))
        self.assertTrue(
            self.bridge.report_local_feedback(
                CanonicalEventType.CLIENT_SOUND_FAILED,
                {"category": "backend"},
            )
        )
        self.assertTrue(
            self.wait_until(
                lambda: len(self.receiver.commands) >= 3
                and len(self.receiver.history) >= 1
            )
        )

        controller = FakeController.instances[0]
        command_threads = {
            item[0]: item[1]
            for item in controller.thread_calls
            if item[0] in {"toggle", "reinsert_last", "reinsert_entry", "history"}
        }
        local_feedback = next(
            item for item in controller.thread_calls if item[0] == "local_feedback"
        )
        self.assertEqual(local_feedback[1], self.bridge.worker_thread_id)
        self.assertEqual(set(command_threads.values()), {self.bridge.worker_thread_id})
        self.assertEqual(self.receiver.history[0][0].id, "entry")

    def test_local_feedback_can_wait_until_worker_processed_it(self):
        self.assertTrue(self.bridge.start())

        self.assertTrue(
            self.bridge.report_local_feedback(
                CanonicalEventType.CLIENT_LIFECYCLE_STOPPING,
                wait_timeout=1.0,
            )
        )

        controller = FakeController.instances[0]
        local_feedback = [
            item for item in controller.thread_calls if item[0] == "local_feedback"
        ]
        self.assertEqual(len(local_feedback), 1)
        self.assertEqual(local_feedback[0][1], self.bridge.worker_thread_id)

    def test_command_before_start_and_after_stop_is_rejected_not_queued(self):
        self.assertFalse(self.bridge.toggle_dictation())
        self.assertTrue(self.wait_until(lambda: len(self.receiver.commands) == 1))
        self.assertEqual(
            self.receiver.commands[0][1].status,
            "core_unavailable",
        )

        self.assertTrue(self.bridge.start())
        self.assertTrue(self.bridge.stop(timeout=2.0))
        self.assertFalse(self.bridge.start_dictation())
        self.assertTrue(self.wait_until(lambda: len(self.receiver.commands) == 2))
        self.assertEqual(
            self.receiver.commands[-1][1].status,
            "core_unavailable",
        )

    def test_shutdown_is_idempotent_and_leaves_no_worker_thread(self):
        self.assertTrue(self.bridge.start())
        worker_id = self.bridge.worker_thread_id

        self.assertTrue(self.bridge.stop(timeout=2.0))
        self.assertTrue(self.bridge.stop(timeout=2.0))

        self.assertFalse(self.bridge.is_running)
        self.assertIsNone(self.bridge.worker_thread_id)
        self.assertNotIn(
            worker_id,
            [thread.ident for thread in threading.enumerate()],
        )

    def test_configured_auto_start_is_armed_before_run(self):
        self.bridge.config.hotkey.auto_start = True
        self.assertTrue(self.bridge.start())
        controller = FakeController.instances[0]
        self.assertTrue(self.wait_until(lambda: bool(controller.thread_calls)))
        self.assertTrue(controller.initial_auto_start_requested)
        self.assertEqual(controller.thread_calls[0][0], "run")

    def test_loop_close_race_rejects_command_without_escaping_runtime_error(self):
        self.assertTrue(self.bridge.start())
        loop = self.bridge._loop
        self.assertIsNotNone(loop)

        with patch.object(
            loop,
            "call_soon_threadsafe",
            side_effect=RuntimeError("loop already closed"),
        ):
            self.assertFalse(self.bridge.toggle_dictation())

        self.assertTrue(self.wait_until(lambda: len(self.receiver.commands) == 1))
        self.assertEqual(
            self.receiver.commands[0][1].status,
            "core_unavailable",
        )


if __name__ == "__main__":
    unittest.main()
