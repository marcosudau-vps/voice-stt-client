[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$BlockPath,
    [string]$RepositoryRoot
)

. "$PSScriptRoot\Arbeitsstruktur.Common.ps1"

$repo = Resolve-RepositoryRoot $RepositoryRoot
$block = (Resolve-Path -LiteralPath $BlockPath).Path
$localLog = Join-Path $block "VERLAUF.md"
$globalLog = Join-Path (Get-ArbeitsdateienRoot $repo) "00_STEUERUNG\LOG_VERLAUF.md"

if (-not (Test-Path -LiteralPath $localLog)) {
    throw "Lokaler Verlauf fehlt: $localLog"
}
if (-not (Test-Path -LiteralPath $globalLog)) {
    Write-Utf8File -Path $globalLog -Content "# Log-Verlauf`r`n"
}

$localEntries = @(Get-StandardLogEntries $localLog)
if ($localEntries.Count -eq 0) {
    throw "Keine standardisierten Verlaufseinträge in $localLog gefunden."
}

function Get-EntryHashSet {
    param([object[]]$Entries)
    $set = @{}
    foreach ($entry in $Entries) {
        $set[(Get-TextHash $entry.Text)] = $true
    }
    return $set
}

$globalEntries = @(Get-StandardLogEntries $globalLog)
$globalHashes = Get-EntryHashSet $globalEntries
$missing = @($localEntries | Where-Object { -not $globalHashes.ContainsKey((Get-TextHash $_.Text)) } | Sort-Object Timestamp)

if ($missing.Count -eq 0) {
    Write-Host "Keine neuen Verlaufseinträge zu promoten."
    return
}

$lines = New-Object System.Collections.Generic.List[string]
foreach ($line in (Get-Content -LiteralPath $globalLog)) {
    $lines.Add([string]$line)
}

foreach ($entry in $missing) {
    $insertAt = $lines.Count
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $m = [regex]::Match($lines[$i], '^##\s+(?<ts>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+[+-]\d{2}:\d{2})\s+–\s+.+$')
        if ($m.Success) {
            $existingTs = [DateTimeOffset]::ParseExact(
                $m.Groups["ts"].Value,
                "yyyy-MM-dd HH:mm:ss zzz",
                [Globalization.CultureInfo]::InvariantCulture
            )
            if ($existingTs -gt $entry.Timestamp) {
                $insertAt = $i
                break
            }
        }
    }

    $entryLines = @($entry.Text -split "`r?`n")
    if ($insertAt -gt 0 -and $lines[$insertAt - 1] -ne "") {
        $entryLines = @("") + $entryLines
    }
    $entryLines += ""

    for ($j = $entryLines.Count - 1; $j -ge 0; $j--) {
        $lines.Insert($insertAt, $entryLines[$j])
    }
}

Set-Content -LiteralPath $globalLog -Value $lines -Encoding UTF8
Write-Host "$($missing.Count) Verlaufseinträge nach $globalLog promoted."
