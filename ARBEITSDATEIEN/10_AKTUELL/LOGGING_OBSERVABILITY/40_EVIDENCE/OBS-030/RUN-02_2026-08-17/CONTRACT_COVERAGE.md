# CONTRACT_COVERAGE – OBS-030 RUN-02 (korrigierte Fassung)

Diese Datei ersetzt **inhaltlich** die Aussagen aus
`RUN-01_2026-08-17_CLAUDE/CONTRACT_COVERAGE.md`. Die RUN-01-Datei bleibt als
Historie erhalten und trägt am Ende einen Korrekturvermerk.

Jede Zeile unten ist gegen den **tatsächlichen Code nach diesem Lauf** und
gegen **tatsächlich ausgeführte Tests** geprüft (siehe `TEST_RESULTS.md`).

## Failure Domain (`ARCH §8.3`) – die korrigierte Tabelle

| Fehler | Vorgeschriebene Reaktion | Health (Norm) | Umsetzung | Nachweis |
|---|---|---|---|---|
| SQLite **locked** | Batch **einmal** wiederholen, dann verwerfen | `DEGRADED_STORE` | `worker.py::_write_with_policy` (genau 2 Versuche je Batch) | `test_obs030_worker.py::test_store_recovers_after_transient_failures_and_resumes_writing` |
| SQLite **disk full** | Batch verworfen, **Retention ausgesetzt** | `FAILED_STORE` | `_looks_like_disk_full` → `_retention_suspended = True`, Pause 60 s | `test_disk_full_error_suspends_retention_and_sets_failed_store` |
| SQLite **corrupt** / Öffnen scheitert | Store deaktiviert, Datei **nie** gelöscht/umbenannt | `FAILED_STORE` | `SQLiteLogStore.open` → `OpenResult(False, …)`; im gesamten Store existiert kein Lösch-/Umbenenncode | `test_open_failure_on_unwritable_directory_reports_failed_not_ok` |
| Store wirft beim Schreiben | nach 5 aufeinanderfolgenden Fehlschlägen 60 s aussetzen, danach **mit einem leeren Testschreibvorgang** prüfen | `DEGRADED_STORE` → ggf. `FAILED_STORE` | `_consecutive_store_failures` / `_store_paused_until`; **neu in RUN-02:** `SQLiteLogStore.probe_write()` (`BEGIN IMMEDIATE`+`COMMIT`) über `worker.py::_probe_store` | `test_obs030_gate_corrections.py::TestW4EmptyTestWriteAfterThePause` (4 Tests) |
| Migration schlägt fehl | Rollback, Datei unverändert, Anwendung läuft | `FAILED_STORE` | `SQLiteLogStore._migrate` | `test_migration_failure_rolls_back_and_leaves_file_unchanged` |
| `user_version` **höher** | Nur-Lesen, nicht löschen, nicht downgraden | `DEGRADED_STORE` | `open()` → `query_only = ON`, `_structural_degraded` | `test_user_version_higher_than_supported_is_read_only_degraded` |
| JSONL-Sink kaputt | Sink deaktivieren, **einmal** melden, Store läuft weiter | `DEGRADED_SINK` | `worker.py::_write_sink` | `test_sink_failure_disables_sink_but_store_keeps_writing` |
| Queue voll / Wasserstand | zählen, kein Log, kein stderr; Meldung erst nach Erholung | `DROPPING` | `ingress.py::submit`, `worker.py::_check_backpressure_state` | `test_obs020_ingress.py`, `test_obs030_worker.py::TestPriorityAndDropPolicyEndToEnd` |
| **Worker-Ausnahme in der Schleife** | **gefangen, `worker_errors++`, Schleife läuft weiter. Bricht sie dennoch ab: Ingress wechselt in „nur verwerfen und zählen". Kein Neustartversuch** | **`FAILED_WORKER`** | **`worker.py::run` (`try/except Exception` um `_iteration`), `_record_loop_failure` (`worker_errors++` über `record_worker_error`, G-2/G-4), Abbruch nach `WORKER_FAILURE_THRESHOLD = 5` aufeinanderfolgenden Fehlern, `_finish()` setzt `FAILED_WORKER` **vor** dem Flush, sodass `ingress.submit` ab da `False` liefert; bereits eingereihte Records werden als `dropped_shutdown` gezählt; kein Neustart. **Offen:** ob `ARCH §8.3` darüber hinaus einen eigenen Zähler für die danach abgewiesenen Submits verlangt — `DECISION_REQUIRED.md`** | **`test_obs030_worker_fault_injection.py` (6 Tests) und `FAULT_INJECTION.md`** |
| Normalizer-Ausnahme | Record verworfen, `logging.record_rejected`, `malformed++` | `OK` + `malformed++` | `ingress.py` (`record_malformed`), Normalizer wirft nie (OBS-010) | `test_obs010_normalizer_*.py`, `test_obs020_ingress.py` |
| Shutdown während Flush | hartes Zeitbudget, danach `dropped_shutdown`, eine stderr-Zeile | – | `_shutdown_flush` / `_drain_and_count_leftovers`; **neu in RUN-02:** auch bei nie gestartetem Worker und bei defektem `drain` | `test_obs030_worker.py::TestShutdownFlush`, `test_obs030_worker_fault_injection.py::TestStopOnNeverStartedWorker` |
| Observability abgeschaltet (`enabled=False`) | – | `DISABLED` (Zustandsmenge §8.3) | **neu in RUN-02:** `ObservabilityManager.__init__` | `test_obs030_gate_corrections.py::TestW5DisabledHealthState` |

