param(
    [string]$ProjectRoot = "$PSScriptRoot\..",
    [switch]$InstallEditable
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path $ProjectRoot).Path
$WorkDir = Join-Path $ProjectRoot "work"
$DiffusionPlannerDir = Join-Path $WorkDir "Diffusion-Planner"
$NuplanDevkitDir = Join-Path $WorkDir "nuplan-devkit"

New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null

if (-not (Test-Path $DiffusionPlannerDir)) {
    git clone https://github.com/ZhengYinan-AIR/Diffusion-Planner.git $DiffusionPlannerDir
} else {
    Write-Output "Diffusion-Planner already exists: $DiffusionPlannerDir"
}

if (-not (Test-Path $NuplanDevkitDir)) {
    git clone https://github.com/motional/nuplan-devkit.git $NuplanDevkitDir
} else {
    Write-Output "nuplan-devkit already exists: $NuplanDevkitDir"
}

& "$PSScriptRoot\download_checkpoint.ps1" -RepoRoot $DiffusionPlannerDir

if ($InstallEditable) {
    python -m pip install setuptools==59.5.0 wheel==0.37.1
    python -m pip install --no-build-isolation --no-use-pep517 -e $NuplanDevkitDir
    python -m pip install --no-build-isolation --no-use-pep517 -e $DiffusionPlannerDir
}

Write-Output ""
Write-Output "Bootstrap complete."
Write-Output "Diffusion-Planner: $DiffusionPlannerDir"
Write-Output "nuplan-devkit: $NuplanDevkitDir"

