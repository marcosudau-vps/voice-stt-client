"""Typed declarative mapping from canonical events to feedback adapters.

The LED half speaks LEFX directly. A rule names a verb and the effect or preset
it addresses, and everything the catalogue offers is reachable — the three
lifecycle forms, both slots, presets, and each effect's own parameters.

That is a deliberate reversal of the previous design, which carried a fixed
vocabulary of ten abstract effects and translated them at the adapter. Ten was
enough while the adapter drove four firmware modes; against a catalogue of
thirty-six it would have meant permanently reaching a fraction of it, and a
translation table nobody could extend from the configuration file.

One consequence follows and is intended: **effect parameters are not validated
here**. This file checks that a call is well formed — a known verb, exactly one
of them, a target that is not empty, a ``config`` that is a mapping. Whether
``speed: 1.8`` is a value that effect accepts is the catalogue's question, and
answering it here would mean a second copy of every effect's parameter schema,
going stale the first time a set is updated.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional

from core.event_models import CanonicalEventType

SCHEMA_VERSION = 2

SLOTS = ("primary", "background")
"""The two state slots LEFX composes, background beneath primary."""

ACTIONS = ("on", "off", "toggle")
SOUND_ACTIONS = ("play", "stop")

MAX_DURATION_MS = 60000


class LedVerb(str, Enum):
    """What a rule does to the ring.

    The value of the verb key is the verb's primary argument: the effect or
    preset for ``set_state``, ``set_overlay`` and ``emit_event``, the slot for
    ``clear_state``, or the payload for ``set_output``. The overlay form here is
    intentionally the self-running timed form; controlled live-input overlays
    remain outside the event mapping.
    """

    SET_STATE = "set_state"
    CLEAR_STATE = "clear_state"
    SET_OVERLAY = "set_overlay"
    EMIT_EVENT = "emit_event"
    SET_OUTPUT = "set_output"


_MODIFIERS: dict[LedVerb, frozenset[str]] = {
    LedVerb.SET_STATE: frozenset({"config", "slot", "action"}),
    LedVerb.CLEAR_STATE: frozenset(),
    LedVerb.SET_OVERLAY: frozenset({"config", "action"}),
    LedVerb.EMIT_EVENT: frozenset({"config", "duration_ms", "priority"}),
    LedVerb.SET_OUTPUT: frozenset(),
}
"""Which sibling keys each verb accepts. Anything else is a typo worth saying so."""


class SoundCueId(str, Enum):
    WAKE_WORD = "wake_word"
    START = "start"
    STOP = "stop"
    COMPLETE = "complete"
    CANCEL = "cancel"
    WARNING = "warning"
    ERROR = "error"
    TIMEOUT_TICK = "timeout_tick"


class AppActionId(str, Enum):
    INDICATOR_IDLE = "indicator.idle"
    INDICATOR_WAITING_FOR_WAKE_WORD = "indicator.waiting_for_wake_word"
    INDICATOR_WAITING_FOR_SPEECH = "indicator.waiting_for_speech"
    INDICATOR_RECORDING = "indicator.recording"
    INDICATOR_FINALIZING = "indicator.finalizing"
    INDICATOR_SUCCESS = "indicator.success"
    INDICATOR_WARNING = "indicator.warning"
    INDICATOR_ERROR = "indicator.error"


@dataclass(frozen=True)
class LedCall:
    """One call into the LED controller, as written in the configuration."""

    verb: LedVerb
    target: Optional[str] = None
    config: Mapping[str, Any] = field(default_factory=dict)
    slot: Optional[str] = None
    action: Optional[str] = None
    duration_ms: Optional[int] = None
    priority: Optional[int] = None
    brightness: Optional[float] = None
    enabled: Optional[bool] = None

    def to_mapping(self) -> dict[str, Any]:
        """Back to the shape it was written in, so saving reproduces the file.

        Not ``dataclasses.asdict``: that produces the *fields*, and the fields
        are not the schema. A round trip through the field form would write a
        file this module then refuses to read.
        """
        if self.verb is LedVerb.SET_OUTPUT:
            payload: dict[str, Any] = {}
            if self.brightness is not None:
                payload["brightness"] = self.brightness
            if self.enabled is not None:
                payload["enabled"] = self.enabled
            return {self.verb.value: payload}
        if self.verb is LedVerb.CLEAR_STATE:
            return {self.verb.value: self.slot or "primary"}

        written: dict[str, Any] = {self.verb.value: self.target}
        if self.config:
            written["config"] = dict(self.config)
        for name, value in (
            ("slot", self.slot),
            ("action", self.action),
            ("duration_ms", self.duration_ms),
            ("priority", self.priority),
        ):
            if value is not None:
                written[name] = value
        return written

    @property
    def is_event(self) -> bool:
        """Whether this is a one-shot announcement rather than a lasting change.

        The distinction decides what may be replayed. A state reconstructed from
        the event stream is the truth about now; an event re-emitted from a
        recording is an announcement of something that already happened.
        """
        return self.verb in {LedVerb.SET_OVERLAY, LedVerb.EMIT_EVENT}

    def validate(self) -> None:
        if not isinstance(self.verb, LedVerb):
            raise ValueError("led.verb must be a known verb")
        if not isinstance(self.config, Mapping):
            raise ValueError("led.config must be a mapping")

        if self.verb in (
            LedVerb.SET_STATE,
            LedVerb.SET_OVERLAY,
            LedVerb.EMIT_EVENT,
        ):
            if not isinstance(self.target, str) or not self.target.strip():
                raise ValueError(f"{self.verb.value} needs an effect or preset name")
        elif self.target is not None:
            raise ValueError(f"{self.verb.value} takes no target")

        if self.slot is not None and self.slot not in SLOTS:
            raise ValueError(f"led.slot must be one of {list(SLOTS)}")
        if self.action is not None and self.action not in ACTIONS:
            raise ValueError(f"led.action must be one of {list(ACTIONS)}")
        if self.verb is LedVerb.SET_OVERLAY and self.action not in {None, "on"}:
            raise ValueError("set_overlay supports only action 'on'")

        if self.duration_ms is not None and (
            isinstance(self.duration_ms, bool)
            or not isinstance(self.duration_ms, int)
            or not 1 <= self.duration_ms <= MAX_DURATION_MS
        ):
            raise ValueError(
                f"led.duration_ms must be null or between 1 and {MAX_DURATION_MS}"
            )
        if self.priority is not None and (
            isinstance(self.priority, bool) or not isinstance(self.priority, int)
        ):
            raise ValueError("led.priority must be null or an integer")

        if self.brightness is not None and (
            isinstance(self.brightness, bool)
            or not isinstance(self.brightness, (int, float))
            or not math.isfinite(self.brightness)
            or not 0.0 <= self.brightness <= 1.0
        ):
            raise ValueError("set_output.brightness must be between 0.0 and 1.0")
        if self.enabled is not None and not isinstance(self.enabled, bool):
            raise ValueError("set_output.enabled must be a boolean")
        if self.verb is LedVerb.SET_OUTPUT and self.brightness is None and self.enabled is None:
            raise ValueError("set_output needs brightness, enabled, or both")


@dataclass(frozen=True)
class SoundEffect:
    cue: SoundCueId
    volume: float = 1.0
    action: str = "play"

    def validate(self) -> None:
        if not isinstance(self.cue, SoundCueId):
            raise ValueError("sound.cue must be a known cue id")
        if self.action not in SOUND_ACTIONS:
            raise ValueError(f"sound.action must be one of {list(SOUND_ACTIONS)}")
        if (
            isinstance(self.volume, bool)
            or not isinstance(self.volume, (int, float))
            or not math.isfinite(self.volume)
            or not 0.0 <= self.volume <= 1.0
        ):
            raise ValueError("sound.volume must be between 0.0 and 1.0")


@dataclass(frozen=True)
class AppEffect:
    action: AppActionId

    def validate(self) -> None:
        if not isinstance(self.action, AppActionId):
            raise ValueError("app.action must be a known action id")


@dataclass(frozen=True)
class FeedbackRule:
    led: tuple[LedCall, ...] = ()
    sound: Optional[SoundEffect] = None
    app: Optional[AppEffect] = None

    def validate(self) -> None:
        if not isinstance(self.led, tuple):
            raise ValueError("led must be a tuple of calls")
        for call in self.led:
            if not isinstance(call, LedCall):
                raise ValueError("led entries must be LedCall")
            call.validate()
        for effect in (self.sound, self.app):
            if effect is not None:
                effect.validate()

    def led_targets(self) -> tuple[str, ...]:
        """Every effect or preset name this rule names, for the startup check."""
        return tuple(call.target for call in self.led if call.target)

    def to_mapping(self) -> dict[str, Any]:
        written: dict[str, Any] = {}
        if self.led:
            # One call stays a mapping, several become a list — the same two
            # spellings the reader accepts, so a hand-written file that used the
            # short form comes back in the short form.
            written["led"] = (
                self.led[0].to_mapping()
                if len(self.led) == 1
                else [call.to_mapping() for call in self.led]
            )
        if self.sound is not None:
            written["sound"] = {
                "cue": self.sound.cue.value,
                "volume": self.sound.volume,
            }
            if self.sound.action != "play":
                written["sound"]["action"] = self.sound.action
        if self.app is not None:
            written["app"] = {"action": self.app.action.value}
        return written


@dataclass
class FeedbackMappingConfig:
    schema_version: int = SCHEMA_VERSION
    events: dict[str, FeedbackRule] = field(default_factory=dict)

    def validate(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != SCHEMA_VERSION
        ):
            raise ValueError(
                f"feedback_mappings.schema_version must be {SCHEMA_VERSION}"
            )
        if not isinstance(self.events, dict):
            raise ValueError("feedback_mappings.events must be a mapping")
        known = {item.value for item in CanonicalEventType}
        for event_name, rule in self.events.items():
            if event_name not in known:
                raise ValueError(f"unknown feedback event id: {event_name!r}")
            if not isinstance(rule, FeedbackRule):
                raise ValueError(f"mapping for {event_name!r} must be a FeedbackRule")
            rule.validate()

    def rule_for(self, event_type: CanonicalEventType) -> FeedbackRule:
        return self.events.get(event_type.value, FeedbackRule())

    def led_targets(self) -> tuple[str, ...]:
        """Every LED target named anywhere, each once, in a stable order.

        This is what the startup check resolves against the catalogue. Names
        rather than rules, because the same effect is normally named by several
        rules and asking about it once is enough.
        """
        seen: dict[str, None] = {}
        for _, rule in sorted(self.events.items()):
            for target in rule.led_targets():
                seen.setdefault(target, None)
        return tuple(seen)

    def to_mapping(self) -> dict[str, Any]:
        """The whole section as it belongs in the file."""
        return {
            "schema_version": self.schema_version,
            "events": {
                name: rule.to_mapping() for name, rule in self.events.items()
            },
        }

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "FeedbackMappingConfig":
        if not isinstance(raw, Mapping):
            raise ValueError("feedback_mappings must be a mapping")
        unknown_root = set(raw) - {"schema_version", "events"}
        if unknown_root:
            raise ValueError(
                f"unknown feedback_mappings fields: {sorted(unknown_root)}"
            )

        declared = raw.get("schema_version", SCHEMA_VERSION)
        if declared == 1:
            # Refused rather than migrated. Schema 1 named ten abstract effects
            # that no longer exist as a concept, and guessing which catalogue
            # entry each of them meant would silently change what the ring shows.
            raise ValueError(
                "feedback_mappings.schema_version 1 is no longer supported: the "
                "led section now names LEFX verbs and effects directly, for "
                "example 'led: {set_state: listening}'. Rewrite the section and "
                "set schema_version: 2."
            )

        events_raw = raw.get("events", {})
        if not isinstance(events_raw, Mapping):
            raise ValueError("feedback_mappings.events must be a mapping")
        config = cls(
            schema_version=declared,
            events={
                str(event_name): _parse_rule(str(event_name), rule_raw)
                for event_name, rule_raw in events_raw.items()
            },
        )
        config.validate()
        return config


def _enum_value(enum_type: type[Enum], value: Any, path: str) -> Enum:
    if not isinstance(value, str):
        raise ValueError(f"{path} must be a string")
    try:
        return enum_type(value)
    except ValueError as exc:
        raise ValueError(f"unknown {path}: {value!r}") from exc


def _parse_led_call(where: str, raw: Any) -> LedCall:
    if not isinstance(raw, Mapping):
        raise ValueError(f"{where} must be a mapping naming one verb")

    verbs = sorted(set(raw) & {item.value for item in LedVerb})
    if not verbs:
        known = ", ".join(item.value for item in LedVerb)
        raise ValueError(f"{where} names no LED verb; expected one of: {known}")
    if len(verbs) > 1:
        raise ValueError(
            f"{where} names several verbs ({', '.join(verbs)}); "
            "write one call per verb, as a list if you need both"
        )

    verb = LedVerb(verbs[0])
    modifiers = set(raw) - {verb.value}
    unknown = sorted(modifiers - _MODIFIERS[verb])
    if unknown:
        allowed = ", ".join(sorted(_MODIFIERS[verb])) or "none"
        raise ValueError(
            f"unknown keys for {where}.{verb.value}: {unknown} (allowed: {allowed})"
        )

    value = raw[verb.value]

    if verb is LedVerb.SET_OUTPUT:
        if not isinstance(value, Mapping):
            raise ValueError(f"{where}.set_output must be a mapping")
        payload_unknown = sorted(set(value) - {"brightness", "enabled"})
        if payload_unknown:
            raise ValueError(f"unknown set_output fields: {payload_unknown}")
        call = LedCall(
            verb=verb,
            brightness=value.get("brightness"),
            enabled=value.get("enabled"),
        )
        call.validate()
        return call

    if verb is LedVerb.CLEAR_STATE:
        if not isinstance(value, str) or value not in SLOTS:
            raise ValueError(f"{where}.clear_state must name a slot: {list(SLOTS)}")
        call = LedCall(verb=verb, slot=value)
        call.validate()
        return call

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where}.{verb.value} must name an effect or preset")

    config_raw = raw.get("config", {})
    if config_raw is None:
        config_raw = {}
    if not isinstance(config_raw, Mapping):
        raise ValueError(f"{where}.config must be a mapping")

    call = LedCall(
        verb=verb,
        target=value.strip(),
        config={str(key): item for key, item in config_raw.items()},
        slot=raw.get("slot"),
        action=raw.get("action"),
        duration_ms=raw.get("duration_ms"),
        priority=raw.get("priority"),
    )
    call.validate()
    return call


def _parse_led(event_name: str, raw: Any) -> tuple[LedCall, ...]:
    """One call, or several in order. Both spellings mean the same thing.

    A list because two lifecycle forms routinely belong to one fact: a wake word
    both flashes and changes what the ring settles into afterwards. With a single
    call per rule that would need two rules for one event, and the configuration
    would stop describing events.
    """
    if raw is None:
        return ()
    if isinstance(raw, Mapping):
        return (_parse_led_call(f"{event_name}.led", raw),)
    if isinstance(raw, (list, tuple)):
        return tuple(
            _parse_led_call(f"{event_name}.led[{index}]", item)
            for index, item in enumerate(raw)
        )
    raise ValueError(f"{event_name}.led must be a mapping or a list of mappings")


def _parse_rule(event_name: str, raw: Any) -> FeedbackRule:
    if raw is None:
        return FeedbackRule()
    if not isinstance(raw, Mapping):
        raise ValueError(f"mapping for {event_name!r} must be a mapping")
    unknown = set(raw) - {"led", "sound", "app"}
    if unknown:
        raise ValueError(f"unknown fields for {event_name!r}: {sorted(unknown)}")

    led = _parse_led(event_name, raw.get("led"))

    sound_raw = raw.get("sound")
    sound = None
    if sound_raw is not None:
        if not isinstance(sound_raw, Mapping):
            raise ValueError(f"{event_name}.sound must be a mapping")
        sound_unknown = set(sound_raw) - {"cue", "volume", "action"}
        if sound_unknown:
            raise ValueError(
                f"unknown {event_name}.sound fields: {sorted(sound_unknown)}"
            )
        sound = SoundEffect(
            cue=_enum_value(SoundCueId, sound_raw.get("cue"), "sound.cue"),
            volume=sound_raw.get("volume", 1.0),
            action=sound_raw.get("action", "play"),
        )

    app_raw = raw.get("app")
    app = None
    if app_raw is not None:
        if not isinstance(app_raw, Mapping):
            raise ValueError(f"{event_name}.app must be a mapping")
        app_unknown = set(app_raw) - {"action"}
        if app_unknown:
            raise ValueError(f"unknown {event_name}.app fields: {sorted(app_unknown)}")
        app = AppEffect(
            action=_enum_value(AppActionId, app_raw.get("action"), "app.action")
        )

    rule = FeedbackRule(led=led, sound=sound, app=app)
    rule.validate()
    return rule


def default_feedback_mappings() -> FeedbackMappingConfig:
    """Return a complete no-effect catalog when no YAML policy is loaded."""
    return FeedbackMappingConfig(
        schema_version=SCHEMA_VERSION,
        events={event_type.value: FeedbackRule() for event_type in CanonicalEventType},
    )
