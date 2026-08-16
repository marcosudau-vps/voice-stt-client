# OUTPUT INDEX

```text
Status  ABGESCHLOSSEN
Run     RUN-OBS-000-01_2026-08-15_CLAUDE
Gate    OBS-000 PASS
Datum   2026-08-15
```

Pfade relativ zu `ARBEITSDATEIEN/AP_THEMA_LOGGING/`, sofern nicht anders
angegeben.

---

## Normative Freeze-Artefakte

| Artefakt | Zweck | Ablage | Status |
|---|---|---|---|
| `LOGGING_ARCHITEKTUR_FREEZE_V1.md` | Invarianten O-01…O-14, Endzustand, Teil A/B, Komponenten, Nebenläufigkeit, Failure Domain, Hot-Path-Regeln, Zukunftsgrenzen | `00_NORMATIV/` | **NEU, FROZEN** |
| `LOGGING_CONTRACTS_FREEZE_V1.md` | CanonicalRecord, Wertemengen, Normalizer, Redaction, SQLite-Schema, Query-, UI- und Sink-Verträge, Konfiguration, V1-Hookliste | `00_NORMATIV/` | **NEU, FROZEN** |
| `LOGGING_DECISIONS_FREEZE_V1.md` | 39 geschlossene Entscheidungen, 19 Widersprüche, Korrektur der Work-Package-Grenzen | `00_NORMATIV/` | **NEU, FROZEN** |
| `README.md` | Freeze-Stand, Autoritätsreihenfolge, Änderungsregel | `00_NORMATIV/` | geändert |

## Evidence

| Artefakt | Zweck | Ablage | Status |
|---|---|---|---|
| `EV-01_QUELLEN_UND_HASHES.md` | SHA-256 aller Quellen, Vergleich gegen das Archiv | `40_EVIDENCE/OBS-000/` | **NEU** |
| `EV-02_GEZIELTE_CODEPRUEFUNGEN.md` | 13 Codeprüfungen mit Kommando, Ausgabe, Bewertung; darunter zwei Korrekturen der Vorarbeit und der Abschluss von W-16 | `40_EVIDENCE/OBS-000/` | **NEU** |
| `EV-03_PRODUKT_BASELINE_GIT.md` | Git-Baseline der drei Repositories, Risiko R-3, Einhaltung der Verbote | `40_EVIDENCE/OBS-000/` | **NEU** |
| `EV-04_PLANKONSISTENZ.md` | Konsistenzcheck Planung ↔ Freeze, Nummernkreise, Statusfelder, Ablage-Altlasten | `40_EVIDENCE/OBS-000/` | **NEU** |

## Analyse

| Artefakt | Zweck | Ablage | Status |
|---|---|---|---|
| `SOURCE_MANIFEST.md` | Herkunft und Integrität der neun Vorarbeitsdateien, Behandlung der Mehrfachablagen, Autoritätseinstufung | `10_ANALYSE/CLAUDE_VORARBEIT/` | **NEU** |
| die neun Vorarbeitsdateien | Herleitung | `10_ANALYSE/CLAUDE_VORARBEIT/` | unverändert |

## Planung

| Artefakt | Zweck | Ablage | Status |
|---|---|---|---|
| `00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md` | Ausführungsfahrplan | `20_PLANUNG/LOGGING_GESAMTPLAN/` | geändert, `FROZEN_BASELINE` |
| `01_WORKPACKAGE_INDEX.md` | Status, Abhängigkeiten, Abbildung 14 → 6 | dito | geändert |
| `02_OBS000_FREEZE_CHECKLIST.md` | Nachweis, wo welche Entscheidung fiel | dito | geändert, abgeschlossen |
| `03_TRACEABILITY_MATRIX.md` | Invarianten, Features, zwölf neue Nachweispflichten | dito | geändert |
| `README.md` | Einstieg und Freeze-Stand | dito | geändert |
| `WP-OBS-010_CANONICAL_MODEL_CONTRACTS.md` | implementation-ready | `…/workpackages/` | geändert, **READY** |
| `WP-OBS-020_INGRESS_HEALTH_REDACTION.md` | implementation-ready | dito | geändert, **READY** |
| `WP-OBS-030_QUEUE_WORKER_SQLITE_RETENTION.md` | Titelkorrektur, D-2/D-4/AR-5/AR-6 | dito | geändert |
| `WP-OBS-040_SERVER_LIVE_ADAPTER_CLIENT_OBSERVATION_HOOKS.md` | Hookvorgaben, Verbote, N-07 | dito | geändert |
| `WP-OBS-050_LOCAL_QUERY_MINIMAL_UI_SETTINGS.md` | Ringbufferwegfall, Abhängigkeit, Configauflage | dito | geändert |
| `WP-OBS-060_V1_HARDENING_EVIDENCE_BASELINE.md` | Isolationsnachweis, Mutationschecks, manuelle Abnahme | dito | geändert |
| `WP-OBS-110_SERVER_CONTROL_ADMIN_AUTH_CAPABILITIES.md` | Capability-Übergabe, `sensitive`-Auflage | dito | geändert |
| `WP-OBS-120_REMOTE_SERVER_HISTORY_GLOBAL_LOGS.md` | Providerreihenfolge, Capabilities, HTTP-Auflage | dito | geändert |
| `WP-OBS-140_LED_CONTROLLER_LOGGING_INTEGRATION.md` | Klarstellung zur `lefx.*`-Regel | dito | geändert |

## Run-Dokumentation

| Artefakt | Zweck | Ablage | Status |
|---|---|---|---|
| `RUN_REPORT.md` | vollständiger Bericht inkl. Readiness-Review | dieser Ordner | geändert |
| `OUTPUT_INDEX.md` | diese Übersicht | dieser Ordner | geändert |

## Übergreifend

| Artefakt | Zweck | Ablage | Status |
|---|---|---|---|
| `LOG_VERLAUF.md` | ein Meilensteineintrag für diesen Run | `ARBEITSDATEIEN/` | geändert |

---

## Nicht verändert

```text
voice-stt-client               nur lesend untersucht
voice-stt-server               nur lesend untersucht
led_controller_respeaker-v3    nicht beruehrt
00_GRUNDLAGEN/*                unveraendert (Herleitung bleibt erhalten)
05_DRAFTS_UNGEPRUEFT/*         unveraendert
10_ANALYSE/CLAUDE_VORARBEIT/   nur SOURCE_MANIFEST.md hinzugefuegt
90_ARCHIV/*                    unveraendert
```
