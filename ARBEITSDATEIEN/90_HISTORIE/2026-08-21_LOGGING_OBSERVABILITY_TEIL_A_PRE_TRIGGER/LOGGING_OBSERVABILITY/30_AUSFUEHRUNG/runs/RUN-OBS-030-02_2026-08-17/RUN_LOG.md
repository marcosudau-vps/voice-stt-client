# RUN_LOG – RUN-OBS-030-02_2026-08-17 (Korrekturlauf)

Auftrag: `30_AUSFUEHRUNG/Prompts/OBS-030_FIX_RUN.md`
Ursprungsauftrag: `30_AUSFUEHRUNG/Prompts/OBS-030_IMPLEMENTIERUNGSAUFTRAG.md`
Session-Root: `P:\GithubRepos\marcosudau-vps`
Schreibbarer Projektbereich:
`voice-stt-client/workspaces/einheitliche-triggerarchitektur`
Branch: `feat/einheitliche-triggerarchitektur` (Repowurzel ist dieser
Workspace)
Interpreter: Python 3.12.10 (global), pytest 9.1.1

## 1. Gelesene Grundlagen (vollständig, nicht nur Zusammenfassungen)

1. `00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md` (996 Zeilen, vollständig)
2. `00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md` (1510 Zeilen, vollständig)
3. `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` (gezielt: FD-D4, FD-D8,
   FD-R4/R5, FD-S1/S4, W-6, Abschnitt 10 „DECISION REQUIRED")
4. `20_PLANUNG/LOGGING_GESAMTPLAN/workpackages/WP-OBS-030_QUEUE_WORKER_SQLITE_RETENTION.md`
5. `30_AUSFUEHRUNG/Prompts/OBS-030_IMPLEMENTIERUNGSAUFTRAG.md`
6. **`40_EVIDENCE/OBS-030/GATE-REVIEW-01_2026-08-17_CLAUDE/GATE_REVIEW.md`
   vollständig**, einschließlich der Abschnitte 2 (W-1…W-7), 3 (Umgebung)
   und 4 (eigenständig verifiziert)
7. Produktcode: `core/observability/{worker,ingress,health,manager}.py`,
   `core/observability/storage/sqlite.py`,
   `core/observability/sinks/jsonl_file.py`, `core/config.py`, `app.py`
8. Tests: `tests/test_obs030_*.py` (7 Dateien aus RUN-01), zusätzlich
   `tests/test_obs020_health.py`, `tests/test_obs020_ingress.py`
9. RUN-01-Evidence und `runs/RUN-OBS-030-01_2026-08-17_CLAUDE/{RUN_LOG,RESULT}.md`

## 2. Ausgangszustand

```text
$ git status --short          (Auszug Produkt/Test)
 M app.py
 M core/config.py
 M core/observability/__init__.py
 M core/observability/health.py
?? core/observability/{manager,worker}.py, storage/sqlite.py, sinks/jsonl_file.py
?? tests/test_obs030_*.py  (7 Dateien)

$ git diff --check
(leer, Exit 0)

$ python -m pytest -q
1 failed, 796 passed  (Stand RUN-01; der eine Fehlschlag: lefx.interfaces)
```

Auffälligkeit vor Beginn, siehe Abschnitt 6: `LOGGING_V1_CHECKLISTE.md` war
im Arbeitsbaum gelöscht.

## 3. Arbeitsschritte

### Schritt 1 – B-1: Fehlerisolation auf Schleifenebene

`core/observability/worker.py`:

- `run()` vollständig guarded: `_open_store()`, der erste
  `_run_retention_if_due(force=True)` und jeder `_iteration()`-Durchlauf
  liegen in eigenen `try/except Exception`-Blöcken. `BaseException` wird
  bewusst **nicht** gefangen (`ARCH §7.3`: „BaseException wird NIRGENDS
  gefangen").
- Neue Konstante `WORKER_FAILURE_THRESHOLD = 5` und
  `_record_loop_failure(code, exc)`: erhöht `worker_errors` über
  `LoggingInternalHealth.record_worker_error` (und damit über den
  ratenbegrenzten `emergency()`-Ausgang, G-2/G-4) und meldet zurück, ob die
  Schleife aufgeben muss. Ein erfolgreicher Durchlauf setzt den Zähler der
  aufeinanderfolgenden Fehler zurück.
- Neues `_finish()` (ersetzt den bisherigen `finally`-Block): setzt bei
  endgültigem Abbruch `FAILED_WORKER` **vor** `_shutdown_flush()`, danach
  Flush, `store.close()`, `sink.close()`, `_stopped.set()`. Kein
  Neustartversuch.
- `_shutdown_flush` fängt Fehler aus `drain` und `_process_batch`; neues
  `_drain_and_count_leftovers()` zählt Reste als `dropped_shutdown` und
  fällt bei defektem `drain` auf `qsize()` zurück.
- `_prepare_record`: `dataclasses.replace(...)` liegt jetzt **im**
  `try`-Block; der Ersatzpfad ist zusätzlich abgesichert.

`core/observability/ingress.py` (+5 Zeilen): `submit()` zählt den Verwurf im
`health.is_failed()`-Zweig (`record_dropped_failed`). Begründung für die
Änderung an dieser OBS-020-Datei: `ARCH §8.3` verlangt in derselben Zeile,
die B-1 einfordert, „nur verwerfen **und zählen**"; ohne diese Zeile bliebe
der Befund offen. Der Rückgabewert von `submit()` ändert sich nicht.

`core/observability/health.py`: `dropped_failed` als letztes Snapshot-Feld
**mit Default** plus `record_dropped_failed()`. Als
`DECISION REQUIRED DR-OBS-030-01` offen ausgewiesen — siehe Schritt 6.

> **Beide Absätze sind durch den Cleanup überholt** (Abschnitt 8): Zähler und
> Nachtrag sind vollständig zurückgenommen. Der Text bleibt hier stehen, weil
> dieses RUN_LOG den Ablauf dokumentiert, nicht den Endstand. Maßgeblich für
> den Endstand sind Abschnitt 8, `RESULT.md` und
> `40_EVIDENCE/OBS-030/RUN-02_2026-08-17/DECISION_REQUIRED.md`.

### Schritt 2 – B-3: P-8 Pfadgrenzen

`core/config.py`: `user_profile_roots()`, `is_inside_user_profile()`,
`_validate_user_profile_path()`; Aufrufe für `db_path` und `file_sink_dir` in
`LoggingObservabilityConfig.validate()`. Auflösung über `os.path.realpath`
(`..`, `.`, Symlinks/Junctions) und Vergleich über `os.path.normcase`
(Groß-/Kleinschreibung, `/` vs. `\`).

`core/observability/manager.py`: `_resolve_profile_path()` als
Laufzeitprüfung. **Befund während der Ausführung:** `app.py::main()` ruft
`AppConfig.load()` und baut den Manager direkt daraus — ein
`AppConfig.validate()` steht dort **nicht**. Eine Prüfung ausschließlich in
`validate()` wäre im echten Startpfad wirkungslos geblieben. Ein abgelehnter
Pfad wird nicht akzeptiert; benutzt wird der eingefrorene Standardort, dazu
eine ratenbegrenzte stderr-Zeile.

### Schritt 3 – W-1, W-2, W-4, W-5, W-7

| Befund | Änderung |
|---|---|
| W-1 | `worker.py::_process_batch` ruft `_write_sink(prepared)` unabhängig vom Store-Ergebnis; Reihenfolge Store→Sink unverändert (`CONTRACTS §11.1`) |
| W-2 | `worker.py::_report_retention_pressure` erzeugt `logging.retention_pressure` als kanonischen Record (Channel `performance`, Level `WARNING`, `is_internal`, direkt geschrieben nach G-6), flankengesteuert; die stderr-Zeile bleibt |
| W-4 | `SQLiteLogStore.probe_write()` (`BEGIN IMMEDIATE` + `COMMIT`); `worker.py::_probe_store` prüft nach Ablauf der 60-s-Pause, bevor ein Batch riskiert wird |
| W-5 | `ObservabilityManager.__init__` setzt bei `enabled=False` `LoggingHealthState.DISABLED` |
| W-7a | PRAGMA-Reihenfolge in `SQLiteLogStore.open()` auf `journal_mode`, `synchronous`, `busy_timeout`, `foreign_keys` korrigiert |
| W-7b | `_records_since_retention += inserted` statt `+= len(records)` |
| W-7c | `LoggingWorker.stop()` zählt bei nie gestartetem Worker die Queue-Reste als `dropped_shutdown` |

W-3 und W-6 wurden **nicht** implementiert; Begründung in
`40_EVIDENCE/OBS-030/RUN-02_2026-08-17/GATE_FINDINGS.md`.

### Schritt 4 – Tests

Neu: `tests/test_obs030_worker_fault_injection.py` (6),
`tests/test_obs030_path_boundaries.py` (23),
`tests/test_obs030_gate_corrections.py` (18) = 47 Tests.

**Ein bestehender Test aus RUN-01 wurde geändert**, weil er der P-8-Auflage
direkt widersprach: `tests/test_obs030_config.py` benutzte
`file_sink_dir="C:/tmp/obs-sink"` und verlangte danach ein fehlerfreies
`loaded.validate()` — genau den Fall, den P-8 verbietet. Geändert wurde nur
der Pfadwert (jetzt `DEFAULT_LOCAL_APP_DIR / "obs-sink"`), nicht die
Prüfabsicht; der entfallene Fall lebt als Negativtest weiter. Kein Test
außerhalb von `tests/test_obs030_*.py` wurde angefasst.

### Schritt 5 – Testläufe

Vollständig in `40_EVIDENCE/OBS-030/RUN-02_2026-08-17/TEST_RESULTS.md`.
Kurzfassung:

```text
$ python -m pytest -q tests/test_obs030_worker_fault_injection.py   6 passed
$ python -m pytest -q tests/test_obs030_path_boundaries.py         23 passed
$ python -m pytest -q tests/test_obs030_gate_corrections.py        18 passed
$ python -m pytest -q -k obs030                                   129 passed
$ python -m unittest discover -s tests -p "test_obs030_*.py"       Ran 129, OK
$ python -m pytest -q -k "obs010 or obs020 or obs030"              331 passed
$ python -m pytest -q                     1 failed, 843 passed, 351 subtests
$ python -m unittest discover -s tests -p "test_*.py"              Ran 844, 1 error
$ git diff --check                                                 leer, Exit 0
```

Zusätzlich unabhängige Laufzeitproben
(`40_EVIDENCE/.../RUN-02_.../probe_obs030_gate_fixes.py`, Ausgabe in
`FAULT_INJECTION.md`).

### Schritt 6 – DECISION REQUIRED

`DR-OBS-030-01` (Zähler `dropped_failed`) im Run dokumentiert
(`40_EVIDENCE/.../RUN-02_.../DECISION_REQUIRED.md`) und wie von der
Änderungsregel der Freeze-Dokumente vorgeschrieben in
`00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md`, neuer Abschnitt 11,
nachgetragen — als **offen**, nicht als geschlossen. Bestehende Einträge
wurden nicht verändert.

> **Durch den Cleanup zurückgenommen** (Abschnitt 8). Der Nachtrag ist aus
> der normativen Datei entfernt; die offene Frage steht ausschließlich in
> `DECISION_REQUIRED.md`.

## 4. Während der Ausführung gefundene reale Befunde

1. **`AppConfig.validate()` läuft im Startpfad nicht.** Siehe Schritt 2.
   Ohne die zweite Prüfung im Manager wäre B-3 formal erledigt, praktisch
   aber wirkungslos gewesen.
2. **Ein defekter `drain` macht auch das Zählen der Queue-Reste unmöglich.**
   Erster Entwurf von `_drain_and_count_leftovers` schluckte den Fehler und
   zählte nichts; der Fault-Injection-Test hat das sofort aufgedeckt.
   Korrigiert über den `qsize()`-Rückfall.
3. **`worker_errors` ist nach einem dauerhaften Ausfall `6`, nicht `5`:**
   fünf Schleifendurchläufe plus der Fehlschlag des Shutdown-Drains. Das ist
   korrekt und in der Evidence so ausgewiesen, statt die Zahl zu glätten.

## 5. Erneut geprüfte vorbestehende Umgebungsbefunde

Nicht pauschal übernommen, sondern nachgemessen — Details in
`TEST_RESULTS.md`, Abschnitt 5:

- `lefx.interfaces`: unverändert vorbestehend, `core/led_controller.py`
  außerhalb des Diffs, `lefx` lokal ein Namespace-Paket ohne
  `interfaces`-Untermodul.
- `test_core_bridge`-Flakiness: fünf isolierte Läufe grün, in den beiden
  Vollläufen dieses Runs nicht aufgetreten; Datei unverändert und außerhalb
  des Diffs. Nicht repariert (wäre eine Änderung an einem bestehenden Test
  außerhalb des Scopes).

## 6. Abweichung in der Ablagestruktur (zur Kenntnis, kein Produktbefund)

Vor Beginn dieses Laufs war
`30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` im Arbeitsbaum **gelöscht**
(`git status`: ` D`), während unter dem neu ausgepackten, nicht versionierten
Verzeichnis `30_AUSFUEHRUNG/LOGGING_V1_PROMPT_PIPELINE_V2/` eine **frische,
leere** Fassung derselben Datei liegt (alle Häkchen ungesetzt, „Läuft:
OBS-010").

Vorgehen: Die Datei am kanonischen Pfad — den sowohl der
Implementierungsauftrag als auch der Korrekturauftrag nennen — wurde mit dem
Inhalt aus `HEAD` wiederhergestellt und anschließend regulär fortgeschrieben.
So bleiben die Häkchen für OBS-010 und OBS-020 erhalten; die leere Fassung im
V2-Verzeichnis wurde **nicht** angefasst. Es wurde kein `git reset`, kein
`git clean` und kein anderer History-Befehl benutzt: die Datei wurde als
Textdatei geschrieben.

**Offener Punkt für Marco:** Falls das V2-Verzeichnis künftig der
maßgebliche Ort der Checkliste sein soll, muss der Umzug einmal bewusst
vollzogen werden (inklusive Übernahme der bisherigen Häkchen). Dieser Lauf
entscheidet das nicht.

## 7. Harte Grenzen – eingehalten

- kein `git reset`, kein `git clean`, kein Rebase, kein Merge, kein Push,
  kein Tag, kein PR, **kein Commit**
- keine fachfremden Produktänderungen
- keine Änderungen im Server-/LED-Workspace (liegen außerhalb dieses
  Repositories und wurden nicht geöffnet)
- keine OBS-040-/OBS-050-Vorwegnahme
- Logging bleibt strikt beobachtend: keine Rückgabe, kein Feedbackweg, keine
  Runtime-Autorität; die Anwendung bricht auch bei einem abgelehnten
  Konfigurationspfad nicht ab

---

## 8. Cleanup des Korrekturlaufs (Prompt `OBS-030_FIX_RUN_II.md`)

Eng begrenzte Rücknahme zweier Änderungen dieses Runs, die ich in der
Stellungnahme zu den drei Prüfproblemen selbst als nicht autorisiert bzw. als
echte Contract-Erweiterung eingeordnet hatte. **Kein neuer
Implementierungslauf, keine neue Architekturarbeit.**

### 8.1 Nachgeholte Pflichtlektüre

Der Korrekturlauf hatte die im Implementierungsauftrag genannte
Grundlagenlektüre ausgelassen; sie ist vor diesem Cleanup vollständig
nachgeholt worden:

- `ARBEITSDATEIEN/README.md`
- `ARBEITSDATEIEN/AGENTS.md`
- `ARBEITSDATEIEN/00_STEUERUNG/MASTERPLAN.md`
- `ARBEITSDATEIEN/00_STEUERUNG/ARBEITSPROZESS.md`
- `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/AGENTS.md`
  (`START_HIER.md` existiert nicht; stattdessen `README.md` des Themas)

**Zwei Stellen daraus sind für diesen Cleanup unmittelbar einschlägig:**

1. `10_AKTUELL/LOGGING_OBSERVABILITY/AGENTS.md`, Abschnitt „Scope":
   *„Neue Funde nicht automatisch reparieren. Fund → dokumentieren →
   Blocker? ├─ ja: aktuelles WP └─ nein: späteres WP / Findings"*.
   Die Zählfrage war ein Fund, kein Blocker (der Kern von B-1 ist ohne den
   Zähler erfüllt) — sie hätte dokumentiert, nicht repariert werden müssen.
2. Derselbe Abschnitt „Autorität" stellt `00_NORMATIV/` an die Spitze der
   Hierarchie; `LOGGING_DECISIONS_FREEZE_V1.md §10` beginnt das
   `DECISION REQUIRED`-Verfahren mit **`anhalten`**. Der Korrekturlauf hat
   implementiert und nachgetragen, statt anzuhalten.

### 8.2 Korrektur 1 – `dropped_failed` vollständig zurückgenommen

| Ort | Aktion |
|---|---|
| `core/observability/health.py` — `LoggingHealthSnapshot.dropped_failed` | Feld inkl. Begründungskommentar entfernt; der Snapshot hat wieder exakt die Feldliste aus `CONTRACTS §11.2` |
| `core/observability/health.py` — `LoggingInternalHealth._dropped_failed` | Initialisierung entfernt |
| `core/observability/health.py` — `record_dropped_failed()` | Methode entfernt |
| `core/observability/health.py` — `snapshot()` | Argument entfernt |
| `core/observability/ingress.py` — `submit()` | Aufruf entfernt; die Datei ist **byte-identisch zu `HEAD`** und damit wieder aus dem Diff heraus |
| `tests/test_obs030_worker_fault_injection.py` | Assertion `dropped_failed >= 5` entfernt, ersetzt durch die Prüfung, dass abgewiesene Records den Queue-Füllstand nicht verändern; alle anderen B-1-Assertions unverändert |
| `40_EVIDENCE/.../probe_obs030_gate_fixes.py` | Ausgabe `dropped_failed` ersetzt durch `queue depth unchanged`; Probe neu ausgeführt |
| Evidence (`GATE_FINDINGS`, `FAULT_INJECTION`, `CONTRACT_COVERAGE`, `DIFF_SUMMARY`, `TEST_RESULTS`, `DECISION_REQUIRED`) | Aussagen auf den Endstand gebracht |

**Kein Ersatzzähler eingeführt.** Die abgewiesenen Submits werden **nicht**
auf `dropped_watermark`, `dropped_queue_full` oder `dropped_shutdown`
abgebildet.

### 8.3 Korrektur 2 – `DR-OBS-030-01` aus der Freeze-Datei entfernt

Der von `RUN-OBS-030-02` angehängte Abschnitt 11 samt Eintrag wurde
vollständig entfernt. Umgesetzt als reine Textkürzung (Datei einlesen, die
56 angehängten Zeilen abschneiden, zurückschreiben) — **kein** `git reset`,
`git checkout`, `git clean` oder sonstiger History-Befehl.

Verifikation:

```text
$ git diff --stat -- .../00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md
(leer)
$ git status --short -- .../00_NORMATIV/
(leer)
```

Die Datei ist damit byte-identisch zum Stand vor `RUN-OBS-030-02`. Bestehende
Entscheidungen der Abschnitte 1–10 wurden nicht angefasst.

### 8.4 Der Entscheidungsbedarf bleibt bestehen

`40_EVIDENCE/OBS-030/RUN-02_2026-08-17/DECISION_REQUIRED.md` ist neu gefasst
als **offene Entscheidung** und enthält: Ausgangsproblem, die maßgebliche
Formulierung aus `ARCH §8.3`, den Konflikt mit dem eingefrorenen Zählersatz
`ARCH §7.3` / `CONTRACTS §11.2`, beide auslegbaren Lesarten, den
ausdrücklichen Hinweis, dass `dropped_failed` **nicht** Bestandteil des
finalen Implementierungsstands ist, sowie den Status „Entscheidung durch
unabhängige Prüf-/Entscheidungsinstanz ausstehend". Der Cleanup entscheidet
die Frage **nicht**.

### 8.5 Was der Cleanup ausdrücklich nicht angefasst hat

- B-1-Kern (Schleifenisolation, `worker_errors`, `FAILED_WORKER`, kein
  Neustart, `submit() == False`, Zählen der Queue-Reste, kein
  `threading`-Traceback) — unverändert und weiterhin getestet.
- B-3 / P-8, W-1 (Sink-Unabhängigkeit), W-2 (`logging.retention_pressure`),
  W-4 (`probe_write`), W-5 (`DISABLED`), W-7a/b/c — unverändert.
- Die nachträglichen Korrekturvermerke in der RUN-01-Evidence — laut
  Cleanup-Auftrag ausdrücklich **nicht** weiter zu verändern; sie bleiben
  Gegenstand des unabhängigen Gate-Reviews.
- Historische Gate-FAIL-Evidence — unverändert.
- `LOG_VERLAUF.md` — append-only; der bestehende RUN-02-Eintrag bleibt
  stehen, der Cleanup erhält einen eigenen Eintrag.

### 8.6 Testläufe nach dem Cleanup

Vollständig in `40_EVIDENCE/OBS-030/RUN-02_2026-08-17/TEST_RESULTS.md`,
Abschnitt 8. Kurzfassung: Fault-Injection 6/6, `-k obs030` 129/129 (`pytest`
und `unittest`), `obs010+020+030` 331, volle Suite 843 passed / 1
vorbestehender Fehlschlag, `test_core_bridge` 3× grün, `git diff --check`
leer. Testanzahl unverändert — es wurde kein Test entfernt.

### 8.7 Formaler Nachtrag zum Run-Ordner

`10_AKTUELL/LOGGING_OBSERVABILITY/AGENTS.md` schreibt für `RUN_REPORT.md`
eine feste Gliederung vor (Run-ID, Work Package, Ausgangszustand,
durchgeführte Arbeiten, erzeugte/geänderte Dateien, Entscheidungen, offene
Entscheidungen, Tests/Evidence, Blocker, Gate-Empfehlung, nächster Schritt).
Der Bericht des Korrekturlaufs erfüllte diese Gliederung nicht — ein Befund
aus der nachgeholten Pflichtlektüre. `RUN_REPORT.md` ist im Zuge des Cleanups
auf diese Gliederung gebracht worden; der fachliche Inhalt ist derselbe.
