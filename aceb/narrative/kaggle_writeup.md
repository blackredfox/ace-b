# Project Name

ACE-B: Rule Change Survival (RCS-1) — Measuring Adaptive Intelligence Under Hidden Rule Change

# Your Team

Nataliia Solodkova

# Problem Statement

Many evaluation setups still summarize agent quality with static accuracy. That is useful for asking whether an agent produced the right answer, but it is weak for asking how the agent behaves when the environment changes without warning. Under hidden rule change, the same final accuracy can hide very different failure modes: an agent may never learn the original rule, may learn it but detect the change slowly, or may keep applying an obsolete policy after the switch. These behaviors matter for adaptive intelligence, but accuracy collapses them into one number.

RCS-1 isolates this problem with procedurally generated episodes in which the transformation rule changes mid-episode without being announced to the agent. The benchmark therefore targets adaptation under hidden environmental change rather than static task performance alone.

# Task & benchmark construction

Each episode is generated from a small symbol alphabet and an input stream. Before the hidden switch, symbols are transformed by one cyclic shift rule. After the switch, a different cyclic shift rule applies. The environment reveals only the current input symbol, bounded recent history, and correctness feedback after the agent acts.

The benchmark includes three baseline agents. `RandomAgent` produces uninformed actions. `StaticShiftAgent` learns a single rule hypothesis and keeps using it even after the hidden change. `AdaptiveShiftAgent` can commit to a hypothesis, detect repeated failure, revise its hypothesis, and recover. This makes the benchmark useful for separating lack of learning from poor adaptation.

Evaluation uses three trajectory-based metrics. **PCM (Pre-Change Mastery)** measures how well the agent learned before the switch. **CDL (Change Detection Lag)** measures how long it takes to show sustained post-switch recovery using a recovery window, not a single lucky correct action. **PR (Perseveration Rate)** measures how often post-switch errors specifically follow the obsolete pre-change rule.

# Dataset

The dataset is synthetic and procedurally generated. Each episode is represented by `EpisodeSpec`, which contains `episode_id`, `alphabet`, `input_stream`, `shift_pre`, `shift_post`, `switch_step`, `history_window`, and `seed`. These fields are sufficient to reproduce the episode deterministically.

This structure keeps labels verifiable and ambiguity low. For every step, the correct output is defined exactly by the active rule and the current input symbol. Because episodes are generated from seeds rather than memorized examples, the benchmark resists simple lookup or dataset-specific shortcutting. Correctness can always be checked directly from the episode specification.

# Technical details

Episode generation is deterministic from config and seed. Rule scheduling is handled by an explicit pre/post wrapper that switches at `step_id >= switch_step`. The environment loop records full trajectories, including actions, expected outputs, correctness, reward, and whether the step occurred after the switch.

Metric computation is fully trajectory-based. PCM is computed from pre-switch correctness only. CDL searches for the first post-switch recovery window meeting a required success threshold. PR reconstructs the old rule and counts only those post-switch errors that match obsolete-policy behavior.

To support scientific validity, the project includes a controlled metric-validation suite and a deterministic validation set for baseline comparison. These components show that the metrics are construct-valid, behaviorally discriminative, and not reducible to plain accuracy.

# Results, insights, and conclusions

On the deterministic validation set, the current baseline summary is:

- **RandomAgent** — accuracy: `0.19`, PCM: `0.238`, CDL: `8.0`, PR: `0.223`
- **StaticShiftAgent** — accuracy: `0.50`, PCM: `0.952`, CDL: `None` (no recovery window detected), PR: `1.00`
- **AdaptiveShiftAgent** — accuracy: `0.80`, PCM: `0.952`, CDL: `2.6`, PR: `0.58`

These results show why accuracy alone is insufficient. Static and adaptive agents have the same strong pre-change mastery, but they differ sharply after the hidden switch: the static agent perseverates on the old rule, while the adaptive agent revises and recovers. PR captures obsolete-policy persistence directly, and CDL captures how long adaptation takes. Controlled trajectory cases also show that two runs can have the same accuracy while differing meaningfully in PR or CDL.

The main conclusion is that accuracy can answer whether an agent failed, but it cannot reliably explain why. RCS-1 decomposes that question into mastery, detection lag, and obsolete-policy persistence, making hidden-change adaptation measurable and inspectable.

# Organizational affiliations

Independent researcher

# References & citations

1. Kaggle Benchmarks competition materials and submission guidelines.
2. Chollet, F. (2019). *On the Measure of Intelligence*.
3. Lake, B. M., Ullman, T. D., Tenenbaum, J. B., & Gershman, S. J. (2017). *Building machines that learn and think like people*.
4. Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction*.
