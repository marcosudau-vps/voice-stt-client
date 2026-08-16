# Logging-Vorbereitung – Analyseordner und Abschlussbewertung

**Auftrag:** `ARBEITSDATEIEN/Implementierungsdateien/prompts/006_Vorbereitung_Logging.md`
**Datum:** 2026-08-15
**Umfang:** Code-Audit und implementation-ready Architekturplan. **Keine
Implementierung.**

---

# Einhaltung der harten Arbeitsregeln

| Regel | Status |
|---|---|
| keine Produktcodeänderungen | eingehalten |
| keine Testcodeänderungen | eingehalten |
| keine Configänderungen | eingehalten |
| keine Änderungen an aktiver Produktdokumentation | eingehalten |
| kein Commit / Push / Merge / Rebase / Tag / PR | eingehalten |
| Analyse-/Planungsartefakte im Arbeitsbereich | erstellt unter `ARBEITSDATEIEN/AP_THEMA_LOGGING/analyse_code_integration/` |
| keine Triggerarchitektur repariert | eingehalten; Auffälligkeiten nur dokumentiert |

Es wurde ausschließlich gelesen. Es wurde keine Datenbank angelegt, kein Schema
ausgeführt und kein Test gestartet, der Produktdateien verändert hätte.

---

# Artefakte

| Datei | Inhalt | Auftragsabschnitte |
|---|---|---|
| `LOGGING_CODE_INTEGRATION_AUDIT.md` | Inventar des Client-Loggings; vollständige Analyse des `/ws/logs`-Pfads; **empfohlener Server-Live-Hook**; Fan-out-Möglichkeiten; präzisierte Client-Hooks mit HOT-PATH-Markierung; Channel-Verifikation; Privacy-Audit; LED-Kurzaudit | 1, 2, 3, 4, 6, 12, 17 |
| `LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md` | Canonical Record Feld für Feld am Code; Zusatzfragen; Replay-/Dedupe-Klärung; Bewertung der bestehenden Persistenzmuster; implementation-ready SQLite-Schema, Migration, Retention, Pagination | 5, 7, 8, 9 |
| `LOGGING_CONCURRENCY_FAILURE_MODEL.md` | reale Threads und Queues; Queue-/Worker-/Backpressure-Entwurf; logging-interne Failure Domain mit Rekursionsschutz und Health-Modell | 10, 11 |
| `LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md` | Settings-Architektur und Einbau; LogView gegen die reale PySide-Architektur; Query-Provider-Schnittstelle; Admin-/Server-Control-Grenze | 13, 14, 15, 16 |
| `LOGGING_V1_IMPLEMENTATION_PLAN.md` | Modulstruktur gegen den echten Baum; 14 Arbeitspakete OBS-00…OBS-13 mit Scope, Non-Scope, Dateien, Sollzustand, Schritten, Tests, Negativtests, Failure-Tests, Akzeptanzkriterien, Evidence | 18, 19, 24 |
| `LOGGING_OPEN_DECISIONS.md` | 13 echte Entscheidungen mit Optionen, Bewertung, Empfehlung und Blockadeangabe; dazu die Liste der bereits am Code entschiedenen Entwurfsfragen | 23 |
| `LOGGING_TEST_MATRIX.md` | Unit-, Integrations-, Failure-, Runtime-Isolations- und Performance-Tests; Regeln, wo ein Testdouble erlaubt ist; verbindliche manuelle Abnahme | 20 |

---

# Die fünf wichtigsten Einzelbefunde

1. **Der naheliegende Hook ist der falsche.**
   `STTController.on_event_stream_event` ist vorhanden und unbenutzt — aber sein
   Rückgabewert entscheidet über den Cursor-Commit und das Recycling der
   `/ws/logs`-Verbindung (`core/event_stream.py:270-286`). Ein Logger dort wäre
   fachliche Runtime-Autorität. Der richtige Punkt ist ein neuer, additiver
   Beobachterschlitz in `DualSessionCoordinator._handle_event` und
   `_handle_control`.

