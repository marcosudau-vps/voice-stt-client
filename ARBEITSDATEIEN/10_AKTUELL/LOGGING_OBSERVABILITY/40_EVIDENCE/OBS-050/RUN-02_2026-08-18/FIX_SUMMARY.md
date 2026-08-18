# OBS-050 RUN-02 – FIX_SUMMARY

Korrekturlauf zu `OBS-050 GATE FAIL`
(`40_EVIDENCE/OBS-050/GATE-REVIEW-01_2026-08-18_CLAUDE/GATE_REVIEW.md`).
Behandelt werden ausschließlich **B-1**, **B-2** und die dazugehörige
Testlücke **W-1**; die Evidenzformulierung **W-2** ist in `UI_ACCEPTANCE.md`
dieses Runs richtiggestellt.

Beide Blocker wurden vor der Korrektur **selbst reproduziert**, mit der
unveränderten Gate-Probe gegen den echten Stack:

```text
A1 first page (top->bottom): ['r0007','r0008','r0009','r0010','r0011']
A2 after 'Weitere laden'   : ['r0007','r0008','r0009','r0010','r0011',
                              'r0002','r0003','r0004','r0005','r0006']
A  chronologically monotone after load_more: False
B1 after first tail        : ['r0004','r0003','r0002','r0001','r0000',
                              'r0001','r0002','r0003','r0004']
B  ascending: False   duplicates present: True
FAILURES: 2                                                    (exit 1)
```

---

## 1. B-1 – nicht monotone Anzeigereihenfolge beim Nachladen

### 1.1 Ursache

`_on_page_ready` drehte **jede** Historieseite mit `tuple(reversed(records))`
in aufsteigende Richtung und hängte jede Folgeseite mit `append_page` **unten**
an. Eine Folgeseite enthält per Keyset (`id < :after_id`) aber ausschließlich
**ältere** Zeilen. Innerhalb eines Blocks lief die Zeit damit vorwärts,
zwischen zwei Blöcken sprang sie zurück:

```text
r7 r8 r9 r10 r11 | r2 r3 r4 r5 r6
                 ^ Sprung um neun Positionen zurück
```

Die Umkehrung stammte aus RUN-01 und war dort mit *„a log is read top-down"*
begründet — sie ist genau der Grund für den Befund. Die Keyset-Semantik des
Providers ist davon nicht betroffen und wurde **nicht** angefasst.

### 1.2 Korrektur

Der Gate-Review nennt zwei zulässige minimale Korrekturen und verlangt
ausdrücklich **eine von beiden**. Umgesetzt ist **Variante 1**:

> „Die Umkehrung je Seite entfällt; die Tabelle zeigt durchgehend absteigend
> (neueste oben). Das passt ohne weitere Änderung zum bestehenden
> Nachladen-am-Listenende, weil ‚unten‘ dann ‚älter‘ bedeutet."

Konkret in `ui/logs/log_page.py`:

* Der Historiezweig von `_on_page_ready` zeigt die Seite **so, wie der Provider
  sie geliefert hat** (`newest_first=True`, also absteigend). Es gibt dort
  keine Umkehrung mehr.
* Die erste Seite wird gesetzt, jede Folgeseite unten angehängt — „unten"
  heißt jetzt „älter", und die Reihenfolge bleibt über beliebig viele Seiten
  streng monoton.
* `_on_scrolled` bleibt **unverändert** am unteren Rand: das von `§9.3`
  geforderte *„automatisches Nachladen am Listenende"* trifft damit
  buchstäblich die Stelle, an der die nächste Seite hingehört.
* Der Live-Modus behält seine aufsteigende Richtung; die **einzige** verbliebene
  Umkehrung im Modul dreht die absteigende **Seed**-Seite des Live-Modus in
  genau diese Richtung, damit die Tails sie fortsetzen statt ihr zu
  widersprechen.

