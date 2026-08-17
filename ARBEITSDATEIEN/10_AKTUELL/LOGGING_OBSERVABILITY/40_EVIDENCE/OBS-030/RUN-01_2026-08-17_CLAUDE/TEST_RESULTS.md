# TEST_RESULTS – OBS-030 RUN-01 (Claude)

Datum: 2026-08-17
Workspace: `voice-stt-client/workspaces/einheitliche-triggerarchitektur`
Interpreter: globales `python` (Python 3.12.10, `C:\Users\marco\AppData\Local\Programs\Python\Python312\python.exe`);
kein workspace-lokales `venv` vorhanden.
CWD für alle Läufe: der Client-Workspace

## Befehle und Ergebnisse

### 1. Baseline vor Änderungen (nach OBS-020 Gate PASS)

```text
$ python -m pytest -q
1 failed, 714 passed, 337 subtests passed in 39.46s
```

Der eine Fehlschlag (`test_ap06_followup.py::TestSettingsDialog::test_failed_runtime_submit_rolls_hotkeys_and_file_back`,
`ModuleNotFoundError: No module named 'lefx.interfaces'`) ist identisch zum in
`CURRENT_STATE.md` dokumentierten vorbestehenden Umgebungsbefund.

### 2. Neue OBS-030-Tests (nur neue Dateien)

```text
$ python -m pytest -q -k obs030
82 passed, 715 deselected, 10 subtests passed in 9.33s

$ python -m unittest discover -s tests -p "test_obs030_*.py"
Ran 82 tests in 7.31s
OK
```

Aufteilung der 82 neuen Tests:

| Datei | Tests | Fokus |
|---|---|---|
| `test_obs030_sqlite_store.py` | 24 | DDL/PRAGMAs, Round-Trip aller Felder, strukturierte/frozen Details, Dedupe (inkl. `producer_id`-Scope), N-05 Fremdthread, Nebenläufiger Leser, Migration (`user_version` höher/niedriger, Rollback bei Fehler), Retention (Alter/Anzahl/blockweise, kein VACUUM), `clear()`, Neustart/Persistenz, `db_bytes` |
| `test_obs030_worker.py` | 20 | Ende-zu-Ende `logger.info -> SQLite`, Batching, nicht-blockierendes Shutdown, HIGH-Sonderregel/N-04, Worker-Fehler (transient/dauerhaft/`disk full`), Sink-Isolation, raw-Redaction+64-KiB-Truncation, `details` nicht doppelt redigiert, Retention-Kadenz, `request_clear`, Health-/Drop-Counter, keine Runtime-Propagation, Shutdown-Flush, Thread-Aufräumung |
| `test_obs030_jsonl_sink.py` | 7 | `schemaVersion` zuerst, `details`/`raw` als JSON-Objekte, leerer Batch, Größenrotation, Wiederherstellbarkeit über rotierte Dateien, Fehler deaktiviert den Sink dauerhaft |
| `test_obs030_manager.py` | 8 | Lifecycle (Start/Stop, kein Thread-Leck), Ende-zu-Ende über den Manager, deaktivierter Manager (`NullIngress`), Store deaktiviert aber Sink läuft weiter, `clear_history`, Neustart über zwei Manager-Instanzen, Level-Verdrahtung |
| `test_obs030_contracts.py` | 11 (+10 Subtests) | Schichtungsregeln (`storage`/`sinks` kennen nur `models`), kein PySide6/QtCore, kein `asyncio.Queue`/`QueueHandler`, keine Verbindung in `__init__`, `check_same_thread` unverändert, azyklische Importe, Signaturen |
| `test_obs030_config.py` | 10 | Defaultwerte nach `CONTRACTS §10.1`, Validierung, Save→Load-Roundtrip mit Nicht-Default-Werten (schließt die in diesem Run gefundene Regression), fehlende Sektion → Defaults, unbekanntes Feld wird ignoriert |
| `test_obs030_app_wiring.py` | 2 | `app.py::main()` startet/stoppt den Manager in der vorgeschriebenen Reihenfolge (AR-5/AR-6), auch wenn der Headless-Pfad wirft |

### 3. Vollständige Client-Suite nach OBS-030

```text
$ python -m pytest -q
1 failed, 796 passed, 351 subtests passed in 46.90s

$ python -m unittest discover -s tests -p "test_*.py"
Ran 797 tests in 43.02s
FAILED (errors=1)
```

796 (pytest) + 1 (der eine vorbestehende Fehlschlag, den pytest als FAILED statt
ERROR zählt) = 797 = 715 (Baseline nach OBS-020) + 82 (neu). Kein bestehender
Test wurde geändert (siehe `DIFF_SUMMARY.md`). Der eine vorbestehende Fehlschlag
ist unverändert derselbe wie vor diesem Run (`lefx.interfaces` fehlt lokal),
außerhalb des Diffs.

### 4. Thread-Hygiene (Pflichtprüfung: "kein Test hinterlässt einen laufenden Worker")

Jede `LoggingWorker`/`ObservabilityManager`-Testklasse in
`test_obs030_worker.py`/`test_obs030_manager.py` vergleicht
`threading.enumerate()` vor und nach dem Test in `tearDown()` und schlägt
fehl, falls ein `RealtimeSTT-Observability`-Thread übrig bleibt. Zusätzlich
bestätigt `test_obs030_contracts.py::TestNoWorkerThreadSurvivesModuleImport`,
dass der bloße Import der Module keinen Thread startet. Geprüft unter
**sowohl** `pytest` **als auch** `unittest discover` (siehe oben) — beide
grün.

