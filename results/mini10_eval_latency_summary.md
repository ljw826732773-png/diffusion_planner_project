# Mini Evaluation Latency Summary

| Metric | Value |
| --- | ---: |
| num_scenarios | 10 |
| mean_compute_runtime_s | 0.4673 |
| median_compute_runtime_s | 0.4764 |
| p90_compute_runtime_s | 0.5532 |
| p95_compute_runtime_s | 0.5572 |
| max_compute_runtime_s | 0.5612 |
| mean_simulation_duration_s | 77.4598 |
| max_simulation_duration_s | 92.3043 |

## Slowest scenarios

| Rank | Scenario type | Scenario token | Mean runtime | Duration |
| ---: | --- | --- | ---: | ---: |
| 1 | following_lane_with_lead | 485e78d3d4035b52 | 0.5612 s | 92.3043 s |
| 2 | stopping_at_stop_sign_with_lead | 6bd0988fce0f548b | 0.5523 s | 92.1310 s |
| 3 | near_multiple_vehicles | 1f151e15c9cf5c81 | 0.5468 s | 90.0279 s |
| 4 | starting_protected_noncross_turn | aa8237ebd54f5a0b | 0.4818 s | 79.0019 s |
| 5 | accelerating_at_traffic_light_without_lead | 99ca544752f255ad | 0.4767 s | 78.5392 s |

Note: these numbers come from nuPlan closed-loop runner reports. They include planner `compute_trajectory` runtime in the simulator loop, so they are more realistic than the synthetic model-only benchmark.
