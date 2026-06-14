# Evaluation Run Comparison

Baseline: `guidance_w3.0`

Candidate: `guidance_w1.0`

## Final Score

| Metric | Baseline | Candidate | Delta |
| --- | ---: | ---: | ---: |
| score | 0.7264 | 0.9254 | 0.1990 |
| ego_is_comfortable | 0.4000 | 0.6000 | 0.2000 |
| ego_progress_along_expert_route | 0.9924 | 0.9869 | -0.0054 |
| no_ego_at_fault_collisions | 0.8000 | 1.0000 | 0.2000 |
| speed_limit_compliance | 0.9151 | 0.9179 | 0.0027 |
| time_to_collision_within_bound | 0.8000 | 1.0000 | 0.2000 |

## Scenario Score Delta

| Scenario Type | Scenario Token | Baseline | Candidate | Delta | Main candidate limits |
| --- | --- | ---: | ---: | ---: | --- |
| accelerating_at_traffic_light_without_lead | 99ca544752f255ad | 0.8714 | 0.8649 | -0.0065 | ego_is_comfortable=0.0000; ego_progress_along_expert_route=0.9678 |
| near_multiple_vehicles | 1f151e15c9cf5c81 | 0.8750 | 0.8750 | 0.0000 | ego_is_comfortable=0.0000 |
| starting_protected_noncross_turn | aa8237ebd54f5a0b | 1.0000 | 1.0000 | 0.0000 | none below 0.999 |
| on_pickup_dropoff | d0b68e15688c58ad | 0.8855 | 0.8870 | 0.0014 | ego_progress_along_expert_route=0.9669; speed_limit_compliance=0.5893 |
| stopping_at_stop_sign_with_lead | 6bd0988fce0f548b | 0.0000 | 1.0000 | 1.0000 | none below 0.999 |

## Interpretation

- A positive delta means the candidate run scored higher than the baseline on the same scenario token.
- A zero candidate score usually indicates a hard metric failure such as at-fault collision or time-to-collision violation.
- This comparison uses the same 5 mini scenario tokens, so it is useful for debugging guidance behavior, but it is still not a paper-level benchmark.
