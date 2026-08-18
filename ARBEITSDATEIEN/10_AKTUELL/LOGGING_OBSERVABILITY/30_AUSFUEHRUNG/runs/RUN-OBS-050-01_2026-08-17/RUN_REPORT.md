# RUN_REPORT – RUN-OBS-050-01_2026-08-17

## Run-ID

`RUN-OBS-050-01_2026-08-17`

## Work Package

**OBS-050 – Local Query, Minimal UI & Settings**
(`20_PLANUNG/LOGGING_GESAMTPLAN/workpackages/WP-OBS-050_LOCAL_QUERY_MINIMAL_UI_SETTINGS.md`)

## Ausgangszustand

- `HEAD` = `91a7b7f` („feat(observability): complete OBS-040 observation hooks"),
  Branch `feat/einheitliche-triggerarchitektur`, Arbeitsbaum sauber bis auf die
  bewusst unversionierten Prompt- und Pipeline-Dateien unter `30_AUSFUEHRUNG/`.
- OBS-040 dokumentiert mit `GATE PASS – OBS-050 MAY PROCEED`.
- Vorhanden: `query/base.py` (eingefrorene Verträge), `PRAGMA query_only`,
  `SQLiteLogStore.clear()`/`ObservabilityManager.clear_history()`,
  `LoggingObservabilityConfig` inklusive `_from_dict`-Sonderbehandlung.
- Offen und OBS-050-Scope: `query/local.py`, `query/service.py`, `ui/logs/**`,
  die Settings-Einträge nach `CONTRACTS §10.3`, `apply_config` nach `§10.4`.

## Durchgeführte Arbeiten

1. Query-Layer: `LocalLogProvider`, `LogQueryService`.
2. Runtime-Einstellungen: `apply_config` am Ingress, Listener-Weitergabe,
   Anwendung von Handler-Level/Retention/Anzahlgrenze/Datei-Sink in der
   Kompositionswurzel bzw. auf dem Workerthread.
3. Apply-Kette: eine Zeile in `core/controller.py::apply_runtime_config`.
4. Sechster Settings-Tab mit den neun Einträgen aus §10.3 und den beiden
   Schaltflächen.
5. Logansicht `ui/logs/**` (sechs Module) inklusive Live-Tail ohne Ringbuffer,
   Keyset-Pagination, Detail-/Raw-Ansicht, Kontextaktionen und Statuszeile.
6. Verdrahtung: Manager an `DesktopApplication` (N-4), Tray-Eintrag,
   Fensterlebensdauer im Abbau.
7. 170 neue Tests, fünf Evidence-Dokumente, ein Ende-zu-Ende-Diagnoseskript.

## Erzeugte und geänderte Dateien

Vollständige Liste mit Zeilenzahlen und Begründung je Datei:
`40_EVIDENCE/OBS-050/RUN-01_2026-08-17/DIFF_SUMMARY.md`.

Neu: 3 Produktmodule in `core/`, 7 Module in `ui/logs/`, 5 Testdateien und ein
Testhilfsmodul, 6 Evidence-Dateien, 4 Run-Dateien.
Geändert (alle additiv): `.gitignore`, `app.py`, `core/controller.py`,
`core/logging_setup.py`, `core/observability/{ingress,manager,worker}.py`,
`ui/{application,settings_dialog,tray}.py`.

## Entscheidungen

E-1 bis E-10, alle aus dem bestehenden Freeze auflösbar — Tabelle in
`RUN_LOG.md` Abschnitt 5. Kein normatives Dokument verändert.

## Offene Entscheidungen

**Keine.** Kein `DECISION REQUIRED`.

## Tests / Evidence

- 170 neue Tests, grün unter `pytest` **und** `unittest`.
- Volle Suite: 1128 passed / 1 vorbestehender, umgebungsbedingter Fehlschlag
  (`lefx.interfaces`), Vorbestand gegen einen frisch ausgepackten
  `91a7b7f`-Baum nachgewiesen (958 passed / 1 identischer Fehlschlag).
- `probe_obs050_end_to_end.py`: 12/12 PASS, exit 0.
- `git diff --check` leer, kein Cross-Workstream-Diff, kein bestehender Test
  geändert.

## Blocker

Keine. Drei während der Arbeit gefundene reale Defekte (F-1 `.gitignore`
verbarg `ui/logs/`, F-2 synchron beantwortete Abfrage wurde verworfen,
F-3 Zugriffsverletzung beim Abbau) sind behoben und dokumentiert.

## Gate-Empfehlung

`OBS-050 IMPLEMENTED – READY FOR REVIEW`. Das Gate gehört in eine frische
Session; ein Coding-Agent vergibt es nicht aufgrund eigener grüner Tests.

Für den Review besonders lohnend:

1. Der Live-Modus: benutzt er wirklich denselben Providerpfad wie die
   Historie, und gibt es irgendwo doch einen Puffer?
2. O-14: erzeugt oder verändert der Query-Layer unter *keinen* Umständen eine
   Datei, auch nicht bei fehlender oder beschädigter Datenbank?
3. §10.4: erreicht eine reine Observability-Änderung tatsächlich weder
   Reconnect noch Audio-Neustart — gemessen am echten `apply_runtime_config`?
4. Die Trennung der Ownership-Domänen: wendet der Worker die
   `IMMEDIATE`-Felder auf seinem eigenen Thread an, und bleiben
   `store_enabled`/`db_path` zur Laufzeit unangetastet?
5. F-1: ist die `.gitignore`-Negation die minimale Korrektur, und ist nach ihr
   wirklich jede neue Datei versionierbar?

## Nächster Schritt

OBS-050 Gate Review (unabhängig, frische Session,
`Prompts/OBS-050_GATE_REVIEW.md`).
