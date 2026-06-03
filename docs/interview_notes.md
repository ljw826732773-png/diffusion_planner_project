# 面试讲解材料

## 30 秒版本

我复现了 ICLR 2025 的 Diffusion-Planner 自动驾驶规划项目。这个项目用扩散模型生成未来轨迹，把自车规划和周围车辆预测统一到一个 trajectory generation 框架里。我完成了 nuPlan-devkit 集成、PyTorch/CUDA 环境搭建、官方 checkpoint 加载、GPU 前向推理验证和 planner 入口验证，并整理了可复现脚本和文档。

## 2 分钟版本

这个项目的核心问题是自动驾驶规划。传统规划方法通常把预测和规划拆开做，而 Diffusion-Planner 将 ego vehicle 和关键邻车的未来轨迹一起建模，用 diffusion model 从噪声中逐步生成未来轨迹。

我复现时没有直接跑大脚本，而是按工程链路逐层验证。首先搭建 Python 3.9 和 PyTorch 2.0/CUDA 11.8 环境，然后安装 `nuplan-devkit` 和 Diffusion-Planner。中间解决了 NumPy/TorchVision ABI、OpenCV/NumPy、protobuf/wandb、GIS 依赖、Windows `fcntl` 等兼容问题。

验证上，我做了三步。第一步验证 Torch/CUDA 可用。第二步用 synthetic batch 跑通模型前向传播，确认 encoder 输出和 decoder 输出 shape 正确，并且没有 NaN。第三步加载官方 HuggingFace checkpoint，确认 276 个权重张量完整匹配，missing 和 unexpected 都是 0。最后也验证了 nuPlan 的 `run_simulation` 入口和 DiffusionPlanner 类可以导入。

这个项目目前还没有跑完整 nuPlan closed-loop 指标，因为缺少官方数据集和 maps。下一步我会接入 nuPlan mini 或 val14 子集，跑小规模闭环仿真，并补充轨迹可视化和推理速度 benchmark。

## 常见追问

### 为什么 diffusion 适合规划?

因为驾驶未来具有多模态性。同一场景下可能有多个合理决策，比如减速、等待、绕行、跟车。扩散模型适合学习复杂分布，可以用场景上下文作为条件，从噪声中生成合理轨迹。

### Diffusion-Planner 的输入是什么?

主要包括自车当前状态、邻车历史状态、局部车道地图、route lanes、静态障碍物、限速和 traffic light 相关信息。

### 输出是什么?

输出 ego vehicle 和若干关键邻车的未来轨迹。每个状态包含 `x, y, cos(heading), sin(heading)`。

### 你具体解决了什么工程问题?

我解决了研究代码常见的环境碎片化问题，包括 PyTorch/CUDA 版本、NumPy ABI、OpenCV 版本、wandb/protobuf 冲突、nuPlan GIS 依赖，以及 Windows 下缺少 `fcntl` 的问题。

### 你没有完成什么?

我没有跑完整 closed-loop benchmark，也没有重新训练模型。当前完成的是核心模型链路和官方 checkpoint 验证。完整指标需要先下载并配置 nuPlan 数据集和 maps。

### 下一步怎么做?

第一步接入 nuPlan mini 或 val14 子集，跑少量 closed-loop simulation。第二步生成 nuBoard 或自定义轨迹可视化。第三步做推理延迟和采样步数 ablation。

