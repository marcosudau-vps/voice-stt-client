"""Safe AP07 smoke for missing LED hardware and a broken sound asset."""

from __future__ import annotations

import threading

from PySide6.QtCore import QCoreApplication

from core.config import FeedbackConfig, LedConfig
from core.feedback_mapping import (
    LedCall,
    LedVerb,
    SoundCueId,
    SoundEffect,
)
from ui.feedback import SoundFeedback
from ui.led_feedback import LedFeedback


def main() -> None:
    application = QCoreApplication.instance() or QCoreApplication([])

    sound_failures: list[str] = []
    sound = SoundFeedback(
        FeedbackConfig(
            sounds_enabled=True,
            error_sound="definitely-missing-ap07-sound.wav",
        )
    )
    sound.failure.connect(sound_failures.append)
    if sound.play(SoundEffect(SoundCueId.ERROR)):
        raise AssertionError("Missing sound asset was unexpectedly accepted")
    application.processEvents()
    sound.play(SoundEffect(SoundCueId.ERROR))
    application.processEvents()
    if len(sound_failures) != 1:
        raise AssertionError("Sound failure was not reported exactly once")

    led_failed = threading.Event()
    led_failures: list[str] = []

    def on_led_failure(reason: str) -> None:
        led_failures.append(reason)
        led_failed.set()

    # A vendor and product nobody has: the transport never connects, the sink
    # reports itself unavailable, and the ring is simply not there. Exactly the
    # situation of an unplugged device, without unplugging one.
    led = LedFeedback(
        LedConfig(
            enabled=True,
            vendor_id=0xFFFF,
            product_id=0xFFFF,
            usb_timeout_ms=100,
            shutdown_timeout=1.0,
        ),
        on_failure=on_led_failure,
    )
    if not led.submit((LedCall(LedVerb.SET_STATE, target="listening"),), live=True):
        raise AssertionError("LED failure smoke did not accept the queued update")
    if not led_failed.wait(3.0):
        raise AssertionError("Missing LED device was not reported")
    if led_failures != ["unavailable"]:
        raise AssertionError("LED failure was not reported exactly once")
    if not led.shutdown() or led.is_running:
        raise AssertionError("LED worker did not shut down cleanly")

    print(
        "AP07 ADAPTER FAILURE SMOKE PASSED "
        "(missing sound and LED are isolated, rate-limited, clean shutdown)"
    )


if __name__ == "__main__":
    main()
