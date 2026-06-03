# nuPlan 数据集接入说明

当前项目已经打通模型、checkpoint 和 planner 入口，但完整 closed-loop simulation 还需要 nuPlan 官方数据集和地图文件。

## 需要的环境变量

PowerShell:

```powershell
$env:NUPLAN_DATA_ROOT="D:\data\nuplan"
$env:NUPLAN_MAPS_ROOT="D:\data\nuplan\maps"
$env:NUPLAN_EXP_ROOT="D:\data\nuplan\exp"
```

官方默认结构通常是:

```text
<NUPLAN_DATA_ROOT>
  maps
    nuplan-maps-v1.0.json
    sg-one-north\9.17.1964\map.gpkg
    us-ma-boston\9.12.1817\map.gpkg
    us-nv-las-vegas-strip\9.15.1915\map.gpkg
    us-pa-pittsburgh-hazelwood\9.17.1937\map.gpkg
  nuplan-v1.1
    splits
      mini
        *.db
    trainval
      *.db
    test
      *.db
    sensor_blobs
```

如果 `maps` 放在 `NUPLAN_DATA_ROOT\maps`，那么:

```powershell
$env:NUPLAN_MAPS_ROOT="$env:NUPLAN_DATA_ROOT\maps"
```

## 检查数据是否就绪

```powershell
outputs\diffusion_planner_project\scripts\check_nuplan_data.ps1 `
  -NuplanDataRoot "D:\data\nuplan" `
  -NuplanMapsRoot "D:\data\nuplan\maps" `
  -NuplanExpRoot "D:\data\nuplan\exp"
```

检查项:

- 数据根目录是否存在
- maps 根目录是否存在
- exp 根目录是否存在
- `mini` / `trainval` / `test` 下是否有 `.db`
- maps metadata 是否存在
- 是否找到 4 个 `map.gpkg`

## mini 数据优先

建议先用 mini 子集验证链路:

```powershell
python "$env:NUPLAN_DEVKIT_ROOT\nuplan\planning\script\run_simulation.py" `
  +simulation=closed_loop_nonreactive_agents `
  planner=diffusion_planner `
  planner.diffusion_planner.config.args_file="work\Diffusion-Planner\checkpoints\args.json" `
  planner.diffusion_planner.ckpt_path="work\Diffusion-Planner\checkpoints\model.pth" `
  scenario_builder=nuplan_mini `
  scenario_filter=val14 `
  experiment_uid=diffusion_planner/mini/local/model `
  verbose=true `
  worker=ray_distributed `
  worker.threads_per_node=8 `
  distributed_mode=SINGLE_NODE `
  number_of_gpus_allocated_per_simulation=0.15 `
  enable_simulation_progress_bar=true `
  hydra.searchpath="[pkg://diffusion_planner.config.scenario_filter, pkg://diffusion_planner.config, pkg://nuplan.planning.script.config.common, pkg://nuplan.planning.script.experiments]"
```

如果 `scenario_filter=val14` 在 mini 数据上没有匹配场景，需要改用项目内已有的更小 filter，或者先用 nuPlan 自带示例配置验证 scenario builder。

## 重要边界

完整复现论文指标通常需要 trainval/test splits 和官方场景过滤配置。mini 子集更适合做链路验证，不适合声称复现论文分数。

