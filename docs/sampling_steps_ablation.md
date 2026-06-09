# Sampling Steps Ablation

Diffusion-Planner uses DPM-Solver++ sampling during inference. In the official decoder, the default call is:

```python
dpm_sampler(..., diffusion_steps=10)
```

The project script `scripts/benchmark_sampling_steps.py` monkey-patches this value at runtime and measures synthetic inference latency for different step counts.

## Command

```powershell
conda run -n diffusion_planner python .\scripts\benchmark_sampling_steps.py `
  --steps 5,10,20,50 `
  --iterations 5 `
  --batch-size 1 `
  --device cuda
```

Outputs:

```text
results/sampling_steps_ablation.csv
results/sampling_steps_ablation.png
```

## Interpretation boundary

This is a model-side synthetic latency ablation. It is useful for understanding the speed cost of additional denoising steps.

It does not by itself prove closed-loop planning quality, because quality needs a nuPlan rerun for each step count and comparison on scenario metrics such as progress, comfort, collision, speed-limit compliance, and final score.

The next rigorous version would run mini evaluation with several planner configs:

```text
5 steps  -> speed-oriented
10 steps -> official default
20 steps -> near-converged setting noted in the sampler comment
50 steps -> high-cost reference
```
