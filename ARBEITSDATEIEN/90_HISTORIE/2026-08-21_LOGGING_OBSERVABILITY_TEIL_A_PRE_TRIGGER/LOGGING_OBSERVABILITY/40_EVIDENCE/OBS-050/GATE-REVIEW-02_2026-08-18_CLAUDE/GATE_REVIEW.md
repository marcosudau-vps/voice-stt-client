# OBS-050 – Gate Review II (gezielter Re-Review des Korrekturlaufs)

Datum: 2026-08-18
Prompt: `30_AUSFUEHRUNG/Prompts/OBS-050_GATE_REVIEW.md` (Re-Review-Auftrag)
Geprüfter Run: `RUN-OBS-050-02_2026-08-18` (Korrekturlauf zu B-1/B-2)
Vorheriges Gate: `40_EVIDENCE/OBS-050/GATE-REVIEW-01_2026-08-18_CLAUDE/GATE_REVIEW.md`
(**`OBS-050 GATE FAIL`**, zwei blockierende Befunde)
Workspace: `voice-stt-client/workspaces/einheitliche-triggerarchitektur`
Branch: `feat/einheitliche-triggerarchitektur`, HEAD bei Reviewbeginn `91a7b7f`
Interpreter: Python 3.12.10, PySide6 offscreen

## Ergebnis

**OBS-050 GATE PASS – OBS-060 MAY PROCEED**

Dies ist **kein** vollständiger neuer Gate-Review. Die im ersten Gate bereits
bestandenen Bereiche — Query-Layer, Settings und Apply-Kette, Manager, Worker,
Löschfunktion, Managerlebensdauer, Importrichtung, „Logging läuft ohne UI",
Tabellenmodell, Filterleiste, Detailansicht — sind nachweislich unverändert
(Abschnitt 1) und werden nicht erneut auditiert. Geprüft wurden ausschließlich
der Korrekturdiff, die beiden früheren Blocker, die neuen bzw. geänderten
Tests und eine Regression.

---

## 1. Tatsächlicher Korrekturscope

Der Korrekturlauf gibt an, produktseitig nur `ui/logs/log_page.py` und
testseitig `tests/test_obs050_ui.py` sowie `tests/test_obs050_contracts.py`
geändert zu haben. **Bestätigt.**

Der versionierte Anteil ist gegenüber dem ersten Gate **stat-identisch**:

```text
$ git diff --stat -- app.py core/ ui/ .gitignore
 .gitignore                    |   4 ++
 app.py                        |  11 ++--
 core/controller.py            |  28 +++++++++
 core/logging_setup.py         |   7 +++
 core/observability/ingress.py |  73 +++++++++++++++++++++-
 core/observability/manager.py | 137 ++++++++++++++++++++++++++++++++++++++----
 core/observability/worker.py  |  59 ++++++++++++++++++
 ui/application.py             |  96 +++++++++++++++++++++++++++--
 ui/settings_dialog.py         |  74 +++++++++++++++++++++--
 ui/tray.py                    |  11 ++++
 10 files changed, 475 insertions(+), 25 deletions(-)
```

Dieselben zehn Dateien mit **exakt denselben** Zahlen wie im ersten Gate. Für
die noch unversionierten Neudateien wurden die Änderungszeitpunkte verglichen:

