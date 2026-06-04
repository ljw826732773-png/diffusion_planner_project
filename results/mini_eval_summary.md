# nuPlan mini evaluation summary

- generated_at: `2026-06-04 17:42:10`
- run_root: `D:\nuplan-data\exp\exp\simulation\closed_loop_nonreactive_agents\dp\mini5\model`
- aggregator_file: `closed_loop_nonreactive_agents_weighted_average_metrics_2026.06.04.17.08.00.parquet`

## Run status

| total | succeeded | failed | mean_duration_s | mean_compute_runtime_s | median_compute_runtime_s |
| --- | --- | --- | --- | --- | --- |
| 5 | 5 | 0 | 134.7063 | 0.8146 | 0.7382 |

## Final score

| score |
| --- |
| 0.9254 |

## Aggregated metric components

| metric | value |
| --- | --- |
| drivable_area_compliance | 1 |
| driving_direction_compliance | 1 |
| ego_is_comfortable | 0.6 |
| ego_is_making_progress | 1 |
| ego_progress_along_expert_route | 0.9856 |
| no_ego_at_fault_collisions | 1 |
| speed_limit_compliance | 0.9197 |
| time_to_collision_within_bound | 1 |

## Scenario runner report

| succeeded | scenario_name | scenario_type | score | log_name | planner | duration_s | mean_runtime_s | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| True | 1f151e15c9cf5c81 | near_multiple_vehicles | 0.875 | 2021.06.08.14.35.24_veh-26_02555_03004 | diffusion_planner | 123.7691 | 0.7544 |  |
| True | 6bd0988fce0f548b | stopping_at_stop_sign_with_lead | 1 | 2021.07.16.18.06.21_veh-38_04933_05307 | diffusion_planner | 147.3882 | 0.8797 |  |
| True | 99ca544752f255ad | accelerating_at_traffic_light_without_lead | 0.8641 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 136.7124 | 0.8291 |  |
| True | aa8237ebd54f5a0b | starting_protected_noncross_turn | 1 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 146.4894 | 0.8939 |  |
| True | d0b68e15688c58ad | on_pickup_dropoff | 0.888 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 119.1724 | 0.7158 |  |

## Metric files

| metric_rows |
| --- |
| 80 |

## Boundary

This is a mini-split engineering evaluation. It verifies the local closed-loop pipeline, but it is not a paper-score reproduction on the official full benchmark split.
