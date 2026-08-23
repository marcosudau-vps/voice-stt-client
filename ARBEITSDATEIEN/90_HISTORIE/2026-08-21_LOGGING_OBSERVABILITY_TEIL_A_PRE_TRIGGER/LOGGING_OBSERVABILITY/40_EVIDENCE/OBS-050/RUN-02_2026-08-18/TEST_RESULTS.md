# OBS-050 RUN-02 – TEST_RESULTS

Run: `RUN-OBS-050-02_2026-08-18` (Korrekturlauf zu `OBS-050 GATE FAIL`)
Ausgangscommit: `91a7b7f` (unverändert, kein Commit erstellt)
Umgebung: Windows 11, Python 3.12.10, PySide6 offscreen

## 1. Neue und geänderte Tests

### 1.1 Neu — B-1 (Reihenfolge über Seitengrenzen)

| Test | prüft |
|---|---|
| `test_display_order_stays_monotone_across_three_history_pages` | lädt **drei** Seiten und vergleicht die **vollständige** dargestellte Reihenfolge `r11 … r0`; zusätzlich strenge Monotonie, Duplikatfreiheit und dass ab der zweiten Seite ein Cursor mitging |
| `test_automatic_load_at_the_list_end_keeps_the_order` | derselbe Pfad über `_on_scrolled` am unteren Rand, also ohne Knopfdruck |
| `test_history_mode_shows_the_newest_page_first_newest_on_top` | die erste Seite vollständig (`r11 … r7`) statt nur zweier Randzeilen |

### 1.2 Neu — B-2 (Antwort folgt aus der Anfrage)

| Test | prüft |
|---|---|
| `test_live_start_on_an_empty_result_set_then_records_arrive` | der vom Gate reproduzierte Fall: Live auf leerem Ergebnis, dann fünf Records; Reihenfolge, Duplikatfreiheit über drei Takte, Cursor auf dem neuesten Record |
| `test_further_records_after_an_empty_start_extend_the_tail` | mehrere aufeinanderfolgende Tail-Antworten setzen fort statt zu wiederholen |
| `test_live_start_with_a_filter_that_matches_nothing_then_matches` | derselbe Leerstart, erreicht über einen Filter statt über einen leeren Store |
| `test_filter_change_during_live_reseeds_without_duplicates` | Filterwechsel im laufenden Live-Modus (setzt `_live_cursor` zurück) |
| `test_live_start_on_a_populated_store_stays_correct` | die Gate-Gegenprobe C darf nicht regressieren |
| `test_a_response_is_interpreted_by_its_request_not_by_the_cursor` | die Anfrageart wird verbraucht; eine wiederholt zugestellte Antwort ändert nichts |
| `test_every_query_records_the_kind_of_request_it_was` (Contract) | kein Pfad reserviert eine Anfrage-ID, ohne die Art festzuhalten |

### 1.3 Richtiggestellt (beide aus RUN-01, beide OBS-050-eigen)

| Test | Grund |
|---|---|
| `test_history_mode_loads_the_newest_page_first` → `…_shows_the_newest_page_first_newest_on_top` | erwartete die B-1-Umkehrung (`r7` oben) |
| `test_the_live_mode_queries_the_provider` | las `request_page` wörtlich in `_tail`; die Abfrage läuft jetzt durch `_issue`, geprüft werden beide Enden |

## 2. Kommandos und Ergebnisse

```text
$ QT_QPA_PLATFORM=offscreen python -m pytest tests -q -k obs050
179 passed, 959 deselected, 319 subtests passed in 30.70s               (exit 0)

$ QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -p "test_obs050_*.py"
Ran 179 tests in 27.885s ... OK                                         (exit 0)

$ QT_QPA_PLATFORM=offscreen python -m pytest tests -q \
      -k "obs010 or obs020 or obs030 or obs040 or obs050"
625 passed, 513 deselected, 620 subtests passed in 50.29s               (exit 0)

$ QT_QPA_PLATFORM=offscreen python -m pytest tests -q
1 failed, 1137 passed, 859 subtests passed in 84.62s

$ QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -p "test_*.py"
Ran 1138 tests in 78.254s ... FAILED (errors=1)
```

Stand vor der Korrektur: 170 OBS-050-Tests, volle Suite 1128 grün.
Jetzt: **179 OBS-050-Tests (+9)**, volle Suite **1137 grün (+9)**.

## 3. Der eine Fehlschlag

`tests/test_ap06_followup.py::TestSettingsDialog::test_failed_runtime_submit_rolls_hotkeys_and_file_back`,
`ModuleNotFoundError: No module named 'lefx.interfaces'`.

Er wird **nur** deshalb weiterhin als vorbestehend ausgewiesen, weil beides
nachgemessen ist:

```text
$ git diff --name-only | grep -E "test_ap06_followup|led_controller"
(keine Treffer)

$ git status --short -- tests/test_ap06_followup.py core/led_controller.py
(leer)

$ python -m pytest <frisch aus 91a7b7f ausgepackter Baum>/tests/test_ap06_followup.py::...
1 failed   —   ModuleNotFoundError: No module named 'lefx.interfaces'
```

Weder die Testdatei noch `core/led_controller.py` liegen im Diff dieses Runs;
der Fehlschlag tritt im unveränderten Ausgangsbaum identisch auf.

## 4. Laufzeitproben

```text
$ python probe_obs050_ordering_fix.py                        8/8 PASS   (exit 0)
    A   Historie streng absteigend über drei Seiten, keine Duplikate
    A'  kein Rückwärtssprung an einer Seitengrenze
    A2  automatisches Nachladen am Listenende hält die Ordnung
    B   Live-Start auf leerem Ergebnis: aufsteigend, keine Duplikate
    B'  weitere Tails setzen fort, ohne Duplikate
    B'' Cursor steht auf dem neuesten Record (id:8)
    C   Live auf befülltem Store unverändert korrekt
    D   Filterwechsel im Live-Modus: kein Duplikat, Reihenfolge hält

$ python <RUN-01>/probe_obs050_end_to_end.py                12/12 PASS  (exit 0)

$ python <GATE-REVIEW-01>/gate_probe_obs050_ordering.py
    B  ascending: True   duplicates present: False     <- B-2 behoben
    A  chronologically monotone after load_more: False <- siehe FIX_SUMMARY 1.3
    FAILURES: 1

$ python <GATE-REVIEW-01>/gate_probe_obs050_live_happy_path.py
    C  ascending=True duplicates=False
```

Die Gate-Probe prüft Fall A hart auf *aufsteigende* Monotonie. Dieser Lauf hat
die vom Gate ausdrücklich angebotene **Variante 1** umgesetzt (durchgehend
absteigend, neueste oben), weshalb diese eine Zusicherung erwartungsgemäß
`False` meldet, obwohl kein Rückwärtssprung mehr existiert. Begründung und
richtungsbewusster Ersatznachweis: `FIX_SUMMARY.md` Abschnitt 1.

## 5. Bekannte Einschränkungen

- Weiterhin offscreen: geprüft wird Verhalten, nicht Aussehen.
- Die Leserichtung wechselt zwischen Historie und Live bewusst; ob die
  Beschriftung in der Statuszeile am echten Desktop ausreicht, ist ein
  manueller Punkt (`UI_ACCEPTANCE.md` dieses Runs, Abschnitt 5).
- Dauerlast und Antwortzeiten bleiben OBS-060-Gegenstand.
