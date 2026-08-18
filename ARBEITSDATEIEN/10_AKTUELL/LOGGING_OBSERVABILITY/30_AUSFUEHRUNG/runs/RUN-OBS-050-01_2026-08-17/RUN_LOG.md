# RUN_LOG – RUN-OBS-050-01_2026-08-17

Work Package: **OBS-050 – Local Query, Minimal UI & Settings**
Prompt: `30_AUSFUEHRUNG/Prompts/OBS-050_IMPLEMENTIERUNGSAUFTRAG.md`
Ausgangscommit: `91a7b7f`
Branch: `feat/einheitliche-triggerarchitektur`

## 1. Voraussetzung geprüft

`CURRENT_STATE.md` und `LOGGING_V1_CHECKLISTE.md` weisen
**OBS-040 GATE PASS – OBS-050 MAY PROCEED** aus (unabhängiger Review,
`40_EVIDENCE/OBS-040/GATE-REVIEW-01_2026-08-17_CLAUDE/GATE_REVIEW.md`), und der
Haken „OBS-040 – Gate Review" ist gesetzt. Die Voraussetzung des Auftrags ist
damit dokumentiert erfüllt. `git log` bestätigt den zugehörigen Checkpoint-
Commit `91a7b7f` als `HEAD`.

## 2. Pflichtlektüre

Gelesen vor Beginn: `ARBEITSDATEIEN/README.md`, `AGENTS.md`,
`00_STEUERUNG/CURRENT_STATE.md`, `MASTERPLAN.md`, `ARBEITSPROZESS.md`, die
Themen-`AGENTS.md`, das Work Package
`WP-OBS-050_LOCAL_QUERY_MINIMAL_UI_SETTINGS.md`, die drei normativen Dokumente
in `00_NORMATIV/` **vollständig** sowie die Fortschrittscheckliste.

Danach der reale Code: `query/base.py`, `storage/sqlite.py`, `worker.py`,
`manager.py`, `ingress.py`, `health.py`, `models.py`, `logging_setup.py`,
`config.py` (Abschnitt `LoggingObservabilityConfig`), `settings_metadata.py`,
`ui/settings_dialog.py`, `ui/application.py`, `ui/tray.py`, `app.py`,
`core/controller.py::apply_runtime_config` und die bestehenden Testkonventionen.

## 3. Arbeitsschritte

1. **Query-Layer.** `core/observability/query/local.py` (`LocalLogProvider`)
   und `core/observability/query/service.py` (`LogQueryService`) nach
   CONTRACTS §5.4/§5.7/§8. Keyset-Pagination mit einer Sonde-Zeile mehr als
   angefragt, damit „gibt es eine Folgeseite" ohne `COUNT` beantwortbar ist.
2. **Runtime-Einstellungen.** `ObservabilityIngress.apply_config` (die vier
   Felder, die der Ingress besitzt) plus Listener-Weitergabe;
   `ObservabilityManager._on_config_applied` für Handler-Level, Retention,
   Anzahlgrenze und Datei-Sink; `LoggingWorker.request_settings` als
   Ablagepunkt, der auf dem Workerthread angewandt wird.
3. **Apply-Kette.** Eine Zeile in `core/controller.py::apply_runtime_config`
   an der von CONTRACTS §10.4 genannten Stelle, nicht werfend.
4. **Settings-Tab.** `core/logging_settings_metadata.py` mit den neun
   Einträgen aus §10.3; sechster Tab und die beiden Schaltflächen im
   bestehenden `SettingsDialog`.
5. **Logansicht.** `ui/logs/` mit den sechs in ARCH §5.1 eingefrorenen
   Modulen.
6. **Verdrahtung.** Manager an `DesktopApplication` (Readinesspunkt N-4),
   Tray-Eintrag, Fensterlebensdauer im `shutdown()`.
7. **Tests.** 170 neue Tests in fünf Dateien plus ein Hilfsmodul ohne
   Testfälle.
8. **Evidence.** Fünf Dokumente und ein Ende-zu-Ende-Diagnoseskript.

## 4. Reale Befunde während der Arbeit

### F-1 `ui/logs/` war durch `.gitignore` unsichtbar

`git status` zeigte das neue UI-Paket überhaupt nicht an.
`git check-ignore -v ui/logs/log_page.py` nannte `.gitignore:23:logs/`: die
Regel für Laufzeitverzeichnisse greift ungeankert auf **jedes** Verzeichnis
namens `logs`, also auch auf den in ARCH §5.1 eingefrorenen Pfad der
Logansicht. Ohne Korrektur wäre das gesamte Paket unversionierbar gewesen und
ein späterer Checkpoint-Commit hätte lautlos eine unvollständige Fassung
enthalten.

Behoben mit einer Negation `!ui/logs/` unmittelbar unter der Regel, samt
Begründung im Kommentar. `logs/` bleibt für Laufzeitdaten unverändert
wirksam. Nachgemessen: `git check-ignore` findet die Datei nicht mehr.

### F-2 Schnelle Antwort wurde als veraltet verworfen

Erste Fassung: `LogPage` speicherte die Anfrage-ID aus dem Rückgabewert von
`request_page`. `concurrent.futures` führt einen `add_done_callback` aber
**sofort im aufrufenden Thread** aus, wenn das Future schon fertig ist — bei
einer kleinen Datenbank antwortet die Abfrage also, bevor `request_page`
zurückkehrt, und die Seite verwarf ihre eigene frische Antwort. Sichtbar als
dauerhaft leere Tabelle.

