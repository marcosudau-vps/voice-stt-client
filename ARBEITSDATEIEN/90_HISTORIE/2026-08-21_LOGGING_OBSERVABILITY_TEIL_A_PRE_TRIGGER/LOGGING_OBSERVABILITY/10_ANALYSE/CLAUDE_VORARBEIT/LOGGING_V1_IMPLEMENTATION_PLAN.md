# LOGGING_V1_IMPLEMENTATION_PLAN

Deckt Auftragsabschnitte **18, 19, 24**.
**Status:** Planungsentwurf. Noch nicht freigegeben. Es wurde kein Produktcode
geschrieben und keine Datei in den drei Repositories geändert.

Voraussetzung für die Freigabe: die als *blockierend* markierten Punkte aus
`LOGGING_OPEN_DECISIONS.md`.

---

# 18. Modulstruktur gegen den echten Repo-Baum

## 18.1 Realer Baum (voice-stt-client)

```text
voice-stt-client/
├── app.py                    Einstieg, setup_logging, Headless/GUI-Weiche
├── core/                     FLACH, 20 Module, KEIN Unterpaket
│   ├── __init__.py           (leer, 1 Zeile)
│   ├── config.py             1011 Z.
│   ├── controller.py         2724 Z.
│   ├── stt_session.py        1446 Z.
│   ├── event_{models,protocol,stream,normalizer,cursor_store}.py
│   ├── feedback_{mapping,reducer}.py
│   ├── session_coordinator.py
│   ├── audio_capture.py, history.py, text_injector.py, reinsertion.py
│   ├── led_controller.py, logging_setup.py, settings_metadata.py
│   ├── actions.py, version.py
├── ui/                       FLACH, 11 Module, KEIN Unterpaket
│   ├── application.py, core_bridge.py, settings_dialog.py, tray.py,
│   ├── overlay.py, presentation.py, feedback.py, led_feedback.py,
│   ├── hotkeys.py, single_instance.py
├── tests/                    FLACH, test_*.py (unittest) + manual_test_*.py
└── scripts/
```

**Befund M-1.** `core/` und `ui/` sind heute **flach**. Es gibt kein einziges
Unterpaket. Ein Unterpaket ist damit ein neues Muster – vertretbar, weil
`core/observability/` sonst 12 weitere Dateien in ein bereits 20-Dateien-
Verzeichnis legen würde, aber es muss ausdrücklich benannt werden.

**Befund M-2.** Alle Importe sind **absolut** (`from core.x import y`,
`from ui.x import y`), auch innerhalb von `core/`. Unterpakete funktionieren
damit unverändert (`from core.observability.models import …`).

**Befund M-3 (Importrichtung heute).**
`ui/*` → `core/*` ist erlaubt und üblich. `core/*` → `ui/*` kommt **nirgends**
vor. `core/config.py` importiert `core/feedback_mapping.py`;
`core/settings_metadata.py` importiert `core/config.py`. Diese Richtung darf das
Vorhaben nicht umkehren.

**Befund M-4 (PyInstaller).** `voice-stt-client.spec` listet nur solche
`hiddenimports`, die über `importlib` **nach Namen** geladen werden
(LEFX-Sets, `usb.*`). Statisch importierte neue Unterpakete werden von der
Analyse gefunden. **Keine Spec-Änderung nötig**, solange die Observability-
Module normal importiert werden. Wird ein Sink oder Provider je über einen
Namensstring geladen, muss er in die Spec – das ist ein Grund, es **nicht** zu
tun.

## 18.2 Empfohlene tatsächliche Modulstruktur

```text
voice-stt-client/
├── core/
│   └── observability/
│       ├── __init__.py            NUR Re-Exports der oeffentlichen Namen:
│       │                          ObservabilityManager, ObservabilityIngress,
│       │                          NULL_INGRESS, CanonicalLogRecord
│       ├── models.py              CanonicalLogRecord, ProducerKind, Channel,
│       │                          Level, Scope, RecordPriority
│       ├── redaction.py           Schluesselregel + Pfadkuerzung (§12 Audit)
│       ├── normalizer.py          LogRecord -> Canonical,
│       │                          EventProtocolResult -> Canonical,
│       │                          ClientEvent -> Canonical
│       ├── ingress.py             ObservabilityIngress, NullIngress,
│       │                          zwei bounded Queues, Ringbuffer
│       ├── health.py              LoggingHealthState/-Snapshot,
│       │                          LoggingInternalHealth, Emergency-stderr
│       ├── worker.py              LoggingWorker (Thread), Batching, Retention
│       ├── manager.py             ObservabilityManager: baut alles zusammen,
│       │                          start()/stop()/apply_config()/snapshot()
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── python_logging.py  UnifiedLogHandler
│       │   ├── client_events.py   ClientEventEmitter (duenne Fassade)
│       │   └── server_live.py     ServerLiveAdapter
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── base.py            LogStore-Protokoll
│       │   └── sqlite.py          SQLiteLogStore, Schema, Migration, Retention
│       ├── query/
│       │   ├── __init__.py
│       │   ├── base.py            LogProvider, QueryFilter, QueryPage,
│       │   │                      ProviderStatus, LogRecordView
│       │   ├── local.py           LocalLogProvider
│       │   └── service.py         LogQueryService
│       └── sinks/
│           ├── __init__.py
│           ├── base.py            Sink-Protokoll
│           └── jsonl_file.py      JsonlSink   (Text-Sink: siehe OD-06)
└── ui/
    └── logs/
        ├── __init__.py
        ├── log_window.py
        ├── log_page.py
        ├── log_table_model.py
        ├── log_filter_bar.py
        ├── log_detail_view.py
        └── log_query_controller.py
```

## 18.3 Abweichungen vom Entwurf und ihre Begründung

| Zielbildentwurf §39 | Empfehlung | Begründung |
|---|---|---|
| `redaction` nicht vorgesehen | **eigenes Modul `redaction.py`** | Die Redaction ist die einzige sicherheitsrelevante Regel des Pakets. Sie muss isoliert testbar sein und darf nicht in `normalizer.py` verschwinden. |
| `adapters/led.py` | **entfällt in V1** | LEFX läuft in-process und loggt nach `lefx.*`; eine Normalizer-Regel genügt (Audit §17). |
| `query/server_history.py` | entfällt in V1 | Zielbildkonform (V2). |
| `sinks/text_file.py` | **abhängig von OD-06** | Ein zweites Format ohne Nutzer verdoppelt die Fehlerfläche. |
| `core/server_control/` | **entfällt vollständig in V1** | Audit §16; `AGENTS.md` schließt den Admin-Service aus. |
| `ui/settings/logging_settings.py` | **entfällt** | Der Settings-Dialog ist metadatengetrieben; eine eigene Datei wäre ein zweiter Weg für dasselbe (`LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md §13.3`). |
| `ui/logs/log_page.py` als einziger Einstieg | zusätzlich `log_window.py` + `log_query_controller.py` | Fenster/Lifetime und Thread-Übergang sind eigene Belange. |

