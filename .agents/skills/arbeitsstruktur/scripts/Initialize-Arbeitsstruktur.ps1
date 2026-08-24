[CmdletBinding()]
param(
    [string]$RepositoryRoot
)

. "$PSScriptRoot\Arbeitsstruktur.Common.ps1"

$repo = Resolve-RepositoryRoot $RepositoryRoot
$arbeitsdateien = Get-ArbeitsdateienRoot $repo

Ensure-Directory $arbeitsdateien
Ensure-Directory (Join-Path $arbeitsdateien "00_STEUERUNG")
Ensure-Directory (Join-Path $arbeitsdateien "10_AKTUELL")
Ensure-Directory (Join-Path $arbeitsdateien "20_ZURUECKGESTELLT")
Ensure-Directory (Join-Path $arbeitsdateien "90_HISTORIE")

$agentsPath = Get-RootFilePath -RepositoryRoot $repo -CanonicalName "AGENTS.md"
$agentsSection = @"
## Arbeitsstruktur und Arbeitsdateien

- Lies zu Beginn einer neuen Session zuerst `ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md`.
- Öffne danach den dort genannten aktiven Arbeitsblock und lies dessen `README.md` und `STATUS.md`.
- Wenn geplant wird, beachte zusätzlich `PLANUNG/README.md`.
- Wenn ein Arbeitspaket umgesetzt wird, lies dessen `README.md` und `PLAN.md` vollständig.
- `IDEEN/` ist ausdrücklich **kein Projektwissen**. Inhalte daraus dürfen nicht für Recherche, Analyse, Planung, Entscheidungen oder Implementierung verwendet werden, sofern der konkrete Auftrag nicht ausdrücklich auf eine bestimmte Datei dort verweist.
- `20_ZURUECKGESTELLT/` enthält derzeit nicht aktive, aber nicht abgeschlossene Arbeitsblöcke.
- `90_HISTORIE/` ist historischer Bestand und grundsätzlich nicht als aktueller Projektstand zu verwenden.
- Große Rohquellen dürfen dauerhaft `RAW / UNINDEXED` bleiben. Sie werden nur bei konkretem fachlichem Bedarf gezielt untersucht.
- Arbeitsblöcke sollen nach Möglichkeit mit den deterministischen Skripten unter `.agents/skills/arbeitsstruktur/scripts/` erstellt, geprüft, zurückgestellt, wiederaufgenommen und abgeschlossen werden.
- Arbeitspakete müssen prüfbare Ziele und Akzeptanzkriterien besitzen. Sobald ein Implementierungs-Arbeitspaket vollständig erfüllt und erfolgreich validiert ist, erstellt der ausführende Agent standardmäßig einen eigenen Commit für genau dieses Arbeitspaket, sofern der Auftrag Commit-Erstellung nicht ausdrücklich ausschließt und die Änderungen sicher von fremden/unabhängigen Working-Tree-Änderungen isoliert werden können.
- Bei einem solchen Commit dürfen nur zum Arbeitspaket gehörende Änderungen gestaged werden. Kein `git add -A` oder vergleichbares blindes Staging bei fremden Änderungen.
- Wenn neue Erkenntnisse eine Umplanung erfordern, darf und soll die Planung angepasst werden. Grund, Auswirkung und neue gültige Richtung müssen nachvollziehbar dokumentiert werden.
"@

[void](Ensure-MarkedSection `
    -Path $agentsPath `
    -MarkerId "ARBEITSSTRUKTUR" `
    -SectionContent $agentsSection `
    -PrefixIfNew "# AGENTS")

$claudePath = Get-RootFilePath -RepositoryRoot $repo -CanonicalName "CLAUDE.md"
$claudeSection = @"
## Projektweite Agentenanweisungen

Vor jeder Arbeit in diesem Repository ist die Datei [`AGENTS.md`](./AGENTS.md) im Repository-Root zu lesen und zu befolgen.

Der Ordner `.agents/` ist wie ein `.claude/`-Ordner als projektlokaler Agenten-, Skill- und Instruktionsbereich zu behandeln. Relevante `SKILL.md`-Dateien und dort referenzierte deterministische Skripte sind bei passenden Aufgaben zu berücksichtigen.

Für die Verwaltung der Arbeitsakten ist insbesondere `.agents/skills/arbeitsstruktur/SKILL.md` maßgeblich.
"@

[void](Ensure-MarkedSection `
    -Path $claudePath `
    -MarkerId "AGENTS-UND-ARBEITSSTRUKTUR" `
    -SectionContent $claudeSection `
    -PrefixIfNew "# CLAUDE")

