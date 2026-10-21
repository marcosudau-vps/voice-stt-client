param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9_-]+$')][string]$Name,
    [switch]$Delete
)
$ErrorActionPreference='Stop'
# One PowerShell process throughout. No recursive delete, forced delete,
# alternate API, policy change, shell composition or V1 path access.
$approvedRoot='C:\Users\marco\.voice-stt\qualification\AP-IV2-020'
$workspace=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../../..')).Path
$target=[IO.Path]::GetFullPath((Join-Path $approvedRoot $Name))
$archive=[IO.Path]::GetFullPath((Join-Path $workspace ('build\ap-iv2-020-suite\private-archive\'+$Name)))
if (-not $target.StartsWith($approvedRoot+'\',[StringComparison]::OrdinalIgnoreCase)) {throw 'Target outside approved namespace'}
if ($target -eq $approvedRoot) {throw 'Cannot remove namespace root'}
$sourceItem=Get-Item -LiteralPath $target
$archiveItem=Get-Item -LiteralPath $archive
if (-not $sourceItem.PSIsContainer -or -not $archiveItem.PSIsContainer) {throw 'Expected directories'}
$items=@($sourceItem,$archiveItem)+@(Get-ChildItem -LiteralPath $target -Recurse -Force)+@(Get-ChildItem -LiteralPath $archive -Recurse -Force)
if ($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) {throw 'Reparse point excluded'}
if (Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(pythonw?|voice-stt-client)\.exe$' -and $_.CommandLine -like ('*'+$target+'*') }) {throw 'Runtime process still active'}
# The endurance runner passes its profile through environment variables, not
# argv. Its project report binds the actual worker PID to the runtime root.
foreach ($probe in @(Get-ChildItem -LiteralPath (Join-Path $workspace 'build\ap-iv2-020-suite') -Directory -Filter 'endurance*')) {
    $probeReport=Join-Path $probe.FullName 'result.json'
    if (-not (Test-Path -LiteralPath $probeReport)) {continue}
    $probeData=Get-Content -LiteralPath $probeReport -Raw | ConvertFrom-Json
    if ($probeData.runtimeFolder -and [IO.Path]::GetFullPath($probeData.runtimeFolder) -eq $target -and $probeData.pid) {
        if (Get-Process -Id ([int]$probeData.pid) -ErrorAction SilentlyContinue) {throw 'Bound endurance worker still active'}
    }
}
$manifestPath=Join-Path $archive 'archive-manifest.json'
$manifest=Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$expected=@{}
if ($manifest.PSObject.Properties.Name -contains 'files') {
    if ($manifest.files -is [Array]) {
        foreach ($file in $manifest.files) {
            if ($expected.ContainsKey($file.path)) {throw 'Duplicate manifest file'}
            $expected[$file.path]=$file.sha256
        }
    } else {
        foreach ($file in $manifest.files.PSObject.Properties) {$expected[$file.Name]=$file.Value}
    }
} else {
    foreach ($file in $manifest.PSObject.Properties) {$expected[$file.Name]=$file.Value}
}
foreach ($binding in @('source','original')) {
    if ($manifest.PSObject.Properties.Name -contains $binding) {
        if ([IO.Path]::GetFullPath($manifest.$binding) -ne $target) {throw 'Wrong archive source binding'}
    }
}
$verified=@()
foreach ($entry in $expected.GetEnumerator()) {
    if ($entry.Value -notmatch '^[a-fA-F0-9]{64}$') {throw 'Malformed hash'}
    $sourceFile=[IO.Path]::GetFullPath((Join-Path $target $entry.Key))
    $archiveFile=[IO.Path]::GetFullPath((Join-Path $archive $entry.Key))
    if (-not $sourceFile.StartsWith($target+'\',[StringComparison]::OrdinalIgnoreCase) -or -not $archiveFile.StartsWith($archive+'\',[StringComparison]::OrdinalIgnoreCase)) {throw 'Manifest path escape'}
    if ((Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash -ne $entry.Value) {throw 'Source changed'}
    if ((Get-FileHash -LiteralPath $archiveFile -Algorithm SHA256).Hash -ne $entry.Value) {throw 'Archive changed'}
    $verified+=@{path=$sourceFile;hash=$entry.Value}
}
$actual=@(Get-ChildItem -LiteralPath $target -Recurse -Force -File)
if ($actual.Count -ne $verified.Count) {throw 'Unindexed source files'}
if (-not $Delete) {
    Write-Output ('VERIFIED_ONLY '+$Name+' files='+$verified.Count)
    return
}
foreach ($file in $verified) {
    if ((Get-FileHash -LiteralPath $file.path -Algorithm SHA256).Hash -ne $file.hash) {throw 'Source changed after preflight'}
    Remove-Item -LiteralPath $file.path -ErrorAction Stop
}
$directories=@(Get-ChildItem -LiteralPath $target -Recurse -Force -Directory | Sort-Object { $_.FullName.Length } -Descending)
foreach ($directory in $directories) {
    if (-not $directory.FullName.StartsWith($target+'\',[StringComparison]::OrdinalIgnoreCase) -or ($directory.Attributes -band [IO.FileAttributes]::ReparsePoint)) {throw 'Directory changed'}
    if (@(Get-ChildItem -LiteralPath $directory.FullName -Force).Count -ne 0) {throw 'Directory not empty'}
    Remove-Item -LiteralPath $directory.FullName -ErrorAction Stop
}
if (@(Get-ChildItem -LiteralPath $target -Force).Count -ne 0) {throw 'Root not empty'}
Remove-Item -LiteralPath $target -ErrorAction Stop
if (Test-Path -LiteralPath $target) {throw 'Cleanup incomplete'}
$report=Join-Path $workspace 'build\ap-iv2-020-suite\cleanup-removals'
New-Item -ItemType Directory -Path $report -Force | Out-Null
@{name=$Name;target=$target;archive=$archive;removedAtUtc=[DateTime]::UtcNow.ToString('o');files=$verified.Count;
  scriptSha256=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash;
  manifestSha256=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash;result='REMOVED_AFTER_VERIFIED_ARCHIVE';
  method='Explicit Delete; per-file hash recheck and non-recursive LiteralPath removal; empty directories only; same approval-reviewed execution tool'} |
    ConvertTo-Json | Set-Content -LiteralPath (Join-Path $report ($Name+'.json')) -Encoding utf8
Write-Output ('REMOVED_VERIFIED '+$Name+' files='+$verified.Count)
