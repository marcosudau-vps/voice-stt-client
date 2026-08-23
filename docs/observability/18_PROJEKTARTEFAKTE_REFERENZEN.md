# Projektartefakte und Referenzen

## Kurz und einfach erklärt

Diese Produktdokumentation erklärt, **wie das Logging funktioniert**.

Daneben existiert die Entwicklungsakte. Dort steht:

- warum eine Entscheidung damals getroffen wurde;
- welcher Lauf was änderte;
- welche Tests tatsächlich liefen;
- welches Gate bestand oder scheiterte.

Für Produktverständnis: `docs/observability/`.  
Für forensische Projektgeschichte: `ARBEITSDATEIEN`.

---

## 1. Autoritätsprinzip

Für Arbeits-/Contractfragen gilt sinngemäß:

```text
1. 00_NORMATIV
2. aktives Work Package / freigegebene Planung
3. realer Produktcode für Ist-Aussagen
4. Analysen
5. historische/Draft-Unterlagen
```

Ein historisches oder ungeprüftes Dokument darf eine eingefrorene normative Entscheidung nicht still überschreiben.

---

## 2. Normative Freeze-Unterlagen

Teil A ist archiviert (siehe Abschnitt 12). Die Arbeitsakte liegt unter:

```text
ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/00_NORMATIV/
├── README.md
├── LOGGING_ARCHITEKTUR_FREEZE_V1.md
├── LOGGING_CONTRACTS_FREEZE_V1.md
└── LOGGING_DECISIONS_FREEZE_V1.md
```

### `LOGGING_ARCHITEKTUR_FREEZE_V1.md`

Invarianten, Komponenten, Nebenläufigkeit, Failure Domain, Hot-Path-Regeln und Zukunftsgrenzen.

### `LOGGING_CONTRACTS_FREEZE_V1.md`

Canonical Record, Normalizer, SQLite-Schema, Query-, UI- und Configverträge sowie Hooklisten.

### `LOGGING_DECISIONS_FREEZE_V1.md`

Geschlossene Entscheidungen, Begründungen und Widerspruchsauflösungen.

---

## 3. Planung

```text
ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/20_PLANUNG/
└── LOGGING_GESAMTPLAN/
```

Teil B (`OBS-100` bis `OBS-180`) ist dort ebenfalls bereits als Work-Package-Draft abgelegt (`20_PLANUNG/LOGGING_GESAMTPLAN/workpackages/WP-OBS-100_*.md` bis `WP-OBS-180_*.md`) und startet erst nach der Triggerarchitektur-Migration.

Zentrale Datei:

```text
00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md
```

Dazu die einzelnen Work Packages.

---

## 4. Work-Package-Kette Teil A

```text
OBS-000  Plan Freeze & Baseline
OBS-010  Canonical Model, Redaction, Normalizer & Contracts
OBS-020  Ingress, Backpressure, Health & Python-Logging-Handler
OBS-030  Worker, SQLite-Store, Retention & JSONL-Sink
OBS-040  Server Live Adapter & strukturierte Client-Hooks
OBS-050  Local Query, Log View & Settings
OBS-060  V1 Hardening, Evidence & Baseline
```

---

## 5. Ausführung

```text
ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/
├── LOGGING_V1_CHECKLISTE.md
├── prompts/
└── runs/
```

Wichtiger letzter Hardening-Run:

```text
runs/RUN-OBS-060-01_2026-08-18/
```

---

## 6. Evidence

```text
ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/40_EVIDENCE/
├── OBS-000/
├── OBS-010/
├── OBS-020/
├── OBS-030/
├── OBS-040/
├── OBS-050/
└── OBS-060/
```

Dort liegen je nach Paket:

- Testresultate;
- Diff-Summary;
- Contract Coverage;
- Failure Injection;
- Performanceprobes;
- Mutation Checks;
- Gate Reviews;
- Runtime-Isolation;
- manuelle/halbmanuelle Nachweise.

---

## 7. Projektsteuerung

```text
ARBEITSDATEIEN/00_STEUERUNG/
├── CURRENT_STATE.md
├── MASTERPLAN.md
├── LOG_VERLAUF.md
├── OFFENE_PUNKTE.md
└── ARBEITSPROZESS.md
```

