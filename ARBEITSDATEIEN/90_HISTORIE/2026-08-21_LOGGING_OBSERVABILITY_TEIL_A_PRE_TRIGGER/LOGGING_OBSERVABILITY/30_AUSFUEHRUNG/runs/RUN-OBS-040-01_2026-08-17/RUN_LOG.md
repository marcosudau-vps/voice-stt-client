# RUN_LOG – RUN-OBS-040-01_2026-08-17

Work Package: **OBS-040 – Server Live Adapter & Client Observation Hooks**
Prompt: `30_AUSFUEHRUNG/Prompts/OBS-040_IMPLEMENTIERUNGSAUFTRAG.md`
Session-Root: `P:\GithubRepos\marcosudau-vps`
Datum: 2026-08-17

## 0. Ablageort dieses Ordners

Der Auftrag nennt `30_AUSFUEHRUNG\Runs\`. Der **versionierte** Pfad im
Repository lautet `30_AUSFUEHRUNG/runs/` (klein), dort liegen die Runs von
OBS-000, OBS-020 und OBS-030. Auf einem case-insensitiven Dateisystem ist das
dasselbe Verzeichnis; dieser Run benutzt bewusst den bestehenden
kleingeschriebenen Pfad, damit im Repository keine zweite
Verzeichnisschreibweise entsteht — dieselbe Begründung wie beim Gate-Befund N-5
des OBS-030-Reviews.

## 1. Pflichtlektüre (vor der ersten Codeänderung)

Vollständig gelesen, in dieser Reihenfolge:

1. `Prompts/OBS-040_IMPLEMENTIERUNGSAUFTRAG.md`
2. `ARBEITSDATEIEN/README.md`
3. `ARBEITSDATEIEN/AGENTS.md`
4. `00_STEUERUNG/CURRENT_STATE.md`
5. `00_STEUERUNG/MASTERPLAN.md`
6. `00_STEUERUNG/ARBEITSPROZESS.md`
7. `10_AKTUELL/LOGGING_OBSERVABILITY/AGENTS.md`
8. `20_PLANUNG/.../workpackages/WP-OBS-040_SERVER_LIVE_ADAPTER_CLIENT_OBSERVATION_HOOKS.md`
9. `00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md` (vollständig, 1510 Zeilen)
10. `00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md` (vollständig, 996 Zeilen)
11. `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` (vollständig, 858 Zeilen)
12. `40_EVIDENCE/OBS-030/GATE-REVIEW-02_2026-08-17_CLAUDE/GATE_REVIEW.md`,
    Abschnitte H (N-1 bis N-5) und I (Readiness OBS-040)
13. `voice-stt-client`-`AGENTS.md` des Workspaces
14. betroffener Produktcode und die zugehörigen bestehenden Tests

## 2. Voraussetzungsprüfung

Der Auftrag verlangt: *„OBS-030 muss dokumentiert mit `PASS` abgeschlossen
sein."*

Geprüft in `00_STEUERUNG/CURRENT_STATE.md`:

```text
OBS-030: GATE PASS – OBS-040 MAY PROCEED (2026-08-17, zweiter unabhängiger
Review in frischer Session,
40_EVIDENCE/OBS-030/GATE-REVIEW-02_2026-08-17_CLAUDE/GATE_REVIEW.md)
```

und in `30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md`:

```text
- [x] OBS-030 – Queue, Worker, SQLite & Retention – Implementierung
- [x] OBS-030 – Gate Review
...
**OBS-040 MAY PROCEED.**
```

Ergebnis: **Voraussetzung erfüllt.** Der Readiness-Check des Gates nennt keine
Blocker und benennt den Fan-out-Hook in `core/session_coordinator.py`
ausdrücklich als „noch nicht vorhanden — genau der Gegenstand von OBS-040".

## 3. Baseline

```text
$ python -m pytest tests -q
1 failed, 843 passed, 351 subtests passed in 51.47s
```

Der Fehlschlag (`test_ap06_followup.py`, `ModuleNotFoundError: No module named
'lefx.interfaces'`) ist vorbestehend und umgebungsbedingt. Er wird in diesem
Run **nicht** behoben, weil er außerhalb des Work Packages liegt (Regel „Fund →
dokumentieren, nicht automatisch reparieren" aus der Themen-`AGENTS.md`).

`git status --short` vor Beginn: sauber, bis auf die bereits vorher
unversionierten Prompt-Dateien unter `30_AUSFUEHRUNG/`.

## 4. Umsetzungsskizze und Reihenfolge

Umgesetzt in der von `CONTRACTS §12.6` vorgeschriebenen Reihenfolge nach
aufsteigendem Risiko, mit einem Testlauf nach jeder Stufe:

| Stufe | Inhalt | Test danach |
|---|---|---|
| 0a | `adapters/server_live.py`, `adapters/client_events.py`, `ingress.emit_record_rejected`, Aggregatquellen-Registry, Worker-Aggregat, zwei Re-Exports | Smoke-Test des Ingress |
| 0b | Fan-out-Hook in `session_coordinator.py`, `client.eventstream.state_changed`, zweiter Beobachtungspunkt in `event_stream.py` | `test_session_coordinator.py` + `test_event_stream.py` grün (25 Tests) |
| 1 | `ui/hotkeys.py`, `ui/core_bridge.py`, `ui/application.py`, `ui/led_feedback.py`, `ui/settings_dialog.py` | `test_core_bridge.py`, `test_hotkeys.py`, `test_ui_application.py`, `test_ui_widgets.py`, `test_led_feedback.py`, `test_feedback_ui.py` grün (97 Tests) |
| 2 | `core/audio_capture.py` (Start/Stop + Zählerattribute) | `test_audio_capture.py` grün |
| 3 | `core/stt_session.py` | `test_stt_session.py`, `test_trigger_lifecycle.py` grün (55 Tests) |
| 4 | `core/controller.py`, `core/text_injector.py` | volle Suite |
| 5 | `app.py` (Verdrahtung) | volle Suite |

## 5. Während der Ausführung aufgetretene reale Befunde

### B-1 Der bestehende Hot-Path-Test hat einen Kommentar abgelehnt

`tests/test_obs020_redaction_end_to_end.py::test_hot_path_audio_functions_never_reference_the_ingress`
liest den **Quelltext** von `AudioCapture._audio_callback` und verlangt, dass
das Wort `ingress` darin nicht vorkommt. Mein erster Kommentar lautete
„… no ingress attribute access" und hat den Test brechen lassen.

Konsequenz: Kommentar umformuliert („no attribute access on the observation
boundary"), mit einem Hinweis, **warum** er die verbotenen Wörter vermeidet.
Der Test hat damit genau das getan, wofür er gebaut ist — festgehalten, weil es
der einzige Fall im Run war, in dem ein bestehender Test eine Änderung erzwungen
hat, und weil die Lösung ausdrücklich **nicht** war, den Test anzupassen.

### B-2 `run_headless` durfte kein zweites Argument bekommen

`tests/test_obs030_app_wiring.py` ersetzt `app.run_headless` durch ein Double
mit der Signatur `(config)`. Ein zusätzliches Argument oder Keyword hätte diesen
bestehenden Test gebrochen.

Lösung: `app._call_with_optional_observability` **inspiziert die Signatur** und
übergibt das Keyword nur, wenn es existiert. Bewusst **nicht** über
`try/except TypeError` — ein `TypeError` aus dem Inneren des Aufrufs hätte einen
kompletten Clientlauf ein zweites Mal gestartet. Dasselbe Muster, mit derselben
Begründung, in `ui/application.py::_request_runtime_apply` für die
Bridge-Doubles aus `test_ap06_followup.py`.

### B-3 Die Transport-Factory des Coordinators ist von einem Test fixiert

`tests/test_session_coordinator.py::FakeEventTransport.__init__` hat genau sechs
Parameter. Der zweite Beobachtungspunkt braucht aber einen Ingress im echten
Transport, und der Transport wird ausschließlich über
`self._transport_factory(...)` gebaut.

Lösung: die **Default-Factory** aus `CONTRACTS §6` — dort für `CoreBridge` mit
exakt demselben Argument („ein bestehender Test übergibt eine eigene Factory")
vorgeschrieben. Eine von außen übergebene Factory wird weiterhin sechsstellig
aufgerufen; die Standard-Factory schließt über den Ingress. Details und Diff in
`40_EVIDENCE/OBS-040/RUN-01_2026-08-17/DIFF_SUMMARY.md`, Abschnitt 4.

### B-4 `logging.record_rejected` ist nur defensiv erreichbar

Gate-Befund N-1 verlangt den Ersatzrecord. Bei der Umsetzung zeigte sich: der
Normalizer **wirft konstruktiv nie** (`CONTRACTS §3`), also ist der
`except`-Zweig im Ingress im Normalbetrieb unerreichbar. Ein erster Testentwurf
ging von einer erreichbaren Ausnahme aus und war schlicht falsch.

Konsequenz: Der Record wird an **allen vier** Stellen erzeugt, die eine
Ausnahme sehen können (`ingress.observe_server_result`, `ingress.event`,
`ServerLiveAdapter.observe`, `UnifiedLogHandler._handle_exception`), und die
Tests sagen jetzt die Wahrheit: ein kaputtes Result-Objekt erzeugt **keinen**
Record (weil der Normalizer `None` liefert), ein Normalizer, der seinen
Vertrag bricht, erzeugt genau einen. Dokumentiert in
`OBSERVATION_HOOK_MATRIX.md`, Anmerkung A-5.

### B-5 `envelope.extra["meldung"]` liegt auf der Envelope-Oberfläche

Beim Schreiben der Serverabbildungstests: `EventEnvelope.from_mapping` sammelt
in `extra` alle **unbekannten Top-Level-Schlüssel** des Envelopes. Ein
Prüfframe mit `"extra": {"meldung": ...}` landet deshalb als
`extra["extra"]["meldung"]` und `message` bleibt `None`. Korrekt ist
`"meldung"` auf Envelope-Ebene — genau wie `CONTRACTS §3.2` es beschreibt
(*„der Client kennt ihn nicht und schiebt ihn nach `EventEnvelope.extra`"*).
Kein Codefehler, ein Testfehler; festgehalten, weil die Stelle laut §3.2
ausdrücklich behandelt werden muss und leicht falsch verstanden wird.

## 6. Entscheidungen dieses Runs (alle aus dem bestehenden Freeze auflösbar)

Keine dieser Entscheidungen erweitert einen eingefrorenen Vertrag; keine
erforderte ein `DECISION REQUIRED`. Vollständige Begründungen in
`OBSERVATION_HOOK_MATRIX.md` (A-1 bis A-6) und `CONTRACT_COVERAGE.md`.

| # | Entscheidung | Aus welchem Freeze abgeleitet |
|---|---|---|
| E-1 | `client.websocket.*` liegt auf `_fire_transport_change` (connecting/connected) und `_record_failure` (disconnected) | `§12.1` nennt beide Orte; `_update_transport` delegiert an `_fire_transport_change`, und der Reducerpfad benutzt nur letzteres |
| E-2 | `client.config.validation_failed` entsteht nicht in `core/config.py` | `ARCH §6.2(a)` benennt den Verlust von `AppConfig.load`-Meldungen ausdrücklich; `CONTRACTS §6` verbietet ein Modul-Singleton |
| E-3 | Recordname `client.settings.apply_completed` statt `client.settings.completed` | `§12.2` schreibt „`apply_started` / `.completed`"; `type` ist nach `§2.1` ein offener Namensraum |
| E-4 | `client.queue.state` ereignisgetrieben + ratenbegrenzt statt timergetrieben | `ARCH §6.4` („kein Anfassen der … Injection-Queues"), `§11.4`; ein Timeout auf `queue.get()` wäre eine Kontrollflussänderung eines fachlichen Pfades |
| E-5 | `client.server.error_classified` an genau einer Stelle mit `(where, count, dictation_state)` | `§12.5` verlangt einen Record; acht Aufrufstellen wären dieselbe Aussage achtfach |
| E-6 | Das Audio-Aggregat setzt `is_internal=False` | `§1.5`/`§1.4` reservieren das Flag für „logging-eigene Records" |
| E-7 | Das DEBUG-Aggregat respektiert den Ingress-Level | `ARCH §8.7`: „Ingress-Level gilt für strukturierte Clientevents" |
| E-8 | Read-only-Zählerquellen-Registry am Ingress statt eines Imports `worker → core.audio_capture` | `ARCH §8.6` verlangt, dass der **Worker** die Zähler liest; `§5.2` verbietet die Importrichtung — die Registry ist der einzige Weg, der beide Regeln hält |
| E-9 | `apply_runtime_config(candidate, *, correlation_id=None)` | `§12.2` verlangt „dieselbe correlation_id"; der Parameter ist rein beobachtend, beeinflusst nichts (O-01) und hat einen Default, bricht also keinen Aufrufer |

## 7. Was ausdrücklich nicht getan wurde

- **Kein** normatives Dokument geändert. `00_NORMATIV/` erscheint nicht in
  `git status --short`.
- **Kein** bestehender Test geändert.
- **Kein** neuer Zähler in `LoggingHealthSnapshot` (die Lektion des
  OBS-030-Cleanups zum entfernten `dropped_failed`); ein Contract-Test fixiert
  die Snapshotform jetzt.
- **Kein** neues Konfigfeld.
- **Kein** Commit, Push, Merge, Rebase, Tag, PR, kein `git reset`, kein
  `git clean`.
- **Keine** OBS-050/OBS-060-Funktionalität vorgezogen (kein `apply_config`, kein
  LogWindow, kein Query-Layer, keine Manager-Übergabe an
  `DesktopApplication`).
- **Keine** Änderung im Server- oder LED-Workspace; beide nur lesend als
  Referenz.
- Der vorbestehende `lefx.interfaces`-Fehlschlag ist **nicht** repariert.

## 8. Abschlussprüfung

```text
$ python -m pytest tests -q
1 failed, 958 passed, 531 subtests passed in 53.82s

