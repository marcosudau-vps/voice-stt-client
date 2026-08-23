---
id: OBS-FREEZE-ARCH
status: FROZEN
authority: normative
workstream: OBS
freeze_gate: OBS-000
run: RUN-OBS-000-01_2026-08-15_CLAUDE
last_updated: 2026-08-15
---

# Logging-/Observability-Architektur – FREEZE

> **Geltung.** Dieses Dokument ist ab `G-OBS-000 PASS` die **normative**
> Architekturgrundlage des Workstreams OBS. Es löst die Entwürfe unter
> `00_GRUNDLAGEN/` als Entscheidungsquelle ab. Die Entwürfe bleiben als
> Herleitung erhalten und werden **nicht** gelöscht.
>
> **Änderungsregel.** Eine Abweichung von diesem Dokument ist nur über einen
> ausdrücklichen `DECISION REQUIRED`-Vorgang zulässig, der im Run Report des
> jeweiligen Work Packages und in
> `LOGGING_DECISIONS_FREEZE_V1.md` festgehalten wird. Ein Coding-Agent darf
> hier nichts stillschweigend ändern.
>
> **Aufbau.** Kapitel 1–4 beschreiben den **Endzustand**. Kapitel 5–8
> beschreiben die **erste Implementierungsstufe (Teil A / V1)**. Kapitel 9–11
> beschreiben die Grenzen zwischen beiden und die Zukunftsauflagen.

**Begleitdokumente gleicher Autorität**

| Datei | Inhalt |
|---|---|
| `LOGGING_CONTRACTS_FREEZE_V1.md` | Datenmodell, Schema, Schnittstellen, Redaction, Hookliste |
| `LOGGING_DECISIONS_FREEZE_V1.md` | Jede geschlossene Entscheidung mit Begründung; Widerspruchsregister |

---

# 1. Grundgedanke und nicht verhandelbare Invarianten

Logging ist in diesem System ein **Beobachter**. Es nimmt am fachlichen Ablauf
teil wie ein Messgerät an einem Kreislauf: es liest, es entscheidet nichts.

## 1.1 Die dreizehn Invarianten

Diese Invarianten gelten für **jede** Ausbaustufe, auch für Teil B.

| ID | Invariante | Bedeutung |
|---|---|---|
| **O-01** | **Observability Only** | Logging besitzt keine fachliche Runtime-Autorität. Kein Rückgabewert eines Beobachters darf einen fachlichen Ablauf steuern. |
| **O-02** | **Fan-out statt Vermittlung** | Ein Ereignis geht *parallel* an Fachlogik und Observability, niemals *durch* die Observability hindurch. |
| **O-03** | **Non-Blocking** | Kein Audio-, WebSocket-, Controller- oder UI-Pfad wartet auf DB- oder Datei-I/O. Es gibt ausschließlich `put_nowait`. |
| **O-04** | **Bounded Memory** | Jede Queue und jeder Puffer ist begrenzt. Überlauf wird verworfen und gezählt, nie gepuffert. |
| **O-05** | **Failure Isolation** | Store-, Sink-, Queue-, Worker-, Query- oder Providerfehler bleiben innerhalb der Observability-Domäne. |
| **O-06** | **Struktur statt Textparsing** | Kritische Diagnosedaten entstehen strukturiert. `message` wird **nie** zurückgeparst. |
| **O-07** | **Source Preservation** | `producer_kind`, `channel`, `level` und `type` bleiben vier getrennte Dimensionen. |
| **O-08** | **Replay Safety** | Replay erzeugt keine unkontrollierten Persistenzduplikate. |
| **O-09** | **Security / Redaction** | Secrets werden nie persistiert — weder in Store, noch in `raw`, noch in einem Datei-Sink. |
| **O-10** | **Query Independence** | Die UI kennt weder SQLite noch WebSocket- oder Admin-Transportdetails. |
| **O-11** | **Extensible Producer / Provider Boundaries** | Neue Producer und neue Query-Provider sind per Adapter bzw. Protokoll ergänzbar, ohne den Core umzubauen. |
| **O-12** | **Admin Separation** | Logging *nutzt* später privilegierte Provider, *besitzt* aber weder Admin-Key noch Authentifizierungszustand. |
| **O-13** | **Control-Plane-Trennung** | `/ws/logs` bleibt Observability. Die fachliche Activation-/Session-Wahrheit liegt auf `/ws/transcribe`. |

## 1.2 Die eine Invariante, die in den Entwürfen fehlte

Aus `LOGGING_ADVERSARIAL_REVIEW.md §5.5`, hier normativ nachgetragen:

```text
O-14  SCHREIBMONOPOL
      Es gibt genau EINEN Schreibpfad in den lokalen Store:

          Ingress -> Worker -> Store

      Der Query-Layer ist ausschliesslich lesend. KEIN LogProvider schreibt
      jemals -- auch ein Remote-Provider nicht.

      Grund: Dasselbe Serverereignis darf gleichzeitig als lokal gespeicherte
      Kopie UND als remote abgefragtes Ergebnis existieren. Genau dieser
      Unterschied ist der Diagnosewert ("Serverhistorie hat es, lokale
      Historie nicht"). Wuerde ein Provider schreiben, ginge er verloren.
```

## 1.3 Was der Logging-Core ausdrücklich nicht tut

- keine Businesslogik ausführen;
- keinen Activation-State besitzen;
- Events nicht korrigieren, nicht ergänzen, nicht raten;
- keine Kommandos wiederholen;
- keine Serverkonfiguration besitzen;
- kein Feedback rendern (weder LED noch Ton noch Overlay);
- die Runtime-Control-Plane nicht ersetzen.

Insbesondere: Ein Fehler der Logging-Domäne wird **niemals** über
`report_local_feedback`, `CanonicalEventType` oder die `FeedbackEngine`
gemeldet. Das würde eine LED-/Sound-/Overlay-Reaktion auslösen und Logging zum
Feedbackproduzenten machen — ein direkter Verstoß gegen O-01.

---

# 2. Endzustand – die vier Verantwortungsbereiche

```text
PRODUCERS                INGESTION            CORE            PERSISTENZ
Client Python Logging ->  PythonLogAdapter \
Client Struct. Events ->  ClientEventAdapter >-> Normalizer -> Queue -> Worker -+-> SQLiteLogStore
Server Live Events    ->  ServerLiveAdapter /                                   +-> JSONL Sink
LED Controller        ->  (in-process: Normalizer-Regel; spaeter LedAdapter)    +-> weitere Sinks
weitere Producer      ->  weitere Adapter

QUERY                                        CONTROL / AUTH        UI
LocalLogProvider          \                  ServerControlConn.    LogWindow
SessionHistoryProvider     >-> LogQueryService <- (nur spaeter) -> Settings-Tab
ServerHistoryProvider     /                  AdminAuth/Caps        Admin-UI (spaeter)
ServerGlobalLogProvider  /                   ServerAdminService
```

