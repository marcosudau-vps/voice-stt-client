Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepositoryRoot {
    param([string]$RepositoryRoot)

    if ($RepositoryRoot) {
        return (Resolve-Path -LiteralPath $RepositoryRoot).Path
    }

    if (Get-Command git -ErrorAction SilentlyContinue) {
        $root = (& git rev-parse --show-toplevel 2>$null)
        if ($LASTEXITCODE -eq 0 -and $root) {
            return (Resolve-Path -LiteralPath $root.Trim()).Path
        }
    }

    $cursor = (Get-Location).Path
    while ($cursor) {
        if (Test-Path -LiteralPath (Join-Path $cursor ".git")) {
            return $cursor
        }
        $parent = Split-Path -Parent $cursor
        if (-not $parent -or $parent -eq $cursor) { break }
        $cursor = $parent
    }

    throw "Repository-Root konnte nicht bestimmt werden. -RepositoryRoot explizit angeben."
}

function Get-ArbeitsdateienRoot {
    param([Parameter(Mandatory=$true)][string]$RepositoryRoot)
    return (Join-Path $RepositoryRoot "ARBEITSDATEIEN")
}

function Get-NowStamp {
    return [DateTimeOffset]::Now.ToString("yyyy-MM-dd HH:mm:ss zzz")
}

function Get-DateStamp {
    return [DateTimeOffset]::Now.ToString("yyyy-MM-dd")
}

function Get-GitBranch {
    param([Parameter(Mandatory=$true)][string]$RepositoryRoot)

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        return "UNKNOWN"
    }

    Push-Location $RepositoryRoot
    try {
        $branch = (& git branch --show-current 2>$null)
        if ($LASTEXITCODE -eq 0 -and $branch) { return $branch.Trim() }
        return "DETACHED_OR_UNKNOWN"
    }
    finally {
        Pop-Location
    }
}

function Get-GitHead {
    param([Parameter(Mandatory=$true)][string]$RepositoryRoot)

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        return "UNKNOWN"
    }

    Push-Location $RepositoryRoot
    try {
        $head = (& git rev-parse HEAD 2>$null)
        if ($LASTEXITCODE -eq 0 -and $head) { return $head.Trim() }
        return "UNKNOWN"
    }
    finally {
        Pop-Location
    }
}

function Normalize-ArbeitsblockName {
    param([Parameter(Mandatory=$true)][string]$Name)

    $normalized = $Name.Trim() -replace '\s+', '_'
    foreach ($char in [IO.Path]::GetInvalidFileNameChars()) {
        $normalized = $normalized.Replace([string]$char, "_")
    }
    $normalized = $normalized -replace '_+', '_'
    $normalized = $normalized.Trim([char[]]"_. ")

    if (-not $normalized) {
        throw "Arbeitsblock-Name ist nach Normalisierung leer."
    }

    if ($normalized -in @(".", "..")) {
        throw "Ungültiger Arbeitsblock-Name: $normalized"
    }

    return $normalized
}

function Ensure-Directory {
    param([Parameter(Mandatory=$true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Write-Utf8File {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][string]$Content,
        [switch]$NoOverwrite
    )

    if ($NoOverwrite -and (Test-Path -LiteralPath $Path)) {
        return
    }

    $parent = Split-Path -Parent $Path
    if ($parent) { Ensure-Directory $parent }
    Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

function Get-RootFilePath {
    param(
        [Parameter(Mandatory=$true)][string]$RepositoryRoot,
        [Parameter(Mandatory=$true)][string]$CanonicalName
    )

    $existing = Get-ChildItem -LiteralPath $RepositoryRoot -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ieq $CanonicalName } |
        Select-Object -First 1

    if ($existing) {
        return $existing.FullName
    }

    return (Join-Path $RepositoryRoot $CanonicalName)
}

function Ensure-MarkedSection {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][string]$MarkerId,
        [Parameter(Mandatory=$true)][string]$SectionContent,
        [string]$PrefixIfNew = ""
    )

    $begin = "<!-- BEGIN $MarkerId -->"
    $end = "<!-- END $MarkerId -->"

    if (Test-Path -LiteralPath $Path) {
        $content = Get-Content -LiteralPath $Path -Raw

        if ($content.Contains($begin)) {
            if (-not $content.Contains($end)) {
                throw "Marker '$MarkerId' ist in '$Path' unvollständig. Bitte manuell prüfen."
            }
            return $false
        }

        $append = ""
        if ($content -and -not $content.EndsWith("`n")) {
            $append += "`r`n"
        }
        $append += "`r`n$begin`r`n$SectionContent`r`n$end`r`n"
        Add-Content -LiteralPath $Path -Value $append -Encoding UTF8
        return $true
    }

    $newContent = ""
    if ($PrefixIfNew) {
        $newContent += "$PrefixIfNew`r`n`r`n"
    }
    $newContent += "$begin`r`n$SectionContent`r`n$end`r`n"
    Write-Utf8File -Path $Path -Content $newContent
    return $true
}

