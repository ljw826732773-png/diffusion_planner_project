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

Note: these numbers come from nuPlan closed-loop runner reports. They include planner `compute_trajectory` runtime in the simulator loop, so they are more realistic than the synthetic model-only benchmark.
