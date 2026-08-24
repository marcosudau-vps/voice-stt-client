[CmdletBinding(DefaultParameterSetName="ByName")]
param(
    [Parameter(Mandatory=$true, ParameterSetName="ByName")][string]$Name,
    [Parameter(Mandatory=$true, ParameterSetName="ByPath")][string]$Path,
    [string]$RepositoryRoot,
    [switch]$Quiet
)

. "$PSScriptRoot\Arbeitsstruktur.Common.ps1"

$repo = Resolve-RepositoryRoot $RepositoryRoot
$arbeitsdateien = Get-ArbeitsdateienRoot $repo

if ($PSCmdlet.ParameterSetName -eq "ByPath") {
    $block = (Resolve-Path -LiteralPath $Path).Path
}
else {
    $safeName = Normalize-ArbeitsblockName $Name
    # @(...) around the whole pipeline forces array context even when exactly
    # one candidate survives the filter; without it, Where-Object unwraps a
    # single match to a scalar and the .Count check below throws under
    # Set-StrictMode -Version Latest ("The property 'Count' cannot be found").
    $candidates = @(
        @(
            (Join-Path $arbeitsdateien ("10_AKTUELL\" + $safeName)),
            (Join-Path $arbeitsdateien ("20_ZURUECKGESTELLT\" + $safeName))
        ) | Where-Object { Test-Path -LiteralPath $_ -PathType Container }
    )

    if ($candidates.Count -eq 0) {
        $history = Get-ChildItem -LiteralPath (Join-Path $arbeitsdateien "90_HISTORIE") -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -eq $safeName -or $_.Name -match ("^\d{4}-\d{2}-\d{2}_" + [regex]::Escape($safeName) + "$") }
        $candidates = @($history | ForEach-Object { $_.FullName })
    }

    if ($candidates.Count -ne 1) {
        throw "Arbeitsblock konnte nicht eindeutig bestimmt werden. Treffer: $($candidates.Count)"
    }

    $block = $candidates[0]
}

$errors = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

$requiredFiles = @(
    "README.md",
    "STATUS.md",
    "VERLAUF.md",
    "PLANUNG\README.md",
    "IDEEN\README.md",
    "ARBEITSPAKETE\README.md"
)

foreach ($relative in $requiredFiles) {
    $full = Join-Path $block $relative
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) {
        $errors.Add("Pflichtdatei fehlt: $relative")
    }
}

$forbiddenDirs = @(
    "00_NORMATIV",
    "05_GRUNDLAGEN",
    "10_ANALYSE",
    "15_DRAFTS_UNGEPRUEFT",
    "20_PLANUNG",
    "30_AUSFUEHRUNG",
    "40_EVIDENCE",
    "50_TOOLS",
    "90_ZWISCHENARCHIV"
)

foreach ($dir in $forbiddenDirs) {
    if (Test-Path -LiteralPath (Join-Path $block $dir) -PathType Container) {
        $errors.Add("Altstruktur im neuen Modell nicht zulässig: $dir")
    }
}

if (Test-Path -LiteralPath (Join-Path $block "STATUS.md")) {
    try {
        $meta = Get-BlockMeta $block
        foreach ($key in @("schema","name","title","state","phase","created_at","updated_at","branch","baseline_head")) {
            if (-not $meta.ContainsKey($key) -or -not $meta[$key]) {
                $errors.Add("STATUS.md: Metadaten-Schlüssel fehlt/leer: $key")
            }
        }

        $state = $meta["state"]
        $normalizedBlock = $block.TrimEnd("\")
        if ($normalizedBlock -like "*\10_AKTUELL\*" -and $state -ne "AKTIV") {
            $errors.Add("STATUS.md state='$state', Pfad liegt aber unter 10_AKTUELL.")
        }
        if ($normalizedBlock -like "*\20_ZURUECKGESTELLT\*" -and $state -ne "ZURUECKGESTELLT") {
            $errors.Add("STATUS.md state='$state', Pfad liegt aber unter 20_ZURUECKGESTELLT.")
        }
        if ($normalizedBlock -like "*\90_HISTORIE\*" -and $state -ne "ABGESCHLOSSEN") {
            $warnings.Add("Historischer Arbeitsblock ist nicht als ABGESCHLOSSEN markiert. Bei Altbestand kann das legitim sein.")
        }
    }
    catch {
        $errors.Add($_.Exception.Message)
    }
}

$ideenReadme = Join-Path $block "IDEEN\README.md"
if (Test-Path -LiteralPath $ideenReadme) {
    $ideenText = Get-Content -LiteralPath $ideenReadme -Raw
    if ($ideenText -notmatch "AGENTENSPERRE") {
        $errors.Add("IDEEN/README.md enthält die Kennzeichnung AGENTENSPERRE nicht.")
    }
}

$planningReadme = Join-Path $block "PLANUNG\README.md"
if (Test-Path -LiteralPath $planningReadme) {
    $planningText = Get-Content -LiteralPath $planningReadme -Raw
    if ($planningText -notmatch "PLANUNGSLEITFADEN") {
        $errors.Add("PLANUNG/README.md enthält PLANUNGSLEITFADEN nicht.")
    }
    if ($planningText -notmatch "ARBEITSPAKET-STANDARD") {
        $errors.Add("PLANUNG/README.md enthält ARBEITSPAKET-STANDARD nicht.")
    }
    if ($planningText -notmatch "Akzeptanzkriterien" -or $planningText -notmatch "dedizierten Git-Commit") {
        $errors.Add("PLANUNG/README.md enthält die erwarteten AP-/Commit-Grundregeln nicht.")
    }
}

$verlaufPath = Join-Path $block "VERLAUF.md"
if (Test-Path -LiteralPath $verlaufPath) {
    $headings = Select-String -LiteralPath $verlaufPath -Pattern '^##\s+' -AllMatches
    foreach ($h in $headings) {
        if ($h.Line -notmatch '^##\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+[+-]\d{2}:\d{2}\s+–\s+.+$') {
            $warnings.Add("Nicht standardisierter Verlaufseintrag: $($h.Line)")
        }
    }
}

$wpRoot = Join-Path $block "ARBEITSPAKETE"
if (Test-Path -LiteralPath $wpRoot -PathType Container) {
    $wps = Get-ChildItem -LiteralPath $wpRoot -Directory -ErrorAction SilentlyContinue
    foreach ($wp in $wps) {
        if (-not (Test-Path -LiteralPath (Join-Path $wp.FullName "README.md"))) {
            $warnings.Add("Arbeitspaket ohne README.md: $($wp.Name)")
        }
        if (-not (Test-Path -LiteralPath (Join-Path $wp.FullName "PLAN.md"))) {
            $warnings.Add("Arbeitspaket ohne PLAN.md: $($wp.Name)")
        }

        $runs = Join-Path $wp.FullName "runs"
        if (Test-Path -LiteralPath $runs -PathType Container) {
            foreach ($run in (Get-ChildItem -LiteralPath $runs -Directory -ErrorAction SilentlyContinue)) {
                if (-not (Test-Path -LiteralPath (Join-Path $run.FullName "PROMPT.md"))) {
                    $warnings.Add("Run ohne PROMPT.md: $($wp.Name)\runs\$($run.Name)")
                }
                if (-not (Test-Path -LiteralPath (Join-Path $run.FullName "REPORT.md"))) {
                    $warnings.Add("Run ohne REPORT.md (bei laufendem Run ggf. legitim): $($wp.Name)\runs\$($run.Name)")
                }
            }
        }
    }
}

if (-not $Quiet) {
    Write-Host "Arbeitsblock: $block"
    Write-Host "Fehler: $($errors.Count)"
    Write-Host "Warnungen: $($warnings.Count)"
    foreach ($e in $errors) { Write-Host "ERROR: $e" }
    foreach ($w in $warnings) { Write-Host "WARN : $w" }
}

if ($errors.Count -gt 0) {
    throw "Arbeitsblock-Validierung fehlgeschlagen: $($errors.Count) Fehler."
}

[pscustomobject]@{
    Path = $block
    Errors = $errors.Count
    Warnings = $warnings.Count
    Valid = $true
}