function Add-MarkdownLogEntry {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][string]$Timestamp,
        [Parameter(Mandatory=$true)][string]$Title,
        [string]$Body = ""
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        Write-Utf8File -Path $Path -Content "# Verlauf`r`n"
    }

    $entry = "`r`n## $Timestamp – $Title`r`n"
    if ($Body) {
        $entry += "`r`n$Body`r`n"
    }
    Add-Content -LiteralPath $Path -Value $entry -Encoding UTF8
}

function Add-BlockLifecycleLogEntry {
    param(
        [Parameter(Mandatory=$true)][string]$RepositoryRoot,
        [Parameter(Mandatory=$true)][string]$BlockPath,
        [Parameter(Mandatory=$true)][string]$Title,
        [string]$Body = ""
    )

    $timestamp = Get-NowStamp
    $localLog = Join-Path $BlockPath "VERLAUF.md"
    Add-MarkdownLogEntry -Path $localLog -Timestamp $timestamp -Title $Title -Body $Body

    # Auf main ist der repositoryweite Verlauf zugleich kanonisch.
    # Auf Feature-Branches bleibt der neue Eintrag zunächst lokal und
    # wird beim Abschluss/Promotion übernommen.
    if ((Get-GitBranch $RepositoryRoot) -eq "main") {
        $globalLog = Join-Path (Get-ArbeitsdateienRoot $RepositoryRoot) "00_STEUERUNG\LOG_VERLAUF.md"
        Add-MarkdownLogEntry -Path $globalLog -Timestamp $timestamp -Title $Title -Body $Body
    }

    return $timestamp
}

function Get-StatusContent {
    param([Parameter(Mandatory=$true)][string]$BlockPath)
    $path = Join-Path $BlockPath "STATUS.md"
    if (-not (Test-Path -LiteralPath $path)) {
        throw "STATUS.md fehlt: $path"
    }
    return Get-Content -LiteralPath $path -Raw
}

function Get-BlockMeta {
    param([Parameter(Mandatory=$true)][string]$BlockPath)

    $content = Get-StatusContent $BlockPath
    $match = [regex]::Match($content, '(?ms)<!--\s*ARBEITSBLOCK-META\s*(.*?)\s*-->')
    if (-not $match.Success) {
        throw "ARBEITSBLOCK-META fehlt in $(Join-Path $BlockPath 'STATUS.md')."
    }

    $meta = @{}
    foreach ($line in ($match.Groups[1].Value -split "`r?`n")) {
        $m = [regex]::Match($line, '^\s*([^:]+):\s*(.*?)\s*$')
        if ($m.Success) {
            $meta[$m.Groups[1].Value.Trim()] = $m.Groups[2].Value.Trim()
        }
    }
    return $meta
}

function Set-BlockMetaValue {
    param(
        [Parameter(Mandatory=$true)][string]$BlockPath,
        [Parameter(Mandatory=$true)][string]$Key,
        [Parameter(Mandatory=$true)][string]$Value
    )

    $path = Join-Path $BlockPath "STATUS.md"
    $content = Get-Content -LiteralPath $path -Raw
    $pattern = "(?m)^" + [regex]::Escape($Key) + ":\s*.*$"

    if (-not [regex]::IsMatch($content, $pattern)) {
        throw "Metadaten-Schlüssel '$Key' fehlt in STATUS.md."
    }

    $replacement = "${Key}: $Value"
    $content = [regex]::Replace($content, $pattern, $replacement, 1)
    Set-Content -LiteralPath $path -Value $content -Encoding UTF8
}