2. **Dedupe ist Pflicht, nicht Kür.**
   `server_instance_id` wird bei jedem Serverneustart neu erzeugt
   (`event_logging.py:700`), der Client verwirft daraufhin seinen Cursor
   (`event_cursor_store.py:72-79`) und der Server replayt die **gesamte**
   verbliebene Historie. Die vorhandene In-Memory-Dedupe von 2048 Einträgen
   fängt das nicht ab. Schlüssel: `(producer_id, event_id)` als partieller
   UNIQUE-Index.

3. **Der `hello`-Payload enthält ein Geheimnis und wird bereits heute
   herumgereicht.** `logAccess.accessToken` läuft durch
   `STTSession._fire_event_callback` und `STTController.handle_server_event`.
   Deshalb: Whitelist statt Blacklist für `hello`, Redaction im Producer-Thread
   vor der Queue.

4. **Transkripttext steht heute schon im Klartext in der `client.log`** —
   auf INFO (`stt_session.py:1296-1300`) und bei Konflikten sogar vollständig
   auf WARNING (`controller.py:2077-2080`). `store_transcription_content` muss
   deshalb auch die **unstrukturierten** Logzeilen erfassen, nicht nur
   Serverevents.

5. **Der LED-Controller braucht keinen Adapter.**
   LEFX läuft im selben Prozess und loggt nach `lefx.*`; die Records erreichen
   den Root-Logger ohnehin. Eine Normalizer-Regel
   (`logger.startswith("lefx.")` → `producer_kind=led`) genügt und beweist die
   Erweiterbarkeit ohne Kernumbau.

---

# 25. Abschlussbewertung

## A. Ist die vorgeschlagene Logging-Zielarchitektur mit dem heutigen Client vereinbar?

**Ja, ohne Einschränkung.** Der Client erfüllt bereits alle Voraussetzungen, die
das Zielbild verlangt:

- Der Core ist frei von Qt (`core/*` importiert nirgends `PySide6`), sodass die
  Invariante „Qt-Grenze" (Zielbild §38) ohne Umbau haltbar ist.
- Der Feedbackpfad ist bereits von der Serververbindung entkoppelt: es gibt
  einen vollständigen STT-Fallback über `/ws/transcribe`
  (`controller.py:1694-1708`), sodass Logging nachweislich keine Voraussetzung
  für Feedback wird.
- Das Haus hat bereits ein durchgängiges Muster „bounded Queue + verwerfen +
  zählen" (Audio, LED) und ein Muster „Teilsystem deaktiviert sich statt zu
  stoppen" (`history.py:174-178`). Die Logging-Failure-Domain fügt sich ein und
  erfindet nichts Neues.
- Es gibt genau **eine** Stelle, an der die Zielarchitektur einen echten
  Konflikt mit dem Code hätte — den Rückgabewert-gesteuerten Eventpfad — und
  dieser Konflikt ist durch die Hookwahl vollständig vermieden.

Zwei Korrekturen am Entwurf sind nötig, beide klein:
Channels **klein** schreiben (Befund C-1) und `transcription_id` als eigenes
Feld führen (OD-02).

## B. Welche Teile können direkt wiederverwendet werden?