## 18.4 Die vier zu vermeidenden Fehler – und wie sie vermieden werden

| Fehler | Gegenmaßnahme | Prüfbar durch |
|---|---|---|
| **Monolithdatei** | 15 Module, keines über ~400 Zeilen; `sqlite.py` und `worker.py` sind die größten | Zeilenzählung im Abschluss |
| **Unnötige Microservices** | Kein Prozess, kein Socket, kein Server. Ein Thread, eine Datei | – |
| **Zyklische Importe** | Strenge Schichtung: `models` ← `redaction` ← `normalizer` ← `ingress` ← `worker` ← `manager`. `storage` und `sinks` kennen nur `models`. `query` kennt nur `models` + `storage`. `adapters` kennen `ingress` + `normalizer`, **nicht** umgekehrt | Ein Test, der jedes Modul einzeln importiert, plus eine Prüfung, dass `models.py` **nichts** aus dem eigenen Paket importiert |
| **Qt-Abhängigkeit im Core** | Kein `PySide6`-Import unterhalb von `core/`. Der Ringbuffer wird **gepollt**, nicht signalisiert | Ein Test, der `core/observability/**/*.py` nach `PySide6`/`QtCore` durchsucht — dasselbe Muster wie bestehende Contract-Tests |
| **Direkte DB-Nutzung aus der UI** | `ui/logs/**` importiert `core.observability.query.*`, **nie** `core.observability.storage.*` und **nie** `sqlite3` | Ein Test, der `ui/logs/**` nach `sqlite3` und `storage` durchsucht |

---

# 19./24. V1-Implementierungsreihenfolge

Die Reihenfolge folgt der **Abhängigkeitsrichtung im Code**, nicht der
Gliederung des Zielbilds. Zwei Abweichungen zur Beispielstruktur des Auftrags:

* **OBS-04 (Store) wird vor OBS-03 (Handler) gebaut.** Ohne Store hat der
  Handler kein Ziel und ist nur mit einem Fake testbar. Mit Store ist der erste
  Ende-zu-Ende-Nachweis bereits in OBS-05 möglich. Grüne Tests gegen Fakes sind
  ausdrücklich kein Fertigstellungsnachweis.
* **Ein eigenes Paket OBS-00 für die Redaction**, vor allem anderen. Sie ist die
  einzige Regel, deren Fehlen einen echten Schaden anrichtet, und alles
  Folgende ruft sie auf.

| Paket | Titel | hängt ab von |
|---|---|---|
| OBS-00 | Canonical Models + Redaction | – |
| OBS-01 | Normalizer (drei Eingänge) | OBS-00 |
| OBS-02 | Health + Emergency-Ausgang | OBS-00 |
| OBS-03 | Ingress + Backpressure + Ringbuffer | OBS-00, OBS-02 |
| OBS-04 | SQLiteLogStore + Schema + Migration + Retention | OBS-00, OBS-02 |
| OBS-05 | Worker + Manager + Shutdown | OBS-02, OBS-03, OBS-04 |
| OBS-06 | UnifiedLogHandler (Python-Logging-Adapter) | OBS-01, OBS-03, OBS-05 |
| OBS-07 | ServerLiveAdapter + Fan-out-Hook im Coordinator | OBS-01, OBS-03 |
| OBS-08 | Strukturierte Client-Hooks | OBS-01, OBS-03, OBS-07 |
| OBS-09 | Query Layer (base/local/service) | OBS-04 |
| OBS-10 | Settings-Integration | OBS-05 |
| OBS-11 | Minimal Log View | OBS-09, OBS-05 |
| OBS-12 | Optionaler JSONL-Sink | OBS-05 |
| OBS-13 | Failure-, Isolations- und Performance-Gate | alle |

---

## OBS-00 — Canonical Models + Redaction

**Scope.** `core/observability/models.py`, `core/observability/redaction.py`.
Das eingefrorene Recordmodell aus
`LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md §5.1`, die Enums, die
Prioritätsableitung und die vollständige Redaction-Regel.

**Non-Scope.** Kein Handler, kein Store, keine Queue, kein Adapter.

**Dateien/Komponenten.**
```text
NEU  core/observability/__init__.py
NEU  core/observability/models.py
NEU  core/observability/redaction.py
NEU  tests/test_observability_models.py
NEU  tests/test_observability_redaction.py
```

**Sollzustand.**
```python
@dataclass(frozen=True)
class CanonicalLogRecord:
    record_id: str
    received_at: str
    producer_kind: str
    producer_id: str
    instance_id: str
    scope: str
    channel: str
    level: str
    replayed: bool = False
    source_timestamp: Optional[str] = None
    type: Optional[str] = None
    component: Optional[str] = None
    session_id: Optional[str] = None
    generation: Optional[int] = None
    activation_id: Optional[str] = None
    segment_id: Optional[int] = None
    transcription_id: Optional[str] = None
    command_id: Optional[str] = None
    event_id: Optional[str] = None
    correlation_id: Optional[str] = None
    server_cursor: Optional[int] = None
    message: Optional[str] = None
    details: Mapping[str, Any] = field(default_factory=dict)
    raw: Optional[Mapping[str, Any]] = None

    @property
    def priority(self) -> RecordPriority: ...
```
`redact(value, *, store_transcription_content, store_raw_payload)` arbeitet
rekursiv über Schlüsselnamen (case-insensitiv, ohne `_`/`-`), ersetzt
Trefferwerte durch `"[redacted]"`, kürzt Benutzerprofilpfade auf `~` und
ersetzt Transkriptfelder durch `"[redacted:<n> chars]"`.

**Implementierungsschritte.**
1. Enums `ProducerKind`, `Channel`, `Level`, `Scope`, `RecordPriority`.
2. `CanonicalLogRecord` als frozen dataclass, `details`/`raw` beim Bau
   einfrieren (Muster `event_models._freeze`, `event_models.py:108-115`).
3. `priority`: `WARNING+` oder `channel == audit` oder `type is not None` → HIGH.
4. `redaction.SENSITIVE_KEYS` und `TRANSCRIPT_KEYS` als Modulkonstanten.
5. `redact_mapping`, `redact_text`, `shorten_user_paths`.
6. Rekursionstiefe hart begrenzen (16) und Ergebnis bei Überschreitung
   abschneiden — ein zyklisches oder pathologisch tiefes `details` darf den
   Producer-Thread nicht binden.

