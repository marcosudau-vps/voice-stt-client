"""Actual V2 transport/media with controlled device and log boundaries."""

import asyncio
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

import numpy as np

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.audio_capture import AudioCapture
from voice_stt_client.core.config import AudioConfig, ServerConfig, EventStreamConfig
from voice_stt_client.core.event_cursor_store import EventCursorStore
from voice_stt_client.core.event_protocol import EventProtocolProcessor, EventStreamAccess
from voice_stt_client.core.event_models import EventConnectionState
from voice_stt_client.core.event_models import EventEnvelope
from voice_stt_client.core.event_stream import EventStreamTransport
from voice_stt_client.core.session_coordinator import DualSessionCoordinator
from voice_stt_client.core.v2_media import BoundedAudioQueue, V2MediaConnection
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig, V2TransportState
from tests.test_event_protocol import access, enter_replay, event_message
from tests.test_session_coordinator import FakeEventTransport, hello, event_result, future_expiry
from tests.test_v2_transport import FakeWebSocket, until, close_error


class Capture:
    """Device boundary; production transport/codec/queue/coordinator stay real."""
    is_running = False
    device_active = True
    on_audio_packet = None
    fail = False
    starts = stops = 0

    def probe(self):
        if self.fail:
            raise OSError("synthetic device unavailable")

    def start(self):
        self.probe()
        self.is_running = True
        self.device_active = True
        self.starts += 1

    def stop(self):
        self.is_running = False
        self.stops += 1

    def emit(self, rate=16000, channels=1, marker=1):
        frames = rate // 25
        self.on_audio_packet(bytes([marker, 0]) * frames * channels, rate, channels, frames)


class Socket(FakeWebSocket):
    available = True

    def push(self, value):
        if isinstance(value, dict) and value.get("type") == "hello.accepted":
            value = deepcopy(value)
            if self.available:
                value["logAccess"]["expiresAt"] = future_expiry()
            else:
                value["logAccess"] = {"available": False, "code": "disabled", "reason": "disabled"}
        super().push(value)


class AudioQueue(unittest.TestCase):
    def test_duration_overflow_drops_oldest_and_retains_latest(self):
        q = BoundedAudioQueue()
        for n in range(20):
            q.put(bytes([n, 0]) * 640, 16000, 1, 640, 7)
        self.assertLessEqual(q.duration_ms, 500)
        self.assertEqual(q.overflow, 8)
        self.assertEqual(q.pop(7).pcm[0], 8)

    def test_age_and_generation_are_rejected(self):
        now = [0.]
        q = BoundedAudioQueue(clock=lambda: now[0])
        q.put(b"\0\0" * 640, 16000, 1, 640, 1)
        self.assertIsNone(q.pop(2))
        q.put(b"\0\0" * 640, 16000, 1, 640, 2)
        now[0] = .501
        self.assertIsNone(q.pop(2))
        self.assertEqual(q.stale, 2)

    def test_formats_and_metrics_reject_misalignment_and_oversize(self):
        q = BoundedAudioQueue()
        for values in ((b"x", 16000, 1, 1), (b"\0\0", 0, 1, 1),
                       (b"\0\0", 16000, 1, 2), (b"\0\0", True, 1, 1),
                       (b"\0\0", 16000, 1, None), (b"x" * 524290, 16000, 1, 262145)):
            self.assertFalse(q.put(*values, 1))
        self.assertEqual(q.invalid, 6)
        self.assertFalse(q.put(b"\0\0" * 16000, 16000, 1, 16000, 1))
        self.assertEqual(q.overflow, 1)

    def test_extreme_rate_has_packet_count_and_byte_bounds(self):
        q = BoundedAudioQueue()
        for n in range(1000):
            q.put(b"\0\0" * 640, 10**9, 1, 640, 1)
        self.assertEqual(len(q._items), 128)
        self.assertLessEqual(q._bytes, 4 * 1024 * 1024)
        q.clear()
        self.assertEqual(q.duration_ms, 0)

    def test_float_capture_clamps_and_encodes_little_endian(self):
        capture = AudioCapture(AudioConfig(), queue_duration_ms=500)
        capture._running = True
        samples = np.array([-2., -1., 0., 1., 2., np.nan, np.inf], dtype=np.float32)
        capture._audio_callback(samples, len(samples), None, None)
        values = np.frombuffer(capture._audio_queue.get_nowait(), dtype="<i2")
        self.assertEqual(values.tolist(), [-32767, -32767, 0, 32767, 32767, 0, 32767])
        self.assertEqual(capture._audio_queue.maxsize, 12)
        capture.set_muted(True)
        capture._audio_callback(samples, len(samples), None, None)
        self.assertTrue(capture._audio_queue.empty())