| Vorhanden | Wiederverwendung |
|---|---|
| `logging_setup.setup_logging` | bleibt vollständig; ein dritter Handler wird additiv ergänzt |
| Der `extra`-Vertrag aus `JsonFormatter` (`session_id`, `segment_id`, `event_type`, `detail`) | wird als bestehender Vertrag übernommen und erweitert |
| `EventEnvelope` / `EventProtocolResult` / `EventProtocolProcessor` | liefern Envelope, Rohpayload, Cursor, Replayflag und Dedupe unverändert — **keine** Änderung nötig |
| `EventCursorStore` | Muster für atomares Schreiben, `schema_version`, strikte Validierung, Verwerfen statt Reparieren |
| `TranscriptHistoryManager` | Muster für `ON CONFLICT DO NOTHING`, `_db_session`, „Init-Fehler deaktiviert die Persistenz" |
| `LedFeedback` | Muster für bounded Queue, Coalescing, „einmal melden", Dauer als abfragbare Zahl, daemon-Thread mit Timeout-Join |
| `CoreBridge` | Muster für den Thread→Qt-Übergang mit `QueuedConnection` |
| `settings_metadata` + `SettingsDialog` | ein neuer Tab kostet nur Metadaten, keinen Dialogcode |
| `apply_runtime_config` + Rollback | nimmt eine zusätzliche Zeile auf |
| `SETTING_DEFINITION.sensitive` | vorgesehener, bisher ungenutzter Platz für einen späteren Admin-Key |
| `sessionCapabilities` | Vorbild für ein Capability-Muster, das der Client bereits versteht |
| `hello.logAccess.historyPath` | vom Server geliefert, vom Client heute verworfen — der billigste Weg zum zweiten Provider |
| Testkonventionen (`unittest`, `ScriptedLogSocket`, offscreen-Qt) | direkt übertragbar |

## C. Welche Teile brauchen neue Infrastruktur?

| Neu | Umfang | Warum es nichts Vorhandenes gibt |
|---|---|---|
| `ObservabilityIngress` mit zwei bounded Queues und Ringbuffer | ein Modul | Es existiert kein Eventbus und kein Mehrfachverteiler im Core (Audit §3.1) |
| Fan-out-Schlitz im `DualSessionCoordinator` | ~14 Zeilen, additiv | Alle Callback-Slots sind einslotig und belegt |
| `LoggingWorker` als eigener Thread | ein Modul | Der asyncio-Loop existiert phasenweise gar nicht (Befund N-2) |
| `SQLiteLogStore` | ein Modul | Der bestehende Historienstore hat keine Schemaversion, kein WAL, keine Batches und ruft Cleanup nach jedem Insert |
| `LoggingInternalHealth` + Emergency-stderr | ein Modul | Kein vorhandener Mechanismus ist rekursionssicher |
| `QAbstractTableModel` + `QTableView` | erstmalig im Repository | Es gibt bis heute **kein** Model/View-Paar; nur `QTableWidget` |
| Query-Layer mit Provider-Schnittstelle | drei Module | Es gibt keine Abfrageschicht |
| Redaction | ein Modul | Es gibt keine |
| Strukturierte Clientevents | ein Adapter plus ~25 Aufrufstellen | Der einzige heutige strukturierte Logaufruf ist `_log_feedback_decision` |

## D. Gibt es technische Blocker für Logging V1?

**Nein. Kein einziger technischer Blocker.**

Geprüft und ausgeschlossen:

| Vermuteter Blocker | Ergebnis |
|---|---|
| Logging müsste den Eventpfad umbauen | nein — ein additiver Beobachterschlitz genügt |
| Logging bräuchte einen Eventbus | nein — ein injizierter Ingress genügt |
| Kein stabiler Dedupe-Schlüssel vorhanden | nein — `event_id` ist uuid4 und serverseitig UNIQUE |
| Die Server-Channels wären ungeeignet | nein — sie sind vollständig wiederverwendbar |
| Der Rohpayload wäre nicht verfügbar | nein — `EventProtocolResult.payload` trägt das vollständige Frame |
| Der SettingsDialog müsste umgebaut werden | nein — er ist metadatengetrieben |
| PyInstaller bräuchte neue `hiddenimports` | nein, solange statisch importiert wird (Befund M-4) |
| Der LED-Controller müsste geändert werden | nein — er läuft in-process und loggt bereits |
| Logging bräuchte eine HTTP-Schicht | nein — V1 ist rein lokal |
| Die Triggerarchitektur müsste vorher fertig sein | nein — V1 beobachtet nur und ist ausdrücklich vorgezogen |

Zwei **Risiken** (keine Blocker), die im Plan adressiert sind:

- **R-a** Der vollständige Replay nach Serverneustart erzeugt sehr viele
  Records auf einmal. Abgefangen durch Dedupe im Index, Batchschreiben und die
  Priorisierung.
- **R-b** Die Client-Suite ist umfangreich und eng verdrahtet. Jedes Paket muss
  sie unverändert grün lassen; muss ein bestehender Test geändert werden, ist
  das ein Signal für eine ungewollte Verhaltensänderung. Als verbindliche Regel
  im Plan festgehalten.

## E. Welche Entscheidungen müssen Marco/Architekturreview noch treffen?

**Blockierend für V1 (zwei):**

| ID | Frage | Empfehlung |
|---|---|---|
| **OD-01** | Paketname `observability` oder `logging` | `core/observability/`, Konfig unter `logging.observability` |
| **OD-02** | `transcription_id` als eigene Spalte | ja |

**Nicht blockierend, aber vor dem jeweiligen Paket zu klären (elf):**

| ID | Frage | Empfehlung | spätestens vor |
|---|---|---|---|
| OD-03 | Default `store_transcription_content` | `false` | OBS-00 |
| OD-04 | Default `store_raw_payload` | `true`, außer Channel `performance` | OBS-01 |
| OD-05 | Retention-Defaults | 14 Tage / 200.000 / 256 MiB | OBS-04 |
| OD-06 | Datei-Sinks in V1 | nur JSONL | OBS-12 |
| OD-07 | Umfang des `hello`-Records | Whitelist | OBS-08 |
| OD-08 | `activation_id` befüllen | ja, als diagnostisch gekennzeichnet | OBS-01 |
| OD-09 | Capability-Modell für Admin | jetzt offen lassen | V2 |
| OD-10 | zweiter Provider: Session-Historie oder Admin | Session-Historie zuerst | V2 |
| OD-11 | doppeltes Datenverzeichnis | unangetastet lassen | OBS-04 |
| OD-12 | Verhalten bei logging-internem Fatalfehler | still, nur Health und Statuszeile | OBS-02 |
| OD-13 | `client.log` neben dem Store | beides bleibt in V1 | OBS-06 |

## F. Ist V1 danach READY FOR WORK-PACKAGE FREEZE?

```text
KLASSIFIKATION:  DECISIONS REQUIRED
```

**Begründung.** Die Architektur ist am Code vollständig verifiziert, der
Integrationspunkt ist eindeutig bestimmt und begründet, das Schema ist
implementation-ready, das Concurrency- und Failure-Modell ist gegen die realen
Threads geplant, und die Arbeitspakete sind so beschrieben, dass ein späterer
Coding-Agent die Architektur nicht erneut erfinden muss.

Es fehlt **keine** Information mehr. Es fehlen genau **zwei Entscheidungen**,
die keine Untersuchung erfordern, sondern eine Festlegung:

```text
OD-01  Paketname (betrifft jeden Dateipfad und jeden Import)
OD-02  transcription_id als eigene Spalte (betrifft Schema und Migration)
```

Sobald diese beiden entschieden sind — und die elf nicht blockierenden
Entscheidungen jeweils vor ihrem Paket bestätigt werden — gilt:

```text
READY FOR FREEZE
```

**Ausdrücklich nicht erforderlich:** eine weitere Codeuntersuchung. Es ist keine
Frage offen geblieben, die nur durch Lesen weiteren Codes beantwortbar wäre.

---

# Abschließender Vorbehalt zur Fertigstellung

Der Plan sieht in OBS-13 eine **verbindliche manuelle Abnahme am realen
Produktionspfad** vor (`LOGGING_TEST_MATRIX.md`, Gruppe M). Solange dieses
Protokoll nicht vorliegt, ist der Status von V1 „offen" oder „teilweise" — auch
dann, wenn die gesamte automatisierte Suite grün ist. Ein grüner Testlauf beweist
das Verhalten der Testdoubles, nicht das der Anwendung.

**Keine Implementierung begonnen. Ende des Auftrags.**