```text
2026-08-18 03:31  ui/logs/log_page.py            <- Korrektur
2026-08-18 03:33  tests/test_obs050_ui.py        <- Korrektur
2026-08-18 03:33  tests/test_obs050_contracts.py <- Korrektur

2026-08-17 23:06  core/observability/query/local.py      unverändert
2026-08-17 23:07  core/observability/query/service.py    unverändert
2026-08-17 23:19  core/logging_settings_metadata.py      unverändert
2026-08-17 23:10  ui/logs/__init__.py                    unverändert
2026-08-17 23:11  ui/logs/log_table_model.py             unverändert
2026-08-17 23:11  ui/logs/log_filter_bar.py              unverändert
2026-08-17 23:12  ui/logs/log_detail_view.py             unverändert
2026-08-17 23:14  ui/logs/log_window.py                  unverändert
2026-08-17 23:31  ui/logs/log_query_controller.py        unverändert
2026-08-17 23:21  tests/test_obs050_local_provider.py    unverändert
2026-08-17 23:22  tests/test_obs050_query_service.py     unverändert
2026-08-17 23:24  tests/obs050_apply_support.py          unverändert
2026-08-18 02:46  tests/test_obs050_settings.py          (RUN-01, vor dem Gate)
```

Die Evidence des ersten Gates und die RUN-01-Evidence sind **unangetastet**;
der Korrekturlauf hat seine Richtigstellung von W-2 in einer eigenen Datei
(`RUN-02_2026-08-18/UI_ACCEPTANCE.md`) abgelegt, statt die FAIL-Historie zu
überschreiben. Das entspricht der Ablageregel des Arbeitssystems.

**Folge:** Die PASS-Befunde des ersten Gates gelten unverändert weiter.

---

## 2. B-1 – Anzeigereihenfolge beim Nachladen älterer Seiten

### 2.1 Ist die gewählte absteigende Darstellung normativ zulässig?

**Ja.** Geprüft gegen den bereits gelesenen Normkontext; es wurde **keine**
neue Contract-Entscheidung getroffen:

* `LOGGING_CONTRACTS_FREEZE_V1.md §5.7` friert die Listenabfrage mit
  `ORDER BY id DESC` und die Folgeseite mit `AND id < :after_id` ein — der
  Historiepfad **läuft** absteigend.
* `§8` friert `QueryFilter.newest_first: bool = True` als Default ein.
* `§9.3` verlangt „automatisches Nachladen am **Listenende**". Mit absteigender
  Anzeige ist das Listenende der ältere Rand — genau dort, wo die per Keyset
  nächste (ältere) Seite hingehört.
* `§9.2` friert für den **Live**-Modus `WHERE id > :last ORDER BY id` ein, also
  aufsteigend; dazu passt `§9.3`s Auto-Scroll, das sich beim Hochscrollen
  abschaltet (neueste unten).

Eine **aufsteigende Historiedarstellung wird nirgends gefordert**. Die
Erwartung „aufsteigend" meiner ersten Probe war eine Ableitung aus dem
damaligen Modulkommentar, nicht aus dem Freeze; sie ist als PASS/FAIL-Kriterium
hiermit ausdrücklich **aufgehoben**. Kein `DECISION REQUIRED`.

Dass beide Modi in verschiedene Richtungen lesen, ist damit nicht Willkür,
sondern jeweils die Richtung der eingefrorenen Abfrage. Die Statuszeile benennt
sie jetzt („neueste oben" / „neueste unten"), was den einzigen verbleibenden
Fehllesegrund beseitigt.

### 2.2 Verhalten – eigene Laufzeitprobe gegen den echten Stack

`gate2_probe_obs050_b1_b2.py`, echter `SQLiteLogStore`, echter
`LocalLogProvider`, echter `LogQueryService`, echtes Qt-`LogPage`, 23 Zeilen,
Seitengröße 5, **fünf** Seiten:

```text
[PASS] B1-a erste Historieseite absteigend (neueste oben) - ids=[23,22,21,20,19]
[PASS] B1-b fünf Seiten bleiben streng absteigend, kein Richtungsbruch
              23 Zeilen, erste=[23,22,21], letzte=[3,2,1]
[PASS] B1-c keine Duplikate über die Seiten - 23 Zeilen / 23 eindeutig
[PASS] B1-d keine Auslassungen: die gelaufene Menge entspricht dem Store
[PASS] B1-e letzte Seite meldet keine weitere Seite - next_cursor=None
[PASS] B1-f automatisches Nachladen am Listenende hält dieselbe Ordnung
              5 -> 23 Zeilen, strikt absteigend=True
```