**Tests.** Modellinvarianten; Prioritätsableitung; `details` nach dem Bau
unveränderlich.
**Negativtests.** `producer_kind`/`channel`/`level` außerhalb der Menge; `details`
kein Mapping; `segment_id` negativ oder `bool`.
**Failure Tests.** Zyklisches `details`; `details` mit 10.000 Schlüsseln;
`details`-Wert, der bei `repr()` wirft.
**Akzeptanzkriterien.**
- Ein Mapping mit `accessToken`/`authorization`/`adminKey`/`password` auf jeder
  Verschachtelungsebene enthält den Originalwert nachweislich nicht mehr.
- Bei `store_transcription_content=False` enthält kein Ergebnisfeld den Text,
  aber die Zeichenzahl bleibt erhalten.
- Ein Pfad `C:\Users\<name>\AppData\…` erscheint als `~\AppData\…`.
- Kein `PySide6`-Import.

**Evidence.** Testlauf `python -m unittest tests.test_observability_redaction -v`
plus ein Diagnoseskript **außerhalb des Produktrepos**, das die reale
`hello`-Struktur aus `docs/structured-logging.md:209-225` durch `redact` schickt
und zeigt, dass `accessToken` verschwindet.

---

## OBS-01 — Normalizer

**Scope.** `normalizer.py` mit drei Eingängen: `logging.LogRecord`,
`(SessionContext, EventProtocolResult)`, strukturiertes Clientevent.

**Non-Scope.** Kein Queueing, kein Speichern, keine Handlerregistrierung.

**Dateien.** `NEU core/observability/normalizer.py`,
`NEU tests/test_observability_normalizer.py`.

**Sollzustand.**
```text
from_log_record(record, *, instance_id, session_id, generation) -> CanonicalLogRecord
    channel     := LOGGER_CHANNEL_MAP.get(record.name, "system")
    producer    := "led"/"respeaker-led-controller", wenn record.name mit
                   "lefx." beginnt, sonst "client"/"voice-stt-client"
    component   := record.name
    level       := record.levelname
    type        := None
    message     := record.getMessage()
    details     := {"logger": name, "func": funcName, "line": lineno,
                    "thread": threadName}
                   + die vier bestehenden extra-Felder (session_id, segment_id,
                     event_type, detail) aus logging_setup.JsonFormatter:39,
                     falls gesetzt
                   + record.exc_info -> details["exception"] als Text
                     (formatException), NIEMALS record.args, NIEMALS repr()

from_server_result(context, result) -> Optional[CanonicalLogRecord]
    Events   -> producer_kind "server", producer_id "voice-stt-server",
                instance_id = envelope.server_instance_id,
                channel/level/type/session_id/segment_id/transcription_id/
                event_id/server_cursor aus dem Envelope,
                generation aus context.generation,
                activation_id aus envelope.data.get("activationId"),
                message aus envelope.extra.get("meldung")   <-- Befund C-2,
                details = envelope.data, raw = result.payload,
                replayed = result.origin is EventOrigin.REPLAY
    Control  -> type "client.eventstream.<kind>", producer_kind "client",
                channel "system", raw = result.payload,
                bei log.gap zusaetzlich lostFromCursor/lostToCursor in details

from_client_event(type, *, channel, level, component, message, details, ids)
                                                  -> CanonicalLogRecord
```

**Implementierungsschritte.**
1. `LOGGER_CHANNEL_MAP` als explizite Tabelle (Audit §6.2), Default `system`.
2. `_normalize_level(severity)` mit Rückfall auf `INFO` und Ablage des
   Originalwerts in `details["source_severity"]` (Befund C-3).
3. Redaction am **Ende** jedes Pfades, nicht am Anfang.
4. Zeitkonvertierung `record.created` → ISO-8601 UTC mit `Z`.

**Tests.** Alle drei Pfade; `meldung` landet in `message`; Servertimestamp bleibt
unverändert; `replayed` korrekt.
**Negativtests.** Envelope mit unbekanntem `severity`; Envelope ohne `data`;
`LogRecord` mit `%s`-Platzhaltern ohne Argumente; `LogRecord` mit `exc_info`,
dessen Exception beim Formatieren wirft.
**Failure Tests.** `result.event is None` bei `kind == EVENT`; `context` mit
`session_id=None`.
**Akzeptanzkriterien.**
- Ein realer `log.event`-Frame (aus `tests/test_event_protocol.py::event_message`)
  ergibt einen Record mit gefüllten `event_id`, `server_cursor`, `channel`,
  `session_id` und `segment_id`.
- Der Normalizer wirft **nie**; er liefert im Zweifel `None`.
- Kein `PySide6`-Import, kein `sqlite3`-Import.

**Evidence.** Testlauf. Zusätzlich ein Vergleich Feld für Feld gegen die Tabelle
in `LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md §5.1` als Kommentar im Test.

---

## OBS-02 — Health + Emergency-Ausgang

**Scope.** `health.py` gemäß `LOGGING_CONCURRENCY_FAILURE_MODEL.md §11.5`.

**Non-Scope.** Keine UI-Anbindung, keine Qt-Signale, keine
`report_local_feedback`-Nutzung (Regel G-5).

**Dateien.** `NEU core/observability/health.py`,
`NEU tests/test_observability_health.py`.

**Implementierungsschritte.**
1. `LoggingHealthState`, `LoggingHealthSnapshot`, `LoggingInternalHealth`
   (alle Zähler unter einem `threading.Lock`).
2. Emergency-Ausgang: eigener, **nicht propagierender** Logger
   `observability.internal` mit einem `StreamHandler(sys.stderr)` (Regel G-2).
3. Rate Limit: höchstens eine Zeile je `(code)` und 60 s, mit
   Wiederholungszähler (Regel G-4).
4. `sys.stderr is None` (PyInstaller-GUI-Build ohne Konsole) muss abgefangen
   werden — dann bleiben nur die Zähler.

**Tests.** Zustandsübergänge; Zähler; Snapshot ist ein Wertobjekt.
**Negativtests.** `note_store_error` mit einer Exception ohne `str()`.
**Failure Tests.** `sys.stderr = None`; `sys.stderr.write` wirft;
2000 Fehler in 1 s erzeugen ≤ 1 Zeile.
**Akzeptanzkriterien.**
- Kein Aufruf von `logging.getLogger()` ohne `propagate=False`.
- Kein Import von `core.event_models` oder `core.feedback_reducer`
  (Nachweis, dass kein Feedbackweg entstehen kann).

