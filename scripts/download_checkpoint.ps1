param(
    [string]$RepoRoot = "$PSScriptRoot\..\..\..\work\Diffusion-Planner"
)

$ErrorActionPreference = "Stop"

$CheckpointDir = Join-Path $RepoRoot "checkpoints"
New-Item -ItemType Directory -Force -Path $CheckpointDir | Out-Null

Invoke-WebRequest `
    -Uri "https://huggingface.co/ZhengYinan2001/Diffusion-Planner/resolve/main/args.json" `
    -OutFile (Join-Path $CheckpointDir "args.json")

Invoke-WebRequest `
    -Uri "https://huggingface.co/ZhengYinan2001/Diffusion-Planner/resolve/main/model.pth" `
    -OutFile (Join-Path $CheckpointDir "model.pth")

Get-ChildItem $CheckpointDir | Select-Object Name,Length