function Set-BlockState {
    param(
        [Parameter(Mandatory=$true)][string]$BlockPath,
        [Parameter(Mandatory=$true)][ValidateSet("AKTIV","ZURUECKGESTELLT","ABGESCHLOSSEN")][string]$State
    )

    Set-BlockMetaValue -BlockPath $BlockPath -Key "state" -Value $State
    Set-BlockMetaValue -BlockPath $BlockPath -Key "updated_at" -Value (Get-NowStamp)

    $path = Join-Path $BlockPath "STATUS.md"
    $content = Get-Content -LiteralPath $path -Raw
    if ([regex]::IsMatch($content, '(?m)^\*\*Status:\*\*\s*.*$')) {
        $content = [regex]::Replace($content, '(?m)^\*\*Status:\*\*\s*.*$', "**Status:** $State", 1)
        Set-Content -LiteralPath $path -Value $content -Encoding UTF8
    }
}

function Set-BlockPhase {
    param(
        [Parameter(Mandatory=$true)][string]$BlockPath,
        [Parameter(Mandatory=$true)][string]$Phase
    )
    Set-BlockMetaValue -BlockPath $BlockPath -Key "phase" -Value $Phase
    Set-BlockMetaValue -BlockPath $BlockPath -Key "updated_at" -Value (Get-NowStamp)
}

function Get-ActiveBlockPath {
    param(
        [Parameter(Mandatory=$true)][string]$RepositoryRoot,
        [Parameter(Mandatory=$true)][string]$Name
    )

    $safeName = Normalize-ArbeitsblockName $Name
    $path = Join-Path (Get-ArbeitsdateienRoot $RepositoryRoot) ("10_AKTUELL\" + $safeName)
    if (-not (Test-Path -LiteralPath $path -PathType Container)) {
        throw "Aktiver Arbeitsblock nicht gefunden: $path"
    }
    return $path
}

function Get-DeferredBlockPath {
    param(
        [Parameter(Mandatory=$true)][string]$RepositoryRoot,
        [Parameter(Mandatory=$true)][string]$Name
    )

    $safeName = Normalize-ArbeitsblockName $Name
    $path = Join-Path (Get-ArbeitsdateienRoot $RepositoryRoot) ("20_ZURUECKGESTELLT\" + $safeName)
    if (-not (Test-Path -LiteralPath $path -PathType Container)) {
        throw "Zurückgestellter Arbeitsblock nicht gefunden: $path"
    }
    return $path
}

function Assert-TargetDoesNotExist {
    param([Parameter(Mandatory=$true)][string]$Path)
    if (Test-Path -LiteralPath $Path) {
        throw "Ziel existiert bereits: $Path"
    }
}

function Get-RelativePathCompat {
    param(
        [Parameter(Mandatory=$true)][string]$BasePath,
        [Parameter(Mandatory=$true)][string]$Path
    )

    $base = (Resolve-Path -LiteralPath $BasePath).Path.TrimEnd("\") + "\"
    $target = (Resolve-Path -LiteralPath $Path).Path

    $baseUri = New-Object System.Uri($base)
    $targetUri = New-Object System.Uri($target)
    $relative = $baseUri.MakeRelativeUri($targetUri).ToString()
    return [Uri]::UnescapeDataString($relative).Replace("/", "\")
}

function Get-StandardLogEntries {
    param([Parameter(Mandatory=$true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) { return @() }

    $lines = Get-Content -LiteralPath $Path
    $entries = New-Object System.Collections.Generic.List[object]
    $current = $null

    foreach ($line in $lines) {
        $m = [regex]::Match($line, '^##\s+(?<ts>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+[+-]\d{2}:\d{2})\s+–\s+(?<title>.+)$')
        if ($m.Success) {
            if ($null -ne $current) {
                $entries.Add([pscustomobject]@{
                    Timestamp = $current.Timestamp
                    Text = ($current.Lines -join "`r`n").TrimEnd()
                })
            }

            $dto = [DateTimeOffset]::ParseExact(
                $m.Groups["ts"].Value,
                "yyyy-MM-dd HH:mm:ss zzz",
                [Globalization.CultureInfo]::InvariantCulture
            )

            $current = [pscustomobject]@{
                Timestamp = $dto
                Lines = New-Object System.Collections.Generic.List[string]
            }
            $current.Lines.Add($line)
        }
        elseif ($null -ne $current) {
            $current.Lines.Add($line)
        }
    }

    if ($null -ne $current) {
        $entries.Add([pscustomobject]@{
            Timestamp = $current.Timestamp
            Text = ($current.Lines -join "`r`n").TrimEnd()
        })
    }

    return @($entries)
}

function Get-TextHash {
    param([Parameter(Mandatory=$true)][string]$Text)

    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [Text.Encoding]::UTF8.GetBytes($Text.Replace("`r`n","`n").Trim())
        return ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-","").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}
