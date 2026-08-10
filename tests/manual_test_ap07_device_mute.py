"""The reSpeaker's own mute line, exercised on the device.

X0D30 drives the mute LED and the microphone mute together, high meaning muted.
It is reached through GPO_WRITE_VALUE, which takes an index into the same order
GPO_READ_VALUES reports: X0D11, X0D30, X0D31, X0D33, X0D39.

Two of the neighbours are not things to write by accident -- index 2 is the
amplifier enable and index 3 is the power to the LED ring -- so this reads all
five levels and checks the layout looks like the documented one before it writes
anything at all.

    python tests/manual_test_ap07_device_mute.py
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import LedConfig  # noqa: E402
from core.feedback_mapping import LedCall, LedVerb  # noqa: E402
from core.led_controller import MUTE_PIN_INDEX, MUTE_PIN_NAME  # noqa: E402
from ui.led_feedback import LedFeedback  # noqa: E402

PIN_NAMES = ("X0D11", "X0D30", "X0D31", "X0D33", "X0D39")
RING_POWER_INDEX = 3


def read_pins(feedback: LedFeedback):
    transport = feedback.controller._transport()
    if transport is None or not transport.is_connected:
        return None
    return transport.read("GPO_READ_VALUES")


def main() -> int:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

    problems: list[str] = []
    feedback = LedFeedback(LedConfig(enabled=True, sink="respeaker", brightness=32))

    try:
        # Bring the ring up first, so "the normal LEDs go out" is observable.
        feedback.submit((LedCall(LedVerb.SET_STATE, target="listening"),), live=True)
        time.sleep(2.0)

        levels = read_pins(feedback)
        if levels is None:
            print("Kein Geraet erreichbar -- Test uebersprungen.")
            return 0

        print("GPO-Pins vor dem Schreiben:")
        for index, name in enumerate(PIN_NAMES):
            mark = "  <- Mute" if index == MUTE_PIN_INDEX else ""
            print(f"   [{index}] {name} = {levels[index]}{mark}")

        if len(levels) != len(PIN_NAMES):
            print(f"ABBRUCH: {len(levels)} Pins statt {len(PIN_NAMES)}.")
            return 1
        if not levels[RING_POWER_INDEX]:
            # The ring is lit, so its power line must read high. If it does not,
            # the order is not what is assumed and writing would be a guess.
            print(
                f"ABBRUCH: {PIN_NAMES[RING_POWER_INDEX]} ist low, obwohl der Ring "
                "leuchtet -- die Pin-Reihenfolge stimmt nicht mit der Annahme."
            )
            return 1
        print(f"   Layout plausibel, {MUTE_PIN_NAME} wird geschrieben.\n")

        print("stummschalten ...")
        if not feedback.set_device_mute(True):
            problems.append("die Mute-Leitung wurde nicht erreicht")
        time.sleep(2.5)
        after = read_pins(feedback)
        print(f"   {MUTE_PIN_NAME} = {after[MUTE_PIN_INDEX]} (erwartet 1)")
        print(f"   gelesener Zustand: {feedback.device_mute()}")
        if not after[MUTE_PIN_INDEX]:
            problems.append("die Mute-Leitung blieb low")
        for index in (RING_POWER_INDEX, 2):
            if after[index] != levels[index]:
                problems.append(f"{PIN_NAMES[index]} hat sich mitveraendert")

        print("\nStummschaltung aufheben ...")
        feedback.set_device_mute(False)
        time.sleep(2.5)
        restored = read_pins(feedback)
        print(f"   {MUTE_PIN_NAME} = {restored[MUTE_PIN_INDEX]} (erwartet 0)")
        if restored[MUTE_PIN_INDEX]:
            problems.append("die Mute-Leitung blieb high")
        if list(restored) != list(levels):
            problems.append(f"Pins nicht wie vorher: {list(levels)} -> {list(restored)}")
    finally:
        stopped = feedback.shutdown()

    print()
    print(f"sauber beendet : {stopped}")
    print(f"befund         : {problems or 'alles wie erwartet'}")
    return 1 if problems or not stopped else 0


if __name__ == "__main__":
    raise SystemExit(main())
