# OBS-020 – Implementierungsauftrag: Ingress, Health & Redaction

## Voraussetzung

OBS-010 muss durch einen dokumentierten Gate-Review mit `PASS` abgeschlossen sein. Verifiziere dies vor Beginn. Bei fehlendem PASS nicht implementieren.

## Ziel

Implementiere **OBS-020 – Ingress, Health & Redaction** auf Basis des kanonischen OBS-010-Modells.


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

Implementiere die freigegebenen Ingress-/Health-/Redaction-Contracts, insbesondere:

- zentralen Logging-Ingress als rein beobachtenden Eingang für kanonische Records
- klare Trennung zwischen Ingestion und späterer Speicherung/Query
- robuste Fehlerisolierung: Logging darf Runtime-/Event-Verarbeitung nicht beschädigen
- die in OBS-000 festgelegte Observer-Regel: eine Logging-Observer-Grenze muss `Exception` selbst abfangen, damit kein Fehler bis zu einem Dispatcher eskaliert, der sonst `reject_event` auslösen würde
- Health-/Counter-Zustände für Ingress-Fehler und interne Logging-Probleme gemäß Plan
- Redaction-/Privacy-Grenzen
- keine Secrets, Tokens, API-Keys oder Audio-Payloads in persistierbare Records
- Transcript-Inhalt ausschließlich entsprechend der festgelegten Opt-in/Policy
- Redaction von strukturierten Details/Raw-Daten ohne unnötigen Verlust nicht sensibler Struktur
- interne Logging-Fehler dürfen keine rekursive Logging-Schleife erzeugen
- klare Contracts für akzeptierte, verworfene und intern fehlgeschlagene Ingestion

Noch **keine** vollständige SQLite-/Worker-/Queue-Implementierung aus OBS-030 vorziehen.

## Tests

Mindestens:
- erfolgreiche Ingestion
- ungültige Records
- Observer-Ausnahmen bleiben isoliert
- Health-/Counter-Verhalten
- Redaction von Secrets
- Erhalt nicht sensibler Struktur
- Audio-Payload-Abwehr
- Transcript-Policy
- keine Mutation von Eingangsdaten
- keine Rekursion bei internen Logging-Fehlern
- Regression der bestehenden Event-/Feedback-Pfade

## Evidence

Mindestens:
- `TEST_RESULTS.md`
- `DIFF_SUMMARY.md`
- `CONTRACT_COVERAGE.md`
- `REDACTION_CASES.md`

## Fortschrittscheckliste

Die zentrale Fortschrittsdatei liegt unter:

`ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\30_AUSFUEHRUNG\LOGGING_V1_CHECKLISTE.md`

Aktualisiere sie am Ende dieses Auftrags selbst:

- nur bei erfolgreichem Abschluss den zu diesem Auftrag gehörenden Punkt auf `[x]` setzen,
- bei `FAIL` oder `BLOCKED` nicht abhaken,
- unter `Aktuell` den nächsten zulässigen Schritt eintragen,
- bestehende frühere Häkchen nicht verändern.

## Abschluss

`OBS-020 IMPLEMENTED – READY FOR REVIEW`
