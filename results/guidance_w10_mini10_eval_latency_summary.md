# Mini Evaluation Latency Summary

| Metric | Value |
| --- | ---: |
| num_scenarios | 10 |
| mean_compute_runtime_s | 4.0871 |
| median_compute_runtime_s | 0.7884 |
| p90_compute_runtime_s | 4.2377 |
| p95_compute_runtime_s | 19.0084 |
| max_compute_runtime_s | 33.7791 |
| mean_simulation_duration_s | 617.0864 |
| max_simulation_duration_s | 5041.2444 |

## Slowest scenarios

| Rank | Scenario type | Scenario token | Mean runtime | Duration |
| ---: | --- | --- | ---: | ---: |
| 1 | waiting_for_pedestrian_to_cross | e4eb6ff392715216 | 33.7791 s | 5041.2444 s |
| 2 | following_lane_with_lead | 485e78d3d4035b52 | 0.9554 s | 151.3579 s |
| 3 | accelerating_at_traffic_light_without_lead | 99ca544752f255ad | 0.8315 s | 131.7656 s |
| 4 | starting_protected_noncross_turn | aa8237ebd54f5a0b | 0.8115 s | 128.5344 s |
| 5 | starting_left_turn | a3a4c3242d345082 | 0.7905 s | 126.2347 s |

Note: these numbers come from nuPlan closed-loop runner reports. They include planner `compute_trajectory` runtime in the simulator loop, so they are more realistic than the synthetic model-only benchmark.
