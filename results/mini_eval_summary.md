# nuPlan mini evaluation summary

- generated_at: `2026-06-04 17:04:14`
- run_root: `D:\nuplan-data\exp\exp\simulation\closed_loop_nonreactive_agents\dp\mini3\model`
- aggregator_file: `closed_loop_nonreactive_agents_weighted_average_metrics_2026.06.04.16.58.06.parquet`

## Run status

| total | succeeded | failed | mean_duration_s | mean_compute_runtime_s | median_compute_runtime_s |
| --- | --- | --- | --- | --- | --- |
| 3 | 3 | 0 | 51.502 | 0.3074 | 0.2824 |

## Final score

| score |
| --- |
| 0.905 |

## Aggregated metric components

| metric | value |
| --- | --- |
| drivable_area_compliance | 1 |
| driving_direction_compliance | 1 |
| ego_is_comfortable | 0.6667 |
| ego_is_making_progress | 1 |
| ego_progress_along_expert_route | 1 |
| no_ego_at_fault_collisions | 1 |
| speed_limit_compliance | 0.7867 |
| time_to_collision_within_bound | 1 |

## Scenario runner report

| succeeded | scenario_name | scenario_type | score | log_name | planner | duration_s | mean_runtime_s | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| True | 1f151e15c9cf5c81 | near_multiple_vehicles | 0.875 | 2021.06.08.14.35.24_veh-26_02555_03004 | diffusion_planner | 63.338 | 0.382 |  |
| True | 6e256d585b245983 | starting_unprotected_cross_turn | 0.84 | 2021.06.09.14.58.55_veh-35_01894_02311 | diffusion_planner | 42.5671 | 0.2484 |  |
| True | aa8237ebd54f5a0b | starting_protected_noncross_turn | 1 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 48.6008 | 0.2917 |  |

## Metric files

| metric_rows |
| --- |
| 48 |

## Boundary

This is a mini-split engineering evaluation. It verifies the local closed-loop pipeline, but it is not a paper-score reproduction on the official full benchmark split.
