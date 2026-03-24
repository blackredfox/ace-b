# Results Snapshot

Deterministic validation summary over the fixed five-episode validation set:

| Agent | Accuracy | PCM | CDL | PR |
|---|---:|---:|---:|---:|
| RandomAgent | 0.19 | 0.238 | 8.0 | 0.223 |
| StaticShiftAgent | 0.50 | 0.952 | None | 1.00 |
| AdaptiveShiftAgent | 0.80 | 0.952 | 2.6 | 0.58 |

Interpretation:

- Static and Adaptive have the same strong pre-change mastery (`PCM = 0.952`), but Adaptive recovers after the switch while Static remains stuck on the obsolete rule.
- PR reveals behavior that accuracy misses: Static’s post-switch errors are fully old-rule-consistent (`PR = 1.00`), while Adaptive reduces perseverative errors even when it is not perfect.
