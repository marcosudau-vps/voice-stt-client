# OBS-050 – Gate Review

## Ziel

Prüfe **OBS-050 – Local Query, Minimal UI & Settings**.

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

- UI greift ausschließlich über vorgesehene Query-Schicht zu
- kein Memory-Ringbuffer
- Live-Ansicht tailt den lokalen Store
- Filter/Cursor/Sortierung verhalten sich deterministisch
- UI ist kein Infrastruktur-/Runtime-Owner
- Logging funktioniert unabhängig von geöffneter UI
- Ownership-Domains der Settings werden nicht vermischt
- keine Remote-History/Admin-Funktionen vorgezogen
- bestehende UI-/Settings-Funktionen regressieren nicht

## Fortschrittscheckliste

Die zentrale Fortschrittsdatei liegt unter:

`ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\30_AUSFUEHRUNG\LOGGING_V1_CHECKLISTE.md`

Aktualisiere sie am Ende dieses Auftrags selbst:

- nur bei erfolgreichem Abschluss den zu diesem Auftrag gehörenden Punkt auf `[x]` setzen,
- bei `FAIL` oder `BLOCKED` nicht abhaken,
- unter `Aktuell` den nächsten zulässigen Schritt eintragen,
- bestehende frühere Häkchen nicht verändern.

## Abschluss

`OBS-050 GATE PASS – OBS-060 MAY PROCEED`

oder:

`OBS-050 GATE FAIL`

## NUR Bei GATE PASS: lokalen Commit erstellen

Nach Aktualisierung von Evidence, Checklist und Steuerungsdateien genau einen lokalen Commit für das erfolgreich geprüfte Work Package erstellen. Vorher git status und den zu commitenden Umfang prüfen. Kein Push.
Bei FAIL oder BLOCKED: keinen Commit erstellen.
