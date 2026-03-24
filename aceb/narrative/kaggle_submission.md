# ACE-B / RCS-1: Measuring Adaptation Under Hidden Change

## Problem
Many benchmarks still reduce agent performance to accuracy. That is useful for asking whether an agent solved a task, but it is weak for asking how the agent behaves when the environment changes without warning. Under hidden rule change, the same accuracy can hide very different failure modes: an agent may never learn the original rule, may learn it but detect the change slowly, or may keep applying an obsolete policy after the change. Accuracy collapses these behaviors into one number.

## Contribution
RCS-1 introduces three compact metrics for adaptive behavior under hidden mid-episode change.

- **PCM (Pre-Change Mastery)** measures whether the agent actually learned the original rule before the switch.
- **CDL (Change Detection Lag)** measures how many post-switch steps pass before behavior shows sustained recovery, using a recovery window rather than a single lucky hit.
- **PR (Perseveration Rate)** measures how often post-switch errors are specifically consistent with the obsolete pre-change policy.

Together, these metrics separate mastery, detection, and persistence of outdated behavior.

## Key Insight
Two agents can have identical accuracy but fundamentally different adaptive behavior. One may fail because it never stabilizes after the switch. Another may fail because it keeps applying the old rule. These are different cognitive failures, and accuracy alone cannot distinguish them.

## Evidence
The benchmark already includes two forms of supporting evidence. First, a controlled metric-validation suite uses hand-constructed trajectories to show that PCM rises with stronger pre-switch correctness, CDL does not trigger on isolated lucky correct actions, and PR stays specific to obsolete-policy errors rather than generic post-switch mistakes. Second, deterministic baseline comparisons show meaningful separation across agent types: random behavior has weak mastery, static behavior can achieve strong pre-change performance but poor recovery, and adaptive behavior recovers faster with lower perseveration.

Additional controlled counterexamples reinforce the argument. We include cases where overall accuracy is the same but CDL or PR differ, and cases where post-switch error count is the same but PR differs sharply depending on whether the wrong actions follow the obsolete rule.

## Practical Meaning
This matters because real agents operate in changing environments. When they fail, we often need to know whether the problem is lack of learning, slow detection, or persistence of stale assumptions. These distinctions support diagnosis, targeted intervention, and more realistic evaluation of adaptive systems.

## Conclusion
Accuracy answers **if** an agent failed. PCM, CDL, and PR help answer **why** it failed. That makes the benchmark more useful for measuring adaptive intelligence under hidden environmental change.