## 2.1 Producers

Erzeugen Beobachtungsdaten und **warten nie** auf deren Verarbeitung.

## 2.2 Ingestion

Nimmt Livedaten entgegen, normalisiert sie in genau ein Recordmodell, redigiert
und übergibt an die Queue.

## 2.3 Query Providers

Liefern historische oder entfernte Daten **auf Anfrage**. Sie sind
Abfrageschnittstellen, keine Abonnementschnittstellen und keine Schreibwege
(O-14).

## 2.4 Control / Auth

Verwaltet privilegierte Serverkommunikation: Admin-Authentifizierung,
bestätigte Capabilities, serverweite Einstellungen, Zugriff auf privilegierte
Loghistorie.

**Logging nutzt diese Schicht, besitzt sie aber nicht.** Sie liegt in einem
eigenen Paket `core/server_control/`, **nicht** unterhalb von
`core/observability/`.

---

# 3. Endzustand – Herkunft, Zeit und Ordnung

## 3.1 Vier orthogonale Dimensionen

```text
producer_kind   WER hat es erzeugt        client | server | led | other
channel         WORUEBER                  system | audit | transcription | performance
level           WIE DRINGEND              DEBUG | INFO | WARNING | ERROR | CRITICAL
type            WAS GENAU                 offener Namensraum, z. B. transcription.completed
```

Diese vier dürfen sich **nie** vermischen. Insbesondere ist `led` ein
`producer_kind` und **kein** Channel, und `client_ui` wäre ein Channel, der
Herkunft in die Kategorie mischt — deshalb gibt es ihn nicht.

## 3.2 Zeit- und Ordnungsmodell

Client und Server haben keine gemeinsame Uhr. Verbindlich:

```text
Sortierung der lokalen Historie      ->  logs.id            (lokale Einfuegeordnung)
Sortierung innerhalb Server-Fakten   ->  server_cursor      (nur je instance_id!)
Anzeige-/Filterdimension "Zeit"      ->  received_at        (lokale Wanduhr)
Diagnose Zeitversatz                 ->  source_timestamp - received_at
NIEMALS                              ->  source_timestamp als Primaersortierung
```

Eine belastbare Reihenfolge über mehrere Producer hinweg wird aus IDs, Cursorn,
Generationen und Kommandobeziehungen gebildet — Zeitstempel sind nur
**ergänzend**.

## 3.3 Welche IDs global eindeutig sind

```text
global eindeutig     event_id (uuid4), record_id (uuid4), instance_id (uuid4 je Prozess)

NICHT global         server_cursor  -> nur je (producer_id, instance_id)
                     session_id     -> faktisch eindeutig, serverseitig je Verbindung neu
                     segment_id     -> nur innerhalb einer Session
                     generation     -> nur innerhalb EINES Clientprozesses
                     command_id     -> 48 Bit; innerhalb einer Session praktisch
                                       kollisionsfrei, NICHT global geeignet
                     activation_id  -> serverseitig nicht stabil, siehe 3.4
```

**Normativ:** Kein Index und keine Dedupe-Regel darf auf `command_id`,
`segment_id` oder `generation` allein aufbauen.

## 3.4 `activation_id` ist diagnostisch, nicht autoritativ

`LETZTE_ARCHITEKTURKLAERUNGEN_VOR_PLAN_FREEZE.md §1.2` belegt: Die
`activationId` wird zum Publikationszeitpunkt frisch aus dem Controller gelesen.
Ist die Activation bereits geschlossen, fehlt sie; ist inzwischen eine neue
geöffnet, ist sie **falsch**.

```text
NORMATIV
  * activation_id wird gespeichert, weil sie in der Mehrzahl der Faelle stimmt
    und weil gerade die FALSCHEN Zuordnungen fuer die kommende
    Triggerarchitektur-Migration wertvoll sind.
  * activation_id wird AUSSCHLIESSLICH aus envelope.data.activationId
    uebernommen -- nie clientseitig ergaenzt, nie geraten, nie fortgeschrieben.
  * activation_id darf NIE zum fachlichen Gruppieren oder Zusammenfassen
    benutzt werden.
  * Der UI-Filter "nur diese Activation" traegt einen sichtbaren Hinweis auf
    die Unzuverlaessigkeit.
```

Nach der Triggerarchitektur-Migration (OBS-100) wird dieser Vorbehalt neu
bewertet, sobald die serverseitige Bindung korrigiert ist.

---

# 4. Endzustand – Ausbauteile

Der Workstream ist zweigeteilt und bleibt es.

## 4.1 TEIL A – vor der Triggerarchitektur-Migration

| WP | Titel |
|---|---|
| OBS-000 | Plan Freeze & Baseline *(dieses Gate)* |
| OBS-010 | Canonical Model, Redaction, Normalizer & Contracts |
| OBS-020 | Ingress, Backpressure, Health & Python-Logging-Handler |
| OBS-030 | Worker, SQLite-Store, Retention & JSONL-Sink |
| OBS-040 | Server Live Adapter & strukturierte Client-Hooks |
| OBS-050 | Local Query, Log View & Settings |
| OBS-060 | V1 Hardening, Failure-/Perf-Gate & Observability Baseline |

## 4.2 TEIL B – nach Stabilisierung der Triggerarchitektur

| WP | Titel |
|---|---|
| OBS-100 | Post-Trigger Instrumentation Completion |
| OBS-110 | Server Control, Admin Auth & Capabilities |
| OBS-120 | Remote Server History & Global Logs |
| OBS-130 | Serverweite Admin-Settings im Desktopclient |
| OBS-140 | LED-Controller Logging Integration |
| OBS-150 | Erweiterte Sinks / Storage Backends |
| OBS-160 | Advanced Query / UX |
| OBS-170 | Cross-Source Correlation / Forensics |
| OBS-180 | Final Hardening, Docs & Acceptance |

## 4.3 Die Regel, die beide Teile verbindet

> **V1 muss spätere Funktionen nicht implementieren, darf ihre Schnittstellen
> aber nicht verbauen.**

Kapitel 10 führt für jede Teil-B-Funktion einzeln auf, *wie* sie später
additiv ergänzt wird und *was* V1 dafür heute schon richtig machen muss.

---

# 5. Teil A / V1 – Komponentenbild