Write-Utf8File -NoOverwrite -Path (Join-Path $arbeitsdateien "00_STEUERUNG\CURRENT_STATE.md") -Content @"
# Current State

**Letztes Update:** $(Get-NowStamp)

## Aktueller Stand

Noch zu pflegen.

## Aktiver Arbeitsblock

Noch zu pflegen.

## Letzter relevanter Meilenstein

Noch zu pflegen.

## Offene Punkte / Blocker

Keine eingetragen.

## Nächster Schritt

Noch zu pflegen.

## Einstieg für neue Agenten

1. Diese Datei vollständig lesen.
2. Den unter „Aktiver Arbeitsblock“ genannten Pfad öffnen.
3. Dort `README.md` und `STATUS.md` lesen.
4. Anschließend nur die für den nächsten Schritt relevanten Planungs- bzw. Arbeitspaketdateien lesen.
"@

Write-Utf8File -NoOverwrite -Path (Join-Path $arbeitsdateien "00_STEUERUNG\MASTERPLAN.md") -Content @"
# Masterplan

Strategische Roadmap des Repositories.

Der Masterplan verfolgt große Arbeitsstränge und Meilensteine. Er ist kein Run-Tracker und keine detaillierte Arbeitspaketliste.
"@

Write-Utf8File -NoOverwrite -Path (Join-Path $arbeitsdateien "00_STEUERUNG\LOG_VERLAUF.md") -Content @"
# Log-Verlauf

Chronologischer repositoryweiter Verlauf.

Einträge sind kurz, append-only und enthalten Datum, Uhrzeit und UTC-Offset.
"@

Write-Utf8File -NoOverwrite -Path (Join-Path $arbeitsdateien "00_STEUERUNG\ARBEITSPROZESS.md") -Content @"
# Arbeitsprozess

## Grundmodell

1. Planung auf einem geeigneten Ausgangsstand.
2. Planungsstand ausreichend konkretisieren.
3. Umsetzung auf dem vorgesehenen Feature-Branch/Workspace.
4. Bei neuen Erkenntnissen jederzeit nachvollziehbar umplanen.
5. Arbeitspakete einzeln anhand prüfbarer Akzeptanzkriterien validieren.
6. Erfolgreich abgeschlossene Implementierungs-Arbeitspakete standardmäßig jeweils mit einem eigenen Commit abschließen.
7. Nach Gesamtabschluss/Merge den repositoryweiten Zustand und Verlauf aktualisieren.

## Arbeitsblöcke

- `10_AKTUELL/`: aktiv bearbeitet
- `20_ZURUECKGESTELLT/`: bewusst pausiert, aber nicht abgeschlossen
- `90_HISTORIE/`: abgeschlossen oder historisch

## Deterministische Verwaltung

Arbeitsblöcke nach Möglichkeit mit den Skripten unter `.agents/skills/arbeitsstruktur/scripts/` erstellen, validieren, zurückstellen, wiederaufnehmen und abschließen.

## Git-Grundsatz für Arbeitspakete

Ein vollständig erfolgreich umgesetztes und validiertes Arbeitspaket endet standardmäßig mit einem dedizierten Commit. Vor dem Commit muss geprüft werden, dass nur zum Arbeitspaket gehörige Änderungen gestaged werden. Bei nicht sicher trennbaren Fremdänderungen wird nicht automatisch committed; stattdessen wird der Blocker berichtet.
"@

Write-Utf8File -NoOverwrite -Path (Join-Path $arbeitsdateien "20_ZURUECKGESTELLT\README.md") -Content @"
# Zurückgestellte Arbeitsblöcke

Dieser Bereich enthält größere Arbeitsblöcke, die weiterhin relevant sind, aktuell aber bewusst nicht bearbeitet werden.

Sie sind nicht abgeschlossen und gehören deshalb nicht nach `90_HISTORIE`.

Für einen zurückgestellten Arbeitsblock soll aus `STATUS.md` hervorgehen:
- warum er zurückgestellt wurde,
- welcher Stand erreicht ist,
- welche Voraussetzungen für die Wiederaufnahme bestehen,
- welcher nächste Schritt bei Wiederaufnahme vorgesehen ist.

Bei Wiederaufnahme wird er deterministisch nach `10_AKTUELL` zurückgeführt.
"@

Write-Host "Arbeitsstruktur initialisiert/geprüft: $arbeitsdateien"
Write-Host "Projektanweisungen geprüft/ergänzt: $agentsPath"
Write-Host "Claude-Verweis geprüft/ergänzt: $claudePath"
