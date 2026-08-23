# LOGGING_ADVERSARIAL_REVIEW

**Auftrag:** `ARBEITSDATEIEN/Implementierungsdateien/prompts/007_Adversarial Review der Logging-Vorbereitung.md`
**Gegenstand:** die sieben Artefakte aus `analyse_code_integration/` vom selben Tag.
**Vorgehen:** keine neue breite Untersuchung. Gezielte Gegenprüfung der eigenen
Aussagen am Code; sechs Punktabfragen zur Verifikation, sonst Kontextarbeit.
**Regeln:** keine Produktänderung, keine Implementierung.

---

# 1. Executive Verdict

Die Grundarchitektur hält der Gegenprüfung stand. Der Beobachterhook, die
Fan-out-Form, das Failure-Modell und die Dedupe-Strategie sind richtig gewählt.

Aber die Prüfung hat **vier echte Defekte** gefunden, die bei einer
Implementierung nach dem heutigen Plan zu Fehlverhalten geführt hätten, sowie
**zwei erhebliche Vereinfachungen**, die den Umfang von V1 spürbar senken.

**Die vier Defekte:**

| # | Defekt | Wirkung ohne Korrektur |
|---|---|---|
| **D-1** | `EventProtocolResult.payload` ist `MappingProxyType`; `json.dumps(..., default=str)` serialisiert es **nicht** als Objekt, sondern als Python-`repr` in **einen String** | Der gesamte Rohpayload landet als `"mappingproxy({...})"` in `raw_json`. Feldbasierte Redaction greift nicht mehr, die Detailansicht ist unbrauchbar, und ein späterer Parser bekommt kein JSON |
| **D-2** | Eine **read-only** SQLite-Verbindung (`mode=ro`) auf eine **WAL**-Datenbank ist nicht allgemein möglich — der öffnende Prozess braucht Schreibrechte auf die `-shm`-Datei | Der Query-Layer würde beim Öffnen scheitern; die Logansicht bliebe leer |
| **D-3** | Der Beobachter läuft **inline auf dem Core-asyncio-Loop**, der auch Audioversand und STT-Session trägt. Redaction plus Serialisierung eines bis zu 1 MiB großen `raw`-Payloads würde dort stattfinden | Latenzkopplung genau in dem Pfad, den das Beobachterprinzip schützen soll |
| **D-4** | Die SQLite-Verbindung darf **nicht** in `manager.start()` erzeugt werden, sondern nur im Worker-Thread selbst (`check_same_thread` bleibt Standard) | `sqlite3.ProgrammingError` beim ersten Batch |

**Die zwei Vereinfachungen:**

| # | Vereinfachung | Ersparnis |
|---|---|---|
| **S-1** | Der **Memory-Ringbuffer entfällt in V1**. Live-Ansicht als tailende Abfrage `WHERE id > :last ORDER BY id LIMIT n` alle 250 ms | Eine Komponente, eine Konfigoption, eine Lock-Diskussion, ein Eigentümerstreit (Ingress vs. Worker) — alles weg |
| **S-2** | **Zwei Queues werden zu einer** mit Wasserstandsregel: oberhalb 75 % Füllstand werden Records unterhalb WARNING verworfen | Kein `get_nowait` aus dem Producer-Thread in eine fremde Queue, kein Zweiqueue-Buchhaltung, kein Prioritätsvergleich |

Zusätzlich: **`ProviderCapabilities` ist für V1 nachweislich YAGNI** und
**`OD-02` ist nicht blockierend** — ich hatte es zu streng eingestuft.

Damit gilt: die Vorbereitung ist inhaltlich richtig, aber die
Ergebnisdokumente sind **noch nicht implementierungsreif**, solange D-1 bis D-4
nicht eingearbeitet sind.

---

# 2. Architecture Risks

## AR-1 — Hookwahl `DualSessionCoordinator`

