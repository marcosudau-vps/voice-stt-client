"""Regression and lifecycle tests for the headless application orchestrator."""

from __future__ import annotations

import asyncio
import contextlib
import io
import os
import shutil
import tempfile
import threading
import unittest
from typing import List, Optional, Tuple

from app import RealtimeSTTClient
from core.config import AppConfig
from core.history import TranscriptHistoryManager, HistoryEntry
from core.text_injector import WindowsInjectionBackend
from core.stt_session import STTSession, TransportState
from core.controller import DictationState


class FakeWindowsBackend(WindowsInjectionBackend):
    """Fake Win32 backend for testing without real OS calls."""

    def create_owner_window(self) -> None:
        pass

    def destroy_owner_window(self) -> None:
        pass

    def get_owner_window(self) -> int:
        return 1001

    def open_clipboard(self, hwnd: int) -> bool:
        return True

    def close_clipboard(self) -> bool:
        return True

    def empty_clipboard(self) -> bool:
        return True

    def is_format_available(self, format_id: int) -> bool:
        return True

    def get_clipboard_data_unicode(self) -> Optional[str]:
        return "previous"

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
    def __init__(self) -> None:
        self._running = False
        self.stop_called = False

    def start(self) -> None:
        self._running = True

    def stop(self, timeout: Optional[float] = None) -> None:
        self.stop_called = True
        self._running = False

    def enqueue(self, entry: HistoryEntry) -> bool:
        return self._running

    def is_running(self) -> bool:
        return self._running

    def queue_size(self) -> int:
        return 0


class RecordingLoop:
    """Minimal event-loop double for the cross-thread scheduling boundary."""

    def __init__(self) -> None:
        self.closed = False
        self.scheduled = []
        self.raise_on_schedule = False

    def is_closed(self) -> bool:
        return self.closed

    def call_soon_threadsafe(self, callback, *args) -> None:
        if self.raise_on_schedule:
            raise RuntimeError("loop closed during scheduling")
        self.scheduled.append((callback, args))


class TestAppIsolatedBase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_app_history.db")

        self.config = AppConfig()
        self.config.history.persistent.db_path = self.db_path

        self.backend = FakeWindowsBackend()
        self.history_mgr = TranscriptHistoryManager(self.config.history, db_path=self.db_path)
        self.fake_queue = FakeInjectionQueue()

        self.client = RealtimeSTTClient(
            self.config,
            history_manager=self.history_mgr,
            injection_queue=self.fake_queue,
            backend=self.backend,
        )

        self._initial_threads = set(threading.enumerate())

    def tearDown(self) -> None:
        if self.client.is_running or not self.client.is_closing:
            asyncio.run(self.client.shutdown())

        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass

        new_workers = [t for t in (set(threading.enumerate()) - self._initial_threads) if "TextInjectionQueueWorker" in t.name]
        self.assertEqual(len(new_workers), 0, f"Leaked worker threads: {new_workers}")


class TestAppDependencyInjectionAndIsolation(TestAppIsolatedBase):
    def test_client_shares_same_history_instance_across_components(self) -> None:
        self.assertIs(self.client.history, self.history_mgr)
        self.assertIs(self.client.reinsertion.history_manager, self.history_mgr)
        self.assertIs(self.client.reinsertion.injection_queue, self.fake_queue)

    def test_headless_client_sets_initial_dictation_requested(self) -> None:
        self.assertTrue(self.client.dictation_requested)


