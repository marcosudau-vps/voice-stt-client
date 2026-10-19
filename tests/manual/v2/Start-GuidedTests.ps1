param([switch]$ProfileRuntime)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
Set-Location -LiteralPath $projectRoot
$suiteArguments = @('-m', 'tests.manual.v2.guided_suite')
if ($ProfileRuntime) { $suiteArguments += '--profile-runtime' }
Start-Process -FilePath (Join-Path $projectRoot 'venv/Scripts/python.exe') -WindowStyle Hidden -WorkingDirectory $projectRoot -ArgumentList $suiteArguments
