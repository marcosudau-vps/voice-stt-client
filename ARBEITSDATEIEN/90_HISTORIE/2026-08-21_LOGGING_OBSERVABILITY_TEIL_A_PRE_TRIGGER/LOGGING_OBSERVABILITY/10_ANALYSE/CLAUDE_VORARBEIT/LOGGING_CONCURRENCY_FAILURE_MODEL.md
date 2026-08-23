# LOGGING_CONCURRENCY_FAILURE_MODEL

Deckt Auftragsabschnitte **10** und **11**.
Alle Concurrency-Aussagen am Produktivcode belegt; die Thread-/Task-Tabelle ist
gegen `code-architektur-baseline/RUNTIME_FLOWS_AND_CONCURRENCY.md §3.1`
gegengeprüft und um die für Logging relevanten Eigenschaften ergänzt.

---

# 10. Queue / Worker / Backpressure gegen reale Threads

## 10.1 Reale Producer im Client

| # | Thread/Task | Erzeugt in | Kritikalität | erzeugt Logrecords? | darf blockieren? |
|---|---|---|---|---|---|
| 1 | **PortAudio-Callbackthread** | `core/audio_capture.py:169-177` (`sd.InputStream(callback=...)`) | **höchste** – Blockieren erzeugt Audioaussetzer im Treiber | heute 3 DEBUG-Zeilen (`:250`, `:252`, `:260`) | **niemals** |
| 2 | Thread `audio-process` (daemon) | `core/audio_capture.py:180-185` | hoch | `logger.exception` bei Callbackfehler (`:295`) | nein |
| 3 | Thread `RealtimeSTT-AsyncCore` (**non-daemon**), asyncio-Loop | `ui/core_bridge.py:78-84` | hoch – trägt Transport, Trigger, Feedback | **die Mehrheit aller Records** | nein |
| 3a | Task `session.run()` | `controller.py:2664` | hoch | `connection`-Logger, 53 Stellen | nein |
| 3b | Task `_audio_sender()` | `controller.py:2667` | **hoch, Hot Path** | DEBUG mit `exc_info` je Fehler (`:2593`) | **niemals** |
| 3c | Task `event-stream-generation-N` | `session_coordinator.py:241-245` | mittel | Serverevents über den Hook | nein |
| 3d | Task `_ping_loop`, `_window_timer_task`, `_timeout_warning_task`, `_maintain_wake_word_mode`, `_auto_start_when_ready`, `_StartAttempt.send_task` | `stt_session.py:998`, `controller.py:1463`, `:1403`, `:2673`, `:2670`, `:631` | mittel | vereinzelt | nein |
| 4 | **Qt-Mainloop** | `ui/application.py:726` | hoch – Blockieren friert die Anwendung sichtbar ein | `ui.*`-Logger, u. a. `_log_feedback_decision` je Decision | **niemals** |
| 5 | Thread `RealtimeSTT-LED` (daemon) | `ui/led_feedback.py:303-305` | mittel | `ui.led_feedback` + alle `lefx.*`-Records | nein |
| 6 | Injection-Worker (**non-daemon**) | `core/text_injector.py:422-425` | mittel | `text`-Logger, 29 Stellen | nein |
| 7 | `QTimer`-Callbacks (`_led_watch` 10 s, `_feedback_timer`, `_fade_timer`, `_alert_timer`) | `ui/application.py:121-125`, `ui/tray.py:130-132`, `ui/overlay.py:55-58` | niedrig | selten | nein |
| 8 | Hauptthread vor Qt-Start (`AppConfig.load`, `setup_logging`) | `app.py:147-148` | – | `core.config`, `app` | – |

**Kernbefund N-1.** Es gibt **mindestens sechs verschiedene Threads**, die
Logrecords erzeugen, davon zwei mit harter Echtzeitanforderung (1 und 3b) und
einen, dessen Blockieren sofort sichtbar ist (4). Der Ingress muss deshalb
thread-sicher und ausnahmslos nicht-blockierend sein.

**Kernbefund N-2.** Der asyncio-Loop existiert **nicht immer**. Er wird von
`CoreBridge._thread_main` erzeugt und am Ende geschlossen
(`ui/core_bridge.py:92`, `:139`). Vor `bridge.start()` und nach `bridge.stop()`
laufen `AppConfig.load`, `setup_logging`, `DesktopApplication.__init__`,
`LedFeedback`-Aufbau, `verify_targets` und der komplette
`LedConfigurationError`-Pfad (`ui/application.py:705-712`) **ohne** Loop. Diese
Phasen erzeugen bereits heute Logzeilen und Fehler.

