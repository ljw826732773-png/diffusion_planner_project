# Device and Latency Notes

The project now tracks three latency views:

1. Synthetic model benchmark:
   - `results/inference_benchmark.csv`
   - `results/inference_benchmark.png`
2. Synthetic sampling-steps ablation:
   - `results/sampling_steps_ablation.csv`
   - `results/sampling_steps_ablation.png`
3. Real closed-loop planner runtime from nuPlan runner report:
   - `results/mini_eval_latency_summary.csv`
   - `results/mini_eval_latency_summary.md`

## CPU smoke test

The benchmark script supports explicit device selection:

```powershell
conda run -n diffusion_planner python .\scripts\benchmark_inference.py `
  --batch-sizes 1 `
  --modes denoise_forward `
  --warmup 1 `
  --iterations 3 `
  --device cpu `
  --output-prefix device_latency_cpu_smoke
```

Current CPU smoke result:

```text
denoise_forward bs=1 mean=133.23 ms
```

The earlier CUDA benchmark measured denoise forward at about 16.20 ms for batch size 1 on an RTX 3060 Laptop GPU.

## Interpretation boundary

- The CPU test is intentionally small. It verifies that the benchmark path works on CPU, but it is not a full production latency study.
- The CUDA synthetic benchmark measures model-side inference with synthetic tensors.
- The nuPlan runner report measures planner `compute_trajectory` inside closed-loop simulation and is closer to real evaluation behavior.
