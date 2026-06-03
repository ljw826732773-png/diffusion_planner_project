param(
    [string]$WorkspaceRoot = "$PSScriptRoot\..\..\..",
    [string]$NuplanDataRoot = "REPLACE_WITH_NUPLAN_DATA_ROOT",
    [string]$NuplanMapsRoot = "REPLACE_WITH_NUPLAN_MAPS_ROOT",
    [string]$NuplanExpRoot = "REPLACE_WITH_NUPLAN_EXP_ROOT",
    [string]$Split = "val14",
    [string]$Challenge = "closed_loop_nonreactive_agents"
)

$ErrorActionPreference = "Stop"

$NuplanDevkitRoot = Join-Path $WorkspaceRoot "work\nuplan-devkit"
$DiffusionPlannerRoot = Join-Path $WorkspaceRoot "work\Diffusion-Planner"

$env:NUPLAN_DEVKIT_ROOT = (Resolve-Path $NuplanDevkitRoot).Path
$env:NUPLAN_DATA_ROOT = $NuplanDataRoot
$env:NUPLAN_MAPS_ROOT = $NuplanMapsRoot
$env:NUPLAN_EXP_ROOT = $NuplanExpRoot
$env:HYDRA_FULL_ERROR = "1"

$ArgsFile = Join-Path $DiffusionPlannerRoot "checkpoints\args.json"
$CkptFile = Join-Path $DiffusionPlannerRoot "checkpoints\model.pth"

python "$env:NUPLAN_DEVKIT_ROOT\nuplan\planning\script\run_simulation.py" `
    +simulation=$Challenge `
    planner=diffusion_planner `
    planner.diffusion_planner.config.args_file="$ArgsFile" `
    planner.diffusion_planner.ckpt_path="$CkptFile" `
    scenario_builder=nuplan `
    scenario_filter=$Split `
    experiment_uid="diffusion_planner/$Split/local/model" `
    verbose=true `
    worker=ray_distributed `
    worker.threads_per_node=8 `
    distributed_mode=SINGLE_NODE `
    number_of_gpus_allocated_per_simulation=0.15 `
    enable_simulation_progress_bar=true `
    hydra.searchpath="[pkg://diffusion_planner.config.scenario_filter, pkg://diffusion_planner.config, pkg://nuplan.planning.script.config.common, pkg://nuplan.planning.script.experiments]"