B1-f fährt das echte `QScrollBar`-Ereignis (`setValue(maximum())`) auf einem
sichtbaren Widget, nicht nur den Slot. Manuelles und automatisches Nachladen
führen zum selben Ergebnis.

**Provider-/Keyset-Cursor unverändert:** `core/observability/query/local.py`
ist byte-identisch zum ersten Gate (Abschnitt 1); die Korrektur liegt
ausschließlich in der Anzeige. B1-d vergleicht die gelaufene Reihenfolge gegen
eine unabhängige Direktabfrage desselben Stores.

**B-1: PASS.** Festgestellte Sortierrichtung: **Historie absteigend, neueste
oben; Live aufsteigend, neueste unten** — beides normativ gedeckt.

---

## 3. B-2 – erster Live-Tail nach leerem Ausgangsergebnis

### 3.1 Struktur

Der fehlerhafte Zweig wurde nicht repariert, sondern **entfernt**. Jede Abfrage
läuft durch den einen Trichter `LogPage._issue(kind, …)`, der die Anfrage-ID
und die **Art** der Anfrage in demselben Schritt festhält
(`REQUEST_HISTORY_FIRST`, `REQUEST_HISTORY_MORE`, `REQUEST_LIVE_SEED`,
`REQUEST_LIVE_TAIL`); `_on_page_ready` verzweigt über diese Art und
**verbraucht** sie dabei. Die Ableitung aus `_live_cursor` existiert nicht mehr
— nachgelesen im Quelltext und strukturell abgesichert (Abschnitt 4).
`_live_cursor` wird in **beiden** Live-Fällen aus der **jüngsten** gelieferten
Zeile gesetzt (Seed: `ordered[-1]` nach der einen verbliebenen Umkehrung;
Tail: `records[-1]`).

### 3.2 Verhalten – Reproduktion des ursprünglichen Fehlerfalls

```text
[PASS] B2-a Live-Seed auf leerem Store: 0 Zeilen, Cursor None
[PASS] B2-b erster Tail nach leerem Seed aufsteigend, keine Duplikate - ids=[1,2,3,4,5]
[PASS] B2-c Cursor zeigt auf den neuesten verarbeiteten Record - cursor=5, max=5
[PASS] B2-d weitere Tails setzen dahinter fort, keine Duplikate, nichts verloren
              5 -> 9 -> 12 Zeilen, Präfix stabil
[PASS] B2-e Live mit Filter ohne Treffer bleibt leer
[PASS] B2-f später eintreffende passende Zeilen tailen korrekt unter dem Filter
[PASS] B2-g Filterwechsel im Live-Modus setzt neu auf, ohne Duplikat
[PASS] B2-h befüllter Normalfall unverändert korrekt (Gegenprobe C des 1. Gates)
[PASS] B2-i ein veralteter _live_cursor ändert die Deutung einer Antwort nicht mehr
```

B2-e/B2-f benutzen einen **echten** Filter (`channels=("audit",)`) gegen den
echten Provider, nicht ein geleertes Double. B2-i vergiftet `_live_cursor`
absichtlich vor einem `load_more()` — die Antwort wird trotzdem als
Historieseite gelesen; das ist der Beweis, dass die Antwortart an der Anfrage
hängt und nicht an veränderlichem Zustand.

Zusätzlich bestätigt die **unveränderte** Probe des ersten Gates denselben
Fall: `B ascending: True   duplicates present: False` (ihre Fall-A-Erwartung
„aufsteigend" ist nach Abschnitt 2.1 gegenstandslos und wurde nicht als
Kriterium verwendet).

**B-2: PASS.**

---

## 4. Neue und geänderte Tests

### 4.1 `tests/test_obs050_ui.py` — acht neue Tests, einer umbenannt

