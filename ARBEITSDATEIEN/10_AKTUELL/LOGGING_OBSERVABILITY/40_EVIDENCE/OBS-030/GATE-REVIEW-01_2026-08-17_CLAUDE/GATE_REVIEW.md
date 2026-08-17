# OBS-030 – Gate Review (unabhängig, frische Session)

Datum: 2026-08-17
Prompt: `30_AUSFUEHRUNG/Prompts/OBS-030_GATE_REVIEW.md`
Geprüfter Run: `RUN-OBS-030-01_2026-08-17_CLAUDE`
Workspace: `voice-stt-client/workspaces/einheitliche-triggerarchitektur`
Branch: `feat/einheitliche-triggerarchitektur`, HEAD `b363346`
Interpreter: Python 3.12.10 (global), pytest 9.1.1

## Ergebnis

**OBS-030 GATE FAIL**

Geprüft wurde der tatsächliche Repositoryzustand, `git diff`/`git status`,
eigenständige Testläufe und zusätzlich eigene Laufzeitproben — nicht der
Abschlussbericht. Die Kernmechanik (Persistenz, Dedupe, Retention,
Nebenläufigkeit, Shutdown-Buchhaltung) ist belastbar. Die Gate-Kriterien
„interne Worker-/DB-Fehler bleiben isoliert" und „Evidence-Konsistenz" sind
jedoch nicht erfüllt; zusätzlich fehlt eine ausdrücklich normative
Sicherheitsauflage (P-8).

---

## 1. Blockierende Befunde

### B-1 Keine Fehlerisolation auf Schleifenebene im Worker

**Dateien:** `core/observability/worker.py:115-132` (`run`),
`core/observability/worker.py:167-174` (`_iteration`),
`core/observability/worker.py:203-223` (`_prepare_record`)

