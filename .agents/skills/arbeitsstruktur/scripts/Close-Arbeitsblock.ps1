[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Name,
    [Parameter(Mandatory=$true)][string]$Summary,
    [string]$FinalCommit,
    [string]$PullRequest = "",
    [string]$CiStatus = "PASS",
    [string]$RepositoryRoot,
    [switch]$AllowNonMain
)

. "$PSScriptRoot\Arbeitsstruktur.Common.ps1"

$repo = Resolve-RepositoryRoot $RepositoryRoot
$branch = Get-GitBranch $repo

if (-not $AllowNonMain -and $branch -ne "main") {
    throw "Close-Arbeitsblock soll standardmäßig auf 'main' nach Integration ausgeführt werden. Aktueller Branch: '$branch'. Nur bewusst mit -AllowNonMain übersteuern."
}

$source = Get-ActiveBlockPath -RepositoryRoot $repo -Name $Name
& "$PSScriptRoot\Test-Arbeitsblock.ps1" -Path $source -RepositoryRoot $repo -Quiet | Out-Null

if (-not $FinalCommit) {
    $FinalCommit = Get-GitHead $repo
}

$safeName = Normalize-ArbeitsblockName $Name
$closeStamp = Get-NowStamp
$dateStamp = Get-DateStamp

Set-BlockState -BlockPath $source -State "ABGESCHLOSSEN"
Set-BlockPhase -BlockPath $source -Phase "ABSCHLUSS"

$bodyLines = @(
    "- Ergebnis: $Summary",
    "- Finaler Commit: ``$FinalCommit``",
    "- CI: $CiStatus"
)
if ($PullRequest) {
    $bodyLines += "- PR: $PullRequest"
}
$body = $bodyLines -join "`r`n"

Add-MarkdownLogEntry -Path (Join-Path $source "VERLAUF.md") -Timestamp $closeStamp -Title "$safeName – abgeschlossen" -Body $body

$abschluss = @"
# Abschluss – $safeName

**Abgeschlossen:** $closeStamp  
**Branch bei Abschluss:** `$branch`  
**Finaler Commit:** `$FinalCommit`  
**CI:** $CiStatus
"@
if ($PullRequest) {
    $abschluss += "`r`n**PR:** $PullRequest`r`n"
}
$abschluss += @"

## Ergebnis

$Summary

## Hinweis

`ABSCHLUSS_MANIFEST.sha256` enthält die SHA-256-Prüfsummen des abgeschlossenen Arbeitsblock-Bestands.
"@

Write-Utf8File -Path (Join-Path $source "ABSCHLUSS.md") -Content $abschluss

& "$PSScriptRoot\Promote-ArbeitsblockVerlauf.ps1" -BlockPath $source -RepositoryRoot $repo

$manifestPath = Join-Path $source "ABSCHLUSS_MANIFEST.sha256"
$files = Get-ChildItem -LiteralPath $source -File -Recurse |
    Where-Object { $_.FullName -ne $manifestPath } |
    ForEach-Object {
        [pscustomobject]@{
            Relative = Get-RelativePathCompat -BasePath $source -Path $_.FullName
            Full = $_.FullName
        }
    } |
    Sort-Object Relative

$manifestLines = foreach ($file in $files) {
    $hash = (Get-FileHash -LiteralPath $file.Full -Algorithm SHA256).Hash.ToLowerInvariant()
    "$hash  $($file.Relative)"
}

Set-Content -LiteralPath $manifestPath -Value $manifestLines -Encoding UTF8

$historyRoot = Join-Path (Get-ArbeitsdateienRoot $repo) "90_HISTORIE"
Ensure-Directory $historyRoot
$target = Join-Path $historyRoot ("$dateStamp" + "_" + $safeName)
Assert-TargetDoesNotExist $target

Move-Item -LiteralPath $source -Destination $target

Write-Host "Arbeitsblock abgeschlossen und archiviert: $target"
Write-Host "WICHTIG: CURRENT_STATE.md und MASTERPLAN.md jetzt auf den Post-Abschluss-Zustand prüfen/aktualisieren; dies wird bewusst nicht automatisch geraten."