Behoben: Die ID wird vor dem Absetzen reserviert
(`next_request_id()` + `request_id=`). Die Verwerfung wirklich veralteter
Antworten bleibt erhalten und ist getestet.

### F-3 Zugriffsverletzung beim Abbau

`LogQueryController.shutdown()` kehrte zunächst sofort zurück. Eine noch
laufende Abfrage veröffentlichte danach über ein `QObject`, dessen C++-Seite
bereits zerstört war — in PySide6 eine Zugriffsverletzung, kein Fehler.
Der Testlauf stürzte reproduzierbar ab.

Behoben: `shutdown(wait=True)` als Standard (gewartet wird auf genau eine
kurzlebige Leseabfrage, nur beim Abbau), plus deterministisches Aufräumen im
`tearDown` der UI-Tests.

### F-4 `settings_metadata.py` ist normativ „bewusst rein"

Die naheliegende Umsetzung — die neun Einträge direkt in
`core/settings_metadata.py` — brach einen bestehenden OBS-040-Contract-Test,
der die von CONTRACTS §12.7 geforderte Reinheit dieses Moduls als Textprüfung
festhält. ARCH §12 verlangt in genau diesem Fall anzuhalten und die
Architektur zu prüfen, statt den Test zu ändern.

Ergebnis der Prüfung: §12.7 meint Instrumentierung (Logaufrufe, Importe der
Observability), §13 erwartet den neuen Tab ausdrücklich „nur als Metadaten".
Beides ist erfüllbar, wenn die Einträge in einem eigenen Modul
`core/logging_settings_metadata.py` liegen und der Dialog beide Listen
zusammensetzt. `core/settings_metadata.py` ist byte-identisch geblieben, kein
bestehender Test wurde geändert. Das in ARCH §5.1 ausgeschlossene Modul
`ui/settings/logging_settings.py` entsteht dabei **nicht** — der Dialog baut
den Tab über denselben generischen Pfad wie jeden anderen.

## 5. Entscheidungen aus dem bestehenden Freeze

| # | Frage | Entscheidung | Grundlage |
|---|---|---|---|
| E-1 | Wo wenden Einstellungen an, die der Ingress nicht besitzt? | Listener am Ingress; die Kompositionswurzel wendet sie an | ARCH §5.2 (Importrichtung), CONTRACTS §10.4 |
| E-2 | Wie erreicht ein Levelwechsel den Python-Handler? | `setup_logging` meldet den Handler der Wurzel; sie setzt ihn beim Apply | ARCH §8.7 (ein Wert, zwei Filter), §10.3 (IMMEDIATE) |
| E-3 | Wer wendet Retention/Sink an? | der Worker selbst, aus einer abgelegten Einstellung | CONTRACTS §5.4 (Verbindungsbesitz), ARCH §6.4 (kein Thread je Sink) |
| E-4 | Was passiert bei `enabled: false` zur Laufzeit? | `DISABLED` in Health; Rückkehr räumt nur `DISABLED` weg | ARCH §8.3 (Zustandsmenge), keine Überschreibung eines Fehlers |
| E-5 | Cursorform | `"id:<n>"`, opak, mit Ablehnung fremder Cursor | CONTRACTS §8.1 |
| E-6 | „Gibt es eine Folgeseite?" | eine Zeile mehr abfragen | CONTRACTS §8.1 („kein `count()`") |
| E-7 | Fehlende Datei | `UNAVAILABLE`, Datei wird nicht angelegt | ARCH §1.2 (O-14) |
| E-8 | Record für „Historie gelöscht"? | **nein** | CONTRACTS §12 ist die verbindliche Liste |
| E-9 | Zeilenobergrenze im Tabellenmodell | ja, ältestes zuerst verwerfen | ARCH §1.1 (O-04) |
| E-10 | Blockiert „Diagnosehistorie löschen" den Qt-Thread? | ja, begrenzt durch den Worker-Timeout — bewusste, benutzerausgelöste Einzelaktion | CONTRACTS §5.8, DEC FD-S4 („etwa zehn Zeilen plus eine Schaltfläche") |

**Kein `DECISION REQUIRED`.** Alle zehn Punkte sind aus dem bestehenden Freeze
auflösbar. Kein normatives Dokument wurde verändert.

## 6. Prüfungen

```text
git diff --check                     leer
git status --short                   siehe DIFF_SUMMARY.md
git diff --stat                      10 Dateien geändert, alle additiv
pytest -k obs050                     170 passed
unittest discover -p test_obs050_*   170 tests OK
pytest tests                         1128 passed / 1 vorbestehender Fehlschlag
unittest discover -p test_*.py       1129 tests, 1 vorbestehender Fehler
Baseline 91a7b7f (frisch ausgepackt) 958 passed / 1 identischer Fehlschlag
probe_obs050_end_to_end.py           12/12 PASS, exit 0
```

## 7. Grenzen dieses Runs

- Kein Gate-PASS: das Work Package verlangt einen separaten Review in einer
  frischen Session.
- Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.
- Die offscreen-Tests prüfen Verhalten, nicht Aussehen; die verbleibenden
  manuellen Punkte stehen in `UI_ACCEPTANCE.md` Abschnitt 4.
