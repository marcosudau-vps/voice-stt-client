"""Losing the output in mid-session, and getting it back, without a cable.

The physical test is to unplug the reSpeaker and plug it in again. This is the
same journey for everything above the transport: the simulator's "device" is a
ring window that dials in over a loopback socket, so closing it is a genuine
disconnect and reopening it a genuine reconnect. What is exercised is the part
that belongs to this application -- the sink report, the once-per-outage
notification, the clock the simulation offer reads, and recovery -- rather than
LEFX's USB reconnect, which is LEFX's own business.

    python tests/manual_test_ap07_led_disconnect.py
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import LedConfig  # noqa: E402
from core.feedback_mapping import LedCall, LedVerb  # noqa: E402
from ui.led_feedback import LedFeedback  # noqa: E402

STATE = LedCall(LedVerb.SET_STATE, target="listening")


def wait_for(predicate, what: str, timeout: float = 20.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.2)
    print(f"  ZEITUEBERSCHREITUNG beim Warten auf: {what}")
    return False


def start_window() -> subprocess.Popen:
    environment = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    return subprocess.Popen(
        [str(Path(sys.executable).parent / "lefx-simulator.exe")],
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> int:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

    reports: list[str] = []
    feedback = LedFeedback(
        LedConfig(enabled=True, sink="simulator", brightness=32),
        on_failure=reports.append,
    )

    problems: list[str] = []
    window: subprocess.Popen | None = None

    def beat() -> None:
        """Keep feedback flowing, the way a session would."""
        feedback.submit((STATE,), live=True)

    try:
        print("1. kein Fenster -> Ausgang muss als weg gelten")
        beat()
        if not wait_for(lambda: feedback.unavailable_seconds > 0, "Ausfallmeldung"):
            problems.append("Ausfall wurde nicht gemeldet")
        if reports != ["unavailable"]:
            problems.append(f"erwartete genau eine Meldung, bekam {reports}")
        print(f"   Meldungen: {reports}, Uhr: {feedback.unavailable_seconds:.1f}s")

        print("2. Uhr laeuft weiter, obwohl Befehle durchgehen")
        before = feedback.unavailable_seconds
        for _ in range(3):
            beat()
            time.sleep(0.4)
        if not feedback.unavailable_seconds > before:
            problems.append("die Uhr wurde von gelungenen Befehlen zurueckgesetzt")
        print(f"   Uhr: {before:.1f}s -> {feedback.unavailable_seconds:.1f}s")

        print("3. Fenster oeffnen -> Erholung ohne Zutun")
        window = start_window()
        if not wait_for(
            lambda: (beat() or True) and feedback.unavailable_seconds == 0.0,
            "Erholung",
        ):
            problems.append("Erholung blieb aus")
        print(f"   Uhr zurueck auf {feedback.unavailable_seconds:.1f}s")

        print("4. Fenster hart beenden -> zweite, getrennte Ausfallmeldung")
        window.kill()
        window.wait(timeout=10)
        window = None
        if not wait_for(
            lambda: (beat() or True) and len(reports) == 2, "zweite Meldung"
        ):
            problems.append(f"zweite Meldung blieb aus, Meldungen={reports}")
        print(f"   Meldungen: {reports}")

        print("5. Fenster erneut oeffnen -> zweite Erholung")
        window = start_window()
        if not wait_for(
            lambda: (beat() or True) and feedback.unavailable_seconds == 0.0,
            "zweite Erholung",
        ):
            problems.append("zweite Erholung blieb aus")
        if len(reports) != 2:
            problems.append(f"Meldungen liefen ueber: {reports}")
        print(f"   Meldungen unveraendert: {reports}")
    finally:
        if window is not None:
            window.kill()
            window.wait(timeout=10)
        stopped = feedback.shutdown()

    print()
    print(f"sauber beendet : {stopped}")
    if not stopped:
        problems.append("der Worker hat nicht angehalten")
    print(f"befund         : {problems or 'alles wie erwartet'}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