| Test | Gegenstand | Bewertung |
|---|---|---|
| `test_history_mode_shows_the_newest_page_first_newest_on_top` | erste Seite, vollständige Reihenfolge | umbenannt und in der Erwartung an die Korrektur angepasst; prüft jetzt die **ganze** Sequenz statt zweier Randzeilen |
| `test_display_order_stays_monotone_across_three_history_pages` | drei Seiten, komplette Sequenz, Monotonie, Duplikatfreiheit, drei Abfragen mit Cursor ab Seite 2 | schließt W-1 genau an der Stelle, an der B-1 durchgerutscht war |
| `test_automatic_load_at_the_list_end_keeps_the_order` | Nachladen ohne Knopfdruck | zusätzlicher Pfad, gleiche Zusicherung |
| `test_live_start_on_an_empty_result_set_then_records_arrive` | B-2-Regression inkl. **zweitem und drittem** Tail und Cursorwert | genau der reproduzierte Fehlerfall |
| `test_further_records_after_an_empty_start_extend_the_tail` | mehrere aufeinanderfolgende Tails | Reihenfolge, Duplikate, Cursor |
| `test_live_start_with_a_filter_that_matches_nothing_then_matches` | Filter ohne Treffer | Alltagsfall |
| `test_filter_change_during_live_reseeds_without_duplicates` | Filterwechsel im Live-Modus | genau der Zustand, der die alte Fehldeutung auslöste |
| `test_live_start_on_a_populated_store_stays_correct` | Normalfall | verhindert eine Regression der bereits korrekten Seite |
| `test_a_response_is_interpreted_by_its_request_not_by_the_cursor` | wiederholte Zustellung derselben Antwort ist ein No-Op | strukturelle Hälfte des B-2-Fixes |

Die Tests laufen über den **echten** `LogQueryController` samt Executor-Thread
und prüfen vollständige Sequenzen (`assertEqual` auf die Liste), nicht nur
Zeilenzahlen — genau die Schwäche, die W-1 benannt hatte. Das Double
`FakeService` ist **unverändert** gegenüber RUN-01 und bildet die
Keyset-Semantik des Providers weiterhin korrekt ab; es wurde nicht an die neue
Erwartung angepasst.

**Kein bestehender Test wurde abgeschwächt.** `test_load_more_pages_backwards_with_the_cursor`
und `test_load_more_does_nothing_without_a_next_page` bleiben unverändert
bestehen.

### 4.2 `tests/test_obs050_contracts.py` — Anpassung an `_issue`, keine Aufweichung

`test_the_live_mode_queries_the_provider` prüfte den Quelltext von `_tail` auf
`newest_first=False` **und** `request_page`. Da `_tail` die Abfrage jetzt über
`_issue` absetzt, prüft der Test `newest_first=False` und `_issue` in `_tail`
und zusätzlich `request_page` im Trichter `_issue` — dieselbe Anforderung, an
beiden Enden geprüft, **nicht** gelockert.

Neu hinzugekommen ist `test_every_query_records_the_kind_of_request_it_was`:
`reload`, `load_more` und `_tail` müssen `self._issue(` benutzen und dürfen
`next_request_id` **nicht** selbst aufrufen, und `_issue` muss
`self._active_kind = kind` enthalten. Das ist eine **Verschärfung**: die
Rückkehr zur zustandsabhängigen Fallunterscheidung wird strukturell verhindert.

