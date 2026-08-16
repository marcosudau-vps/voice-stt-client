---
id: OBS-MASTER
status: DRAFT_REVIEW
authority: planning
workstream: OBS
last_updated: 2026-08-15
---

# Gesamtimplementierungsplan – Logging / Observability

## 0. Status und Zweck

Dieses Dokument beschreibt **den vollständigen Ausbaupfad** der Logging-/Observability-Architektur – nicht nur die vorgezogene erste Ausbaustufe.

Der Plan ist absichtlich zweigeteilt:

- **TEIL A – Observability Foundation vor der Triggerarchitektur-Migration**
- **TEIL B – Vollausbau nach Stabilisierung der Triggerarchitektur**

TEIL A soll vorgezogen werden, damit die anschließende Triggerarchitektur-Migration mit belastbarer, strukturierter Laufzeitdiagnostik beobachtet werden kann.

TEIL B bleibt bereits jetzt architektonisch berücksichtigt, wird aber erst nach der fachlichen Trigger-/Session-Migration umgesetzt.

> Grundsatz: **Featureumfang in V1 begrenzen, Endarchitektur bereits jetzt berücksichtigen.**

---

# 1. Quellen- und Autoritätsmodell

## 1.1 Zielbild

Langfristige Sollquelle:

- `LOGGING_ZIELBILD_ARCHITEKTUR_GESAMTSPEZIFIKATION_ENTWURF.md`

V1-Abgrenzung:

- `LOGGING_V1_ABGRENZUNG_ENTWURF.md`

Historischer/ungeprüfter Ideenentwurf:

- `.unverbindlich_ungeprueft/ErsterEntwurf_Logging.md`

Code-/Architekturerkenntnisse:

- `LETZTE_ARCHITEKTURKLAERUNGEN_VOR_PLAN_FREEZE.md`
- Code-Only-Architekturaufnahme der Triggerarchitektur
- neu erzeugte Logging-Code-Audits und adversarial Review, sobald in den Arbeitsbereich übernommen

## 1.2 Wichtige Regel

Die aktuellen Logging-Spezifikationen sind noch Entwürfe.

**OBS-000 ist deshalb ein verpflichtendes Freeze-Gate.** Vor produktiver Implementierung müssen die jüngsten Claude-Audits und das adversariale Review in diesen Plan eingearbeitet werden.

Kein Coding-Agent darf offene Architekturfragen selbst stillschweigend entscheiden.

---

# 2. Nicht verhandelbare Architektur-Invarianten

## O-01 – Observability Only

Logging besitzt keine fachliche Runtime-Autorität.

## O-02 – Fan-out statt Vermittlung

```text
Event
├── Fachlogik / Feedback
└── Observability
```

Nicht:

```text
Event
→ Observability
→ Fachlogik
```

## O-03 – Non-Blocking

Kein Audio-, WebSocket-, Controller- oder UI-Hot-Path wartet auf DB-/File-I/O.

## O-04 – Bounded Memory

Queues und Livebuffer sind begrenzt.

## O-05 – Failure Isolation

SQLite-, File-, Queue-, Worker-, Query- oder Providerfehler dürfen die Anwendung fachlich nicht beeinflussen.

## O-06 – Struktur statt Textparsing

Kritische Abläufe werden strukturiert korrelierbar erfasst.

## O-07 – Source Preservation

Producer/Herkunft, Channel, Level und Type bleiben getrennte Dimensionen.

## O-08 – Replay Safety

Replay darf keine unkontrollierten Persistenzduplikate erzeugen.

## O-09 – Security / Redaction

Secrets dürfen niemals in LogStore, Raw Payload oder File Sink persistiert werden.

## O-10 – Query Independence

UI kennt weder SQLite noch WebSocket-/Admin-Transportdetails.

## O-11 – Extensible Producer / Provider Boundaries

LED-Controller, ServerHistory und weitere Quellen müssen später per Adapter/Provider ergänzbar sein.

## O-12 – Admin Separation

