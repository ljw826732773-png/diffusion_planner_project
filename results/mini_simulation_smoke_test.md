# nuPlan mini closed-loop smoke test

This file records the local nuPlan mini smoke test used to verify that the
project can go beyond synthetic model forward checks and run a real nuPlan
closed-loop simulation pipeline.

## Test command

```powershell
conda run -n diffusion_planner powershell -ExecutionPolicy Bypass `
  -File .\scripts\run_simulation_template.ps1 `
  -NuplanDataRoot "D:\nuplan-data\dataset" `
  -NuplanMapsRoot "D:\nuplan-data\dataset\maps" `
  -NuplanExpRoot "D:\nuplan-data\exp" `
  -ScenarioBuilder "nuplan_mini" `
  -Split "one_of_each_scenario_type" `
  -Worker "sequential" `
  -LimitTotalScenarios 1 `
  -ExperimentUid "dp/mini/model"
```

## Local data layout

- `NUPLAN_DATA_ROOT`: `D:\nuplan-data\dataset`
- `NUPLAN_MAPS_ROOT`: `D:\nuplan-data\dataset\maps`
- `NUPLAN_EXP_ROOT`: `D:\nuplan-data\exp`
- Mini db files: 64
- Maps: 4 city `map.gpkg` files plus `nuplan-maps-v1.0.json`
- `nuplan-v1.1\splits\mini` is a Windows junction to AWS extracted `data\cache\mini`

## Result

The one-scenario closed-loop nonreactive simulation completed successfully.

| Field | Value |
| --- | --- |
| challenge | `closed_loop_nonreactive_agents` |
| scenario_filter | `one_of_each_scenario_type` |
| limit_total_scenarios | `1` |
| worker | `sequential` |
| successful simulations | `1` |
| failed simulations | `0` |
| scenario type | `near_multiple_vehicles` |
| log name | `2021.06.08.14.35.24_veh-26_02555_03004` |
| scenario token | `1f151e15c9cf5c81` |
| planner | `diffusion_planner` |
| simulation duration | `54.19 s` |
| mean compute trajectory runtime | `0.328 s` |
| median compute trajectory runtime | `0.285 s` |

Generated local artifacts:

- `runner_report.parquet`
- `summary\summary.pdf`
- `simulation_log\...\1f151e15c9cf5c81.msgpack.xz`
- `metrics\*.parquet`
- `nuboard_*.nuboard`

## Notes

- This smoke test verifies data loading, map loading, Hydra configuration,
  checkpoint-backed planner initialization, closed-loop simulation execution,
  metric generation, simulation log writing, and result export.
- This is not a paper-score reproduction. It uses the mini split and only one
  scenario. Full benchmark claims require the official challenge split and
  larger-scale scenario evaluation.
- On Windows, keep `experiment_uid` short. nuPlan simulation logs include
  challenge, scenario type, log name, token, and file name in the output path,
  so long experiment names can hit the 260-character path limit.
