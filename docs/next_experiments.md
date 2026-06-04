# 下一步实验计划

## 1. 接入 nuPlan mini

目标: 从 synthetic forward 升级到真实场景验证。

当前状态:

- 已下载 nuPlan mini 和 maps 到 `D:\nuplan-data`，没有放在 C 盘。
- 已配置 `NUPLAN_DATA_ROOT`、`NUPLAN_MAPS_ROOT`、`NUPLAN_EXP_ROOT`。
- 已完成 1 场景 closed-loop smoke test。
- 已完成 3 场景 mini closed-loop evaluation。
- 已生成 `results/mini_eval_summary.md`、runner report、aggregated metrics 和 metric scores。

当前结果:

- 成功 / 失败: 3 / 0
- final weighted score: 0.905
- mean simulation duration: 51.502 s
- mean trajectory runtime: 0.3074 s

后续产出:

- 至少 5 个真实 scenario 的 closed-loop simulation 结果
- 轨迹截图
- 失败案例分析

## 2. 推理速度 benchmark

目标: 展示工程分析能力。

指标:

- 单次 forward latency
- FPS
- GPU memory
- CPU vs CUDA 对比
- batch size 对 latency 的影响

产出:

- `results/inference_latency.csv`
- `results/inference_latency.png`

当前状态:

- 已完成 synthetic benchmark
- 已输出 `results/inference_benchmark.csv`
- 已输出 `results/inference_benchmark.png`
- 后续可扩展为采样步数、CPU/GPU、真实 scenario 输入的对比实验

## 3. 采样步数 ablation

目标: 分析 diffusion sampling 的速度和质量折中。

对比:

- 5 steps
- 10 steps
- 20 steps
- 50 steps

产出:

- 延迟对比
- 轨迹平滑度对比
- 失败案例截图

## 4. Guidance demo

目标: 贴近论文亮点。

对比:

- no guidance
- collision guidance

产出:

- 轨迹可视化
- 碰撞风险解释
- 面试讲解图

## 5. 项目发布整理

目标: 让项目更像正式作品。

补充:

- GitHub README
- `environment.yml`
- 一键验证脚本
- 结果截图
- 局限说明
- 简历 bullet
