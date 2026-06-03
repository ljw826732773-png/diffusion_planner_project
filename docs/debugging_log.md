# 环境调试记录

这次复现中最大的工作量不在模型代码，而在环境兼容。

## Python 和包管理

官方 README 使用 Python 3.9。当前机器默认 `python` 指向 Windows Store stub，不适合直接使用，因此使用 Conda 创建环境:

```powershell
conda create -n diffusion_planner python=3.9 pip=21.2.4
```

`nuplan-devkit` 是老式 `setup.py develop` 项目，新版 `setuptools` 会触发兼容问题。因此将工具链固定到:

```text
setuptools==59.5.0
wheel==0.37.1
```

## NumPy 和 TorchVision

`requirements_torch.txt` 会间接安装较新的 NumPy。Torch 2.0.0 和 TorchVision 0.15.1 在 Windows 下与 NumPy 2.x 会出现 ABI 警告，因此固定:

```text
numpy==1.23.4
```

## OpenCV

新版 `opencv-python` 要求 NumPy 2.x，与上面的 Torch 兼容要求冲突。nuPlan 原始依赖要求 `opencv-python<=4.5.1.48`，因此固定:

```text
opencv-python==4.5.1.48
```

## wandb 和 protobuf

训练入口虽然默认不启用 wandb，但代码在 import 阶段就导入它。新版 wandb 会把 `protobuf` 升到 6.x，而 TensorBoard 2.11.2 要求 protobuf 3.x。最终固定:

```text
wandb==0.13.11
protobuf==3.20.3
```

## GIS 依赖

nuPlan 地图模块需要:

```text
geopandas
Fiona
pyogrio
rasterio
rtree
shapely
```

其中 `rasterio 1.4.x` 要求 NumPy 1.24+，因此固定:

```text
rasterio==1.3.9
```

## Windows fcntl 问题

`nuplan-devkit/nuplan/database/maps_db/gpkg_mapsdb.py` 直接导入 Linux/POSIX 模块 `fcntl`，Windows 原生没有。为让导入链路继续走通，在本地 `nuplan-devkit` 中加入 no-op fallback。

这个补丁只解决本地单机验证的导入问题。严格复现实验指标时，仍建议使用 Linux 或 WSL2。

## 当前通过的验证

```text
run_simulation import ok
planner import ok
loaded_params=276
missing=0
unexpected=0
score_isfinite=True
```

