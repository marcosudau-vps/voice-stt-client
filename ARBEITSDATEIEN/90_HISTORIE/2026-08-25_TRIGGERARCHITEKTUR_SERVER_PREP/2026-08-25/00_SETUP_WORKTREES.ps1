$ErrorActionPreference = "Stop"

$Repo = "P:\GithubRepos\marcosudau-vps\voice-stt-server\workspaces\einheitliche-triggerarchitektur"
$WorkspaceRoot = "P:\GithubRepos\marcosudau-vps\voice-stt-server\workspaces"
$Base = "db3d2b49539afbf4812d90e13f26f099b9314fe9"

$Targets = @(
    @{ Branch = "prep/AP-SRV-040/protocol-v2"; Path = Join-Path $WorkspaceRoot "prep-srv-040" },
    @{ Branch = "prep/AP-SRV-050/settings-control"; Path = Join-Path $WorkspaceRoot "prep-srv-050" },
    @{ Branch = "prep/AP-SRV-060/wakeword"; Path = Join-Path $WorkspaceRoot "prep-srv-060" }
)

if (-not (Test-Path $Repo)) {
    throw "Server-Worktree existiert nicht: $Repo"
}

Set-Location $Repo

$inside = git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $inside.Trim() -ne "true") {
    throw "Kein Git-Worktree: $Repo"
}

$repoRoot = (git rev-parse --show-toplevel).Trim()
Write-Host "Git-Worktree erkannt: $repoRoot"

git cat-file -e "$Base^{commit}" 2>$null
if ($LASTEXITCODE -ne 0) {
    throw "Base commit $Base ist lokal nicht vorhanden."
}

$baseTree = (git rev-parse "$Base^{tree}").Trim()
Write-Host "Base commit: $Base"
Write-Host "Base tree:   $baseTree"

foreach ($Target in $Targets) {
    $existingBranch = git branch --list $Target.Branch
    if ($existingBranch) {
        throw "Branch existiert bereits: $($Target.Branch)"
    }
    if (Test-Path $Target.Path) {
        throw "Worktree-Ziel existiert bereits: $($Target.Path)"
    }
}

foreach ($Target in $Targets) {
    Write-Host ""
    Write-Host "Erzeuge $($Target.Branch)"
    Write-Host "  -> $($Target.Path)"
    git worktree add -b $Target.Branch $Target.Path $Base
    if ($LASTEXITCODE -ne 0) {
        throw "git worktree add fehlgeschlagen für $($Target.Branch)"
    }
}

Write-Host ""
Write-Host "PREP-WORKTREES: PASS"
git worktree list
