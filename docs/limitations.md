# 当前局限和风险

## 没有完整官方 benchmark 指标

当前已完成 nuPlan mini 上的 1 场景 smoke test、5 场景 baseline evaluation、10 场景 baseline evaluation、5 场景 guidance 对照实验，以及 `guidance_scale=0.1/0.3/0.5/1.0` 小规模扫描。但还没有跑完整官方 challenge split，因此不能声称复现了论文表格中的 Val14/Test14 分数。

当前已配置 mini 数据和地图:

- `NUPLAN_DATA_ROOT=D:\nuplan-data\dataset`
- `NUPLAN_MAPS_ROOT=D:\nuplan-data\dataset\maps`
- `NUPLAN_EXP_ROOT=D:\nuplan-data\exp`

但论文级别评测仍需要更完整的数据 split、场景过滤配置和更大规模评估。

## Synthetic forward 不是性能验证

当前模型前向传播使用 synthetic batch，只能说明:

- 模型结构能运行
- CUDA 能运行
- tensor shape 正确
- 输出没有 NaN/Inf
- checkpoint 能加载

它不能单独说明模型在真实驾驶场景中的规划质量，因此项目进一步接入了 mini closed-loop evaluation。但 mini 结果仍不能替代完整官方 benchmark。

## Windows 不是官方主路径

项目脚本和 nuPlan 生态明显更偏 Linux/bash。Windows 下需要额外兼容处理，尤其是 `fcntl` 和路径格式问题。严格实验建议使用 Linux 或 WSL2。

## 没有重新训练

当前使用官方 checkpoint，没有复现训练过程。重新训练需要大规模 nuPlan 预处理数据和较长 GPU 训练时间。

## 真实场景可视化仍待完善

当前已经提供:

- `visualize_synthetic_trajectory.py`: synthetic scene 轨迹图，只用于模型输出链路验证。
- `visualize_nuplan_trajectory.py`: 从真实 nuPlan simulation log 导出 executed ego、expert ego 和 planner future 对比图。
- `compare_guidance_trajectories.py`: 对同一 scenario 下不同 guidance scale 的 closed-loop executed trajectory 做静态叠加对比。
- `mini10_eval_score_runtime.png`: 评估指标图，不是地图轨迹图。

仍待完善:

- 当前真实轨迹图还没有叠加 lane / route / traffic light 等地图层。
- 多场景批量导出和 NuBoard 截图还没有整理成静态 artifact。
- 静态轨迹图不能直接显示碰撞对象和逐帧交互细节，仍需要 NuBoard 做 frame-level 检查。

## Guidance 结果边界

当前 guidance mini5 已跑通，成功 / 失败为 5 / 0，但默认 `guidance_scale=0.5` 的 final score 从 baseline mini5 的 `0.9254` 降到 `0.7264`。主要退化来自 `stopping_at_stop_sign_with_lead` 场景，该场景 guidance score 为 `0.0000`，并触发 `no_ego_at_fault_collisions=0` 和 `time_to_collision_within_bound=0`。

scale sweep 的 mini5 结果进一步显示:

| Guidance scale | Final score | Stop-sign score | Collision | TTC |
| ---: | ---: | ---: | ---: | ---: |
| 0 baseline | 0.9254 | 1.0000 | 1.0000 | 1.0000 |
| 0.1 | 0.9254 | 1.0000 | 1.0000 | 1.0000 |
| 0.3 | 0.7255 | 0.0000 | 0.8000 | 0.8000 |
| 0.5 | 0.7264 | 0.0000 | 0.8000 | 0.8000 |
| 1.0 | 0.5264 | 0.0000 | 0.6000 | 0.6000 |

stop-sign 失败场景的轨迹复盘显示，baseline executed path length 为 `7.162 m`，scale `0.5` 和 `1.0` 分别增长到 `17.105 m` 和 `20.768 m`，endpoint error 分别为 `11.879 m` 和 `15.423 m`。这说明较强 guidance 在该场景中不仅影响指标，也明显改变了 closed-loop 执行轨迹。

进一步将 collision guidance 内部 multiplier 从 `3.0` 降到 `1.0`，保持外层 `guidance_scale=0.5` 后，mini5 final score 从 `0.7264` 恢复到 `0.9254`，stop-sign 场景从 `0.0000` 恢复到 `1.0000`。这个结果说明 failure 对 guidance 权重敏感，但仍只是 mini5 小样本诊断。

在 10 场景 mini subset 上，`guidance_scale=0.5, collision_weight=1.0` 的 final score 为 `0.9293`，baseline mini10 为 `0.9287`，collision/TTC 都保持 `1.0000`。但该 run 出现明显 runtime outlier：`waiting_for_pedestrian_to_cross` 的 mean compute runtime 为 `33.7791 s`，simulation duration 为 `5041.2444 s`。因此 tuned guidance 仍不能被称为满足实时部署要求。

因此只能说:

- guidance 配置路径已打通。
- guidance closed-loop 对照实验已完成。
- guidance scale sweep 已完成。
- guidance 失败场景的静态轨迹复盘已完成。
- collision guidance weight tuning 已完成一个 mini5 诊断版本。
- tuned guidance 已扩展到 mini10 进行小规模验证。
- 当前结果显示 guidance 需要继续定位 runtime outlier，并在更大场景子集上验证约束权重、触发时机和失败场景处理。

不能说:

- guidance 已经带来性能提升。
- collision guidance 在当前设置下更安全。
- mini5 小样本结论可以外推到完整 benchmark。

## 结果表述边界

可以说:

- 复现并验证了 Diffusion-Planner 核心模型链路
- 完成官方 checkpoint 加载和 CUDA 前向推理
- 打通 nuPlan planner 入口导入
- 完成 nuPlan mini 小规模 closed-loop baseline 和 guidance evaluation
- 完成低分场景、延迟、采样步数和真实轨迹分析
- 解决多类依赖兼容问题

不建议说:

- 完整复现论文指标
- 在 nuPlan benchmark 上达到论文性能
- 完成模型训练
- 完成官方 full split 大规模评测