Logging benutzt später privilegierte Query-Provider, besitzt aber weder Admin-Key noch Authentifizierungszustand selbst.

## O-13 – Runtime-Control-Plane bleibt getrennt

`/ws/logs` bleibt Observability. Die fachliche Activation-Wahrheit liegt nicht im Logging.

---

# 3. Bekannte reale Integrationsgrenzen

Aus der letzten Triggerarchitektur-Untersuchung sind insbesondere folgende Punkte bereits geklärt:

- `/ws/logs` ist ein sessiongebundener Observability-/Eventstream mit eigenem Token, Replay, Cursor und Reconnect-Zustand.
- `/ws/transcribe` bleibt Runtime-/Control-Plane.
- Feedback kann bereits ohne `/ws/logs` über den STT-Fallback funktionieren.
- Der Client besitzt `core/event_stream.py`, `core/session_coordinator.py`, `core/event_cursor_store.py`, Eventnormalisierung und Feedbackreduzierung.
- Logging darf den Feedbackpfad deshalb nur **parallel** beobachten.
- Identifizierte Observation-Hooks umfassen u. a. Connection, EventStream, Trigger send/ack, Audioqueue, Settings Apply, Feedback, LED, Fehlerklassifizierung und Performance.
- Audio-Paket- und VAD-nahe Pfade sind Hot Paths; dort nur Zustandswechsel/Aggregate, keine Einzelrecord-Flut.

Diese Erkenntnisse gelten als Randbedingungen für alle Work Packages.

---

# 4. Gesamtphasen

```text
PHASE 0   Freeze / Verträge
    ↓
PHASE A   Observability Foundation V1
    ↓
OBSERVABILITY BASELINE COMMIT / GATE
    ↓
Triggerarchitektur-Migration
    ↓
PHASE B   Post-Migration Instrumentation
    ↓
PHASE C   Admin / Remote Server History
    ↓
PHASE D   Weitere Producer / Sinks
    ↓
PHASE E   Advanced Query / Forensics
    ↓
FINAL GATE
```

---

# 5. Work-Package-Übersicht

| Reihenfolge | ID | Titel | Zeitpunkt | Hauptergebnis |
|---:|---|---|---|---|
| 0 | OBS-000 | Plan Freeze & Baseline | vor allem | freigegebene Verträge |
| 1 | OBS-010 | Canonical Model & Contracts | vor Trigger-Migration | stabiles Datenmodell |
| 2 | OBS-020 | Ingress, Health & Redaction | vor Trigger-Migration | sichere passive Aufnahme |
| 3 | OBS-030 | Queue, Worker, SQLite & Retention | vor Trigger-Migration | lokale Persistenz |
| 4 | OBS-040 | Live Adapter & Client Observation Hooks | vor Trigger-Migration | reale Live-Daten |
| 5 | OBS-050 | Local Query, Minimal UI & Settings | vor Trigger-Migration | nutzbare Diagnoseansicht |
| 6 | OBS-060 | V1 Hardening, Failure/Perf Gate & Baseline | vor Trigger-Migration | abgenommene Foundation |
| 7 | OBS-100 | Post-Trigger Instrumentation Completion | nach Trigger-Migration | finaler Lifecycle sichtbar |
| 8 | OBS-110 | Server Control, Admin Auth & Capabilities | später | privilegierte Control-Schicht |
| 9 | OBS-120 | Remote Server History & Global Logs | später | Serverhistorie in LogView |
| 10 | OBS-130 | Serverweite Admin-Settings im Desktopclient | später | Admin-Konfiguration |
| 11 | OBS-140 | LED-Controller Logging Integration | später | weitere Producerquelle |
| 12 | OBS-150 | Erweiterte Sinks / Storage Backends | später | optionale Zielsysteme |
| 13 | OBS-160 | Advanced Query / UX | später | Komfort und Analyse |
| 14 | OBS-170 | Cross-Source Correlation / Forensics | später | Client-vs-Server-Vergleich |
| 15 | OBS-180 | Final Hardening, Docs & Acceptance | Abschluss | stabiler Gesamtzustand |

