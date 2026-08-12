"""The seam between the client's feedback rules and the LEFX V3 controller.

Six verbs, one error type, and no knowledge of how the LEDs are reached. That
narrowness is the point. LEFX runs the same engine embedded in a thread, in a
process of its own, or as a standalone service, and an application that talks to
it through this port can be moved between those without the mapping, the reducer
or the tray knowing anything happened. Today only the embedded form is built;
the HTTP form would be a second implementation of this same Protocol.

Nothing here decides *what* to show. Which rule fires on which fact is the YAML's
business, and which effect a rule names is the catalogue's. This file only
carries the call across the boundary and makes every failure on the far side
look the same on this one.
"""

from __future__ import annotations

import logging
import threading
import time
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Optional, Protocol

logger = logging.getLogger("core.led_controller")

DEFAULT_FPS = 30.0
DEFAULT_LED_COUNT = 12

SINK_RESPEAKER = "respeaker"
SINK_SIMULATOR = "simulator"
SINK_NULL = "null"

MUTE_CONFIRM_TIMEOUT_S = 0.6
"""How long to wait for the mute line to read back what was written."""

MUTE_PIN_NAME = "X0D30"
"""The line that drives the mute LED and the microphone mute together.

High means muted, and it is the same line the button on the device pulls — so
reading it answers "is the microphone muted" however it came to be that way.
"""

MUTE_PIN_INDEX = 1
"""Where X0D30 sits in ``GPO_READ_VALUES``.

The read answers five levels "in order of Pin X0D11, X0D30, X0D31, X0D33 and
X0D39" — a position, counting from zero.
"""

MUTE_PIN_NUMBER = 30
"""What ``GPO_WRITE_VALUE`` wants for X0D30.

Not the position: the **pin number**. The two commands address the same five
pins in two different ways, which is easy to miss because the read is what one
reaches for first — and writing the position instead is accepted over USB and
then silently does nothing, on every pin, which looks exactly like a firmware
that refuses host control.

Named as constants rather than passed in because two of the neighbours are not
things to write by accident: 31 is the amplifier enable and 33 is the power to
the LED ring. A wrong number here does not misbehave, it turns hardware off.
"""


class LedControllerError(RuntimeError):
    """Anything the controller could not do.

    One type on purpose. LEFX distinguishes a target that does not exist from
    one that is ambiguous from a parameter that will not validate, and those
    distinctions matter *inside* LEFX. To a caller here they are all "this call
    did not happen, and here is the sentence explaining why" — and a caller that
    had to catch five engine types would be coupled to the engine's taxonomy.
    """


class LedConfigurationError(LedControllerError):
    """A rule names an effect or preset the loaded catalogue does not have.

    Separate from its parent because the two call for opposite reactions. A
    controller error means the hardware is not answering, which is ordinary and
    recoverable — the transport keeps trying and the application keeps running.
    This means the configuration file says something that cannot be carried out,
    which no amount of waiting will fix, and which is worth refusing to start
    over rather than discovering halfway through a dictation.
    """


class LedController(Protocol):
    """What the client needs an LED controller to do."""

    def resolve(self, target: str) -> None:
        """Raise if ``target`` names no effect or preset. Reads, never shows."""

    def set_state(
        self,
        target: str,
        *,
        config: Optional[Mapping[str, Any]] = None,
        slot: str = "primary",
        action: str = "on",
    ) -> None: ...

    def clear_state(self, *, slot: str = "primary") -> None: ...

    def set_overlay(
        self,
        target: str,
        *,
        config: Optional[Mapping[str, Any]] = None,
        action: str = "on",
    ) -> None: ...

    def emit_event(
        self,
        target: str,
        *,
        config: Optional[Mapping[str, Any]] = None,
        duration_ms: Optional[int] = None,
        priority: Optional[int] = None,
    ) -> None: ...

    def set_output(
        self,
        *,
        brightness: Optional[float] = None,
        enabled: Optional[bool] = None,
    ) -> None: ...

    def set_device_mute(self, muted: bool) -> bool:
        """Pull the device's own mute line. Returns whether it reached hardware."""

    def device_mute(self) -> Optional[bool]:
        """What the mute line currently reads, or None when it cannot be read."""

    def close(self) -> None: ...


