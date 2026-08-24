# WS-NORM-002 – Governance-Endbereinigung und Main-Workspace endgültig normalisieren

## Ziel

Dieser kurze Maintenance-Run schließt die noch offenen organisatorischen Punkte aus WS-NORM-001 vollständig ab.

WICHTIG:
- Keine Trigger-Facharbeit.
- Keine Main→Trigger-Integration in diesem Run.
- Trigger-Worktree ausschließlich read-only.
- Keine neuen dauerhaften Worktrees erzeugen.
- Kein manuelles Kopieren von ARBEITSDATEIEN zwischen Worktrees.

Bekannter GitHub-Main-Stand bei Auftragserstellung:
`8428dade9a418960956bcc41b8f53c9b552db509`

Vor Änderungen tatsächlichen aktuellen Stand erneut verifizieren.

## Feste Pfade

Repository-Stamm:
`P:\GithubRepos\marcosudau-vps\voice-stt-client`

Standalone Main-Clone:
`P:\GithubRepos\marcosudau-vps\voice-stt-client\main`

Aktiver Trigger-Worktree / Session Root:
`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`

Branch dort:
`feat/einheitliche-triggerarchitektur`

Alter Logging-Worktree-Pfad:
`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\logging-observability-pre-trigger`

Dieser Pfad ist git-seitig bereits deregistriert. Falls der leere Verzeichnis-Stub vom Benutzer inzwischen gelöscht wurde, nur bestätigen. Falls er noch existiert, nicht erzwingen; Zustand dokumentieren.

## Zeitstempel

Zu Beginn und Ende tatsächliche lokale Zeit erfassen:

```powershell
$RUN_START = Get-Date
$RUN_START.ToString("o")
$RUN_END = Get-Date
$RUN_END.ToString("o")
```

Alle neuen Verlaufseinträge müssen echtes Datum UND Uhrzeit mit UTC-Offset enthalten.

## Trigger-Worktree strikt schützen

Im Trigger-Worktree nur lesen:

```powershell
git -C "P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur" branch --show-current
git -C "P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur" rev-parse HEAD
git -C "P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur" status --short
```

Nicht committen, stagen, staschen, resetten, cleanen, mergen, rebasen oder Dateien schreiben.

## GitHub Main verifizieren

Repository:
`marcosudau-vps/voice-stt-client`

Prüfen:
- aktueller `main`-SHA
- PR #1 ist gemerged
- Logging-/Observability-Arbeitsakte liegt in Main

Wenn Main inzwischen weitergelaufen ist, aktuellen Stand verwenden und dokumentieren.

## Standalone Main-Clone wirklich auf Branch main stellen

Pfad:
`P:\GithubRepos\marcosudau-vps\voice-stt-client\main`

Zuerst:

```powershell
git -C "P:\GithubRepos\marcosudau-vps\voice-stt-client\main" status --short
git -C "P:\GithubRepos\marcosudau-vps\voice-stt-client\main" branch --show-current
git -C "P:\GithubRepos\marcosudau-vps\voice-stt-client\main" remote -v
```

Bekannter Zustand aus WS-NORM-001:
Checkout war weiterhin `wip/led-sound-debugfeedback-sicherung`.

Der Branch selbst muss erhalten bleiben und darf nicht gelöscht oder umgeschrieben werden.

Wenn der Checkout clean ist:
1. WIP-Branch-Ref verifizieren.
2. auf `main` wechseln.
3. echten GitHub-Remote identifizieren.
4. `main` fetchen.
5. ausschließlich Fast-Forward auf GitHub-main.

Beispiel:

```powershell
git -C "P:\GithubRepos\marcosudau-vps\voice-stt-client\main" switch main
git -C "P:\GithubRepos\marcosudau-vps\voice-stt-client\main" fetch <GITHUB_REMOTE>
git -C "P:\GithubRepos\marcosudau-vps\voice-stt-client\main" merge --ff-only <GITHUB_REMOTE>/main
```

Kein Reset. Kein Force. WIP-Branch nicht löschen.

Wenn der Main-Clone unerwartet dirty ist: nicht verändern und `GOVERNANCE CLEANUP BLOCKED`.


## Prompt-/Session-Artefakte dieses Runs versioniert sichern

Die vom Benutzer bereitgestellten Session-Dateien liegen zunächst bewusst außerhalb der Git-Worktrees unter:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\SESSION_PROMPTS\WS-NORM-002_FINAL_GOVERNANCE_AND_MAIN_WORKSPACE_CLEANUP.md`

und:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\SESSION_PROMPTS\WS-NORM-002_BEGLEITNACHRICHT.txt`

