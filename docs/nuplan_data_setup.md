# nuPlan 数据集接入说明

当前项目已经打通模型、checkpoint 和 planner 入口，但完整 closed-loop simulation 还需要 nuPlan 官方数据集和地图文件。

## 需要的环境变量

PowerShell:

```powershell
$env:NUPLAN_DATA_ROOT="D:\nuplan-data\dataset"
$env:NUPLAN_MAPS_ROOT="D:\nuplan-data\dataset\maps"
$env:NUPLAN_EXP_ROOT="D:\nuplan-data\exp"
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

如果使用 AWS Open Data 公开镜像，可以先下载 mini 和 maps:

```powershell
scripts\download_nuplan_mini.ps1
```

该脚本会下载:

- `nuplan-maps-v1.0.zip`，约 0.97 GB
- `nuplan-v1.1_mini.zip`，约 8.55 GB

默认解压到:

```text
D:\nuplan-data\dataset
```

也可以指定路径:

```powershell
scripts\download_nuplan_mini.ps1 -DatasetRoot "D:\nuplan-data\dataset"
```

下载源来自 AWS Open Data Registry 的 `motional-nuplan` bucket。

注意: AWS mini zip 解压后，`.db` 文件实际位于:

```text
D:\nuplan-data\dataset\data\cache\mini
```

而 nuPlan devkit 的 `scenario_builder=nuplan_mini` 默认读取:

```text
D:\nuplan-data\dataset\nuplan-v1.1\splits\mini
```

所以 `download_nuplan_mini.ps1` 会自动创建 junction:

```text
D:\nuplan-data\dataset\nuplan-v1.1\splits\mini -> D:\nuplan-data\dataset\data\cache\mini
```

这样不会重复复制 8GB 数据，也能满足 nuPlan 的目录约定。

```powershell
outputs\diffusion_planner_project\scripts\check_nuplan_data.ps1 `
  -NuplanDataRoot "D:\nuplan-data\dataset" `
  -NuplanMapsRoot "D:\nuplan-data\dataset\maps" `
  -NuplanExpRoot "D:\nuplan-data\exp"
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
  scenario_filter=one_of_each_scenario_type `
  scenario_filter.limit_total_scenarios=1 `
  experiment_uid=dp/mini/model `
  verbose=true `
  worker=sequential `
  distributed_mode=SINGLE_NODE `
  number_of_gpus_allocated_per_simulation=0.15 `
  enable_simulation_progress_bar=true `
  hydra.searchpath="[pkg://diffusion_planner.config.scenario_filter, pkg://diffusion_planner.config, pkg://nuplan.planning.script.config.common, pkg://nuplan.planning.script.experiments]"
```

如果要跑论文 `val14/test14` 相关配置，需要使用更完整的数据 split。mini 子集优先用于验证数据读取、planner 初始化、仿真闭环和输出目录是否贯通。

Windows 下建议保持 `experiment_uid` 较短。nuPlan 的 simulation log 路径会拼接 challenge、场景类型、log name 和 scenario token，过长时可能触发 260 字符路径限制。

## 当前本机验证状态

截至当前项目化版本，本机已确认:

- mini 数据下载在 `D:\nuplan-data\dataset`，不在 C 盘。
- mini `.db` 文件数量: 64。
- 地图 metadata 和 4 个城市 `map.gpkg` 已就绪。
- `nuplan-v1.1\splits\mini` 已通过 junction 指向 AWS 解压出的 mini 数据目录。
- `D:\nuplan-data\exp` 已作为仿真输出目录。

## 重要边界

完整复现论文指标通常需要 trainval/test splits 和官方场景过滤配置。mini 子集更适合做链路验证，不适合声称复现论文分数。
