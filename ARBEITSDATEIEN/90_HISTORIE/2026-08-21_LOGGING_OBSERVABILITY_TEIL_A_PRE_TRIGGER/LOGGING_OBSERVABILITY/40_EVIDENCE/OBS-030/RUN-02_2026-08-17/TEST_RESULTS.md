# TEST_RESULTS – OBS-030 RUN-02 (Korrekturlauf inkl. Cleanup)

> **Alle Zahlen unten stammen aus den Läufen NACH dem Cleanup** (Prompt
> `OBS-030_FIX_RUN_II.md`, Rücknahme von `dropped_failed` und des
> Freeze-Nachtrags). Die Testanzahl ist unverändert: aus dem
> Fault-Injection-Test ist nur die Assertion auf `dropped_failed`
> entfallen, ersetzt durch die Prüfung, dass abgewiesene Records die Queue
> nicht erreichen.

Datum: 2026-08-17
Workspace: `voice-stt-client/workspaces/einheitliche-triggerarchitektur`
Interpreter: globales `python` (Python 3.12.10), pytest 9.1.1;
kein workspace-lokales `venv` vorhanden.
CWD für alle Läufe: der Client-Workspace.

## 1. Neue gezielte Korrekturtests

```text
$ python -m pytest -q tests/test_obs030_worker_fault_injection.py
6 passed in 0.35s

$ python -m pytest -q tests/test_obs030_path_boundaries.py
23 passed in 2.88s

$ python -m pytest -q tests/test_obs030_gate_corrections.py
18 passed in 0.17s
```

47 neue Tests in 3 Dateien:

| Datei | Tests | Gate-Befund |
|---|---|---|
| `tests/test_obs030_worker_fault_injection.py` | 6 | B-1 (Fehlerisolation, `FAILED_WORKER`, `submit() == False`, kein Stranden unbemerkt, kein `threading`-Traceback, `dataclasses.replace`-Austrittspfad) und W-7c |
| `tests/test_obs030_path_boundaries.py` | 23 | B-3 (P-8) |
| `tests/test_obs030_gate_corrections.py` | 18 | W-1, W-2, W-4, W-5, W-7a, W-7b |

## 2. Vollständige OBS-030-Testsuite

```text
$ python -m pytest -q -k obs030
129 passed, 715 deselected, 10 subtests passed in 11.78s

$ python -m unittest discover -s tests -p "test_obs030_*.py"
Ran 129 tests in 7.296s
OK
```

129 = 82 (RUN-01) + 47 (neu). Beide Runner grün — die Pflichtprüfung „kein
Test hinterlässt einen laufenden Worker" gilt unter `unittest` **und**
`pytest`; die neuen Fault-Injection-Tests prüfen `threading.enumerate()` in
ihrem eigenen `tearDown` zusätzlich.

## 3. Gesamter Observability-Workstream

```text
$ python -m pytest -q -k "obs010 or obs020 or obs030"
331 passed, 513 deselected, 112 subtests passed in 16.40s
```

Insbesondere unverändert grün: `test_obs020_health.py` und
`test_obs020_ingress.py`. Nach dem Cleanup ist
`core/observability/ingress.py` wieder unverändert gegenüber `HEAD` und
`LoggingHealthSnapshot` hat wieder exakt die Form aus `CONTRACTS §11.2` —
die OBS-020-Testbasis prüft damit denselben Code wie zum Zeitpunkt ihres
Gate-`PASS`.

## 4. Vollständige Client-Suite

```text
$ python -m pytest -q
1 failed, 843 passed, 351 subtests passed in 48.95s

$ python -m unittest discover -s tests -p "test_*.py"
Ran 844 tests in 47.189s
FAILED (errors=1)
```

843 + 1 = 844 = 797 (Stand RUN-01) + 47 (neu). Die Zähldifferenz zwischen
`pytest` (843 passed) und `unittest` (844 Ran) ist dieselbe wie in RUN-01
dokumentiert: derselbe eine Fehlschlag, den `pytest` als FAILED und
`unittest` als ERROR zählt.

## 5. Vorbestehende Fehlschläge – erneut geprüft, nicht pauschal übernommen

### 5.1 `lefx.interfaces`

```text
FAILED tests/test_ap06_followup.py::TestSettingsDialog::
       test_failed_runtime_submit_rolls_hotkeys_and_file_back
ModuleNotFoundError: No module named 'lefx.interfaces'
```

Geprüft:

```text
$ python -c "import lefx, sys; print('lefx from', lefx.__file__); import lefx.interfaces"
lefx from None
ModuleNotFoundError: No module named 'lefx.interfaces'
```

`lefx` ist lokal ein Namespace-Paket ohne `interfaces`-Untermodul; der
Fehlschlag entsteht in `core/led_controller.py::_build_service`. Diese Datei
liegt **außerhalb** des Diffs dieses Runs (`git status --short` /
`git diff --stat`, siehe `DIFF_SUMMARY.md`) und wurde weder in RUN-01 noch in
RUN-02 angefasst. Der Befund ist unverändert derselbe wie der in
`CURRENT_STATE.md` seit OBS-010 dokumentierte, umgebungsbedingte Fehlschlag.
Kein Zusammenhang mit der Observability-Domäne.