class TestAudioThreadBridge(TestAppIsolatedBase):
    def setUp(self) -> None:
        super().setUp()
        self.loop = RecordingLoop()
        self.client._loop = self.loop

    def _packet(self) -> tuple[bytes, int, int, int]:
        return (b"\x01\x02", 16000, 1, 1)

    def _submit_packet(self, packet: tuple[bytes, int, int, int]) -> None:
        self.client._on_audio_packet_from_thread(*packet)

    def _activate_dictation(self) -> None:
        self.client.session._streaming = True
        self.client._dictation_state = DictationState.ACTIVE

    def test_audio_packet_is_scheduled_threadsafe_before_enqueue(self) -> None:
        packet = self._packet()
        self._activate_dictation()

        producer = threading.Thread(target=self._submit_packet, args=(packet,))
        producer.start()
        producer.join(timeout=1.0)

        self.assertFalse(producer.is_alive())
        self.assertTrue(self.client._audio_send_queue.empty())
        self.assertEqual(len(self.loop.scheduled), 1)

        callback, args = self.loop.scheduled[0]
        self.assertEqual(callback, self.client._enqueue_audio_packet)
        expected_packet = (*packet, self.client.session.generation)
        self.assertEqual(args, (expected_packet,))

        callback(*args)
        self.assertEqual(
            self.client._audio_send_queue.get_nowait(), expected_packet
        )

    def test_audio_before_start_is_not_scheduled(self) -> None:
        self.client.session._streaming = False

        self._submit_packet(self._packet())

        self.assertEqual(self.loop.scheduled, [])
        self.assertTrue(self.client._audio_send_queue.empty())

    def test_audio_is_not_scheduled_without_an_open_loop(self) -> None:
        self._activate_dictation()

        self.client._loop = None
        self._submit_packet(self._packet())

        self.client._loop = self.loop
        self.loop.closed = True
        self._submit_packet(self._packet())

        self.assertEqual(self.loop.scheduled, [])
        self.assertTrue(self.client._audio_send_queue.empty())

    def test_shutdown_race_during_scheduling_is_ignored(self) -> None:
        self._activate_dictation()
        self.loop.raise_on_schedule = True

        self._submit_packet(self._packet())

        self.assertTrue(self.client._audio_send_queue.empty())

    def test_packet_scheduled_before_stop_is_dropped_after_stop(self) -> None:
        packet = self._packet()
        self._activate_dictation()
        self._submit_packet(packet)
        callback, args = self.loop.scheduled[0]

        self.client.session._streaming = False
        callback(*args)

        self.assertTrue(self.client._audio_send_queue.empty())

    def test_packet_scheduled_before_reconnect_is_never_retagged(self) -> None:
        packet = self._packet()
        self._activate_dictation()
        self._submit_packet(packet)
        callback, args = self.loop.scheduled[0]
        old_generation = self.client.session.generation

        self.client.session._generation += 1
        self.client.session._state.generation = self.client.session.generation
        self._activate_dictation()
        callback(*args)

        self.assertNotEqual(old_generation, self.client.session.generation)
        self.assertTrue(self.client._audio_send_queue.empty())

    def test_full_async_queue_drops_new_packet_without_replacing_oldest(self) -> None:
        old_packet = (b"old", 16000, 1, 1, self.client.session.generation)
        self.client._audio_send_queue = asyncio.Queue(maxsize=1)
        self.client._audio_send_queue.put_nowait(old_packet)
        self._activate_dictation()

        self.client._enqueue_audio_packet(
            (*self._packet(), self.client.session.generation)
        )

        self.assertEqual(self.client._audio_send_queue.get_nowait(), old_packet)
        self.assertTrue(self.client._audio_send_queue.empty())


class TestRunLoopBinding(unittest.IsolatedAsyncioTestCase):
    async def test_run_binds_owning_loop_and_clears_it_after_shutdown(self) -> None:
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_app_loop.db")
        config = AppConfig()
        config.history.persistent.db_path = db_path

        fake_q = FakeInjectionQueue()
        hm = TranscriptHistoryManager(config.history, db_path=db_path)
        client = RealtimeSTTClient(config, history_manager=hm, injection_queue=fake_q)

        observed_loops = []

        async def session_observe_loop() -> None:
            observed_loops.append(client._loop)

        async def helper_observe_loop() -> None:
            observed_loops.append(client._loop)
            await asyncio.Future()  # Stay active until cancelled

        client.session.run = session_observe_loop
        client._audio_sender = helper_observe_loop
        client._auto_start_when_ready = helper_observe_loop

        running_loop = asyncio.get_running_loop()
        with contextlib.redirect_stdout(io.StringIO()):
            await client.run()

        self.assertEqual(observed_loops, [running_loop, running_loop, running_loop])
        self.assertIsNone(client._loop)
        self.assertTrue(fake_q.stop_called)

        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