## 10.2 Bereits vorhandene Queues und ihre Verwerfungspunkte

| Queue | Ort | Typ, Größe | Verhalten bei „voll" |
|---|---|---|---|
| Audio-Aufnahme | `audio_capture.py:50` | `queue.Queue(maxsize=200)` | `put_nowait` → `queue.Full` → **verwerfen** + DEBUG (`:258-260`) |
| Audio-Versand | `controller.py:279-281` | `asyncio.Queue(maxsize=300)` | `put_nowait` → `QueueFull` → **verwerfen**, stillschweigend (`:2560-2562`) |
| `/ws/logs`-Empfang | `event_stream.py:196` | `websockets max_queue=512` (`config.py:190`) | Bibliotheksverhalten |
| Textinjektion | `text_injector.py` | unbegrenzt, Sentinel-basiert | – |
| LED-Aufträge | `led_feedback.py:83`, `:269-274` | Liste, `MAX_PENDING=64`, State-Coalescing | älteste verwerfen + WARNING (`:274`) |

**Das Haus hat also bereits ein durchgängiges Muster: bounded + verwerfen +
zählen.** Der Logging-Ingress fügt sich damit ein und erfindet nichts Neues.
`LedFeedback._enqueue` (`:249-274`) ist das direkte Vorbild: Coalescing,
Obergrenze, Verwerfen der ältesten, genau eine Meldung.

## 10.3 Vorschlag

```text
Producer (6 Threads)
   │  ObservabilityIngress.submit(record)      synchron, lockfrei-schnell
   │      1. Health == FAILED ?         -> return False
   │      2. Level/Channel-Filter       -> return False
   │      3. Redaction (Schluesselregel, §12 im Audit)
   │      4. Prioritaet bestimmen
   │      5. queue.put_nowait(...)      -> bei Full: Zaehler++, return False
   ▼
zwei bounded Queues
   high : queue.Queue(maxsize=1024)   WARNING/ERROR/CRITICAL,
                                      channel == "audit",
                                      alle Records mit type != NULL,
                                      logging-interne Meldungen
   low  : queue.Queue(maxsize=8192)   DEBUG/INFO ohne type,
                                      channel == "performance"
   ▼
LoggingWorker            threading.Thread(name="RealtimeSTT-Observability",
                                          daemon=True)
   │  Schleife:
   │    1. bis zu BATCH Records ziehen, high zuerst, dann low
   │       (blockierend nur auf `high.get(timeout=FLUSH_INTERVAL)`)
   │    2. Ringbuffer aktualisieren (fuer die Live-Ansicht)
   │    3. SQLite: eine Transaktion, executemany, ON CONFLICT DO NOTHING
   │    4. optionale Sinks (JSONL/Text)
   │    5. Retention, falls faellig
   │    6. Health/Counter aktualisieren
   ▼
SQLiteLogStore (eine Verbindung, WAL)  +  optionale File-Sinks
```

## 10.4 Festlegungen und Empfehlungen

