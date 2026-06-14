# Evaluation Run Comparison

Baseline: `baseline`

Candidate: `guidance_w1.0`

## Final Score

| Metric | Baseline | Candidate | Delta |
| --- | ---: | ---: | ---: |
| score | 0.9254 | 0.9254 | -0.0000 |
| ego_is_comfortable | 0.6000 | 0.6000 | 0.0000 |
| ego_progress_along_expert_route | 0.9856 | 0.9869 | 0.0013 |
| no_ego_at_fault_collisions | 1.0000 | 1.0000 | 0.0000 |
| speed_limit_compliance | 0.9197 | 0.9179 | -0.0018 |
| time_to_collision_within_bound | 1.0000 | 1.0000 | 0.0000 |

## Scenario Score Delta

| Scenario Type | Scenario Token | Baseline | Candidate | Delta | Main candidate limits |
| --- | --- | ---: | ---: | ---: | --- |
| on_pickup_dropoff | d0b68e15688c58ad | 0.8880 | 0.8870 | -0.0010 | ego_progress_along_expert_route=0.9669; speed_limit_compliance=0.5893 |
| near_multiple_vehicles | 1f151e15c9cf5c81 | 0.8750 | 0.8750 | 0.0000 | ego_is_comfortable=0.0000 |
| starting_protected_noncross_turn | aa8237ebd54f5a0b | 1.0000 | 1.0000 | 0.0000 | none below 0.999 |
| stopping_at_stop_sign_with_lead | 6bd0988fce0f548b | 1.0000 | 1.0000 | 0.0000 | none below 0.999 |
| accelerating_at_traffic_light_without_lead | 99ca544752f255ad | 0.8641 | 0.8649 | 0.0008 | ego_is_comfortable=0.0000; ego_progress_along_expert_route=0.9678 |

## Interpretation

- A positive delta means the candidate run scored higher than the baseline on the same scenario token.
- A zero candidate score usually indicates a hard metric failure such as at-fault collision or time-to-collision violation.
- This comparison uses the same 5 mini scenario tokens, so it is useful for debugging guidance behavior, but it is still not a paper-level benchmark.
