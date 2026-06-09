# Guidance Demo Notes

Diffusion-Planner includes a classifier-guidance path. The planner config `diffusion_planner_guidance.yaml` wires:

```yaml
guidance_fn:
  _target_: diffusion_planner.model.guidance.guidance_wrapper.GuidanceWrapper
```

At inference time the decoder passes the guidance function to DPM-Solver as classifier guidance with `guidance_scale=0.5`.

## Official entry points

- `diffusion_planner/config/planner/diffusion_planner_guidance.yaml`
- `diffusion_planner/model/guidance/guidance_wrapper.py`
- `diffusion_planner/model/guidance/collision.py`
- `diffusion_planner/model/guidance/documentation_guidance.md`
- `sim_guidance_demo.sh`

## Windows command sketch

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
  -Planner "diffusion_planner_guidance"
```

## Current boundary

The base planner has been verified on five mini scenarios. The guidance path has been traced and documented, but it still needs a separate closed-loop run and side-by-side metric comparison before claiming an improvement.

Suggested comparison:

| Run | Planner config | Expected output |
| --- | --- | --- |
| baseline | `diffusion_planner` | current mini evaluation |
| guidance | `diffusion_planner_guidance` | comfort / collision / speed-limit comparison |

The key thing to watch is not only final score. Guidance can reduce one risk metric while increasing latency or changing comfort, so it should be evaluated as a trade-off.
