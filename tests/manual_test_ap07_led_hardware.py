"""Bounded smoke for the physically connected ReSpeaker LED ring.

Walks the states and announcements the shipped mapping actually uses, through
the same LedFeedback the application uses, and leaves the ring dark. Manual
because it needs hardware and because the point of it is that somebody watches.

    python tests/manual_test_ap07_led_hardware.py
    python tests/manual_test_ap07_led_hardware.py --sink simulator
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import AppConfig, LedConfig  # noqa: E402
from core.feedback_mapping import LedCall, LedVerb  # noqa: E402
from ui.led_feedback import LedFeedback  # noqa: E402

HOLD_S = 1.6

WALK: tuple[tuple[str, LedCall], ...] = (
    ("bereit", LedCall(LedVerb.SET_STATE, target="ready_state")),
    ("wake word", LedCall(LedVerb.EMIT_EVENT, target="wakeword_detected")),
    ("wartet auf Sprache", LedCall(LedVerb.SET_STATE, target="waiting")),
    ("nimmt auf", LedCall(LedVerb.SET_STATE, target="listening")),
    ("verarbeitet", LedCall(LedVerb.SET_STATE, target="thinking")),
    ("erfolg", LedCall(LedVerb.EMIT_EVENT, target="success_event", config={"duration_ms": 700})),
    ("spricht", LedCall(LedVerb.SET_STATE, target="speaking")),
    ("warnung", LedCall(LedVerb.EMIT_EVENT, target="warn_event")),
    ("fehler", LedCall(LedVerb.EMIT_EVENT, target="error_event", config={"duration_ms": 1200})),
    ("mikrofon weg", LedCall(LedVerb.SET_STATE, target="reconnect_mic_state")),
    ("netz weg", LedCall(LedVerb.SET_STATE, target="reconnect_network_state")),
    ("bereit", LedCall(LedVerb.SET_STATE, target="ready_state")),
    ("aus", LedCall(LedVerb.CLEAR_STATE, slot="primary")),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sink", default="respeaker", help="respeaker, simulator, null")
    parser.add_argument("--brightness", type=int, default=48, help="0..255")
    parser.add_argument("--hold", type=float, default=HOLD_S, help="seconds per step")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    failures: list[str] = []
    feedback = LedFeedback(
        LedConfig(enabled=True, sink=args.sink, brightness=args.brightness),
        on_failure=failures.append,
    )

    # The same check the application does at startup: every effect the shipped
    # mapping names has to exist before any of this is worth trying.
    mapping = AppConfig.load().feedback_mappings
    feedback.verify_targets(mapping.led_targets())
    print(f"katalog ok: {len(mapping.led_targets())} ziele aufgeloest")

    try:
        for label, call in WALK:
            print(f"  {label:22} {call.verb.value}: {call.target or call.slot}")
            feedback.submit((call,), live=True)
            time.sleep(args.hold)
    finally:
        stopped = feedback.shutdown()

    print()
    print(f"sauber beendet : {stopped}")
    print(f"ausfaelle      : {failures or 'keine'}")
    return 0 if stopped and not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