---

# 6. TEIL A – Vor der Triggerarchitektur-Migration

## Ziel von Teil A

Nach OBS-060 soll der Client:

- lokale Python-Logs strukturiert erfassen;
- ausgewählte Client-Observation-Events strukturiert erfassen;
- Server-Live-Events aus dem bestehenden Eventstream passiv übernehmen;
- die Records normalisieren;
- lokal non-blocking persistieren;
- Replay sinnvoll deduplizieren;
- lokale Historie abfragen;
- eine minimale Logansicht besitzen;
- grundlegende Logging-Einstellungen besitzen;
- Fehler der Logging-Infrastruktur isolieren;
- die kommende Triggerarchitektur-Migration diagnostisch begleiten.

Nicht enthalten:

- Admin-Authentifizierung;
- globale/historische Remote-Serverlogs;
- serverweite Config;
- LED-Controller-Produktion;
- Remote Collector;
- komplexe Analytics.

---

# 7. OBS-000 – Plan Freeze & Baseline

## Ziel

Alle bereits erzeugten Logging-Audits und das adversariale Review gegen Zielbild und V1-Abgrenzung führen und die noch offenen Architekturentscheidungen schließen.

## Aufgaben

- [ ] `LOGGING_CODE_INTEGRATION_AUDIT.md` übernehmen.
- [ ] `LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md` übernehmen.
- [ ] `LOGGING_CONCURRENCY_FAILURE_MODEL.md` übernehmen.
- [ ] `LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md` übernehmen.
- [ ] `LOGGING_V1_IMPLEMENTATION_PLAN.md` übernehmen.
- [ ] `LOGGING_OPEN_DECISIONS.md` übernehmen.
- [ ] `LOGGING_ADVERSARIAL_REVIEW.md` übernehmen.
- [ ] Widersprüche gegen Zielbild protokollieren.
- [ ] echte Codefakten von Architekturvorschlägen trennen.
- [ ] CanonicalRecord finalisieren.
- [ ] Client-Channels finalisieren.
- [ ] Dedupe-Key finalisieren.
- [ ] Queue-/Backpressure-Policy finalisieren.
- [ ] SQLite-Grundschema finalisieren.
- [ ] Privacy-/Raw-Defaults finalisieren.
- [ ] V1 File-Sink-Scope finalisieren.
- [ ] konkrete Eventstream-Fan-out-Stelle finalisieren.
- [ ] UI-Platzierung finalisieren.
- [ ] exakte V1-Observation-Hooks finalisieren.
- [ ] Produktrepo-Baseline/Git-Zustand sichern.
- [ ] V1-Plan auf `READY` setzen.

## Gate

**G-OBS-000 PASS**, wenn kein Coding-Agent mehr eine grundlegende Logging-Architekturentscheidung treffen muss.

---

# 8. OBS-010 – Canonical Model & Contracts

## Ziel

Die stabilen, UI-/Storage-/Transport-unabhängigen Kernverträge implementieren.

## Scope

- Canonical log record;
- Enums / Value Types;
- Query-Filter-Grundmodelle;
- Provider-/Store-Grundinterfaces, soweit für V1 zwingend;
- strukturierte Client-Observation-API;
- Schema-/Record-Versionierung.

## Anforderungen

CanonicalRecord muss mindestens die final freigegebenen Varianten folgender Dimensionen abbilden:

```text
record identity
source timestamp / received time
producer identity
channel
level
type
component
scope
session / generation / activation / segment / command / event correlation
message
details
raw
replay metadata
```

## Tests

- Construction/validation;
- optional/required fields;
- serialization/deserialization;
- enum forward compatibility;
- malformed payload;
- time normalization;
- correlation field preservation.

## Negativtest

Ein zukünftiger unbekannter `type` darf nicht die gesamte Pipeline brechen.

## Gate

Coremodelle funktionieren ohne Qt, SQLite und WebSocket.

---

