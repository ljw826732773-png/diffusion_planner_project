# 推理 Benchmark

这个 benchmark 用 synthetic scene 输入评估 Diffusion-Planner 的本地推理链路。

## 两种模式

### denoise_forward

训练态单次去噪网络前向。它不执行完整 DPM sampling，只衡量 encoder + decoder 主干的一次 forward latency。

适合说明:

- 模型结构在本机 GPU 上可运行
- 单次网络前向延迟
- batch size 对模型主干吞吐的影响

### sampling_inference

eval 模式下的完整采样推理链路。它会走 `dpm_sampler`，默认 10 个 diffusion steps，更接近 planner 真实推理。

适合说明:

- 扩散采样推理比单次 forward 更耗时
- sampling steps 是 diffusion planner 的主要延迟来源
- 后续可以做采样步数和轨迹质量折中实验

## 运行

```powershell
conda activate diffusion_planner
python outputs\diffusion_planner_project\scripts\benchmark_inference.py
```

输出:

```text
outputs\diffusion_planner_project\results\inference_benchmark.csv
outputs\diffusion_planner_project\results\inference_benchmark.png
```

## 当前结果

测试硬件:

```text
NVIDIA GeForce RTX 3060 Laptop GPU
torch 2.0.0+cu118
```

运行命令:

```powershell
python outputs\diffusion_planner_project\scripts\benchmark_inference.py --batch-sizes 1,2,4 --iterations 50 --sampling-iterations 20
```

| Mode | Batch | Mean Latency | Calls/s | Samples/s | Peak CUDA Memory |
| --- | ---: | ---: | ---: | ---: | ---: |
| denoise_forward | 1 | 16.20 ms | 61.73 | 61.73 | 90.1 MB |
| sampling_inference | 1 | 84.04 ms | 11.90 | 11.90 | 89.6 MB |
| denoise_forward | 2 | 17.72 ms | 56.44 | 112.87 | 101.2 MB |
| sampling_inference | 2 | 89.84 ms | 11.13 | 22.26 | 99.9 MB |
| denoise_forward | 4 | 21.84 ms | 45.79 | 183.15 | 125.1 MB |
| sampling_inference | 4 | 92.01 ms | 10.87 | 43.47 | 122.8 MB |

## 结果解读

单次去噪网络前向约 16-22 ms，而完整 sampling inference 约 84-92 ms。二者相差约 4-5 倍，说明 diffusion planner 的主要推理开销来自多步采样。

batch size 从 1 增加到 4 时，调用延迟变化不大，但 sampling 样本吞吐从 11.90 samples/s 提升到 43.47 samples/s。这说明在 synthetic batch 场景下，GPU 还有一定并行余量。

运行时 PyTorch 提示 attention mask dtype 转换:

```text
Converting mask without torch.bool dtype to bool; this will negatively affect performance.
```

这可以作为后续优化点: 检查 attention mask 的 dtype，减少运行时隐式转换。

## 注意

当前 benchmark 使用 synthetic inputs，不代表真实 nuPlan 场景上的 closed-loop 指标。它主要用于工程验证和速度分析。

完整实验仍需要真实 nuPlan 数据集和 maps。