```text
                     Producer-Threads (sechs, siehe 6.1)
                                  |
                                  |  submit(record)   synchron, nie blockierend,
                                  |                   nie werfend
                                  v
                        ObservabilityIngress
                          - Health == FAILED?        -> return False
                          - enabled / Level-Filter   -> return False
                          - Wasserstandsregel (7.2)  -> return False
                          - queue.put_nowait         -> bei Full: zaehlen, False
                                  |
                                  v
                   EINE bounded queue.Queue (Standard 8192)
                                  |
                                  v
     LoggingWorker   threading.Thread("RealtimeSTT-Observability", daemon=True)
                          1. bis zu batch_size Records ziehen
                          2. raw/details entfrieren, serialisieren, redigieren
                             (nur fuer Serverpayloads -- siehe 8.2)
                          3. SQLiteLogStore.write_batch  (eine Transaktion)
                          4. JSONL-Sink, falls aktiv     (NACH dem Commit)
                          5. Retention, falls faellig
                          6. Aggregatrecords + Health aktualisieren
                                  |
                +-----------------+------------------+
                v                                    v
        SQLiteLogStore                          JsonlSink (optional)
     (eine Verbindung, WAL,                  (eine Datei, Tagesrotation)
      im Worker-Thread erzeugt)
                |
                | nur lesend, eigene kurzlebige Verbindung, PRAGMA query_only=ON
                v
        LocalLogProvider -> LogQueryService -> LogQueryController (Qt)
                                                      |
                                                      v
                                            LogTableModel / LogWindow
```

## 5.1 Modulstruktur – eingefroren

```text
voice-stt-client/
├── core/
│   └── observability/               <- Paketname: FD-N1 (OD-01), Option A
│       ├── __init__.py              nur Re-Exports: ObservabilityManager,
│       │                            ObservabilityIngress, NULL_INGRESS,
│       │                            CanonicalLogRecord
│       ├── models.py                CanonicalLogRecord, ProducerKind, Channel,
│       │                            Level, Scope, RecordPriority
│       ├── redaction.py             Schluesselregel, Pfadkuerzung, unfreeze()
│       ├── normalizer.py            drei Eingaenge -> CanonicalLogRecord
│       ├── ingress.py               ObservabilityIngress, NullIngress
│       ├── health.py                LoggingHealthState/-Snapshot,
│       │                            LoggingInternalHealth, Emergency-stderr
│       ├── worker.py                LoggingWorker
│       ├── manager.py               ObservabilityManager (Kompositionswurzel)
│       ├── adapters/
│       │   ├── python_logging.py    UnifiedLogHandler
│       │   ├── client_events.py     ClientEventEmitter
│       │   └── server_live.py       ServerLiveAdapter
│       ├── storage/
│       │   ├── base.py              LogStore-Protokoll
│       │   └── sqlite.py            SQLiteLogStore
│       ├── query/
│       │   ├── base.py              LogProvider, QueryFilter, QueryPage,
│       │   │                        ProviderStatus, LogRecordView
│       │   ├── local.py             LocalLogProvider
│       │   └── service.py           LogQueryService
│       └── sinks/
│           ├── base.py              Sink-Protokoll
│           └── jsonl_file.py        JsonlSink
└── ui/
    └── logs/
        ├── log_window.py            LogWindow(QWidget), nicht-modal
        ├── log_page.py              LogPage(QWidget)
        ├── log_table_model.py       LogTableModel(QAbstractTableModel)
        ├── log_filter_bar.py        LogFilterBar(QWidget)
        ├── log_detail_view.py       LogDetailView(QWidget)
        └── log_query_controller.py  LogQueryController(QObject)
```

**In V1 ausdrücklich NICHT angelegt:**
`adapters/led.py` (LEFX läuft in-process), `query/server_history.py`,
`sinks/text_file.py`, `core/server_control/`, `ui/settings/logging_settings.py`.

## 5.2 Schichtung und Importrichtung – eingefroren

```text
models  <-  redaction  <-  normalizer  <-  ingress  <-  worker  <-  manager

storage  kennt nur models
sinks    kennen nur models
query    kennt models + storage
adapters kennen ingress + normalizer,  NICHT umgekehrt

ui/logs/**  importiert core.observability.query.*
            importiert NIE core.observability.storage.*
            importiert NIE sqlite3
core/**     importiert NIE PySide6
```

Jede dieser Regeln ist durch einen Contract-Test zu belegen (Muster: die
bereits vorhandenen Contract-Tests des Repositories).

## 5.3 Warum ein Unterpaket, obwohl `core/` und `ui/` heute flach sind

`core/` enthält 20 Module, `ui/` elf; es gibt heute **kein** Unterpaket. Das
Observability-Paket bringt rund 15 Module mit. Sie flach dazuzulegen würde
`core/` unlesbar machen. Alle Importe im Repository sind absolut
(`from core.x import y`), Unterpakete funktionieren damit unverändert. Der
Bruch mit der bisherigen Flachstruktur ist **bewusst** und hiermit benannt.

**PyInstaller:** keine Spec-Änderung nötig, solange alle Module **statisch**
importiert werden. Ein Sink oder Provider, der über einen Namensstring geladen
würde, müsste in die Spec — das ist ein Grund, es nicht zu tun. Dynamisches
Laden von Sinks und Providern ist in V1 **verboten**.

---

# 6. Teil A / V1 – Nebenläufigkeit

## 6.1 Die sechs realen Producer-Threads

| # | Thread / Task | Kritikalität | darf blockieren? |
|---|---|---|---|
| 1 | PortAudio-Callbackthread (`audio_capture.py`) | **höchste** – Blockieren erzeugt Treiberaussetzer | **niemals** |
| 2 | Thread `audio-process` (daemon) | hoch | nein |
| 3 | Thread `RealtimeSTT-AsyncCore` (asyncio-Loop): Session, Audio-Sender, Eventstream-Task, Timer | hoch, trägt den Hot Path | **niemals** |
| 4 | Qt-Mainloop | hoch – Blockieren friert die Anwendung sichtbar ein | **niemals** |
| 5 | Thread `RealtimeSTT-LED` (daemon), inkl. aller `lefx.*`-Records | mittel | nein |
| 6 | Injection-Worker (non-daemon) | mittel | nein |
| — | Hauptthread vor Qt-Start (`AppConfig.load`, `setup_logging`) | – | – |

**Kernbefund, der die Bauform bestimmt:** Der asyncio-Loop existiert **nicht
immer**. Er wird von `CoreBridge._thread_main` erzeugt und am Ende geschlossen.
Vor `bridge.start()` und nach `bridge.stop()` laufen Konfigladen,
Logging-Setup, UI-Aufbau, LED-Aufbau und der komplette
`LedConfigurationError`-Startabbruchpfad **ohne** Loop — und erzeugen dabei
bereits heute Logzeilen. Genau diese Startabbrüche sind diagnostisch am
wertvollsten.

**Daraus folgt normativ:**

- Der Worker ist ein **dedizierter Thread**, kein asyncio-Task.
- Die Queue ist eine `queue.Queue` aus der stdlib, **keine** `asyncio.Queue`
  (nicht thread-sicher) und **keine** `PriorityQueue` (Vergleich je `put`).
- `daemon=True` wie bei `RealtimeSTT-LED`, damit ein hängender Worker den
  Prozessabbruch nicht verhindert. Der Flush ist über `stop(timeout)`
  **explizit** abgesichert, nicht über die Thread-Semantik.

