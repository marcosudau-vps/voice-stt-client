# OBS-030 – Implementierungsauftrag: Queue, Worker, SQLite & Retention

## Voraussetzung

OBS-020 muss dokumentiert mit `PASS` abgeschlossen sein. Verifiziere dies vor Beginn.

## Ziel

Implementiere **OBS-030 – Queue, Worker, SQLite & Retention**.


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

Implementiere gemäß normativen Unterlagen:

- nicht blockierenden Übergang vom Ingress in eine begrenzte Queue
- Worker-Verarbeitung außerhalb kritischer Runtime-Pfade
- SQLite als lokalen primären V1-Speicher
- schema-/versionsbewusste Persistenz des kanonischen Records
- deterministische Serialisierung/Deserialisierung der freigegebenen strukturierten Felder
- Retention/Cleanup gemäß Konfiguration
- Failure-Isolation zwischen Queue, Worker und Store
- belastbare Health-/Counter-Anbindung
- die eingefrorene Backpressure-/Drop-Policy:
  - prioritätsbewusst
  - Debug/Performance zuerst verwerfbar
  - High-Priorität geschützt soweit möglich
  - die in OBS-000 festgelegte HIGH-Sonderregel nur für den vorgesehenen **nicht-replayed Server-Event-Typ**
  - bei katastrophaler Überlast dürfen auch hohe Prioritäten verloren gehen, aber dies muss gezählt/sichtbar werden
- Replay-/Dedupe-Identität so vorbereiten/umsetzen, wie für V1 in den Contracts vorgesehen
- **kein Memory-Ringbuffer als parallele Wahrheit**
- lokaler SQLite-Store ist die V1-Quelle für lokale Logabfragen

OBS-050-UI nicht vorziehen.

## Tests

Mindestens:
- Queue-Grenzen
- nicht blockierendes Verhalten
- Prioritäts-/Drop-Policy
- HIGH-Sonderregel
- Worker-Fehler
- SQLite round-trip
- strukturierte/raw-Daten round-trip
- Retention
- Dedupe/Identity soweit im WP vorgesehen
- Neustart/Persistenz
- Lock-/Concurrency-nahe Fälle
- Health-/Drop-Counter
- keine Runtime-Propagation interner Store-Fehler

## Evidence

Mindestens:
- `TEST_RESULTS.md`
- `DIFF_SUMMARY.md`
- `CONTRACT_COVERAGE.md`
- `BACKPRESSURE_RESULTS.md`
- `SQLITE_ROUNDTRIP.md`

## Fortschrittscheckliste

Die zentrale Fortschrittsdatei liegt unter:

`ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\30_AUSFUEHRUNG\LOGGING_V1_CHECKLISTE.md`

Aktualisiere sie am Ende dieses Auftrags selbst:

- nur bei erfolgreichem Abschluss den zu diesem Auftrag gehörenden Punkt auf `[x]` setzen,
- bei `FAIL` oder `BLOCKED` nicht abhaken,
- unter `Aktuell` den nächsten zulässigen Schritt eintragen,
- bestehende frühere Häkchen nicht verändern.

## Abschluss

`OBS-030 IMPLEMENTED – READY FOR REVIEW`
