# Runtime Outlier Analysis

Rows are sorted by candidate mean `compute_trajectory` runtime.

| Rank | Scenario type | Scenario token | Candidate mean | Candidate median | Baseline mean | Delta | Mean objects | Max objects | Mean pedestrians |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | waiting_for_pedestrian_to_cross | e4eb6ff392715216 | 33.7791 s | 0.7389 s | 0.4761 s | 33.3030 s | 140.5235 | 195.0000 | 38.4161 |
| 2 | following_lane_with_lead | 485e78d3d4035b52 | 0.9554 s | 0.8939 s | 0.5612 s | 0.3942 s | 217.6443 | 300.0000 | 78.4094 |
| 3 | accelerating_at_traffic_light_without_lead | 99ca544752f255ad | 0.8315 s | 0.7902 s | 0.4767 s | 0.3548 s | 101.8255 | 121.0000 | 32.8792 |
| 4 | starting_protected_noncross_turn | aa8237ebd54f5a0b | 0.8115 s | 0.7610 s | 0.4818 s | 0.3297 s | 61.0201 | 77.0000 | 13.9463 |
| 5 | starting_left_turn | a3a4c3242d345082 | 0.7905 s | 0.7402 s | 0.4553 s | 0.3352 s | 128.6376 | 150.0000 | 8.0738 |
| 6 | near_multiple_vehicles | 1f151e15c9cf5c81 | 0.7862 s | 0.7828 s | 0.5468 s | 0.2394 s | 59.1467 | 86.0000 | 4.1000 |
| 7 | stopping_at_stop_sign_with_lead | 6bd0988fce0f548b | 0.7672 s | 0.7969 s | 0.5523 s | 0.2149 s | 307.0067 | 375.0000 | 116.2752 |
| 8 | starting_unprotected_cross_turn | 6e256d585b245983 | 0.7588 s | 0.7331 s | 0.4019 s | 0.3569 s | 32.6309 | 51.0000 | 6.6577 |
| 9 | changing_lane_to_left | b2a5c363d1dd5abe | 0.7216 s | 0.6970 s | 0.3936 s | 0.3280 s | 38.1946 | 81.0000 | 7.7383 |
| 10 | on_pickup_dropoff | d0b68e15688c58ad | 0.6693 s | 0.6473 s | 0.3270 s | 0.3423 s | 42.1946 | 61.0000 | 7.8792 |

## Takeaways

- Slowest scenario: `waiting_for_pedestrian_to_cross` / `e4eb6ff392715216`.
- Candidate mean runtime is `33.7791 s`, while baseline mean runtime is `0.4761 s`.
- Candidate median runtime is `0.7389 s`, so the outlier is not representative of every planner call.
- Object counts are diagnostic hints only; frame-level profiling is still needed to identify the exact slow call.