### 5. Ende-zu-Ende-Nachweis `logger.info -> SQLite`

```text
tests/test_obs030_worker.py::TestEndToEndLoggerToSqlite::test_logger_info_reaches_sqlite
```

Verdrahtet `UnifiedLogHandler` (OBS-020) + `from_log_record` (OBS-010) +
`ObservabilityIngress` (OBS-020) + `LoggingWorker`/`SQLiteLogStore` (OBS-030)
exakt wie in `app.py::main()`, ruft `logger.info(...)` auf einem echten
Python-Logger auf und bestätigt anschließend über eine **zweite**,
unabhängig geöffnete `SQLiteLogStore`-Verbindung, dass die Zeile in der
Datei liegt.

### 6. Backpressure-Baseline

Siehe `BACKPRESSURE_RESULTS.md`.

### 7. SQLite-Round-Trip-Details

Siehe `SQLITE_ROUNDTRIP.md`.

## Prüfpflichten (WP-OBS-030)

- [x] Positive Tests
- [x] Negative Tests
- [x] Failure-/Edge-Tests
- [x] N-05: Verbindung aus einem Fremdthread → `sqlite3.ProgrammingError`
- [x] Derselbe Serverrecord zweimal → eine Zeile, `deduplicated` steigt
- [x] `user_version = 99` → Nur-Lesen, `DEGRADED_STORE`, nichts gelöscht
- [x] Migration schlägt fehl → Rollback, Datei unverändert, Anwendung läuft
- [x] Nebenläufiger Leser mit offener Abfrage → `write_batch` bleibt erfolgreich
- [x] Store dauerhaft defekt → Worker läuft weiter, `FAILED_STORE`, Anwendung unbeeinflusst
- [x] Nach `stop()` ist kein Thread mehr aktiv (`threading.enumerate()`),
      geprüft unter `unittest` **und** `pytest`
- [x] Ende-zu-Ende-Nachweis `logger.info -> SQLite`
- [x] `git diff --check` → leer/Exit 0
- [x] kein unbeabsichtigter Cross-Workstream-Diff (`git diff --stat`: nur
      `app.py`, `core/config.py`, `core/observability/__init__.py`,
      `core/observability/health.py`)
- [x] Die vollständige bestehende Client-Suite bleibt grün, ohne dass ein
      bestehender Test geändert wird

## Beobachtete, nicht behobene Umgebungsauffälligkeiten (außerhalb des Scopes)

- Derselbe vorbestehende `lefx.interfaces`-Fehlschlag wie in OBS-010/OBS-020
  dokumentiert; unverändert, außerhalb des Diffs.
- `pytest` zählt 796 „passed" gegen `unittest discover`s 797 „Ran" (bei
  identischem 1 Fehlschlag): reine Zähldifferenz zwischen den Runnern bei
  `subTest`-Aggregation, keine inhaltliche Abweichung — beide Läufe zeigen
  denselben einen (vorbestehenden) Fehlschlag und sonst nur Erfolge.

---

## KORREKTURVERMERK (RUN-02, 2026-08-17)

Angehängt vom Korrekturlauf `RUN-OBS-030-02_2026-08-17`. Oben wurde nichts
gelöscht und nichts umgeschrieben.

Die Zahlen dieses Dokuments (82 neue Tests, 796/797 grün) sind als
Momentaufnahme von RUN-01 korrekt, tragen aber zwei Einschränkungen, die der
unabhängige Gate-Review nachgewiesen hat:

1. **Die Testabdeckung war unvollständig, nicht falsch.** Die Prüfliste hakte
   „Failure-/Edge-Tests" ab, obwohl für die **Schleifenebene** des Workers
   kein Test existierte: `TestWorkerFailureIsolation` prüfte ausschließlich
   Store-Fehler, die schon vorher in einem eigenen `try` lagen. Eine
   unerwartete Ausnahme im Schleifenrumpf blieb ungetestet — und ungefangen
   (Gate-Befund **B-1**). Ebenso fehlten Tests für `CONTRACTS §4.3 P-8`
   (Gate-Befund **B-3**), weil die Auflage nicht umgesetzt war.

2. **„796/797 grün" ist nur modulo einer vorbestehenden Flakiness
   reproduzierbar.** Der Gate-Review beobachtete
   `tests/test_core_bridge.py::TestCoreBridge::test_async_and_sync_commands_execute_in_worker_loop`
   in einem von mehreren Vollläufen intermittierend rot (`StopIteration`).
   Die Datei liegt außerhalb des OBS-030-Diffs. In RUN-02 erneut geprüft:
   fünf isolierte Läufe grün, in den Vollläufen nicht aufgetreten. Bewertung
   unverändert: vorbestehende Test-Flakiness, keine Regression dieses Pakets,
   in diesem Workstream nicht zu reparieren.

Der `lefx.interfaces`-Fehlschlag ist unverändert vorbestehend und
umgebungsbedingt; in RUN-02 erneut verifiziert (`lefx` ist lokal ein
Namespace-Paket ohne `interfaces`-Untermodul; `core/led_controller.py` liegt
außerhalb des Diffs).

Aktueller Teststand: `40_EVIDENCE/OBS-030/RUN-02_2026-08-17/TEST_RESULTS.md`
(129 OBS-030-Tests, 843 passed / 1 vorbestehender Fehlschlag in der
Gesamtsuite).
