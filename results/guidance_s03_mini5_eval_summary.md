# nuPlan mini evaluation summary

- generated_at: `2026-06-11 15:58:13`
- run_root: `D:\nuplan-data\exp\exp\simulation\closed_loop_nonreactive_agents\dp\guidance_s03_mini5\model`
- aggregator_file: `closed_loop_nonreactive_agents_weighted_average_metrics_2026.06.11.15.50.24.parquet`

## Run status

| total | succeeded | failed | mean_duration_s | mean_compute_runtime_s | median_compute_runtime_s |
| --- | --- | --- | --- | --- | --- |
| 5 | 5 | 0 | 80.8828 | 0.5042 | 0.4511 |

## Final score

| score |
| --- |
| 0.7255 |

## Aggregated metric components

| metric | value |
| --- | --- |
| drivable_area_compliance | 1 |
| driving_direction_compliance | 1 |
| ego_is_comfortable | 0.6 |
| ego_is_making_progress | 1 |
| ego_progress_along_expert_route | 0.9901 |
| no_ego_at_fault_collisions | 0.8 |
| speed_limit_compliance | 0.9144 |
| time_to_collision_within_bound | 0.8 |

## Scenario runner report

| succeeded | scenario_name | scenario_type | score | log_name | planner | duration_s | mean_runtime_s | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| True | 1f151e15c9cf5c81 | near_multiple_vehicles | 0.875 | 2021.06.08.14.35.24_veh-26_02555_03004 | diffusion_planner | 104.6369 | 0.6569 |  |
| True | 6bd0988fce0f548b | stopping_at_stop_sign_with_lead | 0 | 2021.07.16.18.06.21_veh-38_04933_05307 | diffusion_planner | 88.8806 | 0.5494 |  |
| True | 99ca544752f255ad | accelerating_at_traffic_light_without_lead | 0.8676 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 72.3019 | 0.4513 |  |
| True | aa8237ebd54f5a0b | starting_protected_noncross_turn | 1 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 72.7667 | 0.455 |  |
| True | d0b68e15688c58ad | on_pickup_dropoff | 0.8849 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 65.8278 | 0.4083 |  |

## Metric files

| metric_rows |
| --- |
| 80 |

## Boundary

This is a mini-split engineering evaluation. It verifies the local closed-loop pipeline, but it is not a paper-score reproduction on the official full benchmark split.
