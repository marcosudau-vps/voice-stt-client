"""
Setting metadata for the sixth tab "Logging & Diagnose" (OBS-050).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §10.3 — the nine entries
and their apply policies below are a transcription of that list, not a
design. §9.1 puts them into the sixth tab of the existing ``SettingsDialog``,
and §13 records why that is cheap: *"settings_metadata + SettingsDialog | ein
neuer Tab kostet nur Metadaten, keinen Dialogcode."*

**Why these definitions live in their own module.** §12.7 lists
``settings_metadata`` among the modules that are *"bewusst rein, nicht
aendern"*, and a contract test from OBS-040
(``tests/test_obs040_client_hooks.py``) enforces that by reading the file and
requiring that the word "observability" does not appear in it. Adding nine
``logging.observability.*`` paths there would have broken an existing test,
and ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §12 is explicit that a package which
has to change an existing test must stop rather than change it. Keeping the
observability vocabulary out of the pure module and composing the two tuples
here satisfies both rules at once: ``core/settings_metadata.py`` stays
byte-identical, and the new tab still costs nothing but metadata.

This is **not** the module ARCH §5.1 rules out. That one is
``ui/settings/logging_settings.py`` — dialog code for logging settings, which
is exactly what does not exist here: the dialog builds this tab through the
same generic path it builds every other tab with.

Deliberately absent (§10.3, *"NUR in config.yaml, nicht im Dialog"*):
``db_path``, ``queue_size``, ``batch_size``, ``flush_interval_s``,
``max_db_bytes``.
"""

from __future__ import annotations

from core.settings_metadata import (
    SETTING_DEFINITIONS,
    ApplyPolicy,
    SettingDefinition,
    SettingType,
)

CATEGORY = "Logging & Diagnose"

LOGGING_SETTING_DEFINITIONS: tuple[SettingDefinition, ...] = (
    SettingDefinition(
        "logging.observability.enabled", "Diagnose-Logging",
        "Erfasst Client- und Serverereignisse in der lokalen "
        "Diagnosehistorie. Der bestehende client.log-Weg bleibt davon "
        "unberührt.",
        SettingType.BOOLEAN, CATEGORY, "Diagnosehistorie", 10,
        ApplyPolicy.IMMEDIATE,
    ),
    SettingDefinition(
        "logging.observability.level", "Diagnose-Loglevel",
        "Mindestlevel für die Diagnosehistorie. Gilt gleichermaßen für "
        "Python-Logzeilen und strukturierte Ereignisse.",
        SettingType.CHOICE, CATEGORY, "Diagnosehistorie", 20,
        ApplyPolicy.IMMEDIATE,
        options=(
            ("DEBUG", "DEBUG"), ("INFO", "INFO"), ("WARNING", "WARNING"),
            ("ERROR", "ERROR"), ("CRITICAL", "CRITICAL"),
        ),
    ),
    SettingDefinition(
        "logging.observability.store_enabled", "Lokale Datenbank verwenden",
        "Schreibt die Diagnosehistorie in eine lokale SQLite-Datei. Die "
        "Änderung wirkt erst nach einem Neustart der Anwendung.",
        SettingType.BOOLEAN, CATEGORY, "Diagnosehistorie", 30,
        ApplyPolicy.APP_RESTART,
    ),
    SettingDefinition(
        "logging.observability.retention_days", "Aufbewahrung",
        "Löscht Einträge, die älter sind. 0 deaktiviert die Altersgrenze.",
        SettingType.INTEGER, CATEGORY, "Diagnosehistorie", 40,
        ApplyPolicy.IMMEDIATE,
        minimum=0, maximum=3650, step=1, unit="Tage",
    ),
    SettingDefinition(
        "logging.observability.max_entries", "Maximale Einträge",
        "Obergrenze der gespeicherten Einträge. 0 deaktiviert die "
        "Anzahlgrenze. Beide Grenzen wirken; die erste greifende gewinnt.",
        SettingType.INTEGER, CATEGORY, "Diagnosehistorie", 50,
        ApplyPolicy.IMMEDIATE,
        minimum=0, maximum=10_000_000, step=1000,
    ),
    SettingDefinition(
        "logging.observability.file_sink_enabled", "Zusätzliche JSONL-Datei",
        "Schreibt jeden Eintrag zusätzlich als eine Zeile JSON in eine "
        "tagesrotierende Datei.",
        SettingType.BOOLEAN, CATEGORY, "Datei-Ausgabe", 60,
        ApplyPolicy.IMMEDIATE,
    ),
    SettingDefinition(
        "logging.observability.file_sink_dir", "Verzeichnis",
        "Leer verwendet <Logverzeichnis>/observability. Nur Pfade innerhalb "
        "des Benutzerprofils sind zulässig.",
        SettingType.STRING, CATEGORY, "Datei-Ausgabe", 70,
        ApplyPolicy.IMMEDIATE,
        visible_when=("logging.observability.file_sink_enabled", True),
        editor="optional_path",
    ),
    SettingDefinition(
        "logging.observability.store_transcription_content",
        "Transkripttexte speichern",
        # FD-D1 asks for exactly this wording: the option also covers
        # unstructured log lines, which is the part that would surprise.
        "Speichert Transkripttexte in der Diagnosehistorie — betrifft auch "
        "technische Logzeilen. Ohne diese Option bleibt nur die Zeichenzahl "
        "erhalten.",
        SettingType.BOOLEAN, CATEGORY, "Datenschutz", 80,
        ApplyPolicy.IMMEDIATE,
    ),
    SettingDefinition(
        "logging.observability.store_raw_payload", "Server-Rohdaten speichern",
        "Speichert den Rohpayload eingehender Serverereignisse. Gilt nicht "
        "für den Channel performance.",
        SettingType.BOOLEAN, CATEGORY, "Datenschutz", 90,
        ApplyPolicy.IMMEDIATE,
    ),
)

ALL_SETTING_DEFINITIONS: tuple[SettingDefinition, ...] = (
    SETTING_DEFINITIONS + LOGGING_SETTING_DEFINITIONS
)

__all__ = [
    "CATEGORY",
    "LOGGING_SETTING_DEFINITIONS",
    "ALL_SETTING_DEFINITIONS",
]