$ python -m unittest discover -s tests -p "test_*.py"
Ran 959 tests in 49.060s      FAILED (errors=1)

$ python -m pytest tests -q -k obs040
115 passed, 844 deselected, 178 subtests passed

$ python -m unittest discover -s tests -p "test_obs040_*.py"
Ran 115 tests      OK

$ python -m pytest tests -q -k "obs010 or obs020 or obs030 or obs040"
446 passed, 513 deselected, 292 subtests passed

$ python ARBEITSDATEIEN/.../probe_obs040_end_to_end.py
P-1 … P-7 alle PASS, exit 0

$ git diff --check
(leer)

$ git diff --stat
16 files changed, 1324 insertions(+), 57 deletions(-)

$ git status --short
16 M (Produkt), 2 ?? (Produktmodule), 6 ?? (Tests), 1 ?? (Evidence),
plus die vorher schon unversionierten Prompt-Dateien
```

Scope-Prüfung gegen das Work Package: alle sieben Scope-Punkte umgesetzt, der
Nachweis N-07 erbracht, kein Non-Scope-Punkt berührt. Details in
`CONTRACT_COVERAGE.md`.

## 9. Blocker

Keine.

## 10. Nächster Schritt

**OBS-040 Gate Review** in frischer Session
(`30_AUSFUEHRUNG/Prompts/OBS-040_GATE_REVIEW.md`). Ein Coding-Agent darf das
Gate nicht allein aufgrund eigener grüner Tests vergeben
(`WP-OBS-040`, Abschnitt „Gate"; `ARBEITSPROZESS.md`).
