param(
    [string]$NuplanDataRoot = $env:NUPLAN_DATA_ROOT,
    [string]$NuplanMapsRoot = $env:NUPLAN_MAPS_ROOT,
    [string]$NuplanExpRoot = $env:NUPLAN_EXP_ROOT
)

$ErrorActionPreference = "Stop"

function Show-Status {
    param(
        [string]$Name,
        [bool]$Ok,
        [string]$Detail
    )

    $mark = if ($Ok) { "[OK]" } else { "[MISS]" }
    Write-Output "$mark $Name - $Detail"
}

if (-not $NuplanDataRoot) {
    $NuplanDataRoot = Join-Path $HOME "nuplan\dataset"
}
if (-not $NuplanMapsRoot) {
    $NuplanMapsRoot = Join-Path $NuplanDataRoot "maps"
}
if (-not $NuplanExpRoot) {
    $NuplanExpRoot = Join-Path $HOME "nuplan\exp"
}

Write-Output "NUPLAN_DATA_ROOT=$NuplanDataRoot"
Write-Output "NUPLAN_MAPS_ROOT=$NuplanMapsRoot"
Write-Output "NUPLAN_EXP_ROOT=$NuplanExpRoot"
Write-Output ""

$dataRootOk = Test-Path $NuplanDataRoot
$mapsRootOk = Test-Path $NuplanMapsRoot
$expRootOk = Test-Path $NuplanExpRoot

Show-Status "data root" $dataRootOk $NuplanDataRoot
Show-Status "maps root" $mapsRootOk $NuplanMapsRoot
Show-Status "exp root" $expRootOk $NuplanExpRoot

$miniPath = Join-Path $NuplanDataRoot "nuplan-v1.1\splits\mini"
$trainvalPath = Join-Path $NuplanDataRoot "nuplan-v1.1\trainval"
$testPath = Join-Path $NuplanDataRoot "nuplan-v1.1\test"
$sensorPath = Join-Path $NuplanDataRoot "nuplan-v1.1\sensor_blobs"

$miniDbCount = if (Test-Path $miniPath) { @(Get-ChildItem -Path $miniPath -Filter "*.db" -File -ErrorAction SilentlyContinue).Count } else { 0 }
$trainvalDbCount = if (Test-Path $trainvalPath) { @(Get-ChildItem -Path $trainvalPath -Filter "*.db" -File -ErrorAction SilentlyContinue).Count } else { 0 }
$testDbCount = if (Test-Path $testPath) { @(Get-ChildItem -Path $testPath -Filter "*.db" -File -ErrorAction SilentlyContinue).Count } else { 0 }

Show-Status "mini db files" ($miniDbCount -gt 0) "$miniPath ($miniDbCount .db files)"
Show-Status "trainval db files" ($trainvalDbCount -gt 0) "$trainvalPath ($trainvalDbCount .db files)"
Show-Status "test db files" ($testDbCount -gt 0) "$testPath ($testDbCount .db files)"
Show-Status "sensor blobs" (Test-Path $sensorPath) $sensorPath

$mapsJson = Join-Path $NuplanMapsRoot "nuplan-maps-v1.0.json"
$gpkgFiles = if (Test-Path $NuplanMapsRoot) {
    @(Get-ChildItem -Path $NuplanMapsRoot -Filter "map.gpkg" -Recurse -File -ErrorAction SilentlyContinue)
} else {
    @()
}

Show-Status "maps metadata" (Test-Path $mapsJson) $mapsJson
Show-Status "map.gpkg files" ($gpkgFiles.Count -ge 4) "$($gpkgFiles.Count) files found"

Write-Output ""
if (($miniDbCount -gt 0 -or $trainvalDbCount -gt 0) -and (Test-Path $mapsJson) -and ($gpkgFiles.Count -ge 4)) {
    Write-Output "Dataset check passed for local evaluation setup."
} else {
    Write-Output "Dataset check incomplete. Download nuPlan dataset/maps or pass explicit paths:"
    Write-Output "  .\outputs\diffusion_planner_project\scripts\check_nuplan_data.ps1 -NuplanDataRoot D:\data\nuplan -NuplanMapsRoot D:\data\nuplan\maps -NuplanExpRoot D:\data\nuplan\exp"
}

