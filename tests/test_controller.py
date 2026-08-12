"""
Unit and integration tests for STTController (AP04 Controller Integration).
"""

from __future__ import annotations

import asyncio
import contextlib
import os
import shutil
import tempfile
import threading
import unittest
from typing import List, Optional, Tuple
from unittest.mock import patch

from core.config import AppConfig, HistoryConfig, HistoryMemoryConfig, HistoryPersistentConfig
from core.controller import (
    AvailabilityState,
    DictationState,
    STTController,
    FinalProcessingStatus,
    FinalProcessingResult,
    TransientEventType,
)
from core.history import (
    TranscriptHistoryManager,
    HistoryEntry,
)
from core.text_injector import (
    TextInjectionQueue,
    WindowsInjectionBackend,
    QueueState,
)
from core.reinsertion import (
    TranscriptReinsertionService,
    ReinsertionResult,
    ReinsertionStatus,
)
from core.stt_session import TransportState, ClientState, SessionState


class FakeWindowsBackend(WindowsInjectionBackend):
    """Fake Win32 backend for testing TextInjectionQueue without real OS calls."""

    def __init__(self) -> None:
        self.owner_hwnd = 1001
        self.created = False
        self.destroyed = False
        self.fail_create = False
        self.open_retries_fail = False

    def create_owner_window(self) -> None:
        if self.fail_create:
            raise RuntimeError("Fake create_owner_window failed")
        self.created = True

    def destroy_owner_window(self) -> None:
        self.destroyed = True

    def get_owner_window(self) -> int:
        return self.owner_hwnd if self.created else 0

    def open_clipboard(self, hwnd: int) -> bool:
        return not self.open_retries_fail

    def close_clipboard(self) -> bool:
        return True

    def empty_clipboard(self) -> bool:
        return True

    def is_format_available(self, format_id: int) -> bool:
        return True

    def get_clipboard_data_unicode(self) -> Optional[str]:
        return "previous_clipboard"

    def set_clipboard_data_unicode(self, text: str) -> bool:
        return True

    def get_clipboard_sequence_number(self) -> int:
        return 42

    def get_foreground_window(self) -> int:
        return 2002

    def get_window_thread_process_id(self, hwnd: int) -> Tuple[int, int]:
        return (100, 200)

    def send_input_keyboard(self, events: List[Tuple[int, bool]]) -> int:
        return len(events)


class FakeInjectionQueue:
    """Controllable fake queue that tracks lifecycle calls without spawning real OS threads."""

    def __init__(self, is_running_val: bool = True) -> None:
        self.start_calls = 0
        self.stop_calls = 0
        self.enqueue_calls = []
        self._running = is_running_val
        self.fail_start = False
        self.timeout_on_stop = False
        self.history_manager = None

    def start(self) -> None:
        self.start_calls += 1
        if self.fail_start:
            self._running = False
            raise RuntimeError("Fake queue start failed")
        self._running = True

    def stop(self, timeout: Optional[float] = None) -> None:
        self.stop_calls += 1
        if not self.timeout_on_stop:
            self._running = False

    def enqueue(self, entry: HistoryEntry) -> bool:
        self.enqueue_calls.append(entry)
        return self._running

    def is_running(self) -> bool:
        return self._running

    def queue_size(self) -> int:
        return len(self.enqueue_calls)


class FakeAudioCapture:
    def __init__(self) -> None:
        self.start_calls = 0
        self.stop_calls = 0
        self.on_audio_packet = None
        self._running = False
        self._muted = False

    @property
    def muted(self) -> bool:
        return self._muted

    def set_muted(self, muted: bool) -> None:
        self._muted = bool(muted)

    def start(self) -> None:
        self.start_calls += 1
        self._running = True

    def stop(self) -> None:
        self.stop_calls += 1
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running


class FakeSTTSession:
    def __init__(self) -> None:
        self.start_calls = 0
        self.stop_calls = 0
        self.on_event = None
        self.on_transport_change = None
        self.on_state_change = None
        self.on_text = None
        self.generation = 1
        self.state = ClientState(
            transport=TransportState.READY,
            ready_ok=True,
            server_status=SessionState.IDLE,
            generation=self.generation,
            session_id="fake-session",
        )
        self._streaming = False
        self.send_start_should_fail = False
        self.invalidate_calls = []
        self.last_failure_reason = ""
        self.is_server_busy = False
        self.reconnect_attempt = 0
        self.next_retry_delay = None
        self.audio_packets = []

    @property
    def is_ready(self) -> bool:
        return self.state.transport == TransportState.READY and self.state.ready_ok

    @property
    def is_streaming(self) -> bool:
        return self._streaming

    def set_streaming(self, streaming: bool) -> None:
        self._streaming = streaming

    async def run(self) -> None:
        pass

    async def stop(self) -> None:
        self.stop_calls += 1
        self._streaming = False

    async def send_start(self) -> None:
        self.start_calls += 1
        if self.send_start_should_fail:
            raise RuntimeError("send_start simulated failure")
        self.state = ClientState(
            transport=self.state.transport,
            ready_ok=self.state.ready_ok,
            server_status=SessionState.LISTENING,
            generation=self.generation,
            session_id=self.state.session_id,
        )
        if self.on_state_change:
            self.on_state_change(self.state)
        if self.on_event:
            self.on_event(
                "status",
                {
                    "type": "status",
                    "state": "listening",
                    "sessionId": self.state.session_id,
                    "_clientGeneration": self.generation,
                },
            )

    async def send_stop(self) -> None:
        self.stop_calls += 1
        self._streaming = False

    async def send_audio(self, pcm_data: bytes, sample_rate: int, channels: int = 1, frames: Optional[int] = None) -> None:
        self.audio_packets.append((pcm_data, sample_rate, channels, frames))

    async def invalidate_connection(self, reason: str = "connection_recycle") -> None:
        self.invalidate_calls.append(reason)
        self._streaming = False


class FakeSessionCoordinator:
    def __init__(self) -> None:
        self.on_event = None
        self.on_context_change = None
        self.begin_calls = []
        self.invalidate_calls = []
        self.hello_calls = []
        self.config_updates = []
        self.shutdown_calls = 0

    async def begin_generation(self, generation: int) -> bool:
        self.begin_calls.append(generation)
        return True

    async def invalidate_generation(self, generation: int) -> bool:
        self.invalidate_calls.append(generation)
        return True

    async def adopt_hello(self, generation: int, event: dict) -> bool:
        self.hello_calls.append((generation, event["sessionId"]))
        return True

    async def update_config(self, server_config, event_config) -> None:
        self.config_updates.append((server_config, event_config))

    async def shutdown(self) -> None:
        self.shutdown_calls += 1


