# BS-001 – Branch Separation Report

Logging/Observability-Teil-A aus `feat/einheitliche-triggerarchitektur` als eigenständigen,
main-basierten Branch `feat/logging-observability-pre-trigger` hergestellt.

## Baselines

| | |
|---|---|
| `origin/main` SHA | `178d32bdf17d4709307e7a2a944888d2cf294e42` (`178d32b – fix(feedback): debug LED and sound feedback`) |
| Quellbranch (`origin/feat/einheitliche-triggerarchitektur`) SHA | `dd0af5ed22e7401895f08c8c13e4e37c7e78ddb7` (`dd0af5e – chore(observability): archive pre-trigger logging workstream`) |
| Neuer Branch | `feat/logging-observability-pre-trigger` |
| Neuer Worktree-Pfad | `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\logging-observability-pre-trigger` |
| Neuer Branch-HEAD nach Abschluss | `fe60348 – chore(observability): adapt logging baseline to main` |

`origin/main` war zum Zeitpunkt des Runs unverändert bei `178d32b`, wie im Auftrag erwartet.
Kein zusätzlicher Analyse- oder Freigaberun war deshalb nötig.

Der neue Worktree wurde als `git worktree add -b feat/logging-observability-pre-trigger <pfad> origin/main`
direkt aus dem bestehenden Trigger-Repository heraus erzeugt (verlinktes Git-Worktree desselben
Objekt-Stores). Anzumerken: `main\` und `workspaces\einheitliche-triggerarchitektur\` sind selbst
zwei unabhängige Git-Clones (kein gemeinsamer Objekt-Store, kein `git worktree link`) – das ist
vorbestehende, nicht durch diesen Run veränderte Repository-Struktur. Der neue Logging-Worktree
ist technisch ein Git-Worktree des Trigger-Repos, referenziert aber denselben `origin`-Remote und
denselben `origin/main`-Stand wie `main\`.

## Commit-Übertragung

Commits zwischen `origin/main` und `origin/feat/einheitliche-triggerarchitektur` (chronologisch):

| Quellcommit | Kurzbeschreibung | Klassifikation | Übernommen | Resultierender Commit | Begründung |
|---|---|---|---|---|---|
| `5f2ee4b` | "umbau trigger-architektur claude 1 (debugging erforderlich)" | **Trigger** | Nein | – | Früher, unfertiger Trigger-Architektur-Commit (dual-mode Trigger-Config, `send_trigger`/`request_trigger`, Server-Aktivierungs-Ownership). Explizit ausgeschlossen laut Auftrag. |
| `f3908cf` | OBS-010 Projektbaseline / Arbeitsakte | Logging | Ja | `0de242c` | Reine Doku-/Arbeitsakte-Baseline, keine Codeänderung, konfliktfrei. |
| `b363346` | OBS-010/OBS-020 Foundation (Canonical Model, Ingress, Redaction, Health) | Logging | Ja | `1c02903` | Neue Dateien unter `core/observability/`, keine Berührung mit Trigger-Dateien. |
| `cb0b81f` | OBS-030 Persistence & Worker (SQLite, JSONL-Sink, Worker) | Logging | Ja | `7c5adb3` | Berührt `core/config.py` (gemeinsam mit `5f2ee4b`), Auto-Merge ohne Konflikt. |
| `91a7b7f` | OBS-040 Observation Hooks | **Gemischt** | Teilweise | `29c450f` (+ Fix in `fe60348`) | Siehe Abschnitt „Separation" unten – Logging-Hooks übernommen, eingebettete Trigger-Command-Implementierung und Trigger-spezifische Feld-/Methodenreferenzen entfernt bzw. angepasst. |
| `7fc6ca6` | OBS-050 Local Log View (Query-Layer, Logging-UI) | Logging | Ja | `19ba8e8` | Berührt `core/controller.py`, `ui/application.py`, `ui/settings_dialog.py` (gemeinsam mit `5f2ee4b`), Auto-Merge ohne Konflikt. |
| `8eea774` | OBS-060 V1 Hardening & Evidence | Logging | Ja | `dc68528` | Keine Dateiüberschneidung mit `5f2ee4b`. |
| `d9369c5` | Logging-Diagnose-UI Polish | Logging | Ja | `b07a813` | Keine Dateiüberschneidung. |
| `9f136c3` | Logging-Phase vor Trigger-Migration schließen | Logging | Ja | `99c6d30` | Reine Steuerungsdokumente (`CURRENT_STATE.md`, `LOG_VERLAUF.md`, Checkliste). |
| `dd0af5e` | Logging-Arbeitsakte archivieren | Logging | Ja | `a350cd9` | Reine Umbenennung/Archivierung nach `90_HISTORIE`, keine Codeänderung. |

Zusätzlich: `fe60348 – chore(observability): adapt logging baseline to main` (eigener
Separation-Fix-Commit, siehe unten).

## Separation

### Bewusst ausgeschlossene Triggeränderungen

- `5f2ee4b` vollständig ausgeschlossen: dual-mode Trigger-Konfiguration
  (`manual_trigger_enabled`/`wake_word_trigger_enabled`, `effective_manual_trigger_enabled`,
  `effective_wake_word_trigger_enabled`, `presentation_mode` in `core/config.py`), die komplette
  Trigger-Command-Implementierung in `core/stt_session.py` (`send_trigger`, `request_trigger`,
  `_resolve_trigger_ack`, `_fail_pending_trigger`, `_discard_pending_triggers`,
  `pending_trigger_ids`, `TriggerAck`/`_PendingTrigger`), die Server-Aktivierungs-Ownership-Logik
  in `core/controller.py` (`_server_owns_activation`, `_client_owns_dictation_window`,
  `_begin_stream_and_trigger`, `_manual_accept_correlation`, `_TriggerRejectedError`) sowie die
  zugehörigen Trigger-Settings-UI-Einträge in `core/settings_metadata.py`.
- In neuen Test-Suiten der Logging-Commits wurden vier Testmethoden entfernt, die ausschließlich
  die ausgeschlossene Trigger-Command-Implementierung prüfen:
  `tests/test_obs040_client_hooks.py::test_trigger_send_and_ack_share_one_command_id`,
  `::test_a_repeated_ack_is_recorded_as_dropped_not_as_received`,
  `::test_an_ack_without_a_command_id_is_dropped_and_correlation_stays_empty`,
  `tests/test_obs040_failure_isolation.py::test_a_broken_ingress_does_not_stop_a_trigger`.

### Aufgetretene Konflikte und Lösung

1. **`core/stt_session.py` (Cherry-Pick von `91a7b7f`, echter Merge-Konflikt).**
   Der Konfliktblock enthielt den kompletten, aus `5f2ee4b` übernommenen Trigger-Command-Codeblock
   (`send_trigger` … `_discard_pending_triggers`), in den `91a7b7f` lediglich `self._observe.audit(...)`-
   Aufrufe eingefügt hatte. Geprüft: alle Referenzen auf `TriggerAck`/`_PendingTrigger`/
   `_pending_triggers` sind ausschließlich innerhalb dieses Blocks verwendet – keine externen
   Abhängigkeiten im restlichen Modul. Lösung: kompletter Block entfernt (reine Trigger-Semantik,
   keine Logging-Infrastruktur unabhängig davon vorhanden).

2. **`core/controller.py`, `ui/application.py`, `ui/settings_dialog.py` (Cherry-Picks von `91a7b7f`
   und `7fc6ca6`, Auto-Merge ohne Marker, aber mit versteckten Restabhängigkeiten.**
   Nach dem Auto-Merge liefen mehrere Bestandstests mit `AttributeError` auf nicht existente,
   aus `5f2ee4b` stammende Felder/Methoden:
   - `SessionConfig.presentation_mode`, `.effective_wake_word_trigger_enabled`,
     `.effective_manual_trigger_enabled` (verwendet in den Logging-Detail-Payloads
     `client.controller.run_started` und `client.app.started`).
   - `STTController._server_owns_activation` (verwendet im Detail-Payload von
     `client.dictation.start_attempt`).
   - `STTController._manual_accept_correlation` (verwendet als `correlation_id` von
     `client.dictation.confirmed`).
   - `STTSession.supports_activation_triggers` (verwendet im Detail-Payload von
     `client.session.admitted`).

   Geprüft für jede Stelle: die referenzierten Felder/Methoden implementieren fachlich dual-mode
   Trigger-Semantik bzw. Server-Aktivierungs-Ownership (Triggerarchitektur), nicht Logging. Die
   Logging-Hooks selbst (welches Ereignis wann geloggt wird) sind unabhängig davon und wurden
   erhalten; nur die referenzierten Werte wurden auf die Pre-Trigger-Semantik zurückgeführt:
   - `presentation_mode` → `session.mode` (das vorbestehende Rohfeld `"hotkey"`/`"wake_word"`).
   - `effective_wake_word_trigger_enabled` → `session.wake_word_enabled` (vorbestehende Property
     auf Basis von `mode`).
   - `effective_manual_trigger_enabled` → `not session.wake_word_enabled` (im Pre-Trigger-Modell
     exklusiv: entweder Hotkey oder Wake Word aktiv).
   - `_server_owns_activation` im `client.dictation.start_attempt`-Payload → Detail-Key entfernt
     (Konzept existiert vor der Triggerarchitektur nicht: der Client besitzt die Aktivierung immer
     lokal).
   - `_manual_accept_correlation(attempt)` → direkt durch
     `f"hotkey:{attempt.generation}:{attempt.token}"` ersetzt (das ist exakt der Fallback-Zweig der
     Original-Methode für den Fall ohne Server-Trigger-Ack, der einzige im Pre-Trigger-Modell
     erreichbare Zweig).
   - `supports_activation_triggers` im `client.session.admitted`-Payload → Detail-Key entfernt
     (Server-Capability-Negotiation für Aktivierungs-Trigger existiert vor der Triggerarchitektur
     nicht).

   Diese Anpassungen wurden zusammen mit der Entfernung der drei nicht mehr implementierten
   `client.trigger.*`-Einträge aus der Hook-Coverage-Liste (`tests/test_obs040_contracts.py::
   TestHookListCoverage`) und der Anpassung des zugehörigen Erwartungswerts in
   `tests/test_obs040_client_hooks.py::test_session_admitted_reports_the_effective_handshake_contract`
   im Commit `fe60348 – chore(observability): adapt logging baseline to main` zusammengefasst.

3. **`core/observability/` und übrige Dateien (`cb0b81f`, `8eea774`, `d9369c5`, `9f136c3`,
   `dd0af5e`).** Keine Konflikte, keine Trigger-Abhängigkeiten festgestellt.

### Technische Abhängigkeiten von frühem Trigger-Commit – Zusammenfassung

Ja, Logging Teil A (konkret die OBS-040-Instrumentierung von `core/stt_session.py` und
`core/controller.py`) hatte technische Abhängigkeiten vom frühen Trigger-Commit `5f2ee4b`, weil die
Logging-Hooks in bereits durch `5f2ee4b` umbenannte/neue Felder und in die Trigger-Command-Methoden
selbst eingefügt worden waren. Alle betroffenen Stellen wurden identifiziert, geprüft und auf die
Pre-Trigger-Semantik zurückgeführt bzw. entfernt, ohne Trigger-Implementierung nachzuziehen.

## Tests

### Ausgeführt

- `python -m compileall -q app.py core ui scripts tests` → **OK**, keine Fehler.
- `python -m unittest discover -s tests -p "test_*.py"` → **1125 Tests**, davon **1122 bestanden**,
  **3 vorbestehende Fehler** (siehe unten), **0 durch die Separation verursachte Fehler**.

### Iterativer Testverlauf

1. Erster Lauf nach vollständigem Cherry-Pick: 9 Failures + 28 Errors, ausschließlich durch die oben
   beschriebenen Trigger-Restabhängigkeiten (`_server_owns_activation`, `_manual_accept_correlation`,
   `supports_activation_triggers`, `presentation_mode`, `effective_*_trigger_enabled`) sowie durch
   die drei nicht mehr implementierten `client.trigger.*`-Hooks.
2. Nach den Separation-Fixes (Commit `fe60348`): nur noch 3 Errors, alle in
   `tests/test_obs040_contracts.py::TestFrozenCounterSetIsUnchanged::
   test_normative_documents_are_untouched_by_this_run`.

### Nicht durch die Separation verursacht (vorbestehender Fehler)

Verifiziert durch direkten Testlauf im unveränderten Quell-Worktree
(`P:\...\workspaces\einheitliche-triggerarchitektur`, HEAD `dd0af5e`):

```
python -m unittest tests.test_obs040_contracts.TestFrozenCounterSetIsUnchanged -v
→ FAILED (errors=3), identischer FileNotFoundError
```

Ursache: `tests/test_obs040_contracts.py` referenziert die Normativ-Dokumente über den seit
Erstellung unveränderten Pfad `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV/...`.
Der Archivierungs-Commit `dd0af5e` selbst hat diese Dokumente nach
`ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/00_NORMATIV/...`
verschoben, ohne den Testpfad nachzuziehen – ein bereits im Quellbranch vorhandener Defekt, nicht
durch diese Separation verursacht. Es wurde bewusst **nicht** repariert, um Tests nicht zu verändern,
nur damit sie grün werden, und weil es sich nicht um eine durch die Separation verursachte
Logging-Regression handelt.

### Nicht lokal reproduzierbar

Keine – alle im Auftrag geforderten Prüfungen (`compileall`, vollständige `unittest`-Discovery) waren
lokal reproduzierbar. Es gab keine Hardware-, Server- oder sonstigen manuell erforderlichen Prüfungen
im Testumfang dieses Branches.

## Endzustand

`git status --short` (neuer Logging-Worktree): **leer** (clean).

Commitliste `feat/logging-observability-pre-trigger` gegenüber `origin/main`:

```
fe60348 chore(observability): adapt logging baseline to main
a350cd9 chore(observability): archive pre-trigger logging workstream
99c6d30 chore(observability): close logging phase before trigger migration
b07a813 feat(observability): polish logging diagnostics UI
dc68528 fix(observability): checkpoint OBS-060 hardening and evidence
19ba8e8 feat(observability): complete OBS-050 local log view
29c450f feat(observability): complete OBS-040 observation hooks
7c5adb3 feat(observability): complete OBS-030 persistence and worker
1c02903 feat(observability): complete OBS-010 and OBS-020 foundation
0de242c chore: establish OBS-010 project baseline and work archive
```

Grobe Diff-Statistik `origin/main...HEAD`: **498 Dateien geändert, 109522 Zeilen hinzugefügt,
59 Zeilen entfernt** (weit überwiegend neue Logging-/Observability-Produktdateien sowie
Arbeitsakte/Dokumentation; die 59 Entfernungen stammen aus im Zuge der Archivierung bereinigten
Steuerungsdokumenten).

Bestätigt:

- Lokaler Worktree-Pfad: `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\logging-observability-pre-trigger`,
  ausgecheckt auf `feat/logging-observability-pre-trigger`.
- `main\`-Worktree wurde in diesem Run nicht umgeschaltet oder verändert (weiterhin auf
  `wip/led-sound-debugfeedback-sicherung`, HEAD `ef230f2` – dieser Zustand war bereits zu Beginn
  des Runs so vorhanden und wurde nicht durch BS-001 verursacht; siehe Anmerkung unten).
- Der ursprüngliche Trigger-Worktree (`workspaces\einheitliche-triggerarchitektur`) blieb
  unverändert: Branch weiterhin `feat/einheitliche-triggerarchitektur`, HEAD weiterhin `dd0af5e`,
  `git status --short` identisch zum Ausgangsstand vor diesem Run (zwei vorbestehend modifizierte
  Dateien und drei vorbestehende untracked Verzeichnisse), kein Stash, kein Reset, kein Clean, kein
  Branch-Wechsel.

**Anmerkung zum `main\`-Worktree:** Der Auftrag ging davon aus, dass `main\` auf Branch `main` steht.
Tatsächlich stand `main\` zu Beginn dieses Runs (und weiterhin am Ende) auf
`wip/led-sound-debugfeedback-sicherung` (HEAD `ef230f2`). Dieser Zustand wurde nicht durch BS-001
verursacht und `main\` wurde in diesem Run nicht angefasst; er wird hier lediglich zur Kenntnis
dokumentiert.

## Schlussurteil

`READY TO PUSH AND OPEN PR AGAINST MAIN`
