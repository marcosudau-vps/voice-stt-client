# RUN_LOG – RUN-OBS-050-02_2026-08-18 (Korrekturlauf)

Work Package: **OBS-050 – Local Query, Minimal UI & Settings**
Anlass: `OBS-050 GATE FAIL`
(`40_EVIDENCE/OBS-050/GATE-REVIEW-01_2026-08-18_CLAUDE/GATE_REVIEW.md`)
Ausgangscommit: `91a7b7f`, Branch `feat/einheitliche-triggerarchitektur`

## 1. Pflichtlektüre

Vollständig gelesen: der Gate-Review samt seinen beiden Probeskripten, der
ursprüngliche Implementierungsauftrag `OBS-050_IMPLEMENTIERUNGSAUFTRAG.md`,
das Work Package `WP-OBS-050`, `LOGGING_CONTRACTS_FREEZE_V1.md` §5.7/§8/§9,
`LOGGING_ARCHITEKTUR_FREEZE_V1.md` §5.1/§5.2/§11.2/§12,
`LOGGING_DECISIONS_FREEZE_V1.md` FD-S1, sowie der tatsächliche Code in
`ui/logs/log_page.py`.

## 2. Eigene Reproduktion vor jeder Änderung

Der Auftrag verlangt ausdrücklich, sich nicht auf die Zusammenfassung zu
verlassen. Die unveränderte Gate-Probe wurde gegen den echten Stack laufen
gelassen:

```text
A2 after 'Weitere laden': ['r0007','r0008','r0009','r0010','r0011',
                           'r0002','r0003','r0004','r0005','r0006']
A  chronologically monotone after load_more: False
B1 after first tail     : ['r0004','r0003','r0002','r0001','r0000',
                           'r0001','r0002','r0003','r0004']
B  ascending: False   duplicates present: True
FAILURES: 2                                                     (exit 1)
```

Beide Befunde reproduzieren exakt wie beschrieben. Anschließend am Code
verifiziert:

* **B-1** — `_on_page_ready`, Historiezweig: `tuple(reversed(records))` je
  Seite, Folgeseite über `append_page` **unten** angehängt. Eine Folgeseite
  enthält per Keyset ausschließlich ältere Zeilen, also springt die Zeit an
  jeder Seitengrenze zurück.
* **B-2** — die Verzweigung
  `if self._mode == MODE_LIVE and self._live_cursor is not None:` entscheidet
  über die Art einer Antwort anhand veränderlichen Zustands. Bleibt der Cursor
  nach einem leeren Seed `None`, fällt die erste aufsteigende Tail-Antwort in
  den absteigenden Zweig: umgedreht dargestellt und der Cursor aus der
  **ältesten** Zeile gesetzt, worauf der nächste Tail dieselben Zeilen erneut
  liefert.

## 3. Korrektur

### 3.1 B-1

Der Gate-Review nennt zwei zulässige minimale Korrekturen, „eine von beiden,
nicht beide". Umgesetzt ist **Variante 1**: die Umkehrung je Historieseite
entfällt, die Tabelle zeigt die Seite so, wie der Provider sie geliefert hat
(absteigend, neueste oben), und die ältere Folgeseite gehört damit
folgerichtig nach unten. `_on_scrolled` bleibt unverändert am unteren Rand —
das eingefrorene *„automatisches Nachladen am Listenende"* (`§9.3`) trifft so
buchstäblich die Stelle, an der die nächste Seite hingehört.

