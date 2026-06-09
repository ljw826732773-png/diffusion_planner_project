param(
    [string]$WorkspaceRoot = "$PSScriptRoot\..\..\..",
    [string]$NuplanDataRoot = "",
    [string]$NuplanMapsRoot = "",
    [string]$NuplanExpRoot = "",
    [string]$ScenarioBuilder = "nuplan_mini",
    [string]$Split = "one_of_each_scenario_type",
    [string]$Challenge = "closed_loop_nonreactive_agents",
    [string]$Worker = "sequential",
    [int]$LimitTotalScenarios = 1,
    [string]$ExperimentUid = "dp/mini/model",
    [string]$Planner = "diffusion_planner"
)

$ErrorActionPreference = "Stop"

$NuplanDevkitRoot = Join-Path $WorkspaceRoot "work\nuplan-devkit"
$DiffusionPlannerRoot = Join-Path $WorkspaceRoot "work\Diffusion-Planner"

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

$env:NUPLAN_DEVKIT_ROOT = (Resolve-Path $NuplanDevkitRoot).Path
$env:NUPLAN_DATA_ROOT = $NuplanDataRoot
$env:NUPLAN_MAPS_ROOT = $NuplanMapsRoot
$env:NUPLAN_EXP_ROOT = $NuplanExpRoot
$env:HYDRA_FULL_ERROR = "1"

$ArgsFile = Join-Path $DiffusionPlannerRoot "checkpoints\args.json"
$CkptFile = Join-Path $DiffusionPlannerRoot "checkpoints\model.pth"

$SimulationArgs = @(
    "+simulation=$Challenge",
    "planner=$Planner",
    "planner.diffusion_planner.config.args_file=$ArgsFile",
    "planner.diffusion_planner.ckpt_path=$CkptFile",
    "scenario_builder=$ScenarioBuilder",
    "scenario_filter=$Split",
    "scenario_filter.limit_total_scenarios=$LimitTotalScenarios",
    "experiment_uid=$ExperimentUid",
    "verbose=true",
    "worker=$Worker",
    "distributed_mode=SINGLE_NODE",
    "number_of_gpus_allocated_per_simulation=0.15",
    "enable_simulation_progress_bar=true",
    "hydra.searchpath=[pkg://diffusion_planner.config.scenario_filter, pkg://diffusion_planner.config, pkg://nuplan.planning.script.config.common, pkg://nuplan.planning.script.experiments]"
)

if ($Worker -eq "ray_distributed") {
    $SimulationArgs += "worker.threads_per_node=8"
}

python "$env:NUPLAN_DEVKIT_ROOT\nuplan\planning\script\run_simulation.py" @SimulationArgs
