# Mini Evaluation Latency Summary

| Metric | Value |
| --- | ---: |
| num_scenarios | 5 |
| mean_compute_runtime_s | 0.4391 |
| median_compute_runtime_s | 0.4401 |
| p90_compute_runtime_s | 0.4712 |
| p95_compute_runtime_s | 0.4745 |
| max_compute_runtime_s | 0.4778 |
| mean_simulation_duration_s | 70.4902 |
| max_simulation_duration_s | 76.3935 |

## Slowest scenarios

| Rank | Scenario type | Scenario token | Mean runtime | Duration |
| ---: | --- | --- | ---: | ---: |
| 1 | near_multiple_vehicles | 1f151e15c9cf5c81 | 0.4778 s | 76.3935 s |
| 2 | stopping_at_stop_sign_with_lead | 6bd0988fce0f548b | 0.4613 s | 74.4192 s |
| 3 | starting_protected_noncross_turn | aa8237ebd54f5a0b | 0.4401 s | 70.3230 s |
| 4 | accelerating_at_traffic_light_without_lead | 99ca544752f255ad | 0.4242 s | 68.3241 s |
| 5 | on_pickup_dropoff | d0b68e15688c58ad | 0.3920 s | 62.9910 s |

Note: these numbers come from nuPlan closed-loop runner reports. They include planner `compute_trajectory` runtime in the simulator loop, so they are more realistic than the synthetic model-only benchmark.