## 6.2 Lebenszyklus – eingefroren

```text
START   (app.py::main)
  1. AppConfig.load()
  2. ObservabilityManager(config.logging.observability) bauen
  3. manager.start()
  4. setup_logging(config.logging, observability=manager)
  5. alles Uebrige wie heute

ENDE    (app.py::main, in einem try/finally um den GESAMTEN Ablauf)
  1. ... regulaerer Ablauf oder Startabbruch ...
  2. DesktopApplication.shutdown()   (wie heute)
  3. bridge.stop(timeout=10.0)       (wie heute)
  4. manager.stop(timeout=2.0)       <- ZULETZT, im finally
```

Zwei Korrekturen an den Entwürfen, beide verbindlich:

**(a) Reihenfolge beim Start.** Der ältere Plan verlangte, den Manager *vor*
`AppConfig.load` zu starten, damit Ladefehler erfasst werden. Das ist unmöglich:
Der Manager braucht `config.logging.observability`, und die entsteht erst durch
`AppConfig.load()`. Meldungen aus `AppConfig.load` bleiben verloren — wie heute.
Ein Konfigfehler ist über `stderr` und die spätere `client.log` sichtbar.

**(b) Ort der Lebensdauer.** Der Manager wird in `app.py::main()` erzeugt und
dort in einem `try/finally` gestoppt — **nicht** in
`DesktopApplication.shutdown()`. Grund: Es gibt vier Wege, auf denen
`run_gui` zurückkehrt, **ohne** dass eine `DesktopApplication` existiert oder
ihr `shutdown` läuft (Instanzsperre, fehlendes Tray, `LedConfigurationError`,
UI-Initialisierungsfehler), und der Headless-Pfad ruft `shutdown` nie.
`DesktopApplication` bekommt den Manager übergeben und stoppt ihn **nicht**.

Die Reihenfolge `bridge.stop()` **vor** `manager.stop()` ist zwingend: Der
Core-Shutdown erzeugt selbst Records (fünf mögliche Fehlerstellen). Ein früher
gestoppter Logger verlöre genau die Shutdownfehler.

## 6.3 Die harte Nichtblockierungs-Invariante und ihr Nachweis

```text
Umgesetzt durch:
  * ausschliesslich put_nowait, kein einziges blockierendes put;
  * kein Lock, das ueber eine I/O-Operation gehalten wird -- die
    Store-Verbindung beruehrt NUR der Worker, es gibt keinen Store-Lock;
  * kein Lock zwischen Ingress und Worker ausser den queue-internen;
  * Entfrieren, Serialisieren und die Redaction von SERVER-Payloads
    geschehen im WORKER, nicht im Producer (siehe 8.2).

Nachweis (verbindlich, OBS-020 und OBS-060):
  Worker anhalten, danach 20.000 Records einreichen. submit() muss
  durchgehend unter einer im ersten Lauf festgeschriebenen Zeitgrenze
  zurueckkehren und darf nie werfen.
```

## 6.4 Ausdrücklich nicht getan

- kein `QueueHandler`/`QueueListener` der stdlib (eigenes Threadmodell, kein
  Batching, keine Dropstrategie);
- keine Änderung an `setup_logging` außer dem Hinzufügen **eines** Handlers;
- kein Anfassen der Audio-, LED- oder Injection-Queues;
- kein zusätzlicher Thread je Sink — Sinks schreiben im Worker.

---

# 7. Teil A / V1 – Backpressure und Priorität

## 7.1 Eine Queue statt zweier

Der ältere Entwurf sah zwei Queues (1024 / 8192) mit gegenseitiger Verdrängung
vor. Eingefroren ist **eine** Queue mit Wasserstandsregel.

Begründung: Die Zweiqueue-Lösung verlangte, dass ein Producer-Thread im
Überlastfall `low.get_nowait()` aufruft, also aus einer fremden Queue entnimmt —
zusätzlicher Zustand, zusätzliche Buchführung, zusätzliche Fehlerfläche, bei
identischem Ergebnis.

```text
queue_size            8192  (konfigurierbar)
Wasserstandsschwelle  75 %  (fest)

Fuellstand <  75 %  ->  jeder Record wird angenommen
Fuellstand >= 75 %  ->  nur HIGH-Records werden angenommen;
                        LOW-Records werden verworfen, dropped_watermark++
Queue voll          ->  verwerfen, dropped_queue_full++
```

## 7.2 Die Prioritätsregel – Korrektur gegenüber der Vorarbeit

```text
HIGH  :=  record.is_internal
      OR  ( replayed is False
            AND ( level >= WARNING
                  OR channel == "audit"
                  OR type is not None ) )

LOW   :=  alles andere
```

**Warum `replayed is False` hinzukommt.** Das adversariale Review begründet den
Schutz gegen die Replay-Flut damit, dass replayte Records „ohne `type`" als LOW
eingestuft würden. Das trifft nicht zu: Jedes Serverevent **hat** einen `type`
und wäre nach der ursprünglichen Regel HIGH — der Flutschutz hätte also gar
nicht gegriffen. Genau der Fall, für den er gedacht war (Serverneustart bei
serverseitiger Retention `0` → vollständiger Replay der gesamten Serverhistorie),
wäre ungeschützt geblieben.

Mit der Ergänzung ist der Schutz wirksam **und verlustfrei**, weil replayte
Daten bereits gespeichert sind und der Dedupe-Index sie ohnehin unterdrückt.

**Benannte Grenze.** Ein replayter `ERROR`, den der Client noch nie gesehen hat
— also beim allerersten Verbindungsaufbau —, kann unter Überlast verworfen
werden. Das ist der bewusst akzeptierte Preis. Sichtbar wird es über
`dropped_watermark` und den Record `logging.records_dropped`.

## 7.3 Zähler – eingefroren

```text
enqueued              angenommen
written               tatsaechlich in den Store geschrieben
deduplicated          durch ON CONFLICT unterdrueckt        <- fehlte im Entwurf
dropped_watermark     wegen Wasserstandsregel verworfen
dropped_queue_full    wegen voller Queue verworfen
dropped_shutdown      beim Shutdown-Timeout verworfen
malformed             Normalizer/Serialisierung gescheitert
store_errors, sink_errors, retention_errors, worker_errors
queue_depth           aktueller Fuellstand
db_bytes              page_count * page_size, optional
```

`deduplicated` ist zwingend: Ohne diesen Zähler ist im Betrieb **nicht
unterscheidbar**, ob ein Replay korrekt dedupliziert oder ob überhaupt nichts
angekommen ist.

Nach Erholung (Füllstand < 25 % über mindestens 5 s) erzeugt **der Worker**
genau **einen** Record `logging.records_dropped` mit den Zählerständen und setzt
sie zurück. Dieser Record entsteht im Worker und wird direkt geschrieben, unter
Umgehung von Handler und Queue — sonst entstünde eine Rekursion.

