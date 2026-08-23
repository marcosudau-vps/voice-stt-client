# GATE_FINDINGS – OBS-030 Korrekturlauf RUN-02

Datum: 2026-08-17
Run: `RUN-OBS-030-02_2026-08-17`
Geprüftes Gate: `40_EVIDENCE/OBS-030/GATE-REVIEW-01_2026-08-17_CLAUDE/GATE_REVIEW.md`
(Ergebnis dort: **OBS-030 GATE FAIL**; diese Historie bleibt unverändert
erhalten und wird durch diesen Lauf **nicht** überschrieben.)

Branch: `feat/einheitliche-triggerarchitektur`
Interpreter: Python 3.12.10 (global), pytest 9.1.1

## Cleanup-Vermerk (Prompt `OBS-030_FIX_RUN_II.md`)

Nach dem Korrekturlauf wurden zwei Änderungen **zurückgenommen**, weil sie
nicht autorisiert waren. Dieses Dokument beschreibt den Stand **nach** dieser
Rücknahme:

1. Der Zähler `dropped_failed` ist vollständig entfernt (Snapshot, Health,
   Ingress, Tests). `LoggingHealthSnapshot` hat wieder exakt die Form aus
   `CONTRACTS §11.2`; `core/observability/ingress.py` ist wieder unverändert
   gegenüber `HEAD`.
2. Der Nachtrag `DR-OBS-030-01` ist aus
   `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` entfernt; die normative Datei
   ist wieder byte-identisch zum Stand vor `RUN-OBS-030-02`.

Die zugrunde liegende **Auslegungsfrage zu `ARCH §8.3` „nur verwerfen und
zählen" bleibt offen** und ist im Gate zu entscheiden:
`DECISION_REQUIRED.md`. Die fachliche B-1-Korrektur bleibt vollständig
bestehen (siehe unten und `FAULT_INJECTION.md`).

---

## 1. Blockierende Befunde

### B-1 – Fehlerisolation auf Schleifenebene im Worker → **BEHOBEN**

**Norm:** `ARCH §8.3` Zeile „Worker-Ausnahme in der Schleife" (*gefangen,
`worker_errors++`, Schleife läuft weiter. Bricht sie dennoch ab: Ingress
wechselt in „nur verwerfen und zählen". **Kein Neustartversuch*** → Health
`FAILED_WORKER`), `ARCH §8.1 G-2/G-4`, `ARCH §8.4`,
`CONTRACTS §11.2`.

**Korrektur (`core/observability/worker.py`, `core/observability/ingress.py`,
`core/observability/health.py`):**

| # | Änderung | Ort |
|---|---|---|
| 1 | `run()` klammert `self._iteration()` in `try/except Exception`; `_record_loop_failure()` erhöht `worker_errors` über den observability-internen Fehlerpfad (`LoggingInternalHealth.record_worker_error` → ratenbegrenztes `emergency()`, G-2/G-4) und die Schleife läuft weiter. | `worker.py::run` |
| 2 | Auch `_open_store()` und der erste `_run_retention_if_due(force=True)` liegen jetzt in Guards — vorher konnten sie den Thread vor dem ersten Schleifendurchlauf still beenden. | `worker.py::run` |
| 3 | Nach `WORKER_FAILURE_THRESHOLD = 5` **aufeinanderfolgenden** Schleifenfehlern bricht die Schleife endgültig ab (**kein Neustartversuch**, §8.3). Ein einzelner Fehler setzt den Zähler beim nächsten erfolgreichen Durchlauf zurück. | `worker.py::_record_loop_failure` |
| 4 | `_finish()` setzt `LoggingHealthState.FAILED_WORKER` **vor** `_shutdown_flush()`. Damit greift `Ingress.is_failed()` ab diesem Moment, und kein Producer bekommt je ein `True` für einen Record, der anschließend dauerhaft strandet. | `worker.py::_finish` |
| 5 | `_prepare_record`: `dataclasses.replace(...)` liegt jetzt **innerhalb** des `try`-Blocks; der Ersatzpfad ist zusätzlich abgesichert und liefert im schlimmsten Fall den Originalrecord zurück. | `worker.py::_prepare_record` |
| 6 | *(zurückgenommen)* Der Korrekturlauf hatte den Verwurf bei `health.is_failed()` zusätzlich gezählt (`dropped_failed`). Der Cleanup hat das entfernt: der Zähler wäre eine nicht autorisierte Erweiterung von `ARCH §7.3` / `CONTRACTS §11.2` gewesen. `core/observability/ingress.py` ist wieder unverändert gegenüber `HEAD`. Die Auslegungsfrage zu „verwerfen **und** zählen" bleibt **offen** und ist im Gate zu entscheiden — `DECISION_REQUIRED.md`. | — |
| 7 | Der gesamte `run()`-Rumpf inklusive `finally` ist guarded; `_shutdown_flush` und `_drain_and_count_leftovers` fangen auch einen defekten `drain`. Kein `threading`-Excepthook-Traceback erreicht mehr stderr an G-2/G-4 vorbei. | `worker.py` |
| 8 | Reste in der Queue werden beim Ende **immer** gezählt (`dropped_shutdown`); ist selbst der `drain` defekt, dient `qsize()` als Rückfall. | `worker.py::_drain_and_count_leftovers` |

