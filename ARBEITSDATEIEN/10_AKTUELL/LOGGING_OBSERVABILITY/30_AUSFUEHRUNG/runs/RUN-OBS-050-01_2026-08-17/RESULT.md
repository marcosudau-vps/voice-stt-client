# RESULT – RUN-OBS-050-01_2026-08-17

## Ergebnis

`OBS-050 IMPLEMENTED – READY FOR REVIEW`

**Kein Gate-PASS in diesem Run** — das Work Package verlangt einen separaten,
unabhängigen Review in einer frischen Session.

## Was entstanden ist

**Query-Layer.** `core/observability/query/local.py` und `.../service.py`
schließen die letzte Lücke der in ARCH §5.1 eingefrorenen Modulstruktur. Der
`LocalLogProvider` öffnet eigene, kurzlebige Verbindungen mit
`PRAGMA query_only = ON` (nie `mode=ro`), bindet jeden Filterwert als
Platzhalter, blättert per Keyset über `logs.id` und lädt `raw_json`
grundsätzlich nicht in die Liste. Drei Eigenschaften sind dabei tragend und
getestet: **er legt die Datenbankdatei nie an** (eine vom *Leser* erzeugte
Datei wäre ein Schreibvorgang des Query-Layers, O-14), **er wirft nie**
(jeder Fehler ist ein Anzeigezustand), und **er lässt keine Verbindung
offen**. `LogQueryService` ist die Registry, die spätere Provider aufnimmt,
ohne dass ein Aufrufer einen Parameter bekommt.

**Logansicht.** `ui/logs/` mit den sechs eingefrorenen Modulen. Live und
Historie sind **derselbe** Abfragepfad mit anderen Parametern: die Historie
fragt `newest_first=True` und blättert rückwärts über `next_cursor`, der
Live-Modus fragt alle 250 ms `newest_first=False` ab dem zuletzt gesehenen
Cursor, `LIMIT 500`. **Kein Ringbuffer, kein Signal je Record** — genau die
Bauform, die FD-S1 verlangt, mit dem dort benannten Nebennutzen: bei totem
Worker bleibt die Ansicht nutzbar und zeigt schlicht keine neuen Zeilen. Die
Abfrage läuft auf einem eigenen `ThreadPoolExecutor(max_workers=1)`, nicht
über `CoreBridge`, dessen Loop Audio und WebSocket trägt.

**Einstellungen.** Die neun Einträge aus CONTRACTS §10.3 im sechsten Tab
„Logging & Diagnose", mit ihren Apply-Policies, dazu „Diagnosehistorie
löschen" (am **Store**, über den Manager — nicht am Query-Provider, O-14) und
„Logs anzeigen". Die Ownership-Domänen sind sauber getrennt: der Ingress wendet
die vier Felder an, die er besitzt, die Kompositionswurzel den Handler-Level
(ARCH §8.7: ein Konfigwert, zwei Filter), der Worker Retention, Anzahlgrenze
und Datei-Sink — auf seinem eigenen Thread, dem die Verbindung und der Sink
gehören. `store_enabled` und `db_path` bleiben `APP_RESTART` und werden zur
Laufzeit ausdrücklich **nicht** angewandt.

**Apply-Kette.** Eine Zeile in `apply_runtime_config`, exakt an der von §10.4
genannten Stelle. Die harte Regel ist gemessen, nicht behauptet: eine reine
Observability-Änderung erreicht eine Fake-Session, deren `reconfigure`
durchfällt, **nicht** — es gibt also weder Reconnect noch Audio-Neustart.

## Nachweise, die zählen

Das Ende-zu-Ende-Diagnoseskript fährt den echten Manager mit echtem
Workerthread, echter SQLite-Datei, echtem Query-Layer und echtem Qt-Fenster:
**12 von 12 Prüfungen bestanden, exit 0.** Darunter: 750 Zeilen paginiert
**während der Worker weiterschreibt**, ohne eine Lücke und ohne ein Duplikat;
`raw` nicht in der Liste, aber über `fetch_raw` vorhanden; ein Levelwechsel,
der Handler und Ingress gleichzeitig bewegt; „Diagnosehistorie löschen", das
765 Zeilen entfernt, während der Query-Layer nachweislich keine
Schreibmethode besitzt; und drei Records, die geschrieben werden, **während
kein Fenster offen ist**, und die ein später geöffnetes Fenster zeigt.

