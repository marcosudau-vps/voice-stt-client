param([switch]$ProfileRuntime, [string[]]$Tasks, [string]$ServerInfo)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
Set-Location -LiteralPath $projectRoot
$suiteArguments = @('-m', 'tests.manual.v2.guided_suite')
if ($ProfileRuntime) { $suiteArguments += '--profile-runtime' }
if (-not $ServerInfo) {
    $ServerInfo=Join-Path $projectRoot 'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/review-ready-20261022/server-info.json'
}
if ($ProfileRuntime -and -not (Test-Path -LiteralPath $ServerInfo -PathType Leaf)) { throw 'Pinned Pro-V2 server evidence missing; no qualification fallback' }
if (Test-Path -LiteralPath $ServerInfo -PathType Leaf) { $suiteArguments += '--server-info'; $suiteArguments += $ServerInfo }
if ($Tasks) { $suiteArguments += '--tasks'; $suiteArguments += $Tasks }
Start-Process -FilePath (Join-Path $projectRoot 'venv/Scripts/python.exe') -WindowStyle Hidden -WorkingDirectory $projectRoot -ArgumentList $suiteArguments
