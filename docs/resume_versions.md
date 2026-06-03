# 简历写法

## 自动驾驶算法岗版本

基于 Diffusion-Planner 的自动驾驶轨迹规划复现与分析

- 复现 ICLR 2025 Diffusion-Planner 自动驾驶规划模型，完成 nuPlan-devkit 集成、官方 checkpoint 加载和 CUDA 前向推理验证。
- 理解并梳理 DiT-based trajectory generation、multi-agent context encoding、ego planning 与 neighbor prediction 联合建模流程。
- 解决 PyTorch/CUDA、NumPy/OpenCV、protobuf/wandb、GIS 依赖及 Windows 兼容问题，沉淀可复现脚本和项目文档。

## 深度学习算法岗版本

Diffusion-Based Trajectory Generation 复现项目

- 搭建 PyTorch 2.0 + CUDA 11.8 环境，复现扩散模型在自动驾驶轨迹生成任务中的核心推理链路。
- 加载官方 checkpoint 并完成模型结构匹配验证，确认 276 个权重张量完整加载，missing/unexpected 均为 0。
- 基于 synthetic multi-agent batch 验证模型前向传播，输出形状为 `(1, 11, 81, 4)`，数值稳定无 NaN/Inf。

## 机器学习工程岗版本

研究代码工程化复现: Diffusion-Planner

- 将 Diffusion-Planner 和 nuPlan-devkit 研究代码整理为可运行项目包，提供环境配置、checkpoint 下载、前向验证和可视化脚本。
- 排查并修复多类依赖冲突，包括 setuptools、NumPy ABI、OpenCV、protobuf、wandb、GIS wheel 和 Windows POSIX 兼容问题。
- 编写项目 README、架构说明、调试记录、局限分析和面试讲解材料，提高项目可维护性和可展示性。

## 英文版本

Diffusion-Planner Reproduction and Analysis

- Reproduced Diffusion-Planner, an ICLR 2025 diffusion-based autonomous driving planner, by integrating nuPlan-devkit, setting up PyTorch/CUDA dependencies, and validating official checkpoint loading.
- Verified GPU forward inference with synthetic multi-agent inputs, producing stable trajectory outputs with shape `(1, 11, 81, 4)`.
- Resolved dependency conflicts across PyTorch, NumPy, OpenCV, protobuf, wandb, geospatial libraries, and Windows compatibility, and packaged the workflow into reusable scripts and documentation.

