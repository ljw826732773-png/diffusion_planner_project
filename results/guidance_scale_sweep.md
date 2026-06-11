# Guidance Scale Sweep

This sweep compares the baseline planner with guidance-enabled runs on the same five mini scenario tokens.

| Scale | Final score | Collision | TTC | Comfort | Progress | Speed limit | Stop-sign score | Mean runtime |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0.9254 | 1.0000 | 1.0000 | 0.6000 | 0.9856 | 0.9197 | 1.0000 | 0.8146 s |
| 0.1 | 0.9254 | 1.0000 | 1.0000 | 0.6000 | 0.9861 | 0.9190 | 1.0000 | 0.7147 s |
| 0.3 | 0.7255 | 0.8000 | 0.8000 | 0.6000 | 0.9901 | 0.9144 | 0.0000 | 0.5042 s |
| 0.5 | 0.7264 | 0.8000 | 0.8000 | 0.4000 | 0.9924 | 0.9151 | 0.0000 | 0.4459 s |
| 1 | 0.5264 | 0.6000 | 0.6000 | 0.4000 | 0.9962 | 0.8991 | 0.0000 | 0.4571 s |

## Takeaways

- Best final score in this sweep: scale `0` with score `0.9254`.
- Stop-sign scenario preserved full score at scales: `0`, `0.1`.
- Stop-sign hard-score degradation appeared at scales: `0.3`, `0.5`, `1`.
- Safety metric degradation appears at scales: `0.3`, `0.5`, `1`.
- This suggests the current collision guidance is too strong or poorly timed for at least one stop-sign scenario.
- These are mini-split diagnostics, not full benchmark conclusions.
