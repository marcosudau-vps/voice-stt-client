---
id: OBS-MASTER
status: FROZEN_BASELINE
authority: planning
workstream: OBS
freeze_gate: OBS-000
freeze_run: RUN-OBS-000-01_2026-08-15_CLAUDE
last_updated: 2026-08-15
---

# Gesamtimplementierungsplan – Logging / Observability

> **Stand nach OBS-000 (2026-08-15).** Das Freeze-Gate ist mit `PASS`
> abgeschlossen. Die **normative** Grundlage sind ab jetzt die drei Dateien
> unter `00_NORMATIV/`:
>
> - `LOGGING_ARCHITEKTUR_FREEZE_V1.md`
> - `LOGGING_CONTRACTS_FREEZE_V1.md`
> - `LOGGING_DECISIONS_FREEZE_V1.md`
>
> Dieser Plan bleibt der **Ausführungsfahrplan** und ist mit dem Freeze
> abgeglichen. Bei einem Widerspruch zwischen diesem Plan und den drei
> normativen Dateien gewinnen die normativen Dateien.

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

## 1.1 Autoritätsreihenfolge nach OBS-000

```text
1. 00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md
   00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md
   00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md
2. dieser Plan und das aktive Work Package
3. realer Produktcode fuer Ist-Aussagen
4. 10_ANALYSE/CLAUDE_VORARBEIT/*   (Herleitung; das adversariale Review
                                    korrigiert die uebrigen Vorarbeitsdateien)
5. 00_GRUNDLAGEN/*                 (Entwuerfe; Herleitung)
6. 05_DRAFTS_UNGEPRUEFT/*          (niemals normativ)
```

Die Entwürfe unter `00_GRUNDLAGEN/` bleiben als Herleitung erhalten und werden
**nicht** gelöscht. Wo der Freeze bewusst von ihnen abweicht, ist das im
Widerspruchsregister (`LOGGING_DECISIONS_FREEZE_V1.md §7`) einzeln benannt.

## 1.2 Plan-Freeze-Regel

**OBS-000 war ein verpflichtendes Freeze-Gate und ist mit `PASS` bestanden.**

Ab jetzt gilt:

- Architekturentscheidungen sind eingefroren.
- Eine Implementierung darf Details nur **innerhalb** der festgelegten Verträge
  wählen.
- Wird eine Vertragsänderung nötig: `DECISION REQUIRED` — anhalten, im Run
  Report begründen, in `LOGGING_DECISIONS_FREEZE_V1.md` nachtragen.
- **Keine stille Planänderung.**

Kein Coding-Agent darf offene Architekturfragen selbst stillschweigend
entscheiden. Nach dem Freeze gibt es keine mehr; wo dennoch eine auftaucht, ist
sie ein `DECISION REQUIRED`, kein Ermessensspielraum.

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

## O-14 – Schreibmonopol *(neu in OBS-000)*

Es gibt genau **einen** Schreibpfad in den lokalen Store: `Ingress → Worker → Store`.
Der Query-Layer ist ausschließlich lesend; **kein** LogProvider schreibt jemals,
auch ein Remote-Provider nicht.