**Nachweis:**

- Tests: `tests/test_obs030_worker_fault_injection.py` (6 Tests)
  - `TestSingleUnexpectedExceptionIsCaught` — eine injizierte Ausnahme:
    `worker_errors == 1`, Worker lebt, nachfolgende Records landen im Store.
  - `TestPermanentWorkerFailure::test_dead_worker_is_visible_and_producers_are_no_longer_told_yes`
    — dauerhafte Ausnahme: `worker_errors >= 5`, `state == FAILED_WORKER`,
    `submit()` liefert `[False×5]`, abgewiesene Records erreichen die Queue
    nicht (Füllstand unverändert), bereits eingereihte Records sind als
    `dropped_shutdown >= 1` gezählt, kein `RealtimeSTT-Observability`-Thread
    übrig.
  - `TestPermanentWorkerFailure::test_no_unfiltered_threading_traceback_reaches_stderr`
    — stderr enthält **kein** `Traceback (most recent call last)`; jede Zeile
    beginnt mit `[observability] `.
  - `TestPrepareRecordExitPath` — der `dataclasses.replace`-Austrittspfad.
  - `TestStopOnNeverStartedWorker` — siehe W-7.
- Laufzeitprobe: `FAULT_INJECTION.md` (Gegenstück zur Probe des Gate-Reviews).

### B-2 – Evidence-Konsistenz → **BEHOBEN**

- `CONTRACT_COVERAGE.md` dieses Runs enthält die korrigierte Zeile
  „Worker-Ausnahme in der Schleife" **inklusive** Health-Spalte
  `FAILED_WORKER` und Verweis auf die neuen Tests.
- Die RUN-01-Evidence wird **nicht** umgeschrieben und **nicht** gelöscht.
  Stattdessen trägt jede betroffene RUN-01-Datei am Ende einen unmissverständlich
  gekennzeichneten Abschnitt `## KORREKTURVERMERK (RUN-02, 2026-08-17)`, der die
  jeweils falsche Aussage wörtlich benennt und hierher verweist.
  Betroffen: `RUN-01.../CONTRACT_COVERAGE.md`, `RUN-01.../TEST_RESULTS.md`,
  `runs/RUN-OBS-030-01_2026-08-17_CLAUDE/RESULT.md`.
- Die Gate-FAIL-Historie (`GATE-REVIEW-01_.../GATE_REVIEW.md`) ist
  unverändert.

### B-3 – `CONTRACTS §4.3 P-8` (Pfadgrenzen) → **BEHOBEN**

**Norm:** `CONTRACTS §4.3 P-8` / `R-7`, `CONTRACTS §5.1`.

**Korrektur:**