```text
Annahme       Der Coordinator-Hook sieht JEDES /ws/logs-Frame.
Gegenargument Nein. Frames, die die Protokollvalidierung nicht bestehen,
              erreichen `_dispatch` nie.
Codebeleg     `event_stream.py:266-268` ruft `processor.process_frame(frame)`;
              jeder Verstoss wirft `EventProtocolError`, propagiert aus
              `_run_live`/`_run_handshake`/`_run_replay` nach `_connect_once`
              und wird in `run()` nur als `logger.warning("Event stream attempt
              failed: %s")` (`:128`) sichtbar. Das Rohframe ist verloren.
Urteil        NEEDS REFINEMENT.
```

**Korrektur.** Die Aussage im Audit §2.4 („JEDES Frame") ist zu stark und muss
lauten: *jedes erfolgreich validierte Ergebnis*. Genau der interessanteste
Diagnosefall — ein Server, der das Protokoll verletzt — bleibt damit ein
unstrukturierter WARNING-Text. **Empfehlung:** in OBS-07 zusätzlich einen
zweiten, sehr kleinen Beobachtungspunkt in `EventStreamTransport.run()` im
`except Exception`-Zweig (`event_stream.py:124-128`) vorsehen, der Typ und
Meldung als `client.eventstream.protocol_error` erfasst — **ohne** das Rohframe
(es liegt dort nicht mehr vor). Kein zusätzlicher Kontrollfluss, eine Zeile.

## AR-2 — Der Beobachter läuft auf dem kritischen Loop → **D-3**

```text
Annahme       Ein synchroner, nicht blockierender Beobachter ist unschaedlich.
Gegenargument "Nicht blockierend" heisst nicht "ohne Laufzeit". Der Aufruf
              liegt inline auf dem asyncio-Loop des Threads
              RealtimeSTT-AsyncCore, auf dem auch `_audio_sender` und
              `session.run()` laufen. Redaction plus JSON-Serialisierung eines
              Payloads bis `max_message_size` = 1 MiB (`config.py:189`) findet
              dort statt und verdoppelt zudem kurzzeitig den Speicher.
Codebeleg     `controller.py:2667` (`_audio_sender` als Task desselben Loops),
              `session_coordinator.py:241-245` (Eventstream-Task desselben
              Loops), `config.py:189`.
Urteil        RISKY -> mit Korrektur ROBUST.
```

**Korrektur (dreiteilig).**

1. **`raw` wird im Producer nicht kopiert und nicht serialisiert.** Der
   Ingress nimmt die bereits eingefrorene Mapping-Referenz entgegen. Die
   Umwandlung in JSON geschieht **im Worker**.
2. **Die Producer-Redaction gilt nur für Records, die der Client selbst baut.**
   Für Serverpayloads ist sie nicht nötig: der Server entfernt Credentials,
   Authorization, Cookies, Querystrings und Binärfelder **vor jedem Sink**
   (`docs/structured-logging.md:66-68`), also auch vor `/ws/logs`. Verbleibt
   allein die Transkriptinhaltsregel — eine Datenschutzrichtlinie, kein
   Geheimnisleck, und im Worker genauso wirksam.
   Die Regel **R-2** aus dem Audit („kein unredigierter Record je in der Queue")
   wird damit präzisiert zu: *kein Record, den der Client selbst gebaut hat*.
   Der `hello`-Payload wird davon nicht berührt, weil er nach Regel R-6 nie
   `raw` wird.
3. **Harte Größengrenze für `raw`:** oberhalb 64 KiB wird der Payload nicht
   gespeichert, sondern durch `{"_truncated": true, "_bytes": n}` ersetzt.
   Begründung: ein 1-MiB-Event ist ein Serverdefekt, kein Diagnosefall.

## AR-3 — Injektion des Ingress in den Controller

```text
Annahme       Konstruktorinjektion in STTController ist unproblematisch.
Gegenargument Der Weg dorthin fuehrt ueber CoreBridge, und dessen Factory ist
              einstellig: `ControllerFactory = Callable[[AppConfig],
              STTController]` und wird als `self._controller_factory(self.config)`
              aufgerufen. Ein bestehender Test uebergibt eine eigene Factory.
              Eine Signaturaenderung wuerde diesen Test brechen -- und damit die
              eigene Regel "kein bestehender Test wird geaendert".
Codebeleg     `ui/core_bridge.py:20`, `:45`, `:97`;
              `tests/test_core_bridge.py:192` (`controller_factory=FakeController`).
Urteil        NEEDS REFINEMENT (Plan war an dieser Stelle unbestimmt).
```

**Korrektur, verbindlich für OBS-05/OBS-08:**

```python
# core/controller.py
def __init__(self, config, ..., observability: ObservabilityIngress = NULL_INGRESS):
    self.observability = observability
    ...
    self.session_coordinator.on_observation = observability.observe_server_result

# ui/core_bridge.py
def __init__(self, config, controller_factory=None, parent=None,
             observability: ObservabilityIngress = NULL_INGRESS):
    self._observability = observability
    self._controller_factory = controller_factory or (
        lambda cfg: STTController(cfg, observability=observability)
    )
```

Eine von außen übergebene Factory bleibt einstellig und bekommt schlicht
`NULL_INGRESS` — der bestehende Test läuft unverändert.

## AR-4 — Qt-Grenze

```text
Annahme       Der Core ist frei von Qt, die Invariante ist ohne Umbau haltbar.
Gegenargument keines gefunden.
Codebeleg     `grep -rn "PySide6|QtCore|QObject" core/` -> kein Treffer.
Urteil        ROBUST.
```

## AR-5 — Startreihenfolge → **innerer Widerspruch des Plans**

```text
Annahme       (Plan OBS-06) "ObservabilityManager vor setup_logging bauen und
              starten, damit auch AppConfig.load-Meldungen erfasst werden".
Gegenargument Unmoeglich. Der Manager braucht `config.logging.observability`,
              und die entsteht erst durch `AppConfig.load()`. Der Plan
              widerspricht sich im selben Absatz, in dem er auch feststellt,
              dass die Ladefehler ohnehin verloren gehen.
Codebeleg     `app.py:147-148`.
Urteil        WRONG -- Textdefekt, keine Architekturfrage.
```

**Korrektur.** Reihenfolge verbindlich:
`AppConfig.load()` → Manager bauen und starten → `setup_logging(..., observability=manager)`.
Meldungen aus `AppConfig.load` bleiben verloren, wie heute. Ein Konfigfehler
ist ohnehin über `stderr` und die spätere `client.log` sichtbar.

## AR-6 — Lebensdauer des Managers gehört nicht in `DesktopApplication`

```text
Annahme       manager.stop() als letzter Schritt in DesktopApplication.shutdown().
Gegenargument Es gibt vier Wege, auf denen run_gui zurueckkehrt, OHNE dass eine
              DesktopApplication existiert oder ihr shutdown laeuft:
              Instanzsperre (`:675-683`), fehlendes Tray (`:699-702`),
              LedConfigurationError (`:705-712`), UI-Initialisierungsfehler
              (`:713-716`). Genau diese Startabbrueche sind die Faelle, deren
              Diagnose am wichtigsten waere -- und ihre Records blieben in der
              Queue eines Daemon-Threads liegen. Der Headless-Pfad ruft
              DesktopApplication.shutdown ueberhaupt nie.
Codebeleg     `ui/application.py:666-731`, `app.py:104-123`.
Urteil        RISKY.
```

**Korrektur.** Der Manager wird in `app.py::main()` erzeugt und in einem
`try/finally` gestoppt. `DesktopApplication` bekommt ihn übergeben und stoppt
ihn **nicht**. Damit gilt für jeden Rückkehrweg: Flush passiert.

## AR-7 — Fan-out-Form

```text
Annahme       Serverevent -> {Feedback, Logging} ist ein echtes Fan-out.
Gegenargument Formal ja, zeitlich nein: der Beobachter laeuft VOR dem
              Feedbackzweig auf demselben Thread. Ein langsamer Beobachter
              verzoegert das Feedback.
Codebeleg     vorgeschlagene Platzierung als erste Anweisung in `_handle_event`.
Urteil        NEEDS REFINEMENT -- durch AR-2 entschaerft, aber die Grenze muss
              benannt werden: das Beobachterprinzip garantiert
              Verhaltensgleichheit, NICHT Latenzgleichheit. Genau deshalb ist
              der Test F-9 ("Beobachter blockiert 2 s") kein Kuriosum, sondern
              die Dokumentation dieser Grenze.
```

## AR-8 — Verschluckte Ausnahmen im Coordinator

```text
Annahme       `except Exception: pass` im Coordinator ist ausreichend.
Gegenargument Ein dort verschluckter Fehler ist unsichtbar -- kein Zaehler,
              keine Meldung. Ausgerechnet die Failure-Domain haette dann eine
              blinde Stelle. Zudem darf es NICHT `BaseException` fangen:
              `asyncio.CancelledError` ist seit 3.8 BaseException, und sie zu
              verschlucken wuerde das Abbrechen des Eventstream-Tasks brechen
              (`event_stream.py:139-142`, `session_coordinator.py:425-437`).
Urteil        NEEDS REFINEMENT.
```

**Korrektur.** Zwei Ebenen: `ServerLiveAdapter.observe()` fängt selbst und meldet
an `LoggingInternalHealth`; das `except Exception` im Coordinator ist nur die
letzte Sicherung und bleibt bewusst leer. `BaseException` wird nirgends gefangen.

---

# 3. Overengineering / YAGNI

| Gegenstand | Urteil | Begründung |
|---|---|---|
| `Normalizer` | **KEEP NOW** | Drei Eingangsformen, ein Modell. Ohne ihn steht die Umwandlung in drei Adaptern doppelt. |
| `Ingress` | **KEEP NOW** | Thread-sichere Grenze **und** die injizierbare Naht, die jeden Isolationstest erst möglich macht. |
| `Worker` | **KEEP NOW** | I/O muss von sechs Producer-Threads weg. |
| `Manager` | **KEEP NOW, aber deckeln** | Reine Kompositionswurzel plus `start/stop/apply_config`. Verbindliche Obergrenze: keine Entscheidungslogik, keine Formatierung, keine Filter. Wächst er, ist er die nächste Monolithdatei. |
| **Memory-Ringbuffer** | **DEFER ENTIRELY** → **S-1** | Die Live-Ansicht ist auch ohne ihn erfüllbar: `SELECT ... WHERE id > :last ORDER BY id LIMIT 500` alle 250 ms, auf dem Primärschlüsselindex, in WAL. Der Ringbuffer bringt nur den Vorsprung eines halben Flushintervalls und kostet: eine Komponente, ein Lock, eine Konfigoption (`live_buffer_size`), eine `live_since`-API und die ungeklärte Eigentümerfrage aus Concurrency §10.4. Zielbild §17 nennt als Zweck „geringe DB-Leselast" — eine indizierte Tailabfrage alle 250 ms ist keine Last. |
| **Zwei Queues** | **REMOVE, ersetzen** → **S-2** | Eine bounded Queue plus Wasserstandsregel: ab 75 % Füllstand nimmt der Ingress nur noch Records ab WARNING, ab Channel `audit` oder mit gesetztem `type` an. Das erreicht dasselbe Ziel („DEBUG/PERFORMANCE zuerst droppen", Zielbild §20) ohne den Fremdgriff `low.get_nowait()` aus dem Producer-Thread und ohne doppelte Buchführung. |
| **`ProviderCapabilities`** | **DEFER ENTIRELY** | In V1 existiert genau ein Provider, der jeden Filter beantwortet. Kein einziger V1-Codepfad liest das Objekt. Es ist additiv nachrüstbar, weil `ProviderStatus` eine frozen dataclass mit Defaults ist. Die Frage des Auftrags — „braucht V1 bereits Provider-Capabilities?" — ist mit **nein** zu beantworten. |
| `ProviderStatus` (nur `state` + `detail`) | **KEEP NOW** | Die UI muss „Store nicht verfügbar" anzeigen können. |
| `LogQueryService` als Registry | **DESIGN FOR LATER, minimal** | 20 Zeilen. Ohne sie müsste später jeder Aufrufer um einen ersten Positionsparameter erweitert werden. |
| `fetch_raw` | **KEEP NOW** | Die Detailansicht braucht es, und es hält `raw_json` aus der Listenabfrage heraus. |
| **Zweiter Datei-Sink (Text)** | **DEFER ENTIRELY** | Bestätigt (OD-06). Nur JSONL. |
| `sinks/base.py` als Protokoll | **KEEP NOW** | Zwei Zeilen; die Fehlerisolation des Worker-Codes wird dadurch einheitlich. |
| `storage/base.py` als Protokoll | **KEEP NOW** | Ermöglicht den Fake-Store in den Worker-Tests, ohne den echten zu instanziieren. |
| `scope`-Spalte | **KEEP NOW** | Nicht ableitbar (Serverrecord ohne Session = global, Clientrecord ohne Session = instance). |
| `server_cursor`-Spalte | **KEEP NOW** | Einzige retentionsfeste Serverordnung. |
| `redaction.py` als eigenes Modul | **KEEP NOW** | Sicherheitsrelevant und einzeln testbar. |
| `core/server_control/` | **DEFER ENTIRELY** | Bestätigt. |
| `adapters/led.py` | **DEFER ENTIRELY** | Bestätigt: LEFX ist in-process. |
| `max_db_bytes` + `incremental_vacuum` | **DESIGN FOR LATER** | `retention_days` und `max_entries` decken den Normalfall. Die Größenbremse ist ein dritter Mechanismus für einen Fall, den die ersten beiden bereits verhindern. Empfehlung: Feld in der Konfiguration vorsehen, Wirkung auf ein reines **Health-Warnsignal** reduzieren, kein automatisches Absenken von `max_entries` und kein `incremental_vacuum` in V1. |
| `process_id`, `host` | **REMOVE** (bestätigt) | – |

**Netto-Ergebnis der Minimalismusprüfung:** V1 verliert den Ringbuffer, eine
Queue, `ProviderCapabilities`, den Text-Sink und die aktive Größenbremse.
Das sind rund **zwei Module und vier Konfigfelder weniger** — bei unverändertem
Funktionsumfang aus Sicht des Nutzers.

---

# 4. Future Compatibility

| Erweiterung | Schnittstelle ausreichend? | späterer Umbau nötig? |
|---|---|---|
| **ServerHistoryProvider** | **JA** | Nur additiv: `LogProvider` implementieren, `ProviderCapabilities` **dann** einführen, `historyPath` in `_build_access` übernehmen (`session_coordinator.py:286-306` verwirft es heute). Der opake String-Cursor trägt sowohl die lokale `id` als auch `nextCursor` des Servers. |
| **globale Serverlogs** | **TEILWEISE** | `scope="global"` ist im Modell vorgesehen. Aber: `QueryFilter` hat kein Feld, das „alle Sessions" ausdrückt — heute ergibt `session_id=None` implizit „ohne Einschränkung", was für den lokalen Store richtig und für einen Adminprovider mehrdeutig ist. **Empfehlung:** `scopes: tuple[str, ...]` bleibt das Ausdrucksmittel; ausdrücklich dokumentieren, dass `scopes=("global",)` die Adminabfrage bedeutet. Kein Umbau, nur eine Festlegung. |
| **Admin-Auth / Capabilities** | **JA** | `ProviderState.AUTH_REQUIRED` existiert von Anfang an. Der LoggingCore importiert nichts aus `server_control`. |
| **serverweite Config** | **JA** | Berührt das Logging nicht; eigener Dienst, eigener Settingsbereich. |
| **LED Controller** | **JA** | Solange in-process: eine Normalizer-Regel. Out-of-process: derselbe Adaptervertrag wie `ServerLiveAdapter`; `producer_kind="led"` existiert. |
| **weitere Produzenten** | **JA** | `producer_kind`/`producer_id`/`instance_id` sind offene TEXT-Felder; der Dedupe-Index ist bereits auf `(producer_id, event_id)` und nicht auf `event_id` allein geschlüsselt — genau für diesen Fall. |
| **mehrere Serverinstanzen** | **JA** | `instance_id` je Record; `server_cursor` darf laut Schema §7.3 nie ohne `instance_id` verglichen werden. |
| **mehrere Clientinstanzen** | **TEILWEISE → NEIN, ehrlich betrachtet** | Der `SingleInstanceGuard` (`ui/single_instance.py`) verhindert eine zweite Instanz auf derselben Maschine, also stellt sich die Frage heute nicht. Aber: **zwei Instanzen auf ZWEI Maschinen, die dieselbe Historie sehen wollen**, brauchen einen Collector — und dann fehlt genau `host`, das ich bewusst gestrichen habe. Das ist kein Umbau des Cores, aber eine **Migration** (Spalte hinzufügen, Altbestand mit NULL). **Ehrliches Urteil: TEILWEISE**, mit dem Hinweis, dass Zielbild §43 „Multi-Host-Aggregation" ausdrücklich als V4 führt und eine nullable Spalte der billigste denkbare Nachtrag ist. |
| **Export / gespeicherte Filter / Charts** | **JA** | `QueryFilter` ist eine frozen dataclass; Export liest, was die Query liefert. |

---

# 5. Canonical Record Corrections

## 5.1 Was wirklich Kernmodell ist

**Prüfmaßstab:** ein Feld ist Kernmodell, wenn danach **gefiltert oder sortiert**
wird oder wenn es die **Identität** trägt. Alles andere gehört nach `details`.

| Feld | Urteil | Anmerkung |
|---|---|---|
| `record_id`, `received_at`, `producer_kind`, `producer_id`, `instance_id`, `scope`, `channel`, `level`, `replayed` | **Kern, NOT NULL** | unverändert |
| `type`, `component`, `session_id`, `generation`, `segment_id`, `command_id`, `event_id`, `correlation_id`, `server_cursor`, `source_timestamp` | **Kern, nullable** | unverändert |
| `activation_id` | **Kern, nullable, diagnostisch** | siehe 5.3 |
| `transcription_id` | **Kern, nullable** — aber **nicht blockierend** | siehe 5.2 |
| `message`, `details`, `raw` | **Kern-Nutzlast** | `message` bleibt ausdrücklich Darstellung |
| `monotonic_ns`, `host`, `process_id` | **entfällt** (bestätigt) | – |

## 5.2 Korrektur an meiner eigenen Einstufung von `transcription_id`

```text
Annahme       OD-02 blockiert V1, weil es Schema und Migration betrifft.
Gegenargument Genau dafuer existiert der Migrationsmechanismus. Eine nullable
              Spalte spaeter hinzuzufuegen ist ein einzeiliges ALTER TABLE,
              und `transcriptionId` wird in V1 von KEINEM Filter gebraucht --
              lokal deckt session_id + segment_id denselben Zugriff ab. Erst
              der ServerHistoryProvider (V2) kennt es als Query-Parameter.
Urteil        Meine Einstufung war zu streng.
```

**Korrektur.** Empfehlung bleibt „Spalte aufnehmen" (sie kostet nichts und ist
ein indiziertes Feld erster Ordnung des Servers), aber
**OD-02 blockiert V1 NICHT**. Damit bleibt genau **eine** blockierende
Entscheidung: OD-01 (Paketname).

## 5.3 Serverseitig nicht stabile Felder

| Feld | Stabilität | Regel |
|---|---|---|
| `activation_id` | **nicht stabil.** Zum Publikationszeitpunkt frisch aus dem Controller gelesen; fehlt bei geschlossener Activation, ist bei bereits neu geöffneter Activation **falsch** (`LETZTE_ARCHITEKTURKLAERUNGEN_VOR_PLAN_FREEZE.md §1.2`) | speichern, **nie** gruppieren, in der UI mit Hinweis |
| `severity` | offenes Vokabular (`info`/`warning`/`error` beobachtet, `critical` in der Priorisierung vorgesehen) | tolerant abbilden, Original in `details.source_severity` |
| `segment_id` | im Envelope Integer, in der Server-DB als TEXT abgelegt (`event_logging.py:571-575`) | lokal INTEGER, Konvertierung im Normalizer |
| `meldung` | undokumentierter, deutschsprachiger Schlüssel; landet clientseitig in `extra` | ausdrücklich behandeln, kein stiller Verlass darauf |
| `cursor` | stabil je Serverdatenbank, **nicht** über eine neu angelegte Datenbank hinweg | nie ohne `instance_id` vergleichen |
| `event_id` | stabil, uuid4, serverseitig UNIQUE | Dedupe-Schlüssel |

## 5.4 Welche IDs nicht global eindeutig sind

```text
global eindeutig     event_id (uuid4), record_id (uuid4),
                     instance_id (uuid4 je Prozess)
NICHT global         server_cursor  -> nur je (producer_id, instance_id-Reihe
                                       derselben Datenbank)
                     session_id     -> uuid4 hex, faktisch eindeutig, aber
                                       serverseitig je Verbindung neu
                     segment_id     -> nur innerhalb einer Session
                     generation     -> nur innerhalb EINES Clientprozesses
                     command_id     -> `cmd-` + 12 Hexzeichen (uuid4[:12]),
                                       also 48 Bit -- praktisch kollisionsfrei
                                       innerhalb einer Session, NICHT als
                                       globaler Schluessel geeignet
                     activation_id  -> siehe 5.3
```

**Konsequenz:** kein Index und keine Dedupe-Regel darf auf `command_id`,
`segment_id` oder `generation` allein aufbauen.

## 5.5 Die drei Erscheinungsformen eines Serverevents

```text
(1) originaeres Serverevent            lebt in der Server-SQLite,
                                       identifiziert durch event_id
(2) lokal gespeicherte Kopie           lebt in observability.sqlite3,
                                       eigenes record_id, traegt event_id
                                       UND den Empfangszeitpunkt received_at
(3) spaeter remote abgefragtes Event   entsteht NUR im Speicher, als
                                       LogRecordView eines Remote-Providers,
                                       traegt dasselbe event_id, aber
                                       provider_id != "local"

Unterscheidung im Modell:
    (2) hat received_at und ist ueber den lokalen Store abfragbar
    (3) hat provider_id != "local" und wird NIE in den lokalen Store geschrieben
Dieselbe event_id in (2) und (3) ist GEWOLLT und der eigentliche Diagnosewert
(Zielbild §24: "Serverhistorie hat es, Clienthistorie nicht").
```

**Antwort auf die Auftragsfrage** „können lokale und Remote-Records denselben
Event-Identifier tragen?" — **Ja, und das ist die Absicht.** Deshalb darf ein
Remote-Provider **niemals** in den lokalen Store schreiben. Diese Regel fehlte
in meinen Artefakten und wird hiermit nachgetragen:

```text
INVARIANTE  Kein LogProvider schreibt. Der Query-Layer ist ausschliesslich
            lesend. Es gibt genau EINEN Schreibpfad: Ingress -> Worker -> Store.
```

## 5.6 `schema_version`, `sequence`, `provider_record_id`, `record_id`-Geltung

| Frage | Antwort |
|---|---|
| `schema_version` je Zeile? | **Nein.** `PRAGMA user_version` + `schema_meta`. **Ja** je Zeile in der JSONL-Datei, weil sie kontextlos gelesen wird. |
| `sequence`? | **Nein.** `logs.id AUTOINCREMENT` ist die lokale Sequenz. |
| `provider_record_id`? | **Nein als Spalte.** Am DTO genügt `provider_id` + `record_id`. |
| `record_id` lokal oder global? | **Lokal erzeugt, global eindeutig** (uuid4). Es identifiziert *diesen Speichereintrag*, nicht das Ereignis. Das Ereignis identifiziert `event_id`. Die beiden dürfen nie verwechselt werden — deshalb sind es zwei Felder. |

## 5.7 Bereinigtes Minimal-Schema

Gegenüber `LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md §9.1` unverändert in den
Spalten, mit **vier Korrekturen**:

```sql
-- KORREKTUR 1 (D-2): KEIN mode=ro fuer Leser. WAL erlaubt das nicht
--   allgemein -- der oeffnende Prozess braucht Schreibrechte auf die
--   -shm-Datei. Leser oeffnen normal und setzen:
--       PRAGMA query_only = ON;
--   Der Prozess besitzt die Datei ohnehin (eigenes %LOCALAPPDATA%).

-- KORREKTUR 2: auto_vacuum/incremental_vacuum entfaellt in V1 (YAGNI, §3).
--   PRAGMA auto_vacuum bleibt auf dem Standard. Damit entfaellt auch die
--   heikle Bedingung "muss vor der ersten Tabelle gesetzt werden".

-- KORREKTUR 3: Retention nach Anzahl ebenfalls BLOCKWEISE, und die
--   Untergrenze muss gegen NULL gesichert werden (weniger Zeilen als
--   max_entries -> SELECT liefert keine Zeile):
--       SELECT id FROM logs ORDER BY id DESC LIMIT 1 OFFSET :max_entries-1;
--       -- kein Ergebnis  -> nichts zu tun
--       -- Ergebnis :floor -> DELETE FROM logs WHERE id IN (
--                               SELECT id FROM logs WHERE id < :floor
--                               ORDER BY id LIMIT 5000);
--          wiederholen, solange changes() = 5000 und das Zeitbudget reicht

-- KORREKTUR 4: raw_json wird oberhalb 64 KiB durch einen Kuerzungsmarker
--   ersetzt (AR-2).
```

Alles Übrige — Spalten, Nullbarkeit, der partielle UNIQUE-Index und die
sechs Indizes — bleibt bestätigt.

---

# 6. Replay / Dedupe Risks

| Fall | eindeutige Identität? | falsche Dedupe? | doppelte Speicherung? | Regel |
|---|---|---|---|---|
| **Reconnect** (gleiche Instanz, Cursor vorhanden) | ja, `event_id` | nein | nein — Server setzt hinter dem Cursor fort | unverändert |
| **Replay** (nach kurzem Abriss) | ja | nein | nein — `ON CONFLICT DO NOTHING` | unverändert |
| **Server Restart** | ja | nein | **nein, aber:** voller Replay der gesamten Retention. Dedupe greift, die **Kosten** bleiben | Batchschreiben; der Replay läuft mit `replayed=1` und wird über die Wasserstandsregel bei Bedarf zugunsten von HIGH-Records verworfen — Verlust ist hier folgenlos, weil die Daten bereits gespeichert sind |
| **Client Restart** | ja | nein | nein — Cursordatei überlebt, `_confirmed_ids` nicht, aber der DB-Index schon | unverändert |
| **Cursor verloren** (Datei gelöscht/ungültig) | ja | nein | nein | `event_cursor_store.py:69-71` verwirft still → Replay → Index fängt ab |
| **Event doppelt empfangen** innerhalb einer Verbindung | ja | nein | nein — der Processor markiert `duplicate=True` und leitet auf `on_control` | **Korrektur, siehe unten** |
| **lokal gespeichert und später remote abgefragt** | ja, gleiche `event_id` | **Gefahr, wenn ein Provider schriebe** | nein, sofern die Invariante aus §5.5 gilt | **Provider schreiben nie** |
| **gleiche `event_id` aus neuer Serverinstanz** | uuid4 → praktisch unmöglich; möglich nur nach Wiedereinspielen eines DB-Backups | Dedupe würde beide zu einer Zeile verschmelzen | nein | **Bewusst akzeptiert**: es *ist* dasselbe Ereignis. Die gespeicherte `instance_id` ist die des ersten Empfangs — im Kommentar der Migration festhalten |

## RD-1 — Korrektur an meiner eigenen Testerwartung

```text
Annahme       (Plan OBS-07, Test) "Ein Duplikat erzeugt einen Record mit
              replayed=True."
Gegenargument Es erzeugt einen Record, der vom partiellen UNIQUE-Index
              unterdrueckt wird. Gespeichert wird nichts. Die Erwartung ist
              falsch formuliert.
Urteil        Testerwartung korrigieren zu: "Ein Duplikat wird beobachtet,
              normalisiert und an den Store uebergeben; der Store fuegt KEINE
              zweite Zeile ein; der Zaehler `deduplicated` steigt."
```

**Zusatz:** Der Store sollte die Zahl der durch `ON CONFLICT` verworfenen Zeilen
zurückliefern und in der Health als `deduplicated` zählen. Ohne diesen Zähler ist
im Betrieb nicht unterscheidbar, ob ein Replay korrekt dedupliziert oder ob gar
nichts angekommen ist. **Fehlt im bisherigen Health-Modell.**

## RD-2 — Der wirkliche Replay-Kostenfall

Bei `retention_days: 0` (Serverstandard = nie löschen, `structured-logging.md:104-108`)
kann ein Serverneustart die vollständige Serverhistorie als Replay auslösen.
Der Dedupe-Index verhindert doppelte Zeilen, aber jeder Record durchläuft
Normalizer, Queue und einen `INSERT`-Versuch.

**Empfehlung, additiv und billig:** Der `ServerLiveAdapter` fragt vor dem
Normalisieren den Store, ob `event_id` bereits bekannt ist — **nein**, das wäre
ein Lesezugriff je Event auf dem Core-Loop und damit genau das, was AR-2
verbietet. Stattdessen: Der **Worker** prüft vor dem Batch nichts und verlässt
sich auf `ON CONFLICT`; der Schutz gegen die Flut ist die Wasserstandsregel
(S-2), die `replayed=1`-Records ohne `type` als LOW einstuft und im
Überlastfall zuerst verwirft. Das ist verlustfrei, weil die Daten bereits in der
Datenbank stehen.

---

# 7. Failure Domain Findings

| Fall | darf Runtime beeinflussen? | was stattdessen | Health sichtbar |
|---|---|---|---|
| SQLite **locked** | NEIN | `busy_timeout=5000` im **Worker**; danach Batch einmal wiederholen, dann verwerfen. Leser blockieren dank WAL ohnehin nicht | `DEGRADED_STORE` |
| SQLite **disk full** | NEIN | `write_batch` scheitert, Batch verworfen; **Retention wird ausgesetzt** (auch ein `DELETE` braucht Platz im WAL) | `FAILED_STORE` |
| SQLite **corrupt** | NEIN | Store deaktiviert. **Datei wird NIE gelöscht oder umbenannt** | `FAILED_STORE` |
| **JSONL-Pfad ungültig** | NEIN | Sink deaktiviert, einmal an stderr | `DEGRADED_SINK` |
| **File handle error** | NEIN | wie oben | `DEGRADED_SINK` |
| **Queue voll** | NEIN | Wasserstandsregel, dann Verwerfen, Zähler | `DROPPING` |
| **Worker tot** | NEIN | Ingress verwirft und zählt. **Neu:** die Live-Ansicht bleibt nach S-1 trotzdem nutzbar, weil sie direkt aus dem Store liest — sie zeigt dann schlicht keine neuen Zeilen, was der Wahrheit entspricht | `FAILED_WORKER` |
| **Normalizer-Exception** | NEIN | Record verworfen, ein `logging.record_rejected` ohne Originaldaten | Zähler `malformed` |
| **malformed Serverevent** | NEIN | erreicht den Beobachter gar nicht erst (AR-1); sichtbar als `client.eventstream.protocol_error` | Zähler |
| **Event flood** | NEIN | siehe RD-2 | `DROPPING` |
| **UI-Abfrage extrem teuer** | NEIN | eigener Query-Thread; Qt-Thread und Core-Loop unberührt. **Neu:** `PRAGMA query_only=ON` verhindert zusätzlich, dass eine fehlerhafte Abfrage je schreibt | Statuszeile |
| **Shutdown während Flush** | NEIN | hartes Zeitbudget 2 s, danach `dropped_shutdown` | stderr |

## FD-1 — Versteckte Blockierstellen, die ich zuerst übersehen hatte

| # | Stelle | Risiko | Gegenmaßnahme |
|---|---|---|---|
| **FD-1a** | `logging.shutdown()` läuft über `atexit` und ruft `flush()`+`close()` auf **jedem** Handler. Zu diesem Zeitpunkt kann der Daemon-Worker bereits eingefroren sein | Ein `close()`, das auf den Worker wartet, wäre ein Deadlock beim Prozessende | `UnifiedLogHandler.flush()` und `.close()` sind **No-Ops**. Der Flush geschieht ausschließlich über `manager.stop()` in `app.py::main()` |
| **FD-1b** | `queue.Queue.put_nowait` nimmt einen Mutex. Aus dem PortAudio-Callback wäre das grenzwertig | Der Callback loggt heute drei DEBUG-Zeilen | HOT-PATH-Regel bleibt: dort **nur** Integer-Inkremente, kein `submit`. Verifiziert durch die Quelltextprüfung in OBS-08 |
| **FD-1c** | Redaction eines tiefen `details` im Producer-Thread | Der Qt-Thread ist ein Producer (`_log_feedback_decision`) | Tiefengrenze 16 **und** eine Knotengrenze (z. B. 500 Elemente); darüber wird abgeschnitten und markiert |
| **FD-1d** | `LoggingInternalHealth` schreibt nach `stderr`; in einem PyInstaller-GUI-Build ist `sys.stderr` `None` **oder** eine nicht gelesene Pipe, die volllaufen kann | Ein blockierender `write` auf eine volle Pipe hinge den meldenden Thread auf | `sys.stderr is None` abfangen (war schon geplant) **und zusätzlich** die Ratenbegrenzung als harte Obergrenze verstehen: höchstens eine Zeile je Code und 60 s, unabhängig von der Fehlerzahl |
| **FD-1e** | Der Query-Thread hält eine Verbindung offen, während der Worker Retention fährt | Mit WAL kein Konflikt; ohne WAL wäre es einer | WAL ist gesetzt; der Test U-4.9 deckt es ab |

## FD-2 — Fehlender Zähler

`deduplicated` fehlt (RD-1). Ergänzen in `LoggingHealthSnapshot`.

---

# 8. Hot Path Findings

| Hook | sicher? | nur enqueue? | Aggregation? | Sampling? | nicht loggen? |
|---|---|---|---|---|---|
| **Audio callback** (`audio_capture.py:237-260`, PortAudio-Thread) | nur mit Regel | **nein — gar kein enqueue** | **ja**, Zähler + 5-s-Aggregat vom Worker gelesen | – | Einzelchunks: **nicht loggen** |
| **Audio process loop** (`audio_capture.py:266-295`) | dito | nein | ja | – | dito |
| **Audio sender** (`controller.py:2572-2593`) | dito | nein | ja (`packets_sent`, `bytes_sent`, `max_queue_depth`) | – | Sendefehler: heute DEBUG mit `exc_info`; bleibt DEBUG und wird vom Handlerlevel (INFO) gefiltert, **bevor** `emit` läuft (`Logger.callHandlers` prüft `record.levelno >= hdlr.level`) |
| **WebSocket receive** (`stt_session.py:1126-1154`) | ja | ja, ein `submit` je Event | nein | **ja für `realtime`** | `realtime`-Events erzeugen **keinen** strukturierten Record; der bestehende DEBUG-Log bleibt und wird gefiltert |
| **Eventstream receive** (Beobachterhook) | **nur nach AR-2** | ja — aber die Kosten liegen in Redaction/Serialisierung | nein | nein | `raw` > 64 KiB: gekürzt |
| **Feedback dispatch** (`ui/application.py:232-299`, **Qt-Thread**) | ja | ja | nein | nein | Replay-Decisions erreichen die Stelle gar nicht (`:236-237` kehrt vorher zurück) — das begrenzt die Burstgefahr erheblich. Der vorhandene `_log_feedback_decision` baut bereits eine verschachtelte Struktur; er bleibt unverändert und wird nur zusätzlich erfasst |
| **Qt main thread allgemein** (Hotkey, Kommandos, Settings) | ja | ja | nein | nein | Nutzeraktionen sind selten; Tiefen-/Knotengrenze der Redaction schützt (FD-1c) |
| **LED-Worker** (`lefx.*`-Logger) | ja | ja | nein | nein | LEFX loggt sparsam und entprellt bereits (`led_feedback.py:433-449`) |
| **Injection-Worker** | ja | ja | nein | nein | – |

## HP-1 — Präzisierung, die im Audit fehlte

`root_logger.setLevel(logging.DEBUG)` (`logging_setup.py:74`) bedeutet, dass
`logger.debug(...)` den `LogRecord` **immer erzeugt** — auch heute schon. Neu ist
nur, dass ein weiterer Handler in der Kette steht. Weil `Logger.callHandlers`
je Handler `record.levelno >= hdlr.level` prüft, wird `UnifiedLogHandler.emit`
für DEBUG-Records bei Handlerlevel INFO **nicht** aufgerufen. Es entsteht also
**kein** zusätzlicher Aufwand — aber auch **keine** Ersparnis gegenüber heute.
Die Aussage im Audit („Handler-Default darf nie DEBUG sein") ist richtig, die
Begründung war unvollständig.

## HP-2 — Doppelte Levelfilterung

Handler-Level und Ingress-Level filtern beide. **Festlegung:** der
Handler-Level gilt für Python-Logs, der Ingress-Level für strukturierte
Clientevents und Serverevents. Ein Wert in der Konfiguration
(`logging.observability.level`) speist beide. Ohne diese Festlegung hätte ein
Coding-Agent zwei plausible Deutungen.

---

# 9. Security / Privacy Findings

## SP-1 — Aktive Einschleusversuche und ihr Ergebnis

| Angriff | Ergebnis | Beleg |
|---|---|---|
| Token über **`hello`** | **würde durchkommen** ohne die Whitelist (OD-07). Mit Whitelist blockiert | `controller.py:1710-1730`, `stt_session.py:1313` |
| Token über **`repr()` eines Access-Objekts** | blockiert: `EventStreamAccess.access_token` hat `repr=False`, `SessionContext.log_access` hat `repr=False`, `HotkeyConfig.key` hat `repr=False` | `event_protocol.py:58`, `session_coordinator.py:40`, `config.py:508` |
| Token über **`record.args`** | blockiert durch Regel R-4: `args` werden nie gespeichert | – |
| Token über **Exception mit URL** | **kein Weg gefunden.** `/ws/logs` ist queryfrei erzwungen (`event_cursor_store.py:32-33`); der Token wird in-band im ersten Frame gesendet (`event_stream.py:209-211`), nicht in der URL | – |
| Konfiguration über **`%r` einer Dataclass** | **offen.** `AppConfig` und Untermodelle haben Standard-`repr`. Heute existiert kein solcher Aufruf, aber nichts verhindert ihn künftig | – |
| **WebSocket-URL mit Query** | `stt_session.py:987` loggt `target_url` inklusive Wake Words und Sensitivitäten | Regel: Query aus jeder URL entfernen |
| **Transkripttext** | steht heute bereits auf INFO und bei Konflikten vollständig auf WARNING im Log | `stt_session.py:1296-1300`, `controller.py:2077-2080`, `:2145-2148` |
| **Stack Traces** | enthalten Dateipfade mit dem Windows-Benutzernamen | Pfadkürzung auf `~` |
| **Raw Payload** | serverseitig bereits saniert (`structured-logging.md:66-68`) | zusätzlich clientseitige Transkriptregel |
| **Audioinhalt** | kein Weg gefunden; nur Byte- und Framezahlen werden geloggt | – |
| **Fenstertitel der Zielanwendung** | nicht vorhanden; `text_injector` loggt nur `HWND` | Regel, damit es so bleibt |

## SP-2 — Zwei neue Befunde

**SP-2a (aus D-1 folgend, sicherheitsrelevant).** Wenn `raw` durch
`json.dumps(..., default=str)` in einen einzigen String kollabiert, ist die
feldbasierte Redaction **wirkungslos** — sie greift auf Schlüsselnamen, und es
gibt dann keine Schlüssel mehr. Ein Payload, der wider Erwarten doch ein
Geheimnis enthielte, käme ungefiltert in die Datenbank. D-1 ist damit nicht nur
ein Formatfehler, sondern auch ein Sicherheitsbefund.

**SP-2b.** Der V1-Abgrenzungsentwurf verlangt in §8 ausdrücklich
„DB-Dateirechte geprüft" und „File-Sink-Dateirechte geprüft". Meine Artefakte
haben diesen Punkt **vollständig übergangen**. Nachtrag:

```text
Regel P-8  Store und Sinks liegen unterhalb von %LOCALAPPDATA%\RealtimeSTT
           Client\ und erben damit die Benutzer-ACL. Es wird KEIN eigenes
           Verzeichnis mit abweichenden Rechten angelegt, KEIN Pfad ausserhalb
           des Benutzerprofils akzeptiert, und ein konfigurierter absoluter
           Pfad wird gegen das Benutzerprofil geprueft (Vorbild:
           `EventStreamConfig.validate` verlangt bereits einen absoluten Pfad,
           `config.py:244-245`).
Regel P-9  Beim Anlegen wird geprueft, dass die -wal- und -shm-Geschwister
           im selben Verzeichnis entstehen. Sie enthalten Nutzdaten und
           gehoeren derselben Zugriffskontrolle.
Test M-11  Nach dem ersten Start werden die effektiven Rechte der Datei
           protokolliert (`icacls`), einmalig, als Abnahmebeleg.
```

**SP-2c (Lücke, kein Defekt).** Es gibt keine Funktion „lokale Logs löschen".
Die Transkripthistorie hat `clear_entries()` (`history.py:623`); der neue Store
hätte nichts Vergleichbares. Der V1-Scope verlangt es nicht — aber ein Nutzer,
der Transkriptinhalte gespeichert hat und sie loswerden will, hat keinen Weg.
**Empfehlung:** eine Schaltfläche „Diagnosehistorie löschen" im Logging-Tab,
zehn Zeilen, `DELETE FROM logs` plus `PRAGMA wal_checkpoint(TRUNCATE)`.
Als **KEEP NOW** eingestuft, weil sie die Datenschutzoption erst vollständig
macht.

## SP-3 — Konsolidierte Redaction-Regeln

```text
R-1  Kein Admin-Key, kein Token, kein Auth-Objekt im LoggingCore.
R-2  (praezisiert, AR-2) Redaction im Producer-Thread fuer Records, die der
     CLIENT selbst baut. Fuer serverseitige `raw`-Payloads im Worker,
     weil der Server bereits saniert hat.
R-3  Schluesselregel, nicht Werteheuristik. Case-insensitiv, ohne `_`/`-`:
     authorization, token, accesstoken, apikey, adminkey, password, secret,
     cookie, credential.
R-4  Kein `record.args`, kein `locals()`, kein Objekt-`repr()`.
     Exception nur als `formatException`-Text.
R-5  Ausgehende Frames (`_send_json`, `subscribe_payload`) nie roh.
R-6  `store_raw_payload` gilt nur fuer EINGEHENDE Serverevents.
     `hello` wird nie `raw`, sondern nur ueber eine Whitelist erfasst.
R-7  Store und Sinks im Benutzerprofil. (Neu: siehe P-8/P-9.)
R-8  Jede URL verliert Query und Fragment vor der Speicherung.
R-9  Benutzerprofilpfade werden auf `~` gekuerzt -- auch in Tracebacks.
R-10 Transkriptfelder nach `store_transcription_content`; Zeichenzahl bleibt.
     Gilt AUCH fuer unstrukturierte Logtexte, nicht nur fuer Serverevents.
R-11 (neu) `raw` wird als JSON-Objekt gespeichert oder gar nicht.
     Ein `default=str`-Rueckfall auf Objektebene ist VERBOTEN, weil er die
     Schluesselregel aushebelt (SP-2a). Der Rueckfall gilt nur je Blattwert.
R-12 (neu) Tiefengrenze 16, Knotengrenze 500. Darueber abschneiden und
     markieren.
```

---

# 10. Implementation Plan Corrections

| Paket | Status | Erforderliche Änderung |
|---|---|---|
| **OBS-00** | **NEEDS CHANGE** | (a) `unfreeze()`-Helfer aufnehmen, der `MappingProxyType`/Tupel rekursiv in `dict`/`list` überführt — **D-1**. (b) `redact` bekommt Tiefen- **und** Knotengrenze (R-12). (c) Die `LOGGER_CHANNEL_MAP` im Audit §6.2 enthält einen **unaufgelösten Gedanken im Fließtext** („-> performance? NEIN -> system"). Ein Coding-Agent hätte dort echten Interpretationsspielraum. **Verbindliche Fassung: alle nicht ausdrücklich genannten Logger → `system`; nur `text` → `transcription`.** Keine Zuordnung nach `performance` aus Loggernamen; `performance` entsteht ausschließlich aus strukturierten Aggregatevents |
| **OBS-01** | **NEEDS CHANGE** | `from_server_result` nutzt `unfreeze()` für `raw` und `details`; Größengrenze 64 KiB; `segment_id`-Konvertierung ausdrücklich |
| **OBS-02** | **NEEDS CHANGE** | Zähler `deduplicated` ergänzen (FD-2); Ratenbegrenzung als **harte** Obergrenze formulieren (FD-1d) |
| **OBS-03** | **NEEDS CHANGE** | Von zwei Queues auf **eine mit Wasserstandsregel** (S-2). Ringbuffer **entfällt** (S-1). Akzeptanzkriterium „100.000 submit < 1,0 s" umformulieren zu „messen, im Protokoll festschreiben, künftig als Regressionsgrenze verwenden" — ein absoluter Zeitwert ist auf fremder Hardware kein Kriterium |
| **OBS-04** | **NEEDS CHANGE** | (a) Verbindung wird **im Worker-Thread** erzeugt, nicht in `start()` — **D-4**. (b) Leser mit `PRAGMA query_only=ON` statt `mode=ro` — **D-2**. (c) `auto_vacuum`/`incremental_vacuum` streichen. (d) Retention nach Anzahl blockweise und NULL-gesichert. (e) `write_batch` liefert `(eingefuegt, dedupliziert)` |
| **OBS-05** | **NEEDS CHANGE** | Manager-Lebensdauer nach `app.py::main()` verlagern (AR-6); Startreihenfolge korrigieren (AR-5); Injektionsweg über die Default-Factory festschreiben (AR-3) |
| **OBS-06** | **NEEDS CHANGE** | `flush()`/`close()` des Handlers als No-Op festschreiben (FD-1a); Levelzuständigkeit klären (HP-2) |
| **OBS-07** | **NEEDS CHANGE** | (a) `except Exception`, **nie** `BaseException`, mit Begründung (AR-8). (b) Adapter meldet selbst an Health. (c) Zusätzlicher kleiner Beobachtungspunkt für Protokollfehler (AR-1). (d) Testerwartung für Duplikate korrigieren (RD-1). (e) Redaction/Serialisierung von `raw` in den Worker (AR-2) |
| **OBS-08** | **READY** nach Übernahme von AR-3 | Der Plan verweist auf die Hooktabelle des Audits — das ist eine ausreichend eindeutige Liste. Ergänzen: die Aggregatrecords werden vom Worker erzeugt, der die Zähler **liest**; die Zählerattribute selbst sind einfache Ints ohne Lock (ein verlorenes Inkrement ist folgenlos, ein Lock im Audiocallback nicht) |
| **OBS-09** | **NEEDS CHANGE** | `ProviderCapabilities` streichen (§3); Invariante „Provider schreiben nie" aufnehmen (§5.5); `query_only`-Verbindung |
| **OBS-10** | **NEEDS CHANGE** | `live_buffer_size` entfällt (S-1); `queue_low_size`/`queue_high_size` werden zu `queue_size` (S-2); `max_db_bytes` wird reines Warnsignal (§3); Löschfunktion ergänzen (SP-2c) |
| **OBS-11** | **NEEDS CHANGE** | Live-Modus als tailende Store-Abfrage statt Ringbuffer (S-1). Damit entfällt `Ingress.live_since` komplett und der Live-Pfad benutzt dieselbe Provider-Schnittstelle wie die Historie — **eine Abstraktion weniger, nicht mehr** |
| **OBS-12** | **READY** | unverändert; abhängig von OD-06 |
| **OBS-13** | **NEEDS CHANGE** | Ergänzen: Dateirechte-Beleg (SP-2b, Test M-11) und **Mutationstests** (unten) |

## IP-1 — Fehlende Mutationstests

Der Auftrag fragt danach, und das Projekt hat die Praxis bereits etabliert:
`evidence/` enthält `ap2_mutation_check.txt`, `ap4_mutation_check.txt`,
`r1_collision_mutation.txt` und weitere. Meine Testmatrix hatte **keinen
einzigen** Mutationscheck. Nachtrag, minimal und aussagekräftig:

| Mutation | Test muss rot werden |
|---|---|
| `ON CONFLICT DO NOTHING` → einfaches `INSERT` | U-3.1, U-3.6, M-5 |
| `except Exception` in `_notify_observer` entfernen | F-8, R-7 |
| `put_nowait` → `put` (blockierend) | U-6.4, F-4 |
| Wasserstandsregel entfernen | U-6.2 |
| Redaction-Aufruf im Normalizer entfernen | U-2.1, U-2.3 |
| Partiellen Index `WHERE event_id IS NOT NULL` entfernen | U-3.3 (Clientrecords würden fälschlich dedupliziert) |
| Handlerlevel auf DEBUG setzen | P-2 bzw. eine neue Prüfung, dass Realtime-Text nicht gespeichert wird |
| `query_only=ON` entfernen | ein Test, der beweist, dass der Leser nicht schreiben kann |

## IP-2 — Reihenfolge

Die Reihenfolge OBS-00 … OBS-13 bleibt richtig. **Eine Änderung:** OBS-11
(Log View) hängt nach S-1 **nur noch** von OBS-09 ab, nicht mehr von OBS-05
(Ringbuffer). Das entkoppelt die UI vom Worker und erlaubt, sie parallel zu
bauen.

## IP-3 — Cross-Cutting Changes

Geprüft: OBS-08 berührt sechs Produktdateien gleichzeitig. Das ist der einzige
Querschnitt und unvermeidbar, weil Beobachtungspunkte per Definition verteilt
sind. **Risikominderung:** die Reihenfolge innerhalb von OBS-08 ist bereits nach
aufsteigendem Risiko geordnet (UI → Audio-Zähler → Session → Controller). Ein
Abbruch nach Stufe 3 hinterlässt einen sinnvollen Zwischenstand.

---

# 11. Contradictions

Keine stillen Korrekturen — vollständige Liste, einschließlich der
Widersprüche in meinen **eigenen** Dokumenten.

| # | Widerspruch | Betroffene Dokumente | Empfehlung | Blockiert V1? |
|---|---|---|---|---|
| W-1 | Channels groß- vs. kleingeschrieben | Zielbild §9/§16 ↔ Code, Audit §6 | Kleinschreibung ist verbindlich; Zielbild bei nächster Überarbeitung angleichen | NEIN |
| W-2 | Zielbild §16 verlangt Indizes auf `source_timestamp`, `producer_kind`, `type`, `level`, `segment_id`, `event_id` einzeln; mein Schema legt sie nicht an | Zielbild §16 ↔ Schema §9.2 | Bewusste Abweichung mit Begründung; im Zielbild als „Indizes werden vor Implementierung an die realen Abfragen angepasst" lesen | NEIN |
| W-3 | Zielbild §17 und V1-Abgrenzung §3.12 verlangen einen Memory-Ringbuffer und `live_buffer_size`; dieses Review empfiehlt, ihn zu streichen | Zielbild §17, Abgrenzung §3.12/§3.11 ↔ Review §3 | **Ausdrückliche Abweichung.** Die geforderte *Live-Ansicht* bleibt erfüllt, nur die *Bauform* ändert sich. Muss von Marco bestätigt werden, weil es eine benannte Anforderung berührt | NEIN, aber bestätigungspflichtig |
| W-4 | Zielbild §39 sieht `core/server_control/` und `adapters/led.py` in der Modulstruktur; Plan streicht beide | Zielbild §39 ↔ Plan §18 | Zielbild beschreibt ausdrücklich den Endzustand, nicht V1 — kein echter Widerspruch, aber im Plan benannt | NEIN |
| W-5 | V1-Abgrenzung §3.1 listet das Canonical Record ohne `transcription_id` und ohne `server_cursor` | Abgrenzung §3.1 ↔ Schema §5.1 | Beide ergänzen; `server_cursor` ist zwingend, `transcription_id` empfohlen | NEIN |
| W-6 | V1-Abgrenzung §8 verlangt Dateirechteprüfungen; meine Artefakte übergehen sie | Abgrenzung §8 ↔ alle meine Dokumente | Nachgetragen als P-8/P-9 und Test M-11 | NEIN |
| W-7 | **Eigener Plan:** OBS-06 verlangt Managerstart *vor* `AppConfig.load`, was unmöglich ist | Plan OBS-06 ↔ Plan „Übergreifende Regeln" | Korrigiert in AR-5 | NEIN |
| W-8 | **Eigener Plan:** `manager.stop()` in `DesktopApplication.shutdown()`, obwohl vier Startabbruchpfade dort nie hinkommen | Plan „Übergreifende Regeln" ↔ `ui/application.py:666-731` | Korrigiert in AR-6 | NEIN |
| W-9 | **Eigener Plan:** Testerwartung „Duplikat erzeugt Record mit `replayed=True`" ↔ Dedupe-Index unterdrückt die Zeile | Plan OBS-07 ↔ Schema §7.3 | Korrigiert in RD-1 | NEIN |
| W-10 | **Eigenes Audit:** „JEDES /ws/logs-Frame" ↔ Protokollfehler erreichen `_dispatch` nie | Audit §2.4 ↔ `event_stream.py:266` | Korrigiert in AR-1 | NEIN |
| W-11 | **Eigenes Concurrency-Dokument:** Ringbuffer im Worker, „damit die Live-Ansicht exakt sieht, was gespeichert wurde" — falsch, sobald der Store scheitert | Concurrency §10.4 | Entfällt mit S-1 | NEIN |
| W-12 | **Eigenes Schema:** Blockweises Löschen nur bei der Altersretention gefordert, bei der Anzahlretention ein einzelnes großes `DELETE` | Schema §9.5 | Korrigiert in §5.7 | NEIN |
| W-13 | **Eigenes Schema:** `mode=ro` für Leser ↔ WAL erlaubt das nicht allgemein | Schema §8.3/§14.4 | Korrigiert (**D-2**) | NEIN |
| W-14 | **Eigene Regel R-2** („kein unredigierter Record je in der Queue") ↔ AR-2 verlagert die `raw`-Redaction in den Worker | Audit §12.2 ↔ Review AR-2 | R-2 präzisiert: gilt für clienterzeugte Records | NEIN |
| W-15 | **Eigene Einstufung:** OD-02 als blockierend | OPEN_DECISIONS ↔ Review §5.2 | Auf „nicht blockierend" korrigieren | NEIN |
| W-16 | AGENTS.md des Clients nennt `docs/IMPLEMENTATION_ROADMAP.md` als maßgeblich für die Clientarchitektur; meine Analyse hat sie nicht herangezogen | `voice-stt-client/AGENTS.md` ↔ meine Artefakte | **Ehrlich benannt:** ich habe ausschließlich Code, die Logging-Entwürfe und die Architekturbaseline ausgewertet. Vor dem Plan-Freeze sollte jemand prüfen, ob die Roadmap eine Aussage zum Logging enthält, die dem hier Geplanten widerspricht | **NEIN**, aber vor Freigabe zu prüfen |

---

# 12. Required Decisions

| ID | Frage | Empfehlung | blockiert V1? |
|---|---|---|---|
| **OD-01** | Paketname `observability` vs. `logging` | `core/observability/` | **JA** |
| **OD-02** | `transcription_id` als Spalte | ja | **NEIN** (korrigiert) |
| **OD-14** *(neu)* | Ringbuffer streichen und Live als tailende Abfrage bauen (S-1) — weicht von Zielbild §17 und Abgrenzung §3.12 ab | streichen | **NEIN**, aber vor OBS-03 zu bestätigen |
| **OD-15** *(neu)* | Eine Queue mit Wasserstandsregel statt zweier Queues (S-2) | eine Queue | **NEIN**, vor OBS-03 |
| **OD-16** *(neu)* | `ProviderCapabilities` in V1 streichen | streichen | **NEIN**, vor OBS-09 |
| **OD-17** *(neu)* | Funktion „Diagnosehistorie löschen" in V1 aufnehmen (SP-2c) | aufnehmen | **NEIN**, vor OBS-10 |
| **OD-18** *(neu)* | Obergrenze für gespeicherte `raw`-Payloads (Vorschlag 64 KiB) | 64 KiB | **NEIN**, vor OBS-01 |
| OD-03 … OD-13 | unverändert aus `LOGGING_OPEN_DECISIONS.md` | unverändert | NEIN |

**Damit:** eine blockierende Entscheidung (OD-01), fünf neue nicht blockierende,
eine Herabstufung (OD-02).

---

# 13. Final Classification

```text
READY AFTER MINOR CORRECTIONS
```

**Begründung.** Kein Befund erzwingt eine andere Architektur. Der Hook bleibt,
wo er ist; das Fan-out-Prinzip, das Failure-Modell, die Dedupe-Strategie, die
Schichtung und die Admin-Abgrenzung sind bestätigt. Die vier Defekte sind
Ausführungsfehler in den Planungsdokumenten (Serialisierung, WAL-Leseverbindung,
Thread-Eigentum der Verbindung, Latenz auf dem Core-Loop) und in Summe an
wenigen Stellen zu beheben. Die zwei Vereinfachungen **verkleinern** V1, statt
es zu vergrößern.

**„Minor" bedeutet hier nicht „unwichtig".** D-1 und D-2 hätten eine
Implementierung nach dem heutigen Plan verlässlich zum Scheitern gebracht —
D-2 sofort und sichtbar, D-1 still und mit Sicherheitsfolge. Sie sind nur
insofern klein, als sie keine Architekturentscheidung berühren.

**Vor dem Plan-Freeze zu erledigen:**

```text
1. OD-01 entscheiden.
2. OD-14 bis OD-18 bestaetigen (fuenf Ja/Nein-Antworten).
3. D-1 bis D-4 in LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md,
   LOGGING_CONCURRENCY_FAILURE_MODEL.md und LOGGING_V1_IMPLEMENTATION_PLAN.md
   einarbeiten.
4. S-1 und S-2 in dieselben drei Dokumente einarbeiten.
5. Audit §2.4 ("JEDES Frame") und §6.2 (LOGGER_CHANNEL_MAP) praezisieren.
6. Mutationstests (IP-1) und Dateirechte-Beleg (SP-2b) in die Testmatrix.
7. W-16 pruefen: enthaelt `voice-stt-client/docs/IMPLEMENTATION_ROADMAP.md`
   eine Aussage zum Logging, die dem hier Geplanten widerspricht?
```

Punkt 7 ist die **einzige** verbliebene Informationslücke dieser Vorbereitung.
Sie ist klein, konkret benannt und in wenigen Minuten zu schließen.

**Keine Produktänderung vorgenommen. Keine Implementierung begonnen.**
