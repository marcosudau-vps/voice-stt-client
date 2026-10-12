"""Continuous V2 audio and observation-only log lifecycle (headless).

Attach before run, alongside V2MirrorConnection. Settings bootstrap and the Qt
composition are supplied by their owners. Audio callbacks use one bounded
thread-safe queue, never one asyncio handle/future per microphone packet.
"""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
import math
import threading
import time
from websockets.exceptions import ConnectionClosed

from . import protocol_v2 as p
from .command_tracker import CommandFailure
from .config import ServerConfig, EventStreamConfig
from .session_coordinator import DualSessionCoordinator
from .v2_transport import V2TransportState


@dataclass(frozen=True)
class AudioChunk:
    pcm: bytes = field(repr=False)
    rate: int
    channels: int
    frames: int
    created: float
    epoch: int


class BoundedAudioQueue:
    """Duration AND age bounded PCM handoff; format checked before admission."""

    def __init__(self, duration_ms=500, *, clock=time.monotonic):
        if isinstance(duration_ms, bool) or not isinstance(duration_ms, (int, float)) or not 0 < duration_ms <= 2000:
            raise ValueError("audio queue duration must be in (0, 2000] ms")
        self.limit = duration_ms / 1000
        self.clock = clock
        self._lock = threading.Lock()
        self._items = deque()
        self._duration = 0.
        self._bytes = 0
        self.overflow = self.stale = self.invalid = 0

    def put(self, pcm, rate, channels, frames, epoch):
        try:
            p.encode_audio_packet(pcm, rate, channels, frames)
            if type(frames) is not int or frames <= 0:
                raise p.ProtocolError("positive frames required")
        except (p.ProtocolError, TypeError, ValueError):
            self.invalid += 1
            return False
        duration = frames / rate
        with self._lock:
            if duration > self.limit:
                self.overflow += 1
                return False
            while self._items and (self._duration + duration > self.limit + 1e-9 or len(self._items) >= 128
                                   or self._bytes + len(pcm) > 4 * 1024 * 1024):
                old = self._items.popleft()
                self._duration -= old.frames / old.rate
                self._bytes -= len(old.pcm)
                self.overflow += 1
            self._items.append(AudioChunk(bytes(pcm), rate, channels, frames, self.clock(), epoch))
            self._duration += duration
            self._bytes += len(pcm)
        return True

    def pop(self, epoch):
        with self._lock:
            while self._items:
                item = self._items.popleft()
                self._duration -= item.frames / item.rate
                self._bytes -= len(item.pcm)
                if item.epoch == epoch and self.clock() - item.created <= self.limit:
                    return item
                self.stale += 1
            self._duration = 0.
            self._bytes = 0
        return None

    def clear(self):
        with self._lock:
            self.stale += len(self._items)
            self._items.clear()
            self._duration = 0.
            self._bytes = 0

    @property
    def duration_ms(self):
        with self._lock:
            return max(0., self._duration * 1000)


