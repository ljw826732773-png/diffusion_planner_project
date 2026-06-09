# nuPlan mini evaluation summary

- generated_at: `2026-06-09 16:57:12`
- run_root: `D:\nuplan-data\exp\exp\simulation\closed_loop_nonreactive_agents\dp\mini10\model`
- aggregator_file: `closed_loop_nonreactive_agents_weighted_average_metrics_2026.06.09.16.42.10.parquet`

## Run status

| total | succeeded | failed | mean_duration_s | mean_compute_runtime_s | median_compute_runtime_s |
| --- | --- | --- | --- | --- | --- |
| 10 | 10 | 0 | 77.4598 | 0.4673 | 0.4327 |

## Final score

| score |
| --- |
| 0.9287 |

## Aggregated metric components

| metric | value |
| --- | --- |
| drivable_area_compliance | 1 |
| driving_direction_compliance | 1 |
| ego_is_comfortable | 0.8 |
| ego_is_making_progress | 1 |
| ego_progress_along_expert_route | 0.9587 |
| no_ego_at_fault_collisions | 1 |
| speed_limit_compliance | 0.8666 |
| time_to_collision_within_bound | 1 |

## Scenario runner report

| succeeded | scenario_name | scenario_type | score | log_name | planner | duration_s | mean_runtime_s | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| True | 1f151e15c9cf5c81 | near_multiple_vehicles | 0.875 | 2021.06.08.14.35.24_veh-26_02555_03004 | diffusion_planner | 90.0279 | 0.5468 |  |
| True | 485e78d3d4035b52 | following_lane_with_lead | 0.9619 | 2021.06.07.12.54.00_veh-35_01843_02314 | diffusion_planner | 92.3043 | 0.5612 |  |
| True | 6bd0988fce0f548b | stopping_at_stop_sign_with_lead | 1 | 2021.07.16.18.06.21_veh-38_04933_05307 | diffusion_planner | 92.131 | 0.5523 |  |
| True | 6e256d585b245983 | starting_unprotected_cross_turn | 0.8386 | 2021.06.09.14.58.55_veh-35_01894_02311 | diffusion_planner | 67.1415 | 0.4019 |  |
| True | 99ca544752f255ad | accelerating_at_traffic_light_without_lead | 0.8643 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 78.5392 | 0.4767 |  |
| True | a3a4c3242d345082 | starting_left_turn | 0.9237 | 2021.05.25.14.16.10_veh-35_01690_02183 | diffusion_planner | 75.525 | 0.4553 |  |
| True | aa8237ebd54f5a0b | starting_protected_noncross_turn | 1 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 79.0019 | 0.4818 |  |
| True | b2a5c363d1dd5abe | changing_lane_to_left | 0.9346 | 2021.06.09.14.58.55_veh-35_01894_02311 | diffusion_planner | 65.6769 | 0.3936 |  |
| True | d0b68e15688c58ad | on_pickup_dropoff | 0.8892 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 55.2572 | 0.327 |  |
| True | e4eb6ff392715216 | waiting_for_pedestrian_to_cross | 1 | 2021.06.09.14.58.55_veh-35_01095_01484 | diffusion_planner | 78.993 | 0.4761 |  |

## Metric files

| metric_rows |
| --- |
| 160 |

## Boundary

This is a mini-split engineering evaluation. It verifies the local closed-loop pipeline, but it is not a paper-score reproduction on the official full benchmark split.
