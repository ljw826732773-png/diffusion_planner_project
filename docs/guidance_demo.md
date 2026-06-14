# Guidance Demo Notes

Diffusion-Planner includes a classifier-guidance path. The planner config `diffusion_planner_guidance.yaml` wires:

```yaml
guidance_fn:
  _target_: diffusion_planner.model.guidance.guidance_wrapper.GuidanceWrapper
```

At inference time the decoder passes the guidance function to DPM-Solver as classifier guidance. The upstream code uses `guidance_scale=0.5` and an internal collision guidance multiplier of `3.0`; this project adds a small patch helper so the scale and collision weight can be controlled through `DP_GUIDANCE_SCALE` and `DP_COLLISION_GUIDANCE_WEIGHT` for diagnostic sweeps.

## Official entry points

- `diffusion_planner/config/planner/diffusion_planner_guidance.yaml`
- `diffusion_planner/model/guidance/guidance_wrapper.py`
- `diffusion_planner/model/guidance/collision.py`
- `diffusion_planner/model/guidance/documentation_guidance.md`
- `sim_guidance_demo.sh`

## Windows command

The guidance planner can be selected by replacing the planner config in a nuPlan simulation run:

```powershell
conda run -n diffusion_planner powershell -ExecutionPolicy Bypass `
  -File .\scripts\run_mini_eval.ps1 `
  -NuplanDataRoot "D:\nuplan-data\dataset" `
  -NuplanMapsRoot "D:\nuplan-data\dataset\maps" `
  -NuplanExpRoot "D:\nuplan-data\exp" `
  -ScenarioBuilder "nuplan_mini" `
  -ScenarioFilter "one_of_each_scenario_type" `
  -Worker "sequential" `
  -LimitTotalScenarios 5 `
  -ExperimentUid "dp/guidance_mini5/model" `
  -SummaryPrefix "guidance_mini5_eval" `
  -Planner "diffusion_planner_guidance" `
  -GuidanceScale 0.5 `
  -GuidanceWeight 1.0