Zusätzlich belegt ein Subprozess ohne einen einzigen `ui.`- oder
PySide6-Import, dass Logging vollständig ohne die Ansicht funktioniert.

## Teststand

170 neue Tests in fünf Dateien, grün unter **pytest und unittest**. Volle
Suite 1128 passed / 1 Fehlschlag, dessen Vorbestand gegen einen frisch aus
`91a7b7f` ausgepackten Baum nachgewiesen ist (dort 958 passed / 1 identischer
Fehlschlag, `lefx.interfaces` fehlt in dieser Umgebung) — **Differenz exakt
die 170 neuen Tests**. **Kein bestehender Test geändert.**
`git diff --check` leer, kein Cross-Workstream-Diff.

## Drei reale Befunde, alle behoben

**F-1:** `.gitignore` verbarg mit der Regel `logs/` das gesamte neue Paket
`ui/logs/` — der in ARCH §5.1 eingefrorene Pfad der Logansicht. Ohne Korrektur
wäre das Ergebnis dieses Work Packages nicht versionierbar gewesen und ein
späterer Checkpoint-Commit hätte lautlos eine unvollständige Fassung
enthalten. Behoben mit einer begründeten Negation `!ui/logs/`; die Regel für
Laufzeitdaten bleibt unverändert wirksam.

**F-2:** Eine Abfrage, die schneller antwortet als `request_page` zurückkehrt,
veröffentlicht ihr Ergebnis synchron im aufrufenden Thread — die Seite verwarf
dadurch ihre eigene frische Antwort als „veraltet". Behoben, indem die
Anfrage-ID vor dem Absetzen reserviert wird.

**F-3:** Ein sofort zurückkehrendes `shutdown()` ließ eine laufende Abfrage in
ein bereits zerstörtes `QObject` veröffentlichen — in PySide6 eine
Zugriffsverletzung. Behoben durch `shutdown(wait=True)`.

## Entscheidungen

Zehn Entscheidungen, **alle aus dem bestehenden Freeze auflösbar**:
**kein `DECISION REQUIRED`**, **kein neuer Zähler**, **kein neuer Recordtyp**
(§12 ist die verbindliche Liste — auch das Löschen der Historie erzeugt
bewusst keinen), **kein neues Konfigurationsfeld** und **kein normatives
Dokument verändert**.

Eine davon verdient eine eigene Zeile: die neun Settings-Einträge liegen in
`core/logging_settings_metadata.py` statt in `core/settings_metadata.py`, weil
CONTRACTS §12.7 letzteres ausdrücklich „bewusst rein" hält und ein bestehender
OBS-040-Test das prüft. ARCH §12 verlangt in diesem Fall anzuhalten und die
Architektur zu prüfen statt den Test zu ändern; das Ergebnis der Prüfung ist
diese Trennung. `core/settings_metadata.py` ist byte-identisch geblieben.

## Grenzen

- Offscreen-Tests prüfen Verhalten, nicht Aussehen. Die fünf verbleibenden
  manuellen Punkte stehen in `UI_ACCEPTANCE.md` Abschnitt 4.
- Dauerlast, Antwortzeiten und das Performance-Gate sind OBS-060.
- Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.

## Unterlagen

- `30_AUSFUEHRUNG/runs/RUN-OBS-050-01_2026-08-17/` (`RUN_LOG.md`,
  `RESULT.md`, `RUN_REPORT.md`, `OUTPUT_INDEX.md`)
- `40_EVIDENCE/OBS-050/RUN-01_2026-08-17/` (`TEST_RESULTS.md`,
  `DIFF_SUMMARY.md`, `CONTRACT_COVERAGE.md`, `QUERY_CASES.md`,
  `UI_ACCEPTANCE.md`, `probe_obs050_end_to_end.py`)
