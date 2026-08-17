"""
Microphone audio capture for the RealtimeSTT client.

Captures PCM audio from the system microphone using sounddevice,
packages it into binary packets per the server protocol, and
delivers them via an async callback.

This module has ZERO UI dependencies and can be tested headless.
"""

from __future__ import annotations

import asyncio
import logging
import queue
import struct
import json
import threading
from typing import Callable, Optional

import numpy as np
import sounddevice as sd

from core.observability.adapters.client_events import ClientEventEmitter
from core.observability.ingress import NULL_INGRESS

logger = logging.getLogger("audio")


class AudioCapture:
    """
    Captures audio from the system microphone and produces binary packets
    ready for the WebSocket protocol.

    Usage:
        capture = AudioCapture(config.audio)
        capture.on_audio_packet = my_callback  # receives (packet_bytes,)
        capture.start()
        ...
        capture.stop()
    """

    def __init__(self, audio_config, *, observability=NULL_INGRESS):
        self._config = audio_config
        self._observe = ClientEventEmitter(observability, component="audio")
        self._stream: Optional[sd.InputStream] = None
        self._running = False
        self._muted = False

        # ARCH §8.6 hot-path counters. Plain ``int`` attributes, incremented
        # WITHOUT a lock: a lost increment is inconsequential, a lock in the
        # PortAudio callback is not. Read by the LoggingWorker every 5 s
        # (``client.audio.stream_stats``), never by the hot path itself.
        self.chunks_captured = 0
        self.chunks_dropped_capture_queue = 0
        self.overflow_count = 0
        self.underflow_count = 0

        # Actual device sample rate (may differ from preferred)
        self._device_sample_rate: int = audio_config.sample_rate

        # Thread-safe queue for audio chunks
        self._audio_queue: queue.Queue[Optional[bytes]] = queue.Queue(maxsize=200)

        # Async callback: receives the fully encoded binary packet
        self.on_audio_packet: Optional[Callable[[bytes, int, int, int], None]] = None

        # Processing thread
        self._thread: Optional[threading.Thread] = None

    @property
    def sample_rate(self) -> int:
        """The actual sample rate being used by the device."""
        return self._device_sample_rate

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def muted(self) -> bool:
        return self._muted

    def set_muted(self, muted: bool) -> None:
        """Stop or resume passing captured audio on.

        The stream keeps running while muted, and packets are dropped on their
        way out. Closing the device instead would be the obvious reading of
        "mute" and the wrong one: reopening takes long enough to be noticed, it
        can fail if something else took the device meanwhile, and a mute that
        might not come back is worse than no mute at all.

        Dropping rather than sending silence, because silence is a recording.
        A muted microphone should produce nothing for the server to transcribe,
        bill for, or keep.
        """
        self._muted = bool(muted)
        logger.info("Microphone %s.", "muted" if self._muted else "unmuted")

    # -------------------------------------------------------------------
    # Device management
    # -------------------------------------------------------------------

    @staticmethod
    def list_devices() -> list[dict]:
        """List available audio input devices."""
        devices = sd.query_devices()
        result = []
        for i, dev in enumerate(devices):
            if dev["max_input_channels"] > 0:
                result.append({
                    "index": i,
                    "name": dev["name"],
                    "channels": dev["max_input_channels"],
                    "default_samplerate": dev["default_samplerate"],
                    "is_default": i == sd.default.device[0],
                })
        return result

    # -------------------------------------------------------------------
    # Start / Stop
    # -------------------------------------------------------------------

    def start(self) -> None:
        """Start capturing audio from the microphone."""
        if self._running:
            logger.warning("AudioCapture already running.")
            return

        device_id = self._config.device  # None = system default
        channels = self._config.channels
        preferred_rate = self._config.sample_rate

        # Query the actual device to determine supported sample rate
        try:
            device_info = sd.query_devices(device_id, kind="input")
            device_name = device_info["name"]
            default_rate = int(device_info["default_samplerate"])
        except Exception:
            logger.exception("Failed to query audio device.")
            raise

        # Try preferred rate first, fall back to device default
        self._device_sample_rate = preferred_rate
        try:
            sd.check_input_settings(
                device=device_id,
                channels=channels,
                dtype=self._config.dtype,
                samplerate=preferred_rate,
            )
            logger.info(
                "Using preferred sample rate %d Hz on '%s'.",
                preferred_rate, device_name,
            )
        except sd.PortAudioError:
            self._device_sample_rate = default_rate
            logger.info(
                "Device '%s' doesn't support %d Hz, using default %d Hz (server will resample).",
                device_name, preferred_rate, default_rate,
            )

        chunk_frames = int(
            self._device_sample_rate * self._config.chunk_duration_ms / 1000
        )

        self._running = True

        # Clear the queue
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                break

        # Everything that can fail lives in here, and anything that does leaves
        # the object exactly as it was found. Without that, a device busy for a
        # moment at startup is permanent: the flag stays set, no stream is ever
        # opened, and every later attempt returns "already running" -- a
        # microphone that never comes back for the rest of the session.
        try:
            self._stream = sd.InputStream(
                device=device_id,
                channels=channels,
                samplerate=self._device_sample_rate,
                blocksize=chunk_frames,
                dtype=self._config.dtype,
                callback=self._audio_callback,
            )
            self._stream.start()

            # Start the processing thread
            self._thread = threading.Thread(
                target=self._process_loop,
                name="audio-process",
                daemon=True,
            )
            self._thread.start()
        except Exception:
            self._running = False
            stream, self._stream = self._stream, None
            self._thread = None
            if stream is not None:
                try:
                    stream.close()
                except Exception:
                    logger.debug("Could not close the half-open stream.", exc_info=True)
            raise

        logger.info(
            "Audio capture started: device=%s, rate=%d, channels=%d, chunk=%dms (%d frames)",
            device_name,
            self._device_sample_rate,
            channels,
            self._config.chunk_duration_ms,
            chunk_frames,
        )
        # CONTRACTS §12.2: client.audio.stream_started (P+S). ARCH §8.6 allows
        # exactly this -- a record on a STATE CHANGE, never per chunk. Not on
        # the hot path: ``start()`` runs once per dictation.
        self._observe.audit(
            "client.audio.stream_started",
            details={
                "sample_rate": self._device_sample_rate,
                "channels": channels,
                "chunk_duration_ms": self._config.chunk_duration_ms,
                "chunk_frames": chunk_frames,
                "requested_sample_rate": preferred_rate,
            },
        )

    def stop(self) -> None:
        """Stop capturing audio."""
        if not self._running:
            return

        self._running = False

        # Signal the processing thread to stop
        try:
            self._audio_queue.put_nowait(None)
        except queue.Full:
            pass

        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                logger.debug("Error closing audio stream", exc_info=True)
            self._stream = None

        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

        logger.info("Audio capture stopped.")
        # CONTRACTS §12.2: client.audio.stream_stopped (P+S), with the final
        # counter state so a session's totals survive even if the last 5-second
        # aggregate never ran.
        self._observe.audit(
            "client.audio.stream_stopped",
            details=self.capture_counters(),
        )

    # -- ARCH §8.6: the read side of the hot-path counters ------------------

    def capture_counters(self) -> dict:
        """Snapshot of the capture-side counters. Called from the worker thread
        (through the registered aggregate source) and from ``stop()``.

        No lock: these are plain ``int`` reads of values written without a lock
        in the callback. A torn read cannot occur for a Python ``int``
        attribute, and a slightly stale value in a diagnostic aggregate is the
        deliberate trade §8.6 makes.
        """
        return {
            "chunks_captured": self.chunks_captured,
            "chunks_dropped_capture_queue": self.chunks_dropped_capture_queue,
            "overflow_count": self.overflow_count,
            "underflow_count": self.underflow_count,
            "capture_queue_depth": self._audio_queue.qsize(),
        }

    # -------------------------------------------------------------------
    # Internal: sounddevice callback (runs in audio thread)
    # -------------------------------------------------------------------

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info,
        status: sd.CallbackFlags,
    ) -> None:
        """
        Called by sounddevice for each audio chunk.
        Runs in the PortAudio callback thread – must be fast and non-blocking.
        """
        # ARCH §8.6: this function is on the hot-path list. Only int increments
        # here -- no observation call, no format, no json, no attribute access
        # on the observation boundary at all. Verified by a source-scanning
        # test, which is also why this comment avoids the forbidden words.
        if status:
            if status.input_overflow:
                self.overflow_count += 1
                logger.debug("Audio input overflow.")
            if status.input_underflow:
                self.underflow_count += 1
                logger.debug("Audio input underflow.")

        # Convert to bytes (already int16 due to dtype="int16")
        pcm_bytes = indata.tobytes()

        try:
            self._audio_queue.put_nowait(pcm_bytes)
        except queue.Full:
            self.chunks_dropped_capture_queue += 1
            logger.debug("Audio queue full, dropping chunk.")
        else:
            self.chunks_captured += 1

    # -------------------------------------------------------------------
    # Internal: processing thread
    # -------------------------------------------------------------------

    def _process_loop(self) -> None:
        """
        Drain the audio queue and invoke the callback.
        Runs in a separate thread to avoid blocking the audio callback.
        """
        while self._running:
            try:
                pcm_bytes = self._audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if pcm_bytes is None:
                break  # Stop signal

            if self.on_audio_packet is None or self._muted:
                # Drained and discarded: the queue must keep moving even while
                # muted, or unmuting would replay whatever piled up behind it.
                continue

            frames = len(pcm_bytes) // (self._config.channels * 2)  # int16 = 2 bytes

            try:
                self.on_audio_packet(
                    pcm_bytes,
                    self._device_sample_rate,
                    self._config.channels,
                    frames,
                )
            except Exception:
                logger.exception("Error in audio packet callback.")
