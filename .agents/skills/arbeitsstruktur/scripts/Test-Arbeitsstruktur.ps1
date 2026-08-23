[CmdletBinding()]
param(
    [string]$RepositoryRoot
)

. "$PSScriptRoot\Arbeitsstruktur.Common.ps1"

$repo = Resolve-RepositoryRoot $RepositoryRoot
$arbeitsdateien = Get-ArbeitsdateienRoot $repo

$errors = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

$agents = Get-RootFilePath -RepositoryRoot $repo -CanonicalName "AGENTS.md"
if (-not (Test-Path -LiteralPath $agents -PathType Leaf)) {
    $errors.Add("AGENTS.md fehlt im Repository-Root.")
}
else {
    $text = Get-Content -LiteralPath $agents -Raw
    if ($text -notmatch '<!-- BEGIN ARBEITSSTRUKTUR -->') {
        $errors.Add("AGENTS.md enthält den Abschnitt ARBEITSSTRUKTUR nicht.")
    }
}

$claude = Get-RootFilePath -RepositoryRoot $repo -CanonicalName "CLAUDE.md"
if (-not (Test-Path -LiteralPath $claude -PathType Leaf)) {
    $errors.Add("CLAUDE.md fehlt im Repository-Root.")
}
else {
    $text = Get-Content -LiteralPath $claude -Raw
    if ($text -notmatch '<!-- BEGIN AGENTS-UND-ARBEITSSTRUKTUR -->') {
        $errors.Add("CLAUDE.md enthält den Verweisabschnitt AGENTS-UND-ARBEITSSTRUKTUR nicht.")
    }
    if ($text -notmatch '\.agents/' -or $text -notmatch 'AGENTS\.md') {
        $errors.Add("CLAUDE.md verweist nicht ausreichend auf AGENTS.md und .agents/.")
    }
}

foreach ($relative in @(
    "00_STEUERUNG\CURRENT_STATE.md",
    "00_STEUERUNG\MASTERPLAN.md",
    "00_STEUERUNG\LOG_VERLAUF.md",
    "00_STEUERUNG\ARBEITSPROZESS.md",
    "20_ZURUECKGESTELLT\README.md"
)) {
    if (-not (Test-Path -LiteralPath (Join-Path $arbeitsdateien $relative) -PathType Leaf)) {
        $errors.Add("Pflichtdatei fehlt: ARBEITSDATEIEN\$relative")
    }
}

foreach ($relative in @("10_AKTUELL", "20_ZURUECKGESTELLT", "90_HISTORIE")) {
    if (-not (Test-Path -LiteralPath (Join-Path $arbeitsdateien $relative) -PathType Container)) {
        $errors.Add("Pflichtordner fehlt: ARBEITSDATEIEN\$relative")
    }
}

$requiredScripts = @(
    "Initialize-Arbeitsstruktur.ps1",
    "Test-Arbeitsstruktur.ps1",
    "New-Arbeitsblock.ps1",
    "Test-Arbeitsblock.ps1",
    "Defer-Arbeitsblock.ps1",
    "Resume-Arbeitsblock.ps1",
    "Promote-ArbeitsblockVerlauf.ps1",
    "Close-Arbeitsblock.ps1"
)

foreach ($script in $requiredScripts) {
    if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot $script) -PathType Leaf)) {
        $errors.Add("Skill-Skript fehlt: $script")
    }
}

Write-Host "Repository: $repo"
Write-Host "Fehler: $($errors.Count)"
Write-Host "Warnungen: $($warnings.Count)"
foreach ($e in $errors) { Write-Host "ERROR: $e" }
foreach ($w in $warnings) { Write-Host "WARN : $w" }

if ($errors.Count -gt 0) {
    throw "Arbeitsstruktur-Validierung fehlgeschlagen: $($errors.Count) Fehler."
}

[pscustomobject]@{
    Repository = $repo
    Errors = 0
    Warnings = $warnings.Count
    Valid = $true
}
