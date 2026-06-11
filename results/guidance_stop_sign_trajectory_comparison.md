# Stop-sign Guidance Trajectory Comparison

Scenario: `stopping_at_stop_sign_with_lead` / `6bd0988fce0f548b`

| Run | Scale | Score | Path length | Avg error to expert | Max error | Endpoint error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 0 | 1.0000 | 7.162 m | 1.388 m | 1.965 m | 1.965 m |
| scale_0.1 | 0.1 | 1.0000 | 7.382 m | 1.560 m | 2.182 m | 2.182 m |
| scale_0.3 | 0.3 | 0.0000 | 8.699 m | 2.740 m | 3.489 m | 3.489 m |
| scale_0.5 | 0.5 | 0.0000 | 17.105 m | 7.971 m | 11.879 m | 11.879 m |
| scale_1.0 | 1.0 | 0.0000 | 20.768 m | 9.752 m | 15.423 m | 15.423 m |

## Takeaways

- Successful runs in this scenario: `baseline`, `scale_0.1`. Failed hard-score runs: `scale_0.3`, `scale_0.5`, `scale_1.0`.
- Closest executed path to the expert by average error: `baseline`.
- Largest average deviation from the expert: `scale_1.0`.
- Failed runs have executed path lengths in the range `8.699-20.768 m`, compared with baseline `7.162 m`.
- The metric score still matters more than geometric closeness alone: collision/TTC hard failures can occur even when the path shape looks broadly plausible.
- This figure is a static trajectory diagnostic. NuBoard is still needed to inspect actor-level interactions frame by frame.