class Media(unittest.IsolatedAsyncioTestCase):
    async def start(self, *, capture=None, sockets=None, settings=None, **config):
        sockets = sockets or [Socket()]
        count = [0]
        async def connector(*args, **kwargs):
            socket = sockets[min(count[0], len(sockets) - 1)]
            count[0] += 1
            return socket
        session = V2STTSession(V2TransportConfig(backoff_initial=.01, ack_timeout=config.pop('ack_timeout',.05),
                              command_retries=0, **config), connector=connector, jitter=lambda a,b:1)
        logs = DualSessionCoordinator(ServerConfig(), EventStreamConfig(cursor_persistence_enabled=False),
                                      transport_factory=FakeEventTransport)
        media = V2MediaConnection(session, capture or Capture(), logs=logs, settings_bootstrap=settings,
                                  recovery_interval=.01)
        task = asyncio.create_task(session.run())
        self.addAsyncCleanup(self.join, task)
        self.addAsyncCleanup(media.close)
        await until(lambda: session.is_ready or session.status.state == V2TransportState.BLOCKED)
        if session.is_ready:
            await until(lambda: media.capture.is_running or media._reported_available == (session.binding, False))
            await until(lambda: media._gate or media._reported_available == (session.binding, False))
        return media, sockets[0]

    async def join(self, task):
        await asyncio.gather(task, return_exceptions=True)

    async def test_continuous_manual_wake_and_combined_across_commands(self):
        for manual, wake in ((True, False), (False, True), (True, True)):
            media, socket = await self.start(manual=manual, wake_word=wake, wake_word_ids=("hey_jarvis",) if wake else ())
            media.capture.emit()
            await until(lambda: media.sent == 1)
            await media.session.request(p.CommandType.ACTIVATION, action="activate", source="manual")
            media.capture.emit(48000, 2)
            await until(lambda: media.sent == 2)
            await media.session.request(p.CommandType.ACTIVATION, action="finish", activationId=p.new_id())
            media.capture.emit()
            await until(lambda: media.sent == 3)
            await media.session.request(p.CommandType.ACTIVATION, action="cancel", activationId=p.new_id())
            await media.session.request(p.CommandType.SUPPRESSION, manual=True, wakeWord=True)
            media.capture.emit()
            await until(lambda: media.sent == 4)
            self.assertEqual(media.capture.starts, 1)
            decoded = [p.decode_audio_packet(x) for x in socket.sent if isinstance(x, bytes)]
            self.assertEqual([x.metadata["sampleRate"] for x in decoded], [16000,48000,16000,16000])
            self.assertEqual(decoded[1].metadata["channels"], 2)
            await media.close()

    async def test_config_ready_gates_capture_and_sending(self):
        entered, release = asyncio.Event(), asyncio.Event()
        capture = Capture()
        async def settings(client, binding):
            entered.set()
            self.assertFalse(capture.is_running)
            self.assertFalse(await client.send_audio(b"\0\0", 16000))
            await release.wait()
        starting = asyncio.create_task(self.start(capture=capture, settings=settings))
        await entered.wait()
        self.assertFalse(capture.is_running)
        release.set()
        media, socket = await starting
        self.assertTrue(media._gate)

    async def test_device_loss_mute_recovery_and_led_are_separate(self):
        media, socket = await self.start(suppress_wake_word=True)
        binding = media.session.binding
        before = len(socket.commands)
        media.set_led_available(False)
        self.assertEqual(len(socket.commands), before)
        self.assertTrue(media.audio_available)
        old_callback = media.capture.on_audio_packet
        media.set_device_available(False)
        old_callback(b"\0\0" * 640,16000,1,640)
        self.assertFalse(media._gate)
        await until(lambda: media._reported_available == (binding, False))
        self.assertIs(media.session.binding, binding)
        self.assertEqual(media.queue.duration_ms, 0)
        media.set_device_available(True)
        await until(lambda: media._gate)
        media.set_hardware_muted(True)
        await until(lambda: media._reported_available == (binding, False))
        media.set_hardware_muted(False)
        await until(lambda: media._gate)
        self.assertEqual(media.session._desired_suppression, (False,True))
        old_callback(b"\0\0" * 640,16000,1,640)
        self.assertEqual(media.queue.duration_ms, 0)
        self.assertFalse(any(c["type"] == "activation.command" for c in socket.commands))

    async def test_dead_capture_reports_false_then_reopens(self):
        media, socket = await self.start()
        media.capture.device_active = False
        await until(lambda: media.capture.starts == 2 and media._gate)
        available = [c["audioAvailable"] for c in socket.commands if c["type"] == "audio_availability.set"]
        self.assertEqual(available, [False,True])

    async def test_active_driver_without_callbacks_reports_loss_before_blocked_stop(self):
        # Reproduce the real unplug trace: PortAudio still says active, but
        # its production capture counter has stopped advancing.
        capture = AudioCapture(AudioConfig())
        class Stream:
            active = True
            def __init__(self, **kwargs): pass
            def start(self): pass
            def stop(self): self.active = False
            def close(self): pass
        entered, release = threading.Event(), threading.Event()
        with patch('sounddevice.query_devices', return_value={'name':'synthetic', 'default_samplerate':16000}), patch('sounddevice.check_input_settings'), patch('sounddevice.InputStream', Stream):
            media, socket = await self.start(capture=capture,ack_timeout=1)
            original = capture.stop
            def stop():
                entered.set()
                release.wait(5)
                original()
            capture.stop = stop
            old_callback = capture.on_audio_packet
            try:
                await asyncio.sleep(2.05)
                await until(lambda:entered.is_set() and media._reported_available is not None
                            and media._reported_available[1] is False)
                self.assertTrue(entered.is_set())
                self.assertTrue(capture.device_active)
                self.assertFalse(media.audio_available)
                self.assertFalse(media._gate)
                self.assertFalse(media._reported_available[1])
                old_callback(b'\0\0'*640,16000,1,640)
                self.assertEqual(media.queue.duration_ms, 0)
                self.assertEqual([c['audioAvailable'] for c in socket.commands if c['type']=='audio_availability.set'], [False])
            finally:
                release.set()
                capture.stop = original
                await media.close()

    async def test_silent_pcm_is_progress_and_stalled_stream_recovers_without_activation(self):
        capture = AudioCapture(AudioConfig())
        class Stream:
            active = True
            def __init__(self, **kwargs): pass
            def start(self): pass
            def stop(self): self.active = False
            def close(self): pass
        with patch('sounddevice.query_devices', return_value={'name':'synthetic', 'default_samplerate':16000}), patch('sounddevice.check_input_settings'), patch('sounddevice.InputStream', Stream):
            media, socket = await self.start(capture=capture)
            binding = media.session.binding
            # Zero-valued PCM must not be mistaken for absent callbacks.
            for _ in range(12):
                capture._audio_callback(np.zeros((640,1),dtype=np.int16),640,None,None)
                await asyncio.sleep(.2)
            self.assertFalse(any(c['type']=='audio_availability.set' for c in socket.commands))
            await asyncio.sleep(2.2)
            self.assertTrue(any(c['type']=='audio_availability.set' and not c['audioAvailable'] for c in socket.commands))
            await until(lambda: media._gate)
            before = media.sent
            capture._audio_callback(np.zeros((640,1),dtype=np.int16),640,None,None)
            await until(lambda: media.sent > before)
            self.assertIs(media.session.binding, binding)
            self.assertEqual([c['audioAvailable'] for c in socket.commands if c['type']=='audio_availability.set'],[False,True])
            self.assertFalse(any(c['type']=='activation.command' for c in socket.commands))
            await media.close()

    async def test_failed_start_remains_session_bound_and_recovers(self):
        capture = Capture()
        capture.fail = True
        media, socket = await self.start(capture=capture)
        binding = media.session.binding
        self.assertFalse(media._gate)
        self.assertGreater(media.capture_failures, 0)
        capture.fail = False
        await until(lambda: media._gate)
        self.assertIs(media.session.binding, binding)

    async def test_network_reconnect_clears_samples_and_uses_new_ids(self):
        first, second = Socket(), Socket(session_id=p.new_id())
        media, socket = await self.start(sockets=[first, second], suppress_manual=True)
        old = media.session.binding
        callback = media.capture.on_audio_packet
        media.capture.emit(marker=9)
        first.push(close_error(1011))
        await until(lambda: media.session.binding is not None and media.session.binding is not old and media._gate)
        callback(b"\x09\0" * 640,16000,1,640)
        media.capture.emit(marker=4)
        await until(lambda: any(isinstance(x,bytes) for x in second.sent))
        packets = [p.decode_audio_packet(x).pcm[0] for x in second.sent if isinstance(x,bytes)]
        self.assertEqual(packets, [4])
        self.assertEqual(media.session._desired_suppression, (True,False))
        self.assertFalse(media.set_device_available(False, binding=old))
        a = {c["commandId"] for c in first.commands}
        b = {c["commandId"] for c in second.commands}
        self.assertFalse(a & b)
        self.assertNotEqual(old.session_id, media.session.binding.session_id)

    async def test_log_unavailable_and_expired_access_do_not_block_audio(self):
        for invalid in (False,True):
            socket = Socket()
            socket.available = invalid
            if invalid:
                def push(value):
                    if isinstance(value,dict) and value.get("type") == "hello.accepted":
                        value["logAccess"]["expiresAt"] = future_expiry(-1)
                    FakeWebSocket.push(socket, value)
                socket.push = push
            media, _ = await self.start(sockets=[socket])
            await until(lambda: media._binding is media.session.binding)
            media.capture.emit()
            await until(lambda: media.sent == 1)
            self.assertEqual(media.logs.active_transport_count, 0)
            self.assertTrue(media.session.is_ready)
            await media.close()

    async def test_log_final_is_observation_only_and_snapshot_keeps_token(self):
        media, socket = await self.start()
        await until(lambda: media.logs.context.log_access is not None)
        access = media.logs.context.log_access
        before = len(socket.commands)
        result = event_result(media.session.binding.session_id)
        self.assertTrue(await media.logs._handle_event(media.logs._binding, result))
        self.assertEqual(len(socket.commands), before)
        await media.session.request(p.CommandType.SNAPSHOT_REQUEST)
        self.assertIs(media.logs.context.log_access, access)
        self.assertNotIn(access.access_token, repr(media.logs.context))
        self.assertNotIn(access.access_token, access.endpoint)
        media.logs._handle_state(media.logs._binding, EventConnectionState.BACKOFF)
        media.capture.emit()
        await until(lambda: media.sent == 1)
        self.assertEqual(media.session.generation, 1)

    async def test_audio_availability_rejection_recycles_without_resuming_samples(self):
        media, socket = await self.start()
        async def reject(command):
            socket.reply(command, "invalid_payload")
        socket.on_send = reject
        media.set_device_available(False)
        await until(lambda: not media.session.is_ready)
        self.assertFalse(media._gate)

    async def test_shutdown_is_idempotent_and_joins_all_media_tasks(self):
        media, socket = await self.start()
        tasks = (media._task, media._sender)
        await asyncio.wait_for(media.close(), 1)
        await media.close()
        self.assertTrue(all(t.done() for t in tasks))
        self.assertFalse(media.capture.is_running)
        self.assertEqual(media.logs.active_transport_count, 0)
        self.assertIsNone(media.session.binding)
        self.assertEqual(media.queue.duration_ms, 0)

    async def test_shutdown_joins_native_start_before_stopping_device(self):
        media, socket = await self.start()
        await until(lambda: media._gate)
        entered, release = threading.Event(), threading.Event()
        order = []
        def native_start():
            entered.set()
            release.wait(2)
            order.append("started")
        original_stop = media.capture.stop
        def stop():
            order.append("stopped")
            original_stop()
        media.capture.stop = stop
        operation = asyncio.create_task(media._capture_call(native_start))
        await until(entered.is_set)
        operation.cancel()
        await asyncio.gather(operation, return_exceptions=True)
        closing = asyncio.create_task(media.close())
        await asyncio.sleep(.02)
        self.assertFalse(closing.done())
        self.assertEqual(order, [])
        release.set()
        await asyncio.wait_for(closing, 1)
        self.assertEqual(order, ["started", "stopped"])
        self.assertIsNone(media._capture_operation)

    async def assert_unavailable_before_blocked_stop(self, cause):
        media, socket = await self.start()
        binding = media.session.binding
        entered, release = threading.Event(), threading.Event()
        original_stop = media.capture.stop
        def blocked_stop():
            entered.set()
            release.wait(3)
            original_stop()
        media.capture.stop = blocked_stop
        callback = media.capture.on_audio_packet
        try:
            if cause == "device":
                media.set_device_available(False)
            elif cause == "mute":
                media.set_hardware_muted(True)
            else:
                media.capture.device_active = False
            await until(entered.is_set)
            # The driver is still blocked: ACK/false must already be known.
            self.assertFalse(release.is_set())
            self.assertEqual(media._reported_available, (binding, False))
            self.assertTrue(any(c["type"] == "audio_availability.set" and
                                c["audioAvailable"] is False for c in socket.commands))
            self.assertFalse(media._gate)
            callback(b"\0\0" * 640, 16000, 1, 640)
            self.assertEqual(media.queue.duration_ms, 0)
            self.assertIs(media.session.binding, binding)
        finally:
            release.set()
            await media.close()

    async def test_device_loss_reports_false_before_blocked_native_stop(self):
        await self.assert_unavailable_before_blocked_stop("device")

    async def test_hardware_mute_reports_false_before_blocked_native_stop(self):
        await self.assert_unavailable_before_blocked_stop("mute")

    async def test_dead_device_reports_false_before_blocked_native_stop(self):
        await self.assert_unavailable_before_blocked_stop("dead")

    async def assert_timeout_cleans_logs_and_retry(self, kind):
        media, socket = await self.start()
        await until(lambda: media.logs.active_transport_count == 1)
        log_task, expiry_task = media.logs._transport_task, media.logs._expiry_task
        log_transport = media.logs._transport
        entered, release = threading.Event(), threading.Event()
        original_stop = media.capture.stop
        pending = None
        def blocked():
            entered.set()
            release.wait(3)
            if kind == "stop":
                original_stop()
        media.shutdown_timeout = .1
        try:
            if kind == "stop":
                media.capture.stop = blocked
            else:
                pending = asyncio.create_task(media._capture_call(blocked))
                await until(entered.is_set)
            with self.assertRaises(TimeoutError):
                await asyncio.wait_for(media.close(), 1)
            self.assertTrue(entered.is_set())
            self.assertFalse(release.is_set())
            self.assertEqual(media.logs.active_transport_count, 0)
            self.assertTrue(log_task.done() and expiry_task.done())
            self.assertEqual(log_transport.stop_calls, 1)
            self.assertIsNone(media.session.binding)
            self.assertFalse(media._gate)
            self.assertEqual(media.queue.duration_ms, 0)
            # Repeated close while the driver still hangs must report failure.
            with self.assertRaises(TimeoutError):
                await asyncio.wait_for(media.close(), 1)
            release.set()
            media.shutdown_timeout = 1
            if pending:
                await pending
            await asyncio.wait_for(media.close(), 1)
            await media.close()
            self.assertFalse(media.capture.is_running)
            self.assertIsNone(media._capture_operation)
        finally:
            release.set()
            media.shutdown_timeout = 1
            if pending:
                await pending
            # Cleanup also on the unfixed baseline, where close skips logs.
            await media.logs.shutdown()
            await media.close()
            original_stop()

    async def test_native_operation_timeout_closes_logs_and_retries_cleanup(self):
        await self.assert_timeout_cleans_logs_and_retry("operation")

    async def test_native_stop_timeout_closes_logs_and_retries_cleanup(self):
        await self.assert_timeout_cleans_logs_and_retry("stop")

    async def test_cancelled_close_still_cleans_logs_and_can_retry(self):
        media, socket = await self.start()
        await until(lambda: media.logs.active_transport_count == 1)
        log_task = media.logs._transport_task
        entered, release = threading.Event(), threading.Event()
        def blocked():
            entered.set()
            release.wait(3)
        pending = asyncio.create_task(media._capture_call(blocked))
        closing = None
        try:
            await until(entered.is_set)
            closing = asyncio.create_task(media.close())
            await until(lambda: media._closed and media._task is None)
            closing.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await closing
            self.assertEqual(media.logs.active_transport_count, 0)
            self.assertTrue(log_task.done())
            release.set()
            await pending
            await media.close()
            self.assertFalse(media.capture.is_running)
        finally:
            release.set()
            await pending
            if closing:
                await asyncio.gather(closing, return_exceptions=True)
            await media.close()

    async def assert_cancel_during_task_join_cleans_logs(self, method):
        entered, release = asyncio.Event(), asyncio.Event()
        original = getattr(V2MediaConnection, method)
        async def held_cleanup(instance):
            try:
                await original(instance)
            finally:
                entered.set()
                await release.wait()
        with patch.object(V2MediaConnection, method, held_cleanup):
            media, socket = await self.start()
        await until(lambda: media.logs.active_transport_count == 1)
        log_task, expiry_task = media.logs._transport_task, media.logs._expiry_task
        stopped = asyncio.Event()
        original_stop = media.session.stop
        async def stop():
            await original_stop()
            stopped.set()
        media.session.stop = stop
        closing = asyncio.create_task(media.close())
        try:
            await asyncio.wait_for(stopped.wait(), 1)
            await asyncio.wait_for(entered.wait(), 1)
            self.assertFalse(closing.done())
            closing.cancel()
            release.set()
            with self.assertRaises(asyncio.CancelledError):
                await asyncio.wait_for(closing, 1)
            self.assertEqual(media.logs.active_transport_count, 0)
            self.assertTrue(log_task.done() and expiry_task.done())
            self.assertFalse(media._cleanup_complete)
            self.assertFalse(media._gate)
            await media.close()
            self.assertTrue(media._cleanup_complete)
            self.assertFalse(media.capture.is_running)
        finally:
            release.set()
            await asyncio.gather(closing, return_exceptions=True)
            await media.logs.shutdown()
            await media.close()

    async def test_cancel_during_sender_join_cleans_logs_and_retries(self):
        await self.assert_cancel_during_task_join_cleans_logs("_send")

    async def test_cancel_during_lifecycle_join_cleans_logs_and_retries(self):
        await self.assert_cancel_during_task_join_cleans_logs("_lifecycle")

    async def test_repeated_cancel_during_logclose_joins_cleanup_before_raising(self):
        media, socket = await self.start()
        await until(lambda: media.logs.active_transport_count == 1)
        log_task, expiry_task = media.logs._transport_task, media.logs._expiry_task
        transport = media.logs._transport
        entered, release = asyncio.Event(), asyncio.Event()
        original = transport.stop
        async def held_stop():
            entered.set()
            await release.wait()
            await original()
        transport.stop = held_stop
        closing = asyncio.create_task(media.close())
        try:
            await asyncio.wait_for(entered.wait(), 1)
            closing.cancel()
            await asyncio.sleep(0)
            closing.cancel()
            release.set()
            with self.assertRaises(asyncio.CancelledError):
                await asyncio.wait_for(closing, 1)
            # Detaching a log transport is not sufficient: its tasks must exit.
            self.assertTrue(log_task.done() and expiry_task.done())
            self.assertEqual(transport.stop_calls, 1)
            self.assertEqual(media.logs.active_transport_count, 0)
            self.assertFalse(media._cleanup_complete)
            await media.close()
            self.assertTrue(media._cleanup_complete)
        finally:
            release.set()
            await asyncio.gather(closing, return_exceptions=True)
            # Explicitly clean captured detached resources on the old baseline.
            await original()
            for task in (log_task, expiry_task):
                task.cancel()
            await asyncio.gather(log_task, expiry_task, return_exceptions=True)
            await media.close()

    async def test_task_join_timeout_cleans_logs_and_retains_task_for_retry(self):
        entered, release = asyncio.Event(), asyncio.Event()
        original = V2MediaConnection._send
        async def held_cleanup(instance):
            try:
                await original(instance)
            finally:
                entered.set()
                await release.wait()
        with patch.object(V2MediaConnection, "_send", held_cleanup):
            media, socket = await self.start()
        await until(lambda: media.logs.active_transport_count == 1)
        sender = media._sender
        media.shutdown_timeout = .1
        try:
            with self.assertRaises(TimeoutError):
                await asyncio.wait_for(media.close(), 1)
            self.assertTrue(entered.is_set())
            self.assertFalse(sender.done())
            self.assertIs(media._sender, sender)
            self.assertEqual(media.logs.active_transport_count, 0)
            self.assertFalse(media._cleanup_complete)
            release.set()
            media.shutdown_timeout = 1
            await media.close()
            self.assertTrue(sender.done())
            self.assertTrue(media._cleanup_complete)
        finally:
            release.set()
            media.shutdown_timeout = 1
            await media.close()

    async def test_logclose_timeout_retains_pending_cleanup_for_retry(self):
        media, socket = await self.start()
        await until(lambda: media.logs.active_transport_count == 1)
        log_task, expiry_task = media.logs._transport_task, media.logs._expiry_task
        entered, release = asyncio.Event(), asyncio.Event()
        original = media.logs.shutdown
        async def held_shutdown():
            entered.set()
            await release.wait()
            await original()
        media.logs.shutdown = held_shutdown
        media.shutdown_timeout = .1
        try:
            with self.assertRaises(TimeoutError):
                await asyncio.wait_for(media.close(), 4)
            self.assertTrue(entered.is_set())
            pending = media._log_shutdown_task
            self.assertFalse(pending.done())
            self.assertFalse(media._cleanup_complete)
            release.set()
            await media.close()
            self.assertIs(media._log_shutdown_task, pending)
            self.assertTrue(pending.done() and log_task.done() and expiry_task.done())
            self.assertEqual(media.logs.active_transport_count, 0)
            self.assertTrue(media._cleanup_complete)
        finally:
            release.set()
            media.shutdown_timeout = 1
            await media.close()

    async def test_real_capture_callback_processing_and_packet_flow(self):
        capture = AudioCapture(AudioConfig())
        class Stream:
            active = True
            def __init__(self, **kwargs): pass
            def start(self): pass
            def stop(self): self.active = False
            def close(self): pass
        with patch("sounddevice.query_devices", return_value={"name":"synthetic", "default_samplerate":16000}), patch("sounddevice.check_input_settings"), patch("sounddevice.InputStream", Stream):
            media, socket = await self.start(capture=capture)
            capture._audio_callback(np.full((640,1),123,dtype=np.int16),640,None,None)
            await until(lambda: media.sent == 1)
            packet = next(p.decode_audio_packet(x) for x in socket.sent if isinstance(x,bytes))
            self.assertEqual(packet.pcm,b"{\0" * 640)
            self.assertEqual(packet.metadata["frames"],640)
            await media.close()

    async def test_thread_burst_coalesces_handles_and_bounds_pcm(self):
        media, socket = await self.start()
        callback = media.capture.on_audio_packet
        def burst():
            for n in range(2000):
                callback(b"\0\0" * 640,16000,1,640)
        # Block the core loop deliberately while producer runs.
        with patch.object(media._loop,"call_soon_threadsafe",wraps=media._loop.call_soon_threadsafe) as wake:
            thread = threading.Thread(target=burst)
            thread.start()
            thread.join(2)
            self.assertFalse(thread.is_alive())
            self.assertEqual(wake.call_count,1)
            self.assertLessEqual(media.queue.duration_ms,500)
        await until(lambda: media.sent > 0)
        self.assertGreater(media.counters()["overflow"],0)

    async def test_sustained_slow_socket_overflow_recycles_transport(self):
        media, socket = await self.start()
        old = media.session.binding
        original = socket.send
        async def slow(wire):
            if isinstance(wire, bytes):
                # While one bounded send is pending, simulate capture backlog.
                for _ in range(20):
                    media.capture.emit()
                await asyncio.sleep(.002)
            await original(wire)
        socket.send = slow
        media.capture.emit()
        await until(lambda: media.session.status.reason == "sustained_audio_overflow" or media.session.binding is not old)
        self.assertFalse(media._gate)
        self.assertGreater(media.queue.overflow,0)

    async def test_mute_during_bootstrap_is_acked_before_desired_suppression(self):
        entered, release = asyncio.Event(), asyncio.Event()
        holder = {}
        async def settings(session, binding):
            holder["session"] = session
            entered.set()
            await release.wait()
        # Attach explicitly so the hardware input is available during bootstrap.
        socket = Socket()
        async def connector(*args, **kwargs): return socket
        session = V2STTSession(connector=connector)
        logs = DualSessionCoordinator(ServerConfig(),EventStreamConfig(enabled=False))
        media = V2MediaConnection(session,Capture(),logs=logs,settings_bootstrap=settings,recovery_interval=.01)
        task = asyncio.create_task(session.run())
        self.addAsyncCleanup(self.join,task)
        self.addAsyncCleanup(media.close)
        await entered.wait()
        media.set_hardware_muted(True)
        release.set()
        await until(lambda: session.is_ready)
        commands = socket.commands
        self.assertEqual([c["type"] for c in commands[:2]],["audio_availability.set","trigger_suppression.set"])
        self.assertFalse(commands[0]["audioAvailable"])
        self.assertFalse(media.capture.is_running)