class V2MediaConnection:
    """Own capture/send/log tasks for exactly the transport's current binding.

    Device and mute inputs run on the core loop, with optional binding guards.
    LED availability has no audio/domain side effect. Audio failure sends only
    audio_availability.set; the server owns cancellation of the open input.
    Log callbacks are observation-only; never connect them to a V2 reducer or
    text injection. A failed log bootstrap cannot prevent audio readiness.
    """

    def __init__(self, session, capture, *, logs=None, settings_bootstrap=None,
                 queue_ms=500, recovery_interval=.25, shutdown_timeout=3):
        if session.binding is not None or session.bootstrap is not None:
            raise RuntimeError("attach media before run; pass settings_bootstrap here")
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v > 0
                   for v in (recovery_interval, shutdown_timeout)):
            raise ValueError("invalid media timeout")
        self.session, self.capture = session, capture
        self.logs = logs or DualSessionCoordinator(ServerConfig(url=session.config.url), EventStreamConfig())
        self.settings_bootstrap = settings_bootstrap
        self.queue = BoundedAudioQueue(queue_ms)
        bound_capture = getattr(capture, "bound_queue", None)
        if bound_capture is not None:
            bound_capture(queue_ms)
        self.recovery_interval, self.shutdown_timeout = recovery_interval, shutdown_timeout
        self.device_available = True
        self.hardware_muted = False
        self.led_available = True
        self.capture_available = False
        self.sent = self.gated = self.capture_failures = 0
        self.log_failure = None
        self._binding = None
        self._epoch = 0
        self._gate = False
        self._closed = False
        self._cleanup_complete = False
        self._close_lock = asyncio.Lock()
        self._wake = asyncio.Event()
        self._audio_wake = asyncio.Event()
        self._notify_lock = threading.Lock()
        self._notification_pending = False
        self._loop = None
        self._task = self._sender = None
        self._capture_operation = None
        self._log_shutdown_task = None
        self._reported_available = None
        self._overflow_at_last_send = 0
        self._overflow_streak = 0
        old_status, old_accepted, old_lost = session.on_status, session.on_accepted, session.on_lost

        def status(value):
            if value.state != V2TransportState.READY:
                self._block()
            self._ensure_tasks()
            self._wake.set()
            if old_status:
                old_status(value)

        def accepted(binding):
            self._wake.set()
            if old_accepted:
                old_accepted(binding)

        def lost(binding):
            self._block()
            self._wake.set()
            if old_lost:
                old_lost(binding)

        session.on_status, session.on_accepted, session.on_lost = status, accepted, lost
        session.bootstrap = self.bootstrap

    @property
    def audio_available(self):
        return self.device_available and self.capture_available and not self.hardware_muted

    def _block(self):
        self._gate = False
        self._epoch += 1
        self.queue.clear()

    def _ensure_tasks(self):
        if self._closed or self._task is not None:
            return
        self._loop = asyncio.get_running_loop()
        self._task = asyncio.create_task(self._lifecycle(), name="v2-media-lifecycle")
        self._sender = asyncio.create_task(self._send(), name="v2-audio-send")

    async def bootstrap(self, session, binding):
        # Probe without capture: no microphone frames before config-ready.
        try:
            probe = getattr(self.capture, "probe", None)
            if probe is not None and self.device_available and not self.hardware_muted:
                await self._capture_call(probe)
            available = self.device_available and not self.hardware_muted
        except Exception:
            available = False
            self.capture_failures += 1
        if not available:
            await session.bootstrap_command(binding, p.CommandType.AUDIO_AVAILABILITY, audioAvailable=False)
        self._reported_available = (binding, available)
        if self.settings_bootstrap:
            await self.settings_bootstrap(session, binding)
        # A mute/device change while settings awaited must be acknowledged
        # before the transport restores desired suppression and becomes ready.
        available = available and self.device_available and not self.hardware_muted
        if self._reported_available != (binding, available):
            await session.bootstrap_command(binding, p.CommandType.AUDIO_AVAILABILITY, audioAvailable=available)
            self._reported_available = (binding, available)

    def set_device_available(self, available, *, binding=None):
        return self._set_audio_input("device_available", available, binding)

    def set_hardware_muted(self, muted, *, binding=None):
        return self._set_audio_input("hardware_muted", muted, binding)

    def _set_audio_input(self, name, value, binding):
        if type(value) is not bool:
            raise ValueError("availability/mute must be boolean")
        if self._closed or binding is not None and binding is not self.session.binding:
            return False
        if getattr(self, name) != value:
            # Immediate local barrier, before any command await or device stop.
            self._block()
            setattr(self, name, value)
            self._wake.set()
        return True

    def set_led_available(self, available):
        if type(available) is not bool:
            raise ValueError("LED availability must be boolean")
        self.led_available = available

    def _packet_callback(self, binding, epoch):
        def packet(pcm, rate, channels, frames):
            if not self._gate or epoch != self._epoch or binding is not self.session.binding:
                self.gated += 1
                return
            if not self.queue.put(pcm, rate, channels, frames, epoch):
                return
            # At most one pending loop handle, even if the core loop stalls.
            with self._notify_lock:
                if self._notification_pending or self._closed:
                    return
                self._notification_pending = True
            try:
                self._loop.call_soon_threadsafe(self._notify_audio)
            except RuntimeError:
                with self._notify_lock:
                    self._notification_pending = False
        return packet

    def _notify_audio(self):
        with self._notify_lock:
            self._notification_pending = False
        self._audio_wake.set()

    async def _stop_capture(self):
        self._block()
        self.capture_available = False
        await self._capture_call(self.capture.stop)

    async def _capture_call(self, operation):
        # Cancelling the asyncio owner doesn't cancel a native PortAudio call.
        # Keep its task so close can join it before calling stop on the device.
        previous = self._capture_operation
        if previous is not None:
            await asyncio.shield(previous)
        task = self._capture_operation = asyncio.create_task(asyncio.to_thread(operation))
        try:
            return await asyncio.shield(task)
        finally:
            if task.done() and self._capture_operation is task:
                self._capture_operation = None

    async def _lifecycle(self):
        try:
            while not self._closed:
                self._wake.clear()
                binding = self.session.binding
                if binding is not self._binding:
                    await self._stop_capture()
                    previous = self._binding
                    self._binding = binding
                    try:
                        if previous:
                            await self.logs.invalidate_generation(previous.generation)
                        if binding:
                            await self.logs.begin_generation(binding.generation)
                            hello = binding.accepted.to_mapping()
                            if not binding.accepted.logAccess.available:
                                hello["logAccess"] = {"available": False, "code": "log_unavailable", "reason": "Log access unavailable"}
                            await self.logs.adopt_hello(binding.generation, hello)
                            self.log_failure = None
                    except Exception:
                        # No exception/raw credential is published.
                        self.log_failure = "log_bootstrap_invalid"
                if binding and self.session.is_ready:
                    if self.device_available and not self.hardware_muted:
                        if not self.capture.is_running or not getattr(self.capture, "device_active", True):
                            was_available = self.capture_available
                            self._block()
                            self.capture_available = False
                            if was_available:
                                await self._report_availability(binding, False)
                            await self._stop_capture()
                            try:
                                await self._capture_call(self.capture.start)
                                self.capture_available = True
                            except Exception:
                                self.capture_failures += 1
                        available = self.audio_available
                    else:
                        available = False
                        # A native stop can hang. The server must cancel its
                        # open input before we wait on that independent driver.
                        self._block()
                        self.capture_available = False
                        if self._reported_available != (binding, False):
                            await self._report_availability(binding, False)
                        await self._stop_capture()
                    if self._reported_available != (binding, available):
                        await self._report_availability(binding, available)
                    if available and self.session.binding is binding and self.session.is_ready:
                        # Reinstall after every local barrier; old callback epochs
                        # stay stale across mute, device and network recovery.
                        self.capture.on_audio_packet = self._packet_callback(binding, self._epoch)
                        self._gate = True
                elif self.capture.is_running:
                    await self._stop_capture()
                try:
                    await asyncio.wait_for(self._wake.wait(), self.recovery_interval)
                except TimeoutError:
                    pass
        except (CommandFailure, OSError, TimeoutError, ConnectionClosed):
            self._block()
            if not self._closed:
                await asyncio.sleep(self.recovery_interval)
                self._task = None
                self._ensure_tasks_after_failure()
        finally:
            self._block()

    def _ensure_tasks_after_failure(self):
        # Receiver/transport cleanup owns reconnect; restart only lifecycle.
        self._task = asyncio.create_task(self._lifecycle(), name="v2-media-lifecycle")

    async def _report_availability(self, binding, available):
        result = await self.session.request(p.CommandType.AUDIO_AVAILABILITY, binding=binding, audioAvailable=available)
        if not result.ack.accepted:
            self._block()
            await self.session.reconnect(binding, "audio_availability_rejected")
            raise CommandFailure("audio availability rejected")
        self._reported_available = (binding, available)

    def counters(self):
        return {"sent": self.sent, "gated": self.gated, "overflow": self.queue.overflow,
                "stale": self.queue.stale, "invalid": self.queue.invalid,
                "queue_ms": self.queue.duration_ms, "capture_failures": self.capture_failures,
                "audio_available": self.audio_available, "led_available": self.led_available,
                "log_failure": self.log_failure}

    async def _send(self):
        while not self._closed:
            await self._audio_wake.wait()
            self._audio_wake.clear()
            while self._gate and self.session.is_ready:
                item = self.queue.pop(self._epoch)
                if item is None:
                    break
                binding = self._binding
                try:
                    if await self.session.send_audio(item.pcm, item.rate, item.channels, item.frames, binding=binding):
                        self.sent += 1
                except (OSError, TimeoutError, CommandFailure, ConnectionClosed):
                    self._block()
                    break
                overflow = self.queue.overflow
                self._overflow_streak = self._overflow_streak + 1 if overflow > self._overflow_at_last_send else 0
                self._overflow_at_last_send = overflow
                if self._overflow_streak >= 3:
                    self._block()
                    await self.session.reconnect(binding, "sustained_audio_overflow")
                    break

    async def close(self):
        """Bounded independent cleanup; retry unfinished native shutdown.

        _closed blocks new work immediately; it does not claim cleanup success.
        A native timeout is propagated after log cleanup, retaining its task so
        the next close joins it before attempting another driver operation.
        """
        async with self._close_lock:
            if self._cleanup_complete:
                return
            self._closed = True
            self._block()
            self.capture_available = False
            self.capture.on_audio_packet = None
            try:
                try:
                    await self.session.stop()
                finally:
                    tasks = [task for task in (self._task, self._sender) if task]
                    for task in tasks:
                        if not task.done() and not task.cancelling():
                            task.cancel()
                    try:
                        await asyncio.wait_for(asyncio.shield(
                            asyncio.gather(*tasks, return_exceptions=True)), self.shutdown_timeout)
                    finally:
                        # Interrupted joins retain pending tasks for a later close.
                        if self._task is not None and self._task.done():
                            self._task = None
                        if self._sender is not None and self._sender.done():
                            self._sender = None
                    pending = self._capture_operation
                    if pending is not None:
                        try:
                            await asyncio.wait_for(asyncio.shield(pending), self.shutdown_timeout)
                        finally:
                            if pending.done() and self._capture_operation is pending:
                                self._capture_operation = None
                    await asyncio.wait_for(self._stop_capture(), self.shutdown_timeout)
            finally:
                # Every await above, including the task join, reaches log cleanup.
                await self._shutdown_logs()
            self._cleanup_complete = True

    async def _shutdown_logs(self):
        """Defer owner cancellation until bounded independent cleanup finishes.

        Shield the actual coordinator shutdown: it detaches resources before
        awaiting socket/task cleanup, so cancelling it would lose those handles.
        A timeout retains this same task for retry, rather than invoking the
        coordinator's already-marked-shutdown fast path a second time.
        """
        if self._log_shutdown_task is None:
            self._log_shutdown_task = asyncio.create_task(
                self.logs.shutdown(), name="v2-media-log-shutdown")
        pending = self._log_shutdown_task
        deadline = asyncio.get_running_loop().time() + self.shutdown_timeout + 3
        cancelled = None
        while True:
            try:
                remaining = max(0, deadline - asyncio.get_running_loop().time())
                await asyncio.wait_for(asyncio.shield(pending), remaining)
                break
            except asyncio.CancelledError as error:
                if pending.cancelled():
                    raise
                cancelled = error
                # Further owner cancellations cannot cancel the log task or
                # extend its fixed cleanup budget.
        if cancelled is not None:
            raise cancelled