**Evidence.** Testlauf; ein Test, der `logging.getLogger("observability.internal").propagate is False` prüft.

---

## OBS-03 — Ingress + Backpressure + Ringbuffer

**Scope.** `ingress.py` gemäß `LOGGING_CONCURRENCY_FAILURE_MODEL.md §10.3/10.4`.

**Non-Scope.** Kein Worker, kein Store.

**Dateien.** `NEU core/observability/ingress.py`,
`NEU tests/test_observability_ingress.py`.

**Sollzustand.** `ObservabilityIngress.submit(record) -> bool` ist
thread-sicher, blockiert nie, wirft nie. `NullIngress` als No-Op mit derselben
Signatur; `NULL_INGRESS` als Modulkonstante.

**Implementierungsschritte.**
1. Zwei `queue.Queue`; Größen aus der Konfiguration.
2. Dropstrategie exakt nach §10.4 (HIGH verdrängt LOW).
3. Ringbuffer `deque(maxlen=…)` mit Monotonmarke; `live_since(marker)` liefert
   `(records, new_marker)`.
4. `drain(max_items, timeout)` für den Worker.
5. `enabled=False` ⇒ `submit` liefert sofort `False`.

**Tests.** Reihenfolge HIGH vor LOW; `live_since` liefert keine Doppel;
`NullIngress` ist verhaltensgleich.
**Negativtests.** `submit(None)`; `submit` mit fremdem Typ.
**Failure Tests.** Beide Queues voll ⇒ `submit` liefert `False`, wirft nicht,
Zähler stimmen. 20.000 Submits ohne laufenden Worker.
**Akzeptanzkriterien.**
- **Harte Zeitgrenze:** 100.000 `submit`-Aufrufe bei voller Queue in unter
  1,0 s auf einem gewöhnlichen Arbeitsplatzrechner (der Wert ist ein
  Regressionswächter, keine Leistungszusage).
- Aus acht gleichzeitigen Threads mit je 5000 Submits gehen `written + dropped`
  genau auf; kein Record wird doppelt geliefert.
**Evidence.** Testlauf plus die gemessenen Zeiten im Testprotokoll.

---

## OBS-04 — SQLiteLogStore

**Scope.** `storage/base.py`, `storage/sqlite.py`: Schema, Migration, Batch-
Insert mit Dedupe, Retention, Größengrenze, read-only Leseverbindung.

**Non-Scope.** Kein Worker, kein Query-Layer, keine UI.

**Dateien.** `NEU core/observability/storage/{__init__,base,sqlite}.py`,
`NEU tests/test_observability_store.py`.

**Sollzustand.** Exakt das DDL aus
`LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md §9.1`; Schreiben ausschließlich über
`write_batch(records) -> int`; Retention nach §9.5; Migration nach §9.4.

**Implementierungsschritte.**
1. `open()`: Verzeichnis anlegen, PRAGMAs **in der Reihenfolge aus §9.1**
   (`auto_vacuum` vor der ersten Tabelle), `user_version` prüfen, migrieren.
2. `write_batch`: eine Transaktion, `executemany` mit
   `ON CONFLICT DO NOTHING`, liefert die Anzahl tatsächlich eingefügter Zeilen
   (`cursor.rowcount` bzw. `total_changes`-Differenz).
3. `run_retention(now)`: blockweises Löschen, Zeitbudget 200 ms je Lauf.
4. `db_bytes()` über `page_count * page_size`.
5. `open_readonly()` als eigener Einstieg für den Query-Layer
   (`sqlite3.connect("file:…?mode=ro", uri=True)`).
6. Jeder Fehler wird an `LoggingInternalHealth` gemeldet und **nicht** geworfen.

**Tests.** Anlegen; Migration von `user_version=0`; Batch-Insert; Dedupe über
`(producer_id, event_id)`; Retention nach Alter, nach Anzahl, nach Größe;
Keyset-Pagination liefert stabile Seiten bei parallelem Schreiben.
**Negativtests.** Datei ist ein Verzeichnis; `user_version` höher als bekannt
(⇒ Nur-Lesen, kein Löschen); Datei ist keine SQLite-Datei;
`details_json` nicht serialisierbar.
**Failure Tests.** DB-Datei schreibgeschützt; Verzeichnis nach dem Öffnen
entfernt; `disk I/O error` über eine gepatchte `executemany`;
`database is locked` (zweite Verbindung hält eine exklusive Transaktion);
Retention wirft mitten im Lauf.
**Akzeptanzkriterien.**
- Derselbe Serverrecord zweimal geschrieben ⇒ genau **eine** Zeile, kein Fehler.
- 10.000 Records in Batches à 200 in unter 5 s (Regressionswächter).
- Ein schreibgeschützter Store setzt `FAILED_STORE`, wirft nicht und lässt
  `write_batch` `0` liefern.
- Bei einem Leser mit offener Abfrage bleibt `write_batch` erfolgreich (WAL).
**Evidence.** Testlauf; zusätzlich ein Diagnoseskript außerhalb des Produktrepos,
das eine echte Datei anlegt, 50.000 Records schreibt, Retention ausführt und
Dateigröße, Zeilenzahl und Dauer ausgibt.

---

## OBS-05 — Worker + Manager + Shutdown

**Scope.** `worker.py`, `manager.py`; Lebenszyklus, Batching, Flush,
Retention-Taktung, Health-Verdrahtung.

**Non-Scope.** Noch kein Handler, kein Adapter, keine UI, keine Settings.

**Dateien.** `NEU core/observability/{worker,manager}.py`,
`NEU tests/test_observability_worker.py`.
**Geändert:** noch keine bestehende Datei.

**Sollzustand.** `ObservabilityManager` ist das einzige nach außen sichtbare
Objekt: `start()`, `stop(timeout)`, `apply_config(cfg)`, `ingress`,
`query_service`, `health_snapshot()`.

**Implementierungsschritte.**
1. `LoggingWorker` als `threading.Thread(name="RealtimeSTT-Observability",
   daemon=True)`.
2. Schleifenkörper vollständig in `try/except BaseException` (§11.4).
3. Sentinel-basiertes Stoppen mit hartem Zeitbudget.
4. `logging.records_dropped` / `logging.recovered` werden **im Worker**
   erzeugt und direkt geschrieben (Regel G-6).
5. `apply_config` ändert Level, Retention, Sinks, Buffergröße zur Laufzeit;
   `store_enabled` und `db_path` erfordern Neustart (Design in
   `LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md §13.4`).

