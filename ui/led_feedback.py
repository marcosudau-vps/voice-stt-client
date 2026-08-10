"""The one thread that is allowed to talk to the LED controller.

Everything the previous generation did in this file — opening the device,
encoding firmware commands, isolating the native call in a killable process,
holding a pulse for its duration and restoring what was underneath it — now
belongs to LEFX. What is left is what LEFX does not do and cannot: decide which
thread makes the call, decide what may be dropped when calls arrive faster than
the ring can show them, and report a lasting failure exactly once.

**Why a dedicated thread at all.** A LEFX command renders in the calling thread,
and a render can sit on a USB control transfer. Calling from the Qt thread would
therefore make an unresponsive device look like a frozen application. One worker
owns the controller; the Qt thread only ever hands it work.
"""

from __future__ import annotations

import logging
import threading
import time
from pathlib import Path
from typing import Callable, Iterable, Optional, Sequence

from core.config import DEFAULT_LOCAL_APP_DIR, LedConfig
from core.feedback_mapping import LedCall, LedVerb
from core.led_controller import (
    InProcessLedController,
    LedConfigurationError,
    LedController,
    LedControllerError,
    NullLedController,
)

logger = logging.getLogger("ui.led_feedback")

MAX_PENDING = 64
"""How many calls may wait. Reaching this means the device stopped answering."""

MUTE_POLL_INTERVAL_S = 1.0
"""How often the device's mute line is read while the worker is running.

X0D30 is the mute *function*, not the button: it reads the same whether the
line was pulled by this application or by somebody pressing the device. That
makes it the one truth about whether the microphone is muted, and something the
client has to follow rather than merely set -- otherwise the device and the
application can end up disagreeing, with the ring dark and the client still
streaming.

On the worker thread, like every other USB access here. A read takes the
transport's lock and can wait as long as the configured timeout; doing it from
the Qt thread would trade a stale checkbox for a frozen window.
"""

_STATE_VERBS = (LedVerb.SET_STATE, LedVerb.CLEAR_STATE)


def default_state_file() -> Path:
    """Where LEFX keeps the background state it restores on the next start.

    Beside this application's own data rather than in LEFX's default temporary
    directory, which every LEFX on the machine would otherwise share.
    """
    return DEFAULT_LOCAL_APP_DIR / "lefx" / "background_state.json"