---

# 8. Teil A / V1 – Failure Domain

## 8.1 Die vier Rekursionswege und ihre Sperren

```text
Weg 1  Store wirft -> Store loggt -> Root-Logger -> Handler -> Queue ->
       Worker -> Store wirft ...
Weg 2  Handler.emit wirft -> stdlib handleError -> Traceback je Record
Weg 3  Normalizer wirft -> logger.exception -> derselbe Weg
Weg 4  Sink-Fehler wird ueber den Handler gemeldet -> derselbe Sink

G-1  Wiedereintrittssperre im Handler (threading.local-Flag). Deckt 1 und 3.
G-2  Eigener, NICHT propagierender Logger "observability.internal" mit einem
     Emergency-stderr-Handler. Jeder logger-Aufruf INNERHALB von
     core/observability/ benutzt ausschliesslich diesen. Guertel und
     Hosentraeger, weil G-1 bei einem Fehler in einem ANDEREN Thread nicht
     greift.
G-3  UnifiedLogHandler.handleError meldet an LoggingInternalHealth, nicht an
     stderr. Deckt 2.
G-4  Der Emergency-stderr-Ausgang ist HART ratenbegrenzt: hoechstens eine
     Zeile je Fehlercode und 60 s, unabhaengig von der Fehlerzahl, mit
     Wiederholungszaehler. Format:
         [observability] store_write_failed (x37): database is locked
     sys.stderr is None (PyInstaller-GUI-Build) wird abgefangen; eine volle,
     ungelesene Pipe darf den meldenden Thread nie haengen lassen.
G-5  Kein Logging-Fehler wird je ueber den Feedbackweg gemeldet (O-01).
G-6  logging.records_dropped und logging.recovered schreibt der Worker direkt.
G-7  UnifiedLogHandler.flush() und .close() sind NO-OPS. Grund:
     logging.shutdown() laeuft ueber atexit und ruft flush()+close() auf jedem
     Handler; zu diesem Zeitpunkt kann der Daemon-Worker bereits eingefroren
     sein. Ein wartendes close() waere ein Deadlock beim Prozessende. Der
     Flush geschieht ausschliesslich ueber manager.stop().
```

## 8.2 Wo redigiert wird – präzisierte Regel

Der ältere Entwurf verlangte: „kein unredigierter Record je in der Queue",
also Redaction vollständig im Producer-Thread. Das ist für Serverpayloads
falsch, weil dort bis zu 1 MiB (`max_message_size`) auf dem Core-asyncio-Loop
entfroren, serialisiert und durchsucht würden — genau auf dem Loop, der
Audioversand und STT-Session trägt.

```text
NORMATIV

  Records, die der CLIENT selbst baut
      -> Redaction im Producer-Thread, vor der Queue.
         Es sind kleine, flache Strukturen; die Tiefen- und Knotengrenze
         (R-12) begrenzt den Aufwand hart.

  raw-Payloads EINGEHENDER Serverevents
      -> Der Ingress nimmt die bereits eingefrorene Referenz entgegen und
         kopiert nichts.
      -> Entfrieren, Serialisieren und Redigieren geschehen im WORKER.
      -> Zulaessig, weil der Server Credentials, Authorization, Cookies,
         Querystrings und Binaerfelder bereits VOR jedem Sink entfernt.
         Verbleibt allein die Transkriptinhaltsregel -- eine
         Datenschutzrichtlinie, kein Geheimnisleck, und im Worker genauso
         wirksam.
      -> Der hello-Payload ist davon NICHT beruehrt: er wird nie raw,
         sondern ausschliesslich ueber eine Whitelist erfasst (R-6).

  Groessengrenze
      -> raw ueber 64 KiB wird nicht gespeichert, sondern durch
         {"_truncated": true, "_bytes": n} ersetzt. Ein 1-MiB-Event ist ein
         Serverdefekt, kein Diagnosefall.
```

## 8.3 Fehlerfälle und Health-Zustände

| Fehler | Reaktion | Health |
|---|---|---|
| SQLite **locked** | `busy_timeout=5000` im Worker; Batch **einmal** wiederholen, dann verwerfen. Leser blockieren dank WAL ohnehin nicht | `DEGRADED_STORE` |
| SQLite **disk full** | Batch verworfen; **Retention wird ausgesetzt** (auch ein `DELETE` braucht Platz im WAL) | `FAILED_STORE` |
| SQLite **corrupt** / Öffnen scheitert | Store deaktiviert. **Die Datei wird NIE gelöscht oder umbenannt** — sie ist Diagnosematerial, und der Fehlerfall ist der schlechteste denkbare Moment, sie wegzuwerfen | `FAILED_STORE` |
| Store wirft beim Schreiben | nach 5 aufeinanderfolgenden Fehlschlägen Store für 60 s aussetzen, danach mit einem leeren Testschreibvorgang prüfen | `DEGRADED_STORE` → ggf. `FAILED_STORE` |
| Migration schlägt fehl | Rollback, Store deaktiviert, **Datei unverändert**, Anwendung läuft | `FAILED_STORE` |
| `user_version` **höher** als bekannt | Store im **Nur-Lesen**-Betrieb. Nicht löschen, nicht downgraden — der Nutzer hat vielleicht nur eine ältere Version gestartet | `DEGRADED_STORE` |
| JSONL-Sink kaputt | Sink deaktivieren, **einmal** an stderr, Store läuft weiter | `DEGRADED_SINK` |
| Queue voll / Wasserstand | zählen, kein Log, kein stderr; Meldung erst nach Erholung | `DROPPING` |
| Worker-Ausnahme in der Schleife | gefangen, `worker_errors++`, Schleife läuft weiter. Bricht sie dennoch ab: Ingress wechselt in „nur verwerfen und zählen". **Kein Neustartversuch** — ein Worker, der zweimal stirbt, stirbt beim dritten Mal auch | `FAILED_WORKER` |
| Normalizer-Ausnahme | Record verworfen; **ein** Ersatzrecord `logging.record_rejected` mit Komponente und Ausnahmetyp, **ohne** Originaldaten | `OK` + `malformed++` |
| malformed Serverevent | erreicht den Beobachter gar nicht (siehe 8.5); sichtbar als `client.eventstream.protocol_error` | Zähler |
| UI-Abfrage teuer/fehlerhaft | eigener Query-Thread; `PRAGMA query_only=ON` verhindert zusätzlich jedes Schreiben durch den Leser | Statuszeile |
| Shutdown während Flush | hartes Zeitbudget 2 s, danach `dropped_shutdown`, eine stderr-Zeile | – |

Zustandsmenge, eingefroren:
`OK`, `DROPPING`, `DEGRADED_SINK`, `DEGRADED_STORE`, `FAILED_STORE`,
`FAILED_WORKER`, `DISABLED`.

## 8.4 Verhalten bei einem logging-internen Fatalfehler

