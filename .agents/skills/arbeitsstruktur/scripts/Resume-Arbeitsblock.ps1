[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Name,
    [string]$Reason = "Arbeitsblock wird wieder aufgenommen.",
    [string]$RepositoryRoot
)

. "$PSScriptRoot\Arbeitsstruktur.Common.ps1"

$repo = Resolve-RepositoryRoot $RepositoryRoot
$source = Get-DeferredBlockPath -RepositoryRoot $repo -Name $Name
& "$PSScriptRoot\Test-Arbeitsblock.ps1" -Path $source -RepositoryRoot $repo -Quiet | Out-Null

$safeName = Normalize-ArbeitsblockName $Name
$targetRoot = Join-Path (Get-ArbeitsdateienRoot $repo) "10_AKTUELL"
Ensure-Directory $targetRoot
$target = Join-Path $targetRoot $safeName
Assert-TargetDoesNotExist $target

Set-BlockState -BlockPath $source -State "AKTIV"

$statusPath = Join-Path $source "STATUS.md"
Add-Content -LiteralPath $statusPath -Encoding UTF8 -Value @"

## Wiederaufnahme – $(Get-NowStamp)

$Reason
"@

$body = "- Anlass: $Reason"
Add-BlockLifecycleLogEntry -RepositoryRoot $repo -BlockPath $source -Title "$safeName – wieder aufgenommen" -Body $body | Out-Null

Move-Item -LiteralPath $source -Destination $target
Write-Host "Arbeitsblock wieder aufgenommen: $target"
