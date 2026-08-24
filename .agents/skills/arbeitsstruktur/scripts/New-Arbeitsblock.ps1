[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Name,
    [string]$Title,
    [string]$Purpose = "Noch zu konkretisieren.",
    [string]$RepositoryRoot
)

. "$PSScriptRoot\Arbeitsstruktur.Common.ps1"

$repo = Resolve-RepositoryRoot $RepositoryRoot
$arbeitsdateien = Get-ArbeitsdateienRoot $repo
$safeName = Normalize-ArbeitsblockName $Name
if (-not $Title) { $Title = $safeName.Replace("_", " ") }

Ensure-Directory (Join-Path $arbeitsdateien "10_AKTUELL")
Ensure-Directory (Join-Path $arbeitsdateien "20_ZURUECKGESTELLT")
Ensure-Directory (Join-Path $arbeitsdateien "90_HISTORIE")

$block = Join-Path $arbeitsdateien ("10_AKTUELL\" + $safeName)
$deferred = Join-Path $arbeitsdateien ("20_ZURUECKGESTELLT\" + $safeName)

Assert-TargetDoesNotExist $block
Assert-TargetDoesNotExist $deferred

$historyCollision = Get-ChildItem -LiteralPath (Join-Path $arbeitsdateien "90_HISTORIE") -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq $safeName -or $_.Name -match ("^\d{4}-\d{2}-\d{2}_" + [regex]::Escape($safeName) + "$") }

if ($historyCollision) {
    throw "Ein gleichnamiger Arbeitsblock existiert bereits in 90_HISTORIE. Bitte bewusst einen neuen Namen wählen."
}

Ensure-Directory $block
Ensure-Directory (Join-Path $block "PLANUNG")
Ensure-Directory (Join-Path $block "IDEEN")
Ensure-Directory (Join-Path $block "ARBEITSPAKETE")

$now = Get-NowStamp
$branch = Get-GitBranch $repo
$head = Get-GitHead $repo

Write-Utf8File -Path (Join-Path $block "README.md") -Content @"
# $Title

**Arbeitsblock:** `$safeName`  
**Erstellt:** $now  
**Ausgangsbranch:** `$branch`  
**Ausgangs-HEAD:** `$head`

## Zweck

$Purpose

## Einstieg

1. `STATUS.md`
2. `PLANUNG/README.md`
3. relevante Planungsunterlagen
4. bei Umsetzung das aktive Arbeitspaket

`IDEEN/` ist kein Projektwissen und darf nur bei explizitem Auftrag gelesen werden.
"@

Write-Utf8File -Path (Join-Path $block "STATUS.md") -Content @"
# Status – $Title

<!-- ARBEITSBLOCK-META
schema: 1
name: $safeName
title: $Title
state: AKTIV
phase: PLANUNG
created_at: $now
updated_at: $now
branch: $branch
baseline_head: $head
-->

**Status:** AKTIV  
**Phase:** PLANUNG  
**Branch:** `$branch`

## Aktueller Stand

Noch zu pflegen.

## Aktive Arbeitspakete

Keine eingetragen.

## Abgeschlossene Arbeitspakete

Keine eingetragen.

## Offene Punkte / Blocker

Keine eingetragen.

## Nächster Schritt

Planung gemäß `PLANUNG/README.md` beginnen bzw. fortsetzen.
"@

Write-Utf8File -Path (Join-Path $block "VERLAUF.md") -Content "# Verlauf – $Title`r`n"

Write-Utf8File -Path (Join-Path $block "PLANUNG\README.md") -Content @"
# Planung

<!-- PLANUNGSLEITFADEN -->
<!-- ARBEITSPAKET-STANDARD -->

Diese Datei beschreibt die Standardlogik der Planung für diesen Arbeitsblock. Sie ist Orientierung und Qualitätsmaßstab, aber kein starrer Freigabeprozess. Neue Erkenntnisse dürfen jederzeit dazu führen, frühere Planungsschritte erneut zu bearbeiten.

## Empfohlener Planungsablauf

1. **Zielbild**
   - Was soll am Ende fachlich und technisch gelten?
   - Welche bisherigen Verantwortlichkeiten oder Abläufe sollen sich ändern?

2. **Ist-Analyse**
   - Wie funktioniert das System heute tatsächlich?
   - Welche Komponenten, Repositories, Schnittstellen und Abhängigkeiten sind betroffen?
   - Welche Annahmen sind belegt und welche noch offen?

3. **Gap-/Auswirkungsanalyse**
   - Was unterscheidet Ist und Ziel?
   - Welche Risiken, Migrationen, Kompatibilitätsfragen oder Übergangszustände entstehen?

4. **Entscheidungen**
   - Welche Architektur-, Zuständigkeits- und Verhaltensentscheidungen müssen verbindlich getroffen werden?
   - Offene Alternativen dürfen dokumentiert werden; ungeprüfte freie Gedanken gehören dagegen nach `IDEEN/`.

5. **Konkretisierung**
   - Abläufe, Datenflüsse, Verträge, Fehlerfälle, Reihenfolgen und Abhängigkeiten so weit klären, dass die Umsetzung sicher zerlegt werden kann.

6. **Arbeitspaket-Dekomposition**
   - Umsetzung in kleine, agentengerechte und einzeln prüfbare Arbeitspakete zerlegen.
   - Ein Arbeitspaket soll einen klaren Endzustand besitzen und möglichst unabhängig validierbar sein.

7. **Implementierungsplan**
   - Arbeitspakete in eine sinnvolle Reihenfolge bringen.
   - Abhängigkeiten und Übergaben sichtbar machen.
   - Für jedes Arbeitspaket Ziele, Scope und Akzeptanzkriterien festlegen.

8. **Umsetzungsbereitschaft**
   - Prüfen, ob die nächsten Arbeitspakete ausreichend konkret sind.
   - Es ist nicht erforderlich, jede spätere Detailfrage vor Beginn der Umsetzung endgültig zu lösen.
   - Bei neuen Erkenntnissen darf während der Implementierung jederzeit zur Analyse/Planung zurückgekehrt werden.

---

## Standard für ein Arbeitspaket

Ein Implementierungs-Arbeitspaket soll mindestens enthalten:

1. **ID und Titel**
2. **Ziel / gewünschter Endzustand**
3. **Scope**
4. **Nicht-Ziele**, falls zur Abgrenzung nötig
5. **Voraussetzungen / Abhängigkeiten**
6. **Betroffene Bereiche oder Repositories**, soweit bekannt
7. **Umsetzungsauftrag**
8. **Prüfbare Akzeptanzkriterien**
9. **Konkrete Validierung**
10. **Abschluss-/Commit-Regel**

### Anforderungen an Ziele und Akzeptanzkriterien

Akzeptanzkriterien müssen so formuliert sein, dass ein Agent am Ende belastbar `PASS` oder `FAIL/BLOCKED` feststellen kann.

Schlecht:

> Logging verbessern.

Besser:

> Alle drei Trigger-Einstiegspfade erzeugen einen strukturierten Log-Eintrag mit Session-ID und Trigger-Ursprung; die angegebenen Tests laufen ohne Fehler.

Wo sinnvoll, gehören zu den Kriterien konkrete Befehle, Tests, Build-Schritte, beobachtbare Zustände oder reproduzierbare Prüfungen.

### Abschluss und Commit

Ein Implementierungs-Arbeitspaket gilt erst als erfolgreich abgeschlossen, wenn:
- alle verpflichtenden Ziele umgesetzt sind,
- alle Akzeptanzkriterien erfüllt sind,
- die vorgesehene Validierung erfolgreich durchlaufen wurde,
- keine bekannten Blocker offen sind.

**Danach erstellt der ausführende Agent standardmäßig automatisch einen dedizierten Git-Commit für dieses Arbeitspaket**, sofern der konkrete Auftrag dies nicht ausdrücklich ausschließt.

Dabei gilt:
- nur zum Arbeitspaket gehörende Änderungen stagen,
- keine fremden/unabhängigen Working-Tree-Änderungen mitnehmen,
- kein blindes `git add -A`,
- Commit-SHA im Report bzw. Arbeitspaket dokumentieren,
- wenn eine sichere Trennung der Änderungen nicht möglich ist: **nicht committen**, sondern den Blocker melden.

Bei mehreren Repositories erfolgt die Commit-Erstellung repositoryweise und nur dort, wo die jeweiligen Änderungen erfolgreich validiert und sicher isoliert sind.

---

## Empfohlener Aufbau eines Implementierungsplans

```markdown
# Implementierungsplan

## 1. Ziel und Ausgangslage
Kurzer Überblick über Zielzustand und relevante Ist-Situation.

## 2. Verbindliche Entscheidungen
Nur bereits getroffene Entscheidungen, die für die Umsetzung gelten.

## 3. Arbeitspaket-Übersicht

| AP | Ziel | Betroffener Bereich / Repo | Abhängigkeit | Status |
|---|---|---|---|---|
| AP-C010 | ... | Client | - | PLANNED |
| AP-S010 | ... | Server | AP-C010 / Contract X | PLANNED |

## 4. Arbeitspakete

### AP-C010 – Beispiel
**Ziel:** Eindeutiger, prüfbarer Endzustand.

**Scope:**
- ...

**Nicht-Ziele:**
- ...

**Voraussetzungen / Abhängigkeiten:**
- ...

**Umsetzungsauftrag:**
- ...

**Akzeptanzkriterien:**
- [ ] Kriterium 1 ist reproduzierbar erfüllt.
- [ ] Test/Befehl X endet erfolgreich.
- [ ] Kein Regressionstest aus Bereich Y schlägt fehl.

**Validierung:**
- `pytest ...`
- Build/Compile ...
- ggf. manueller Smoke-Test ...

**Abschluss:**
Bei vollständigem PASS dedizierten Commit für dieses AP erstellen und SHA dokumentieren.
```

Der Implementierungsplan darf repositoryübergreifende Analysen und Arbeitspakete enthalten, wenn dies für die Planung sinnvoll ist. Es gibt keine Pflicht, Planungsunterlagen künstlich nach Repositorygrenzen zu trennen.
"@

Write-Utf8File -Path (Join-Path $block "IDEEN\README.md") -Content @"
# IDEEN

## AGENTENSPERRE

Dieser Ordner ist ein freier Denkraum.

Alle Inhalte sind:
- ungeprüft,
- nicht beschlossen,
- nicht normativ,
- nicht Teil der aktuellen Planung,
- nicht als Quelle für Analyse, Recherche, Planung, Entscheidung oder Implementierung zu verwenden.

Agenten dürfen Dateien in diesem Ordner nur lesen oder berücksichtigen, wenn ein Auftrag ausdrücklich auf eine konkrete Datei in `IDEEN/` verweist.

Eine Idee wird erst projektwirksam, wenn sie bewusst geprüft und in eine reguläre Planungs- oder Arbeitspaketdatei übernommen wurde.
"@

Write-Utf8File -Path (Join-Path $block "ARBEITSPAKETE\README.md") -Content @"
# Arbeitspakete

Arbeitspakete sind die agentengerechten Umsetzungseinheiten dieses Arbeitsblocks.

Die verbindlichen Grundregeln für Aufbau, prüfbare Ziele, Akzeptanzkriterien, Validierung und Commit-Verhalten stehen in `../PLANUNG/README.md`.

## Empfohlene Struktur

```text
AP-.../
├── README.md
├── PLAN.md
└── runs/
    └── 01_IMPLEMENTATION/
        ├── PROMPT.md
        ├── REPORT.md
        └── evidence/
```

`runs/` wird erst mit dem ersten tatsächlichen Run angelegt. Weitere Runs können danach ohne Strukturwechsel ergänzt werden.

Abgeschlossene Arbeitspakete bleiben an ihrem Platz und werden über ihren Status als abgeschlossen gekennzeichnet.
"@

$body = "- Arbeitsblock erstellt.`r`n- Ausgangsbranch: $branch`r`n- Ausgangs-HEAD: $head"
Add-BlockLifecycleLogEntry -RepositoryRoot $repo -BlockPath $block -Title "$safeName – Arbeitsblock erstellt" -Body $body | Out-Null

Write-Host "Arbeitsblock erstellt: $block"
