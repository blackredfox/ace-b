# Results Snapshot

Deterministic validation summary over the fixed five-episode validation set:

| Agent | Accuracy | PCM | CDL | PR |
|---|---:|---:|---:|---:|
| RandomAgent | 0.19 | 0.238 | 8.0 | 0.223 |
| StaticShiftAgent | 0.50 | 0.952 | None | 1.00 |
| AdaptiveShiftAgent | 0.80 | 0.952 | 2.6 | 0.58 |

Interpretation:

- StaticShiftAgent and AdaptiveShiftAgent show the same strong `PCM` (`0.952`), but differ sharply in `CDL` and `PR`: Adaptive recovers, while Static remains stuck on the obsolete rule.
- Plain accuracy is insufficient to distinguish these failure modes: `PR` shows that Static’s post-switch errors are fully old-rule-consistent (`1.00`), while Adaptive reduces perseverative errors (`0.58`).