Warum Variante 1 und nicht Variante 2 („Folgeseite oben einfügen"): Variante 2
hätte den automatischen Nachladepunkt an den **oberen** Rand verlegt und damit
den Wortlaut von `§9.3` („am Listenende") gedehnt, und sie hätte zum Einfügen
oben entweder eine neue Modellmethode (zweite Produktdatei) oder einen
vollständigen `set_records`-Reset je Seite gebraucht — Letzteres verwirft
Auswahl und Detailansicht bei jedem Nachladen. Variante 1 kommt ohne beides
aus und ist die kleinere Änderung.

Die Anzeigerichtung ist jetzt in der Statuszeile benannt („neueste oben" /
„neueste unten"), damit die einzige Stelle, die man missverstehen könnte, im
laufenden Programm sichtbar ist.

### 1.3 Nachweis

`probe_obs050_ordering_fix.py`, Fälle A und A2 (echter Store, echter Provider,
echter Service, echtes `LogPage`):

```text
A1 erste Seite      : ['r0011','r0010','r0009','r0008','r0007']
A2 nach drei Seiten : ['r0011','r0010','r0009','r0008','r0007',
                       'r0006','r0005','r0004','r0003','r0002',
                       'r0001','r0000']
[PASS] A  Historie: streng absteigend ueber drei Seiten, keine Duplikate
       - 12 Zeilen, monoton=True, eindeutig=True
[PASS] A' kein Rueckwaertssprung an einer Seitengrenze
       - Grenze 1: r0007 > r0006, Grenze 2: r0002 > r0001
A3 nach Auto-Nachladen am Listenende: [... 10 Zeilen ...]
[PASS] A2 automatisches Nachladen am Listenende haelt die Ordnung
```

**Hinweis zur unveränderten Gate-Probe.** Sie prüft Fall A hart auf
*aufsteigende* Monotonie und meldet für Variante 1 daher weiterhin
`monotone: False` — nicht, weil ein Rückwärtssprung bliebe, sondern weil die
Tabelle jetzt durchgehend absteigend ist. Ihre Rohausgabe nach der Korrektur:

```text
A1 first page (top->bottom): ['r0011','r0010','r0009','r0008','r0007']
A2 after 'Weitere laden'   : ['r0011','r0010','r0009','r0008','r0007',
                              'r0006','r0005','r0004','r0003','r0002']
A  chronologically monotone after load_more: False   <- Variante-1-Erwartung
B  ascending: True   duplicates present: False       <- B-2 behoben
FAILURES: 1
```

Die inhaltliche Eigenschaft, um die es dem Gate geht — **kein Rückwärtssprung
über eine Seitengrenze** —, ist erfüllt und wird in `probe_obs050_ordering_fix.py`
richtungsbewusst geprüft.

---

## 2. B-2 – Live-Modus nach leerem Ausgangsergebnis

### 2.1 Ursache

`_on_page_ready` entschied über die Art einer Antwort mit

```python
if self._mode == MODE_LIVE and self._live_cursor is not None:
```

also anhand **veränderlichen Zustands** statt anhand der abgeschickten
Anfrage. Liefert die Seed-Abfrage des Live-Modus keine Zeile — leerer Store,
frische Installation, Filter ohne Treffer, oder unmittelbar nach jedem
Filterwechsel, weil `reload()` den Cursor zurücksetzt —, bleibt
`_live_cursor` `None`. Die erste **aufsteigende** Tail-Antwort fiel dann in
den absteigenden Zweig:

1. sie wurde mit `reversed(...)` umgedreht (neueste oben, entgegen der
   Live-Konvention samt `scrollToBottom`), und
2. `_live_cursor` wurde aus `records[0]` gesetzt — in einer aufsteigenden
   Liste die **älteste** Zeile.

Der nächste Tail fragte `id > <älteste>` und lieferte dieselben Zeilen erneut,
die dann angehängt wurden.

### 2.2 Korrektur

Die Semantik einer Antwort ergibt sich jetzt aus der **Anfrage**:

* Vier Anfragearten sind benannt: `REQUEST_HISTORY_FIRST`,
  `REQUEST_HISTORY_MORE`, `REQUEST_LIVE_SEED`, `REQUEST_LIVE_TAIL`.
* Jede Abfrage läuft durch den einen Trichter `LogPage._issue`, der die
  Anfrage-ID reserviert **und** die Art in demselben Schritt festhält. Es gibt
  keinen Pfad mehr, der eine ID vergibt, ohne zu vermerken, was gefragt wurde
  — ein Contract-Test hält genau das fest.
* `_on_page_ready` verzweigt über diese Art. Sie wird beim Verarbeiten
  **verbraucht**, sodass eine wiederholte Zustellung derselben Antwort folgenlos
  bleibt.
* `_live_cursor` wird in beiden Live-Fällen aus der **jüngsten** gelieferten
  Zeile gesetzt: beim Seed nach dem Drehen die letzte, beim Tail ohnehin die
  letzte.

Damit ist der fehlerhafte Zweig nicht repariert, sondern entfernt: die
Fallunterscheidung kann gar nicht mehr aus dem Cursorstand entstehen.

### 2.3 Nachweis

`probe_obs050_ordering_fix.py`, Fälle B, C und D:

```text
B0 Zeilen nach Live-Start auf leerem Store: 0
B1 nach erstem Tail     : ['r0000','r0001','r0002','r0003','r0004']
B2 nach zweitem Tail    : ['r0000','r0001','r0002','r0003','r0004']
B3 nach weiteren Records: ['r0000',...,'r0007']
[PASS] B   Live-Start auf leerem Ergebnis: aufsteigend, keine Duplikate
[PASS] B'  weitere Tails setzen die Reihenfolge fort, ohne Duplikate
[PASS] B'' Cursor steht auf dem neuesten Record - live_cursor=id:8
[PASS] C   Live auf befuelltem Store (Gate-Gegenprobe) unveraendert korrekt
[PASS] D   Filterwechsel im Live-Modus: kein Duplikat, Reihenfolge haelt
```

Die unveränderte Gate-Probe bestätigt denselben Fall:
`B ascending: True   duplicates present: False`.

Die vom Auftrag geforderten Situationen sind damit abgedeckt: frische
Installation/leerer Store (B), Filter ohne Treffer (B und der Test
`test_live_start_with_a_filter_that_matches_nothing_then_matches`),
Filterwechsel im laufenden Live-Modus (D), erster Record nach leerem Ergebnis
(B1), mehrere aufeinanderfolgende Tails (B2/B3) und der bereits befüllte
Normalfall (C).

---

## 3. Geänderte Dateien

| Datei | Art | Umfang |
|---|---|---|
| `ui/logs/log_page.py` | **Produkt** | 456 → 526 Zeilen; vier Stellen: Modul-Docstring (Ordnungsinvariante), vier Anfragearten als Konstanten, `_issue` als einziger Abfragetrichter, `_on_page_ready` verzweigt über die Anfrageart; dazu die Richtungsangabe in der Statuszeile |
| `tests/test_obs050_ui.py` | Test | +9 Tests (B-1: 3, B-2: 6), eine bestehende OBS-050-Erwartung richtiggestellt |
| `tests/test_obs050_contracts.py` | Test | `test_the_live_mode_queries_the_provider` folgt dem Trichter; ein neuer Strukturtest `test_every_query_records_the_kind_of_request_it_was` |

**Keine weitere Produktdatei berührt.** Query-Layer, Settings, Apply-Kette,
Manager, Worker, Modell, Fenster, Filterleiste und Detailansicht sind
unverändert — nachgewiesen über die Änderungszeitstempel und darüber, dass
`git diff --stat` für die versionierten Bestandsdateien exakt denselben Stand
zeigt wie am Ende von RUN-01 (10 Dateien, +475/−25).

`ui/logs/log_page.py` und die Testdateien sind seit RUN-01 **unversioniert**
(kein Commit erstellt), erscheinen deshalb in `git status` als `??` und nicht
in `git diff --stat`.

### 3.1 Angepasste Erwartungen in RUN-01-Tests

Zwei Tests aus RUN-01 erwarteten das fehlerhafte Verhalten und sind
richtiggestellt — genau die Lücke, die das Gate als **W-1** benannt hat:

| Test | vorher | jetzt |
|---|---|---|
| `test_history_mode_loads_the_newest_page_first` | erwartete `r7` oben, `r11` unten (die B-1-Umkehrung) | `test_history_mode_shows_the_newest_page_first_newest_on_top`: prüft die vollständige Seite `r11 … r7` |
| `test_the_live_mode_queries_the_provider` | las `request_page` wörtlich in `_tail` | prüft `_tail` (fragt aufsteigend, benutzt den Trichter) **und** `_issue` (ruft `request_page`) |

Beide gehören zu OBS-050 und stammen aus RUN-01; kein Test außerhalb dieses
Work Packages wurde angefasst.

---

## 4. Verifikation

```text
python -m pytest tests -q -k obs050                179 passed, 319 subtests   (exit 0)
python -m unittest discover -p "test_obs050_*.py"  Ran 179 tests ... OK       (exit 0)
python -m pytest -k "obs010..obs050"               625 passed, 620 subtests   (exit 0)
python -m pytest tests -q                          1 failed, 1137 passed
python -m unittest discover -p "test_*.py"         Ran 1138 tests, 1 error
probe_obs050_ordering_fix.py                       8/8 PASS                   (exit 0)
probe_obs050_end_to_end.py (RUN-01, erneut)        12/12 PASS                 (exit 0)
gate_probe_obs050_ordering.py (unverändert)        B behoben; A siehe 1.3
gate_probe_obs050_live_happy_path.py               C ascending=True dup=False
git diff --check                                   leer                       (exit 0)
```

Vor der Korrektur waren es 170 OBS-050-Tests, jetzt 179 (+9). Die volle Suite
wuchs entsprechend von 1128 auf 1137 grüne Tests.

**Der eine Fehlschlag ist unverändert vorbestehend und liegt außerhalb des
Diffs:** `tests/test_ap06_followup.py::TestSettingsDialog::test_failed_runtime_submit_rolls_hotkeys_and_file_back`,
`ModuleNotFoundError: No module named 'lefx.interfaces'`. Nachgemessen:

* `git diff --name-only` enthält weder `tests/test_ap06_followup.py` noch
  `core/led_controller.py`; `git status --short` zeigt beide als unverändert.
* Derselbe Test schlägt im frisch aus `91a7b7f` ausgepackten Baum mit
  derselben Meldung fehl.

---

## 5. Scope- und Git-Abgleich

```text
HEAD                       91a7b7f (unverändert, kein Commit)
git diff --check           leer
git diff --stat            10 Dateien, +475/−25  — identisch zu RUN-01
00_NORMATIV/               unverändert
core/settings_metadata.py  unverändert
Cross-Workstream-Diff      keiner
```

Die acht bewusst unversionierten Prompt- und Pipeline-Einträge unter
`30_AUSFUEHRUNG/` sind unangetastet und wurden nicht gestaged.

Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.
