# 下一步实验计划

## 1. 接入 nuPlan mini

目标: 从 synthetic forward 升级到真实场景验证。

当前状态:

- 已下载 nuPlan mini 和 maps 到 `D:\nuplan-data`，没有放在 C 盘。
- 已配置 `NUPLAN_DATA_ROOT`、`NUPLAN_MAPS_ROOT`、`NUPLAN_EXP_ROOT`。
- 已完成 1 场景 closed-loop smoke test。
- 已完成 5 场景和 10 场景 mini closed-loop evaluation。
- 已生成 `results/mini_eval_summary.md`、runner report、aggregated metrics 和 metric scores。

当前结果:

- mini5 成功 / 失败: 5 / 0，final weighted score: 0.9254
- mini10 成功 / 失败: 10 / 0，final weighted score: 0.9287
- mini10 mean simulation duration: 77.4598 s
- mini10 mean trajectory runtime: 0.4673 s

后续产出:

- 15 个以上真实 scenario 的 closed-loop simulation 结果
- 多场景真实轨迹图
- guidance 失败案例复盘

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
- 已完成采样步数 synthetic ablation、CPU smoke test 和真实 runner latency summary
- 后续可扩展为真实 scenario 输入的分步 profile

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
- baseline vs guidance 对比图

当前状态:

- 已完成 guidance mini5 closed-loop run，成功 / 失败: 5 / 0。
- guidance mini5 final weighted score: 0.7264。
- baseline mini5 final weighted score: 0.9254。
- 主要退化来自 `stopping_at_stop_sign_with_lead` 场景，guidance score 为 0，触发 collision/TTC/comfort 相关扣分。
- 已完成 `guidance_scale=0.1/0.3/0.5/1.0` 扫描。
- scale `0.1` 保持 baseline 级别 final score；scale `0.3/0.5/1.0` 都让 stop-sign 场景 score 掉到 0。
- 已完成 stop-sign 失败场景轨迹复盘，scale `0.5/1.0` 的 executed path length 明显长于 baseline。
- 已完成 collision guidance weight tuning：`guidance_scale=0.5, collision_weight=1.0` 在 mini5 上将 final score 从默认 guidance 的 `0.7264` 恢复到 `0.9254`。
- 已完成 tuned guidance mini10 验证：10 / 0 成功，final score `0.9293`，baseline mini10 为 `0.9287`。
- 当前主要问题从 score 退化转为 runtime outlier：`waiting_for_pedestrian_to_cross` mean compute runtime `33.7791 s`。

后续方向:

- 定位 `waiting_for_pedestrian_to_cross` 的 runtime outlier，检查 guidance 梯度计算、agent 数量和场景长度。
- 如果新的失败集中在特定类型，继续调 collision guidance 的触发时间窗或场景条件。
- 在调整 guidance 函数后复跑同一组 scale/weight sweep，避免只看单点结果。

## 5. 项目发布整理

目标: 让项目更像正式作品。

补充:

- GitHub README
- `environment.yml`
- 一键验证脚本
- 结果截图
- 局限说明
- 结果复盘和局限说明
