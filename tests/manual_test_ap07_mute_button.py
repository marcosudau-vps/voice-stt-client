"""What the mute button on the device actually does, measured rather than assumed.

The pin table says X1D09 is the button (input, read-only) and X0D30 is the
effect (output, read-write). It does not say whether the firmware connects the
two by itself. The protocol offers no way to read input pins, so the button
cannot be observed directly -- but its consequences can.

Two things are watched at once, because that is what tells the three cases apart:

  pin changes + audio stops  -> the firmware drives the line; the client has to
                                follow it, or it will disagree with the device
  pin unchanged + audio stops -> the firmware mutes invisibly; nothing on this
                                interface can detect it
  pin unchanged + audio flows -> the button does nothing without host software

Press the mute button on the reSpeaker when asked. Nothing is written to the
device here; this only reads.

    python tests/manual_test_ap07_mute_button.py
"""

from __future__ import annotations

import logging
import math
import struct
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.audio_capture import AudioCapture  # noqa: E402
from core.config import AppConfig, LedConfig  # noqa: E402
from core.led_controller import MUTE_PIN_INDEX, MUTE_PIN_NAME  # noqa: E402
from ui.led_feedback import LedFeedback  # noqa: E402

PIN_NAMES = ("X0D11", "X0D30", "X0D31", "X0D33", "X0D39")
WATCH_S = 25.0
SILENCE_RMS = 30.0
"""Below this the microphone is producing nothing worth calling signal."""


def rms(pcm: bytes) -> float:
    count = len(pcm) // 2
    if not count:
        return 0.0
    samples = struct.unpack(f"<{count}h", pcm[: count * 2])
    return math.sqrt(sum(value * value for value in samples) / count)


def main() -> int:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    config = AppConfig.load()

    feedback = LedFeedback(LedConfig(enabled=True, sink="respeaker", brightness=24))
    capture = AudioCapture(config.audio)
    levels: list[float] = []
    capture.on_audio_packet = lambda pcm, *_: levels.append(rms(pcm))

    transport = feedback.controller._transport()
    if transport is None:
        print("Kein ReSpeaker-Sink -- Test uebersprungen.")
        return 0
    for _ in range(50):
        if transport.is_connected:
            break
        time.sleep(0.2)
    if not transport.is_connected:
        print("ReSpeaker nicht erreichbar -- Test uebersprungen.")
        return 0

    start_pins = tuple(transport.read("GPO_READ_VALUES"))
    print("GPO-Pins zu Beginn:")
    for index, name in enumerate(PIN_NAMES):
        mark = "  <- Mute" if index == MUTE_PIN_INDEX else ""
        print(f"   [{index}] {name} = {start_pins[index]}{mark}")

    capture.start()
    time.sleep(1.5)
    print()
    print(f">>> Bitte jetzt die Mute-Taste am ReSpeaker druecken. {WATCH_S:.0f} s Zeit. <<<")
    print()

    changes: list[tuple[float, int]] = []
    audio_windows: list[tuple[float, float]] = []
    last = start_pins[MUTE_PIN_INDEX]
    started = time.monotonic()
    next_window = started + 1.0

    try:
        while time.monotonic() - started < WATCH_S:
            now = time.monotonic()
            try:
                pins = tuple(transport.read("GPO_READ_VALUES"))
            except Exception:
                time.sleep(0.3)
                continue
            if pins[MUTE_PIN_INDEX] != last:
                last = pins[MUTE_PIN_INDEX]
                changes.append((now - started, last))
                print(f"   {now - started:5.1f}s  {MUTE_PIN_NAME} -> {last}")
            if now >= next_window:
                window, levels[:] = levels[:], []
                loudest = max(window) if window else 0.0
                audio_windows.append((now - started, loudest))
                next_window = now + 1.0
            time.sleep(0.15)
    finally:
        capture.stop()
        feedback.shutdown()

    quiet = [t for t, level in audio_windows if level < SILENCE_RMS]
    loud = [t for t, level in audio_windows if level >= SILENCE_RMS]

    print()
    print(f"Pinwechsel      : {changes or 'keine'}")
    print(f"Audiofenster    : {len(audio_windows)}, davon still: {len(quiet)}")
    if audio_windows:
        print(
            "Pegelverlauf    : "
            + " ".join(f"{level:.0f}" for _, level in audio_windows)
        )
    print()

    if changes:
        print("BEFUND: Die Firmware legt X0D30 beim Tastendruck selbst um.")
        print("        Der Client muss den Pin beobachten und sich angleichen,")
        print("        sonst widersprechen sich Geraet und Anwendung.")
    elif quiet and loud:
        print("BEFUND: Der Pin bleibt unveraendert, aber der Ton setzt aus.")
        print("        Die Firmware schaltet unsichtbar stumm -- ueber diese")
        print("        Schnittstelle nicht erkennbar.")
    else:
        print("BEFUND: Weder Pin noch Ton haben sich geaendert.")
        print("        Entweder wurde nicht gedrueckt, oder die Taste wirkt")
        print("        ohne Hostsoftware nicht.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