Begründung: Dasselbe Serverereignis darf gleichzeitig als lokal gespeicherte
Kopie **und** als remote abgefragtes Ergebnis existieren. Genau dieser
Unterschied ist der Diagnosewert („Serverhistorie hat es, lokale Historie
nicht"). Würde ein Provider schreiben, ginge er verloren.

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
| 0 | OBS-000 | Plan Freeze & Baseline — **DONE, PASS** | abgeschlossen 2026-08-15 | eingefrorene Verträge |
| 1 | OBS-010 | Canonical Model, Redaction, Normalizer & Contracts | vor Trigger-Migration | stabiles Datenmodell |
| 2 | OBS-020 | Ingress, Backpressure, Health & Python-Logging-Handler | vor Trigger-Migration | sichere passive Aufnahme |
| 3 | OBS-030 | Worker, SQLite-Store, Retention & JSONL-Sink | vor Trigger-Migration | lokale Persistenz |
| 4 | OBS-040 | Live Adapter & Client Observation Hooks | vor Trigger-Migration | reale Live-Daten |
| 5 | OBS-050 | Local Query, Log View & Settings | vor Trigger-Migration | nutzbare Diagnoseansicht |
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

# 7. OBS-000 – Plan Freeze & Baseline — **ABGESCHLOSSEN**

```text
Status  DONE
Gate    G-OBS-000 PASS
Run     RUN-OBS-000-01_2026-08-15_CLAUDE
Datum   2026-08-15
```

## Ziel (erreicht)

Alle bereits erzeugten Logging-Audits und das adversariale Review gegen Zielbild und V1-Abgrenzung führen und die noch offenen Architekturentscheidungen schließen.

## Aufgaben

- [x] `LOGGING_CODE_INTEGRATION_AUDIT.md` übernommen.
- [x] `LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md` übernommen.
- [x] `LOGGING_CONCURRENCY_FAILURE_MODEL.md` übernommen.
- [x] `LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md` übernommen.
- [x] `LOGGING_V1_IMPLEMENTATION_PLAN.md` übernommen.
- [x] `LOGGING_OPEN_DECISIONS.md` übernommen.
- [x] `LOGGING_TEST_MATRIX.md` übernommen.
- [x] `LOGGING_ADVERSARIAL_REVIEW.md` übernommen.
- [x] Widersprüche protokolliert — 19 Stück, alle aufgelöst (`DECISIONS §7`).
- [x] echte Codefakten von Architekturvorschlägen getrennt (`EV-02`).
- [x] CanonicalRecord finalisiert (`CONTRACTS §1`).
- [x] Client-Channels finalisiert (`CONTRACTS §2.2`).
- [x] Dedupe-Key finalisiert (`CONTRACTS §5.5`).
- [x] Queue-/Backpressure-Policy finalisiert (`ARCH §7`).
- [x] SQLite-Grundschema finalisiert (`CONTRACTS §5.2`).
- [x] Privacy-/Raw-Defaults finalisiert (`DECISIONS §3`).
- [x] V1 File-Sink-Scope finalisiert — nur JSONL (`FD-D4`).
- [x] konkrete Eventstream-Fan-out-Stelle finalisiert (`CONTRACTS §7`).
- [x] UI-Platzierung finalisiert (`CONTRACTS §9`).
- [x] exakte V1-Observation-Hooks finalisiert (`CONTRACTS §12`).
- [x] Produktrepo-Baseline/Git-Zustand gesichert (`EV-03`).
- [x] V1-Plan auf `READY` gesetzt — OBS-010 und OBS-020 sind
      implementation-ready.

## Gate

**G-OBS-000 PASS** — kein Coding-Agent muss mehr eine grundlegende
Logging-Architekturentscheidung treffen.

## Offene Vorbedingung für OBS-010 (kein Blocker dieses Gates)

Der Arbeitsbaum von `voice-stt-client` trägt 22 nicht committete Änderungen,
darunter alle Dateien, auf deren Zeilennummern die Analysen verweisen. Vor
Beginn von OBS-010 ist dieser Zustand festzuschreiben — durch einen Commit oder
durch die ausdrückliche Bestätigung, dass der Baum unverändert bleibt. Details
in `40_EVIDENCE/OBS-000/EV-03_PRODUKT_BASELINE_GIT.md`.

---

# 8. OBS-010 – Canonical Model, Redaction, Normalizer & Contracts

## Ziel

Die stabilen, UI-/Storage-/Transport-unabhängigen Kernverträge implementieren.

## Scope

- Canonical log record;
- Enums / Value Types;
- **Redaction** (`redaction.py`) inklusive `unfreeze()`;
- **Normalizer** mit drei Eingängen;
- Query-Filter-Grundmodelle;
- Provider-/Store-/Sink-Protokolle, soweit für V1 zwingend;
- strukturierte Client-Observation-API (Signatur);
- Schema-/Record-Versionierung.

> **Grenzkorrektur aus OBS-000.** Redaction und Normalizer liegen hier, nicht in
> OBS-020: Der Normalizer ruft `redact` am Ende **jedes** Pfades, beide sind
> untrennbar, und beide sind reine, I/O-freie Logik, die das Gate dieses Pakets
> („funktioniert ohne Qt, SQLite und WebSocket") erfüllt. Begründung in
> `LOGGING_DECISIONS_FREEZE_V1.md §8.2`.

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

# 9. OBS-020 – Ingress, Backpressure, Health & Python-Logging-Handler

## Ziel

Alle Records durch eine passive, sichere und nichtrekursive Aufnahmegrenze führen.

## Scope

- `ObservabilityIngress` / `NullIngress` / `NULL_INGRESS`;
- **eine** bounded Queue plus Wasserstandsregel bei 75 %;
- Prioritätsableitung nach `CONTRACTS §1.5`;
- interner Health-State inkl. Emergency-stderr;
- `UnifiedLogHandler` (Python-logging-Adapter) und seine Registrierung.

> **Grenzkorrektur aus OBS-000.** Normalizer und Redaction liegen in OBS-010.
> Der Titel „Ingress, Health & Redaction" war insofern irreführend.

## Wichtige Regeln

- Producer dürfen nicht auf Persistenz warten; ausschließlich `put_nowait`.
- Loggerinterne Fehler dürfen nicht wieder durch denselben Handler laufen
  (G-1 bis G-4 in `ARCH §8.1`).
- `flush()` und `close()` des Handlers sind **No-Ops** (G-7) — sonst Deadlock
  über `atexit`.
- Secret-Redaction geschieht **vor Persistenz/Sinks**; für clienterzeugte
  Records im Producer-Thread, für Server-`raw` im Worker (`ARCH §8.2`).
- Raw darf niemals ungeprüft persistiert werden.

## Gate-Hinweis

Der Ende-zu-Ende-Nachweis `logger.info → SQLite` gehört zum Gate von
**OBS-030**, nicht hierher: In OBS-020 existiert der Store noch nicht. OBS-020
wird gegen einen aufzeichnenden Fake-Store abgenommen. Begründung in
`LOGGING_DECISIONS_FREEZE_V1.md §8.3`.

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

# 10. OBS-030 – Worker, SQLite-Store, Retention & JSONL-Sink

## Ziel

Lokale Persistenz vollständig außerhalb kritischer Runtimepfade.

## Scope

- `LoggingWorker` (Thread), Batching, Flush;
- `ObservabilityManager` als Kompositionswurzel, Lebensdauer in `app.py::main()`;
- `SQLiteLogStore`, Schema, Migration, Indizes;
- Retention und Cleanup;
- Replay-Dedupe über den partiellen UNIQUE-Index;
- kontrollierter Shutdown/Flush;
- `JsonlSink` (nur JSONL, `FD-D4`).

> **Grenzkorrektur aus OBS-000.** Die Queue liegt im Ingress und damit in
> OBS-020. Der bisherige Titel „Queue, Worker, SQLite & Retention" hätte dazu
> verleitet, sie zweimal zu bauen.

## Backpressure

Die Policy ist in OBS-020 umgesetzt. Hier gilt nur die Priorität, gegen die
getestet wird:

1. Runtime nie blockieren.
2. Memory bounded.
3. hochwertige Records bevorzugen.

Explizit testen: Queue voll · DB locked · disk/file error · worker exception ·
shutdown mit Restqueue.

## SQLite – verbindliche Korrekturen aus OBS-000

- Der Worker besitzt genau **eine** Verbindung, und sie wird **im
  Worker-Thread** erzeugt, nicht in `start()` (sonst
  `sqlite3.ProgrammingError` beim ersten Batch).
- Leser öffnen **kein** `mode=ro` — auf einer WAL-Datenbank ist das nicht
  allgemein möglich. Stattdessen `PRAGMA query_only = ON`.
- **Kein** `auto_vacuum`, **kein** `incremental_vacuum`, **kein** `VACUUM`.
- `write_batch` liefert `(eingefügt, dedupliziert)`.
- WAL, `synchronous=NORMAL`, `busy_timeout=5000`.
- Dedupe-Constraint ausschließlich auf `(producer_id, event_id)`, partiell.
- DB außerhalb des Repositories, im Benutzerprofil (P-8/P-9).

Vollständiges DDL: `LOGGING_CONTRACTS_FREEZE_V1.md §5.2`.

## Retention

- `retention_days` **und** `max_entries` wirken beide; die erste greifende
  Grenze gewinnt.
- **Beide** löschen blockweise (`LIMIT 5000`), die Anzahlgrenze zusätzlich
  gegen NULL gesichert.
- `max_db_bytes` ist ein **reines Warnsignal** — kein automatisches Absenken
  von `max_entries`.
- Bei `disk full` wird die Retention **ausgesetzt**.

## Gate

Failure-Isolation-Test: SQLite kaputt → Audio/WebSocket/Controller/Feedback unverändert funktionsfähig.

---

# 11. OBS-040 – Server Live Adapter & strukturierte Client-Hooks

## Ziel

Die Foundation mit realen Datenquellen verbinden, ohne fachliche Pfade umzubauen.

## 11.1 Server Live

Anbindung am freigegebenen passiven Fan-out-Punkt des bestehenden `/ws/logs`-Pfads:
`DualSessionCoordinator._handle_event` und `_handle_control`, jeweils als
**erste** Anweisung, rückgabewertfrei, in `try/except Exception`
(`CONTRACTS §7`).

Zusätzlich ein **zweiter, sehr kleiner** Beobachtungspunkt im `except`-Zweig von
`EventStreamTransport.run()` für Protokollfehler (`client.eventstream.protocol_error`,
ohne Rohframe) — sonst bliebe der interessanteste Diagnosefall unstrukturiert
(`FD-R3`).

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
- replay → **kein** zweiter Datensatz; `deduplicated` steigt
  *(korrigierte Erwartung — der Index unterdrückt die Zeile, es entsteht
  **kein** Record mit `replayed=True`)*;
- same event still reaches feedback;
- disabling logging does not alter event dispatch;
- structured client hook carries IDs correctly;
- ein **werfender** Beobachter verändert weder den Rückgabewert von
  `_handle_event` noch den Cursorstand — nachzuweisen über den **echten**
  `EventProtocolProcessor` mit **echtem** `EventCursorStore` auf einer
  temporären Datei, **nicht** über ein Double.

## Gate

Ein Live-Durchlauf kann Client- und Serverrecords derselben Session gemeinsam anzeigen.

`git diff` zeigt in `session_coordinator.py` **keine** Änderung an einer
bestehenden Zeile außer den zwei eingefügten Aufrufen.

---

# 12. OBS-050 – Local Query, Log View & Settings

> **Abhängigkeitskorrektur aus OBS-000.** OBS-050 hängt an OBS-030 und ist von
> OBS-040 **unabhängig**. Nach dem Wegfall des Ringbuffers (`FD-S1`) benutzt der
> Live-Modus dieselbe Provider-Schnittstelle wie die Historie; die UI hängt damit
> nur noch am Query-Layer und kann **parallel** zu OBS-040 gebaut werden.

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

- **eigenes, nicht-modales `LogWindow`** (Tray-Menü und Knopf im Logging-Tab);
- QTableView/QAbstractTableModel statt QTableWidget;
- **sieben** Spalten: time, source, channel, level, type, component, message;
- detail pane;
- structured details;
- raw JSON, **bei Auswahl nachgeladen**;
- **Live-Modus als tailende Store-Abfrage** (`QTimer` 250 ms,
  `WHERE id > :last ORDER BY id LIMIT 500`) — **kein Ringbuffer**, kein Signal
  je Record;
- history mode; kein Mischbetrieb in V1;
- filters;
- context actions Session/Activation/Segment — der Activation-Filter trägt
  einen Hinweis auf die Unzuverlässigkeit des Wertes (`FD-C2`).

## Settings

Sechster Tab „Logging & Diagnose"; nur Logging-spezifische lokale Einstellungen:

- enabled;
- level;
- store enabled;
- retention days;
- max entries;
- file sink enabled;
- file sink dir;
- transcript content policy;
- raw payload policy;
- Schaltfläche „Diagnosehistorie löschen" (`FD-S4`);
- Schaltfläche „Logs anzeigen".

Entfallen gegenüber dem Entwurf: `live buffer size` (kein Ringbuffer),
`file format` (nur JSONL).

Nur in `config.yaml`: `db_path`, `queue_size`, `batch_size`,
`flush_interval_s`, `max_db_bytes`.

## Harte Grenze

LogView liest nie direkt SQLite. SettingsView besitzt nie den Logging-Worker.
Der Query-Layer läuft **nicht** über `CoreBridge` — dort liegen Audio und
WebSocket.

Eine reine Observability-Änderung löst **keinen** Reconnect und **keinen**
Audio-Neustart aus.

## Gate

UI kann große Historien paginiert/gefiltert lesen, ohne alles in den Speicher zu laden.

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

### Mutation Checks *(neu aus OBS-000)*

Das Projekt hat diese Praxis bereits etabliert. Jede dieser Mutationen **muss**
einen Test rot werden lassen:

| Mutation | erwartet rot |
|---|---|
| `ON CONFLICT DO NOTHING` → einfaches `INSERT` | Dedupe-Tests, manuelle Abnahme |
| `except Exception` im Beobachterwrapper entfernen | Fan-out-Isolationstest |
| `put_nowait` → blockierendes `put` | Backpressure-Test |
| Wasserstandsregel entfernen | Backpressure-Test |
| Redaction-Aufruf im Normalizer entfernen | Redaction-Tests |
| `WHERE event_id IS NOT NULL` aus dem Index entfernen | Clientrecords würden fälschlich dedupliziert |
| Handlerlevel auf DEBUG setzen | Nachweis, dass Realtime-Text nicht gespeichert wird |
| `PRAGMA query_only = ON` entfernen | Nachweis, dass der Leser nicht schreiben kann |

### Dateirechte *(neu aus OBS-000)*

Nach dem ersten Start werden die effektiven Rechte von Store und Sink einmalig
protokolliert (`icacls`), als Abnahmebeleg (P-8/P-9, Test M-11).

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

Remote-Historie **darf nicht** in die lokale SQLite repliziert werden (O-14).
Der Server bleibt originäre Quelle, und dasselbe Ereignis darf in beiden
Historien mit derselben `event_id` erscheinen — genau das ist der Diagnosewert.

## Auflagen aus OBS-000

- **`ProviderCapabilities` wird hier eingeführt**, nicht in V1 (`FD-S3`).
- **`SessionHistoryProvider` zuerst**, nicht der Admin-Provider (`FD-B2`): Er
  braucht keinen Admin-Key, nur den vorhandenen Session-Token und
  `hello.logAccess.historyPath`, das der Client heute verwirft.
- **HTTP-Fähigkeit klären** (`FD-B3`): Der Client hat heute **keinen**
  HTTP-Client. Abhängigkeits- und Buildentscheidung gehören in dieses Paket.
- `QueryFilter.scopes = ("global",)` **bedeutet** die Adminabfrage;
  `session_id=None` bleibt „ohne Einschränkung".

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

`G-OBS-000 PASS` ist am 2026-08-15 erreicht. Damit gilt:

- Architekturentscheidungen sind eingefroren;
- Implementation darf Details nur innerhalb der festgelegten Verträge wählen;
- notwendige Contractänderung → `DECISION REQUIRED`, im Run Report begründet
  und in `LOGGING_DECISIONS_FREEZE_V1.md` nachgetragen;
- keine stille Planänderung.

---

# 30. Startreihenfolge

```text
OBS-010
→ OBS-020
→ OBS-030
→ OBS-040 ─┐
           ├→ OBS-060 → Observability Baseline → Triggerarchitektur
→ OBS-050 ─┘
```

OBS-040 und OBS-050 hängen beide an OBS-030 und sind **voneinander unabhängig**
(`FD-S1`). Einzelne rein interne Tests und Modelle können innerhalb eines
Pakets parallelisiert werden; die Gates bleiben sequenziell.

**Vorbedingung für OBS-010:** Der Arbeitsbaum von `voice-stt-client` ist
festzuschreiben (`40_EVIDENCE/OBS-000/EV-03_PRODUKT_BASELINE_GIT.md`).

---

# 31. Stand der Vorarbeit

Die Logging-spezifischen Code-Audits, die Testmatrix und das adversariale Review
liegen vollständig unter `10_ANALYSE/CLAUDE_VORARBEIT/` und sind in OBS-000
eingearbeitet worden:

- Befunde integriert;
- Dateipfade und Schnittstellen präzisiert;
- alle Entscheidungen geschlossen (`LOGGING_DECISIONS_FREEZE_V1.md`);
- Work-Package-Scope und -Grenzen korrigiert (dort §8);
- 19 Widersprüche aufgelöst, keiner offen;
- die letzte Informationslücke (`IMPLEMENTATION_ROADMAP.md`) geprüft und
  geschlossen (`40_EVIDENCE/OBS-000/EV-02`, C-13).

**Es ist keine weitere breite Logging-Untersuchung vorgesehen.** Gezielte
Codeprüfungen innerhalb eines Pakets bleiben erlaubt.

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
