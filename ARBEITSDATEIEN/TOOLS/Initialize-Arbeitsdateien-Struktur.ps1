[CmdletBinding()]
param(
    [string]$WorkspaceRoot = "P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur-claude",
    [string]$SourceArbeitsdateien = "",
    [string]$ClientRepo = "",
    [switch]$Apply,
    [switch]$Backup,
    [switch]$MigrateLegacyDocs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($SourceArbeitsdateien)) {
    $SourceArbeitsdateien = Join-Path $WorkspaceRoot "ARBEITSDATEIEN"
}
if ([string]::IsNullOrWhiteSpace($ClientRepo)) {
    $ClientRepo = Join-Path $WorkspaceRoot "voice-stt-client"
}

$DestinationRoot = Join-Path $ClientRepo "ARBEITSDATEIEN"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Today = Get-Date -Format "yyyy-MM-dd"
$Actions = New-Object 'System.Collections.Generic.List[string]'

function Write-Section {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 78) -ForegroundColor DarkGray
    Write-Host $Text -ForegroundColor Cyan
    Write-Host ("=" * 78) -ForegroundColor DarkGray
}

function Ensure-Directory {
    param([string]$Path)
    Write-Host "[DIR ] $Path"
    if ($Apply) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Get-UniqueDestination {
    param([string]$Destination)

    if (-not (Test-Path -LiteralPath $Destination)) {
        return $Destination
    }

    $Dir = Split-Path -Parent $Destination
    $Name = [System.IO.Path]::GetFileNameWithoutExtension($Destination)
    $Ext = [System.IO.Path]::GetExtension($Destination)
    $Index = 1

    do {
        $Candidate = Join-Path $Dir ("{0}__DUPLICATE_{1:D2}{2}" -f $Name, $Index, $Ext)
        $Index++
    } while (Test-Path -LiteralPath $Candidate)

    return $Candidate
}

function Move-FileSafe {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        return
    }

    $FinalDestination = Get-UniqueDestination $Destination
    Write-Host "[MOVE] $Source" -ForegroundColor Yellow
    Write-Host "       -> $FinalDestination"
    $Actions.Add("MOVE FILE: $Source -> $FinalDestination")

    if ($Apply) {
        New-Item -ItemType Directory -Path (Split-Path -Parent $FinalDestination) -Force | Out-Null
        Move-Item -LiteralPath $Source -Destination $FinalDestination
    }
}

function Move-TreeSafe {
    param(
        [string]$SourceDirectory,
        [string]$DestinationDirectory
    )

    if (-not (Test-Path -LiteralPath $SourceDirectory -PathType Container)) {
        return
    }

    $Files = Get-ChildItem -LiteralPath $SourceDirectory -File -Recurse -Force
    foreach ($File in $Files) {
        $Relative = $File.FullName.Substring($SourceDirectory.Length).TrimStart("\")
        $Target = Join-Path $DestinationDirectory $Relative
        Move-FileSafe $File.FullName $Target
    }
}

function Write-TextFile {
    param(
        [string]$Path,
        [string]$Content
    )

    Write-Host "[WRITE] $Path" -ForegroundColor Green
    $Actions.Add("WRITE FILE: $Path")

    if ($Apply) {
        New-Item -ItemType Directory -Path (Split-Path -Parent $Path) -Force | Out-Null
        $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($Path, $Content, $Utf8NoBom)
    }
}

function Copy-FileSafe {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        return
    }

    $FinalDestination = Get-UniqueDestination $Destination
    Write-Host "[COPY] $Source" -ForegroundColor DarkYellow
    Write-Host "       -> $FinalDestination"
    $Actions.Add("COPY FILE: $Source -> $FinalDestination")

    if ($Apply) {
        New-Item -ItemType Directory -Path (Split-Path -Parent $FinalDestination) -Force | Out-Null
        Copy-Item -LiteralPath $Source -Destination $FinalDestination
    }
}

Write-Section "Preflight"

foreach ($PathToCheck in @($WorkspaceRoot, $SourceArbeitsdateien, $ClientRepo)) {
    if (-not (Test-Path -LiteralPath $PathToCheck -PathType Container)) {
        throw "Verzeichnis fehlt: $PathToCheck"
    }
}