### 5.2 Intermittierender `test_core_bridge`-Befund des Gate-Reviews

Das Gate-Review hielt fest, dass
`tests/test_core_bridge.py::TestCoreBridge::test_async_and_sync_commands_execute_in_worker_loop`
**intermittierend** mit `StopIteration` rot wird (in einem von mehreren
Vollläufen), weil die `wait_until`-Bedingung die `local_feedback`-Zustellung
nicht abwartet.

Gezielt nachgeprüft:

```text
$ for i in 1..5: python -m pytest -q tests/test_core_bridge.py
7 passed in 1.13s
7 passed in 1.11s
7 passed in 1.10s
7 passed in 1.08s
7 passed in 1.09s
```

In den Vollläufen dieses Runs (`pytest -q` und `unittest discover`) trat der
Fehlschlag **nicht** auf. Bewertung unverändert zum Gate: Es handelt sich um
eine vorbestehende Test-Flakiness in einer Datei, die außerhalb des Diffs
liegt (`tests/test_core_bridge.py` ist unverändert) und keine
Observability-Komponente berührt. Sie wird hier **nicht** repariert — das wäre
eine Änderung an einem bestehenden Test außerhalb des OBS-030-Scopes
(`ARCH §12`). Sie bleibt als Beobachtung notiert; die Zahl „843/844 grün" gilt
modulo dieser Flakiness.

## 6. Diff-Hygiene

```text
$ git diff --check
(keine Ausgabe, Exit 0)
```

## 7. Prüfpflichten des Korrekturauftrags

- [x] alle neuen gezielten Korrekturtests (47)
- [x] komplette OBS-030-Testsuite (129, `pytest` **und** `unittest`)
- [x] vollständige Client-Testsuite (843 passed / 1 vorbestehender Fehlschlag)
- [x] unabhängige Fault-Injection für Worker-Ausfall (`FAULT_INJECTION.md`)
- [x] Pfadgrenzen P-8 (`PATH_BOUNDARIES.md`)
- [x] Store-/Sink-Fehlerisolation entsprechend der Entscheidung zu W-1
- [x] Retention-Pressure entsprechend der Entscheidung zu W-2
- [x] Backpressure/Drop-Recovery (`test_obs030_worker.py::TestPriorityAndDropPolicyEndToEnd`,
      `TestHighSpecialRule`, `test_obs020_ingress.py`; unverändert grün)
- [x] Shutdown (`TestShutdownFlush`, neu: `TestStopOnNeverStartedWorker`)
- [x] SQLite-Dedupe/Persistenz/Retention (`test_obs030_sqlite_store.py`,
      unverändert grün, jetzt zusätzlich mit der PRAGMA-Reihenfolge nach §5.2)
- [x] `git diff --check`

## 8. Cleanup-Verifikation (Prompt `OBS-030_FIX_RUN_II.md`)

Nach der Rücknahme von `dropped_failed` und des Freeze-Nachtrags erneut
ausgeführt — alle oben genannten Zahlen stammen aus diesen Läufen:

```text
$ python -m pytest -q tests/test_obs030_worker_fault_injection.py   6 passed
$ python -m pytest -q -k obs030                                   129 passed
$ python -m pytest -q -k "obs010 or obs020 or obs030"              331 passed
$ python -m unittest discover -s tests -p "test_obs030_*.py"       Ran 129, OK
$ python -m pytest -q                     1 failed, 843 passed, 351 subtests
$ python -m unittest discover -s tests -p "test_*.py"              Ran 844, 1 error
$ python -m pytest -q tests/test_core_bridge.py  (3x)              je 7 passed
$ git diff --check                                                 leer, Exit 0
```

Die Testanzahl ist unverändert (129 / 843): Es wurde **kein** Test entfernt,
nur eine Assertion ersetzt. Der eine Fehlschlag ist unverändert der
vorbestehende `lefx.interfaces`-Fehler; `tests/test_ap06_followup.py` und
`core/led_controller.py` erscheinen in keinem `git status`-/`git diff`-Eintrag
dieses Stands, liegen also nachweislich außerhalb des aktuellen Diffs.

Zusätzlich nach dem Cleanup geprüft:

| Prüfung | Ergebnis |
|---|---|
| `grep -rn "dropped_failed" core/ app.py tests/` | keine Treffer (außer verwaisten `__pycache__`-Binärdateien, die beim nächsten Import neu erzeugt werden) |
| `git diff --stat -- core/observability/ingress.py` | leer — Datei wieder auf `HEAD` |
| `git diff --stat -- core/observability/health.py` | `+21/-2` — exakt der von GATE-REVIEW-01 festgehaltene RUN-01-Stand |
| `git status --short -- ARBEITSDATEIEN/.../00_NORMATIV/` | leer — kein normatives Dokument verändert |