class ScopedCursor(unittest.TestCase):
    def test_integer_and_opaque_log_ids_are_diagnostic_only(self):
        for value in (7,"recording-7",p.new_id()):
            raw=event_message(3,"e3",replay=True)["event"]
            raw["segmentId"]=value
            envelope=EventEnvelope.from_mapping(raw)
            self.assertEqual(envelope.segment_id,value)
            self.assertNotIn("activationId",envelope.extra)
    def test_cursor_is_bound_to_session_filter_origin_and_instance(self):
        with tempfile.TemporaryDirectory() as directory:
            store = EventCursorStore(Path(directory)/"cursor.json")
            processor = EventProtocolProcessor(access(), cursor_store=store)
            enter_replay(processor)
            result = processor.process_mapping(event_message(3,"e3",replay=True))
            processor.confirm_event(result)
            self.assertEqual(processor.begin_subscription(),3)
            for change in ({"session_id":"other"}, {"channels":("audit",)},
                           {"server_instance_id":"other"}, {"endpoint":"wss://other.example/ws/logs"}):
                changed = EventProtocolProcessor(access(**change),cursor_store=store)
                self.assertEqual(changed.begin_subscription(),0)

    def test_legacy_unscoped_cursor_is_preserved_but_not_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            store = EventCursorStore(Path(directory)/"cursor.json")
            old = store.commit(10,endpoint=access().endpoint,server_instance_id="server-1",protocol_version=2)
            self.assertEqual(EventProtocolProcessor(access(),cursor_store=store).begin_subscription(),0)
            self.assertEqual(store.load(endpoint=access().endpoint,server_instance_id="server-1",protocol_version=2),old)

    def test_retention_gap_does_not_jump_confirmation_cursor(self):
        processor = EventProtocolProcessor(access())
        enter_replay(processor)
        processor.process_mapping({"type":"log.gap","reason":"retention","lostFromCursor":1,
                                  "lostToCursor":8,"oldestCursor":9,"latestCursor":20})
        self.assertEqual(processor.resume_cursor,0)
        result = processor.process_mapping(event_message(15,"survivor",replay=True))
        processor.confirm_event(result)
        self.assertEqual(processor.resume_cursor,15)