class LedFeedback:
    """Serialises LED calls onto one worker and survives the device going away."""

    def __init__(
        self,
        config: LedConfig,
        *,
        controller_factory: Optional[Callable[[], LedController]] = None,
        on_failure: Optional[Callable[[str], None]] = None,
        on_device_mute_changed: Optional[Callable[[bool], None]] = None,
    ) -> None:
        config.validate()
        self.config = config
        self._on_failure = on_failure
        self._on_device_mute_changed = on_device_mute_changed
        self._known_device_mute: Optional[bool] = None
        self._condition = threading.Condition()
        self._pending: list[LedCall] = []
        self._stopping = False
        self._thread: Optional[threading.Thread] = None
        self._failure_reported = False
        self._unavailable_since: Optional[float] = None
        self._sink_available: Optional[bool] = None
        """What the sink last said about itself. None until it has said anything.

        The authority on whether anything is being displayed, and deliberately
        not the same question as whether a call returned. Neither the reSpeaker
        sink nor the simulator raises from ``apply_frame`` -- a frame arrives
        thirty times a second and a pulled cable is an ordinary condition, so
        they record the fault and answer it through ``status()``. A command that
        "succeeded" therefore says only that LEFX accepted it.
        """

        factory = controller_factory or self._default_controller_factory()
        # Built now, not on the first call: the configuration check at startup
        # has to be able to ask the catalogue whether an effect exists. Building
        # it touches no hardware — the USB connection is made by the transport's
        # own thread whenever the device turns up, and never here.
        self.controller: LedController = factory()

    def _default_controller_factory(self) -> Callable[[], LedController]:
        if not self.config.enabled:
            return NullLedController
        config = self.config
        return lambda: InProcessLedController(
            sink=config.sink,
            fps=config.fps,
            brightness=config.brightness_fraction,
            usb_timeout_ms=config.usb_timeout_ms,
            vendor_id=config.vendor_id,
            product_id=config.product_id,
            effect_paths=tuple(config.effect_paths),
            state_file=default_state_file(),
            on_sink_changed=self._on_sink_changed,
        )

    # -- reads --------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        thread = self._thread
        return thread is not None and thread.is_alive()

    @property
    def unavailable_seconds(self) -> float:
        """How long the output has been unreachable, or 0.0 while it works.

        Read from the Qt thread, which is why it is a number to poll rather than
        a callback: deciding to offer the user something is a UI decision, and it
        belongs on the thread that owns the tray.
        """
        with self._condition:
            since = self._unavailable_since
        return 0.0 if since is None else max(0.0, time.monotonic() - since)

    def resolve(self, target: str) -> None:
        """Raise :class:`LedControllerError` if the catalogue has no such name."""
        self.controller.resolve(target)

    def set_device_mute(self, muted: bool) -> bool:
        """Mute the device and darken the ring, the way its own button does.

        Two effects from one line: X0D30 lights the mute LED and mutes the
        microphone in hardware. The ring is silenced separately, with
        ``set_output(enabled=False)`` rather than by clearing the slots -- the
        state machine keeps running and unmuting simply shows it again, so
        nothing has to be reconstructed and nothing is lost.

        Runs on the caller's thread rather than through the queue: it is a
        deliberate act by somebody watching, not feedback, and it should not
        queue behind whatever the ring happens to be doing.
        """
        applied = self.controller.set_device_mute(muted)
        try:
            self.controller.set_output(enabled=not muted)
        except Exception:
            logger.debug("could not change LED output while muting", exc_info=True)
        return applied

    def device_mute(self) -> Optional[bool]:
        try:
            return self.controller.device_mute()
        except Exception:
            logger.debug("could not read the device mute state", exc_info=True)
            return None

    def _poll_device_mute(self) -> None:
        """Notice the line moving, whoever moved it.

        Only differences are reported, and the first reading only establishes
        what "unchanged" means -- so plugging in a device that is already muted
        announces itself once, and a quiet device says nothing at all.
        """
        if self._on_device_mute_changed is None:
            return
        state = self.device_mute()
        if state is None or state == self._known_device_mute:
            return
        first_reading = self._known_device_mute is None
        self._known_device_mute = state
        if first_reading and not state:
            return
        try:
            self._on_device_mute_changed(state)
        except Exception:
            logger.exception("device mute callback failed")

    def note_device_mute(self, muted: bool) -> None:
        """Record a state this application just set, so it is not re-announced."""
        self._known_device_mute = muted

    def verify_targets(self, targets: Sequence[str]) -> None:
        """Check every name a mapping uses, and report all failures at once.

        All of them, not the first: fixing a configuration file one error per
        start is a miserable way to spend an evening, and the catalogue can
        answer thirty questions as cheaply as one.

        Says nothing about the hardware. A name resolves or it does not, and
        whether a device is plugged in has no bearing on that — which is exactly
        why this can refuse to start while an unplugged reSpeaker cannot.
        """
        unknown: list[str] = []
        for target in targets:
            try:
                self.controller.resolve(target)
            except Exception as exc:
                unknown.append(f"  {target}: {exc}")
        if not unknown:
            return
        raise LedConfigurationError(
            "feedback_mappings names LED effects this catalogue does not have:\n"
            + "\n".join(unknown)
            + "\n\nCheck the spelling against the installed effect sets, or "
            "point led.effect_paths at the catalogue that provides them."
        )

    # -- submission ---------------------------------------------------------

    def submit(self, calls: Sequence[LedCall], *, live: bool = False) -> bool:
        """Queue a rule's LED calls. Returns whether anything was queued.

        ``live`` says this came from something that just happened, rather than
        from state being rebuilt — after a replay, or at the moment the event
        stream goes live. Rebuilt state must restore what the ring *is*; it must
        not re-announce what already happened, so events are dropped from it
        while states are kept. That rule predates LEFX and survives it.
        """
        if not calls or not self.config.enabled:
            return False

        wanted = [call for call in calls if live or not call.is_event]
        if not wanted:
            return False

        with self._condition:
            if self._stopping:
                return False
            self._enqueue(wanted)
            self._ensure_worker()
            self._condition.notify()
        return True

    def _enqueue(self, calls: Iterable[LedCall]) -> None:
        """Append, letting a newer state supersede one that has not run yet.

        Two states for the same slot can only ever end in the second one, so
        showing the first on the way there buys a flicker and costs a USB write.
        Events are never dropped and never drop anything: each one is a distinct
        announcement, and coalescing two of them would lose one outright.
        """
        for call in calls:
            if call.verb in _STATE_VERBS:
                slot = call.slot or "primary"
                self._pending = [
                    item
                    for item in self._pending
                    if not (
                        item.verb in _STATE_VERBS and (item.slot or "primary") == slot
                    )
                ]
            self._pending.append(call)

        overflow = len(self._pending) - MAX_PENDING
        if overflow > 0:
            # Only reachable if the controller has stopped consuming, which
            # means the device is gone. Keeping the newest is the useful half.
            del self._pending[:overflow]
            logger.warning("LED queue overflowed; dropped %s oldest calls", overflow)

    # -- lifecycle ----------------------------------------------------------

    def shutdown(self) -> bool:
        """Stop the worker and release the device. False if it would not stop."""
        with self._condition:
            if not self._stopping:
                self._stopping = True
                self._pending.clear()
                self._condition.notify_all()
            thread = self._thread

        if thread is not None and thread.is_alive():
            thread.join(timeout=float(self.config.shutdown_timeout))
            if thread.is_alive():
                # Deliberately not closing the controller here: the worker is
                # inside a call that owns it, and closing underneath it would
                # turn a hung shutdown into an unpredictable one.
                logger.warning("the LED worker did not stop in time")
                return False
        else:
            self._quieten()
            self._close_controller()
        return True

    def _ensure_worker(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(
            target=self._worker, name="RealtimeSTT-LED", daemon=True
        )
        self._thread.start()

    def watch_device_mute(self) -> None:
        """Start following the device's mute line, if anybody is listening.

        Reading it needs the worker, and the worker otherwise only exists once
        there is something to show. Watching is a reason of its own to run: the
        line can change without this application doing anything.
        """
        if self._on_device_mute_changed is None or not self.config.enabled:
            return
        with self._condition:
            if self._stopping:
                return
            self._ensure_worker()

    def _worker(self) -> None:
        next_poll = 0.0
        try:
            while True:
                with self._condition:
                    if not self._pending and not self._stopping:
                        # With a timeout rather than without: the worker has a
                        # second job now, and it is one nothing will wake it for.
                        self._condition.wait(MUTE_POLL_INTERVAL_S)
                    if self._stopping:
                        break
                    call = self._pending.pop(0) if self._pending else None
                if call is not None:
                    self._dispatch(call)
                now = time.monotonic()
                if now >= next_poll:
                    next_poll = now + MUTE_POLL_INTERVAL_S
                    self._poll_device_mute()
        finally:
            self._quieten()
            self._close_controller()

    def _quieten(self) -> None:
        """Stop showing anything, without discarding the background state.

        ``set_output(enabled=False)`` rather than clearing the slots: what the
        user chose to have on the ring between sessions is theirs, and LEFX
        restores it on the next start.
        """
        try:
            self.controller.set_output(enabled=False)
        except Exception:
            logger.debug("could not mute the LED output on shutdown", exc_info=True)

    def _close_controller(self) -> None:
        try:
            self.controller.close()
        except Exception:
            logger.debug("closing the LED controller failed", exc_info=True)

    # -- dispatch -----------------------------------------------------------

    def _dispatch(self, call: LedCall) -> None:
        try:
            self._perform(call)
        except Exception as exc:
            # The reason travels with the report. Without it the log says only
            # that something failed, and a configuration mistake looks exactly
            # like an unplugged cable.
            self._report_failure(f"{call.verb.value} {call.target or ''}: {exc}".strip())
            return
        self._mark_available()

    def _perform(self, call: LedCall) -> None:
        if call.verb is LedVerb.SET_STATE:
            self.controller.set_state(
                call.target,
                config=call.config,
                slot=call.slot or "primary",
                action=call.action or "on",
            )
        elif call.verb is LedVerb.CLEAR_STATE:
            self.controller.clear_state(slot=call.slot or "primary")
        elif call.verb is LedVerb.EMIT_EVENT:
            self.controller.emit_event(
                call.target,
                config=call.config,
                duration_ms=call.duration_ms,
                priority=call.priority,
            )
        elif call.verb is LedVerb.SET_OUTPUT:
            self.controller.set_output(brightness=call.brightness, enabled=call.enabled)
        else:  # pragma: no cover — the enum is closed and validated on load
            raise LedControllerError(f"unsupported LED verb {call.verb!r}")

    # -- failure reporting --------------------------------------------------

    def _on_sink_changed(self, available: bool, detail: str) -> None:
        """LEFX noticed the output appear or disappear.

        The same debounce as a failed call, and deliberately the same one: a
        pulled cable produces both, and reporting it twice would be reporting
        one fact twice.
        """
        with self._condition:
            self._sink_available = available
        if available:
            self._mark_available()
            return
        self._report_failure(detail or "output unavailable")

    def _mark_available(self) -> None:
        """Clear the fault, unless the sink is still saying it has one.

        A command completing does not mean anything was shown. Letting it clear
        a standing sink fault would reset the clock on every piece of feedback,
        and the wait for an unreachable ring would never grow long enough to be
        worth telling anybody about.
        """
        with self._condition:
            if self._sink_available is False:
                return
            self._failure_reported = False
            self._unavailable_since = None

    def _report_failure(self, reason: str) -> None:
        with self._condition:
            first = not self._failure_reported
            self._failure_reported = True
            if self._unavailable_since is None:
                self._unavailable_since = time.monotonic()

        if first:
            logger.warning("LED output unavailable: %s", reason)
        else:
            logger.debug("LED output still unavailable: %s", reason)
        if not first or self._on_failure is None:
            return
        try:
            self._on_failure("unavailable")
        except Exception:
            logger.exception("LED failure callback failed.")


__all__ = ["LedFeedback", "MAX_PENDING", "default_state_file"]