class BaseControllerTestCase(unittest.TestCase):
    """Base class providing isolated temporary database storage & worker leak checking."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_controller_history.db")

        self.config = AppConfig()
        self.config.history.persistent.db_path = self.db_path

        self.backend = FakeWindowsBackend()
        self.history_mgr = TranscriptHistoryManager(self.config.history, db_path=self.db_path)
        self.queue = TextInjectionQueue(self.config, self.history_mgr, self.backend)
        self.reinsertion = TranscriptReinsertionService(self.history_mgr, self.queue)
        self.audio = FakeAudioCapture()
        self.session = FakeSTTSession()

        self.controller = STTController(
            self.config,
            session=self.session,
            audio=self.audio,
            history_manager=self.history_mgr,
            injection_queue=self.queue,
            reinsertion_service=self.reinsertion,
            backend=self.backend,
        )

        self._initial_threads = set(threading.enumerate())

    def tearDown(self) -> None:
        if self.controller.is_running or not self.controller.is_closing:
            asyncio.run(self.controller.shutdown())

        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass

        current_threads = set(threading.enumerate())
        new_workers = [t for t in (current_threads - self._initial_threads) if "TextInjectionQueueWorker" in t.name]
        self.assertEqual(len(new_workers), 0, f"Leaked worker threads detected: {new_workers}")


class TestSTTControllerWiringAndLifecycle(BaseControllerTestCase):
    def test_queue_and_reinsertion_share_same_history_instance(self) -> None:
        self.assertIs(self.controller.queue.history_manager, self.controller.history)
        self.assertIs(self.controller.reinsertion.history_manager, self.controller.history)
        self.assertIs(self.controller.reinsertion.injection_queue, self.controller.queue)

    def test_rejects_injected_queue_with_different_history_instance(self) -> None:
        mismatched_queue = FakeInjectionQueue()
        mismatched_queue.history_manager = object()

        with self.assertRaisesRegex(ValueError, "same history manager"):
            STTController(
                self.config,
                history_manager=self.history_mgr,
                injection_queue=mismatched_queue,
            )

    def test_rejects_injected_reinsertion_with_different_dependencies(self) -> None:
        fake_queue = FakeInjectionQueue()
        mismatched_reinsertion = TranscriptReinsertionService(
            TranscriptHistoryManager(
                HistoryConfig(persistent=HistoryPersistentConfig(enabled=False))
            ),
            fake_queue,
        )

        with self.assertRaisesRegex(ValueError, "same history manager"):
            STTController(
                self.config,
                history_manager=self.history_mgr,
                injection_queue=fake_queue,
                reinsertion_service=mismatched_reinsertion,
            )

    def test_start_queue_activates_worker_and_prevents_double_start(self) -> None:
        self.assertFalse(self.controller.is_running)
        self.controller.start_queue()
        self.assertTrue(self.controller.is_running)
        self.assertTrue(self.controller.queue.is_running())

        self.controller.start_queue()
        self.assertTrue(self.controller.is_running)

    def test_start_partial_failure_cleans_up_already_started_components(self) -> None:
        fake_q = FakeInjectionQueue()
        fake_q.fail_start = True

        cntr = STTController(self.config, injection_queue=fake_q, history_manager=self.history_mgr)
        with self.assertRaises(RuntimeError):
            cntr.start_queue()

        self.assertFalse(cntr.is_running)
        self.assertEqual(fake_q.stop_calls, 1)

    def test_shutdown_is_idempotent_and_stops_components_exactly_once(self) -> None:
        fake_q = FakeInjectionQueue()
        fake_audio = FakeAudioCapture()
        fake_sess = FakeSTTSession()

        cntr = STTController(
            self.config,
            session=fake_sess,
            audio=fake_audio,
            history_manager=self.history_mgr,
            injection_queue=fake_q,
        )
        cntr.start_queue()
        self.assertTrue(cntr.is_running)

        asyncio.run(cntr.shutdown())
        self.assertFalse(cntr.is_running)
        self.assertTrue(cntr.is_closing)
        self.assertEqual(fake_audio.stop_calls, 1)
        self.assertEqual(fake_sess.stop_calls, 1)
        self.assertEqual(fake_q.stop_calls, 1)

        asyncio.run(cntr.shutdown())
        self.assertEqual(fake_audio.stop_calls, 1)
        self.assertEqual(fake_sess.stop_calls, 1)
        self.assertEqual(fake_q.stop_calls, 1)

    def test_shutdown_raises_queue_stop_timeout_with_fake(self) -> None:
        fake_q = FakeInjectionQueue()
        fake_q.timeout_on_stop = True

        cntr = STTController(
            self.config,
            history_manager=self.history_mgr,
            injection_queue=fake_q,
        )
        cntr.start_queue()

        with self.assertRaises(TimeoutError):
            asyncio.run(cntr.shutdown())

    def test_no_new_finals_accepted_during_closing(self) -> None:
        self.controller.start_queue()
        asyncio.run(self.controller.shutdown())

        event = {"type": "final", "sessionId": "s1", "segmentId": 1, "text": "Hello"}
        res = self.controller.handle_server_event("final", event)
        self.assertIsNone(res)

        res_direct = self.controller.process_raw_final_event(event)
        self.assertEqual(res_direct.status, FinalProcessingStatus.INVALID_FINAL)
        self.assertEqual(res_direct.reason, "closing")


class TestSTTControllerDualSessionLifecycle(unittest.IsolatedAsyncioTestCase):
    def make_controller(self):
        config = AppConfig()
        config.history.persistent.enabled = False
        history = TranscriptHistoryManager(config.history)
        queue = FakeInjectionQueue()
        session = FakeSTTSession()
        coordinator = FakeSessionCoordinator()
        controller = STTController(
            config,
            session=session,
            audio=FakeAudioCapture(),
            history_manager=history,
            injection_queue=queue,
            session_coordinator=coordinator,
        )
        return controller, session, coordinator

    async def test_transport_and_hello_callbacks_share_generation(self) -> None:
        controller, session, coordinator = self.make_controller()
        controller._loop = asyncio.get_running_loop()

        controller._handle_transport_change(TransportState.CONNECTING)
        controller.handle_server_event(
            "hello",
            {
                "type": "hello",
                "sessionId": session.state.session_id,
                "_clientGeneration": session.generation,
            },
        )
        await asyncio.sleep(0)

        self.assertEqual(coordinator.begin_calls, [session.generation])
        self.assertEqual(
            coordinator.hello_calls,
            [(session.generation, session.state.session_id)],
        )
        await controller.shutdown()

    async def test_disconnect_invalidates_event_session_and_shutdown_is_once(self) -> None:
        controller, session, coordinator = self.make_controller()
        controller._loop = asyncio.get_running_loop()
        controller.start_queue()

        controller._handle_transport_change(TransportState.DISCONNECTED)
        await asyncio.sleep(0)
        await asyncio.gather(
            controller.shutdown(),
            controller.shutdown(),
            controller.shutdown(),
        )

        self.assertEqual(coordinator.invalidate_calls, [session.generation])
        self.assertEqual(coordinator.shutdown_calls, 1)
        self.assertEqual(session.stop_calls, 1)


class TestSTTControllerRunLoopAndConcurrentShutdown(unittest.IsolatedAsyncioTestCase):
    async def test_auto_start_completion_does_not_terminate_run_loop(self) -> None:
        config = AppConfig()
        config.history.persistent.enabled = False
        session = FakeSTTSession()
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()
        history_mgr = TranscriptHistoryManager(config.history)

        session_running_event = asyncio.Event()

        async def session_run() -> None:
            session_running_event.set()
            await asyncio.Future()

        session.run = session_run

        cntr = STTController(config, session=session, audio=audio, history_manager=history_mgr, injection_queue=fake_q)
        cntr.request_initial_auto_start()

        run_task = asyncio.create_task(cntr.run())

        await session_running_event.wait()
        await asyncio.sleep(0.15)

        self.assertEqual(audio.start_calls, 1)
        self.assertEqual(session.start_calls, 1)
        self.assertFalse(run_task.done())

        run_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await run_task

    async def test_partial_task_creation_failure_cleans_up_created_tasks_and_loop(self) -> None:
        config = AppConfig()
        config.history.persistent.enabled = False
        session = FakeSTTSession()
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()
        history_mgr = TranscriptHistoryManager(config.history)

        cntr = STTController(config, session=session, audio=audio, history_manager=history_mgr, injection_queue=fake_q)

        real_create_task = asyncio.create_task
        create_calls = 0

        def fail_third_create_task(coro):
            nonlocal create_calls
            create_calls += 1
            if create_calls == 3:
                coro.close()
                raise RuntimeError("Task creation 3 failed")
            return real_create_task(coro)

        with patch("core.controller.asyncio.create_task", side_effect=fail_third_create_task):
            with self.assertRaisesRegex(RuntimeError, "Task creation 3 failed"):
                await cntr.run()

        self.assertEqual(create_calls, 3)
        self.assertIsNone(cntr._loop)
        self.assertEqual(fake_q.stop_calls, 1)

    async def test_second_task_creation_failure_cleans_up_first_task(self) -> None:
        config = AppConfig()
        config.history.persistent.enabled = False
        session = FakeSTTSession()
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()
        cntr = STTController(
            config,
            session=session,
            audio=audio,
            injection_queue=fake_q,
        )

        async def blocking_session_run() -> None:
            await asyncio.Future()

        session.run = blocking_session_run
        real_create_task = asyncio.create_task
        create_calls = 0
        created_tasks = []

        def fail_second_create_task(coro):
            nonlocal create_calls
            create_calls += 1
            if create_calls == 2:
                coro.close()
                raise RuntimeError("Task creation 2 failed")
            task = real_create_task(coro)
            created_tasks.append(task)
            return task

        with patch("core.controller.asyncio.create_task", side_effect=fail_second_create_task):
            with self.assertRaisesRegex(RuntimeError, "Task creation 2 failed"):
                await cntr.run()

        self.assertEqual(create_calls, 2)
        self.assertEqual(len(created_tasks), 1)
        self.assertTrue(created_tasks[0].done())
        self.assertTrue(created_tasks[0].cancelled())
        self.assertIsNone(cntr._loop)
        self.assertEqual(fake_q.stop_calls, 1)

    async def test_queue_start_failure_resets_loop_to_none(self) -> None:
        config = AppConfig()
        config.history.persistent.enabled = False
        fake_q = FakeInjectionQueue()
        fake_q.fail_start = True
        session = FakeSTTSession()
        audio = FakeAudioCapture()

        cntr = STTController(
            config,
            session=session,
            audio=audio,
            injection_queue=fake_q,
        )

        with self.assertRaises(RuntimeError):
            await cntr.run()

        self.assertIsNone(cntr._loop)
        self.assertEqual(fake_q.stop_calls, 1)

    async def test_auto_start_failure_keeps_background_controller_alive(self) -> None:
        config = AppConfig()
        config.history.persistent.enabled = False
        session = FakeSTTSession()
        session.send_start_should_fail = True
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()

        async def blocking_session_run() -> None:
            await asyncio.Future()

        session.run = blocking_session_run

        cntr = STTController(config, session=session, audio=audio, injection_queue=fake_q)
        cntr.request_initial_auto_start()

        run_task = asyncio.create_task(cntr.run())
        for _ in range(50):
            if session.start_calls:
                break
            await asyncio.sleep(0.01)

        self.assertEqual(session.start_calls, 1)
        self.assertFalse(run_task.done())
        run_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await run_task

        self.assertEqual(audio.start_calls, 1)
        self.assertEqual(audio.stop_calls, 2)  # Rollback on start failure + shutdown audio stop
        self.assertFalse(cntr.dictation_requested)
        self.assertIsNone(cntr._loop)

    async def test_unexpected_helper_cancellation_is_reported(self) -> None:
        config = AppConfig()
        config.history.persistent.enabled = False
        session = FakeSTTSession()
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()

        async def blocking_session_run() -> None:
            await asyncio.Future()

        async def self_cancelling_audio_sender() -> None:
            current_task = asyncio.current_task()
            self.assertIsNotNone(current_task)
            current_task.cancel()
            await asyncio.sleep(0)

        session.run = blocking_session_run
        cntr = STTController(
            config,
            session=session,
            audio=audio,
            injection_queue=fake_q,
        )
        cntr._audio_sender = self_cancelling_audio_sender

        with self.assertRaisesRegex(RuntimeError, "cancelled unexpectedly"):
            await cntr.run()

        self.assertIsNone(cntr._loop)
        self.assertEqual(fake_q.stop_calls, 1)

    async def test_wake_word_run_loop_does_not_treat_background_start_as_initial_auto_start(self) -> None:
        config = AppConfig()
        config.history.persistent.enabled = False
        config.session.mode = "wake_word"
        session = FakeSTTSession()
        session.state = ClientState(
            transport=TransportState.CONNECTING,
            ready_ok=False,
            server_status=SessionState.UNKNOWN,
            generation=session.generation,
            session_id="fake-session",
        )
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()

        ready_event = asyncio.Event()

        async def delayed_ready_session_run() -> None:
            await asyncio.sleep(0.205)
            session.state = ClientState(
                transport=TransportState.READY,
                ready_ok=True,
                server_status=SessionState.IDLE,
                generation=session.generation,
                session_id="fake-session",
            )
            if session.on_transport_change:
                session.on_transport_change(TransportState.READY)
            ready_event.set()
            await asyncio.Future()

        session.run = delayed_ready_session_run

        cntr = STTController(
            config,
            session=session,
            audio=audio,
            injection_queue=fake_q,
        )

        run_task = asyncio.create_task(cntr.run())
        await asyncio.wait_for(ready_event.wait(), timeout=1.0)
        await asyncio.sleep(0.25)

        self.assertEqual(session.start_calls, 1)
        self.assertEqual(cntr.dictation_state, DictationState.ACTIVE)
        self.assertTrue(cntr.dictation_requested)
        self.assertFalse(run_task.done())

        run_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await run_task

    async def test_shutdown_shield_cancellation_preserves_cleanup_for_other_waiters(self) -> None:
        config = AppConfig()
        config.history.persistent.enabled = False
        session = FakeSTTSession()
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()

        cntr = STTController(config, session=session, audio=audio, injection_queue=fake_q)
        cntr.start_queue()

        stop_entered_event = asyncio.Event()
        stop_block_event = asyncio.Event()

        async def blocking_session_stop() -> None:
            stop_entered_event.set()
            await stop_block_event.wait()
            session.stop_calls += 1

        session.stop = blocking_session_stop

        # Caller 1 starts shutdown
        t1 = asyncio.create_task(cntr.shutdown())
        await asyncio.wait_for(stop_entered_event.wait(), timeout=1.0)

        # Caller 2 also calls shutdown
        t2 = asyncio.create_task(cntr.shutdown())
        await asyncio.sleep(0)

        # Cancel caller 1
        t1.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await t1

        # Unblock session.stop
        stop_block_event.set()

        # Caller 2 MUST complete successfully
        await t2

        self.assertEqual(audio.stop_calls, 1)
        self.assertEqual(session.stop_calls, 1)
        self.assertEqual(fake_q.stop_calls, 1)

    async def test_shutdown_serializes_with_inflight_start_transition(self) -> None:
        config = AppConfig()
        config.history.persistent.enabled = False
        session = FakeSTTSession()
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()
        cntr = STTController(
            config,
            session=session,
            audio=audio,
            injection_queue=fake_q,
        )
        cntr.start_queue()

        start_entered = asyncio.Event()
        release_start = asyncio.Event()

        async def blocking_send_start() -> None:
            session.start_calls += 1
            start_entered.set()
            await release_start.wait()
            session._streaming = True
            session.state = ClientState(
                transport=session.state.transport,
                ready_ok=session.state.ready_ok,
                server_status=SessionState.LISTENING,
                generation=session.generation,
                session_id="fake-session",
            )
            if session.on_state_change:
                session.on_state_change(session.state)
            if session.on_event:
                session.on_event(
                    "status",
                    {
                        "type": "status",
                        "state": "listening",
                        "sessionId": session.state.session_id,
                        "_clientGeneration": session.generation,
                    },
                )

        session.send_start = blocking_send_start

        start_task = asyncio.create_task(cntr.start_dictation())
        await asyncio.wait_for(start_entered.wait(), timeout=1.0)

        shutdown_task = asyncio.create_task(cntr.shutdown())
        await asyncio.sleep(0)
        self.assertTrue(cntr.is_closing)

        release_start.set()
        start_result = await start_task
        await shutdown_task

        self.assertFalse(start_result.success)
        self.assertEqual(start_result.status, "closing")
        self.assertEqual(audio.start_calls, 1)
        self.assertEqual(audio.stop_calls, 1)
        self.assertEqual(session.start_calls, 1)
        self.assertEqual(session.stop_calls, 1)
        self.assertFalse(session.is_streaming)


class TestSTTControllerFinalAndDeduplication(BaseControllerTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller.start_queue()

    def test_valid_final_creates_history_entry_and_enqueues(self) -> None:
        results = []
        self.controller.on_final_result = results.append

        event = {"type": "final", "sessionId": "sess_1", "segmentId": 10, "text": "First test transcription"}
        res = self.controller.handle_server_event("final", event)

        self.assertIsNotNone(res)
        self.assertEqual(res.status, FinalProcessingStatus.QUEUED)
        self.assertEqual(res.session_id, "sess_1")
        self.assertEqual(res.segment_id, 10)
        self.assertEqual(res.text, "First test transcription")
        self.assertIsNotNone(res.entry_id)

        entries = self.controller.history.get_memory_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].id, res.entry_id)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], res)

    def test_identical_duplicate_final_is_deduplicated_without_second_enqueue(self) -> None:
        event = {"type": "final", "sessionId": "sess_1", "segmentId": 10, "text": "Duplicate test"}

        res1 = self.controller.handle_server_event("final", event)
        self.assertEqual(res1.status, FinalProcessingStatus.QUEUED)

        res2 = self.controller.handle_server_event("final", event)
        self.assertEqual(res2.status, FinalProcessingStatus.DEDUPLICATED)
        self.assertFalse(res2.is_conflict)

        entries = self.controller.history.get_memory_entries()
        self.assertEqual(len(entries), 1)

    def test_contradictory_duplicate_final_reports_conflict_without_second_enqueue(self) -> None:
        event1 = {"type": "final", "sessionId": "sess_1", "segmentId": 10, "text": "Text version A"}
        event2 = {"type": "final", "sessionId": "sess_1", "segmentId": 10, "text": "Text version B"}

        res1 = self.controller.handle_server_event("final", event1)
        self.assertEqual(res1.status, FinalProcessingStatus.QUEUED)

        res2 = self.controller.handle_server_event("final", event2)
        self.assertEqual(res2.status, FinalProcessingStatus.DEDUPLICATED)
        self.assertTrue(res2.is_conflict)

        entries = self.controller.history.get_memory_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].text, "Text version A")

    def test_preexisting_db_history_duplicate_is_not_auto_enqueued(self) -> None:
        pre_entry = self.history_mgr.add_entry("sess_db", 99, "DB pre-existing text")
        self.assertIsNotNone(pre_entry)

        cntr = STTController(
            self.config,
            history_manager=self.history_mgr,
            injection_queue=self.queue,
        )
        cntr.start_queue()

        event = {"type": "final", "sessionId": "sess_db", "segmentId": 99, "text": "DB pre-existing text"}
        res = cntr.handle_server_event("final", event)

        self.assertEqual(res.status, FinalProcessingStatus.DEDUPLICATED)
        self.assertEqual(res.reason, "preexisting_duplicate")
        self.assertEqual(res.entry_id, pre_entry.id)
        self.assertFalse(res.is_conflict)

    def test_evicted_history_duplicate_classified_as_deduplicated(self) -> None:
        config = HistoryConfig(
            enabled=True,
            memory=HistoryMemoryConfig(max_entries=1),
            persistent=HistoryPersistentConfig(enabled=False),
        )
        hm = TranscriptHistoryManager(config)
        fake_q = FakeInjectionQueue()

        cntr = STTController(self.config, history_manager=hm, injection_queue=fake_q)
        cntr.start_queue()

        res1 = hm.add_entry_with_status("s", 1, "Text 1")
        res2 = hm.add_entry_with_status("s", 2, "Text 2")
        self.assertEqual(res1.status.value, "new")
        self.assertEqual(res2.status.value, "new")

        event = {"type": "final", "sessionId": "s", "segmentId": 1, "text": "Text 1"}
        res = cntr.handle_server_event("final", event)

        self.assertEqual(res.status, FinalProcessingStatus.DEDUPLICATED)
        self.assertEqual(res.reason, "duplicate_entry_evicted")
        self.assertIsNone(res.entry_id)

    def test_atomic_reservation_race_prevents_duplicate_history_calls(self) -> None:
        history_calls = []
        enter_event = threading.Event()
        unblock_event = threading.Event()

        class SlowFailingHistory(TranscriptHistoryManager):
            def add_entry_with_status(self, session_id, segment_id, text, timestamp=None):
                history_calls.append(text)
                enter_event.set()
                unblock_event.wait(timeout=2.0)
                raise RuntimeError("History failure simulated")

        history_config = HistoryConfig(enabled=True, persistent=HistoryPersistentConfig(enabled=False))
        slow_hm = SlowFailingHistory(history_config)
        cntr = STTController(self.config, history_manager=slow_hm, injection_queue=FakeInjectionQueue())

        event = {"type": "final", "sessionId": "race_sess", "segmentId": 1, "text": "Race text"}

        results = []

        def call_1():
            results.append(cntr.handle_server_event("final", event))

        def call_2():
            enter_event.wait(timeout=2.0)
            results.append(cntr.handle_server_event("final", event))

        t1 = threading.Thread(target=call_1)
        t2 = threading.Thread(target=call_2)

        t1.start()
        t2.start()

        enter_event.wait(timeout=2.0)
        unblock_event.set()

        t1.join(timeout=2.0)
        t2.join(timeout=2.0)

        self.assertEqual(len(history_calls), 1)
        statuses = [r.status for r in results]
        self.assertIn(FinalProcessingStatus.HISTORY_UNAVAILABLE, statuses)
        self.assertIn(FinalProcessingStatus.DEDUPLICATED, statuses)

    def test_shutdown_starting_during_validation_prevents_final_reservation(self) -> None:
        first_closing_check_reached = threading.Event()
        release_first_check = threading.Event()

        class GatedController(STTController):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._gate_first_closing_check = True

            @property
            def is_closing(self) -> bool:
                if self._gate_first_closing_check:
                    self._gate_first_closing_check = False
                    first_closing_check_reached.set()
                    release_first_check.wait(timeout=2.0)
                    return False
                return super().is_closing

        fake_q = FakeInjectionQueue()
        cntr = GatedController(
            self.config,
            session=FakeSTTSession(),
            audio=FakeAudioCapture(),
            history_manager=self.history_mgr,
            injection_queue=fake_q,
        )
        event = {
            "type": "final",
            "sessionId": "closing_race",
            "segmentId": 1,
            "text": "Must not be accepted",
        }
        results = []

        worker = threading.Thread(
            target=lambda: results.append(cntr.process_raw_final_event(event))
        )
        worker.start()
        self.assertTrue(first_closing_check_reached.wait(timeout=2.0))

        with cntr._lock:
            cntr._closing = True
        release_first_check.set()
        worker.join(timeout=2.0)

        self.assertFalse(worker.is_alive())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, FinalProcessingStatus.INVALID_FINAL)
        self.assertEqual(results[0].reason, "closing")
        self.assertEqual(fake_q.enqueue_calls, [])
        matching_entries = [
            entry
            for entry in self.history_mgr.get_memory_entries()
            if entry.session_id == "closing_race" and entry.segment_id == 1
        ]
        self.assertEqual(matching_entries, [])

    def test_same_segment_id_in_different_session_is_processed_separately(self) -> None:
        event_s1 = {"type": "final", "sessionId": "sess_A", "segmentId": 5, "text": "Session A Text"}
        event_s2 = {"type": "final", "sessionId": "sess_B", "segmentId": 5, "text": "Session B Text"}

        res1 = self.controller.handle_server_event("final", event_s1)
        res2 = self.controller.handle_server_event("final", event_s2)

        self.assertEqual(res1.status, FinalProcessingStatus.QUEUED)
        self.assertEqual(res2.status, FinalProcessingStatus.QUEUED)

        entries = self.controller.history.get_memory_entries()
        self.assertEqual(len(entries), 2)

    def test_invalid_final_fields_are_rejected(self) -> None:
        res1 = self.controller.process_raw_final_event({"type": "final", "sessionId": "", "segmentId": 1, "text": "T"})
        self.assertEqual(res1.status, FinalProcessingStatus.INVALID_FINAL)

        res2 = self.controller.process_raw_final_event({"type": "final", "sessionId": "s", "segmentId": True, "text": "T"})
        self.assertEqual(res2.status, FinalProcessingStatus.INVALID_FINAL)

        res3 = self.controller.process_raw_final_event({"type": "final", "sessionId": "s", "segmentId": -1, "text": "T"})
        self.assertEqual(res3.status, FinalProcessingStatus.INVALID_FINAL)

        res4 = self.controller.process_raw_final_event({"type": "final", "sessionId": "s", "segmentId": 1, "text": "   "})
        self.assertEqual(res4.status, FinalProcessingStatus.INVALID_FINAL)

    def test_non_final_events_do_not_produce_history_or_enqueue(self) -> None:
        rt_event = {"type": "realtime", "sessionId": "s", "segmentId": 1, "text": "Realtime text"}
        res1 = self.controller.handle_server_event("realtime", rt_event)
        self.assertIsNone(res1)

        timeline_event = {"type": "timeline", "event": "final_transcript", "sessionId": "s", "segmentId": 1, "text": "T"}
        res2 = self.controller.handle_server_event("timeline", timeline_event)
        self.assertIsNone(res2)

        entries = self.controller.history.get_memory_entries()
        self.assertEqual(len(entries), 0)


class TestSTTControllerConcurrencyAndLockSafety(BaseControllerTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller.start_queue()

    def test_callback_querying_controller_status_does_not_deadlock(self) -> None:
        status_observed = []

        def lock_querying_callback(res):
            st = self.controller.get_status()
            status_observed.append(st)

        self.controller.on_final_result = lock_querying_callback

        event1 = {"type": "final", "sessionId": "s_lock", "segmentId": 1, "text": "Lock test text"}
        event2 = {"type": "final", "sessionId": "s_lock", "segmentId": 1, "text": "Lock test text"}

        res1 = self.controller.handle_server_event("final", event1)
        res2 = self.controller.handle_server_event("final", event2)

        self.assertEqual(res1.status, FinalProcessingStatus.QUEUED)
        self.assertEqual(res2.status, FinalProcessingStatus.DEDUPLICATED)
        self.assertEqual(len(status_observed), 2)

    def test_parallel_duplicate_final_events_produce_exactly_one_history_entry(self) -> None:
        barrier = threading.Barrier(2)
        results = []
        lock = threading.Lock()

        event = {"type": "final", "sessionId": "parallel_sess", "segmentId": 77, "text": "Parallel test text"}

        def worker():
            barrier.wait(timeout=2.0)
            res = self.controller.handle_server_event("final", event)
            with lock:
                results.append(res)

        t1 = threading.Thread(target=worker)
        t2 = threading.Thread(target=worker)

        t1.start()
        t2.start()

        t1.join(timeout=2.0)
        t2.join(timeout=2.0)

        self.assertFalse(t1.is_alive())
        self.assertFalse(t2.is_alive())
        self.assertEqual(len(results), 2)

        statuses = [r.status for r in results]
        self.assertEqual(statuses.count(FinalProcessingStatus.QUEUED), 1)
        self.assertEqual(statuses.count(FinalProcessingStatus.DEDUPLICATED), 1)

        entries = self.controller.history.get_memory_entries()
        self.assertEqual(len(entries), 1)


class TestSTTControllerSemanticAPIAsync(unittest.IsolatedAsyncioTestCase):
    async def test_start_and_stop_dictation_success(self) -> None:
        config = AppConfig()
        session = FakeSTTSession()
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()

        cntr = STTController(config, session=session, audio=audio, injection_queue=fake_q)
        cntr.start_queue()

        res_start = await cntr.start_dictation()
        self.assertTrue(res_start.success)
        self.assertEqual(res_start.status, "listening")
        self.assertTrue(cntr.dictation_requested)
        self.assertEqual(audio.start_calls, 1)
        self.assertEqual(session.start_calls, 1)

        res_toggle = await cntr.toggle_dictation()
        self.assertTrue(res_toggle.success)
        self.assertEqual(res_toggle.status, "stopped")
        self.assertFalse(cntr.dictation_requested)
        self.assertEqual(audio.stop_calls, 1)
        self.assertEqual(session.stop_calls, 1)

    async def test_start_dictation_failure_rolls_back_audio(self) -> None:
        config = AppConfig()
        session = FakeSTTSession()
        session.send_start_should_fail = True
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()

        cntr = STTController(config, session=session, audio=audio, injection_queue=fake_q)

        res = await cntr.start_dictation()
        self.assertFalse(res.success)
        self.assertEqual(res.status, "start_command_failed")
        self.assertEqual(audio.start_calls, 1)
        self.assertEqual(audio.stop_calls, 1)
        self.assertFalse(cntr.dictation_requested)

    async def test_start_dictation_rejects_silent_non_streaming_result(self) -> None:
        config = AppConfig()
        config.server.start_confirmation_timeout = 0.05
        session = FakeSTTSession()
        session.state.server_status = SessionState.IDLE
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()
        cntr = STTController(
            config,
            session=session,
            audio=audio,
            injection_queue=fake_q,
        )

        async def silent_send_start() -> None:
            session.start_calls += 1

        session.send_start = silent_send_start

        result = await cntr.start_dictation()

        self.assertFalse(result.success)
        self.assertEqual(result.status, "start_confirmation_timeout")
        self.assertFalse(cntr.dictation_requested)
        self.assertEqual(audio.start_calls, 1)
        self.assertEqual(audio.stop_calls, 1)

    async def test_stop_dictation_rejects_silent_streaming_result(self) -> None:
        config = AppConfig()
        session = FakeSTTSession()
        session._streaming = True
        audio = FakeAudioCapture()
        audio._running = True
        fake_q = FakeInjectionQueue()
        cntr = STTController(
            config,
            session=session,
            audio=audio,
            injection_queue=fake_q,
        )
        cntr._dictation_requested = True

        async def silent_send_stop() -> None:
            session.stop_calls += 1
            session._streaming = True

        session.send_stop = silent_send_stop

        result = await cntr.stop_dictation()

        self.assertTrue(result.success)
        self.assertEqual(result.status, "stopped")
        self.assertFalse(cntr.dictation_requested)
        self.assertEqual(audio.stop_calls, 1)
        self.assertEqual(session.stop_calls, 1)

    async def test_start_confirmation_timeout_fails_dictation(self) -> None:
        config = AppConfig()
        config.server.start_confirmation_timeout = 0.05
        session = FakeSTTSession()
        session.state.server_status = SessionState.IDLE  # not confirmed yet

        async def unconfirming_send_start() -> None:
            session.start_calls += 1

        session.send_start = unconfirming_send_start

        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()

        cntr = STTController(config, session=session, audio=audio, injection_queue=fake_q)
        feedback_events = []
        cntr.on_feedback_event = lambda ev: feedback_events.append(ev)

        result = await cntr.start_dictation()
        self.assertFalse(result.success)
        self.assertEqual(result.status, "start_confirmation_timeout")
        self.assertEqual(len(feedback_events), 1)
        self.assertEqual(feedback_events[0].event_type.value, "dictation_start_failed")
        self.assertEqual(cntr.dictation_state.value, "idle")

    async def test_disconnect_during_dictation_emits_interrupted_event(self) -> None:
        config = AppConfig()
        session = FakeSTTSession()
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()

        cntr = STTController(config, session=session, audio=audio, injection_queue=fake_q)
        feedback_events = []
        cntr.on_feedback_event = lambda ev: feedback_events.append(ev)

        # Start dictation successfully
        await cntr.start_dictation()
        self.assertEqual(cntr.dictation_state.value, "active")

        # Simulate transport loss
        session.state.transport = TransportState.DISCONNECTED
        cntr._handle_transport_change(TransportState.DISCONNECTED)

        self.assertEqual(cntr.dictation_state.value, "idle")
        self.assertFalse(cntr.dictation_requested)
        self.assertEqual(len(feedback_events), 1)
        self.assertEqual(feedback_events[0].event_type.value, "dictation_interrupted")

    async def test_snapshot_status_and_revision(self) -> None:
        config = AppConfig()
        session = FakeSTTSession()
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()

        cntr = STTController(config, session=session, audio=audio, injection_queue=fake_q)
        snap1 = cntr.get_snapshot()
        self.assertEqual(snap1.dictation_state.value, "idle")
        self.assertEqual(snap1.availability_state.value, "starting")

        cntr._handle_transport_change(TransportState.READY)
        snap2 = cntr.get_snapshot()
        self.assertEqual(snap2.availability_state.value, "ready")
        self.assertGreater(snap2.revision, snap1.revision)

    async def test_start_dictation_when_transport_not_ready(self) -> None:
        config = AppConfig()
        session = FakeSTTSession()
        session.state.transport = TransportState.DISCONNECTED
        session.state.ready_ok = False
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()

        cntr = STTController(config, session=session, audio=audio, injection_queue=fake_q)

        res = await cntr.start_dictation()
        self.assertFalse(res.success)
        self.assertEqual(res.status, "transport_not_ready")
        # AP05 requirement: start on not-ready transport is rejected immediately and NOT stored
        self.assertFalse(cntr.dictation_requested)

    async def test_stop_before_ready_prevents_auto_start(self) -> None:
        config = AppConfig()
        session = FakeSTTSession()
        session.state.transport = TransportState.DISCONNECTED
        session.state.ready_ok = False
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()

        cntr = STTController(config, session=session, audio=audio, injection_queue=fake_q)

        await cntr.start_dictation()
        self.assertFalse(cntr.dictation_requested)

        await cntr.stop_dictation()
        self.assertFalse(cntr.dictation_requested)

        session.state.transport = TransportState.READY
        session.state.ready_ok = True

        auto_task = asyncio.create_task(cntr._auto_start_when_ready())
        await asyncio.sleep(0.15)
        auto_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await auto_task

        self.assertEqual(audio.start_calls, 0)
        self.assertEqual(session.start_calls, 0)

    async def test_dictation_transition_race_serialized(self) -> None:
        config = AppConfig()
        session = FakeSTTSession()
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()

        cntr = STTController(config, session=session, audio=audio, injection_queue=fake_q)
        cntr.start_queue()

        start_entered = asyncio.Event()
        release_start = asyncio.Event()

        async def blocking_send_start() -> None:
            session.start_calls += 1
            start_entered.set()
            await release_start.wait()
            session._streaming = True
            session.state = ClientState(
                transport=session.state.transport,
                ready_ok=session.state.ready_ok,
                server_status=SessionState.LISTENING,
                generation=session.generation,
                session_id="fake-session",
            )
            if session.on_state_change:
                session.on_state_change(session.state)
            if session.on_event:
                session.on_event(
                    "status",
                    {
                        "type": "status",
                        "state": "listening",
                        "sessionId": session.state.session_id,
                        "_clientGeneration": session.generation,
                    },
                )

        session.send_start = blocking_send_start

        t1 = asyncio.create_task(cntr.start_dictation())
        await asyncio.wait_for(start_entered.wait(), timeout=1.0)
        t2 = asyncio.create_task(cntr.stop_dictation())
        await asyncio.sleep(0)
        self.assertTrue(t2.done())

        release_start.set()
        res1, res2 = await asyncio.gather(t1, t2)
        self.assertFalse(res1.success)
        self.assertEqual(res1.status, "start_cancelled")
        self.assertTrue(res2.success)
        self.assertFalse(cntr.dictation_requested)
        self.assertEqual(audio.start_calls, 1)
        self.assertEqual(audio.stop_calls, 1)
        self.assertEqual(session.start_calls, 1)
        self.assertEqual(session.stop_calls, 1)
        self.assertFalse(session.is_streaming)

    async def test_auto_start_and_manual_stop_are_serialized(self) -> None:
        config = AppConfig()
        session = FakeSTTSession()
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()
        cntr = STTController(
            config,
            session=session,
            audio=audio,
            injection_queue=fake_q,
        )
        cntr.request_initial_auto_start()

        start_entered = asyncio.Event()
        release_start = asyncio.Event()

        async def blocking_send_start() -> None:
            session.start_calls += 1
            start_entered.set()
            await release_start.wait()
            session._streaming = True
            session.state = ClientState(
                transport=session.state.transport,
                ready_ok=session.state.ready_ok,
                server_status=SessionState.LISTENING,
                generation=session.generation,
                session_id="fake-session",
            )
            if session.on_state_change:
                session.on_state_change(session.state)
            if session.on_event:
                session.on_event(
                    "status",
                    {
                        "type": "status",
                        "state": "listening",
                        "sessionId": session.state.session_id,
                        "_clientGeneration": session.generation,
                    },
                )

        session.send_start = blocking_send_start

        auto_task = asyncio.create_task(cntr._auto_start_when_ready())
        await asyncio.wait_for(start_entered.wait(), timeout=1.0)
        stop_task = asyncio.create_task(cntr.stop_dictation())
        await asyncio.sleep(0)
        self.assertTrue(stop_task.done())

        release_start.set()
        await auto_task
        stop_result = await stop_task

        self.assertTrue(stop_result.success)
        self.assertFalse(cntr.dictation_requested)
        self.assertEqual(audio.start_calls, 1)
        self.assertEqual(audio.stop_calls, 1)
        self.assertEqual(session.start_calls, 1)
        self.assertEqual(session.stop_calls, 1)

    async def test_stop_before_ready_clears_explicit_initial_auto_start(self) -> None:
        config = AppConfig()
        session = FakeSTTSession()
        session.state.transport = TransportState.DISCONNECTED
        session.state.ready_ok = False
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()

        cntr = STTController(config, session=session, audio=audio, injection_queue=fake_q)
        cntr.request_initial_auto_start()

        await cntr.stop_dictation()
        self.assertFalse(cntr.dictation_requested)

        session.state.transport = TransportState.READY
        session.state.ready_ok = True

        auto_task = asyncio.create_task(cntr._auto_start_when_ready())
        await asyncio.sleep(0.15)
        auto_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await auto_task

        self.assertEqual(audio.start_calls, 0)
        self.assertEqual(session.start_calls, 0)

    async def test_parallel_toggle_decision_is_atomic(self) -> None:
        config = AppConfig()
        session = FakeSTTSession()
        audio = FakeAudioCapture()
        fake_q = FakeInjectionQueue()
        cntr = STTController(
            config,
            session=session,
            audio=audio,
            injection_queue=fake_q,
        )

        start_entered = asyncio.Event()
        release_start = asyncio.Event()

        async def blocking_send_start() -> None:
            session.start_calls += 1
            start_entered.set()
            await release_start.wait()
            session._streaming = True
            session.state = ClientState(
                transport=session.state.transport,
                ready_ok=session.state.ready_ok,
                server_status=SessionState.LISTENING,
                generation=session.generation,
                session_id="fake-session",
            )
            if session.on_state_change:
                session.on_state_change(session.state)
            if session.on_event:
                session.on_event(
                    "status",
                    {
                        "type": "status",
                        "state": "listening",
                        "sessionId": session.state.session_id,
                        "_clientGeneration": session.generation,
                    },
                )

        session.send_start = blocking_send_start

        first_toggle = asyncio.create_task(cntr.toggle_dictation())
        await asyncio.wait_for(start_entered.wait(), timeout=1.0)
        second_toggle = asyncio.create_task(cntr.toggle_dictation())
        await asyncio.sleep(0)
        self.assertTrue(second_toggle.done())

        release_start.set()
        first_result, second_result = await asyncio.gather(
            first_toggle,
            second_toggle,
        )

        self.assertEqual(first_result.status, "start_cancelled")
        self.assertEqual(second_result.status, "stopped")
        self.assertFalse(cntr.dictation_requested)
        self.assertEqual(audio.start_calls, 1)
        self.assertEqual(audio.stop_calls, 1)
        self.assertEqual(session.start_calls, 1)
        self.assertEqual(session.stop_calls, 1)


class TestSTTControllerAP05Hardening(unittest.IsolatedAsyncioTestCase):
    def make_controller(
        self,
        *,
        timeout: float = 0.1,
    ) -> tuple[STTController, FakeSTTSession, FakeAudioCapture]:
        config = AppConfig()
        config.server.start_confirmation_timeout = timeout
        config.history.persistent.enabled = False
        session = FakeSTTSession()
        audio = FakeAudioCapture()
        controller = STTController(
            config,
            session=session,
            audio=audio,
            injection_queue=FakeInjectionQueue(),
        )
        return controller, session, audio

    async def test_preexisting_listening_state_does_not_confirm_new_start(self) -> None:
        controller, session, _ = self.make_controller(timeout=0.03)
        session.state.server_status = SessionState.LISTENING

        async def silent_send_start() -> None:
            session.start_calls += 1

        session.send_start = silent_send_start
        result = await controller.start_dictation()

        self.assertFalse(result.success)
        self.assertEqual(result.status, "start_confirmation_timeout")
        self.assertEqual(controller.dictation_state, DictationState.IDLE)
        self.assertEqual(
            session.invalidate_calls,
            ["start_confirmation_timeout"],
        )

    async def test_disconnect_while_starting_cannot_reactivate_dictation(self) -> None:
        controller, session, _ = self.make_controller(timeout=1.0)
        entered = asyncio.Event()

        async def pending_send_start() -> None:
            session.start_calls += 1
            entered.set()
            await asyncio.Future()

        session.send_start = pending_send_start
        feedback = []
        controller.on_feedback_event = feedback.append

        start_task = asyncio.create_task(controller.start_dictation())
        await asyncio.wait_for(entered.wait(), timeout=0.2)
        session.state.transport = TransportState.DISCONNECTED
        session.state.ready_ok = False
        controller._handle_transport_change(TransportState.DISCONNECTED)
        controller._handle_transport_change(TransportState.DISCONNECTED)
        result = await asyncio.wait_for(start_task, timeout=0.2)

        self.assertFalse(result.success)
        self.assertEqual(result.status, "dictation_interrupted")
        self.assertEqual(controller.dictation_state, DictationState.IDLE)
        self.assertFalse(session.is_streaming)
        self.assertEqual(
            [event.event_type for event in feedback],
            [TransientEventType.DICTATION_INTERRUPTED],
        )

    async def test_status_and_feedback_callback_errors_are_non_fatal(self) -> None:
        controller, session, _ = self.make_controller()

        def fail_callback(_value) -> None:
            raise RuntimeError("simulated UI callback failure")

        controller.on_snapshot_change = fail_callback
        controller.on_feedback_event = fail_callback

        controller._handle_transport_change(TransportState.READY)
        session.state.transport = TransportState.DISCONNECTED
        session.state.ready_ok = False
        result = await controller.start_dictation()

        self.assertFalse(result.success)
        self.assertEqual(result.status, "transport_not_ready")

    async def test_start_timeout_recycles_connection_without_stopping_loop(self) -> None:
        controller, session, _ = self.make_controller(timeout=0.03)

        async def silent_send_start() -> None:
            session.start_calls += 1

        session.send_start = silent_send_start
        result = await controller.start_dictation()

        self.assertEqual(result.status, "start_confirmation_timeout")
        self.assertEqual(session.stop_calls, 0)
        self.assertEqual(
            session.invalidate_calls,
            ["start_confirmation_timeout"],
        )

    async def test_stop_while_reconnecting_is_idempotent_and_local(self) -> None:
        controller, session, audio = self.make_controller()
        session.state.transport = TransportState.DISCONNECTED
        session.state.ready_ok = False
        controller._handle_transport_change(TransportState.DISCONNECTED)

        result = await controller.stop_dictation()

        self.assertTrue(result.success)
        self.assertEqual(result.status, "stopped")
        self.assertEqual(session.stop_calls, 0)
        self.assertEqual(session.invalidate_calls, [])
        self.assertEqual(audio.stop_calls, 1)

    async def test_local_start_send_error_emits_specific_feedback(self) -> None:
        controller, session, _ = self.make_controller()
        session.send_start_should_fail = True
        feedback = []
        controller.on_feedback_event = feedback.append

        result = await controller.start_dictation()

        self.assertEqual(result.status, "start_command_failed")
        self.assertEqual(
            [event.event_type for event in feedback],
            [TransientEventType.DICTATION_START_FAILED],
        )
        self.assertEqual(session.invalidate_calls, ["start_command_failed"])

    async def test_status_must_match_generation_and_session(self) -> None:
        controller, session, _ = self.make_controller(timeout=0.3)
        sent = asyncio.Event()

        async def silent_send_start() -> None:
            session.start_calls += 1
            sent.set()

        session.send_start = silent_send_start
        task = asyncio.create_task(controller.start_dictation())
        await asyncio.wait_for(sent.wait(), timeout=0.2)
        await asyncio.sleep(0)

        controller.handle_server_event(
            "status",
            {
                "type": "status",
                "state": "listening",
                "sessionId": session.state.session_id,
                "_clientGeneration": session.generation - 1,
            },
        )
        controller.handle_server_event(
            "status",
            {
                "type": "status",
                "state": "listening",
                "sessionId": "different-session",
                "_clientGeneration": session.generation,
            },
        )
        await asyncio.sleep(0)
        self.assertFalse(task.done())

        controller.handle_server_event(
            "status",
            {
                "type": "status",
                "state": "wakeword_wait",
                "sessionId": session.state.session_id,
                "_clientGeneration": session.generation,
            },
        )
        result = await asyncio.wait_for(task, timeout=0.2)
        self.assertTrue(result.success)
        self.assertEqual(result.status, "wakeword_wait")

    async def test_server_command_error_fails_start_without_reconnect_storm(self) -> None:
        controller, session, _ = self.make_controller(timeout=0.3)

        async def rejected_start() -> None:
            session.start_calls += 1
            controller.handle_server_event(
                "error",
                {
                    "type": "error",
                    "where": "command",
                    "message": "invalid state",
                    "_clientGeneration": session.generation,
                },
            )

        session.send_start = rejected_start
        result = await controller.start_dictation()

        self.assertEqual(result.status, "start_command_rejected")
        self.assertEqual(
            controller.availability_state,
            AvailabilityState.PROTOCOL_ERROR,
        )
        self.assertEqual(session.invalidate_calls, [])
        self.assertEqual(controller.dictation_state, DictationState.IDLE)

    async def test_snapshot_revisions_cover_dictation_transitions(self) -> None:
        controller, session, _ = self.make_controller()
        snapshots = []
        controller.on_snapshot_change = snapshots.append

        start_result = await controller.start_dictation()
        self.assertTrue(start_result.success)
        session.state.transport = TransportState.DISCONNECTED
        session.state.ready_ok = False
        controller._handle_transport_change(TransportState.DISCONNECTED)

        states = [snapshot.dictation_state for snapshot in snapshots]
        self.assertIn(DictationState.STARTING, states)
        self.assertIn(DictationState.ACTIVE, states)
        self.assertEqual(states[-1], DictationState.IDLE)
        revisions = [snapshot.revision for snapshot in snapshots]
        self.assertEqual(revisions, sorted(revisions))
        self.assertEqual(len(revisions), len(set(revisions)))

    async def test_error_classes_produce_distinct_persistent_states(self) -> None:
        controller, session, _ = self.make_controller()
        controller.handle_server_event(
            "error",
            {
                "type": "error",
                "where": "admission",
                "message": "full",
                "_clientGeneration": session.generation,
            },
        )
        self.assertEqual(
            controller.availability_state, AvailabilityState.SERVER_BUSY
        )

        controller._handle_transport_change(TransportState.READY)
        controller.handle_server_event(
            "error",
            {
                "type": "error",
                "where": "main_engine",
                "message": "engine down",
                "_clientGeneration": session.generation,
            },
        )
        self.assertEqual(
            controller.availability_state,
            AvailabilityState.SERVER_UNAVAILABLE,
        )

    async def test_shutdown_publishes_shutting_down_then_stopped(self) -> None:
        controller, _, _ = self.make_controller()
        states = []
        controller.on_snapshot_change = (
            lambda snapshot: states.append(snapshot.availability_state)
        )
        controller.start_queue()

        await controller.shutdown()

        self.assertIn(AvailabilityState.SHUTTING_DOWN, states)
        self.assertEqual(states[-1], AvailabilityState.STOPPED)
        self.assertEqual(
            controller.get_snapshot().availability_state,
            AvailabilityState.STOPPED,
        )

    async def test_hello_prunes_old_session_reservations(self) -> None:
        controller, session, _ = self.make_controller()
        controller._processed_finals = {
            ("old-session", 1): "old",
            ("new-session", 2): "new",
        }

        controller.handle_server_event(
            "hello",
            {
                "type": "hello",
                "sessionId": "new-session",
                "_clientGeneration": session.generation,
            },
        )

        self.assertEqual(
            controller._processed_finals,
            {("new-session", 2): "new"},
        )

    async def test_final_identity_cache_is_bounded(self) -> None:
        controller, _, _ = self.make_controller()
        with controller._lock:
            for segment_id in range(5000):
                controller._remember_final_identity_locked(
                    ("long-session", segment_id),
                    str(segment_id),
                )

        self.assertEqual(len(controller._processed_finals), 4096)
        self.assertNotIn(("long-session", 0), controller._processed_finals)
        self.assertIn(("long-session", 4999), controller._processed_finals)


class TestSTTControllerErrorBranches(BaseControllerTestCase):
    def test_history_disabled_returns_history_unavailable(self) -> None:
        self.controller.history.config.enabled = False
        self.controller.start_queue()

        event = {"type": "final", "sessionId": "s", "segmentId": 1, "text": "Hello"}
        res = self.controller.handle_server_event("final", event)

        self.assertEqual(res.status, FinalProcessingStatus.HISTORY_UNAVAILABLE)

    def test_queue_not_started_returns_queue_unavailable_and_logs_skipped_attempt(self) -> None:
        event = {"type": "final", "sessionId": "s", "segmentId": 1, "text": "Hello"}
        res = self.controller.handle_server_event("final", event)

        self.assertEqual(res.status, FinalProcessingStatus.QUEUE_UNAVAILABLE)

        entries = self.controller.history.get_memory_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(len(entries[0].attempts), 1)
        self.assertEqual(entries[0].attempts[0].status, "skipped")

    def test_enqueue_exception_returns_failed_and_logs_failed_attempt(self) -> None:
        self.controller.start_queue()

        def failing_enqueue(entry):
            raise RuntimeError("Simulated enqueue failure")

        self.controller.queue.enqueue = failing_enqueue

        event = {"type": "final", "sessionId": "s", "segmentId": 1, "text": "Hello"}
        res = self.controller.handle_server_event("final", event)

        self.assertEqual(res.status, FinalProcessingStatus.FAILED)
        self.assertEqual(res.reason, "enqueue_exception")

        entries = self.controller.history.get_memory_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(len(entries[0].attempts), 1)
        self.assertEqual(entries[0].attempts[0].status, "failed")

    def test_attempt_logging_failure_does_not_crash_controller(self) -> None:
        fake_q = FakeInjectionQueue()

        cntr = STTController(self.config, injection_queue=fake_q, history_manager=self.history_mgr)
        cntr.start_queue()
        fake_q._running = False

        def failing_record(*args, **kwargs):
            raise RuntimeError("Record attempt failed")

        cntr.history.record_injection_attempt = failing_record

        event = {"type": "final", "sessionId": "s", "segmentId": 1, "text": "Hello"}
        res = cntr.handle_server_event("final", event)
        self.assertEqual(res.status, FinalProcessingStatus.QUEUE_UNAVAILABLE)


class TestSTTControllerReinsertion(BaseControllerTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller.start_queue()

    def test_reinsert_last_uses_queue_without_new_history_entry(self) -> None:
        event = {"type": "final", "sessionId": "s1", "segmentId": 1, "text": "Reinsertion original text"}
        self.controller.handle_server_event("final", event)

        entries_before = self.controller.history.get_memory_entries()
        self.assertEqual(len(entries_before), 1)

        res = self.controller.reinsert_last()
        self.assertEqual(res.status, ReinsertionStatus.QUEUED)
        self.assertEqual(res.entry_id, entries_before[0].id)

        entries_after = self.controller.history.get_memory_entries()
        self.assertEqual(len(entries_after), 1)

    def test_reinsert_entry_by_id(self) -> None:
        event = {"type": "final", "sessionId": "s1", "segmentId": 1, "text": "Target text"}
        self.controller.handle_server_event("final", event)
        entry_id = self.controller.history.get_memory_entries()[0].id

        res = self.controller.reinsert_entry(entry_id)
        self.assertEqual(res.status, ReinsertionStatus.QUEUED)
        self.assertEqual(res.entry_id, entry_id)

    def test_reinsert_empty_history(self) -> None:
        res = self.controller.reinsert_last()
        self.assertEqual(res.status, ReinsertionStatus.EMPTY_HISTORY)

    def test_reinsert_non_existent_id(self) -> None:
        res = self.controller.reinsert_entry("unknown_id")
        self.assertEqual(res.status, ReinsertionStatus.ENTRY_NOT_FOUND)

    def test_reinsert_when_queue_unavailable(self) -> None:
        event = {"type": "final", "sessionId": "s1", "segmentId": 1, "text": "Target text"}
        self.controller.handle_server_event("final", event)

        self.controller.queue.stop()

        res = self.controller.reinsert_last()
        self.assertEqual(res.status, ReinsertionStatus.QUEUE_UNAVAILABLE)


if __name__ == "__main__":
    unittest.main()


class TestMicrophoneMuteAndManualReconnect(BaseControllerTestCase):
    """Deliberate acts by somebody watching, rather than automatic behaviour."""

    def test_muting_stops_audio_leaving_the_client(self) -> None:
        self.assertFalse(self.controller.microphone_muted)

        result = self.controller.set_microphone_muted(True)
        self.assertTrue(result.success)
        self.assertTrue(self.controller.microphone_muted)
        self.assertTrue(self.audio.muted)

        # The stream is not torn down: reopening it takes long enough to be
        # noticed and can fail if something else took the device meanwhile.
        self.assertEqual(self.audio.stop_calls, 0)

    def test_unmuting_returns_the_microphone(self) -> None:
        self.controller.set_microphone_muted(True)
        result = self.controller.set_microphone_muted(False)
        self.assertTrue(result.success)
        self.assertFalse(self.controller.microphone_muted)
        self.assertFalse(self.audio.muted)

    def test_manual_reconnect_drops_the_connection_now(self) -> None:
        result = asyncio.run(self.controller.reconnect_server())
        self.assertTrue(result.success)
        self.assertIn("manual_reconnect", self.session.invalidate_calls)

    def test_a_failing_reconnect_is_reported_rather_than_raised(self) -> None:
        async def boom(reason: str = "") -> None:
            raise OSError("no route to host")

        self.session.invalidate_connection = boom
        result = asyncio.run(self.controller.reconnect_server())
        self.assertFalse(result.success)
        self.assertIn("no route to host", result.message)