> **Korrektur gegenüber RUN-01.** Die RUN-01-Zeile „Worker-Ausnahme in der
> Schleife" behauptete *„gefangen, `worker_errors`/`store_errors`++, Schleife
> läuft weiter"* mit dem Nachweis *„jede `except Exception` in `worker.py`s
> Verarbeitungspfad"* und einer leeren Health-Spalte. Das traf für die
> **Schleifenebene** nicht zu, und `worker_errors` wurde nirgends erhöht
> (`record_worker_error` und `FAILED_WORKER` hatten null Aufrufer im
> Produktcode). Beides ist jetzt zutreffend und getestet.

## Sink- und Store-Kopplung (`CONTRACTS §11.1`, `O-05`)

| Regel | Umsetzung | Nachweis |
|---|---|---|
| Reihenfolge: `write_batch` **zuerst**, Sink **danach** | `worker.py::_process_batch` | `TestW1SinkIndependentOfStore::test_store_still_comes_first` |
| Sink-Fehler löst nie einen SQLite-Rollback aus | Sink läuft nach dem Commit, in eigenem `try` | `test_sink_failure_disables_sink_but_store_keeps_writing` |
| Store-Fehler nimmt den Sink **nicht** mit (O-05) | **neu in RUN-02:** `_write_sink` unabhängig vom Store-Ergebnis | `TestW1SinkIndependentOfStore` (3 Tests), `FAULT_INJECTION.md` |
| Bei `FAILED_STORE` schaltet der Ingress ab | `ARCH §5` „Health == FAILED? → return False" — unverändert, hier ausdrücklich als benannte Grenze festgehalten | `ingress.py::submit`, `test_obs020_ingress.py` |

## Pfade und Dateirechte (`CONTRACTS §4.3`)

| Regel | Umsetzung | Nachweis |
|---|---|---|
| **P-8** kein Pfad außerhalb des Benutzerprofils; ein konfigurierter absoluter Pfad wird gegen das Benutzerprofil geprüft | **neu in RUN-02:** `core/config.py::_validate_user_profile_path` (in `LoggingObservabilityConfig.validate`) und `manager.py::_resolve_profile_path` | `tests/test_obs030_path_boundaries.py` (23 Tests), `PATH_BOUNDARIES.md` |
| **P-9** `-wal`/`-shm` im selben Verzeichnis | SQLite legt die Geschwister immer neben der Datei an; das Verzeichnis liegt seit P-8 garantiert im Profil | `test_obs030_sqlite_store.py::test_wal_journal_mode_and_pragmas` |
| **M-11** einmaliges `icacls`-Protokoll | Abnahmeauflage, **nicht** in OBS-030 — bleibt bei OBS-060 | — |
| **R-7** Store und Sinks im Benutzerprofil | über P-8 erfüllt | wie P-8 |

## Interne Records des Workers (`CONTRACTS §12.4`, `ARCH §7.3`, G-6)

| Record | Erzeuger | Umsetzung | Nachweis |
|---|---|---|---|
| `logging.records_dropped` | Worker, nach Erholung genau **einer**, Zähler danach zurückgesetzt | `_check_backpressure_state` | `BACKPRESSURE_RESULTS.md` (RUN-01, unverändert gültig) |
| `logging.recovered` | Worker, nach Rückkehr in `OK` | `_emit_recovery_record` | `test_store_recovers_after_transient_failures_and_resumes_writing` |
| `logging.retention_pressure` | Worker | **neu in RUN-02:** `_report_retention_pressure` (Channel `performance`, Level `WARNING`, `is_internal`, flankengesteuert) | `TestW2RetentionPressureRecord` (4 Tests) |
| `logging.record_rejected` | Ingress/Normalizer-Pfad (OBS-020) | unverändert | `test_obs020_ingress.py` |
| Alle vier: direkt geschrieben, an Handler und Queue vorbei (G-6) | `_write_direct` | unverändert | Code + `TestW2RetentionPressureRecord` |

## SQLite (`CONTRACTS §5`)

