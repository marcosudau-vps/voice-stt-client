"""Deterministic V1 -> V2 profile migration; no network, Qt or runtime pauses.

Unresolved values and their provenance remain in the profile. Callers must
present blocking issues and resolve them before admission. Persistence is an
explicit transaction, preserving the original bytes in an adjacent backup.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
import os
from pathlib import Path
import tempfile

import yaml

from .config import HotkeyConfig
from .v2_controls import ControlConfig, migrate_hotkeys


PROFILE_VERSION = 2


@dataclass
class V2Profile:
    schema_version: int = PROFILE_VERSION
    manual: bool = True
    wake_word: bool = False
    wake_word_ids: list[str] = field(default_factory=list)
    desired_settings: dict = field(default_factory=dict)
    controls: dict = field(default_factory=lambda: asdict(ControlConfig()))
    unresolved: dict = field(default_factory=dict)
    retired: dict = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)

    def validate(self):
        if type(self.schema_version) is not int or self.schema_version != PROFILE_VERSION:
            raise ValueError("unsupported V2 profile version")
        if type(self.manual) is not bool or type(self.wake_word) is not bool:
            raise ValueError("trigger flags must be boolean")
        if not self.manual and not self.wake_word:
            raise ValueError("at least one configured trigger required")
        if not isinstance(self.wake_word_ids, list) or not all(isinstance(x, str) and x.strip() for x in self.wake_word_ids):
            raise ValueError("wake IDs must be strings")
        if not all(isinstance(x, dict) for x in (self.desired_settings, self.controls, self.unresolved, self.retired)):
            raise ValueError("profile maps required")
        if not isinstance(self.issues, list) or not all(isinstance(x, str) for x in self.issues):
            raise ValueError("profile issues required")
        ControlConfig(**self.controls)

    def require_ready(self):
        self.validate()
        if self.issues or self.unresolved:
            raise ValueError("profile needs visible repair before admission")


def seconds_to_ms(value):
    if type(value) not in (int, float):
        raise ValueError("seconds must be finite numbers")
    try:
        converted = Decimal(str(value)) * 1000
        if not converted.is_finite() or converted < 0 or converted != converted.to_integral_value():
            raise ValueError("seconds are not exactly representable as milliseconds")
        return int(converted)
    except InvalidOperation:
        raise ValueError("invalid seconds") from None


def migrate_profile(raw: dict, catalog=None) -> V2Profile:
    """Pure conversion of the actual user mapping, before layering defaults.

    Already versioned profiles are never re-derived from legacy fields. An
    offline migration can be resumed with a catalog without losing raw inputs.
    """
    if not isinstance(raw, dict):
        raise ValueError("configuration mapping required")
    if "v2_profile" in raw and raw["v2_profile"] is not None:
        profile = V2Profile(**deepcopy(raw["v2_profile"]))
        if profile.schema_version != PROFILE_VERSION:
            raise ValueError("unsupported V2 profile version")
    else:
        profile = V2Profile()
        session = raw.get("session") or {}
        window = raw.get("dictation_window") or {}
        if not isinstance(session, dict) or not isinstance(window, dict):
            raise ValueError("legacy sections must be maps")
        mode = session.get("mode", "hotkey")
        flags = (session.get("manual_trigger_enabled"), session.get("wake_word_trigger_enabled"))
        if mode not in ("hotkey", "wake_word") and None in flags:
            profile.unresolved["session.mode"] = mode
        profile.manual = flags[0] if flags[0] is not None else mode == "hotkey"
        profile.wake_word = flags[1] if flags[1] is not None else mode == "wake_word"
        if type(profile.manual) is not bool or type(profile.wake_word) is not bool or not (profile.manual or profile.wake_word):
            profile.unresolved["session.trigger_flags"] = list(flags)
        for old, new in (("initial_speech_timeout", "activation.initialSpeechTimeoutMs"),
                         ("followup_timeout", "activation.followupTimeoutMs")):
            sources = {section + "." + old: values[old] for section, values in (("session", session), ("dictation_window", window))
                       if values.get(old) is not None}
            try:
                converted = {name: seconds_to_ms(value) for name, value in sources.items()}
                if len(set(converted.values())) > 1:
                    raise ValueError("colliding timing preferences")
                if converted:
                    profile.desired_settings[new] = next(iter(converted.values()))
            except ValueError:
                profile.unresolved[new] = sources
        sensitivity = session.get("wake_word_sensitivity")
        if sensitivity is not None:
            profile.desired_settings["wakeWord.sensitivity"] = sensitivity
        # These values have no proven one-to-one V2 semantic equivalent.
        for section, values in (("session", session), ("dictation_window", window)):
            for key, value in values.items():
                if value is not None and key not in ("mode", "manual_trigger_enabled", "wake_word_trigger_enabled",
                                                     "wake_words", "initial_speech_timeout", "followup_timeout", "wake_word_sensitivity"):
                    profile.retired[section + "." + key] = value
        words = session.get("wake_words", "hey_jarvis")
        if words:
            profile.unresolved["wake_words"] = words
        try:
            profile.controls = asdict(migrate_hotkeys(HotkeyConfig(**(raw.get("hotkey") or {}))))
        except (ValueError, TypeError, AttributeError):
            profile.unresolved["hotkey"] = deepcopy(raw.get("hotkey"))
    words = profile.unresolved.get("wake_words")
    if words is not None and catalog is not None:
        values = words.split(",") if isinstance(words, str) else words
        try:
            profile.wake_word_ids = list(catalog.resolve(values))
            del profile.unresolved["wake_words"]
        except ValueError:
            pass
    # Recompute diagnostics, never erase the user's unresolved or retired data.
    profile.issues = []
    try:
        profile.validate()
    except (ValueError, TypeError):
        profile.issues.append("invalid_trigger_profile")
    if profile.unresolved:
        profile.issues.append("migration_values_need_repair")
    if catalog is not None and profile.wake_word_ids:
        try:
            catalog.validate_selection(profile.wake_word_ids)
        except ValueError:
            profile.issues.append("wake_selection_unavailable")
    return profile


def migrate_config_file(path: Path, catalog=None) -> V2Profile:
    """Explicit atomic write, byte-for-byte backup, idempotent on repetition.

    The V1 sections and local device/feedback/clipboard preferences are retained.
    No credentials, run suppression, tokens or IDs are introduced by migration.
    """
    path = Path(path)
    original = path.read_bytes()
    raw = yaml.safe_load(original)
    profile = migrate_profile(raw, catalog)
    updated = deepcopy(raw)
    updated["v2_profile"] = asdict(profile)
    # Convert string enums from controls before safe YAML serialization.
    for key in ("primary_action", "secondary_action"):
        updated["v2_profile"]["controls"][key] = str(updated["v2_profile"]["controls"][key])
    if updated == raw:
        return profile
    backup = path.with_name(path.name + ".pre-v2.bak")
    if not backup.exists():
        with backup.open("xb") as handle:
            handle.write(original)
            handle.flush()
            os.fsync(handle.fileno())
    temp = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temp = Path(handle.name)
            yaml.safe_dump(updated, handle, allow_unicode=True, sort_keys=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()
    return profile
