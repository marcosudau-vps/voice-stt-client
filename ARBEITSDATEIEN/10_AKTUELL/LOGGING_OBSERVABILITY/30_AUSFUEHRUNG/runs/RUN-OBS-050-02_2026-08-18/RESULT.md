# RESULT – RUN-OBS-050-02_2026-08-18 (Korrekturlauf)

## Ergebnis

`OBS-050 CORRECTED – READY FOR RE-REVIEW`

**Der OBS-050-Gate-Review bleibt offen.** Ein Korrekturlauf vergibt sein
eigenes Gate nicht; der erneute unabhängige Review gehört in eine frische
Session. **OBS-060 wurde nicht begonnen.**

## B-1 – nicht monotone Anzeige beim Nachladen

**Ursache.** `_on_page_ready` drehte **jede** Historieseite um und hängte jede
Folgeseite unten an. Eine Folgeseite enthält per Keyset aber ausschließlich
**ältere** Zeilen — innerhalb eines Blocks lief die Zeit vorwärts, zwischen
zwei Blöcken zurück. Die Umkehrung stammte aus RUN-01 und war dort mit „a log
is read top-down" begründet; sie ist genau der Grund für den Befund.

**Korrektur.** Variante 1 der beiden vom Gate angebotenen: Die Umkehrung
entfällt. Die Historie zeigt jede Seite so, wie der Provider sie geliefert hat
(`newest_first=True`, neueste oben), und die ältere Folgeseite gehört damit
folgerichtig nach unten. `_on_scrolled` bleibt unverändert am unteren Rand —
das eingefrorene *„automatisches Nachladen am Listenende"* trifft so
buchstäblich die Stelle, an der die nächste Seite hingehört. Die Keyset-/
Cursor-Semantik des Providers ist unberührt.

**Nachweis.** `probe_obs050_ordering_fix.py` gegen echten Store, echten
Provider, echten Service und echtes `LogPage`:

```text
A2 nach drei Seiten: ['r0011','r0010','r0009','r0008','r0007',
                      'r0006','r0005','r0004','r0003','r0002',
                      'r0001','r0000']
[PASS] streng absteigend über drei Seiten, keine Duplikate
[PASS] kein Rückwärtssprung an einer Seitengrenze (r0007 > r0006, r0002 > r0001)
[PASS] automatisches Nachladen am Listenende hält die Ordnung
```

## B-2 – Live-Modus nach leerem Ausgangsergebnis

**Ursache.** Die Ansicht entschied über die Art einer Antwort mit
`if self._mode == MODE_LIVE and self._live_cursor is not None:` — also anhand
veränderlichen Zustands statt anhand der abgeschickten Anfrage. Nach einem
leeren Seed bleibt der Cursor `None`, die erste **aufsteigende** Tail-Antwort
fiel in den absteigenden Zweig, wurde umgedreht dargestellt, und der Cursor
wurde aus der **ältesten** Zeile gesetzt. Der nächste Tail lieferte dieselben
Zeilen erneut.

**Korrektur.** Die Semantik folgt jetzt aus der Anfrage: vier benannte
Anfragearten, ein einziger Abfragetrichter `_issue`, der Anfrage-ID **und**
Art in demselben Schritt festhält, eine Verzweigung über diese Art, die sie
beim Verarbeiten verbraucht, und `_live_cursor` in beiden Live-Fällen aus der
**jüngsten** gelieferten Zeile. Der fehlerhafte Zweig wurde nicht repariert,
sondern entfernt — die Fallunterscheidung kann gar nicht mehr aus dem
Cursorstand entstehen. Keine neue Abfragearchitektur: dieselbe
Provider-Schnittstelle, derselbe 250-ms-`QTimer`, derselbe Executor, kein
Ringbuffer.

**Nachweis.**

```text
B0 Zeilen nach Live-Start auf leerem Store: 0
B1 nach erstem Tail     : ['r0000','r0001','r0002','r0003','r0004']
B2 nach zweitem Tail    : unverändert
B3 nach weiteren Records: ['r0000' … 'r0007']
[PASS] aufsteigend, keine Duplikate
[PASS] Cursor steht auf dem neuesten Record (id:8)
[PASS] Live auf befülltem Store (Gate-Gegenprobe C) unverändert korrekt
[PASS] Filterwechsel im Live-Modus: kein Duplikat, Reihenfolge hält
```

Die **unveränderte** Gate-Probe bestätigt denselben Fall:
`B ascending: True   duplicates present: False`.

## W-1 / W-2

**W-1** ist geschlossen: neun Regressionstests prüfen die tatsächliche
UI-Verarbeitung über den echten `LogQueryController` samt Executor-Thread —
drei für die Reihenfolge über zwei bzw. drei Seiten, sechs für den Live-Modus
(Leerstart, mehrere Tails, Filter ohne Treffer, Filterwechsel, befüllter
Normalfall, Antwortzuordnung). **W-2** ist in
`40_EVIDENCE/OBS-050/RUN-02_2026-08-18/UI_ACCEPTANCE.md` richtiggestellt;
RUN-01- und Gate-FAIL-Evidence bleiben unverändert erhalten.

## Umfang

Produktseitig **ausschließlich** `ui/logs/log_page.py`. Testseitig
`tests/test_obs050_ui.py` und — mechanisch bedingt, weil er den Quelltext von
`_tail` liest — `tests/test_obs050_contracts.py`. Query-Layer, Settings,
Apply-Kette, Manager, Worker, Tabellenmodell, Filterleiste, Detailansicht und
Fenster sind unverändert; `git diff --stat` zeigt für die versionierten
Bestandsdateien exakt denselben Stand wie am Ende von RUN-01.

## Teststand

170 → **179 OBS-050-Tests**, grün unter **pytest und unittest**;
OBS-010…050 625 grün; volle Suite **1137 passed** / 1 vorbestehender,
umgebungsbedingter Fehlschlag (`lefx.interfaces`), dessen Vorbestand **und**
Lage außerhalb des Diffs für diesen Lauf erneut nachgemessen sind.
`git diff --check` leer, HEAD unverändert `91a7b7f`.

## Unterlagen

- `30_AUSFUEHRUNG/runs/RUN-OBS-050-02_2026-08-18/` (`RUN_LOG.md`, `RESULT.md`,
  `RUN_REPORT.md`, `OUTPUT_INDEX.md`)
- `40_EVIDENCE/OBS-050/RUN-02_2026-08-18/` (`FIX_SUMMARY.md`,
  `TEST_RESULTS.md`, `UI_ACCEPTANCE.md`, `probe_obs050_ordering_fix.py`)

Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.
