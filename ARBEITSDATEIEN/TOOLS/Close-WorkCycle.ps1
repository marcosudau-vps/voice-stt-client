[CmdletBinding()]
param(
    [string]$ArbeitsdateienRoot = "P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur-claude\voice-stt-client\ARBEITSDATEIEN",
    [Parameter(Mandatory = $true)]
    [string]$Name,
    [Parameter(Mandatory = $true)]
    [string[]]$Topics,
    [string]$ArchiveDate = (Get-Date -Format "yyyy-MM-dd"),
    [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function ConvertTo-SafeName {
    param([string]$Text)
    $Result = $Text.ToUpperInvariant() -replace '[^A-Z0-9_-]+', '_'
    $Result = $Result -replace '_+', '_'
    return $Result.Trim('_')
}

$CurrentRoot = Join-Path $ArbeitsdateienRoot "10_AKTUELL"
$HistoryRoot = Join-Path $ArbeitsdateienRoot "90_HISTORIE"
$ControlRoot = Join-Path $ArbeitsdateienRoot "00_STEUERUNG"

if (-not (Test-Path -LiteralPath $CurrentRoot -PathType Container)) {
    throw "10_AKTUELL fehlt: $CurrentRoot"
}
if (-not (Test-Path -LiteralPath $HistoryRoot -PathType Container)) {
    throw "90_HISTORIE fehlt: $HistoryRoot"
}

$ArchiveName = "{0}_{1}" -f $ArchiveDate, (ConvertTo-SafeName $Name)
$ArchiveRoot = Join-Path $HistoryRoot $ArchiveName

if (Test-Path -LiteralPath $ArchiveRoot) {
    throw "Historienordner existiert bereits: $ArchiveRoot"
}

$ResolvedTopics = @()

foreach ($Topic in $Topics) {
    $Path = Join-Path $CurrentRoot $Topic

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        throw "Aktuelles Thema nicht gefunden: $Path"
    }

    $ResolvedTopics += New-Object PSObject -Property @{
        Name = $Topic
        Path = $Path
    }
}

Write-Host "Arbeitszyklus abschliessen" -ForegroundColor Cyan
Write-Host "Archiv: $ArchiveRoot"
Write-Host ("Modus: " + $(if ($Apply) { "APPLY" } else { "DRY-RUN" }))

if ($Apply) {
    New-Item -ItemType Directory -Path $ArchiveRoot -Force | Out-Null
}

foreach ($File in @(
    "CURRENT_STATE.md",
    "MASTERPLAN.md",
    "OFFENE_PUNKTE.md",
    "ARBEITSPROZESS.md"
)) {
    $Source = Join-Path $ControlRoot $File

    if (Test-Path -LiteralPath $Source -PathType Leaf) {
        $Destination = Join-Path $ArchiveRoot ("STEUERUNG_" + $File)
        Write-Host "COPY $Source -> $Destination" -ForegroundColor Yellow

        if ($Apply) {
            Copy-Item -LiteralPath $Source -Destination $Destination
        }
    }
}

$LogPath = Join-Path $ControlRoot "LOG_VERLAUF.md"

if (Test-Path -LiteralPath $LogPath -PathType Leaf) {
    $ArchivedLog = Join-Path $ArchiveRoot "LOG_VERLAUF.md"
    Write-Host "MOVE $LogPath -> $ArchivedLog" -ForegroundColor Yellow

    if ($Apply) {
        Move-Item -LiteralPath $LogPath -Destination $ArchivedLog
    }
}

foreach ($Topic in $ResolvedTopics) {
    $Destination = Join-Path $ArchiveRoot $Topic.Name
    Write-Host "MOVE $($Topic.Path) -> $Destination" -ForegroundColor Yellow

    if ($Apply) {
        Move-Item -LiteralPath $Topic.Path -Destination $Destination
    }
}

if ($Apply) {
    $TopicLines = @()

    foreach ($Topic in $Topics) {
        $TopicLines += "- $Topic"
    }

    $ArchiveReadme = @'
# WORK CYCLE ARCHIVE

This directory contains the complete working record of a completed work cycle.

Archived topics:
'@

    $ArchiveReadme = $ArchiveReadme + "`r`n`r`n" + ($TopicLines -join "`r`n")
    $ArchiveReadme = $ArchiveReadme + "`r`n`r`nAbgeschlossen: $ArchiveDate`r`n"

    $NewLog = @'
# Arbeitsverlauf

## Vorgaenger

Der vorherige Arbeitszyklus wurde archiviert unter:
'@

    $NewLog = $NewLog + "`r`n`r`n90_HISTORIE/$ArchiveName/`r`n"
    $NewLog = $NewLog + "`r`nBeginn dieses Arbeitszyklus: $(Get-Date -Format 'yyyy-MM-dd')`r`n"

    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

    [System.IO.File]::WriteAllText(
        (Join-Path $ArchiveRoot "README.md"),
        $ArchiveReadme,
        $Utf8NoBom
    )

    [System.IO.File]::WriteAllText(
        $LogPath,
        $NewLog,
        $Utf8NoBom
    )
}

if ($Apply) {
    Write-Host "Archivierung abgeschlossen." -ForegroundColor Green
    Write-Host "CURRENT_STATE.md und MASTERPLAN.md danach bewusst aktualisieren." -ForegroundColor Yellow
} else {
    Write-Host "DRY-RUN: Keine Aenderungen vorgenommen." -ForegroundColor Green
}