| Regel | Umsetzung | Nachweis |
|---|---|---|
| PRAGMA-Reihenfolge `journal_mode`, `synchronous`, `busy_timeout`, `foreign_keys` „in dieser Reihenfolge" (§5.2) | **korrigiert in RUN-02** | `TestW7SmallerDeviations::test_pragma_order_follows_the_frozen_ddl` |
| DDL, Indizes, partieller UNIQUE-Index | unverändert aus RUN-01 | `test_obs030_sqlite_store.py::TestBootstrapAndDDL`, `TestDedupe` |
| `write_batch` → `(eingefügt, dedupliziert)` (§5.5, FD-R5) | unverändert | `TestDedupe`, `TestHealthAndDropCounters` |
| Migration, `user_version`, Rollback (§5.5) | unverändert | `TestMigrationAndVersioning` |
| Retentionstakt: höchstens alle 60 s **und** höchstens alle 2000 **geschriebenen** Records (§5.6) | **korrigiert in RUN-02:** `_records_since_retention` zählt `inserted` | `TestW7SmallerDeviations` (3 Tests) |
| Retention blockweise, zeitbudgetiert, gegen `NULL` gesichert; kein `VACUUM`/`auto_vacuum`/`incremental_vacuum` (FD-D8) | unverändert | `TestRetention`, `test_retention_never_calls_vacuum` |
| `max_db_bytes` nur messen, nicht eingreifen (§5.6.3) | unverändert; Meldung jetzt zusätzlich als Record (W-2) | `TestW2RetentionPressureRecord` |
| `clear()` = `DELETE FROM logs` + `wal_checkpoint(TRUNCATE)` (§5.8) | unverändert | `TestClear`, `TestClearRequest` |
| Eine Schreibverbindung, im Worker-Thread erzeugt (§5.4, D-4), `check_same_thread` unverändert (N-05) | unverändert | `test_obs030_contracts.py`, `test_n05_connection_used_from_a_foreign_thread_raises` |

## WP-OBS-030 Scope-Checkliste

| Punkt | Stand nach RUN-02 |
|---|---|
| `LoggingWorker` mit Batching und Flush | erfüllt, jetzt mit Schleifen-Fehlerisolation |
| `ObservabilityManager` als Kompositionswurzel, Lebensdauer in `app.py::main()` mit `try/finally`, `stop(2.0)` **nach** `bridge.stop(10.0)` | unverändert erfüllt (`test_obs030_app_wiring.py`); vom Gate eigenständig verifiziert |
| `SQLiteLogStore` + Schema/Migration/Indizes | erfüllt, PRAGMA-Reihenfolge korrigiert |
| Replay-Dedupe über partiellen UNIQUE-Index | unverändert erfüllt |
| Retention/Cleanup nach §5.6 | erfüllt, Takt korrigiert |
| `LogStore.clear()` (FD-S4) | unverändert erfüllt |
| `JsonlSink`, **nach** dem SQLite-Commit | erfüllt, jetzt unabhängig von dessen Ergebnis |
| Shutdown/Flush und Failure Isolation | erfüllt, inkl. Worker-Ausfall und nie gestartetem Worker |

## Schichtung (`ARCH §5.2`) – unverändert eingehalten

`storage`/`sinks` kennen nur `models`; kein `PySide6`/`QtCore` in
OBS-030-Modulen; kein `asyncio.Queue`/`QueueHandler`/`QueueListener` im
Worker; azyklische Importe. Nachweis: `test_obs030_contracts.py` (11 Tests
+ 10 Subtests), unverändert grün. `manager.py` importiert wie zuvor aus
`core.config` (jetzt zusätzlich `is_inside_user_profile`) — die
Kompositionswurzel darf das, `storage`/`sinks` nicht und tun es nicht.

## Non-Scope – bewusst nicht angefasst

Keine Query, keine UI, keine Settings-Einträge, kein Adapter, kein Text-Sink,
kein Fan-out-Hook. `ui/**`, `core/controller.py`,
`core/session_coordinator.py`, `core/event_stream.py`, `core/stt_session.py`
sind unverändert (siehe `DIFF_SUMMARY.md`).

## Offen ausgewiesen

- Auslegung von `ARCH §8.3` „nur verwerfen und zählen": eigener Zähler für
  nach `FAILED_WORKER` abgewiesene Submits oder nicht — `DECISION_REQUIRED.md`.
  Der im Korrekturlauf zwischenzeitlich eingeführte Zähler `dropped_failed`
  ist zurückgenommen; `LoggingHealthSnapshot` entspricht wieder exakt
  `CONTRACTS §11.2`.
- W-3 (kein Zähler für Verwürfe bei ausgesetztem Store) — als Lücke benannt,
  Begründung in `GATE_FINDINGS.md`.
- W-6 (`clear_history()` blockiert) — Auflage für OBS-050.
