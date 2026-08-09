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

    def __init__(self, audio_config):
        self._config = audio_config
        self._stream: Optional[sd.InputStream] = None
        self._running = False

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

        # Open the audio stream
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

        logger.info(
            "Audio capture started: device=%s, rate=%d, channels=%d, chunk=%dms (%d frames)",
            device_name,
            self._device_sample_rate,
            channels,
            self._config.chunk_duration_ms,
            chunk_frames,
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
        if status:
            if status.input_overflow:
                logger.debug("Audio input overflow.")
            if status.input_underflow:
                logger.debug("Audio input underflow.")

        # Convert to bytes (already int16 due to dtype="int16")
        pcm_bytes = indata.tobytes()

        try:
            self._audio_queue.put_nowait(pcm_bytes)
        except queue.Full:
            logger.debug("Audio queue full, dropping chunk.")

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

            if self.on_audio_packet is None:
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