```

## Local result

The guidance run has been executed on the same five mini scenario tokens as the baseline mini5 run.

| Run | Scenarios | Success / Fail | Final score | Mean compute runtime |
| --- | ---: | ---: | ---: | ---: |
| baseline mini5 | 5 | 5 / 0 | 0.9254 | 0.8146 s |
| guidance mini5 | 5 | 5 / 0 | 0.7264 | 0.4459 s |

The guidance run completed successfully, but it reduced the mini5 final score. The main regression was:

| Scenario type | Baseline | Guidance | Main limiting metrics |
| --- | ---: | ---: | --- |
| `stopping_at_stop_sign_with_lead` | 1.0000 | 0.0000 | `ego_is_comfortable=0`, `no_ego_at_fault_collisions=0`, `time_to_collision_within_bound=0` |

This means guidance is not automatically better. On this mini split, the collision/TTC-related hard failure outweighed the small progress improvement in another scenario.

## Guidance scale sweep

The same five mini scenario tokens were also evaluated with `guidance_scale=0.1/0.3/0.5/1.0`, using the baseline run as scale `0`.

| Guidance scale | Final score | Collision | TTC | Comfort | Stop-sign score | Mean runtime |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 baseline | 0.9254 | 1.0000 | 1.0000 | 0.6000 | 1.0000 | 0.8146 s |
| 0.1 | 0.9254 | 1.0000 | 1.0000 | 0.6000 | 1.0000 | 0.7147 s |
| 0.3 | 0.7255 | 0.8000 | 0.8000 | 0.6000 | 0.0000 | 0.5042 s |
| 0.5 | 0.7264 | 0.8000 | 0.8000 | 0.4000 | 0.0000 | 0.4459 s |
| 1.0 | 0.5264 | 0.6000 | 0.6000 | 0.4000 | 0.0000 | 0.4571 s |

Interpretation:

- Scale `0.1` keeps the baseline-level score on this mini subset.
- Scales `0.3`, `0.5`, and `1.0` all turn the stop-sign scenario into a hard failure.
- Scale `1.0` further degrades aggregate collision and TTC scores, so stronger guidance is not safer under this setup.
- These results are diagnostics for the mini subset, not full benchmark conclusions.

## Stop-sign trajectory inspection

The failing stop-sign scenario was inspected by overlaying the executed ego trajectory from baseline and all guidance scale runs.

| Run | Score | Executed path length | Avg error to expert | Endpoint error |
| --- | ---: | ---: | ---: | ---: |
| baseline | 1.0000 | 7.162 m | 1.388 m | 1.965 m |
| scale 0.1 | 1.0000 | 7.382 m | 1.560 m | 2.182 m |
| scale 0.3 | 0.0000 | 8.699 m | 2.740 m | 3.489 m |
| scale 0.5 | 0.0000 | 17.105 m | 7.971 m | 11.879 m |
| scale 1.0 | 0.0000 | 20.768 m | 9.752 m | 15.423 m |

This gives a useful failure hypothesis: stronger collision guidance pushes the executed path much farther than the successful baseline/scale-0.1 runs. The static plot does not prove the exact collision partner or frame, but it narrows the next debug target to guidance weighting, timing, and stop-sign interaction behavior.

## Collision weight tuning

The internal collision guidance multiplier was then reduced from `3.0` to `1.0`, while keeping the outer DPM-Solver `guidance_scale=0.5`.

| Run | Final score | Collision | TTC | Comfort | Stop-sign score | Mean runtime |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 0.9254 | 1.0000 | 1.0000 | 0.6000 | 1.0000 | 0.8146 s |
| guidance scale 0.5, weight 3.0 | 0.7264 | 0.8000 | 0.8000 | 0.4000 | 0.0000 | 0.4459 s |
| guidance scale 0.5, weight 1.0 | 0.9254 | 1.0000 | 1.0000 | 0.6000 | 1.0000 | 0.4391 s |

On this mini5 subset, reducing the internal collision weight recovers the stop-sign hard failure and restores the final score to the baseline level. It does not prove that guidance is better than baseline; it shows that the original failure is sensitive to guidance weighting and can be debugged systematically.

## Tuned guidance mini10

The tuned guidance setting was then validated on the existing 10-scenario mini subset.

| Run | Scenarios | Success / Fail | Final score | Collision | TTC | Mean runtime | Median runtime |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline mini10 | 10 | 10 / 0 | 0.9287 | 1.0000 | 1.0000 | 0.4673 s | 0.4327 s |
| guidance scale 0.5, weight 1.0 mini10 | 10 | 10 / 0 | 0.9293 | 1.0000 | 1.0000 | 4.0871 s | 0.7581 s |

The tuned guidance score is essentially tied with the baseline on this subset. It preserves collision and TTC metrics, but it introduces a runtime outlier: `waiting_for_pedestrian_to_cross` has mean compute runtime `33.7791 s` and simulation duration `5041.2444 s`.

The outlier report adds two important details:

- The same scenario has baseline mean runtime `0.4761 s`.
- The tuned guidance median runtime is only `0.7389 s`, so the high mean is likely caused by one or a few very slow planner calls rather than every frame being slow.

Outputs:

- `results/guidance_mini5_eval_summary.md`
- `results/guidance_mini5_eval_low_score_analysis.md`
- `results/guidance_mini5_eval_latency_summary.md`
- `results/guidance_vs_baseline_mini5.md`
- `results/guidance_vs_baseline_mini5.png`
- `results/guidance_scale_sweep.md`
- `results/guidance_scale_sweep.csv`
- `results/guidance_scale_sweep.png`
- `results/guidance_stop_sign_trajectory_comparison.md`
- `results/guidance_stop_sign_trajectory_comparison.csv`
- `results/guidance_stop_sign_trajectory_comparison.png`
- `results/guidance_w10_mini5_eval_summary.md`
- `results/guidance_weight_vs_default_mini5.md`
- `results/guidance_weight_vs_default_mini5.png`
- `results/guidance_weight_vs_baseline_mini5.md`
- `results/guidance_weight_stop_sign_trajectory_comparison.md`
- `results/guidance_weight_stop_sign_trajectory_comparison.png`
- `results/guidance_w10_mini10_eval_summary.md`
- `results/guidance_w10_mini10_eval_latency_summary.md`
- `results/guidance_w10_mini10_runtime_outliers.md`
- `results/guidance_w10_vs_baseline_mini10.md`
- `results/guidance_w10_vs_baseline_mini10.png`

## Next boundary

The next useful experiment is frame-level profiling for `waiting_for_pedestrian_to_cross`, then deciding whether guidance should be disabled, clipped, or weakened under that interaction pattern.