# 9. OBS-020 – Ingress, Normalizer, Health & Redaction

## Ziel

Alle Records durch eine passive, sichere und nichtrekursive Aufnahmegrenze führen.

## Scope

- `LoggingIngress` / Fassade;
- Normalisierung;
- Redaction;
- interner Health-State;
- Python-logging Handler/Adapter;
- strukturierte ClientEvent-API.

## Wichtige Regeln

- Producer dürfen nicht auf Persistenz warten.
- Loggerinterne Fehler dürfen nicht wieder durch denselben Handler laufen.
- Secret-Redaction geschieht **vor Persistenz/Sinks**.
- Raw darf niemals ungeprüft persistiert werden.

## Security Cases

Mindestens redigieren:

- Admin-/API-Key;
- Authorization;
- Tokens;
- Passwörter;
- sensitive URL query values;
- Config dumps mit Secrets;
- optional Transkriptinhalt.

## Tests

- Python `logger.info/exception` → canonical;
- `extra` preservation;
- Redaction before enqueue/storage;
- recursive-error protection;
- malformed records;
- internal health counters.

## Gate

Logging kann aktiv oder deaktiviert werden, ohne das fachliche Clientverhalten zu verändern.

---

# 10. OBS-030 – Queue, Worker, SQLite & Retention

## Ziel

Lokale Persistenz vollständig außerhalb kritischer Runtimepfade.

## Scope

- bounded queue;
- worker lifecycle;
- batching;
- `SQLiteLogStore`;
- schema version;
- migrationsgrundlage;
- indices;
- retention;
- cleanup;
- replay dedupe;
- kontrollierter Shutdown/Flush;
- optional erster File Sink nach OBS-000-Entscheidung.

## Backpressure

Priorität:

1. Runtime nie blockieren.
2. Memory bounded.
3. hochwertige Records bevorzugen.

Explizit testen:

- Queue voll;
- DB locked;
- disk/file error;
- worker exception;
- shutdown mit Restqueue.

## SQLite

Bevorzugt:

- eigener Worker besitzt DB-Schreibzugriff;
- kurze Transaktionen / Batch writes;
- Busy-/Lock-Verhalten bewusst konfigurieren;
- Dedupe-Constraint nur auf wirklich stabile Serveridentität;
- DB außerhalb des Repositories.

## Retention

Mindestens:

- `retention_days`;
- `max_entries`.

Optional später:

- Max DB size.

## Gate

Failure-Isolation-Test: SQLite kaputt → Audio/WebSocket/Controller/Feedback unverändert funktionsfähig.

---

# 11. OBS-040 – Server Live Adapter & strukturierte Client-Hooks

## Ziel

Die Foundation mit realen Datenquellen verbinden, ohne fachliche Pfade umzubauen.

## 11.1 Server Live

Anbindung am freigegebenen passiven Fan-out-Punkt des bestehenden `/ws/logs`-Pfads.

Muss erhalten:

- origin;
- server event id;
- channel;
- event type;
- timestamps;
- session context;
- replay marker;
- raw structured payload nach Redaction.

Darf nicht:

- FeedbackController ersetzen;
- Eventstream-Lifecycle besitzen;
- Eventreplay als fachliche State-Rekonstruktion benutzen.

## 11.2 Client-Hooks – V1

Mindestens:

- Connection established/lost;
- STT reconnect attempt/result;
- Eventstream state/replay/cursor;
- trigger sent;
- trigger ack accepted/rejected/stale;
- pending commands discarded;
- Settings Apply start/result/rollback;
- Feedback decision;
- LED dispatch/failure;
- transient action blocked;
- classified server errors;
- start/ack timings;
- Audio queue overflow/packet-drop **aggregiert**.

## Hot-Path-Regel

Keine Record-per-audio-packet- oder Record-per-VAD-frame-Instrumentierung.

## Tests

- server event → local store;
- replay → no duplicate local record;
- same event still reaches feedback;
- disabling logging does not alter event dispatch;
- structured client hook carries IDs correctly.

## Gate

