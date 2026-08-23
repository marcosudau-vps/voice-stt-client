# OBS-030 – Gate Review

## Ziel

Prüfe **OBS-030 – Queue, Worker, SQLite & Retention**.

## Verbindlicher Kontext

Session-Root:

`P:\GithubRepos\marcosudau-vps`

Zu prüfender Projektbereich:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`

Lies:

- `ARBEITSDATEIEN\README.md`
- `ARBEITSDATEIEN\AGENTS.md`
- `ARBEITSDATEIEN\00_STEUERUNG\CURRENT_STATE.md`
- `ARBEITSDATEIEN\00_STEUERUNG\MASTERPLAN.md`
- `ARBEITSDATEIEN\00_STEUERUNG\ARBEITSPROZESS.md`
- alle für das zu prüfende Work Package relevanten normativen, planerischen, Run- und Evidence-Unterlagen
- den tatsächlichen Git-Diff und die Tests

Die Authority-Hierarchie ist verbindlich.

## Prüfprinzip

Prüfe den **tatsächlichen Zustand**, nicht nur Abschlussberichte.

Mindestens:

- Contract-/Anforderungsabdeckung
- Scope-Treue
- Implementierungsqualität
- Fehler- und Randfälle
- Regressionen
- Testqualität
- Evidence-Konsistenz
- `git diff --check`
- finaler Git-Status
- keine unzulässigen Änderungen außerhalb des Work Packages

Keine Implementierung durchführen. Kleine redaktionelle Review-Dateien dürfen nur dort angelegt werden, wo das bestehende Arbeitssystem Review-/Evidence-Dateien vorsieht. Produktcode nicht verändern.

## Ergebnis

Nur `PASS`, wenn sämtliche Gate-Kriterien belastbar erfüllt sind.

Bei `FAIL`:

- konkrete Befunde
- betroffene Dateien/Tests
- minimale erforderliche Korrekturen
- keine pauschalen Neuplanungen

Wenn PASS und ein nächstes Work Package existiert, nutze verbleibende Zeit für einen **Readiness-Check des nächsten bereits vorbereiteten Auftrags**. Prüfe, ob dessen Voraussetzungen durch den realen Endzustand erfüllt sind. Keine nächste Implementierung starten.

## Besondere Gate-Kriterien

- Runtime-Pfade werden nicht durch Persistenz blockiert
- Queue ist bounded
- Drop-/Prioritätspolitik entspricht exakt dem Freeze
- HIGH-Sonderregel ist nicht verallgemeinert
- Überlast wird gezählt/sichtbar
- SQLite round-trip ist strukturerhaltend
- Retention ist deterministisch und testbar
- kein Memory-Ringbuffer als zweite Wahrheit
- interne Worker-/DB-Fehler bleiben isoliert
- Persistenz-/Dedupe-Identität ist stabil
- Tests enthalten echte Überlast-/Fehlerfälle

## Fortschrittscheckliste

Die zentrale Fortschrittsdatei liegt unter:

`ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\30_AUSFUEHRUNG\LOGGING_V1_CHECKLISTE.md`

Aktualisiere sie am Ende dieses Auftrags selbst:

- nur bei erfolgreichem Abschluss den zu diesem Auftrag gehörenden Punkt auf `[x]` setzen,
- bei `FAIL` oder `BLOCKED` nicht abhaken,
- unter `Aktuell` den nächsten zulässigen Schritt eintragen,
- bestehende frühere Häkchen nicht verändern.

## Abschluss

`OBS-030 GATE PASS – OBS-040 MAY PROCEED`

oder:

`OBS-030 GATE FAIL`

## NUR Bei GATE PASS: lokalen Commit erstellen

Nach Aktualisierung von Evidence, Checklist und Steuerungsdateien genau einen lokalen Commit für das erfolgreich geprüfte Work Package erstellen. Vorher git status und den zu commitenden Umfang prüfen. Kein Push.
Bei FAIL oder BLOCKED: keinen Commit erstellen.