| Punkt | Empfehlung | Begründung am Code |
|---|---|---|
| **Queue-Typ** | Zwei `queue.Queue` (stdlib, thread-sicher), **nicht** `asyncio.Queue`, **nicht** `PriorityQueue` | `asyncio.Queue` ist nicht thread-sicher und der Loop existiert phasenweise nicht (N-2). `PriorityQueue` müsste bei jedem `put` vergleichen und braucht einen Tiebreaker; zwei einfache Queues leisten dasselbe mit weniger Zustand. |
| **Queue-Größe** | `high = 1024`, `low = 8192`, beide konfigurierbar (`logging.observability.queue_high_size`, `queue_low_size`) | Ein Record ist ~0,5–2 KiB als Python-Objekt. 9216 Records ≈ 10–20 MiB Obergrenze. Zum Vergleich: die Audio-Sendequeue hält 300 Pakete zu je ~1,3 KiB. |
| **Worker: Thread oder asyncio-Task?** | **Dedizierter Thread, daemon=True** | (a) Producer liegen auf sechs Threads – ein Task würde die Thread-Sicherheit nicht ersparen. (b) `sqlite3` will genau einen besitzenden Thread. (c) Der Loop existiert vor `bridge.start()` und nach `bridge.stop()` nicht (N-2); Logging muss die gesamte Prozesslebensdauer abdecken, insbesondere den `LedConfigurationError`-Startabbruch (`ui/application.py:705-712`). (d) `daemon=True` wie `RealtimeSTT-LED`, damit ein hängender Worker den Prozessabbruch nicht verhindert – der Flush ist über `stop(timeout)` explizit, nicht über die Thread-Semantik abgesichert. |
| **Batchgröße** | `200` Records je Transaktion, konfigurierbar | Serverseitig wird jedes Event einzeln committed (`event_logging.py:584`), das ist hier nicht nötig, weil kein anderer Prozess auf den Commit wartet. |
| **Flushintervall** | `0.5 s` (Zeitgrenze für einen Teilbatch) | Kurz genug, dass die Live-Ansicht ohne Ringbuffer noch brauchbar wäre; lang genug, um Bursts zusammenzufassen. |
| **Shutdown** | `ObservabilityManager.stop(timeout=2.0)`: Stop-Flag setzen, Sentinel in beide Queues, Worker leert bis zum Timeout, danach `flush`+`close`. Aufruf an **zwei** Stellen: `DesktopApplication.shutdown()` als **letzter** Schritt nach `bridge.stop()` (`ui/application.py:661`) und im `finally` von `run_headless` | Die Reihenfolge ist wichtig: Der Core-Shutdown erzeugt selbst Records (`controller._do_shutdown` loggt fünf mögliche Fehler). Ein früher gestoppter Logger würde genau die Shutdownfehler verlieren. |
| **max. Flushzeit** | `2.0 s` hart. Danach werden verbleibende Records verworfen und über `stderr` gezählt gemeldet | Vorbild `LedFeedback.shutdown` (`:287-294`, `shutdown_timeout` 1,5 s) und `CoreBridge.stop` (10 s). 2 s ist der Kompromiss: 9216 Records × 200 je Transaktion sind ~46 Commits, das ist bei WAL deutlich unter 2 s. |
| **Dropstrategie** | 1. `low` ist voll → verwerfen, `dropped_low++`. 2. `high` ist voll → **zuerst** versuchen, aus `low` nicht-blockierend zu entnehmen und zu verwerfen (`low.get_nowait()`), dann erneut `high.put_nowait`. Gelingt auch das nicht → verwerfen, `dropped_high++`. 3. **Nie** blockieren, **nie** eine Ausnahme nach oben lassen | Erfüllt die Zielbildpriorität „Runtime nie blockieren > Speicher bounded > hochwertige Records erhalten" (Zielbild §20). Schritt 2 ist der einzige Ort, an dem ein wichtiger Record einen unwichtigen verdrängt. |
| **Prioritäten** | genau **zwei**. Kein feineres Schema | Drei oder mehr Stufen erfordern eine Prioritätswarteschlange und damit einen Vergleich je `put` im Hot Path. Der messbare Unterschied wäre null. |
| **Drop Counter** | `dropped_low`, `dropped_high`, `dropped_shutdown`, jeweils `itertools.count`-frei als einfache Ints unter dem Health-Lock. Nach Erholung (Queue < 25 % über ≥ 5 s) erzeugt der **Worker** genau einen Record `logging.records_dropped` mit den Zählerständen und setzt sie zurück | Der Record entsteht im Worker, **nicht** über den Handler – sonst Rekursion (§11). |
| **Health State** | siehe §11 | – |
| **Ringbuffer (Live-Ansicht)** | `collections.deque(maxlen=live_buffer_size)`, Default 2000, geschrieben **nur vom Worker**, gelesen von der UI über eine Kopie unter `threading.Lock` | Schreiben im Worker statt im Ingress: der Ingress läuft im Hot Path, das Anhängen an eine `deque` unter Lock ist zwar billig, aber der Worker hat den Record ohnehin in der Hand. Zusätzlich sieht die Live-Ansicht dann exakt das, was auch gespeichert wurde. |

## 10.5 Die harte Invariante und ihre Prüfung