Ein Live-Durchlauf kann Client- und Serverrecords derselben Session gemeinsam anzeigen.

---

# 12. OBS-050 – Local Query, Minimal Log UI & Settings

## Ziel

Die Daten praktisch nutzbar machen, ohne die spätere Remote-Provider-Architektur zu verbauen.

## Query Layer

Minimal:

```text
LogQueryService
→ LocalLogProvider
```

QueryFilter:

- time range;
- producer/source;
- channel;
- level;
- type;
- component;
- session;
- activation;
- segment;
- text;
- pagination/cursor.

## UI – Minimalumfang

- LogView als eigener Bereich/Tab nach OBS-000-Entscheidung;
- QTableView/QAbstractTableModel statt QTableWidget;
- columns: time, source, channel, level, type, component, message;
- detail pane;
- structured details;
- raw JSON;
- live mode;
- history mode;
- filters;
- context actions Session/Activation/Segment.

## Settings

Nur Logging-spezifische lokale Einstellungen:

- enabled;
- local history enabled;
- level;
- retention;
- max entries;
- optional file sink;
- file format/path;
- live buffer size;
- transcript content policy;
- raw payload policy.

## Harte Grenze

LogView liest nie direkt SQLite.

SettingsView besitzt nie den Logging-Worker.

## Gate

UI kann große Historien paginiert/gefiltet lesen, ohne alles in den Speicher zu laden.

---

# 13. OBS-060 – V1 Hardening, Evidence & Observability Baseline

## Ziel

Teil A als eigenständige, belastbare Foundation abschließen.

## Testmatrix

### Unit

- canonical normalization;
- redaction;
- dedupe;
- query filter;
- retention;
- queue/drop;
- store.

### Integration

- Python logging → SQLite;
- server event → SQLite;
- structured client event → SQLite;
- replay;
- restart;
- shutdown/flush;
- settings reload.

### Failure

- SQLite read-only;
- SQLite locked;
- DB path invalid;
- file sink invalid;
- queue full;
- worker exception;
- malformed event;
- UI query failure.

### Runtime Isolation

Explizit:

```text
Logging kaputt
→ Audio funktioniert
→ /ws/transcribe funktioniert
→ /ws/logs/Feedback-Fallback bleibt fachlich korrekt
→ Controller funktioniert
→ Feedback funktioniert
```

### Performance

- Burst;
- batch throughput;
- Qt responsiveness;
- eventstream receive;
- audio hot-path overhead;
- DB cleanup.

## Evidence

Je Test:

- command;
- exit code;
- result;
- relevant counters;
- failure injection;
- git diff check.

## Baseline Checkpoint

Nach bestandenem Gate:

- separater Logging-/Observability-Commit **nur nach ausdrücklicher Freigabe**;
- Baseline-Tag/Branch nur wenn ausdrücklich gewünscht;
- `CURRENT_STATE` und Masterplan aktualisieren.

## Gate

**G-OBS-V1 PASS**

Danach darf die Triggerarchitektur-Migration beginnen.

---

# 14. TEIL B – Nach Stabilisierung der Triggerarchitektur

Der zweite Teil erweitert das System auf den endgültigen Zielzustand. Er ist bereits jetzt Bestandteil des Plans, wird aber nicht vorgezogen.

---

# 15. OBS-100 – Post-Trigger Instrumentation Completion

## Ziel

Die nach der Migration endgültigen Runtimepfade vollständig und konsistent beobachtbar machen.

## Voraussetzungen

- ActivationController-Zielmodell stabil;
- `/ws/transcribe`-Lifecycle-Contract stabil;
- Continuous Streaming stabil;
- ActivationMirror stabil;
- Hotkey-/Wake-Word-Semantik abgenommen.

## Neue/aktualisierte Hooks

- activation admitted;
- activation suppressed;
- activation phase transitions;
- primary source;
- finish/cancel/timeout;
- finalization terminal count;
- activation finalized / idle;
- ActivationMirror transitions;
- state resync/self-healing;
- wake-word pause/resume;
- continuous audio stream state;
- generation/session changes.

