# nuPlan mini evaluation summary

- generated_at: `2026-06-14 21:27:25`
- run_root: `D:\nuplan-data\exp\exp\simulation\closed_loop_nonreactive_agents\dp\guidance_w10_mini10\model`
- aggregator_file: `closed_loop_nonreactive_agents_weighted_average_metrics_2026.06.14.13.32.28.parquet`

## Run status

| total | succeeded | failed | mean_duration_s | mean_compute_runtime_s | median_compute_runtime_s |
| --- | --- | --- | --- | --- | --- |
| 10 | 10 | 0 | 617.0864 | 4.0871 | 0.7581 |

## Final score

| score |
| --- |
| 0.9293 |

## Aggregated metric components

| metric | value |
| --- | --- |
| drivable_area_compliance | 1 |
| driving_direction_compliance | 1 |
| ego_is_comfortable | 0.8 |
| ego_is_making_progress | 1 |
| ego_progress_along_expert_route | 0.9633 |
| no_ego_at_fault_collisions | 1 |
| speed_limit_compliance | 0.8632 |
| time_to_collision_within_bound | 1 |

## Scenario runner report

| succeeded | scenario_name | scenario_type | score | log_name | planner | duration_s | mean_runtime_s | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| True | 1f151e15c9cf5c81 | near_multiple_vehicles | 0.875 | 2021.06.08.14.35.24_veh-26_02555_03004 | diffusion_planner | 125.4271 | 0.7862 |  |
| True | 485e78d3d4035b52 | following_lane_with_lead | 0.9684 | 2021.06.07.12.54.00_veh-35_01843_02314 | diffusion_planner | 151.3579 | 0.9554 |  |
| True | 6bd0988fce0f548b | stopping_at_stop_sign_with_lead | 1 | 2021.07.16.18.06.21_veh-38_04933_05307 | diffusion_planner | 123.7243 | 0.7672 |  |
| True | 6e256d585b245983 | starting_unprotected_cross_turn | 0.8379 | 2021.06.09.14.58.55_veh-35_01894_02311 | diffusion_planner | 120.7726 | 0.7588 |  |
| True | 99ca544752f255ad | accelerating_at_traffic_light_without_lead | 0.8652 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 131.7656 | 0.8315 |  |
| True | a3a4c3242d345082 | starting_left_turn | 0.9238 | 2021.05.25.14.16.10_veh-35_01690_02183 | diffusion_planner | 126.2347 | 0.7905 |  |
| True | aa8237ebd54f5a0b | starting_protected_noncross_turn | 1 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 128.5344 | 0.8115 |  |
| True | b2a5c363d1dd5abe | changing_lane_to_left | 0.9364 | 2021.06.09.14.58.55_veh-35_01894_02311 | diffusion_planner | 115.0216 | 0.7216 |  |
| True | d0b68e15688c58ad | on_pickup_dropoff | 0.8867 | 2021.05.12.23.36.44_veh-35_01133_01535 | diffusion_planner | 106.7817 | 0.6693 |  |
| True | e4eb6ff392715216 | waiting_for_pedestrian_to_cross | 1 | 2021.06.09.14.58.55_veh-35_01095_01484 | diffusion_planner | 5041.2444 | 33.7791 |  |

## Metric files

| metric_rows |
| --- |
| 160 |

## Boundary

This is a mini-split engineering evaluation. It verifies the local closed-loop pipeline, but it is not a paper-score reproduction on the official full benchmark split.