`LOG_VERLAUF.md` ist append-only zu behandeln.

---

## 8. Wichtige Produktcommits

| Commit | Inhalt |
|---|---|
| `b363346` | OBS-010 + OBS-020 Foundation |
| `cb0b81f` | OBS-030 Persistenz und Worker |
| `91a7b7f` | OBS-040 Observation Hooks |
| `7fc6ca6` | OBS-050 Local Log View |
| `8eea774` | OBS-060 Hardening/Evidence Checkpoint |
| `d9369c5` | Logging Diagnostics UI Polish |

Ein späterer organisatorischer Teilabschluss-/Dokumentationscommit kann diese Liste ergänzen.

---

## 9. Zentrale Produktdateien

### Core

```text
core/observability/
```

insbesondere:

```text
models.py
redaction.py
normalizer.py
ingress.py
health.py
worker.py
manager.py
adapters/
storage/
query/
sinks/
```

### Integration

```text
core/logging_setup.py
core/config.py
core/controller.py
core/stt_session.py
core/session_coordinator.py
core/event_stream.py
core/audio_capture.py
ui/application.py
ui/settings_dialog.py
```

### UI

```text
ui/logs/
```

---

## 10. Serverprotokoll-Referenzen

Für den operativen `/ws/transcribe`-Vertrag:

```text
server-docs-for-client-development/
├── 02-websocket-protokoll.md
├── 03-server-events-kurzreferenz.md
├── 04-server-events-katalog-und-chronologie.md
└── ...
```

Diese Dokumente sind detaillierter als die Observability-Einordnung in dieser Produktdokumentation.

---

## 11. Welche Quelle für welche Frage?

| Frage | Primärquelle |
|---|---|
| Wie benutzt/erweitert man Observability? | `docs/observability/` |
| Was ist der normative Architekturvertrag? | `00_NORMATIV/` |
| Warum wurde eine Variante gewählt? | `LOGGING_DECISIONS_FREEZE_V1.md` |
| Was war pro WP gefordert? | `20_PLANUNG` / Work Packages |
| Was wurde tatsächlich getestet? | `40_EVIDENCE` |
| Was ist aktueller Gesamtprojektstand? | `CURRENT_STATE.md` |
| Wie war der historische Verlauf? | `LOG_VERLAUF.md` |
| Wie lautet der Server-WebSocket-Vertrag? | `server-docs-for-client-development/` |

---

## 12. Teilabschluss-Snapshot

Mit `OBS-CLOSE-001` ist Teil A / Pre-Trigger Foundation als zusammenhängende Arbeitsakte archiviert. `LOGGING_OBSERVABILITY` liegt seither **nicht mehr** unter `10_AKTUELL`, sondern vollständig unter:

```text
ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/
├── README.md
├── LOGGING_OBSERVABILITY/
└── STEUERUNG_SNAPSHOT/
```

Der Snapshot enthält:

- Kopien der globalen Steuerungsdateien zum Abschlusszeitpunkt (`LOG_VERLAUF.md`, `CURRENT_STATE.md`, `MASTERPLAN.md`) unter `STEUERUNG_SNAPSHOT/`;
- diese Produktdokumentation (unter `80_DOCS/` innerhalb der Arbeitsakte sowie kanonisch unter `docs/observability/`);
- Git-/Statusreferenz im `RUN_REPORT.md` des Abschlussruns (`30_AUSFUEHRUNG/runs/RUN-OBS-CLOSE-001_2026-08-23/`);
- Verweisindex auf Normativ, Planung, Runs und Evidence (diese Datei sowie das Archiv-`README.md`).

Status: `CONTROLLED CLOSED / ACCEPTED PRE-TRIGGER BASELINE`. Formal: `G-OBS-V1 NOT PASSED`. Teil B (`OBS-100` bis `OBS-180`) ist `DEFERRED / POST-TRIGGER` und startet erst nach der Triggerarchitektur-Migration; siehe `MASTERPLAN.md` und [19_AUSBLICK_TEIL_B.md](19_AUSBLICK_TEIL_B.md).