## Ziel

Ein kompletter Turn muss über Client und Server anhand IDs rekonstruiert werden können.

## Gate

Keine Hooks bestimmen State; sie spiegeln ausschließlich die final abgenommene Runtimearchitektur.

---

# 16. OBS-110 – Server Control, Admin Authentication & Capabilities

## Ziel

Die bestehende zweite Serververbindung als Control-/Observability-Verbindung im Desktopclient sauber abstrahieren.

## Scope

- `ServerControlConnection`;
- Admin authentication service;
- secure Admin-Key handling;
- auth state;
- capability state;
- reconnect/expiry;
- capability-driven availability;
- vorhandenen Browserclient-/Servercontract wiederverwenden statt neu erfinden.

## Auth States

Mindestens:

```text
UNAUTHENTICATED
AUTHENTICATING
AUTHENTICATED
AUTH_FAILED
EXPIRED
```

## Security

- key nicht loggen;
- key nicht in exception repr;
- key nicht in raw payload;
- keine UI-Freischaltung nur weil lokal ein Key eingetragen ist;
- Serverbestätigung/Capabilities sind maßgeblich.

## Gate

Admin-Auth kann ausfallen, ohne Session-Logging oder normalen Clientbetrieb zu beeinträchtigen.

---

# 17. OBS-120 – Remote Server History & Global Logs

## Ziel

Historische und serverweite Logs per privilegierter Server-Schnittstelle in derselben LogView sichtbar machen.

## Scope

- `ServerHistoryProvider`;
- `ServerGlobalLogProvider` oder sinnvoll konsolidiertes Provider-Modell;
- serverseitige Filter/Pagination/Cursor;
- ProviderStatus;
- auth-required handling;
- canonical normalization von Remote-Records;
- originäre Serveridentität erhalten.

## Wichtige Architekturregel

Remote-Historie muss nicht pauschal in lokale SQLite repliziert werden.

Server bleibt originäre Quelle.

## Diagnostischer Mehrwert

Lokale Beobachtung vs. Serverhistorie vergleichbar machen:

```text
server event vorhanden
local copy fehlt
→ möglicher Transport-/Clientempfangsfehler
```

## Gate

Remote-Provider und LocalProvider können dieselbe Query-UI nutzen, ohne Storage-/Transportwissen in der View.

---

# 18. OBS-130 – Serverweite Admin-Settings im Desktopclient

## Ziel

Serverweite Konfiguration getrennt von lokaler und Session-Konfiguration verwalten.

## Scope

`ServerAdminService` z. B.:

- read server config;
- update server config;
- runtime/model status;
- loaded model;
- server defaults;
- weitere bereits serverseitig unterstützte Adminwerte.

## Drei Configklassen bleiben strikt getrennt

```text
Client-local
Session-specific
Server-global/Admin
```

## UI

Adminbereiche nur bei bestätigter Capability.

## Gate

Sessionconfig und serverweite Config können nicht versehentlich dieselben Runtime-Owner verwenden.

---

# 19. OBS-140 – LED-Controller Logging Integration

## Ziel

`led_controller_respeaker-v3` als weiteren Producer integrieren.

## Vorgehen

Zuerst LED-seitigen Istzustand neu prüfen; Transport nicht vorab festlegen.

Mögliche Wege:

- Python logging adapter;
- IPC;
- Eventstream;
- WS/REST;
- anderer vorhandener Mechanismus.

## Muss erhalten

- Producer identity `led`;
- component/effect/job context;
- Fehler/Performance;
- optional Korrelation zu Session/Activation, wenn übergeben.

## Nichtziel

Keine Logging-Abhängigkeit für LED-Ausführung.

## Gate

LED Logging kann ausfallen, ohne LED Runtime oder Client Runtime zu beeinflussen.

---

# 20. OBS-150 – Erweiterte Sinks / Storage Backends

## Ziel

Optionale zusätzliche Persistenz-/Exportziele.