Still. Nur Health, ratenbegrenztes stderr und die **Statuszeile im LogWindow**.
Keine Tray-Benachrichtigung: Das würde ein Diagnoseproblem zu einer
Nutzerunterbrechung machen, und `TrayController.notify` ist heute den Dingen
vorbehalten, die den Nutzer wirklich betreffen. Kein automatischer Neustart des
Workers.

**Ausnahme:** Wer das LogWindow geöffnet hat, sieht sofort, dass die Daten
unvollständig sind.

## 8.5 Benannte Grenzen der Beobachtung

Diese vier Grenzen sind Eigenschaften der Architektur, keine Mängel. Sie werden
benannt, damit niemand sie später für einen Defekt hält.

```text
GRENZE 1  Der Beobachterhook sieht jedes erfolgreich VALIDIERTE Ergebnis,
          nicht jedes Frame. Frames, die die Protokollvalidierung nicht
          bestehen, erreichen den Dispatch nie -- ausgerechnet der
          interessanteste Diagnosefall (ein Server, der das Protokoll
          verletzt) bliebe unstrukturiert.
          -> Gegenmassnahme in V1: ein zweiter, sehr kleiner
             Beobachtungspunkt im except-Zweig von EventStreamTransport.run(),
             der Typ und Meldung als client.eventstream.protocol_error
             erfasst -- OHNE das Rohframe, das dort nicht mehr vorliegt.
             Kein zusaetzlicher Kontrollfluss.

GRENZE 2  Das Beobachterprinzip garantiert VERHALTENSGLEICHHEIT, nicht
          LATENZGLEICHHEIT. Der Beobachter laeuft vor dem Feedbackzweig auf
          demselben Thread. Deshalb ist der Test "Beobachter blockiert 2 s"
          kein Kuriosum, sondern die Dokumentation dieser Grenze.

GRENZE 3  Faellt der Worker aus, gehen ab diesem Zeitpunkt alle Records
          verloren. Der bestehende RotatingFileHandler bleibt davon
          UNBERUEHRT und ist genau deshalb die Rueckfallebene. Das ist der
          Hauptgrund, ihn nicht zu ersetzen.

GRENZE 4  Ein harter Prozessabbruch verliert den Queue-Inhalt. Das ist der
          bewusste Preis der Nichtblockierung.
```

## 8.6 Hot-Path-Regeln – verbindlich

```text
HOT PATH (keine Logzeile, kein submit, kein Format-, kein JSON-Aufwand)
    core/audio_capture.py::_audio_callback         PortAudio-Thread
    core/audio_capture.py::_process_loop           Thread audio-process
    core/controller.py::_on_audio_packet_from_thread
    core/controller.py::_enqueue_audio_packet
    core/controller.py::_audio_sender
    core/stt_session.py::send_audio
    core/stt_session.py::_message_loop
    core/event_stream.py::_run_live / _receive_result
    core/stt_session.py::_apply_event, Zweig "realtime"

An diesen Stellen ausschliesslich:
    einfache int-Attribute erhoehen. Ohne Lock -- ein verlorenes Inkrement
    ist folgenlos, ein Lock im PortAudio-Callback nicht.

Der Aggregatrecord entsteht im WORKER, der die Zaehler LIEST:
    client.audio.stream_stats, Channel "performance", Level DEBUG, alle 5 s
    waehrend aktiven Streamings, mit
        chunks_captured, chunks_dropped_capture_queue,
        chunks_dropped_send_queue, bytes_sent, packets_sent,
        overflow_count, underflow_count, max_send_queue_depth
    Zusaetzlich einmalig bei Zustandswechsel:
        client.audio.stream_started / client.audio.stream_stopped

Rechnung, die die Regel begruendet: bei 40-ms-Chunks sind das 25 Callbacks
je Sekunde und Richtung. Eine Zeile je Chunk ergaebe ~90.000 Records je
Stunde Diktat und machte die lokale Historie unbrauchbar.

Nachweis: ein Test, der den QUELLTEXT der genannten Funktionen liest und
belegt, dass dort kein submit, kein format, kein json und kein
Attributzugriff auf den Ingress steht.
```

## 8.7 Levelzuständigkeit

Handler-Level und Ingress-Level filtern beide. Ohne Festlegung hätte ein
Coding-Agent zwei plausible Deutungen.

```text
NORMATIV
    Handler-Level   gilt fuer Python-Logs.
    Ingress-Level   gilt fuer strukturierte Clientevents und Serverevents.
    Ein einziger Konfigwert -- logging.observability.level -- speist beide.
    Default INFO.
```

`DEBUG` ist waehlbar, aber teuer: Der Root-Logger steht ohnehin auf `DEBUG`,
sodass jeder `LogRecord` erzeugt wird; erst der Handler-Level verhindert
`emit`. Datenschutzseitig ist `DEBUG` unbedenklich, weil Regel `R-10` auch für
unstrukturierte Logtexte gilt und den Realtime-Text redigiert.

---

# 9. Die Grenze zur Runtime-Control-Plane

Diese Trennung ist die wichtigste Abgrenzung des gesamten Workstreams und gilt
unverändert bis Teil B.

```text
/ws/transcribe    RUNTIME / CONTROL PLANE
                  autoritativ fuer Audio, Befehle, Realtime- und Finaltext,
                  Trigger-Acks, Session-Lifecycle.
                  Der spaetere ActivationMirror wird HIER gebaut.
                  Logging beobachtet, besitzt nichts.

/ws/logs          OBSERVABILITY
                  sessiongebundener Eventstream mit eigenem Token, Replay,
                  Cursor und Reconnect-Zustand.
                  Feedback funktioniert nachweislich auch ohne ihn
                  (STT-Fallback ueber /ws/transcribe).
                  Logging haengt PARALLEL daneben und besitzt weder den
                  Eventstream-Lifecycle noch den Cursor.
```

**Verboten, in jeder Ausbaustufe:**

- Eventreplay als fachliche State-Rekonstruktion benutzen;
- den `FeedbackController` durch Logging ersetzen oder umgehen;
- den Logging-Hook so setzen, dass sein Rückgabewert oder eine aus ihm
  entweichende Ausnahme den Cursor-Commit oder das Verbindungsrecycling
  beeinflusst.

Der letzte Punkt ist keine Vorsichtsmaßnahme, sondern durch den Code erzwungen:
Der Dispatch fängt eine durchschlagende Ausnahme mit `except BaseException`,
ruft `reject_event(result)` und wirft weiter. Ein Beobachter, der wirft, würde
also das Event **aktiv verwerfen**. Deshalb ist `except Exception` im
Beobachterwrapper Pflicht — und `BaseException` dort verboten, weil
`asyncio.CancelledError` das Abbrechen des Eventstream-Tasks trägt.

---

# 10. Zukunftsgrenzen – was V1 nicht verbauen darf