class LogBootstrap(unittest.IsolatedAsyncioTestCase):
    async def test_log_connection_error_redacts_token_and_keeps_diagnostics(self):
        current = access()
        async def connector(*args, **kwargs):
            raise OSError("synthetic failure for " + current.access_token)
        transport = EventStreamTransport(EventStreamConfig(), current, EventProtocolProcessor(current),
                                         on_event=lambda result: True, connect_factory=connector)
        task = asyncio.create_task(transport.run())
        try:
            with self.assertLogs("eventstream", level="WARNING") as captured:
                await until(lambda: transport.last_error is not None)
            self.assertNotIn(current.access_token, " ".join(captured.output))
            self.assertNotIn(current.access_token, transport.last_error)
            self.assertIn("synthetic failure", transport.last_error)
        finally:
            await transport.stop()
            await task

    async def test_unavailable_without_capability_fields_or_token(self):
        logs = DualSessionCoordinator(ServerConfig(),EventStreamConfig(cursor_persistence_enabled=False))
        self.addAsyncCleanup(logs.shutdown)
        await logs.begin_generation(1)
        self.assertFalse(await logs.adopt_hello(1,{"sessionId":"s1","logAccess":{"available":False,"code":"disabled"}}))
        self.assertIsNone(logs.context.log_access)

    async def test_both_paths_reject_foreign_origin_before_token_transport(self):
        for field in ("websocketPath","historyPath"):
            logs = DualSessionCoordinator(ServerConfig(),EventStreamConfig(cursor_persistence_enabled=False),transport_factory=FakeEventTransport)
            self.addAsyncCleanup(logs.shutdown)
            await logs.begin_generation(1)
            payload = hello("s1")
            payload["logAccess"][field] = "//attacker.example/path"
            with self.assertRaises(ValueError):
                await logs.adopt_hello(1,payload)
            self.assertEqual(logs.transport_start_count,0)

    async def test_stale_runtime_delivery_rejected_with_diagnostics_preserved(self):
        logs = DualSessionCoordinator(ServerConfig(),EventStreamConfig(cursor_persistence_enabled=False),transport_factory=FakeEventTransport)
        self.addAsyncCleanup(logs.shutdown)
        await logs.begin_generation(1)
        await logs.adopt_hello(1,hello("s1"))
        old = logs._binding
        await logs.begin_generation(2)
        seen = []
        logs.on_observation = lambda *args: seen.append(args)
        self.assertFalse(await logs._handle_event(old,event_result("s1")))
        logs._handle_control(old,event_result("s1"))
        self.assertEqual(len(seen),2)


if __name__ == "__main__":
    unittest.main()
