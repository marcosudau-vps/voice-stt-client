# OBS-050 – TEST_RESULTS

Run: `RUN-OBS-050-01_2026-08-17`
Ausgangscommit: `91a7b7f` (`feat(observability): complete OBS-040 observation hooks`)
Umgebung: Windows 11, Python 3.12.10, PySide6 offscreen (`QT_QPA_PLATFORM=offscreen`)

## 1. Neue Tests

| Datei | Tests | Subtests | Gegenstand |
|---|---:|---:|---|
| `tests/test_obs050_local_provider.py` | 42 | 7 | Filter, Keyset-Pagination, Sortierung, `fetch_raw`, Fehlerzustände, Leseverbindung |
| `tests/test_obs050_query_service.py` | 10 | 0 | Registry, unbekannter Provider, werfender Provider |
| `tests/test_obs050_settings.py` | 37 | 23 | Settings-Metadaten §10.3, Candidate-Bau, Ownership-Domains, Apply-Kette §10.4 |
| `tests/test_obs050_ui.py` | 60 | 9 | Model/Filterbar/Detail/Controller/Page/Window, sechster Tab, Desktop-Verdrahtung |
| `tests/test_obs050_contracts.py` | 21 | 277 | Modulstruktur, Importrichtung, kein Ringbuffer, Query-Verträge, Logging ohne UI |
| **Summe** | **170** | **316** | |

`tests/obs050_apply_support.py` ist ein Hilfsmodul ohne Testfälle (bewusst nicht
`test_*` benannt, damit es von keinem Runner eingesammelt wird).

## 2. Kommandos und Ergebnisse

```text
$ python -m pytest tests -q -k obs050
170 passed, 959 deselected, 316 subtests passed in 17.88s          (exit 0)

$ python -m unittest discover -s tests -p "test_obs050_*.py"
Ran 170 tests ... OK                                               (exit 0)

$ python -m pytest tests -q
1 failed, 1128 passed, 856 subtests passed in 71.66s

$ python -m unittest discover -s tests -p "test_*.py"
Ran 1129 tests ... FAILED (errors=1)

$ python -m pytest tests -q -k "obs010 or obs020 or obs030 or obs040 or obs050"
616 passed, 513 deselected, 617 subtests passed in 41.19s          (exit 0)
```

Der eine Fehlschlag ist in **beiden** Runnern derselbe:
`tests/test_ap06_followup.py::TestSettingsDialog::test_failed_runtime_submit_rolls_hotkeys_and_file_back`,
`ModuleNotFoundError: No module named 'lefx.interfaces'`.

## 3. Nachweis, dass dieser Fehlschlag vorbesteht

Der Ausgangscommit wurde frisch in ein separates Verzeichnis ausgepackt
(`git archive 91a7b7f | tar -x -C <tmp>`) und dort unverändert getestet:

```text
Baseline 91a7b7f:  1 failed, 958 passed, 531 subtests passed
Arbeitsbaum:       1 failed, 1128 passed, 856 subtests passed
```

Gleiche Testdatei, gleiche Ursache (`lefx.interfaces` fehlt in dieser
Prüfumgebung, außerhalb des Diffs). **Differenz: exakt 170 Tests** — die neuen
OBS-050-Tests. Kein bestehender Test wurde geändert.

## 4. Ende-zu-Ende-Diagnoseskript

`probe_obs050_end_to_end.py` (in diesem Verzeichnis) fährt den **echten**
`ObservabilityManager` mit echtem Workerthread und echter SQLite-Datei, den
echten Query-Layer und das echte Qt-`LogWindow` (offscreen) hoch.

```text
$ python probe_obs050_end_to_end.py
[PASS] P-8a reader never creates the store file — exists=False, state=unavailable
[PASS] P-1 ingress -> worker -> store -> query — 1 Zeile(n), types=['client.app.started']
[PASS] P-2 raw absent from the list, present through fetch_raw
[PASS] P-3 keyset pagination: no gaps, no duplicates while writing — 750 Zeilen, 750 eindeutig, 8 Seiten
[PASS] P-4 live view tails through the query layer (no ring buffer) — 200 -> 205 Zeilen im Modell
[PASS] P-4b status line shows the health snapshot — Provider: available · 205 Zeilen · Logging: ok · geschrieben 765 · dedupliziert 0 · verworfen 0 · Queue 0
[PASS] P-5 one config value moves handler AND ingress level — handler=40, ingress=ERROR
[PASS] P-5b retention settings reach the worker — retention_days=3, max_entries=1234
[PASS] P-5c the raised level filters immediately — 0 -> 0
[PASS] P-6 clear runs at the store, not in the query layer — 765 gelöscht, 0 verblieben, query-Layer-Schreibmethode=False
[PASS] P-7 logging runs without the view; a later view shows it — 3 geschrieben, 3 sichtbar
[PASS] P-8b the reader connection cannot write (PRAGMA query_only)

12/12 Prüfungen bestanden.                                          (exit 0)
```

## 5. Nebenläufigkeit und Threadhygiene

- Kein Test hinterlässt einen laufenden `RealtimeSTT-Observability`-Thread; das
  Diagnoseskript stoppt den Manager im `finally`.
- Der Query-Executor (`RealtimeSTT-LogQuery`) wird in jedem Test über
  `LogQueryController.shutdown()` beendet. `shutdown()` **wartet** seit diesem
  Run (siehe `DIFF_SUMMARY.md`, Befund F-2).
- `tests/test_obs050_ui.py` sammelt in `tearDown` deterministisch ein
  (`gc.collect()` zwischen zwei `processEvents`), weil die dort erzeugten
  Fenster elternlos sind und ihre C++-Seite sonst irgendwann im
  `processEvents` eines *späteren* Tests stirbt. Ohne diesen Aufräumpunkt
  stürzte der Lauf reproduzierbar mit einer Zugriffsverletzung ab (F-2).

## 6. Bekannte Einschränkungen

- Die Tests laufen ausschließlich offscreen; eine sichtbare Fenstergeometrie,
  Schriftmetriken und Kontextmenü-Popups werden nicht optisch geprüft.
  `UI_ACCEPTANCE.md` benennt, was daraus folgt.
- Das `LogWindow` wurde nicht in einem echten Tray-Prozess über Stunden
  betrieben; Dauerlast des Live-Modus ist OBS-060-Gegenstand.
- Die Zeitmessung des Query-Pfades (Antwortdauer je Seite) ist nicht Teil
  dieses Pakets; das Performance-Gate liegt in OBS-060.