```text
Logging darf niemals Producer blockieren.

Umgesetzt durch:
  * ausschließlich put_nowait, kein einziges blockierendes put;
  * kein Lock, das vom Worker über eine I/O-Operation gehalten wird
    (der Store-Lock existiert gar nicht -- nur der Worker berührt die
    Verbindung);
  * kein Lock zwischen Ingress und Worker außer den queue-internen;
  * Redaction und Serialisierung nach JSON passieren im Producer-Thread
    (nötig für R-2 im Audit), sind aber reine CPU-Arbeit ohne I/O.
    Für Hot-Path-Records entfällt sie ohnehin, weil dort nur Aggregate
    entstehen (Audit §4.1).

Nachweis im Test: siehe LOGGING_TEST_MATRIX.md, Gruppe „Runtime isolation"
und „Backpressure". Insbesondere der Test, der den Worker anhält und danach
20.000 Records einreicht: submit() muss durchgehend unter einer harten
Zeitgrenze zurückkehren und darf nie werfen.
```

## 10.6 Was ausdrücklich NICHT getan wird

```text
* Kein `QueueHandler`/`QueueListener` aus der stdlib.
  Grund: `QueueListener` ruft die Zielhandler auf und bringt sein eigenes
  Threadmodell mit, das weder Priorität noch Dropstrategie noch Batching
  kennt. Der eigene Worker ist kleiner als der Anpassungsaufwand.

* Keine Änderung an `logging_setup.setup_logging` außer dem Hinzufügen
  EINES weiteren Handlers. Datei- und Stdout-Handler bleiben unverändert.
  Grund: Sie sind heute die einzige Diagnose und müssen es bleiben, solange
  der neue Weg nicht bewiesen ist -- und sie sind die Rückfallebene, wenn
  der Store ausfällt.

* Kein Anfassen der Audio-Queues, der LED-Queue oder der Injection-Queue.

* Kein zusätzlicher Thread pro Sink. Text- und JSONL-Sink schreiben im
  LoggingWorker, nach dem SQLite-Commit.
```

---

# 11. Logging-interne Failure Domain

## 11.1 Vorhandene Error-/Health-Mechanismen im Repository

| Muster | Ort | Übernehmen? |
|---|---|---|
| „Einmal melden, dann nur noch DEBUG" plus Dauer als abfragbare Zahl (`unavailable_seconds`) | `ui/led_feedback.py:419-449` | **ja, direktes Vorbild** |
| Fehler in einem Callback fängt der Aufrufer und loggt `exception`, ohne den eigenen Ablauf zu ändern | durchgängig, z. B. `controller.py:470`, `session_coordinator.py:465`, `event_stream.py:333` | ja |
| Teilsystem deaktiviert sich bei Init-Fehler statt die Anwendung zu stoppen (`_db_enabled = False`) | `history.py:174-178` | **ja** |
| Qt-Signal für Fehlermeldungen an die UI | `ui/feedback.py` `failure`-Signal, `CoreBridge.fatal_error` | ja, für die UI-Anzeige |
| Ungültige Persistenzdatei wird ignoriert statt repariert | `event_cursor_store.py:69-71` | ja |

## 11.2 Rekursionsgefahr – die konkreten Wege

```text
Weg 1  Der Store wirft. Der Store loggt den Fehler über `logger.error`.
       Der Root-Logger reicht ihn an den UnifiedLogHandler.
       Der Handler legt ihn in die Queue. Der Worker versucht ihn zu
       schreiben. Der Store wirft wieder.  -> Endlosschleife.

Weg 2  `logging.Handler.emit` wirft. Die stdlib ruft `handleError`, das
       bei `logging.raiseExceptions == True` einen Traceback nach stderr
       schreibt -- je Record. Bei einem defekten Store ist das je Logzeile
       ein Traceback.

Weg 3  Der Normalizer wirft bei einem fehlerhaften Record. Wird das über
       `logger.exception` gemeldet, entsteht ein neuer Record, der denselben
       Weg nimmt.

Weg 4  Ein Sink-Fehler wird über den Handler gemeldet; der Sink läuft im
       Worker; der Worker schreibt den Fehlerrecord in denselben Sink.
```

## 11.3 Gegenmaßnahmen