Mögliche Pakete:

- JSONL + Text vollständig;
- MySQL/MariaDB;
- PostgreSQL;
- Remote collector;
- zentrale Observability-Plattform.

## Regel

Neue Sinks implementieren bestehende Sink-/Store-Grenzen.

Keine Änderung am CanonicalRecord nur für einen einzelnen Backendanbieter, außer explizit versionierter Schemaentscheidung.

## Gate

Lokale SQLite bleibt unabhängig nutzbar.

---

# 21. OBS-160 – Advanced Query / UX

## Ziel

Komfort- und Analysefunktionen nach stabiler Datenbasis.

Mögliche Features:

- saved filters;
- configurable columns;
- rule-based colors;
- advanced time ranges;
- export;
- copy raw/detail;
- context navigation;
- statistics;
- charts;
- aggregation;
- multi-provider toggles.

## Nichtziel

Keine Businesslogik im UI.

---

# 22. OBS-170 – Cross-Source Correlation & Forensics

## Ziel

Aus den unterschiedlichen Quellen einen belastbaren Diagnoseworkflow machen.

## Features

- korrelierte Timeline pro Session;
- Activation drill-down;
- Segment drill-down;
- command/event relation;
- local-vs-server comparison;
- missing-event detection;
- latency breakdown;
- producer timeline;
- optional saved forensic bundle.

## Wichtig

Keine falsche globale Reihenfolge allein anhand Wall Clock behaupten.

Reihenfolge bevorzugt aus:

- sequence/cursor;
- generation;
- event IDs;
- command relationships;
- producer monotonic order;
- timestamps nur ergänzend.

## Gate

Ein manueller Fehlerfall kann aus Logs reproduzierbar über mehrere Producer analysiert werden.

---

# 23. OBS-180 – Final Hardening, Documentation & Acceptance

## Ziel

Gesamten Workstream abschließen.

## Prüfungen

- vollständige Testmatrix;
- DB migrations;
- retention;
- large-history performance;
- multi-provider behavior;
- admin auth expiry/failure;
- remote history;
- LED producer;
- secrets/redaction;
- crash/restart;
- packaging/build;
- upgrade from V1 DB;
- documentation;
- manual UX review.

## Abschlussartefakte

- Architektur;
- Contracts;
- Operations;
- Privacy;
- Troubleshooting;
- Query semantics;
- Admin features;
- migration notes;
- final traceability;
- final evidence index.

---

# 24. Cross-Cutting Teststrategie

Jedes WP besitzt eigene Tests. Zusätzlich gelten durchgängig:

## Positive Tests
Beweisen den Sollpfad.

## Negative Tests
Beweisen, dass ungültige Inputs isoliert werden.

## Mutation Tests
Bei kritischen Invarianten bewusst Schutz entfernen/umgehen und sicherstellen, dass der Test rot wird.

## Failure Injection
Persistenz-/Transport-/Worker-/Auth-Ausfälle aktiv provozieren.

## Production-Path Evidence
Keine ausschließliche Abnahme anhand unrealistischer Fakes.

---

# 25. Traceability – Kernanforderungen zu Work Packages

| Anforderung | WP |
|---|---|
| passives Logging | OBS-020, 040, 060 |
| canonical schema | OBS-010 |
| local SQLite | OBS-030 |
| replay dedupe | OBS-030, 040 |
| live server events | OBS-040 |
| local client events | OBS-040 |
| query abstraction | OBS-050 |
| minimal UI | OBS-050 |
| settings | OBS-050 |
| failure isolation | OBS-020, 030, 060 |
| privacy/redaction | OBS-020, 060 |
| post-trigger lifecycle visibility | OBS-100 |
| admin auth/capabilities | OBS-110 |
| server history/global logs | OBS-120 |
| server-global settings | OBS-130 |
| LED integration | OBS-140 |
| extended sinks | OBS-150 |
| advanced UX | OBS-160 |
| forensic correlation | OBS-170 |
| final docs/acceptance | OBS-180 |