class NullLedController:
    """Accepts every call and does nothing. Used when LED output is switched off.

    ``resolve`` succeeds for any name, because with no catalogue loaded there is
    nothing to check against and refusing would turn "LEDs are off" into a
    configuration error.
    """

    def resolve(self, target: str) -> None:
        del target

    def set_state(self, target: str, **_: Any) -> None:
        del target

    def clear_state(self, **_: Any) -> None:
        return

    def set_overlay(self, target: str, **_: Any) -> None:
        del target

    def emit_event(self, target: str, **_: Any) -> None:
        del target

    def set_output(self, **_: Any) -> None:
        return

    def set_device_mute(self, muted: bool) -> bool:
        del muted
        return False

    def device_mute(self) -> Optional[bool]:
        return None

    def close(self) -> None:
        return


def _catalogue_directories(extra_paths: Iterable[str] = ()) -> list[Path]:
    """Where the ``.lefxset`` archives are, without asking the entry points.

    LEFX finds its catalogues through ``importlib.metadata``, which is the right
    mechanism for a service that should play whatever happens to be installed. A
    frozen single-file build has no distribution metadata, so that mechanism
    finds nothing there — the archives are present as bundled data, and only the
    index to them is missing. Importing the two set modules by name reaches the
    same files in both worlds.

    Naming the sets here rather than discovering them is deliberate: this client
    decided which catalogues it runs on, and a build that silently picked up a
    third one would be a build nobody tested.
    """
    import importlib

    found: list[Path] = []
    for module_name in ("lefx.sets.core_set", "lefx.sets.smartspeaker_set"):
        try:
            archive = Path(importlib.import_module(module_name).package_file())
        except Exception:
            logger.warning("effect set %s is not importable", module_name, exc_info=True)
            continue
        if not archive.is_file():
            logger.warning("effect set archive is missing: %s", archive)
            continue
        if archive.parent not in found:
            found.append(archive.parent)

    for item in extra_paths:
        path = Path(item).expanduser()
        if path not in found:
            # A directory that is not there is not an error. These are the
            # user's own folders, and one on a drive that happens to be
            # unplugged must not stop the application from starting.
            if path.is_dir():
                found.append(path)
            else:
                logger.warning("configured effect path does not exist: %s", path)
    return found


def _create_sink(name: str, options: Mapping[str, Any]) -> tuple[Any, int]:
    """Build the output, and say how many LEDs it has.

    The hardware sink is constructed directly rather than looked up by name, for
    the same reason the catalogues are: entry points do not survive freezing.
    Everything else still goes through discovery, because everything else is a
    development aid that only ever runs from an installed environment.
    """
    if name in (None, "", SINK_NULL):
        from lefx.interfaces.discovery import NullSink

        return NullSink(), DEFAULT_LED_COUNT

    if name == SINK_RESPEAKER:
        from lefx.device.respeaker import xvf
        from lefx.device.respeaker.registration import create_frame_sink

        # The firmware declares its own ring size, and a sink configured for a
        # different one reports itself unavailable for as long as it holds.
        # Reading it here means the number cannot be got wrong.
        led_count = xvf.RING_LED_COUNT
        return create_frame_sink(led_count=led_count, **options), led_count

    from lefx.interfaces.discovery import create_sink

    return create_sink(name, led_count=DEFAULT_LED_COUNT, **options), DEFAULT_LED_COUNT