**Tests.** Start/Stop mehrfach; Flush bei Shutdown; Retention-Taktung;
`records_dropped` erscheint genau einmal nach Erholung.
**Negativtests.** `stop()` ohne `start()`; `start()` zweimal;
`apply_config` mit ungültigen Werten.
**Failure Tests.** Store wirft dauerhaft ⇒ Worker läuft weiter, Health
`FAILED_STORE`, Anwendung unbeeinflusst. Worker-Schleifenkörper wirft
`RuntimeError` ⇒ Schleife läuft weiter, `worker_errors` steigt.
Shutdown mit 9000 Records in der Queue ⇒ `stop(2.0)` kehrt in ≤ 2,5 s zurück
und meldet `dropped_shutdown`.
**Akzeptanzkriterien.**
- Nach `stop()` ist kein Thread mehr aktiv (`threading.enumerate()`).
- Kein Test hinterlässt einen laufenden Worker (wichtig, weil die Suite mit
  `unittest` **und** `pytest` läuft).
**Evidence.** Testlauf; `threading.enumerate()`-Prüfung in `tearDown`.

---

## OBS-06 — UnifiedLogHandler

**Scope.** `adapters/python_logging.py` und die Registrierung in
`core/logging_setup.py`.

**Non-Scope.** Datei- und Stdout-Handler bleiben **unverändert** bestehen.

**Dateien.**
```text
NEU      core/observability/adapters/python_logging.py
GEAENDERT core/logging_setup.py     (additiv: optionaler dritter Handler)
GEAENDERT app.py                    (Manager bauen, an setup_logging und
                                     an den Rest weiterreichen)
NEU      tests/test_observability_handler.py
```

**Sollzustand.**
```python
def setup_logging(config, *, observability=None) -> None:
    ...                       # unveraendert
    if observability is not None:
        handler = UnifiedLogHandler(observability.ingress, normalizer)
        handler.setLevel(observability.level)     # NIE unter INFO als Default
        root_logger.addHandler(handler)
```

**Implementierungsschritte.**
1. `UnifiedLogHandler(logging.Handler)` mit Wiedereintrittssperre (Regel G-1)
   und überschriebenem `handleError` (Regel G-3).
2. `emit`: normalisieren → `ingress.submit`. Kein `format()`-Aufruf, kein I/O.
3. Filter, der Records des Loggers `observability.internal` verwirft
   (redundant zu `propagate=False`, aber billig).
4. `app.py`: `ObservabilityManager` **vor** `setup_logging` bauen und starten,
   damit auch `AppConfig.load`-Meldungen erfasst werden — **Reihenfolge
   beachten:** `AppConfig.load()` läuft heute vor `setup_logging`
   (`app.py:147-148`); dessen Meldungen gehen ohnehin verloren. Das bleibt so.

**Tests.** Eine `logger.info`-Zeile erzeugt genau einen Record mit korrektem
`component`/`channel`/`level`. `exc_info` landet als Text in
`details["exception"]`. Die vier `extra`-Felder aus
`logging_setup.JsonFormatter:39` werden übernommen.
**Negativtests.** Logzeile mit fehlerhaftem `%`-Format; `extra` mit einem Objekt,
dessen `__str__` wirft; Logzeile aus einem Thread ohne Namen.
**Failure Tests.** Ingress liefert immer `False` ⇒ keine Ausnahme, kein stderr
je Zeile. Normalizer wirft ⇒ `handleError` zählt, Anwendung läuft weiter.
Rekursionstest: der Store loggt seinen eigenen Fehler über `logging` ⇒ **kein**
unbegrenztes Wachstum, Nachweis über eine Obergrenze der erzeugten Records.
**Akzeptanzkriterien.**
- Datei- und Stdout-Ausgabe sind Zeile für Zeile identisch zum Zustand vor der
  Änderung (Vergleich zweier `client.log` aus demselben Skript).
- Ohne `observability`-Parameter verhält sich `setup_logging` **exakt** wie
  heute (Rückwärtskompatibilität für Tests, die es direkt aufrufen).
**Evidence.** Testlauf; Diff zweier erzeugter `client.log`-Dateien.

---

## OBS-07 — ServerLiveAdapter + Fan-out-Hook

**Scope.** `adapters/server_live.py` und der additive Beobachterschlitz in
`core/session_coordinator.py` gemäß `LOGGING_CODE_INTEGRATION_AUDIT.md §2.4`.

**Non-Scope.** **Keine** Änderung an `event_stream.py`, `event_protocol.py`,
`event_normalizer.py`, `feedback_reducer.py` oder am Feedbackpfad.
**Keine** Nutzung von `STTController.on_event_stream_event`.

**Dateien.**
```text
NEU      core/observability/adapters/server_live.py
GEAENDERT core/session_coordinator.py   (ein Attribut, zwei Aufrufe, ~14 Zeilen)
GEAENDERT core/controller.py            (eine Zeile Verdrahtung im __init__)
NEU      tests/test_observability_server_live.py
GEAENDERT tests/test_session_coordinator.py  (neue Faelle, bestehende unveraendert)
```

**Sollzustand.**
```python
# session_coordinator.py -- additiv
self.on_observation: Optional[
    Callable[[SessionContext, EventProtocolResult], None]
] = None

def _notify_observer(self, result: EventProtocolResult) -> None:
    observer = self.on_observation
    if observer is None:
        return
    try:
        observer(self._context, result)
    except Exception:
        pass          # Fehlerbehandlung liegt in der Logging-Failure-Domain

async def _handle_event(self, binding, result) -> bool:
    self._notify_observer(result)        # <-- ERSTE Anweisung
    ...                                  # alles Uebrige unveraendert

def _handle_control(self, binding, result) -> None:
    self._notify_observer(result)        # <-- ERSTE Anweisung
    ...                                  # alles Uebrige unveraendert
```

**Implementierungsschritte.**
1. Schlitz und `_notify_observer` ergänzen; beide bestehenden Methoden bekommen
   je **eine** neue erste Zeile.
2. `ServerLiveAdapter.observe(context, result)` normalisiert und übergibt an den
   Ingress.
3. `STTController.__init__`: `self.session_coordinator.on_observation =
   self._observability.observe_server_result`, nur wenn ein Ingress übergeben
   wurde.