Nachdem der Standalone Main-Clone erfolgreich auf Branch `main` umgestellt und auf aktuellen GitHub-main-Stand gebracht wurde, beide Dateien als Run-Artefakte versioniert sichern unter:

`ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/prompts/WS-NORM-002_FINAL_GOVERNANCE_AND_MAIN_WORKSPACE_CLEANUP.md`

und:

`ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/prompts/WS-NORM-002_BEGLEITNACHRICHT.txt`

Die versionierten Kopien müssen in `OUTPUT_INDEX.md` und `FINALIZATION_REPORT.md` referenziert werden.

Kein Prompt-/Session-Artefakt darf ausschließlich außerhalb der Projektakte verbleiben.

## Governance-Lücken schließen

Im Standalone Main-Clone arbeiten.

### 1. WORKSPACE_KONVENTION.md

Sicherstellen, dass existiert:

`ARBEITSDATEIEN/00_STEUERUNG/WORKSPACE_KONVENTION.md`

Falls nicht: erstellen.

Mindestens festhalten:
- `main\` = Baseline / Branch `main`
- `workspaces\einheitliche-triggerarchitektur\` = aktiver Entwicklungs-Workspace
- Standard-Agent-Session-Root = Trigger-Worktree
- temporäre Worktrees nur für klaren Zweck und nach Abschluss entfernen
- ARBEITSDATEIEN nie manuell zwischen Worktrees kopieren
- jeder Agentenauftrag enthält Startordner, Branch, Prompt-Pfad, Report-Pfad und Rückgabe-Artefakt

### 2. CURRENT_STATE.md

`ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md`

Minimal aktualisieren:
- Logging/Observability Teil A ist nach `main` integriert
- Status weiterhin `CONTROLLED CLOSED / ACCEPTED PRE-TRIGGER BASELINE`
- `G-OBS-V1` weiterhin `NOT PASSED`
- Logging Teil B weiterhin deferred
- Triggerarchitektur ist aktiver Workstream
- aktiver Workspace: `workspaces\einheitliche-triggerarchitektur`
- nächster technischer Schritt: `Main-Baseline kontrolliert in feat/einheitliche-triggerarchitektur integrieren`
- kein aktiver Logging-Worktree mehr

### 3. MASTERPLAN.md

`ARBEITSDATEIEN/00_STEUERUNG/MASTERPLAN.md`

Minimal korrigieren:
- Logging Teil A jetzt Bestandteil Main-Baseline
- Logging Teil B bleibt deferred bis nach Trigger-Migration
- Triggerarchitektur ist nächster aktiver Entwicklungsabschnitt
- Branch-Separation / Merge / Aufräumphase abgeschlossen
- keine Trigger-Fachentscheidungen verändern

### 4. AUFRAEUMPHASE_INDEX.md

Aktuell kanonisch:
`ARBEITSDATEIEN/00_STEUERUNG/AUFRAEUMPHASE_INDEX.md`

Diesen Pfad beibehalten, nicht duplizieren.

Konsistent machen:
- WS-NORM-001 nicht als physisch vollständig entfernt bezeichnen, falls der leere Stub noch existiert
- Main-Workspace nur dann als Branch main bezeichnen, wenn Checkout tatsächlich main ist
- tatsächliche Run-/Prompt-/Report-Pfade beibehalten

### 5. OUTPUT_INDEX für WS-NORM-001

Sicherstellen, dass existiert:

`ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-WS-NORM-001_2026-08-23/OUTPUT_INDEX.md`

Falls fehlend: erstellen.

Mindestens zuordnen:
- `AUFRAEUMPHASE_INDEX.md`
- `LOG_VERLAUF.md`
- `RUN_REPORT.md`
- BS-002-Prompt
- BS-003-Prompt
- CI_GREEN_REPORT.md
- finale Workspace-/Governance-Artefakte
- lokale `WORKSPACE_MAP.md` und `ACTIVE_SESSION_ROOT.txt`, falls vorhanden

Spalten:
| Artefakt | Pfad | Typ | Versioniert? | Zweck | Zeitbezug |

Nichts erfinden.

## Lokale Workspace-Hinweise außerhalb von Git

Prüfen:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\WORKSPACE_MAP.md`

und:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\ACTIVE_SESSION_ROOT.txt`

Falls fehlend: erstellen.

`ACTIVE_SESSION_ROOT.txt` enthält exakt:
`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`

`WORKSPACE_MAP.md` muss den tatsächlichen Zustand wiedergeben:
- BASELINE: `main\`, Branch main
- ACTIVE DEVELOPMENT: Trigger-Worktree
- DEFAULT AGENT SESSION ROOT: Trigger-Worktree
- TEMPORARY WORKTREES: none

Falls der leere Logging-Verzeichnis-Stub noch existiert: als kosmetischen Restpunkt erwähnen, aber nicht als Worktree.

## WS-NORM-001 RUN_REPORT endgültig konsistent machen

Datei:

`ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-WS-NORM-001_2026-08-23/RUN_REPORT.md`

Nur sachliche Korrekturen:
- finalen GitHub-main-Ausgangsstand korrekt wiedergeben
- Main-Clone-Endcheckout nach diesem Run korrekt als `main`
- WIP-Branch weiterhin erhalten
- Logging-Worktree git-seitig entfernt
- physischen Stub nur dann als gelöscht bezeichnen, wenn `Test-Path` tatsächlich false ergibt
- keine falschen SHAs stehen lassen

## LOG_VERLAUF append-only finalisieren

`ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md`

Keine historischen Einträge löschen.

Einen neuen kurzen Finalisierungseintrag anhängen:

`## 2026-08-23 HH:MM:SS +02:00 – WS-NORM-002: Governance- und Workspace-Endbereinigung`

Mindestens:
- Ausgangsbefund nach WS-NORM-001
- Main-Clone war noch auf WIP ausgecheckt
- Governance-Dateien vervollständigt
- OUTPUT_INDEX ergänzt
- endgültiger Default Session Root
- Status des leeren Logging-Stubs
- Trigger-Worktree unverändert
- nächster Schritt: `Main-Baseline kontrolliert in feat/einheitliche-triggerarchitektur integrieren`

## Abschlussreport

Erstelle:

`ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-WS-NORM-002_2026-08-23/FINALIZATION_REPORT.md`

Enthält:
- Startzeit / Endzeit
- Ausgangs-Main-SHA
- Main-Clone-Pfad
- Trigger-Branch/HEAD
- gefundene Inkonsistenzen
- Korrekturen
- GitHub main
- lokaler Main-Clone: Branch und HEAD
- WIP-LED/Sound-Branch weiterhin vorhanden
- Trigger-Worktree unverändert
- Logging-Worktree nicht registriert
- physischer Stub vorhanden/entfernt
- Default Session Root
- nächster Schritt exakt: `Main-Baseline kontrolliert in feat/einheitliche-triggerarchitektur integrieren`

Schlussurteil genau eines:
`GOVERNANCE CLEAN – READY FOR TRIGGER MAIN-INTEGRATION`
oder
`GOVERNANCE CLEANUP BLOCKED`

## Commit und Push

Vor Commit:

```powershell
git -C "P:\GithubRepos\marcosudau-vps\voice-stt-client\main" status --short
git -C "P:\GithubRepos\marcosudau-vps\voice-stt-client\main" diff --check
```

Nur Governance-/Dokumentationsdateien stagen.

Keine Produktcodeänderungen.

Commit:
`docs(project): finalize workspace governance after logging merge`

Auf `main` pushen.

Danach GitHub-CI für genau diesen finalen Main-HEAD abwarten.

Akzeptanz: `success`

Nach dem Push keine weiteren Dateien verändern.

## Definition of Done

Erfolgreich nur wenn:
1. `main\` tatsächlich auf Branch `main` ausgecheckt ist.
2. WIP-LED/Sound-Branch erhalten bleibt.
3. `WORKSPACE_KONVENTION.md` existiert.
4. `CURRENT_STATE.md` aktuellen Stand wiedergibt.
5. `MASTERPLAN.md` aktuellen Stand wiedergibt.
6. `AUFRAEUMPHASE_INDEX.md` konsistent ist.
7. WS-NORM-001 `OUTPUT_INDEX.md` existiert.
8. `WORKSPACE_MAP.md` und `ACTIVE_SESSION_ROOT.txt` vorhanden sind.
9. `LOG_VERLAUF.md` datierten/zeitgestempelten WS-NORM-002-Eintrag besitzt.
10. WS-NORM-002 `FINALIZATION_REPORT.md` existiert.
11. Trigger-Worktree unverändert ist.
12. finaler Main-CI-Lauf grün ist.
13. kein neuer dauerhafter Worktree erzeugt wurde.
14. Schlussurteil lautet:

`GOVERNANCE CLEAN – READY FOR TRIGGER MAIN-INTEGRATION`
