# nuPlan mini evaluation summary

- generated_at: `2026-06-11 16:06:10`
- run_root: `D:\nuplan-data\exp\exp\simulation\closed_loop_nonreactive_agents\dp\guidance_s10_mini5\model`
- aggregator_file: `closed_loop_nonreactive_agents_weighted_average_metrics_2026.06.11.15.59.12.parquet`

## Run status

| total | succeeded | failed | mean_duration_s | mean_compute_runtime_s | median_compute_runtime_s |
| --- | --- | --- | --- | --- | --- |
| 5 | 5 | 0 | 73.3241 | 0.4571 | 0.4176 |

## Final score

| score |
| --- |
| 0.5264 |

## Aggregated metric components

| metric | value |
| --- | --- |
| drivable_area_compliance | 1 |
| driving_direction_compliance | 1 |
| ego_is_comfortable | 0.4 |
| ego_is_making_progress | 1 |
| ego_progress_along_expert_route | 0.9962 |
| no_ego_at_fault_collisions | 0.6 |
| speed_limit_compliance | 0.8991 |
| time_to_collision_within_bound | 0.6 |

## Scenario runner report

| succeeded | scenario_name | scenario_type | score | log_name | planner | duration_s | mean_runtime_s | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| True | 1f151e15c9cf5c81 | near_multiple_vehicles | 0.875 | 2021.06.08.14.35.24_veh-26_02555_03004 | diffusion_planner | 85.7687 | 0.5372 |  |
| True | 6bd0988fce0f548b | stopping_at_stop_sign_with_lead | 0 | 2021.07.16.18.06.21_veh-38_04933_05307 | diffusion_planner | 74.5591 | 0.4605 |  |
| True | 99ca544752f255ad | accelerating_at_traffic_light_without_lead | 0 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 71.5953 | 0.4475 |  |
| True | aa8237ebd54f5a0b | starting_protected_noncross_turn | 0.875 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 71.9249 | 0.4506 |  |
| True | d0b68e15688c58ad | on_pickup_dropoff | 0.882 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 62.7723 | 0.3895 |  |

## Metric files

| metric_rows |
| --- |
| 80 |

## Boundary

This is a mini-split engineering evaluation. It verifies the local closed-loop pipeline, but it is not a paper-score reproduction on the official full benchmark split.