Für jede Teil-B-Funktion: was V1 heute richtig macht, und wie die Funktion
später **additiv** entsteht.

## 10.1 Admin Authentication / Capability State (OBS-110)

```text
V1 macht richtig
  * Der LoggingCore importiert nichts aus core/server_control/ und nichts aus
    core/stt_session.py.
  * ProviderState.AUTH_REQUIRED existiert von Anfang an als gueltiger Wert,
    auch wenn V1 ihn nie erzeugt.
  * Der Core sieht den Session-Log-Token auch NICHT indirekt: der Hook
    liefert SessionContext und EventProtocolResult; SessionContext.log_access
    traegt zwar den Token, wird vom Normalizer aber NIE gelesen -- nur
    generation, session_id, event_state, unavailable_code.

V1 darf NICHT
  * kein Feld, keine Config-Option, kein Settings-Eintrag fuer einen
    Admin-Key;
  * keine HTTP-Schicht (existiert heute nicht; der Client spricht
    ausschliesslich WebSocket);
  * kein "alle Sessions"-Schalter, auch nicht deaktiviert.

Spaeter additiv
  * core/server_control/ als eigenes Paket; ServerControlConnection besitzt
    Auth und Capabilities.
  * Der Zustandswechsel AUTH_REQUIRED -> AVAILABLE ist das EINZIGE, was Auth
    fuer den Query-Layer bedeutet.
  * Auflage: SettingDefinition.sensitive existiert heute, wird aber von
    KEINEM UI-Code ausgewertet. Bevor es je einen Admin-Key traegt, muss es
    zuerst tatsaechlich wirken (Maskierung, kein Klartext in config.yaml,
    keine Aufnahme in changes-Logs).
```

**Offen und bewusst offen gelassen:** Der Server kennt **kein** benanntes
Capability-Set für Admins, sondern nur „admin ja/nein" plus die abgeleiteten
Erweiterungen. Ob später ein benanntes Set eingeführt oder aus dem binären
Zustand abgeleitet wird, ist eine **Serverproduktentscheidung** und wird in
OBS-110 getroffen. Sie kostet heute nichts.

## 10.2 ServerControlConnection (OBS-110)

Eigene Verbindung, eigenes Paket, eigener Lebenszyklus. Sie darf ausfallen,
ohne Session-Logging oder normalen Clientbetrieb zu beeinträchtigen.

## 10.3 Historische und globale Serverlogs (OBS-120)

```text
V1 macht richtig
  * LogProvider ist ein Protokoll; LogQueryService ist eine REGISTRY, keine
    fest verdrahtete Liste. Ohne sie muesste spaeter jeder Aufrufer um einen
    Parameter erweitert werden.
  * QueryPage.next_cursor ist ein OPAKER String. Er passt damit sowohl auf die
    lokale id als auch auf nextCursor des Servers. Ein typisierter
    Integer-Cursor wuerde eines von beidem falsch abbilden.
  * QueryFilter enthaelt bereits die Felder, die der Serverendpunkt kennt
    (session_id, transcription_id, types, since/until).
  * scope existiert als eigene Spalte, weil es NICHT ableitbar ist: ein
    Serverrecord ohne session_id ist "global", ein Clientrecord ohne
    session_id ist "instance".
  * Der Dedupe-Index ist auf (producer_id, event_id) geschluesselt, nicht auf
    event_id allein -- genau fuer einen kuenftigen zweiten Produzenten mit
    eigenem ID-Schema.

Festlegung, damit spaeter kein Umbau noetig ist
    QueryFilter.scopes ist das Ausdrucksmittel fuer "alle Sessions".
    scopes=("global",) BEDEUTET die Adminabfrage. session_id=None bedeutet
    weiterhin "ohne Einschraenkung" und ist damit fuer den lokalen Store
    richtig und fuer einen Adminprovider NICHT mehrdeutig.

Spaeter additiv
  * ProviderCapabilities wird DANN eingefuehrt (in V1 YAGNI, siehe 11.2).
    Moeglich, weil ProviderStatus eine frozen dataclass mit Defaults ist.
  * hello.logAccess.historyPath wird uebernommen -- der Client verwirft dieses
    vom Server gelieferte Feld heute. Eine additive Zeile.
  * Remote-Historie wird NICHT in die lokale SQLite repliziert. Der Server
    bleibt originaere Quelle (O-14).

AUFLAGE, in diesem Run neu ermittelt
    Der Client hat heute KEINEN HTTP-Client: requirements.txt kennt nur
    websockets, sounddevice, numpy, PySide6, PyYAML und
    led-controller-version-3. Die Historien-Endpunkte des Servers sind
    HTTP (/api/logs/*). OBS-120 muss deshalb eine Abhaengigkeits- und
    Buildentscheidung mitplanen (stdlib http.client/urllib gegen eine neue
    Abhaengigkeit) und die PyInstaller-Spec pruefen. Die dortigen excludes
    (fastapi, starlette, uvicorn, pydantic, lefx.interfaces.api|cli)
    betreffen den SERVER-Stack innerhalb von LEFX und stehen dem nicht
    entgegen.
```

## 10.4 Nächster Provider: zuerst die Session-Historie, nicht der Admin

Der naheliegendste zweite Provider ist **nicht** der Admin-Provider, sondern ein
`SessionHistoryProvider` für die **eigene** Session. Er braucht keinen
Admin-Key, keine Auth-UI und keine `ServerControlConnection` — der vorhandene
Session-Log-Token genügt. Er liefert sofort den wertvollsten Vergleich:
„Serverhistorie hat `transcription.completed`, lokale Historie nicht."

Das soll die V2-Planung wissen, **bevor** sie mit dem Admin-Key beginnt.

## 10.5 Serverweite Konfiguration (OBS-130)

Berührt das Logging nicht. Eigener Dienst, eigener Settingsbereich. Die drei
Konfigurationsklassen — **Client-lokal**, **Session-spezifisch**,
**Serverweit/Admin** — bleiben strikt getrennt und dürfen nie denselben
Runtime-Owner verwenden.

## 10.6 LED-Controller als Producer (OBS-140)

```text
V1 macht richtig
  * producer_kind = "led" existiert von Anfang an.
  * LEFX laeuft IM SELBEN PROZESS und loggt nach lefx.*; die Records
    erreichen den Root-Logger ohnehin. Es genuegt EINE Normalizer-Regel:
        logger name startswith "lefx."
            -> producer_kind = "led"
            -> producer_id   = "respeaker-led-controller"
            -> component     = <logger name>
    Damit ist die Herkunftstrennung erfuellt, ohne ein Feld, eine Tabelle
    oder eine Schnittstelle hinzuzufuegen -- und die Erweiterbarkeit ist
    bewiesen, statt behauptet.

Spaeter additiv
  * Erst wenn der LED-Controller in einen eigenen Prozess oder auf ein
    eigenes Geraet wandert, entsteht ein echter LedAdapter -- mit demselben
    Adaptervertrag wie ServerLiveAdapter.
  * Nichtziel bleibt: keine Logging-Abhaengigkeit fuer die LED-Ausfuehrung.
```

