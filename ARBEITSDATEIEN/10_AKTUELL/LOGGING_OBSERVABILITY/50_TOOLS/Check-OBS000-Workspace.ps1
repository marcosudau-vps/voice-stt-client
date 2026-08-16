$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Write-Host "OBS-000 Workspace Check" -ForegroundColor Cyan
Write-Host "Root: $Root"
Write-Host ""

$RequiredStructure = @(
    "START_HIER.md",
    "AGENTS.md",
    "00_GRUNDLAGEN\LOGGING_ZIELBILD_ARCHITEKTUR_GESAMTSPEZIFIKATION_ENTWURF.md",
    "00_GRUNDLAGEN\LOGGING_V1_ABGRENZUNG_ENTWURF.md",
    "00_GRUNDLAGEN\LETZTE_ARCHITEKTURKLAERUNGEN_VOR_PLAN_FREEZE.md",
    "20_PLANUNG\LOGGING_GESAMTPLAN\00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md",
    "20_PLANUNG\LOGGING_GESAMTPLAN\02_OBS000_FREEZE_CHECKLIST.md",
    "30_AUSFUEHRUNG\prompts\PRM-OBS-000-01_2026-08-15_PLAN_FREEZE.md"
)

Write-Host "Struktur:" -ForegroundColor Yellow
foreach ($Rel in $RequiredStructure) {
    $Path = Join-Path $Root $Rel
    if (Test-Path $Path) {
        Write-Host "  [OK]      $Rel" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $Rel" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Frische Claude-Artefakte (rekursive Suche im Workspace):" -ForegroundColor Yellow

$Workspace = Resolve-Path (Join-Path $Root "..\..")
$Expected = @(
    "LOGGING_CODE_INTEGRATION_AUDIT.md",
    "LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md",
    "LOGGING_CONCURRENCY_FAILURE_MODEL.md",
    "LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md",
    "LOGGING_V1_IMPLEMENTATION_PLAN.md",
    "LOGGING_OPEN_DECISIONS.md",
    "LOGGING_ADVERSARIAL_REVIEW.md"
)

foreach ($Name in $Expected) {
    $Matches = Get-ChildItem -Path $Workspace -Filter $Name -File -Recurse -ErrorAction SilentlyContinue
    if ($Matches) {
        Write-Host "  [FOUND]   $Name" -ForegroundColor Green
        foreach ($M in $Matches) {
            Write-Host "            $($M.FullName)"
        }
    } else {
        Write-Host "  [MISSING] $Name" -ForegroundColor DarkYellow
    }
}

$Optional = "LOGGING_TEST_MATRIX.md"
$Matches = Get-ChildItem -Path $Workspace -Filter $Optional -File -Recurse -ErrorAction SilentlyContinue
if ($Matches) {
    Write-Host "  [FOUND]   $Optional (optional)" -ForegroundColor Green
    foreach ($M in $Matches) { Write-Host "            $($M.FullName)" }
} else {
    Write-Host "  [OPTIONAL-MISSING] $Optional" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Dieses Skript hat keine Dateien verändert." -ForegroundColor Cyan
