# Frame-Level Runtime Profile

This report summarizes one `compute_trajectory` profile CSV generated through `DP_FRAME_PROFILE_CSV`.

## Summary

| Metric | Value |
| --- | ---: |
| Completed frames | 149 |
| Incomplete frames | 0 |
| Mean runtime | 2.3202 s |
| Median runtime | 2.1796 s |
| P95 runtime | 2.6455 s |
| Max runtime | 11.3980 s |
| Runner mean runtime | 2.3202 s |
| Runner median runtime | 2.1796 s |
| Runner duration | 369.5618 s |

## Slowest Frames

| Rank | Iteration | Runtime | Iteration time |
| ---: | ---: | ---: | ---: |
| 1 | 0 | 11.3980 s | 1623266522.7497 |
| 2 | 143 | 2.9654 s | 1623266537.0505 |
| 3 | 56 | 2.6934 s | 1623266528.3502 |
| 4 | 10 | 2.6692 s | 1623266523.7500 |
| 5 | 60 | 2.6684 s | 1623266528.7503 |
| 6 | 3 | 2.6589 s | 1623266523.0498 |
| 7 | 139 | 2.6538 s | 1623266536.6505 |
| 8 | 100 | 2.6467 s | 1623266532.7514 |
| 9 | 84 | 2.6436 s | 1623266531.1510 |
| 10 | 80 | 2.6380 s | 1623266530.7508 |

## Takeaways

- The previous mini10 tuned-guidance runtime outlier was not reproduced in this single-scenario run.
- The largest observed call is the first planner iteration, which points to cold-start overhead.
- After the first iteration, runtime stays in a much narrower range, but the median is still higher than the baseline mini10 mean.
- The profile hook now makes future slow-scenario reruns auditable at frame level.
