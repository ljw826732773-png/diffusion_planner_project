# Evaluation Run Comparison

Baseline: `baseline_mini10`

Candidate: `guidance_w1.0_mini10`

## Final Score

| Metric | Baseline | Candidate | Delta |
| --- | ---: | ---: | ---: |
| score | 0.9287 | 0.9293 | 0.0006 |
| ego_is_comfortable | 0.8000 | 0.8000 | 0.0000 |
| ego_progress_along_expert_route | 0.9587 | 0.9633 | 0.0047 |
| no_ego_at_fault_collisions | 1.0000 | 1.0000 | 0.0000 |
| speed_limit_compliance | 0.8666 | 0.8632 | -0.0034 |
| time_to_collision_within_bound | 1.0000 | 1.0000 | 0.0000 |

## Scenario Score Delta

| Scenario Type | Scenario Token | Baseline | Candidate | Delta | Main candidate limits |
| --- | --- | ---: | ---: | ---: | --- |
| on_pickup_dropoff | d0b68e15688c58ad | 0.8892 | 0.8867 | -0.0026 | ego_progress_along_expert_route=0.9725; speed_limit_compliance=0.5811 |
| starting_unprotected_cross_turn | 6e256d585b245983 | 0.8386 | 0.8379 | -0.0006 | speed_limit_compliance=0.3517 |
| near_multiple_vehicles | 1f151e15c9cf5c81 | 0.8750 | 0.8750 | 0.0000 | ego_is_comfortable=0.0000 |
| starting_protected_noncross_turn | aa8237ebd54f5a0b | 1.0000 | 1.0000 | 0.0000 | none below 0.999 |
| stopping_at_stop_sign_with_lead | 6bd0988fce0f548b | 1.0000 | 1.0000 | 0.0000 | none below 0.999 |
| waiting_for_pedestrian_to_cross | e4eb6ff392715216 | 1.0000 | 1.0000 | 0.0000 | none below 0.999 |
| starting_left_turn | a3a4c3242d345082 | 0.9237 | 0.9238 | 0.0001 | ego_progress_along_expert_route=0.7932; speed_limit_compliance=0.9535 |
| accelerating_at_traffic_light_without_lead | 99ca544752f255ad | 0.8643 | 0.8652 | 0.0009 | ego_is_comfortable=0.0000; ego_progress_along_expert_route=0.9686 |
| changing_lane_to_left | b2a5c363d1dd5abe | 0.9346 | 0.9364 | 0.0018 | speed_limit_compliance=0.7456 |
| following_lane_with_lead | 485e78d3d4035b52 | 0.9619 | 0.9684 | 0.0066 | ego_progress_along_expert_route=0.8990 |

## Interpretation

- A positive delta means the candidate run scored higher than the baseline on the same scenario token.
- A zero candidate score usually indicates a hard metric failure such as at-fault collision or time-to-collision violation.
- This comparison uses the same 10 mini scenario tokens, so it is useful for debugging guidance behavior, but it is still not a paper-level benchmark.
