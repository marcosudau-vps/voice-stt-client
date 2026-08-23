# OBS-050 – DIFF_SUMMARY

Run: `RUN-OBS-050-01_2026-08-17`, Ausgangscommit `91a7b7f`.
`git diff --check`: leer. Kein Commit, kein Push, kein Merge, kein Tag.

## 1. Neue Dateien

| Datei | Zeilen | Zweck |
|---|---:|---|
| `core/observability/query/local.py` | 483 | `LocalLogProvider` (ARCH §5.1) |
| `core/observability/query/service.py` | 138 | `LogQueryService`-Registry (ARCH §5.1/§10.3) |
| `core/logging_settings_metadata.py` | 129 | Metadaten des sechsten Tabs (CONTRACTS §10.3) |
| `ui/logs/__init__.py` | 54 | Paket mit verzögerten Re-Exports |
| `ui/logs/log_window.py` | 107 | `LogWindow` (nicht-modal, `hide()` statt `close()`) |
| `ui/logs/log_page.py` | 456 | `LogPage` (Modi, Live-Tail, Pagination, Statuszeile) |
| `ui/logs/log_table_model.py` | 155 | `LogTableModel`, sieben Spalten |
| `ui/logs/log_filter_bar.py` | 240 | `LogFilterBar`, entprellt, Activation-Hinweis |
| `ui/logs/log_detail_view.py` | 186 | `LogDetailView`, `details`-Baum, `raw`-JSON |
| `ui/logs/log_query_controller.py` | 177 | `LogQueryController` mit eigenem Executor |
| `tests/test_obs050_*.py` (5 Dateien) | 2128 | 170 neue Tests |
| `tests/obs050_apply_support.py` | 152 | Testfixtures ohne eigene Testfälle |

## 2. Geänderte Bestandsdateien

```text
 .gitignore                    |   4 ++++      (Befund F-1)
 app.py                        |  11 ++--
 core/controller.py            |  28 +++++++++
 core/logging_setup.py         |   7 +++
 core/observability/ingress.py |  73 +++++++++++++++++++++-
 core/observability/manager.py | 137 ++++++++++++++++++++++++++++++++++++++----
 core/observability/worker.py  |  59 ++++++++++++++++++
 ui/application.py             |  96 +++++++++++++++++++++++++++--
 ui/settings_dialog.py         |  74 +++++++++++++++++++++--
 ui/tray.py                    |  11 ++++
```

Alle Änderungen sind **additiv**: keine bestehende Funktion wurde in ihrem
bisherigen Verhalten verändert, keine bestehende Signatur gebrochen (jeder neue
Parameter hat einen Default), kein bestehender Test geändert.

### 2.1 `core/observability/ingress.py`

`apply_config(config)` (CONTRACTS §10.4) und `register_config_listener(...)`.
Der Ingress wendet **nur** an, was er besitzt: `enabled`, `level`,
`store_raw_payload`, `store_transcription_content`. Alles Übrige geht an
registrierte Listener — der Ingress erfährt nie, dass es einen Worker gibt
(Importrichtung ARCH §5.2). `NullIngress` überschreibt beides als No-Op.

### 2.2 `core/observability/manager.py`

`query_service` (lazy, mit `LocalLogProvider`), `db_path`, `health_snapshot()`,
`register_log_handler()`, `_build_sink()` und der Listener `_on_config_applied`.
Letzterer wendet die `IMMEDIATE`-Einstellungen an, die der Ingress nicht
besitzt: Handler-Level (ARCH §8.7), Retention, Anzahlgrenze, Datei-Sink.
`store_enabled`/`db_path` bleiben unangetastet — `APP_RESTART` nach §10.3.

### 2.3 `core/observability/worker.py`

`request_settings(**settings)` legt Einstellungen unter einem Lock ab;
`_apply_pending_settings()` wendet sie **auf dem Workerthread** an, als erste
Anweisung von `_iteration()`. Ein ersetzter Sink wird von dem Thread
geschlossen, dem er gehört (ARCH §6.4). Keine Änderung an Schreibpfad, Batch,
Retentionstakt oder Health-Zählern.

### 2.4 `core/controller.py`

