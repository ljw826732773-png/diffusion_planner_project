# Mini Evaluation Low-score Analysis

Source scenarios: 3

The simulations all succeeded. This report only highlights lower-scoring scenarios and the metrics that reduced their weighted score.

| Rank | Scenario Type | Scenario Token | Score | Main limiting metrics |
| ---: | --- | --- | ---: | --- |
| 1 | accelerating_at_traffic_light_without_lead | 99ca544752f255ad | 0.8641 | ego_is_comfortable=0.0000; ego_progress_along_expert_route=0.9651 |
| 2 | near_multiple_vehicles | 1f151e15c9cf5c81 | 0.8750 | ego_is_comfortable=0.0000 |
| 3 | on_pickup_dropoff | d0b68e15688c58ad | 0.8880 | ego_progress_along_expert_route=0.9629; speed_limit_compliance=0.5985 |

Interpretation:

- `ego_is_comfortable=0` usually points to acceleration, jerk, yaw rate, or lateral acceleration exceeding the nuPlan comfort thresholds.
- `speed_limit_compliance<1` means the executed ego trajectory exceeded the mapped speed limit for part of the scenario.
- `ego_progress_along_expert_route<1` means the planner progressed slightly less than the expert route baseline.
- These are mini-split diagnostic results, not paper-level Val14/Test14 conclusions.