```text
G-1  Wiedereintrittssperre im Handler.
     `_in_emit = threading.local()`. `UnifiedLogHandler.emit` setzt das Flag,
     arbeitet, löscht es im `finally`. Ist es bereits gesetzt, kehrt emit
     sofort zurück. Deckt Weg 1 und 3 auf der Handlerseite.

G-2  Eigener, nicht propagierender Logger für die Observability-Pakete.
        internal = logging.getLogger("observability.internal")
        internal.propagate = False
        internal.addHandler(<Emergency-stderr-Handler>)
     Jeder `logger.*`-Aufruf INNERHALB von core/observability/ benutzt
     ausschließlich diesen Logger. Damit erreicht kein interner Fehler den
     Root-Logger, unabhängig von G-1. Gürtel und Hosenträger, weil G-1 bei
     einem Fehler in einem ANDEREN Thread nicht greift.

G-3  `UnifiedLogHandler.handleError(record)` wird überschrieben und meldet
     an LoggingInternalHealth statt an stderr. Deckt Weg 2.

G-4  Der Emergency-stderr-Ausgang ist ratenbegrenzt: höchstens eine Zeile
     je Fehlerkategorie und 60 Sekunden, mit Wiederholungszähler.
     Format bewusst einzeilig und präfigiert:
        [observability] store_write_failed (x37): database is locked
     Ohne Rate Limit ist stderr bei einem dauerhaft defekten Store selbst
     die Störung -- und in einem PyInstaller-GUI-Build ohne Konsole ist es
     ein blockierender Schreibvorgang ins Nichts.

G-5  Kein Fehler der Logging-Domäne wird über `report_local_feedback`,
     `CanonicalEventType` oder die FeedbackEngine gemeldet.
     Begründung: das würde eine LED-/Sound-/Overlay-Reaktion auslösen
     (ui/application.py:232-253) und damit Logging zum Feedbackproduzenten
     machen -- ein direkter Verstoß gegen das Beobachterprinzip (Zielbild
     §2.1, Invariante O-1).

G-6  Der Record `logging.records_dropped` und ein etwaiger
     `logging.store_recovered` werden VOM WORKER direkt in den Store
     geschrieben, unter Umgehung von Handler und Queue.
```

## 11.4 Fehlerfälle und ihr Verhalten

| Fehler | Erkennung | Reaktion | Health |
|---|---|---|---|
| **SQLite failure** beim Öffnen/Migrieren | Ausnahme im Store-Init | Store deaktiviert, Anwendung läuft weiter, Ringbuffer und Sinks arbeiten weiter | `FAILED_STORE` |
| **SQLite failure** beim Batchschreiben | Ausnahme in `executemany`/`commit` | Rollback; Batch **einmal** wiederholen; scheitert das erneut, Batch verwerfen, `store_errors++`; nach 5 aufeinanderfolgenden Fehlschlägen Store für 60 s aussetzen und danach mit einem leeren Testschreibvorgang prüfen | `DEGRADED_STORE` → ggf. `FAILED_STORE` |
| **SQLite read-only / Disk full** | `sqlite3.OperationalError` | wie oben; zusätzlich Retention aussetzen (ein `DELETE` braucht auch Platz) | `FAILED_STORE` |
| **File sink failure** (Verzeichnis weg, Rechte, Platte voll) | Ausnahme beim Schreiben/Rotieren | Sink deaktivieren, **einmal** über stderr melden, Store läuft weiter | `DEGRADED_SINK` |
| **Malformed record** (Normalizer wirft, nicht serialisierbares `details`) | Ausnahme im Normalizer oder in `json.dumps` | Record verwerfen; **einen** Ersatzrecord `logging.record_rejected` mit `component`, Ausnahmetyp und **ohne** die Originaldaten erzeugen; `malformed++`. `json.dumps(..., default=str)` als erste Rückfallebene, genau wie serverseitig (`event_logging.py:576-581`) | `OK` mit Zähler |
| **Worker crash** (unerwartete Ausnahme in der Schleife) | `try/except BaseException` um den Schleifenkörper | Ausnahme wird gefangen, `worker_errors++`, Schleife läuft weiter. Bricht die Schleife dennoch ab (z. B. `SystemExit`): Flag setzen, Ingress wechselt in „nur verwerfen und zählen", stderr-Meldung. **Kein Neustartversuch** – ein Worker, der zweimal stirbt, stirbt beim dritten Mal auch | `FAILED_WORKER` |
| **Queue overflow** | `queue.Full` in `submit` | Zähler, kein Log, kein stderr (das wäre das Frequenzproblem erneut). Meldung erst nach Erholung als ein `logging.records_dropped` | `DROPPING` während der Überlast |
| **Retention failure** | Ausnahme im Retentionlauf | Lauf abbrechen, `retention_errors++`, nächster Versuch im nächsten Intervall. Retention darf nie den Schreibpfad blockieren | `DEGRADED_STORE` |
| **Shutdown-Timeout** | verbleibende Queue-Länge > 0 nach `stop(timeout)` | `dropped_shutdown` setzen, eine stderr-Zeile | – |