- `core/config.py`: neue Helfer `user_profile_roots()`,
  `is_inside_user_profile()` und `_validate_user_profile_path()`.
  `LoggingObservabilityConfig.validate()` weist `db_path` und
  `file_sink_dir` mit `ValueError` zurück, wenn der **aufgelöste** Pfad
  (`os.path.realpath` + `os.path.normcase`, damit `..`, `.`, Symlinks/
  Junctions, Groß-/Kleinschreibung und `/`-vs-`\` keine Umgehung sind)
  außerhalb des Benutzerprofils liegt. Ein relativer, leerer,
  laufwerksrelativer (`C:datei`) oder UNC-Pfad wird ebenfalls abgelehnt
  (Vorbild `EventStreamConfig.validate`, das bereits absolute Pfade verlangt).
- `core/observability/manager.py`: `_resolve_profile_path()` wiederholt die
  Prüfung zur Laufzeit. Grund: `app.py::main()` baut den Manager direkt aus
  `AppConfig.load()` und ruft **kein** `AppConfig.validate()` — ohne diese
  zweite Prüfung wäre P-8 im echten Startpfad wirkungslos. Ein abgelehnter
  Pfad wird **nicht akzeptiert**: es wird der eingefrorene Standardort benutzt
  und genau eine ratenbegrenzte stderr-Zeile ausgegeben
  (`[observability] path_outside_user_profile: ...`). Die Anwendung bricht
  wegen eines Konfigurationsfehlers nicht ab (O-01/O-05).

**Nachweis:** `tests/test_obs030_path_boundaries.py` (23 Tests) und
`PATH_BOUNDARIES.md`. Enthalten sind ausdrücklich: gültiger Pfad im
Benutzerprofil, absoluter Pfad außerhalb (inkl. des im Gate genannten
`C:\ProgramData\somewhere-else\...`), `..`-Escape, `..` das **innerhalb**
bleibt (muss zulässig sein), relativer Pfad, laufwerksrelativer Pfad,
UNC-Pfad, Profil eines anderen Benutzers, Groß-/Kleinschreibung und
`/`-Separatoren unter Windows.

**Keine OBS-050-Vorwegnahme:** Es entsteht kein Settings-Eintrag, kein
Dialogfeld und keine UI. Die Prüfung liegt ausschließlich in
`validate()` und in der Kompositionswurzel.

---

## 2. W-1 bis W-7 – Entscheidungen

Maßstab ist jeweils das vollständige Gate-Review-Dokument, `WP-OBS-030` und
die eingefrorenen Normdokumente.

### W-1 – Defekter Store legt den intakten JSONL-Sink still → **FIXED**

**Entscheidung:** verpflichtender OBS-030-Fehler.

**Begründung.** `ARCH §8.3` zählt die Reaktion auf einen Store-Fehler
abschließend auf („Batch **einmal** wiederholen, dann verwerfen", „Batch
verworfen; Retention wird ausgesetzt", „nach 5 aufeinanderfolgenden
Fehlschlägen … aussetzen"). Das stille Abschalten des Sinks steht dort
**nicht** und ist damit eine zusätzliche, nicht vorgesehene Reaktion.
`CONTRACTS §11.1` legt eine **Reihenfolge** fest („write_batch ZUERST, Sink
DANACH — damit ein Sink-Fehler nie einen SQLite-Rollback auslöst"), keine
Bedingung. `O-05` führt Store und Sink als getrennte Fehlerdomänen, und
`WP-OBS-030` verlangt ausdrücklich „Failure Isolation" zwischen ihnen.

**Korrektur:** `worker.py::_process_batch` ruft `_write_sink(prepared)`
unabhängig vom Store-Ergebnis; die Reihenfolge Store→Sink bleibt exakt
erhalten.

**Benannte Grenze (unverändert normativ und hier ausdrücklich festgehalten):**
Bei `FAILED_STORE` schaltet der **Ingress** nach `ARCH §5` („Health ==
FAILED? → return False") ohnehin ab; die Entkopplung wirkt daher für
`DEGRADED_STORE`, die 60-s-Aussetzung und den Nur-Lesen-Betrieb — genau die
Fälle, in denen der Sink weiterlaufen kann und soll.

**Nachweis:** `tests/test_obs030_gate_corrections.py::TestW1SinkIndependentOfStore`
(3 Tests, inkl. Reihenfolgeprüfung), Laufzeitprobe in `FAULT_INJECTION.md`
(20 Records, Store wirft dauerhaft → `sink lines written: 20`, vorher `0`).

### W-2 – `logging.retention_pressure` entsteht nicht als Record → **FIXED**

**Entscheidung:** verpflichtender OBS-030-Fehler.

**Begründung.** `CONTRACTS §12.4` führt
`logging.records_dropped` / `logging.recovered` / `logging.retention_pressure` /
`logging.record_rejected` gemeinsam als **vom Worker erzeugte** strukturierte
Records (`S, intern`). `CONTRACTS §5.6` nennt die Überschreitung von
`max_db_bytes` ausdrücklich „Health-Warnsignal (`logging.retention_pressure`)",
`LOGGING_DECISIONS_FREEZE_V1.md FD-D8` ebenso.

**Korrektur:** `worker.py::_report_retention_pressure` erzeugt den Record über
`_build_internal_record(..., level="WARNING")` und schreibt ihn direkt am
Handler und an der Queue vorbei (G-6). Die ratenbegrenzte stderr-Zeile bleibt
zusätzlich bestehen.

**Bewusste Ausgestaltung, hiermit dokumentiert:** Der Record ist
**flankengesteuert** — er entsteht beim Eintritt in den Überschreitungszustand,
nicht bei jedem Retentionslauf. Andernfalls erzeugte eine dauerhaft zu große
Datenbank alle 60 s einen Record und träfe damit genau das Frequenzproblem,
das `ARCH §8.6`/`§7.3` und die „einmal melden"-Muster vermeiden. Sinkt
`db_bytes` wieder unter die Grenze und steigt später erneut darüber, wird
erneut gemeldet. `max_db_bytes` bleibt reines Warnsignal — **kein**
automatisches Absenken von `max_entries`, **kein** `VACUUM`,
**kein** `incremental_vacuum` (FD-D8).

**Nachweis:** `tests/test_obs030_gate_corrections.py::TestW2RetentionPressureRecord`
(4 Tests), Laufzeitprobe in `FAULT_INJECTION.md`.

### W-3 – Kein Zähler für Records, die wegen ausgesetztem/degradiertem Store verworfen werden → **NOT A DEFECT (Lücke ausdrücklich benannt)**

**Entscheidung:** keine Korrektur; die Lücke wird ausdrücklich benannt.

**Begründung.** `ARCH §7.3` überschreibt die Zählerliste mit „Zähler –
**eingefroren**" und enthält für diesen Fall keinen Zähler;
`CONTRACTS §11.2` friert `LoggingHealthSnapshot` entsprechend ein. Einen
Zähler für „wegen Store-Pause verworfen" zu ergänzen wäre eine Änderung an
zwei eingefrorenen Verträgen ohne normativen Auftrag — genau das, was ohne
`DECISION REQUIRED` untersagt ist. Ein Abbilden auf `dropped_watermark` oder
`dropped_queue_full` verböte sich zusätzlich, weil beide den Record
`logging.records_dropped` speisen und dann eine falsche Ursache behaupteten.

**Sichtbarkeit im Betrieb (was stattdessen trägt):** `store_errors` steigt bei
jedem Fehlschlag, der Health-State ist `DEGRADED_STORE`/`FAILED_STORE`, die
ratenbegrenzte stderr-Zeile `store_write_failed`/`store_disk_full` erscheint,
und seit W-1 erreichen genau diese Records weiterhin den JSONL-Sink, sind also
nicht verloren, wenn ein Sink konfiguriert ist. Was fehlt, ist ausschließlich
die arithmetische Identität `enqueued == written + dropped_*` während einer
Store-Störung.

**Vorlage an das Gate:** Soll der Zähler existieren, ist er ein
`DECISION REQUIRED`-Vorgang gegen `ARCH §7.3` + `CONTRACTS §11.2` und gehört
sinnvollerweise zusammen mit dem V1-Härtungspaket **OBS-060** entschieden.
Dieser Lauf trifft die Entscheidung nicht eigenmächtig.

### W-4 – Kein „leerer Testschreibvorgang" nach der Store-Pause → **FIXED**

**Entscheidung:** verpflichtender OBS-030-Fehler.

**Begründung.** `ARCH §8.3` ist wörtlich: „nach 5 aufeinanderfolgenden
Fehlschlägen Store für 60 s aussetzen, danach **mit einem leeren
Testschreibvorgang prüfen**". Der Store-Schreibpfad ist Kern von OBS-030.

**Korrektur:** `SQLiteLogStore.probe_write()` führt eine Schreibtransaktion
**ohne Zeilen** aus (`BEGIN IMMEDIATE` + `COMMIT`); `BEGIN IMMEDIATE` nimmt
die Writer-Sperre, sodass eine gesperrte, nur lesbare oder geschlossene
Datenbank erkannt wird. `worker.py::_write_with_policy` prüft nach Ablauf der
Pause zuerst mit dieser Probe: scheitert sie, kostet das eine Probe und
**nicht** den Batch, und die Pause verlängert sich um weitere 60 s. Ein
Store-Double ohne `probe_write` wird wie „Probe bestanden" behandelt, damit
sich das Verhalten für solche Doubles nicht ändert.

**Nachweis:** `tests/test_obs030_gate_corrections.py::TestW4EmptyTestWriteAfterThePause`
(4 Tests), Laufzeitprobe in `FAULT_INJECTION.md`.

### W-5 – `LoggingHealthState.DISABLED` wird nie erzeugt → **FIXED**

**Entscheidung:** kleiner, in OBS-030 liegender Fehler.

**Begründung.** `ARCH §8.3` friert die Zustandsmenge inklusive `DISABLED` ein;
`CONTRACTS §11.2` führt ihn im Enum. Ein Zustand, den niemand erzeugt, ist
toter Vertrag, und Health meldete für eine vollständig abgeschaltete
Observability `OK` — eine Falschaussage in genau der Statuszeile, die
`ARCH §8.4` als einzigen Sichtbarkeitsweg vorsieht. Die einzige Komponente,
die von `enabled=False` weiß, ist die in OBS-030 gebaute Kompositionswurzel.

**Korrektur:** `ObservabilityManager.__init__` setzt bei `enabled=False`
`LoggingHealthState.DISABLED`. `store_enabled=False` bleibt bewusst `OK`:
Queue, Worker und Sink laufen dann weiter (`manager._NullStore`), die
Observability ist also nicht abgeschaltet. `DISABLED` ist kein Failure-State
(`is_failed()` bleibt `False`).

**Nachweis:** `tests/test_obs030_gate_corrections.py::TestW5DisabledHealthState`
(2 Tests).

### W-6 – `manager.clear_history()` blockiert den Aufrufer bis zu 5 s → **DEFERRED (OBS-050)**

**Entscheidung:** eindeutig Scope eines späteren Work Packages.

**Begründung.** Das Gate-Review selbst formuliert es als „Für OBS-050
vormerken". `CONTRACTS §5.8` schreibt vor, dass `clear()` über den
`ObservabilityManager` läuft und **nicht** über den Query-Layer; `§10.3`
ordnet die auslösende Schaltfläche „Diagnosehistorie löschen" dem
Logging-Tab zu, und `ARCH §4.1`/`§5.1` legen den gesamten UI-Teil auf
OBS-050. In OBS-030 existiert **kein** Qt-Aufrufer: `ui/**` ist in diesem
Workstream unverändert. Das Blockieren ist zudem architektonisch gewollt —
`request_clear` führt die Löschung auf dem Worker-Thread aus, weil dieser
laut `CONTRACTS §5.4` der alleinige Eigentümer der Schreibverbindung ist.

**Auflage für OBS-050 (hiermit dokumentiert):** `clear_history()` darf nicht
direkt aus dem Qt-Mainthread gerufen werden (`O-03`); der Aufruf gehört auf
denselben Query-/Worker-Thread-Übergang, den `CONTRACTS §9.2` für die
Abfragen vorschreibt. Es wird in diesem Lauf **nichts** davon vorgezogen.

### W-7 – Kleinere Abweichungen → **FIXED (alle drei)**

| Teilbefund | Norm | Entscheidung | Korrektur | Nachweis |
|---|---|---|---|---|
| PRAGMA-Reihenfolge `busy_timeout, foreign_keys, journal_mode, synchronous` | `CONTRACTS §5.2`: „in dieser Reihenfolge" `journal_mode`, `synchronous`, `busy_timeout`, `foreign_keys` | FIXED — eine eingefrorene DDL ist wörtlich umzusetzen, auch wenn die Abweichung funktional unschädlich ist | `storage/sqlite.py::open` | `TestW7SmallerDeviations::test_pragma_order_follows_the_frozen_ddl` |
| `_records_since_retention` zählt **gezogene** Records | `CONTRACTS §5.6`: „alle 2000 **geschriebenen** Records" | FIXED | `worker.py::_process_batch` erhöht um `inserted` | `TestW7SmallerDeviations` (3 Tests: dedupliziert, geschrieben, verworfen) |
| `stop()` auf nie gestartetem Worker lässt eingereihte Records ungezählt | `ARCH §8.3` Shutdown-Zeile („danach `dropped_shutdown`") | FIXED | `worker.py::stop` → `_drain_and_count_leftovers()` | `test_obs030_worker_fault_injection.py::TestStopOnNeverStartedWorker` |

---

## 3. Vorbestehende Umgebungsauffälligkeit (Abschnitt 3 des Gate-Reviews)

Siehe `TEST_RESULTS.md`, Abschnitt „Vorbestehende Fehlschläge". Beide vom
Gate benannten Punkte wurden erneut geprüft und **nicht** pauschal als
irrelevant übernommen.

## 4. Was dieser Lauf ausdrücklich nicht tut

- Kein OBS-040, kein OBS-050 (keine Adapter, keine Query, keine UI, keine
  Settings-Einträge).
- Kein Refactoring ohne Gate-Bezug.
- Der Gate-Punkt `OBS-030 – Gate Review` bleibt in
  `LOGGING_V1_CHECKLISTE.md` **nicht** abgehakt: ein Korrekturlauf vergibt
  sein eigenes Gate nicht.
- Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.
