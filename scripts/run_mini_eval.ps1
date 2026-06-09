param(
    [string]$WorkspaceRoot = "$PSScriptRoot\..\..\..",
    [string]$NuplanDataRoot = "",
    [string]$NuplanMapsRoot = "",
    [string]$NuplanExpRoot = "",
    [string]$ScenarioBuilder = "nuplan_mini",
    [string]$ScenarioFilter = "one_of_each_scenario_type",
    [string]$Challenge = "closed_loop_nonreactive_agents",
    [string]$Worker = "sequential",
    [int]$LimitTotalScenarios = 5,
    [string]$ExperimentUid = "dp/mini5/model",
    [string]$SummaryPrefix = "mini_eval",
    [string]$Planner = "diffusion_planner",
    [switch]$SkipSimulation
)

$ErrorActionPreference = "Stop"

if (-not $NuplanDataRoot) {
    if ($env:NUPLAN_DATA_ROOT) {
        $NuplanDataRoot = $env:NUPLAN_DATA_ROOT
    } elseif (Test-Path "D:\") {
        $NuplanDataRoot = "D:\nuplan-data\dataset"
    } else {
        $NuplanDataRoot = Join-Path $HOME "nuplan\dataset"
    }
}
if (-not $NuplanMapsRoot) {
    if ($env:NUPLAN_MAPS_ROOT) {
        $NuplanMapsRoot = $env:NUPLAN_MAPS_ROOT
    } else {
        $NuplanMapsRoot = Join-Path $NuplanDataRoot "maps"
    }
}
if (-not $NuplanExpRoot) {
    if ($env:NUPLAN_EXP_ROOT) {
        $NuplanExpRoot = $env:NUPLAN_EXP_ROOT
    } elseif (Test-Path "D:\") {
        $NuplanExpRoot = "D:\nuplan-data\exp"
    } else {
        $NuplanExpRoot = Join-Path $HOME "nuplan\exp"
    }
}

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ResultsDir = Join-Path $ProjectRoot "results"
$ExperimentPath = $ExperimentUid -replace "/", "\"
$RunRoot = Join-Path $NuplanExpRoot (Join-Path "exp\simulation\$Challenge" $ExperimentPath)

Write-Output "NuplanDataRoot=$NuplanDataRoot"
Write-Output "NuplanMapsRoot=$NuplanMapsRoot"
Write-Output "NuplanExpRoot=$NuplanExpRoot"
Write-Output "RunRoot=$RunRoot"

if (-not $SkipSimulation) {
    & "$PSScriptRoot\run_simulation_template.ps1" `
        -WorkspaceRoot $WorkspaceRoot `
        -NuplanDataRoot $NuplanDataRoot `
        -NuplanMapsRoot $NuplanMapsRoot `
        -NuplanExpRoot $NuplanExpRoot `
        -ScenarioBuilder $ScenarioBuilder `
        -Split $ScenarioFilter `
        -Challenge $Challenge `
        -Worker $Worker `
        -LimitTotalScenarios $LimitTotalScenarios `
        -ExperimentUid $ExperimentUid `
        -Planner $Planner
}

python "$PSScriptRoot\summarize_nuplan_results.py" `
    --run-root "$RunRoot" `
    --output-dir "$ResultsDir" `
    --prefix "$SummaryPrefix"