**Tests.** Ein `log.event` erzeugt genau einen Record mit `event_id`,
`server_cursor`, `replayed`, `raw`. Ein `log.gap` erzeugt einen Record. Ein
Duplikat (das `on_event` nie erreicht) erzeugt einen Record mit `replayed=True`.
Ein Event mit falscher Session (das `_handle_event` verwirft) wird trotzdem
beobachtet.
**Negativtests.** `on_observation = None`; Beobachter wirft; Beobachter
blockiert 2 s (der Feedbackpfad darf trotzdem laufen — dieser Test belegt die
Grenze und begründet, warum der Ingress nie blockiert).
**Failure Tests.** Beobachter wirft `MemoryError` ⇒ `_handle_event` liefert
weiterhin `True`, `confirm_event` wird aufgerufen, der Cursor wird committed.
**Akzeptanzkriterien — die wichtigsten des ganzen Pakets.**
- Ein werfender Beobachter verändert **weder** den Rückgabewert von
  `_handle_event` **noch** den Cursorstand. Nachzuweisen über den echten
  `EventProtocolProcessor` mit echtem `EventCursorStore` auf einer temporären
  Datei, **nicht** über ein Double.
- Die bestehende Suite `tests/test_session_coordinator.py`,
  `tests/test_event_stream.py`, `tests/test_feedback_integration.py` und
  `tests/test_trigger_feedback_contract.py` läuft **unverändert** grün.
- `git diff` zeigt in `session_coordinator.py` **keine** Änderung an einer
  bestehenden Zeile außer den zwei eingefügten Aufrufen.
**Evidence.** Testlauf, `git diff --stat` und der vollständige Diff der
geänderten Produktdatei im Abschlussbericht.

---

## OBS-08 — Strukturierte Client-Hooks

**Scope.** `adapters/client_events.py` plus die Aufrufe an den in
`LOGGING_CODE_INTEGRATION_AUDIT.md §4` aufgeführten Stellen, **ohne** die
HOT-PATH-Stellen.

**Non-Scope.** Keine fachliche Änderung. Kein Umbau des Triggerpfads. Keine
neuen `CanonicalEventType`-Werte. Keine Änderung an `feedback_*`.

**Dateien.**
```text
NEU      core/observability/adapters/client_events.py
GEAENDERT core/controller.py       (Aufrufe an ~10 Stellen, je 1-3 Zeilen)
GEAENDERT core/stt_session.py      (Aufrufe an ~6 Stellen)
GEAENDERT core/audio_capture.py    (Zaehler + Start/Stop, KEINE Hot-Path-Zeile)
GEAENDERT ui/application.py        (Lifecycle, Settings-Apply, Hotkey/Command)
GEAENDERT ui/core_bridge.py        (Kommando-Korrelation, Ingress durchreichen)
GEAENDERT ui/hotkeys.py            (Auslösung, heute voellig ungeloggt)
NEU      tests/test_observability_client_events.py
```

**Sollzustand.** Jede Stelle erzeugt **eine** Zeile der Form
`self._obs.event("client.trigger.sent", channel="audit", level="INFO",
component="stt_session", command_id=cid, session_id=…, generation=…,
details={"action": action, "source": source})`. `self._obs` ist im Zweifel
`NULL_INGRESS`.

**Implementierungsschritte (Reihenfolge nach Risiko, aufsteigend).**
1. `ui/hotkeys.py`, `ui/core_bridge.py`, `ui/application.py` — reine
   UI-Beobachtung, kein fachlicher Zustand.
2. `core/audio_capture.py` — nur Start/Stop plus Zählerattribute; die
   Hot-Path-Methoden erhöhen ausschließlich `int`-Attribute.
3. `core/stt_session.py` — `send_start`, `send_trigger`, `_resolve_trigger_ack`,
   `_wait_for_hello`, `_record_failure`, `_update_transport`.
4. `core/controller.py` — `_begin_start_locked`, `_await_start_attempt`,
   `_fail_start_attempt`, `_handle_dictation_interrupted`, `_handle_error_event`,
   `_emit_final_result`, `apply_runtime_config`.
5. Der periodische Aggregatrecord (`client.audio.stream_stats`, 5 s) wird vom
   **Worker** erzeugt, indem er die Zähler abfragt — nicht von einer Task im
   Core-Loop. Damit entsteht kein zusätzlicher Task im kritischen Loop.

**Tests.** Je Hook ein Test, der über einen aufzeichnenden Fake-Ingress prüft,
dass genau ein Record mit den erwarteten Korrelationsfeldern entsteht.
`command_id` verbindet `client.trigger.sent` und `client.trigger.ack_received`.
**Negativtests.** Alle Hooks mit `NULL_INGRESS` ⇒ kein Verhaltensunterschied.
Hook bei `session_id is None`.
**Failure Tests.** Ingress wirft an **jeder** Aufrufstelle (parametrisiert) ⇒
kein Verhaltensunterschied. Das ist der Test, der die Additivität beweist.
**Akzeptanzkriterien.**
- **Die vollständige bestehende Client-Suite bleibt grün, ohne dass ein
  bestehender Test geändert wird.** Neue Tests dürfen dazukommen.
- Kein `logger.*`-Aufruf wird entfernt oder umformuliert. Die strukturierten
  Events kommen **zusätzlich**.
- In keiner HOT-PATH-Funktion steht ein `submit`, ein `format`, ein `json` oder
  ein Attributzugriff auf den Ingress. Nachweis über einen Test, der den
  Quelltext der genannten Funktionen liest.
**Evidence.** Testlauf; die Liste der geänderten Zeilen je Datei; ein manuelles
Ablaufprotokoll (siehe OBS-13).

---

## OBS-09 — Query Layer

**Scope.** `query/base.py`, `query/local.py`, `query/service.py` gemäß
`LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md §15`.

**Non-Scope.** Keine UI. Kein Remote-Provider. Kein Qt.

**Dateien.** `NEU core/observability/query/{__init__,base,local,service}.py`,
`NEU tests/test_observability_query.py`.

**Implementierungsschritte.**
1. Datenmodelle exakt wie im Entwurf.
2. `LocalLogProvider` mit eigener read-only Verbindung und der Keyset-Abfrage
   aus §9.6; Parameterbindung ausschließlich über Platzhalter.
3. `fetch_raw(record_id)` als eigener `SELECT`.
4. `LogQueryService` als Registry.

**Tests.** Jeder Filter einzeln; Kombinationen; Keyset-Pagination über drei
Seiten; `newest_first=False`; Zeitbereich; Freitext.
**Negativtests.** `limit` über `max_limit`; unbekannte `provider_id`; `cursor`
mit fremdem Format; Filterwert mit `'` und `%` (SQL-Injektionsversuch,
Erwartung: als Literal behandelt).
**Failure Tests.** DB-Datei während der Abfrage gelöscht; Store gesperrt
(`busy_timeout` läuft ab) ⇒ `QueryPage` mit `state=ERROR` und leeren Records,
**keine** Ausnahme.
**Akzeptanzkriterien.**
- `query()` wirft unter keinem geprüften Umstand.
- Bei parallelem Schreiben liefern drei aufeinanderfolgende Seiten keine
  doppelte und keine übersprungene `record_id`.