Eine Zeile im Apply-Pfad, exakt an der von §10.4 genannten Stelle
(unmittelbar nach `_install_runtime_config`), plus die kleine, nicht werfende
Hilfsmethode `_apply_observability_config`. Der `getattr`-Schutz ist keine
Vorsicht, sondern die Umsetzung von §10.4 („ein Fehler dort darf das
Apply-Ergebnis nicht beeinflussen") für **jede** Ingress-Implementierung; er
ist derselbe Gedanke wie das eine `try/except` im `ClientEventEmitter`.
`BaseException` bleibt ungefangen (ARCH §7.3).

### 2.5 `core/logging_setup.py`

Drei Zeilen: der Handler wird der Kompositionswurzel bekannt gemacht, damit
eine Levelsänderung zur Laufzeit **beide** von ARCH §8.7 genannten Filter
bewegt. Ohne sie wäre `logging.observability.level` zur Hälfte wirkungslos.
`getattr`-geschützt, damit ein Double ohne die Methode weiterhin funktioniert.

### 2.6 `ui/application.py`

Neuer Parameter `observability_manager=None` an `DesktopApplication` und
`run_gui` (Readinesspunkt N-4), `show_logs()`, `clear_diagnostics_history()`,
die zwei neuen Dialogsignale und das Freigeben des Fensters im `shutdown()`.
`DesktopApplication` stoppt den Manager **nicht** (ARCH §6.2(b)) — dafür gibt
es einen eigenen Test.

### 2.7 `ui/settings_dialog.py`

Sechster Tab in `TAB_NAMES`, zwei Aktionsschaltflächen samt Statuszeile für
diesen Tab, zwei neue Signale, `editor="optional_path"` im vorhandenen
`_editor_value` und der Import der zusammengesetzten Definitionsliste. Die
generische Tab- und Editorlogik ist unverändert; der neue Tab kostet
tatsächlich nur Metadaten (CONTRACTS §13).

### 2.8 `ui/tray.py`

Ein optionaler Callback `on_show_logs` und ein Menüeintrag „Logs anzeigen …",
deaktiviert, wenn kein Manager vorliegt (CONTRACTS §9.1).

## 3. Befunde

### F-1 (behoben) — `ui/logs/` war durch `.gitignore` unsichtbar

`.gitignore` enthält seit jeher `logs/` für Laufzeitdaten. Dieses Muster
greift ohne Ankerung auf **jedes** Verzeichnis namens `logs`, also auch auf
`ui/logs/` — den in ARCH §5.1 eingefrorenen Pfad der Logansicht.
`git check-ignore -v ui/logs/log_page.py` wies vor der Korrektur auf
`.gitignore:23:logs/` hin: das gesamte neue UI-Paket wäre lautlos nicht
versionierbar gewesen, und ein späterer Checkpoint-Commit hätte eine
unvollständige Fassung enthalten, die niemandem aufgefallen wäre.

Korrektur: eine Negation `!ui/logs/` direkt unter der Regel, mit Begründung im
Kommentar. Das Muster `logs/` bleibt für alle Laufzeitverzeichnisse
unverändert wirksam. Nachgemessen: `git check-ignore` findet die Datei nicht
mehr, `git status --short` listet `?? ui/logs/`.

Diese Änderung ist keine fachfremde Produktänderung, sondern die Bedingung
dafür, dass das Ergebnis dieses Work Packages überhaupt versioniert werden
kann.

### F-2 (behoben) — schnelle Antwort wurde als veraltet verworfen

`concurrent.futures` führt einen `add_done_callback` **sofort im aufrufenden
Thread** aus, wenn das Future bereits fertig ist. Eine Abfrage, die schneller
antwortet als `request_page` zurückkehrt, veröffentlichte ihr Ergebnis also
noch während `LogPage` die Anfrage stellte — und `LogPage` verwarf die eigene,
frische Antwort als „veraltet", weil `_active_request` noch den alten Wert
trug. Sichtbar wurde das als dauerhaft leere Tabelle bei einer sehr kleinen
Datenbank.

Korrektur: die Anfrage-ID wird **vor** dem Absetzen reserviert
(`LogQueryController.next_request_id()` + `request_id=`-Parameter). Die
Verwerfung veralteter Antworten bleibt vollständig erhalten und wird
weiterhin getestet.

### F-3 (behoben) — Zugriffsverletzung beim Testabbau

`LogQueryController.shutdown()` kehrte ursprünglich sofort zurück
(`wait=False`). Eine noch laufende Abfrage veröffentlichte ihr Ergebnis danach
über ein `QObject`, dessen C++-Seite bereits zerstört war — in PySide6 eine
Zugriffsverletzung, keine Ausnahme. Der Testlauf stürzte reproduzierbar ab.

Korrektur: `shutdown(wait=True)` als Standard. Gewartet wird auf genau eine
kurzlebige SQLite-Leseabfrage, und nur beim Abbau — kein produzierender Pfad
ist betroffen, O-03 bleibt unberührt. Zusätzlich räumt
`tests/test_obs050_ui.py` in `tearDown` deterministisch auf.

## 4. Was ausdrücklich **nicht** geändert wurde

- `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV/` — byte-identisch
  zu `91a7b7f` (mit `git status` geprüft: keine Datei dort ist geändert).
- `core/settings_metadata.py` — byte-identisch. §12.7 führt das Modul unter
  „bewusst rein, nicht ändern"; deshalb liegen die neun neuen Einträge in
  `core/logging_settings_metadata.py` (Begründung dort im Modulkopf).
- `core/config.py`, `core/observability/models.py`, `redaction.py`,
  `normalizer.py`, `health.py`, `storage/sqlite.py`, `sinks/jsonl_file.py`,
  `query/base.py`, `adapters/**` — unverändert.
- Kein bestehender Test.
- Kein Cross-Workstream-Diff: der Diff berührt ausschließlich
  `voice-stt-client/workspaces/einheitliche-triggerarchitektur`.
- Kein neuer Zähler in `LoggingHealthSnapshot`, kein neuer Recordtyp
  (§12 ist die verbindliche Liste), keine neue Konfigurationsoption
  (§10.1 ist eingefroren).