**Norm:** `LOGGING_ARCHITEKTUR_FREEZE_V1.md §8.3`, Zeile „Worker-Ausnahme in
der Schleife": *gefangen, `worker_errors++`, Schleife läuft weiter. Bricht sie
dennoch ab: Ingress wechselt in „nur verwerfen und zählen". Kein
Neustartversuch* → Health `FAILED_WORKER`. Ferner `§8.1 G-2/G-4` (jede Ausgabe
aus `core/observability/` läuft über den nicht propagierenden Notfallkanal und
ist hart ratenbegrenzt), `§8.4` („Still. Nur Health, ratenbegrenztes stderr"),
`CONTRACTS §11.2` (`FAILED_WORKER`, Zähler `worker_errors`). Gate-Kriterium
„interne Worker-/DB-Fehler bleiben isoliert".

**Befund:** `run()` ruft `self._iteration()` in einer `while`-Schleife **ohne
jede `try/except`-Klammer** auf. Einzelne Teilschritte sind zwar abgesichert
(`_write_with_policy`, `_write_sink`, `_write_direct`, `store.run_retention`),
die Schleife selbst ist es nicht. Zusätzlich liegt in `_prepare_record` die
Zeile `return dataclasses.replace(record, raw=redacted)` (`worker.py:223`)
**außerhalb** des eigenen `try`-Blocks, ist also ein realer, im Produktionscode
vorhandener Austrittspfad aus dem geschützten Bereich.

`LoggingHealthState.FAILED_WORKER` und `LoggingInternalHealth.record_worker_error`
haben im gesamten Produktionscode **null Aufrufer** (verifiziert per
`grep -rn "record_worker_error\|FAILED_WORKER" --include=*.py`; Treffer nur in
`health.py` selbst und in OBS-020-Tests).

**Nachweis (eigene Laufzeitprobe, Ingress-`drain` wirft einmalig):**

```text
before boom: rows = 1 | alive = True | state = ok
after  boom: worker alive = False
             health.state = ok
             worker_errors = 0
             live observability threads = []
submit() after worker death returns: [True, True, True, True, True]
health.is_failed() -> False
rows written after death: 1
queue depth (records stranded): 5
```

Zusätzlich schreibt Pythons `threading`-Excepthook den **vollständigen
Traceback ungefiltert und unratenbegrenzt nach stderr** — genau der Ausgabeweg,
den `G-2`/`G-4` für alles aus `core/observability/` ausschließen.

**Wirkung im Betrieb:** Der Worker stirbt still, `SQLiteLogStore.close()` und
`JsonlSink.close()` laufen im `finally`, Health meldet weiterhin `OK`,
`Ingress.is_failed()` bleibt `False`, `submit()` liefert weiter `True` — bis die
Queue voll ist. Ab dann ist die gesamte Diagnose tot, während die Statusanzeige
`OK` behauptet. Das ist die „blinde Stelle ohne Zaehler und ohne Meldung", die
`ARCH §7.3`/`§8` ausdrücklich verhindern sollen.

**Minimale erforderliche Korrektur:**

1. `run()`: `self._iteration()` in `try/except Exception` klammern →
   `self._health.record_worker_error("worker_loop_failed", str(exc)[:200])`,
   Schleife fortsetzen.
2. Bricht die Schleife dennoch ab (bzw. bei wiederholtem Fehlschlag):
   `self._health.set_state(LoggingHealthState.FAILED_WORKER, ...)` **vor** dem
   `_shutdown_flush()`, damit `Ingress.is_failed()` greift und der Ingress in
   „nur verwerfen und zählen" wechselt. Kein Neustartversuch (`§8.3`).
3. `_prepare_record`: `dataclasses.replace(...)` in den bestehenden
   `try`-Block ziehen.
4. Ergänzend (`§8.3`): Der Verwurf im Ingress bei `is_failed()`
   (`ingress.py:111-112`) erhöht heute **keinen** Zähler — „verwerfen **und
   zählen**" verlangt beides.
5. Test: Worker mit einem einmalig werfenden `drain`/`_prepare_record`;
   erwartet `worker_errors >= 1`, Schleife läuft weiter; bei dauerhaftem
   Fehlschlag `state == FAILED_WORKER` und `submit()` liefert `False`.

### B-2 Evidence widerspricht dem Code (Gate-Kriterium „Evidence-Konsistenz")

**Datei:** `40_EVIDENCE/OBS-030/RUN-01_2026-08-17_CLAUDE/CONTRACT_COVERAGE.md`,
Abschnitt „Failure Domain (ARCH §8)", Zeile „Worker-Ausnahme in der Schleife".

Dort steht *„gefangen, `worker_errors`/`store_errors`++, Schleife läuft weiter"*
mit dem Nachweis *„jede `except Exception` in `worker.py`s Verarbeitungspfad"*;
die Health-Spalte ist auf „—" gesetzt, obwohl der Freeze dort `FAILED_WORKER`
fordert. Nach B-1 trifft die Aussage für die Schleifenebene nicht zu, und
`worker_errors` wird nirgends erhöht. Die Evidence beschreibt damit einen
Zustand, den der Code nicht hat.

**Minimale erforderliche Korrektur:** Nach Behebung von B-1 die Zeile
korrigieren (inkl. Health-Spalte `FAILED_WORKER`) und den neuen Test
referenzieren.

### B-3 P-8 nicht umgesetzt: Speicher- und Sink-Pfade außerhalb des Benutzerprofils werden akzeptiert

**Dateien:** `core/config.py:812-851` (`LoggingObservabilityConfig.validate`),
`core/observability/manager.py:90-106` (`db_path`/`file_sink_dir`-Auflösung)

**Norm:** `CONTRACTS §4.3 P-8`: *„Es wird KEIN eigenes Verzeichnis mit
abweichenden Rechten angelegt und **KEIN Pfad ausserhalb des Benutzerprofils
akzeptiert**. Ein konfigurierter absoluter Pfad wird gegen das Benutzerprofil
geprueft."* sowie `R-7`. `§5.1` weist `logging.observability.db_path` genau dem
in OBS-030 gebauten Store zu; OBS-030 ist das erste Work Package, in dem diese
Pfade tatsächlich aufgelöst und benutzt werden.

**Befund:** `validate()` prüft ausschließlich den Typ (`str` oder `None`). Der
Manager macht daraus ohne weitere Prüfung `Path(db_path)` bzw.
`Path(file_sink_dir)`, `SQLiteLogStore.open()` legt das Zielverzeichnis per
`mkdir(parents=True, exist_ok=True)` an.

**Nachweis:**

```text
validate() accepted db_path outside %LOCALAPPDATA%: C:\ProgramData\somewhere-else\observability.sqlite3
DEFAULT_LOCAL_APP_DIR = C:\Users\marco\AppData\Local\RealtimeSTT Client
```

Damit können Store, `-wal`/`-shm` und der JSONL-Sink — die nachweislich
Transkriptinhalte und `raw`-Payloads tragen können — in einem Verzeichnis mit
fremder ACL landen. P-9 („beim Anlegen wird geprüft, dass `-wal`/`-shm` im
selben Verzeichnis entstehen") existiert ebenfalls nur als Testbeobachtung
(`test_obs030_sqlite_store.py:111-118`), nicht als Prüfung zur Laufzeit.

**Minimale erforderliche Korrektur:** In `LoggingObservabilityConfig.validate()`
(Vorbild: `EventStreamConfig.validate`, das bereits einen absoluten Pfad
verlangt) einen gesetzten `db_path`/`file_sink_dir` auflösen und gegen das
Benutzerprofil bzw. `DEFAULT_LOCAL_APP_DIR` prüfen; Ablehnung mit `ValueError`.
Negativtest ergänzen. Alternativ, falls die Auflage bewusst nach OBS-050
verschoben werden soll: ausdrücklicher `DECISION REQUIRED`-Vorgang mit Eintrag
in `LOGGING_DECISIONS_FREEZE_V1.md` — stillschweigend darf sie nicht entfallen.

---

## 2. Weitere Befunde (Entscheidung oder Korrektur erforderlich, nicht allein gate-entscheidend)

### W-1 Ein defekter Store legt den intakten JSONL-Sink mit still

`core/observability/worker.py:194-201`: `_write_sink(prepared)` läuft nur
`if ok`. Ist der Store degradiert, ausgesetzt (60-s-Circuit-Breaker) oder
`disk full`, erhält der Sink **nichts** — obwohl er eine eigene Fehlerdomäne
ist (`O-05`) und der Manager mit `_NullStore` genau darauf ausgelegt ist
(„keeps the worker/sink pipeline running … the JSONL sink is independent of
the store", `manager.py:33-36`). `ARCH §8.3` regelt nur die Gegenrichtung
(Sink kaputt → Store läuft weiter).

Nachweis: 20 Records, Store wirft dauerhaft → `sink lines written: 0`,
`health.state = degraded_store`.

Minimale Korrektur: `_write_sink(prepared)` unabhängig vom Store-Ergebnis
aufrufen (Reihenfolge „Store zuerst, Sink danach" nach `§11.1` bleibt
gewahrt) — oder die Kopplung als bewusste Entscheidung dokumentieren.

### W-2 `logging.retention_pressure` entsteht nicht als Record

`worker.py:374-383` meldet die Überschreitung von `max_db_bytes` nur über
`emergency("retention_pressure", …)` auf stderr. `CONTRACTS §5.6` verlangt ein
Health-Warnsignal `logging.retention_pressure`, `§12.4` führt es zusammen mit
`logging.records_dropped` und `logging.recovered` als **vom Worker erzeugten**
strukturierten Record. Die beiden anderen sind als Record umgesetzt, dieser
nicht — inkonsistent.

### W-3 Records, die wegen ausgesetztem/degradiertem Store verworfen werden, sind nirgends gezählt

`_write_with_policy` (`worker.py:227-232`) liefert bei
`_structural_degraded` oder aktivem `_store_paused_until` stumm `(0, 0, False)`.
Während der 60-Sekunden-Pause wächst weder `written` noch ein Drop-Zähler; die
Buchhaltung `enqueued == written + dropped_*` bricht auf. Sichtbar bleibt nur
der Health-State. `ARCH §7.3` kennt für diesen Fall keinen Zähler — entweder
einen ergänzen oder die Lücke ausdrücklich benennen.

### W-4 Kein „leerer Testschreibvorgang" nach der Store-Pause

`ARCH §8.3` verlangt nach der 60-s-Aussetzung eine Prüfung *„mit einem leeren
Testschreibvorgang"*. Umgesetzt ist stattdessen ein regulärer Batch-Versuch;
scheitert er, geht dieser Batch verloren statt nur eine Probe.

### W-5 `LoggingHealthState.DISABLED` wird nie erzeugt

Weder `enabled=False` noch `store_enabled=False` setzen den Zustand; Health
meldet `OK` für eine abgeschaltete Observability (`manager.py:75-77`,
`manager.py:33-54`).

### W-6 `manager.clear_history()` blockiert den Aufrufer bis zu 5 s

`worker.request_clear` wartet auf den Worker-Thread und damit auf Datei-I/O.
Für OBS-050 vormerken: Diese Methode darf nicht direkt aus dem Qt-Mainthread
aufgerufen werden (`O-03`).

### W-7 Kleinere Abweichungen ohne Wirkungsbefund

- `open()` setzt die PRAGMAs in der Reihenfolge `busy_timeout`,
  `foreign_keys`, `journal_mode`, `synchronous`; `§5.2` schreibt
  „in dieser Reihenfolge" `journal_mode`, `synchronous`, `busy_timeout`,
  `foreign_keys`. Funktional unschädlich, formal eine Abweichung.
- `_records_since_retention` zählt gezogene, nicht *geschriebene* Records
  (`§5.6`: „alle 2000 **geschriebenen** Records").
- `stop()` auf einem nie gestarteten Worker (`worker.py:142-143`) lässt
  eingereihte Records ungezählt.

---

## 3. Vorbestehende Umgebungsauffälligkeit (kein OBS-030-Befund)

Zusätzlich zum dokumentierten `lefx.interfaces`-Fehlschlag ist
`tests/test_core_bridge.py::TestCoreBridge::test_async_and_sync_commands_execute_in_worker_loop`
**intermittierend** rot (`StopIteration`): die `wait_until`-Bedingung wartet auf
`commands >= 3 and history >= 1`, aber nicht auf die `local_feedback`-Zustellung,
die anschließend per `next(...)` erwartet wird. In einem von mehreren
Vollläufen dieser Prüfung trat der Fehlschlag auf (`2 failed, 795 passed`),
danach 10× isoliert grün. Die Datei liegt außerhalb des OBS-030-Diffs und
berührt keine Observability-Komponente — keine Regression dieses Pakets,
aber die im Bericht genannte Zahl „796/797 grün" ist nur modulo dieser
Flakiness reproduzierbar.

---

## 4. Eigenständig verifiziert und in Ordnung

Damit der Korrekturlauf diese Punkte nicht erneut prüfen muss:

**Scope/Diff**
- `git diff --check` leer (Exit 0).
- `git diff --stat`: geänderte Bestandsdateien ausschließlich `app.py` (+27/-8),
  `core/config.py` (+101), `core/observability/__init__.py` (+8),
  `core/observability/health.py` (+21/-2). Alles Übrige neu.
- Unverändert: `ui/**`, `core/controller.py`, `core/session_coordinator.py`,
  `core/event_stream.py`, `core/stt_session.py`, `core/logging_setup.py`,
  `core/observability/{ingress,normalizer,redaction,models}.py`,
  `adapters/python_logging.py`. Kein Cross-Workstream-Diff.
- Kein bestehender Test geändert.

**Tests**
- `python -m pytest -q -k obs030` → 82 passed, 10 subtests (eigener Lauf).
- Vollständige Suite reproduziert (795–796 passed); der `lefx.interfaces`-
  Fehlschlag ist unverändert vorbestehend und außerhalb des Diffs.

**Verträge**
- Queue bounded, genau **eine** Queue, **kein** Memory-Ringbuffer
  (`grep deque|ring_buffer|live_buffer` in `core/observability/` → keine
  Treffer).
- Prioritätsregel (`models.py:183-201`) exakt nach `CONTRACTS §1.5` /
  `ARCH §7.2` inkl. `not replayed`; die HIGH-Sonderregel ist **nicht**
  verallgemeinert.
- Wasserstandsregel 75 % / Verwerfen + Zählen wie eingefroren.
- Überlast ist gezählt **und sichtbar**: eigene Probe belegt genau **einen**
  Record `logging.records_dropped` (Channel `performance`, `is_internal=True`)
  mit `{'dropped_watermark': 28, 'dropped_queue_full': 0}` nach der Erholung,
  danach Zähler zurückgesetzt und Zustand wieder `OK`.

**Shutdown**
- Buchhaltung exakt: 1000 eingereiht → `written=20` + `dropped_shutdown=980`
  = 1000; genau **eine** ratenbegrenzte stderr-Zeile
  (`shutdown_flush_incomplete`); `stop(0.5)` liefert `True`; kein
  `RealtimeSTT-Observability`-Thread übrig.

**Nebenläufigkeit**
- 8 Producer-Threads × 1500 Records + gleichzeitig pollender Leser mit
  `PRAGMA query_only = ON`: `enqueued = written = Zeilen in der DB = 12000`,
  keine Drops, `PRAGMA integrity_check = ok`, 0 ungültige `details_json`,
  keine Ausnahme aus `submit()`, ~22 µs/`submit`, kein Thread-Leck.
- N-05 (Fremdthread → `sqlite3.ProgrammingError`), `check_same_thread`
  unverändert, Verbindung erst in `run()` erzeugt (D-4): im Code und in den
  Tests belegt.

**Persistenz / Identität**
- Daten überleben `close()`/Neuöffnen und einen vollständigen
  Manager-Neustart.
- Dedupe-Identität über Prozessläufe hinweg stabil: identisches
  `(producer_id, event_id)` im zweiten Lauf → `deduplicated=1`, weiterhin
  genau **eine** Zeile.
- Partieller UNIQUE-Index inkl. der für SQLite zwingenden
  `WHERE`-Wiederholung im `ON CONFLICT`-Ziel; erste Fassung gewinnt.
- Migration: `user_version = 99` → Nur-Lesen/`DEGRADED_STORE`, nichts
  gelöscht; fehlgeschlagener Schritt → Rollback, Datei unbeschädigt.
- Retention blockweise, zeitbudgetiert, gegen `NULL` gesichert, kein
  `VACUUM`/`auto_vacuum`/`incremental_vacuum`.

**Verdrahtung**
- `app.py::main()` nach AR-5 (`AppConfig.load()` → Manager bauen/starten →
  `setup_logging(..., observability=...)`) und AR-6 (`try/finally` in `main()`,
  `stop(2.0)` nach `run_gui`s internem `desktop.shutdown()`/`bridge.stop(10.0)`;
  auch alle vier Startabbruchpfade und der Headless-Pfad erreichen das
  `finally`). `ui/application.py` unverändert.
- `core/config.py::_from_dict`: die neue `logging`-Sonderbehandlung ist
  verhaltensgleich zum bisherigen `_build`-Pfad plus Auflösung der
  verschachtelten `observability`-Dataclass; Save/Load-Roundtrip grün.

---

## 5. Nächster zulässiger Schritt

Korrekturlauf **RUN-OBS-030-02** im Umfang von B-1, B-2, B-3 sowie einer
Entscheidung zu W-1 und W-2. Kein Neuentwurf, keine Neuplanung: die
Architektur, das Schema und die Testbasis tragen. Danach erneutes,
unabhängiges OBS-030 Gate. **OBS-040 darf nicht beginnen.**