- Kein `PySide6`-Import.
**Evidence.** Testlauf.

---

## OBS-10 — Settings-Integration

**Scope.** `LoggingObservabilityConfig`-Dataclass, `SETTING_DEFINITIONS`,
sechster Tab, Apply-Weg gemäß `LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md §13`.

**Non-Scope.** Keine Änderung an bestehenden Feldern oder deren Bedeutung.
Kein Admin-Key. Keine Logansicht.

**Dateien.**
```text
GEAENDERT core/config.py                (neue Dataclass + Feld in LoggingConfig
                                         + validate + _from_dict)
GEAENDERT core/settings_metadata.py     (12 neue SettingDefinition)
GEAENDERT ui/settings_dialog.py         (ein Eintrag in TAB_NAMES)
GEAENDERT core/controller.py            (eine Zeile in apply_runtime_config)
GEAENDERT config.yaml                   (neuer Unterabschnitt mit Defaults)
GEAENDERT tests/test_config.py          (neue Faelle)
NEU      tests/test_observability_settings.py
```

**Implementierungsschritte.**
1. `LoggingObservabilityConfig` mit `validate()`; `LoggingConfig` bekommt
   `observability: LoggingObservabilityConfig`.
   **Achtung:** `LoggingConfig` wird heute über `_build(LoggingConfig, …)`
   gebaut (`config.py:945`), was verschachtelte Dataclasses **nicht** auflöst —
   dieselbe Sonderbehandlung wie bei `history` (`config.py:924-931`) ist nötig.
2. `AppConfig.validate()` um `self.logging.observability.validate()` ergänzen.
3. `SETTING_DEFINITIONS` erweitern; `TAB_NAMES` um `"Logging & Diagnose"`.
4. Eine Zeile in `apply_runtime_config` nach `_install_runtime_config`.

**Tests.** Laden mit und ohne den neuen Abschnitt; `save_user`/`load`-Rundlauf;
Sichtbarkeitsregeln; `build_candidate` erzeugt einen validen Kandidaten.
**Negativtests.** `retention_days` negativ; `file_sink_format` unbekannt;
`queue_high_size` = 0; ein altes `config.yaml` **ohne** den Abschnitt lädt
weiterhin.
**Failure Tests.** Benutzer-`config.yaml` mit einem unbekannten Feld unterhalb
von `logging.observability` ⇒ der gesamte Override wird verworfen (bestehendes
Verhalten, `config.py:852-860`) — der Test hält das Verhalten fest, **repariert
es nicht** (Befund S-3).
**Akzeptanzkriterien.**
- Eine reine Observability-Änderung löst **keinen** Reconnect und **keinen**
  Audio-Neustart aus. Nachzuweisen über `apply_runtime_config` mit einem
  Fake-Session, dessen `reconfigure` bei Aufruf durchfällt.
- `tests/test_config.py` bleibt ohne Änderung an bestehenden Fällen grün.
**Evidence.** Testlauf; ein gespeichertes und wieder geladenes `config.yaml`.

---

## OBS-11 — Minimal Log View

**Scope.** `ui/logs/*` gemäß `LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md §14`.

**Non-Scope.** Kein Export, keine gespeicherten Filter, keine Charts, keine
Farbregeln außer Level, kein Mischbetrieb Live/Historie.

**Dateien.**
```text
NEU      ui/logs/{__init__,log_window,log_page,log_table_model,
                  log_filter_bar,log_detail_view,log_query_controller}.py
GEAENDERT ui/tray.py            (Menueintrag "Logs anzeigen")
GEAENDERT ui/application.py     (Fenster halten, oeffnen, beim Shutdown schliessen)
NEU      tests/test_log_view.py
```

**Implementierungsschritte.**
1. `LogTableModel` mit sieben Spalten.
2. `LogQueryController` mit `ThreadPoolExecutor(max_workers=1)` und Entprellung.
3. `LogFilterBar` erzeugt `QueryFilter`.
4. `LogDetailView` lädt `raw` bei Auswahl nach.
5. `LogPage` mit `QTimer` (250 ms) für den Live-Modus.
6. `LogWindow` mit `hide()` statt `close()`; Geometrie über `QSettings`.

**Tests.** Modell liefert korrekte `rowCount`/`data`; `append_page` hängt an;
Filterleiste erzeugt den erwarteten `QueryFilter`; Kontextaktion setzt den
Filter. Qt-Tests im `offscreen`-Modus, wie in den bestehenden
`tests/test_ui_widgets.py`/`test_ui_application.py`.
**Negativtests.** Abfrage liefert `QueryPage` mit `state=ERROR` ⇒ Statuszeile
zeigt den Fehler, die Tabelle bleibt leer, kein Absturz. Leeres Ergebnis.
**Failure Tests.** Store gelöscht, während das Fenster offen ist. Manager
angehalten (`FAILED_WORKER`) ⇒ Statuszeile zeigt es, Live-Timer läuft leer
weiter, kein Absturz.
**Akzeptanzkriterien.**
- Kein `sqlite3`-Import unterhalb von `ui/`.
- Kein Zugriff auf `core.observability.storage` aus `ui/`.
- Der Live-Modus erzeugt bei 500 Records/s **keine** spürbare Verzögerung der
  Oberfläche (gemessen über die Zeit zwischen zwei `QTimer`-Durchläufen).
**Evidence.** Testlauf; Bildschirmfoto der Ansicht mit realen Daten im
Abschlussbericht.

---

## OBS-12 — Optionaler JSONL-Sink

**Scope.** `sinks/base.py`, `sinks/jsonl_file.py`. Abhängig von OD-06.

**Non-Scope.** Kein Ersatz für den bestehenden `RotatingFileHandler`.

**Dateien.** `NEU core/observability/sinks/{__init__,base,jsonl_file}.py`,
`NEU tests/test_observability_sinks.py`.

**Implementierungsschritte.** Eine Zeile JSON je Record, `schemaVersion` als
erstes Feld; Tagesrotation über den Dateinamen; Größengrenze je Datei;
Fehler deaktivieren den Sink und melden **einmal** an Health.