---

# 26. Modell-/Agentenstrategie zur Kostenkontrolle

## Claude / starkes Modell bevorzugt für

- OBS-000 Plan Freeze;
- CanonicalRecord-/Contract-Review;
- sensitive concurrency/failure architecture review;
- Admin-/Capability-Contract review;
- final adversarial reviews;
- Cross-Repo integration decisions.

## DeepSeek kann den Großteil der Ausführung übernehmen

Nach eingefrorenem WP besonders geeignet für:

- Models/serialization;
- SQLite store;
- retention;
- query implementation;
- UI models/views;
- settings;
- adapters mit klarer Schnittstelle;
- tests;
- file sinks;
- bounded refactors.

## Empfohlenes Muster

```text
1. Spezifikation/Plan mit starkem Modell freigeben
2. DeepSeek implementiert genau ein WP
3. automatisierte Tests
4. starkes Modell prüft Diff nur bei architekturreichem WP
5. Gate
```

Damit wird hochwertige Modellzeit für Entscheidungen statt für mechanische Implementierung eingesetzt.

---

# 27. Git-/Commitstrategie

Empfehlung:

- jedes größere, sauber bestandene WP oder logisch zusammengehörige Paket als eigener Commit;
- keine Cross-Workstream-Mischcommits;
- Commit erst nach Gate und ausdrücklicher Freigabe;
- OBS-V1 erhält einen klaren Baseline-Checkpoint vor Triggerarchitektur-Änderungen.

Besonders wertvoll:

```text
OBS Foundation
→ eigener Commit
→ Triggerarchitektur startet danach
```

---

# 28. Umgang mit neuen Funden

```text
Fund
→ FINDINGS / Inbox
→ Blocker?
   ├─ JA → aktuelles WP
   └─ NEIN → passendes späteres WP
```

Kein spontanes Scope-Wachstum.

---

# 29. Plan-Freeze-Regel

Nach `G-OBS-000 PASS` gilt:

- Architekturentscheidungen sind eingefroren;
- Implementation darf Details nur innerhalb der festgelegten Verträge wählen;
- notwendige Contractänderung → `DECISION REQUIRED`;
- keine stille Planänderung.

---

# 30. Startreihenfolge

Sobald OBS-000 abgeschlossen ist:

```text
OBS-010
→ OBS-020
→ OBS-030
→ OBS-040
→ OBS-050
→ OBS-060
→ Observability Baseline
→ Triggerarchitektur
```

Einzelne rein interne Tests/Modelle können innerhalb eines WPs parallelisiert werden, aber die Gates bleiben sequenziell.

---

# 31. Aktueller Vorbehalt

Die zuletzt von Claude erzeugten **Logging-spezifischen Code-Audits und der adversariale Review** sind in dieser Chat-Arbeitskopie noch nicht als Dateien verfügbar.

Deshalb ist dieser Gesamtplan bereits vollständig strukturiert, aber **noch nicht `FROZEN`**.

Nach Übernahme dieser Resultate muss ausschließlich OBS-000 ausgeführt werden:

- Befunde integrieren;
- konkrete Dateipfade/Interfaces korrigieren;
- offene Entscheidungen schließen;
- Work-Package-Scope präzisieren.

Danach ist keine weitere breite Logging-Untersuchung vorgesehen.

---

# 32. Definition des Gesamtabschlusses

Der Logging-/Observability-Workstream ist abgeschlossen, wenn:

- alle vorgesehenen Producer sauber angebunden sind;
- lokale und Remote-Historie über gemeinsame Query-Verträge nutzbar sind;
- Adminfunktionen capability-basiert funktionieren;
- lokale, Session- und Serverconfig sauber getrennt sind;
- Logging keine Runtime-Autorität besitzt;
- Failure Isolation nachgewiesen ist;
- Secrets zuverlässig redigiert werden;
- Cross-Source-Forensik möglich ist;
- Build/Upgrade/Retention/Performance abgenommen sind;
- Dokumentation und Traceability vollständig sind.