class InProcessLedController:
    """Drives a :class:`lefx.interfaces.ControllerService` in this process.

    The catalogue is loaded when this object is built, because the configuration
    check at startup has to be able to ask whether an effect exists, and an
    answer that only arrives at the first piece of feedback would arrive in the
    middle of a dictation. Everything with a cost is still deferred: the render
    thread starts on the first command, and the USB connection is established by
    the transport's own thread whenever the device turns up.

    Not thread-safe by intent rather than by accident: every method reaches
    LEFX, LEFX renders in the calling thread, and a render can sit on a USB
    transfer. One dedicated caller thread owns this object — never the Qt thread.
    """

    def __init__(
        self,
        *,
        sink: str = SINK_RESPEAKER,
        fps: float = DEFAULT_FPS,
        brightness: Optional[float] = None,
        usb_timeout_ms: Optional[int] = None,
        vendor_id: Optional[int] = None,
        product_id: Optional[int] = None,
        effect_paths: Iterable[str] = (),
        state_file: Optional[str | Path] = None,
        on_sink_changed: Optional[Callable[[bool, str], None]] = None,
        service_factory: Optional[Callable[[], Any]] = None,
    ) -> None:
        self.sink_name = sink
        self.brightness = brightness
        self._on_sink_changed = on_sink_changed
        self._lock = threading.RLock()
        self._started = False
        self._closed = False

        if service_factory is not None:
            self._service = service_factory()
        else:
            self._service = self._build_service(
                sink,
                fps,
                {
                    "usb_timeout_ms": usb_timeout_ms,
                    "vendor_id": vendor_id,
                    "product_id": product_id,
                },
                effect_paths,
                state_file,
            )

        listen = getattr(self._service, "add_listener", None)
        if listen is not None:
            listen(self._on_service_event)

    # -- construction -------------------------------------------------------

    @staticmethod
    def _build_service(
        sink: str,
        fps: float,
        device_options: Mapping[str, Any],
        effect_paths: Iterable[str],
        state_file: Optional[str | Path],
    ) -> Any:
        from lefx.interfaces import ControllerService

        # Only what was actually configured. LEFX leaves its own defaults in
        # place for anything it is not told about, and passing None would ask
        # it to treat "unspecified" as a value.
        options = {
            key: value for key, value in device_options.items() if value is not None
        }

        try:
            device, led_count = _create_sink(sink, options)
        except Exception as exc:
            raise LedControllerError(f"LED output {sink!r} is unavailable: {exc}") from exc

        # Every value LEFX would otherwise read from a configuration file is
        # passed here instead. Without that it looks for config.yaml beside the
        # working directory and finds *this application's* config.yaml, whose
        # keys mean something else entirely.
        return ControllerService(
            sink=device,
            led_count=led_count,
            fps=float(fps),
            search_paths=_catalogue_directories(effect_paths),
            state_file=state_file,
            autostart_providers=False,
        )

    # -- lifecycle ----------------------------------------------------------

    def _ensure_started(self) -> None:
        if self._started:
            return
        self._service.start()
        self._started = True
        if self.brightness is not None:
            self._service.set_output(brightness=float(self.brightness))

    def _on_service_event(self, event: str, payload: Mapping[str, Any]) -> None:
        if event != "sink_changed" or self._on_sink_changed is None:
            return
        available = bool(payload.get("available"))
        detail = str(payload.get("detail") or "")
        try:
            self._on_sink_changed(available, detail)
        except Exception:
            logger.exception("sink listener failed")

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._service.stop()
        except Exception:
            logger.warning("stopping the LED service failed", exc_info=True)
        if self.sink_name == SINK_RESPEAKER:
            # The transport is a module-level singleton shared by sink and
            # provider. Stopping the service stops it, but leaving it in place
            # would hand a dead handle to whoever builds the next controller.
            try:
                from lefx.device.respeaker.registration import reset_shared_transport

                reset_shared_transport()
            except Exception:
                logger.debug("could not reset the USB transport", exc_info=True)

    # -- commands -----------------------------------------------------------

    def _call(self, what: str, action: Callable[[], Any]) -> None:
        if self._closed:
            raise LedControllerError(f"{what} after the controller was closed")
        with self._lock:
            try:
                self._ensure_started()
                action()
            except LedControllerError:
                raise
            except Exception as exc:
                raise LedControllerError(f"{what} failed: {exc}") from exc

    def resolve(self, target: str) -> None:
        """Ask the catalogue whether this name means anything. Shows nothing.

        Deliberately does not start the render thread: this is what the startup
        check calls, once per rule, before anything is meant to light up.
        """
        if self._closed:
            raise LedControllerError("resolve after the controller was closed")
        try:
            self._service.show(target)
        except Exception as exc:
            raise LedControllerError(f"unknown LED target {target!r}: {exc}") from exc

    def set_state(
        self,
        target: str,
        *,
        config: Optional[Mapping[str, Any]] = None,
        slot: str = "primary",
        action: str = "on",
    ) -> None:
        self._call(
            f"set_state {target!r}",
            lambda: self._service.set_state(
                target, dict(config or {}), slot=slot, action=action
            ),
        )

    def clear_state(self, *, slot: str = "primary") -> None:
        self._call(
            f"clear_state {slot!r}", lambda: self._service.clear_state(slot=slot)
        )

    def set_overlay(
        self,
        target: str,
        *,
        config: Optional[Mapping[str, Any]] = None,
        action: str = "on",
    ) -> None:
        self._call(
            f"set_overlay {target!r}",
            lambda: self._service.set_overlay(
                target, config=dict(config or {}), action=action
            ),
        )

    def emit_event(
        self,
        target: str,
        *,
        config: Optional[Mapping[str, Any]] = None,
        duration_ms: Optional[int] = None,
        priority: Optional[int] = None,
    ) -> None:
        self._call(
            f"emit_event {target!r}",
            lambda: self._service.emit_event(
                target,
                dict(config or {}),
                priority=priority,
                duration_ms=duration_ms,
            ),
        )

    def set_output(
        self,
        *,
        brightness: Optional[float] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        self._call(
            "set_output",
            lambda: self._service.set_output(brightness=brightness, enabled=enabled),
        )

    # -- the device's own mute line -----------------------------------------

    def _transport(self) -> Any:
        """The USB connection the sink already owns, or None for other outputs.

        Reached rather than opened: the handle is exclusive, and this is the one
        that exists. ``shared_transport`` is a singleton, so asking again during
        the service's lifetime returns what the sink is using.
        """
        if self.sink_name != SINK_RESPEAKER:
            return None
        from lefx.device.respeaker.registration import shared_transport

        return shared_transport()

    def set_device_mute(self, muted: bool) -> bool:
        """Mute the device, and report whether the line actually moved.

        Sets X0D30, which lights the mute LED and silences the microphone
        together -- the same line, and the same effect, as the button on the
        device. Measured: the captured level falls flat while it is set.

        Checked rather than assumed. A write with the wrong pin address is
        accepted over USB and then does nothing at all, so the command reporting
        success proves only that it was delivered.
        """
        transport = self._transport()
        if transport is None or not transport.is_connected:
            return False
        try:
            transport.write("GPO_WRITE_VALUE", [MUTE_PIN_NUMBER, 1 if muted else 0])
        except Exception as exc:
            raise LedControllerError(
                f"could not set the mute line {MUTE_PIN_NAME}: {exc}"
            ) from exc

        # The level does not read back the instant the write returns, so this
        # asks a few times rather than once. Bounded and short: it runs on the
        # LED worker in response to a deliberate action, never per frame.
        deadline = time.monotonic() + MUTE_CONFIRM_TIMEOUT_S
        while True:
            if self.device_mute() is muted:
                return True
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.05)

    def device_mute(self) -> Optional[bool]:
        transport = self._transport()
        if transport is None or not transport.is_connected:
            return None
        try:
            levels = transport.read("GPO_READ_VALUES")
        except Exception:
            logger.debug("could not read the GPO pins", exc_info=True)
            return None
        if len(levels) <= MUTE_PIN_INDEX:
            return None
        return bool(levels[MUTE_PIN_INDEX])


__all__ = [
    "DEFAULT_FPS",
    "DEFAULT_LED_COUNT",
    "InProcessLedController",
    "LedConfigurationError",
    "LedController",
    "LedControllerError",
    "NullLedController",
    "SINK_NULL",
    "SINK_RESPEAKER",
    "SINK_SIMULATOR",
]