**Tests.** Format; Rotation; deaktivierter Sink.
**Negativtests.** Verzeichnis nicht anlegbar; Datei schreibgeschützt.
**Failure Tests.** Platte voll (simuliert über eine wirft-Datei); Verzeichnis
während des Betriebs entfernt.
**Akzeptanzkriterien.** Ein Sink-Fehler beeinflusst den Store nicht; der Store
schreibt weiter. `write_batch` und der Sink sind in dieser Reihenfolge
aufgerufen, sodass ein Sink-Fehler nie einen SQLite-Rollback auslöst.
**Evidence.** Testlauf; eine erzeugte JSONL-Datei.

---

## OBS-13 — Failure-, Isolations- und Performance-Gate

**Scope.** Die Nachweise, die belegen, dass die Logging-Infrastruktur den
Produktionspfad **nicht** verändert. Details in `LOGGING_TEST_MATRIX.md`.

**Non-Scope.** Keine Codeänderung außer der Behebung dessen, was hier auffällt.

**Sollzustand.** Alle F-Tests aus `LOGGING_V1_ABGRENZUNG_ENTWURF.md §6` sind
umgesetzt und laufen automatisiert; zusätzlich eine **manuelle Abnahme am
realen Produktionspfad**.

**Implementierungsschritte.**
1. Automatisierte Failure-Isolationstests (Matrix, Gruppe F).
2. Performance-Messung mit und ohne Logging (Matrix, Gruppe P).
3. **Manuelle Abnahme gegen den echten Server**, protokolliert:
   - Anwendung starten, Diktat per Hotkey, Text wird eingefügt.
   - `observability.sqlite3` prüfen: `client.trigger.sent` und
     `client.trigger.ack_received` haben dieselbe `command_id`;
     `transcription.completed` des Servers ist vorhanden;
     die Zeitreihe ist lückenlos.
   - DB-Datei schreibgeschützt setzen, Anwendung neu starten, Diktat
     wiederholen: Text wird weiterhin eingefügt, LED und Ton reagieren,
     Health meldet `FAILED_STORE`.
   - Server neu starten, während der Client läuft: der volle Replay erzeugt
     **keine** doppelten Zeilen (Nachweis über
     `SELECT event_id, COUNT(*) FROM logs GROUP BY event_id HAVING COUNT(*)>1`
     — Ergebnis muss leer sein).
   - Log-Ansicht öffnen, nach Session filtern, Detail und Raw JSON prüfen.
   - Anwendung beenden: keine Restthreads, DB konsistent.

**Akzeptanzkriterien.**
- **Jeder** F-Fall aus §6 des Abgrenzungsentwurfs ist grün.
- Das manuelle Protokoll liegt vor und benennt Server, Datum, Clientversion.
- **Ohne** das manuelle Protokoll gilt V1 als „teilweise", nicht als „fertig".
**Evidence.** Testprotokolle unter
`ARBEITSDATEIEN/AP_THEMA_LOGGING/analyse_code_integration/evidence/`,
Bildschirmfotos, SQL-Ausgaben, die gemessenen Zeiten.

---

# Übergreifende Regeln für alle Pakete

```text
1. Jedes Paket ist fuer sich lauffaehig und laesst die vollstaendige
   bestehende Client-Suite gruen, OHNE dass ein bestehender Test geaendert
   wird. Muss ein bestehender Test geaendert werden, ist das ein Signal,
   dass das Paket fachliches Verhalten aendert -- dann anhalten und die
   Architektur pruefen (Abgrenzungsentwurf §10).

2. Kein Paket faengt an, die Triggerarchitektur zu reparieren. Auffaelligkeiten
   werden in LOGGING_OPEN_DECISIONS.md bzw. im Aenderungslog notiert,
   nicht behoben (Auftrag §21).

3. Reihenfolge der Aufrufe beim Start:
       ObservabilityManager bauen und starten
       setup_logging(config.logging, observability=manager)
       ... alles Uebrige wie heute
   Reihenfolge beim Beenden (umgekehrt, mit einer Ausnahme):
       DesktopApplication.shutdown()  ... wie heute ...
       bridge.stop(timeout=10.0)
       manager.stop(timeout=2.0)      <-- ZULETZT, damit Shutdownfehler
                                          des Cores noch erfasst werden

4. Ein Testdouble des Ingress ist erlaubt und noetig. Ein Testdouble des
   SessionCoordinators oder des EventProtocolProcessors ist im
   Isolationsnachweis (OBS-07) NICHT erlaubt -- dort wird die echte Klasse
   verwendet, weil ein Double sonst nur sein eigenes Verhalten beweist.

5. Der Commit erfolgt als EIN klar benannter Commit am Ende, nach OBS-13,
   mit `git diff --check` und der ausdruecklichen Pruefung, dass der Diff
   keine Triggerarchitektur-Reparatur enthaelt (Abgrenzungsentwurf §11).
```

# Geänderte Produktdateien im Gesamtüberblick

| Datei | Art der Änderung | Umfang |
|---|---|---|
| `core/session_coordinator.py` | 1 Attribut, 1 Hilfsmethode, 2 eingefügte Aufrufe | ~14 Zeilen, rein additiv |
| `core/logging_setup.py` | optionaler Parameter, optionaler dritter Handler | ~10 Zeilen, rein additiv |
| `app.py` | Manager bauen/starten/stoppen | ~15 Zeilen |
| `core/controller.py` | Ingress im `__init__`, Verdrahtung, ~10 Beobachtungsaufrufe | ~35 Zeilen, additiv |
| `core/stt_session.py` | ~6 Beobachtungsaufrufe | ~20 Zeilen, additiv |
| `core/audio_capture.py` | Zählerattribute + 2 Beobachtungsaufrufe | ~15 Zeilen, additiv |
| `core/config.py` | neue Dataclass, Feld, Validierung, Sonderbehandlung im `_from_dict` | ~50 Zeilen |
| `core/settings_metadata.py` | 12 neue Definitionen | ~60 Zeilen, additiv |
| `ui/application.py` | Manager durchreichen, Lifecycle-Hooks, Fenster halten | ~30 Zeilen |
| `ui/core_bridge.py` | Ingress durchreichen, Kommando-Korrelation | ~20 Zeilen |
| `ui/hotkeys.py` | Beobachtung der Auslösung | ~8 Zeilen |
| `ui/settings_dialog.py` | ein Tabname | 1 Zeile |
| `ui/tray.py` | ein Menüeintrag | ~6 Zeilen |
| `config.yaml` | neuer Unterabschnitt | ~16 Zeilen |
| `voice-stt-client.spec` | **keine Änderung** (Befund M-4) | – |
| `voice-stt-server`, `led_controller_respeaker-v3` | **keine Änderung** | – |

**Summe:** ~300 geänderte Zeilen in 13 bestehenden Dateien, davon der
allergrößte Teil additiv, plus ~15 neue Module und ~12 neue Testdateien.