## 11.5 Empfohlener Health-Zustand

```python
# core/observability/health.py   (Entwurf, nicht implementiert)

class LoggingHealthState(str, Enum):
    OK              = "ok"
    DROPPING        = "dropping"          # Queue laeuft ueber, Rest funktioniert
    DEGRADED_SINK   = "degraded_sink"     # Datei-Sink aus, Store laeuft
    DEGRADED_STORE  = "degraded_store"    # Store zeitweise gestoert
    FAILED_STORE    = "failed_store"      # Store dauerhaft aus
    FAILED_WORKER   = "failed_worker"     # nichts wird mehr geschrieben
    DISABLED        = "disabled"          # per Konfiguration aus

@dataclass(frozen=True)
class LoggingHealthSnapshot:
    state: LoggingHealthState
    since: Optional[float]              # time.monotonic(), wie unavailable_since
    detail: str                          # kurze, redigierte Ursache
    enqueued: int
    written: int
    dropped_low: int
    dropped_high: int
    dropped_shutdown: int
    malformed: int
    store_errors: int
    sink_errors: int
    retention_errors: int
    worker_errors: int
    queue_high_depth: int
    queue_low_depth: int
    db_bytes: Optional[int]

class LoggingInternalHealth:
    """Zaehlt, entprellt und meldet. Kennt weder Store noch Handler."""
    def snapshot(self) -> LoggingHealthSnapshot: ...
    def note_store_error(self, exc: BaseException) -> None: ...
    def note_sink_error(self, name: str, exc: BaseException) -> None: ...
    def note_dropped(self, priority: str, count: int = 1) -> None: ...
    def note_malformed(self, component: str, exc: BaseException) -> None: ...
    def note_written(self, count: int) -> None: ...
```

**Ausgabewege**

```text
stderr        ratenbegrenzt (G-4), Format "[observability] <code> (xN): <detail>".
              Der einzige Weg, der ohne funktionierende Infrastruktur trägt.

UI-Status     Die Log-Ansicht zeigt LoggingHealthSnapshot in ihrer Statuszeile
              und POLLT ihn (QTimer, 1 s) -- kein Signal je Fehler, sonst
              wiederholt sich das Frequenzproblem. Vorbild: der bestehende
              QTimer `_led_watch` (ui/application.py:121-125), der
              `LedFeedback.unavailable_seconds` pollt.

Counters      Über `snapshot()` abrufbar, auch für Tests. Die Tests prüfen
              Zähler, nicht Logausgaben.

Recovery      Automatisch und still: Store nach Aussetzintervall erneut
              prüfen; Sink beim nächsten Rotationszeitpunkt erneut versuchen;
              nach Rückkehr in OK genau EIN Record `logging.recovered` mit
              den Zählern seit dem Fehlerbeginn, geschrieben vom Worker (G-6).
              Kein Nutzerdialog, keine Tray-Benachrichtigung: eine defekte
              Diagnose ist kein Ereignis, das ein Diktat unterbrechen darf.
```

## 11.6 Grenzen, die ausdrücklich benannt werden

```text
* Fällt der Worker aus, gehen ab diesem Zeitpunkt alle Records verloren.
  Die vorhandene Datei-/Stdout-Ausgabe von logging_setup bleibt davon
  UNBERÜHRT und ist genau deshalb die Rückfallebene. Das ist der Hauptgrund,
  den bestehenden RotatingFileHandler nicht zu ersetzen.

* Der Health-State selbst wird nicht persistiert. Nach einem Neustart ist er
  OK, bis der erste Fehler erneut auftritt. Eine Persistenz würde einen
  zweiten Speicher benötigen, der dieselben Fehler haben kann.

* Ein Fehler, der den gesamten Prozess beendet (harter Absturz, TerminateProcess),
  verliert den Inhalt beider Queues. Das ist der bewusste Preis für die
  Nicht-Blockierung und ist im Zielbild §20 bereits so entschieden.
```
