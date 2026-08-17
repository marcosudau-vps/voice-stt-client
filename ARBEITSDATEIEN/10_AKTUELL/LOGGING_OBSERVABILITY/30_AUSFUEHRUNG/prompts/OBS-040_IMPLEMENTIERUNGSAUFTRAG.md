# OBS-040 – Implementierungsauftrag: Server Live Adapter & Client Observation Hooks

## Voraussetzung

OBS-030 muss dokumentiert mit `PASS` abgeschlossen sein. Verifiziere dies vor Beginn.

## Ziel

Implementiere **OBS-040 – Server Live Adapter & Client Observation Hooks**.


## Verbindlicher Kontext

Session-Root:

`P:\GithubRepos\marcosudau-vps`

Schreibbarer Projektbereich:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`

Server- und LED-Workspace dürfen ausschließlich lesend als Referenz verwendet werden, sofern dies für Contract-Abgleiche nötig ist.

Lies vor Beginn mindestens:

- `ARBEITSDATEIEN\README.md`
- `ARBEITSDATEIEN\AGENTS.md`
- `ARBEITSDATEIEN\00_STEUERUNG\CURRENT_STATE.md`
- `ARBEITSDATEIEN\00_STEUERUNG\MASTERPLAN.md`
- `ARBEITSDATEIEN\00_STEUERUNG\ARBEITSPROZESS.md`
- die relevanten normativen, planerischen und Evidence-Unterlagen unter `ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\`

Die dokumentierte Authority-Hierarchie ist verbindlich. Historische, analytische oder ungeprüfte Draft-Unterlagen dürfen normative Vorgaben nicht überschreiben.

## Arbeitsorganisation

Verwende unter `30_AUSFUEHRUNG\Runs\` den nächsten freien Laufordner nach dem Schema:

`RUN-<WP>-<NN>_<YYYY-MM-DD>`

Dort mindestens:
- `RUN_LOG.md`
- `RESULT.md`

Evidence kommt unter:

`40_EVIDENCE\<WP>\RUN-<NN>_<YYYY-MM-DD>\`

Aktualisiere am Ende:
- `ARBEITSDATEIEN\00_STEUERUNG\CURRENT_STATE.md`
- `ARBEITSDATEIEN\00_STEUERUNG\LOG_VERLAUF.md`

`LOG_VERLAUF.md` append-only.

## Harte Grenzen

- kein `git reset`
- kein `git clean`
- kein Rebase
- kein Merge
- kein Push
- kein Tag
- kein PR
- kein Commit
- keine fachfremden Produktänderungen
- keine Änderungen in Server-/LED-Workspace
- keine spätere Work-Package-Implementierung vorziehen, außer eine minimale Schnittstelle ist für Testbarkeit zwingend erforderlich und wird ausdrücklich dokumentiert
- Logging bleibt strikt beobachtend und niemals Runtime-/Lifecycle-Autorität

## Abschlussprüfung

Mindestens:
- relevante Unit-/Integrationstests
- bestehende betroffene Regressionstests
- `git diff --check`
- `git status --short`
- `git diff --stat`
- Scope-Prüfung gegen das Work Package

Bei einem echten Blocker: nicht raten oder Architektur erfinden, sondern exakt dokumentieren.


## Verbindlicher Scope

Implementiere die Beobachtungsanbindung, ohne bestehende Runtime-Autoritäten zu verschieben:

- Server-Live-Adapter für den vorhandenen Session-/Eventstream
- Normalisierung strukturierter Server-Events in das kanonische Logging-Modell
- bestehender Event-Ingress fächert unabhängig zu Feedback und Logging auf; Logging darf Feedback nicht besitzen oder steuern
- vorhandene Session-/Eventstream-/Cursor-/Reconnect-Mechanismen respektieren
- replayed-Information und stabile Eventidentität korrekt erhalten
- strukturierte Client-Observation-Hooks an natürlichen Punkten, insbesondere soweit im Plan vorgesehen:
  - Connection
  - Eventstream
  - Trigger send/ack
  - Audio-Queue-Zustände
  - Settings apply
  - Feedback
  - LED
  - klassifizierte Fehler
  - Performance
- keine Rekonstruktion von Lifecycle aus Logtext
- keine per-Packet-Audio- oder per-VAD-Sample-Logging-Flut
- Python-Logging-Anbindung und strukturierte Client-Events gemäß freigegebenem Contract
- Session-/Activation-/Command-/Correlation-Kontext korrekt übernehmen, wenn verfügbar
- Logging-Ausfall beeinflusst die eigentliche Clientfunktion nicht

Noch keine erweiterte Remote-History/Admin-Control-Funktionalität aus OBS-100+ vorziehen.

## Tests

Mindestens:
- Server-Live-Event-Normalisierung
- replayed/non-replayed
- Eventidentität/Dedupe
- unabhängiges Fan-out Feedback vs Logging
- Logging-Observer-Ausfall ohne Runtime-Ausfall
- relevante Client-Hooks
- Korrelationsfelder
- kein per-packet Logging
- Reconnect/Replay-nahe Fälle
- Regression bestehender Feedback-/Eventstream-Funktion

## Evidence

Mindestens:
- `TEST_RESULTS.md`
- `DIFF_SUMMARY.md`
- `CONTRACT_COVERAGE.md`
- `OBSERVATION_HOOK_MATRIX.md`
- `SERVER_EVENT_MAPPING.md`

## Fortschrittscheckliste

Die zentrale Fortschrittsdatei liegt unter:

`ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\30_AUSFUEHRUNG\LOGGING_V1_CHECKLISTE.md`

Aktualisiere sie am Ende dieses Auftrags selbst:

- nur bei erfolgreichem Abschluss den zu diesem Auftrag gehörenden Punkt auf `[x]` setzen,
- bei `FAIL` oder `BLOCKED` nicht abhaken,
- unter `Aktuell` den nächsten zulässigen Schritt eintragen,
- bestehende frühere Häkchen nicht verändern.

## Abschluss

`OBS-040 IMPLEMENTED – READY FOR REVIEW`
