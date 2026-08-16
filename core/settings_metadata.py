"""Declarative metadata for editing the typed :mod:`core.config` model."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Optional

from core.config import AppConfig


class SettingType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    CHOICE = "choice"


class ApplyPolicy(str, Enum):
    IMMEDIATE = "immediate"
    HOTKEY_REREGISTER = "hotkey_reregister"
    AUDIO_RESTART = "audio_restart"
    SESSION_RECONNECT = "session_reconnect"
    APP_RESTART = "app_restart"


@dataclass(frozen=True)
class SettingDefinition:
    path: str
    label: str
    description: str
    setting_type: SettingType
    category: str
    group: str
    order: int
    apply_policy: ApplyPolicy = ApplyPolicy.IMMEDIATE
    show_in_dialog: bool = True
    advanced: bool = False
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    step: Optional[float] = None
    options: tuple[tuple[str, Any], ...] = ()
    unit: Optional[str] = None
    sensitive: bool = False
    visible_when: Optional[tuple[str, Any]] = None
    editor: Optional[str] = None


def get_config_value(config: AppConfig, path: str) -> Any:
    value: Any = config
    for part in path.split("."):
        if not hasattr(value, part):
            raise KeyError(path)
        value = getattr(value, part)
    return value


def set_config_value(config: AppConfig, path: str, value: Any) -> None:
    parts = path.split(".")
    target: Any = config
    for part in parts[:-1]:
        if not hasattr(target, part):
            raise KeyError(path)
        target = getattr(target, part)
    if not hasattr(target, parts[-1]):
        raise KeyError(path)
    setattr(target, parts[-1], value)


def build_candidate(
    current: AppConfig, changes: dict[str, Any]
) -> AppConfig:
    candidate = copy.deepcopy(current)
    for path, value in changes.items():
        set_config_value(candidate, path, value)
    candidate.validate()
    return candidate


SETTING_DEFINITIONS = (
    SettingDefinition(
        "hotkey.enabled", "Globale Hotkeys", "Globale Windows-Hotkeys aktivieren.",
        SettingType.BOOLEAN, "Allgemein", "Hotkeys", 10,
        ApplyPolicy.HOTKEY_REREGISTER,
    ),
    SettingDefinition(
        "hotkey.toggle_key", "Primäre Diktataktion",
        "Startet ein Diktat; während eines Hotkey-Diktats wird die Frist verlängert.",
        SettingType.STRING, "Allgemein", "Hotkeys", 20,
        ApplyPolicy.HOTKEY_REREGISTER, editor="hotkey",
    ),
    SettingDefinition(
        "hotkey.finish_key", "Diktat abschließen",
        "Optionaler separater Hotkey zum sofortigen Abschluss.",
        SettingType.STRING, "Allgemein", "Hotkeys", 30,
        ApplyPolicy.HOTKEY_REREGISTER, editor="optional_hotkey",
    ),
    SettingDefinition(
        "hotkey.cancel_key", "Diktat verwerfen",
        "Optionaler separater Hotkey zum Verwerfen.",
        SettingType.STRING, "Allgemein", "Hotkeys", 40,
        ApplyPolicy.HOTKEY_REREGISTER, editor="optional_hotkey",
    ),
    SettingDefinition(
        "hotkey.reinsert_last_key", "Letztes Transkript erneut einfügen",
        "Globaler Hotkey für die Reinsertion.",
        SettingType.STRING, "Allgemein", "Hotkeys", 50,
        ApplyPolicy.HOTKEY_REREGISTER, editor="hotkey",
    ),
    SettingDefinition(
        "hotkey.overlay_toggle_key", "Overlay umschalten",
        "Optionaler globaler Hotkey für das Overlay.",
        SettingType.STRING, "Allgemein", "Hotkeys", 60,
        ApplyPolicy.HOTKEY_REREGISTER, editor="optional_hotkey",
    ),
    SettingDefinition(
        "text_injection.append_space", "Leerzeichen anhängen",
        "Hängt nach jedem finalen Segment ein Leerzeichen an.",
        SettingType.BOOLEAN, "Allgemein", "Textinjektion", 100,
    ),
    SettingDefinition(
        "clipboard.restore_previous", "Zwischenablage wiederherstellen",
        "Stellt vorherigen Clipboard-Inhalt nach dem Einfügen wieder her.",
        SettingType.BOOLEAN, "Allgemein", "Zwischenablage", 120,
    ),
    SettingDefinition(
        "history.persistent.max_entries", "Maximale Verlaufseinträge",
        "0 deaktiviert das Anzahl-Limit.",
        SettingType.INTEGER, "Allgemein", "Verlauf", 140,
        minimum=0, maximum=100000, step=1,
    ),
    SettingDefinition(
        "logging.level", "Loglevel", "Anwendungsweiter Mindest-Loglevel.",
        SettingType.CHOICE, "Allgemein", "Logging", 160,
        ApplyPolicy.APP_RESTART,
        options=(("DEBUG", "DEBUG"), ("INFO", "INFO"), ("WARNING", "WARNING"), ("ERROR", "ERROR")),
    ),
    SettingDefinition(
        "server.url", "WebSocket-URL", "Live-WebSocket-Endpunkt des Servers.",
        SettingType.STRING, "Verbindung & Betriebsmodus", "Verbindung", 10,
        ApplyPolicy.SESSION_RECONNECT,
    ),
    SettingDefinition(
        "session.mode", "Legacy-Betriebsmodus",
        "Nur noch für die Migration alter Konfigurationen. Maßgeblich sind die "
        "beiden Triggerschalter darunter.",
        SettingType.CHOICE, "Verbindung & Betriebsmodus", "Legacy", 30,
        ApplyPolicy.SESSION_RECONNECT,
        options=(("Hotkey", "hotkey"), ("Wake Word", "wake_word")),
    ),
    SettingDefinition(
        "session.manual_trigger_enabled", "Manueller Trigger",
        "Aktiviert manuelle Steuerung per Hotkey/Tray.",
        SettingType.BOOLEAN, "Verbindung & Betriebsmodus", "Triggerquellen", 32,
        ApplyPolicy.SESSION_RECONNECT,
    ),
    SettingDefinition(
        "session.wake_word_trigger_enabled", "Wake-Word-Trigger",
        "Aktiviert serverseitige Wakeword-Erkennung.",
        SettingType.BOOLEAN, "Verbindung & Betriebsmodus", "Triggerquellen", 35,
        ApplyPolicy.SESSION_RECONNECT,
    ),
    SettingDefinition(
        "session.wake_words", "Wake Word", "Vom Server veröffentlichte Wake-Word-ID.",
        SettingType.STRING, "Verbindung & Betriebsmodus", "Wake Word", 40,
        ApplyPolicy.SESSION_RECONNECT,
        visible_when=("session.mode", "wake_word"),
    ),
    SettingDefinition(
        "session.wake_word_sensitivity", "Empfindlichkeit",
        "Optionale serverseitige Wake-Word-Empfindlichkeit.",
        SettingType.FLOAT, "Verbindung & Betriebsmodus", "Wake Word", 50,
        ApplyPolicy.SESSION_RECONNECT, minimum=0.0, maximum=1.0, step=0.01,
        visible_when=("session.mode", "wake_word"),
        editor="optional_float",
    ),
    SettingDefinition(
        "dictation_window.initial_speech_timeout", "Zeit bis zur ersten Sprache",
        "Beendet einen versehentlichen Start ohne erkanntes recording_started.",
        SettingType.FLOAT, "Verbindung & Betriebsmodus", "Hotkey-Diktatfenster", 80,
        minimum=1.0, maximum=120.0, step=1.0, unit="s",
        visible_when=("session.mode", "hotkey"),
    ),
    SettingDefinition(
        "dictation_window.followup_timeout", "Nachsprechfenster",
        "Wartezeit nach recording_ended auf einen weiteren Sprachabschnitt.",
        SettingType.FLOAT, "Verbindung & Betriebsmodus", "Hotkey-Diktatfenster", 90,
        minimum=0.1, maximum=60.0, step=0.1, unit="s",
        visible_when=("session.mode", "hotkey"),
    ),
    SettingDefinition(
        "dictation_window.extension_seconds", "Manuelle Verlängerung",
        "Zusätzliche Zeit durch erneutes Drücken des primären Hotkeys.",
        SettingType.FLOAT, "Verbindung & Betriebsmodus", "Hotkey-Diktatfenster", 100,
        minimum=1.0, maximum=120.0, step=1.0, unit="s",
        visible_when=("session.mode", "hotkey"),
    ),
    SettingDefinition(
        "dictation_window.timeout_warning_seconds", "Timeout-Vorwarnung",
        "Startet Tickton und LED-Countdown so viele Sekunden vor Ablauf.",
        SettingType.FLOAT, "Verbindung & Betriebsmodus", "Hotkey-Diktatfenster", 110,
        minimum=0.5, maximum=30.0, step=0.5, unit="s",
        visible_when=("session.mode", "hotkey"),
    ),
    SettingDefinition(
        "audio.device", "Mikrofon", "Statische Eingabegeräteauswahl.",
        SettingType.INTEGER, "Geräte & Audio", "Mikrofon", 10,
        ApplyPolicy.AUDIO_RESTART, editor="audio_device",
    ),
    SettingDefinition(
        "audio.sample_rate", "Samplerate", "Bevorzugte Audio-Samplerate.",
        SettingType.INTEGER, "Geräte & Audio", "Audio", 30,
        ApplyPolicy.AUDIO_RESTART, minimum=8000, maximum=192000, step=1000,
    ),
    SettingDefinition(
        "overlay.enabled", "Overlay anzeigen", "Passives Transkript-Overlay aktivieren.",
        SettingType.BOOLEAN, "Erscheinungsbild & Feedback", "Overlay", 10,
    ),
    SettingDefinition(
        "overlay.show_realtime_text", "Realtime-Text anzeigen",
        "Zeigt unverbindliche Zwischentexte ausschließlich visuell.",
        SettingType.BOOLEAN, "Erscheinungsbild & Feedback", "Overlay", 20,
    ),
    SettingDefinition(
        "overlay.position", "Position", "Position des passiven Overlays.",
        SettingType.CHOICE, "Erscheinungsbild & Feedback", "Overlay", 30,
        options=tuple((value, value) for value in (
            "bottom_center", "top_right", "top_left", "bottom_right", "bottom_left"
        )),
    ),
    SettingDefinition(
        "overlay.opacity", "Deckkraft", "Deckkraft des Overlays.",
        SettingType.FLOAT, "Erscheinungsbild & Feedback", "Overlay", 40,
        minimum=0.0, maximum=1.0, step=0.05,
    ),
    SettingDefinition(
        "overlay.font_size", "Schriftgröße", "Schriftgröße in Punkten.",
        SettingType.INTEGER, "Erscheinungsbild & Feedback", "Overlay", 50,
        minimum=6, maximum=72, step=1,
    ),
    SettingDefinition(
        "overlay.font_family", "Schriftart",
        "Optionale installierte Schriftfamilie; leer verwendet den Qt-Standard.",
        SettingType.STRING, "Erscheinungsbild & Feedback", "Overlay", 60,
    ),
    SettingDefinition(
        "overlay.background_color", "Hintergrundfarbe",
        "Farbe im Format #RRGGBB.",
        SettingType.STRING, "Erscheinungsbild & Feedback", "Overlay", 70,
    ),
    SettingDefinition(
        "overlay.text_color", "Schriftfarbe",
        "Farbe im Format #RRGGBB.",
        SettingType.STRING, "Erscheinungsbild & Feedback", "Overlay", 75,
    ),
    SettingDefinition(
        "feedback.sounds_enabled", "Sounds", "Optionale nicht blockierende Tonsignale.",
        SettingType.BOOLEAN, "Erscheinungsbild & Feedback", "Feedback", 80,
    ),
    SettingDefinition(
        "feedback.wake_word_sound", "Wake-Word-Sound", "Lokaler Pfad zu einem Soundasset.",
        SettingType.STRING, "Erscheinungsbild & Feedback", "Feedback", 90,
        visible_when=("feedback.sounds_enabled", True),
    ),
    SettingDefinition(
        "feedback.start_sound", "Startsound", "Lokaler Pfad zu einem Soundasset.",
        SettingType.STRING, "Erscheinungsbild & Feedback", "Feedback", 100,
        visible_when=("feedback.sounds_enabled", True),
    ),
    SettingDefinition(
        "feedback.stop_sound", "Stopsound", "Lokaler Pfad zu einem Soundasset.",
        SettingType.STRING, "Erscheinungsbild & Feedback", "Feedback", 110,
        visible_when=("feedback.sounds_enabled", True),
    ),
    SettingDefinition(
        "feedback.complete_sound", "Abschlusssound", "Lokaler Pfad zu einem Soundasset.",
        SettingType.STRING, "Erscheinungsbild & Feedback", "Feedback", 120,
        visible_when=("feedback.sounds_enabled", True),
    ),
    SettingDefinition(
        "feedback.cancel_sound", "Abbruchsound", "Lokaler Pfad zu einem Soundasset.",
        SettingType.STRING, "Erscheinungsbild & Feedback", "Feedback", 130,
        visible_when=("feedback.sounds_enabled", True),
    ),
    SettingDefinition(
        "feedback.warning_sound", "Warnsound", "Lokaler Pfad zu einem Soundasset.",
        SettingType.STRING, "Erscheinungsbild & Feedback", "Feedback", 140,
        visible_when=("feedback.sounds_enabled", True),
    ),
    SettingDefinition(
        "feedback.error_sound", "Fehlersound", "Lokaler Pfad zu einem Soundasset.",
        SettingType.STRING, "Erscheinungsbild & Feedback", "Feedback", 150,
        visible_when=("feedback.sounds_enabled", True),
    ),
    SettingDefinition(
        "feedback.timeout_tick_sound", "Timeout-Ticken",
        "Lokaler Pfad zum Tickton für die Diktatfenster-Vorwarnung.",
        SettingType.STRING, "Erscheinungsbild & Feedback", "Feedback", 155,
        visible_when=("feedback.sounds_enabled", True),
    ),
    SettingDefinition(
        "led.enabled", "ReSpeaker-LED", "LED-Ring des XVF3800 automatisch verwenden.",
        SettingType.BOOLEAN, "Erscheinungsbild & Feedback", "Feedback", 160,
    ),
    SettingDefinition(
        "led.sink", "LED-Ausgabe",
        "Hardware-Ring, Simulatorfenster (Zusatzpaket) oder keine Ausgabe.",
        SettingType.CHOICE, "Erscheinungsbild & Feedback", "Feedback", 165,
        visible_when=("led.enabled", True),
        options=(
            ("ReSpeaker", "respeaker"),
            ("Simulator", "simulator"),
            ("Keine", "null"),
        ),
    ),
    SettingDefinition(
        "led.brightness", "LED-Helligkeit", "Helligkeit von 0 bis 255.",
        SettingType.INTEGER, "Erscheinungsbild & Feedback", "Feedback", 170,
        minimum=0, maximum=255, step=1,
        visible_when=("led.enabled", True),
    ),
)


def visible_definitions(
    config: AppConfig,
    definitions: Iterable[SettingDefinition] = SETTING_DEFINITIONS,
) -> tuple[SettingDefinition, ...]:
    result = []
    for definition in definitions:
        if not definition.show_in_dialog:
            continue
        if definition.visible_when is not None:
            path, expected = definition.visible_when
            if get_config_value(config, path) != expected:
                continue
        result.append(definition)
    return tuple(result)
