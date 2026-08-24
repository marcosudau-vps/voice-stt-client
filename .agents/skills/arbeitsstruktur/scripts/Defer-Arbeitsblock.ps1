[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Name,
    [Parameter(Mandatory=$true)][string]$Reason,
    [string]$RepositoryRoot
)

. "$PSScriptRoot\Arbeitsstruktur.Common.ps1"

$repo = Resolve-RepositoryRoot $RepositoryRoot
$source = Get-ActiveBlockPath -RepositoryRoot $repo -Name $Name
& "$PSScriptRoot\Test-Arbeitsblock.ps1" -Path $source -RepositoryRoot $repo -Quiet | Out-Null

$safeName = Normalize-ArbeitsblockName $Name
$targetRoot = Join-Path (Get-ArbeitsdateienRoot $repo) "20_ZURUECKGESTELLT"
Ensure-Directory $targetRoot
$target = Join-Path $targetRoot $safeName
Assert-TargetDoesNotExist $target

Set-BlockState -BlockPath $source -State "ZURUECKGESTELLT"

$statusPath = Join-Path $source "STATUS.md"
Add-Content -LiteralPath $statusPath -Encoding UTF8 -Value @"

## Zurückstellung – $(Get-NowStamp)

$Reason
"@

$body = "- Grund: $Reason"
Add-BlockLifecycleLogEntry -RepositoryRoot $repo -BlockPath $source -Title "$safeName – zurückgestellt" -Body $body | Out-Null

Move-Item -LiteralPath $source -Destination $target
Write-Host "Arbeitsblock zurückgestellt: $target"
