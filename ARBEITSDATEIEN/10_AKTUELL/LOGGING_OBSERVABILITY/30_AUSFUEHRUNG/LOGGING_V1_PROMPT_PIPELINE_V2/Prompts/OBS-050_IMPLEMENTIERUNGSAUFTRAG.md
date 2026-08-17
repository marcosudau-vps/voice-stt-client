# OBS-050 – Implementierungsauftrag: Local Query, Minimal UI & Settings

## Voraussetzung

OBS-040 muss dokumentiert mit `PASS` abgeschlossen sein. Verifiziere dies vor Beginn.

## Ziel

Implementiere **OBS-050 – Local Query, Minimal UI & Settings** für Logging V1.


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

Implementiere:

- lokale Query-Abstraktion über den SQLite-V1-Store
- Query/Filter/Cursor/Limit gemäß freigegebenem Contract
- LogQueryService als UI-Zugriffsschicht
- minimale V1-Logansicht
- Tabelle/Liste plus Details/Raw-Ansicht
- Filter mindestens nach den im Plan vorgesehenen Dimensionen:
  - Source/Producer
  - Channel
  - Level
  - Type
  - Text
  - relevanter Kontext/IDs
- Live-Ansicht liest/tailt über die DB-/Query-Schicht; **kein Memory-Ringbuffer**
- klare Trennung zwischen:
  - lokalen Client-Logging-Einstellungen
  - Session-Konfiguration
  - späterer serverweiter Admin-Konfiguration
- Retention/Privacy/Transcript-Logging-Einstellungen nur im bereits freigegebenen V1-Umfang
- UI ist Consumer, nicht Logging-Infrastruktur
- Logging funktioniert auch ohne geöffnete Logansicht
- keine Remote-History/Admin-UI aus späteren Work Packages

## Tests

Mindestens:
- Query-Filter
- Cursor/Pagination
- deterministische Sortierung
- Text-/Kontextfilter
- leere/ungültige Filter
- UI öffnet/aktualisiert ohne Runtime-Autorität
- Live-Tailing über Store/Query
- Einstellungen wirken nur auf ihre Ownership-Domain
- Logging läuft ohne UI
- Regression bestehender Settings/UI

## Evidence

Mindestens:
- `TEST_RESULTS.md`
- `DIFF_SUMMARY.md`
- `CONTRACT_COVERAGE.md`
- `QUERY_CASES.md`
- `UI_ACCEPTANCE.md`

## Fortschrittscheckliste

Die zentrale Fortschrittsdatei liegt unter:

`ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\30_AUSFUEHRUNG\LOGGING_V1_CHECKLISTE.md`

Aktualisiere sie am Ende dieses Auftrags selbst:

- nur bei erfolgreichem Abschluss den zu diesem Auftrag gehörenden Punkt auf `[x]` setzen,
- bei `FAIL` oder `BLOCKED` nicht abhaken,
- unter `Aktuell` den nächsten zulässigen Schritt eintragen,
- bestehende frühere Häkchen nicht verändern.

## Abschluss

`OBS-050 IMPLEMENTED – READY FOR REVIEW`