$RepoTop = (& git -C $ClientRepo rev-parse --show-toplevel 2>$null)
if ($LASTEXITCODE -ne 0) {
    throw "ClientRepo ist kein Git-Repository: $ClientRepo"
}

Write-Host "Workspace:   $WorkspaceRoot"
Write-Host "Quelle:      $SourceArbeitsdateien"
Write-Host "Client-Repo: $ClientRepo"
Write-Host "Ziel:        $DestinationRoot"
Write-Host ("Modus:       " + $(if ($Apply) { "APPLY" } else { "DRY-RUN" }))

if ($Backup) {
    Write-Section "Backup"

    $BackupDirectory = Join-Path $WorkspaceRoot "_arbeitsdateien_backups"
    $BackupFile = Join-Path $BackupDirectory "ARBEITSDATEIEN_BEFORE_REORG_$Timestamp.zip"

    Write-Host "[BACKUP] $BackupFile" -ForegroundColor Magenta

    if ($Apply) {
        New-Item -ItemType Directory -Path $BackupDirectory -Force | Out-Null
        Compress-Archive `
            -Path (Join-Path $SourceArbeitsdateien "*") `
            -DestinationPath $BackupFile `
            -CompressionLevel Optimal
    }
}

Write-Section "Zielstruktur"

$Steuerung = Join-Path $DestinationRoot "00_STEUERUNG"
$Aktuell = Join-Path $DestinationRoot "10_AKTUELL"
$Trigger = Join-Path $Aktuell "EINHEITLICHE_TRIGGERARCHITEKTUR"
$Logging = Join-Path $Aktuell "LOGGING_OBSERVABILITY"
$Historie = Join-Path $DestinationRoot "90_HISTORIE"
$Tools = Join-Path $DestinationRoot "TOOLS"

$TopicSubdirectories = @(
    "00_NORMATIV",
    "05_GRUNDLAGEN",
    "10_ANALYSE",
    "15_DRAFTS_UNGEPRUEFT",
    "20_PLANUNG",
    "30_AUSFUEHRUNG\prompts",
    "30_AUSFUEHRUNG\runs",
    "40_EVIDENCE",
    "50_TOOLS",
    "90_ZWISCHENARCHIV"
)

foreach ($Directory in @($DestinationRoot, $Steuerung, $Aktuell, $Historie, $Tools)) {
    Ensure-Directory $Directory
}

foreach ($Topic in @($Trigger, $Logging)) {
    Ensure-Directory $Topic
    foreach ($Subdirectory in $TopicSubdirectories) {
        Ensure-Directory (Join-Path $Topic $Subdirectory)
    }
}

Ensure-Directory (Join-Path $Historie "VOR_NEUEM_ARBEITSSYSTEM")

Write-Section "Root-Dateien einsortieren"

Move-FileSafe `
    (Join-Path $SourceArbeitsdateien "LOG_VERLAUF.md") `
    (Join-Path $Steuerung "LOG_VERLAUF.md")

Move-FileSafe `
    (Join-Path $SourceArbeitsdateien "ZIELBILD_TRIGGERARCHITEKTUR.md") `
    (Join-Path $Trigger "00_NORMATIV\ZIELBILD_TRIGGERARCHITEKTUR.md")

Move-FileSafe `
    (Join-Path $SourceArbeitsdateien "README.md") `
    (Join-Path $Historie "VOR_NEUEM_ARBEITSSYSTEM\README_ARBEITSDATEIEN_VOR_UMSTELLUNG.md")

Write-Section "Aktuelles Thema: Einheitliche Triggerarchitektur"

Move-TreeSafe `
    (Join-Path $SourceArbeitsdateien "AP_THEMA_EINHEITLICHE_TRIGGERARCHITEKTUR\planung_migration") `
    (Join-Path $Trigger "20_PLANUNG\planung_migration")

$OldPrompts = Join-Path $SourceArbeitsdateien "Implementierungsdateien\prompts"

if (Test-Path -LiteralPath $OldPrompts -PathType Container) {
    Get-ChildItem -LiteralPath $OldPrompts -File | ForEach-Object {
        if ($_.Name -match '^(001|002|003|004|005)_') {
            Move-FileSafe `
                $_.FullName `
                (Join-Path $Trigger "30_AUSFUEHRUNG\prompts\LEGACY_NUMMERIERT\$($_.Name)")
        }
    }
}

Move-TreeSafe `
    (Join-Path $SourceArbeitsdateien "Implementierungsdateien\claude_zwischenstaende") `
    (Join-Path $Trigger "90_ZWISCHENARCHIV\CLAUDE_SNAPSHOTS")

$ModelRoot = Join-Path `
    $SourceArbeitsdateien `
    "Implementierungsdateien\VonModelErstellt\einheitliche-triggerarchitektur"

Move-TreeSafe `
    (Join-Path $ModelRoot "code-architektur-baseline") `
    (Join-Path $Trigger "10_ANALYSE\CODE_ARCHITEKTUR_BASELINE")

Move-TreeSafe `
    (Join-Path $ModelRoot "evidence") `
    (Join-Path $Trigger "40_EVIDENCE\VOR_NEUEM_RUN_SYSTEM")

foreach ($Name in @(
    "CONTRACTS.md",
    "DECISIONS.md",
    "DOKUMENTATIONSAUDIT.md",
    "PLAN.md",
    "REPORT.md",
    "STATUS.md",
    "VALIDATION.md"
)) {
    Move-FileSafe `
        (Join-Path $ModelRoot $Name) `
        (Join-Path $Trigger "10_ANALYSE\VORHERIGER_AGENTENSTAND_UND_AUDIT\$Name")
}

Write-Section "Aktuelles Thema: Logging / Observability"

$OldLogging = Join-Path $SourceArbeitsdateien "AP_THEMA_LOGGING"

Move-FileSafe `
    (Join-Path $OldLogging "AGENTS.md") `
    (Join-Path $Logging "AGENTS.md")

Move-FileSafe `
    (Join-Path $OldLogging "START_HIER.md") `
    (Join-Path $Logging "90_ZWISCHENARCHIV\OBS000_BOOTSTRAP\START_HIER.md")

Move-FileSafe `
    (Join-Path $OldLogging "PAKETMANIFEST.md") `
    (Join-Path $Logging "90_ZWISCHENARCHIV\OBS000_BOOTSTRAP\PAKETMANIFEST.md")

Move-TreeSafe `
    (Join-Path $OldLogging "00_NORMATIV") `
    (Join-Path $Logging "00_NORMATIV")

Move-TreeSafe `
    (Join-Path $OldLogging "00_GRUNDLAGEN") `
    (Join-Path $Logging "05_GRUNDLAGEN")

Move-TreeSafe `
    (Join-Path $OldLogging "10_ANALYSE") `
    (Join-Path $Logging "10_ANALYSE")

Move-FileSafe `
    (Join-Path $OldLogging "05_DRAFTS_UNGEPRUEFT\ErsterEntwurf_Logging.md") `
    (Join-Path $Logging "15_DRAFTS_UNGEPRUEFT\ErsterEntwurf_Logging.md")

Move-TreeSafe `
    (Join-Path $OldLogging "05_DRAFTS_UNGEPRUEFT\LOGGING_GESAMTPLAN") `
    (Join-Path $Logging "90_ZWISCHENARCHIV\OBS000_PRE_FREEZE_DRAFT_PLAN")

Move-TreeSafe `
    (Join-Path $OldLogging "20_PLANUNG\LOGGING_GESAMTPLAN") `
    (Join-Path $Logging "20_PLANUNG\LOGGING_GESAMTPLAN")

foreach ($Name in @(
    "LOGGING_V1_ABGRENZUNG_ENTWURF.md",
    "LOGGING_ZIELBILD_ARCHITEKTUR_GESAMTSPEZIFIKATION_ENTWURF.md"
)) {
    Move-FileSafe `
        (Join-Path $OldLogging "20_PLANUNG\$Name") `
        (Join-Path $Logging "90_ZWISCHENARCHIV\OBS000_PRE_FREEZE_DUPLIKATE\$Name")
}

Move-TreeSafe `
    (Join-Path $OldLogging "30_AUSFUEHRUNG") `
    (Join-Path $Logging "30_AUSFUEHRUNG")

Move-TreeSafe `
    (Join-Path $OldLogging "40_EVIDENCE") `
    (Join-Path $Logging "40_EVIDENCE")

Move-TreeSafe `
    (Join-Path $OldLogging "TOOLS") `
    (Join-Path $Logging "50_TOOLS")

Move-TreeSafe `
    (Join-Path $OldLogging "90_ARCHIV") `
    (Join-Path $Logging "90_ZWISCHENARCHIV\OBS000_BOOTSTRAP_ARCHIVE")

if (Test-Path -LiteralPath $OldPrompts -PathType Container) {
    Get-ChildItem -LiteralPath $OldPrompts -File | ForEach-Object {
        if ($_.Name -match '^(006|007)_') {
            Move-FileSafe `
                $_.FullName `
                (Join-Path $Logging "30_AUSFUEHRUNG\prompts\LEGACY_NUMMERIERT\$($_.Name)")
        }
    }
}

if ($MigrateLegacyDocs) {
    Write-Section "Historische Arbeitsakten aus docs"

    $Docs = Join-Path $ClientRepo "docs"

    if (Test-Path -LiteralPath $Docs -PathType Container) {
        Write-Host "Gefundene datierte Arbeitsordner unter docs:" -ForegroundColor DarkCyan
        $DatedDocDirectories = Get-ChildItem -LiteralPath $Docs -Directory | Where-Object {
            $_.Name -match '^\d{4}-\d{2}-\d{2}_'
        }
        if ($DatedDocDirectories.Count -eq 0) {
            Write-Warning "Keine datierten Arbeitsordner unter docs gefunden."
        } else {
            foreach ($DatedDirectory in $DatedDocDirectories) {
                Write-Host ("  - " + $DatedDirectory.Name)
            }
        }
    }

    $LegacyTarget = Join-Path $Historie "VOR_NEUEM_ARBEITSSYSTEM"

    if (-not (Test-Path -LiteralPath $Docs -PathType Container)) {
        throw "docs-Verzeichnis fehlt: $Docs"
    }

    Get-ChildItem -LiteralPath $Docs -Directory | Where-Object {
        $_.Name -match '^\d{4}-\d{2}-\d{2}_'
    } | ForEach-Object {
        Move-TreeSafe $_.FullName (Join-Path $LegacyTarget $_.Name)
    }

    foreach ($DirectoryName in @(".archive", "evaluations", "work-packages")) {
        Move-TreeSafe `
            (Join-Path $Docs $DirectoryName) `
            (Join-Path $LegacyTarget $DirectoryName)
    }

    foreach ($FileName in @(
        "ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md",
        "IMPLEMENTATION_ROADMAP.md"
    )) {
        Move-FileSafe `
            (Join-Path $Docs $FileName) `
            (Join-Path $LegacyTarget $FileName)
    }
}

Write-Section "Steuerungsdateien erzeugen"

$RootReadme = @'
# ARBEITSDATEIEN

Dieser Bereich enthaelt die aktive Arbeitssteuerung und die vollstaendige
Entwicklungshistorie des Projekts.

- 00_STEUERUNG: aktueller Gesamtstand und Arbeitsverlauf.
- 10_AKTUELL: vollstaendige Arbeitsakten laufender Themen.
- 90_HISTORIE: abgeschlossene Arbeitszyklen und Altbestand.
- TOOLS: Organisations- und Archivierungsskripte.

docs/ enthaelt die dauerhafte Produktdokumentation.

Aktive Themen werden nach Abschluss als zusammenhaengende Arbeitsakte unter
90_HISTORIE/YYYY-MM-DD_<THEMA>/ archiviert.
'@

$RootAgents = @'
# AGENTS.md - ARBEITSDATEIEN

## Vor jedem neuen Run

1. 00_STEUERUNG/CURRENT_STATE.md
2. 00_STEUERUNG/MASTERPLAN.md
3. README bzw. AGENTS des betroffenen Themas
4. aktives Work Package
5. konkreten Prompt

## Sessionregel

Ein Agent-Run = eine Session.

Nur ein noch nicht abgeschlossener Run darf nach einem Usage-Reset in
derselben Session fortgesetzt werden. Review bzw. Gate eines abgeschlossenen
Runs startet in einer frischen Session.

## Ablage

- Soll/Freigabe: 00_NORMATIV
- Grundlagen: 05_GRUNDLAGEN
- Analyse: 10_ANALYSE
- ungepruefte Entwuerfe: 15_DRAFTS_UNGEPRUEFT
- Planung: 20_PLANUNG
- Prompts/Runs: 30_AUSFUEHRUNG
- Evidence: 40_EVIDENCE
- Tools: 50_TOOLS
- abgeloeste Zwischenartefakte: 90_ZWISCHENARCHIV

Nach jedem relevanten Run oder Gate genau einen Meilensteineintrag in
00_STEUERUNG/LOG_VERLAUF.md ergaenzen.

Commit, Push, Merge, Rebase, Tag oder PR nur bei ausdruecklicher Freigabe.
'@

$CurrentState = @'
# CURRENT STATE

## Logging / Observability

- OBS-000: PASS
- OBS-010: READY FOR IMPLEMENTATION
- OBS-020: READY FOR IMPLEMENTATION
- Naechster technischer Schritt: OBS-010

## Einheitliche Triggerarchitektur

- Zielbild und Voranalysen vorhanden.
- Umsetzung wartet auf die vorgeschaltete Observability Foundation.

## Aktueller organisatorischer Schritt

- ARBEITSDATEIEN in voice-stt-client integrieren.
- gemeinsamen Git-Baseline-Commit herstellen.
- danach OBS-010 starten.
'@

$CurrentState = $CurrentState + "`r`n**Stand:** $Today`r`n"

$Masterplan = @'
# MASTERPLAN

Aktuelle Reihenfolge:

1. Logging / Observability Foundation
   - OBS-010
   - OBS-020
   - OBS-030
   - OBS-040
   - OBS-050
   - OBS-060
2. Einheitliche Triggerarchitektur
3. Logging / Observability Post-Migration
   - OBS-100 ff.
'@

$OpenPoints = @'
# OFFENE PUNKTE - globale Inbox

Neue, noch keinem Work Package zugeordnete Themen zunaechst hier erfassen.

Regel:

Fund -> Blocker des aktiven Gates?
- JA: in das aktive Work Package aufnehmen.
- NEIN: spaeterem Work Package oder der Inbox zuordnen.
'@

$Process = @'
# ARBEITSPROZESS

Standardablauf:

Soll / Entscheidung
-> Work Package READY
-> Agent Run
-> Tests / Evidence
-> frischer Review-Run
-> Gate PASS
-> naechstes Work Package

Abgeschlossene Themen werden gemeinsam mit einem Snapshot der
Steuerungsdateien unter 90_HISTORIE/YYYY-MM-DD_<THEMA>/ archiviert.
'@

$HistoryReadme = @'
# 90_HISTORIE

Hier liegen abgeschlossene Arbeitszyklen.

Namenskonvention:

YYYY-MM-DD_<THEMA_ODER_SCHLAGWORT>/

VOR_NEUEM_ARBEITSSYSTEM enthaelt aeltere Arbeitsakten aus der Zeit vor
Einfuehrung des standardisierten Workstream-, Work-Package- und Run-Systems.
'@

$LegacyReadme = @'
# VOR_NEUEM_ARBEITSSYSTEM

Hier liegen Arbeits-, Planungs-, Pruef- und Abnahmeunterlagen aus der Zeit vor
Einfuehrung des neuen ARBEITSDATEIEN-Systems.

Historische Inhalte werden nur verschoben bzw. einsortiert, nicht inhaltlich
modernisiert.
'@

$TriggerReadme = @'
# Einheitliche Triggerarchitektur

Aktive Arbeitsakte der serverseitigen Triggerarchitektur.

- Normatives Ziel: 00_NORMATIV
- Analysen: 10_ANALYSE
- Planung: 20_PLANUNG
'@

$LoggingReadme = @'
# Logging / Observability

Aktive Arbeitsakte des Logging- und Observability-Workstreams.

OBS-000 ist abgeschlossen.
Eingefrorene Vertraege: 00_NORMATIV
Aktiver Gesamtplan: 20_PLANUNG/LOGGING_GESAMTPLAN
'@

Write-TextFile (Join-Path $DestinationRoot "README.md") $RootReadme
Write-TextFile (Join-Path $DestinationRoot "AGENTS.md") $RootAgents
Write-TextFile (Join-Path $Steuerung "CURRENT_STATE.md") $CurrentState
Write-TextFile (Join-Path $Steuerung "MASTERPLAN.md") $Masterplan
Write-TextFile (Join-Path $Steuerung "OFFENE_PUNKTE.md") $OpenPoints
Write-TextFile (Join-Path $Steuerung "ARBEITSPROZESS.md") $Process
Write-TextFile (Join-Path $Historie "README.md") $HistoryReadme
Write-TextFile (Join-Path $Historie "VOR_NEUEM_ARBEITSSYSTEM\README.md") $LegacyReadme
Write-TextFile (Join-Path $Trigger "README.md") $TriggerReadme
Write-TextFile (Join-Path $Logging "README.md") $LoggingReadme

if ($MyInvocation.MyCommand.Path -and (Test-Path -LiteralPath $MyInvocation.MyCommand.Path)) {
    Copy-FileSafe `
        $MyInvocation.MyCommand.Path `
        (Join-Path $Tools "Initialize-Arbeitsdateien-Struktur.ps1")

    $ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
    $CloseWorkCycleSource = Join-Path $ScriptDirectory "Close-WorkCycle.ps1"

    if (Test-Path -LiteralPath $CloseWorkCycleSource -PathType Leaf) {
        Copy-FileSafe `
            $CloseWorkCycleSource `
            (Join-Path $Tools "Close-WorkCycle.ps1")
    } else {
        Write-Warning "Close-WorkCycle.ps1 liegt nicht neben dem Initialisierungsskript und wird daher nicht nach ARBEITSDATEIEN\TOOLS kopiert."
    }
}

Write-Section "Abschlusspruefung"

$ReportPath = Join-Path $Steuerung "UMSTELLUNGSREPORT_$Timestamp.md"
$Leftovers = @()

if (Test-Path -LiteralPath $SourceArbeitsdateien) {
    $Leftovers = Get-ChildItem `
        -LiteralPath $SourceArbeitsdateien `
        -File `
        -Recurse `
        -Force |
        Select-Object -ExpandProperty FullName
}

if ($Apply) {
    $Lines = New-Object 'System.Collections.Generic.List[string]'
    $Lines.Add("# Umstellungsreport")
    $Lines.Add("")
    $Lines.Add("Zeit: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
    $Lines.Add("")
    $Lines.Add("## Aktionen")

    foreach ($Action in $Actions) {
        $Lines.Add("- $Action")
    }

    $Lines.Add("")
    $Lines.Add("## Nicht einsortierte Quelldateien")

    if ($Leftovers.Count -eq 0) {
        $Lines.Add("- Keine.")
    } else {
        foreach ($Leftover in $Leftovers) {
            $Lines.Add("- $Leftover")
        }
    }

    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines($ReportPath, $Lines, $Utf8NoBom)

    Write-Host "Report: $ReportPath" -ForegroundColor Green
} else {
    Write-Host "DRY-RUN: Keine Aenderungen vorgenommen." -ForegroundColor Green
}

Write-Section "Git-Status"
& git -C $ClientRepo status --short

if ($Apply) {
    Write-Host "Umstellung abgeschlossen. Nichts wurde gestaged oder committed." -ForegroundColor Cyan
} else {
    Write-Host "Dry-Run abgeschlossen. Fuer echte Umstellung mit -Apply starten." -ForegroundColor Cyan
}