## 10.7 Zusätzliche Sinks und Storage-Backends (OBS-150)

Neue Sinks implementieren das bestehende Sink-Protokoll. **Keine Änderung am
CanonicalRecord nur für einen einzelnen Backendanbieter**, außer als
ausdrücklich versionierte Schemaentscheidung. Die lokale SQLite bleibt
unabhängig nutzbar.

## 10.8 Advanced Query / UX (OBS-160) und Forensik (OBS-170)

`QueryFilter` ist eine frozen dataclass; Export liest, was die Query liefert.
Für die Forensik gilt die Ordnungsregel aus 3.2: **keine falsche globale
Reihenfolge allein anhand der Wanduhr behaupten.**

## 10.9 Mehrere Hosts – ehrlich bewertet

`SingleInstanceGuard` verhindert eine zweite Instanz auf **derselben**
Maschine. Zwei Instanzen auf **zwei** Maschinen, die dieselbe Historie sehen
wollen, brauchen einen Collector — und dann fehlt `host`, das V1 bewusst
streicht.

**Ehrliches Urteil: teilweise vorbereitet.** Es ist kein Umbau des Cores,
sondern eine **Migration**: eine nullable Spalte hinzufügen, Altbestand `NULL`.
Multi-Host-Aggregation ist ohnehin als späte Ausbaustufe geführt, und eine
nullable Spalte ist der billigste denkbare Nachtrag.

Der Grund für das Streichen bleibt gültig: Der Windows-Rechnername ist auf
Arbeitsplatzrechnern regelmäßig `VORNAME-PC` und damit ein personenbezogenes
Datum ohne Abfragenutzen, solange nur eine Maschine schreibt.

---

# 11. Was V1 bewusst NICHT baut

## 11.1 Nicht in V1 (architektonisch berücksichtigt)

ServerHistoryProvider · globale Serverlogs · Admin-Authentifizierung ·
Admin-Capability-UI · ServerAdminService · serverweite Config im Desktopclient ·
LedAdapter · MySQL/PostgreSQL · Remote Collector · Exportdialog · gespeicherte
Filterpresets · komplexe Farbregeln · Charts/Statistiken · externe Debug-App ·
REST-/CLI-Query · Multi-Host-Aggregation.

## 11.2 In V1 gestrichen, obwohl in den Entwürfen enthalten

| Gegenstand | Entscheidung | Begründung |
|---|---|---|
| **Memory-Ringbuffer** | **entfällt** | Die Live-Ansicht wird als tailende Abfrage `WHERE id > :last ORDER BY id LIMIT n` alle 250 ms realisiert — auf dem Primärschlüsselindex, in WAL. Der Ringbuffer brächte den Vorsprung eines halben Flushintervalls und kostete eine Komponente, ein Lock, eine Konfigoption, eine `live_since`-API und eine ungeklärte Eigentümerfrage. **Der Live-Pfad benutzt damit dieselbe Provider-Schnittstelle wie die Historie — eine Abstraktion weniger, nicht mehr.** Zusatznutzen: Die Live-Ansicht bleibt auch bei totem Worker nutzbar und zeigt dann schlicht keine neuen Zeilen — was der Wahrheit entspricht. |
| **Zweite Queue** | **entfällt** | Ersetzt durch eine Queue mit Wasserstandsregel (7.1). |
| **`ProviderCapabilities`** | **entfällt** | In V1 existiert genau ein Provider, der jeden Filter beantwortet. **Kein einziger V1-Codepfad läse das Objekt.** Additiv nachrüstbar. |
| **Text-Sink** | **entfällt** | Ein Format, ein Test, ein Fehlerpfad. Text ist aus JSONL in einer Zeile erzeugbar. |
| **Aktive Größenbremse** (`incremental_vacuum`, automatisches Absenken von `max_entries`) | **entfällt** | `retention_days` und `max_entries` decken den Normalfall. `max_db_bytes` bleibt als **reines Health-Warnsignal**. Damit entfällt zugleich die heikle Bedingung, `auto_vacuum` vor der ersten Tabelle setzen zu müssen. |
| **`monotonic_ns`, `host`, `process_id` als Spalten** | **entfallen** | `monotonic_ns` nur im Speicher zur Ordnung vor dem Schreiben; prozessübergreifend bedeutungslos. `host` siehe 10.9. `process_id` gehört in `details` der `client.app.started`-Zeile. |

**Nettoergebnis:** rund zwei Module und vier Konfigfelder weniger — bei
unverändertem Funktionsumfang aus Sicht des Nutzers.

## 11.3 Neu in V1 aufgenommen

| Gegenstand | Begründung |
|---|---|
| **Funktion „Diagnosehistorie löschen"** | Ohne sie ist die Datenschutzoption unvollständig: Wer Transkriptinhalte gespeichert hat und sie loswerden will, hätte keinen Weg. Die Transkript-Historie hat mit `clear_entries()` bereits ein Vorbild. Umfang: eine Schaltfläche im Logging-Tab, `DELETE FROM logs` plus `PRAGMA wal_checkpoint(TRUNCATE)`. **Die Funktion liegt am Store, nicht am Query-Provider** — der Query-Layer bleibt ausschließlich lesend (O-14). |
| **Beobachtungspunkt für Protokollfehler** | Siehe Grenze 1 in 8.5. |
| **Zähler `deduplicated`** | Siehe 7.3. |

## 11.4 Nicht mit V1 vermischen

V1 darf **nicht gleichzeitig** die Triggerarchitektur reparieren, den
ActivationMirror bauen, Continuous Streaming einführen, `mode` entfernen, die
Hotkeysemantik ändern, die Feedbacklogik fachlich umbauen oder den
Server-Lifecycle ändern.

Ausnahme: ausschließlich minimale, rein beobachtende Hooks.

> **Wenn Logging einen fachlichen Runtime-Umbau voraussetzt, ist die
> Logging-Architektur zu überprüfen — nicht der Runtime-Code.**

---

# 12. Baseline-Regel für Teil A

Nach `G-OBS-V1 PASS` (OBS-060):

- ein separater Observability-Commit, **nur nach ausdrücklicher Freigabe**;
- kein Cross-Workstream-Mischcommit;
- Baseline-Tag oder -Branch nur, wenn ausdrücklich gewünscht;
- **erst danach** beginnt die Triggerarchitektur-Migration.

Verbindliche Regel für **jedes** Paket in Teil A:

> Die vollständige bestehende Client-Suite bleibt grün, **ohne dass ein
> bestehender Test geändert wird**. Neue Tests dürfen dazukommen. Muss ein
> bestehender Test geändert werden, ist das das Signal, dass das Paket
> fachliches Verhalten ändert — dann anhalten und die Architektur prüfen.