Warum nicht Variante 2 („Folgeseite oben einfügen"): sie hätte den
automatischen Nachladepunkt an den oberen Rand verlegt und damit den Wortlaut
von `§9.3` gedehnt, und zum Einfügen oben entweder eine neue Modellmethode
(zweite Produktdatei, außerhalb des vom Auftrag gesetzten Minimalumfangs) oder
einen vollständigen `set_records`-Reset je Seite gebraucht — Letzteres verwirft
Auswahl und Detailansicht bei jedem Nachladen.

Die Anzeigerichtung des aktiven Modus steht jetzt in der Statuszeile
(„neueste oben" / „neueste unten").

### 3.2 B-2

Die Semantik einer Antwort folgt jetzt aus der Anfrage:

* vier benannte Anfragearten (`REQUEST_HISTORY_FIRST`, `REQUEST_HISTORY_MORE`,
  `REQUEST_LIVE_SEED`, `REQUEST_LIVE_TAIL`),
* ein einziger Abfragetrichter `LogPage._issue`, der Anfrage-ID **und** Art in
  demselben Schritt festhält — es gibt keinen Pfad mehr, der das eine ohne das
  andere tut,
* `_on_page_ready` verzweigt über die Art und **verbraucht** sie, sodass eine
  wiederholte Zustellung folgenlos bleibt,
* `_live_cursor` wird in beiden Live-Fällen aus der **jüngsten** gelieferten
  Zeile gesetzt.

Der fehlerhafte Zweig wurde damit nicht repariert, sondern entfernt: die
Fallunterscheidung kann gar nicht mehr aus dem Cursorstand entstehen.

Die bestehende OBS-050-Struktur bleibt: dieselbe Provider-Schnittstelle,
derselbe `QTimer` mit 250 ms, derselbe `ThreadPoolExecutor(max_workers=1)`,
kein Ringbuffer, keine neue Abfragearchitektur.

## 4. Umfang

Produktseitig **ausschließlich** `ui/logs/log_page.py` (456 → 526 Zeilen), wie
vom Auftrag vorgegeben. Kein Anhalten nötig — der Befund ist innerhalb dieser
einen Datei lösbar.

Testseitig `tests/test_obs050_ui.py` (+9 Tests, eine RUN-01-Erwartung
richtiggestellt) und `tests/test_obs050_contracts.py` (ein Test folgt dem neuen
Trichter, ein neuer Strukturtest). Die zweite Testdatei ist über den vom
Auftrag genannten Umfang hinaus berührt; sie ist **kein Produktcode**, und der
Grund ist mechanisch: `test_the_live_mode_queries_the_provider` liest den
Quelltext von `_tail` und suchte dort wörtlich `request_page`, das jetzt im
Trichter `_issue` steht. Der Test prüft nun beide Enden derselben Aussage.

Query-Layer, Settings, Apply-Kette, Manager, Worker, Tabellenmodell,
Filterleiste, Detailansicht und Fenster sind **unverändert**.

## 5. W-1 und W-2

* **W-1** (Testlücke): geschlossen durch die drei B-1- und sechs
  B-2-Regressionstests. Sie prüfen die tatsächliche UI-Verarbeitung über den
  echten `LogQueryController` samt Executor-Thread — keine isolierten
  Hilfsfunktionen.
* **W-2** (Evidenzformulierung): `RUN-02_2026-08-18/UI_ACCEPTANCE.md` stellt
  A-11 bis A-13 richtig und ergänzt A-34 bis A-42. Die RUN-01-Evidence und die
  Gate-FAIL-Evidence bleiben unverändert erhalten.

Die nicht blockierenden Beobachtungen N-1 bis N-7 des Gates sind **nicht**
Gegenstand dieses Laufs und bleiben für OBS-060 vorgemerkt.

## 6. Verifikation

```text
-k obs050 (pytest)            179 passed, 319 subtests            exit 0
-k obs050 (unittest)          Ran 179 tests ... OK                exit 0
OBS-010..050                  625 passed, 620 subtests            exit 0
volle Suite (pytest)          1 failed, 1137 passed
volle Suite (unittest)        Ran 1138 tests, 1 error
probe_obs050_ordering_fix     8/8 PASS                            exit 0
probe_obs050_end_to_end       12/12 PASS                          exit 0
Gate-Probe (unverändert)      B behoben; A siehe FIX_SUMMARY 1.3
Gate-Gegenprobe C             ascending=True duplicates=False
git diff --check              leer
git diff --stat               10 Dateien, +475/−25 (identisch zu RUN-01)
```

Der eine Fehlschlag (`lefx.interfaces`) ist nachgemessen vorbestehend und
liegt außerhalb des Diffs: weder `tests/test_ap06_followup.py` noch
`core/led_controller.py` erscheinen in `git diff --name-only`, und derselbe
Test schlägt im frisch aus `91a7b7f` ausgepackten Baum identisch fehl.

## 7. Grenzen dieses Runs

- Der OBS-050-Gate-Review **bleibt offen**. Ein Korrekturlauf vergibt sein
  eigenes Gate nicht.
- Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR. Die acht
  bewusst unversionierten Prompt- und Pipeline-Einträge sind unangetastet.
- OBS-060 wurde nicht begonnen.