Alle übrigen Contract-Tests (Modulstruktur `ARCH §5.1`, Importrichtung `§5.2`,
kein Ringbuffer, kein `live_buffer_size`, 250 ms / `LIMIT 500`, Query-Verträge,
„Logging läuft ohne UI") sind unverändert. Testzahl der Datei: 21 → 22.

**Bewertung: zulässig.**

---

## 5. Regression

```text
$ QT_QPA_PLATFORM=offscreen python -m pytest tests -q -k obs050
179 passed, 959 deselected, 319 subtests passed                     (exit 0)

$ QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -p "test_obs050_*.py"
Ran 179 tests ... OK                                                (exit 0)

$ QT_QPA_PLATFORM=offscreen python -m pytest tests -q      (drei Läufe)
Lauf 1:  2 failed, 1136 passed, 859 subtests passed
Lauf 2:  1 failed, 1137 passed, 859 subtests passed
Lauf 3:  1 failed, 1137 passed, 859 subtests passed

$ git diff --check
(leer, exit 0)
```

170 → **179** Tests: exakt die neun neuen (acht in `test_obs050_ui.py`, einer
in `test_obs050_contracts.py`). Gesamtzahl 1138 = 1129 der Baseline `91a7b7f`
plus 179 − 170 = 9. Der Fehlschlag
`tests/test_ap06_followup.py::…::test_failed_runtime_submit_rolls_hotkeys_and_file_back`
(`ModuleNotFoundError: No module named 'lefx.interfaces'`) ist derselbe wie im
ersten Gate, tritt identisch auf und liegt außerhalb des Korrekturdiffs; er
wurde nicht erneut untersucht.

**Zum zweiten Fehlschlag in Lauf 1**
(`tests/test_ui_widgets.py::TestTranscriptOverlay::test_realtime_replaces_text_and_final_fades`):
gezielt nachgeprüft und als **flatterhaft, nicht als Regression** eingeordnet.
Er trat in Lauf 2 und Lauf 3 nicht auf, die Datei allein läuft zweimal
hintereinander grün (20/20), und `tests/test_ui_widgets.py` wie `ui/overlay.py`
stammen vom 2026-08-14 — beide außerhalb von RUN-01 **und** RUN-02. Der Test
wartet mit `QTest.qWait(350)` auf eine Ausblendanimation und ist damit
lastabhängig; der im Lauf 1 mit ausgegebene alte Worktree-Pfad kam aus einem
veralteten `__pycache__`-Eintrag, der inzwischen neu erzeugt ist.

---

## 6. Entscheidung

| Prüfpunkt | Ergebnis |
|---|---|
| Korrekturscope eng geblieben wie behauptet | **ja** |
| B-1 geschlossen | **ja** (Historie absteigend, normativ gedeckt, über fünf Seiten deterministisch) |
| B-2 geschlossen | **ja** (Antwortart hängt an der Anfrage, Cursor auf der jüngsten Zeile) |
| neue Tests schließen die Lücken (W-1) | **ja** |
| Contract-Test nicht abgeschwächt | **ja**, sogar verschärft |
| W-2 richtiggestellt | **ja**, in `RUN-02_2026-08-18/UI_ACCEPTANCE.md`, FAIL-Historie erhalten |
| Regression | **keine** |

**`OBS-050 GATE PASS – OBS-060 MAY PROCEED`**

Die nicht blockierenden Beobachtungen N-1 bis N-7 des ersten Gates bleiben
bestehen und sind für OBS-060 vorgemerkt; keine davon war Gegenstand dieses
Korrekturlaufs.

Nach diesem Gate wird genau **ein** lokaler Commit für den geprüften
OBS-050-Endstand erstellt
(`feat(observability): complete OBS-050 local log view`). Die acht bewusst
unversionierten Prompt- und Pipeline-Einträge unter `30_AUSFUEHRUNG/` sind
nicht aufgenommen. Kein Push, kein Merge, kein Rebase, kein Tag, kein PR.
OBS-060 wird nicht begonnen.

---

## 7. Artefakte dieses Reviews

| Datei | Inhalt |
|---|---|
| `gate2_probe_obs050_b1_b2.py` | 15 Prüfungen zu B-1 und B-2 gegen echten Store, echten Provider, echten Service und echtes `LogPage` (offscreen). 15/15 PASS, exit 0. |
