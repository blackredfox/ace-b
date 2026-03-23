# PRD

## Original problem statement
Task 1 — ShiftRule Implementation
- Implement a Python class `ShiftRule`
- Inputs: `alphabet: list[str]`, `shift: int`
- Apply cyclic shift over alphabet with wrap-around
- Validate input symbols and raise a clear error when invalid
- Include tests for basic shift, wrap-around, invalid symbol, and preferred negative shift support

Task 2 — EpisodeSpec Data Model
- Define a Python `@dataclass` named `EpisodeSpec`
- Fields: `episode_id`, `alphabet`, `input_stream`, `shift_pre`, `shift_post`, `switch_step`, `history_window`, `seed`
- Keep it as a strict data container with full type hints and no business logic
- Add preferred lightweight validation and tests for valid creation plus invalid `switch_step`

Task 3 — RuleSet (Pre/Post Rule Wrapper)
- Create a pure rule scheduler `RuleSet`
- Internally compose two `ShiftRule` instances for pre/post behavior
- Apply the pre rule when `step_id < switch_step`, otherwise the post rule
- Expose `is_post_switch(step_id)` with critical boundary `step_id >= switch_step`
- Keep validation minimal, but explicitly reject negative `step_id`
- Add tests for before switch, after switch, boundary, consistency, and negative `step_id`

Task 4 — Episode Builder
- Implement `build_episode_spec(config, episode_id: str) -> EpisodeSpec`
- Add a minimal `BenchmarkConfig` dataclass with only the fields needed for generation
- Keep generation deterministic from the base seed and episode id
- Generate a unique alphabet, a non-constant input stream, distinct non-zero shifts with modulo non-equivalence, and a middle-band switch step
- Return a valid `EpisodeSpec` without bypassing validation
- Add tests for validity, switch-step bounds, shift constraints, input stream constraints, and determinism

Task 5 — RCS Environment Core Loop
- Implement `RCSEnvironment` that consumes `EpisodeSpec` and `RuleSet`
- Add environment I/O dataclasses: `Observation`, `StepResult`, `TrajectoryRecord`
- Enforce explicit lifecycle: `reset()` is required before `step()`
- Execute steps deterministically, produce correctness/reward, maintain bounded history, and record trajectory
- Raise clear errors for stepping before reset or after done
- Keep scope limited to environment execution only

Task 6 — Baseline Agents + Single-Episode Runner
- Implement a minimal agent interface, baseline agents, and the first runnable single-episode execution path
- Add deterministic `RandomAgent` using local RNG only
- Add `StaticShiftAgent` with simple non-adaptive policy learning
- Implement `run_episode(environment, agent) -> EpisodeRunResult`
- Return full trajectory plus minimal execution summary (`total_steps`, `total_correct`, `accuracy`)
- Preserve benchmark validity by keeping agent-visible information limited to interaction signals only

Task 7 — Adaptive Baseline Agent
- Implement `AdaptiveShiftAgent` using the strict feedback-only contract
- Support commit, failure detection, revision, re-commit, and continued recovery within a single episode
- After revision, continue search from the next candidate shift in order
- Add focused unit tests plus end-to-end runner smoke coverage
- Keep scope limited to agent behavior only, without evaluator metrics or aggregation

Task 8 — Core Evaluator Metrics (PCM, CDL, PR)
- Implement pure per-episode evaluator functions:
  - `compute_pcm(...)`
  - `compute_cdl(...)`
  - `compute_pr(...)`
  - `evaluate_core_metrics(...)`
- Add compact metric result dataclass
- Keep validation explicit and deterministic
- Use window-based CDL and pre-rule-based PR
- Keep scope limited to trajectory-based metrics only

Task 9 — Baseline Comparison Helper (Random / Static / Adaptive)
- Implement a small deterministic comparison layer across baseline agents
- Reuse the existing runner and evaluator functions
- Produce side-by-side per-episode comparison outputs for accuracy, PCM, CDL, and PR
- Add a small summary helper with simple per-agent averages
- Keep scope limited to fair same-episode comparisons only

Task 10 — Deterministic Validation Set & Sanity-Check Flow
- Implement a fixed validation episode set
- Add a validation runner wrapper over the comparison layer
- Add summary output and boolean-only behavioral separation diagnostics
- Keep this as a lightweight developer-facing validation flow only
- Reuse existing comparison and evaluator logic without adding export or UI

Task 11 — Metric Validation Suite (for Kaggle / Measuring AGI)
- Implement a focused evidence-oriented validation suite for PCM, CDL, and PR
- Use small controlled trajectory fixtures rather than only generated runs
- Return structured validation checks with compact metric details and expected/observed relations
- Demonstrate construct validity, behavioral discrimination, non-redundancy, and value beyond plain accuracy
- Keep scope limited to validation of existing metrics only

Task 12 — Evidence Summary Package for Reviewers
- Build a compact reviewer-facing evidence package over the existing validation outputs
- Add structured claims tied to metric-validation and baseline-separation evidence
- Add a deterministic markdown renderer with compact sections for review use
- Keep this as a packaging layer only, without new benchmark logic

Task 13 — Kaggle Submission Narrative + Minimal Scientific Reinforcement
- Add a concise reviewer-facing Kaggle submission narrative
- Add compact evidence notes mapping claims to evidence
- Add 1–2 minimal controlled scientific cases that strengthen the “accuracy is insufficient” argument
- Reuse existing evaluator functions only and keep the cases explicit and deterministic
- Keep scope limited to framing and reinforcement, not new benchmark functionality

## Architecture decisions
- Created a minimal benchmark package structure under `aceb/` aligned with the implementation plan
- Kept primitive transformation logic in `aceb.rules.shift.ShiftRule`
- Kept deterministic episode metadata in `aceb.env.episode.EpisodeSpec`
- Added `aceb.rules.ruleset.RuleSet` as a small composition layer that schedules between two `ShiftRule` instances without environment behavior
- Added a minimal `aceb.config.BenchmarkConfig` contract for generation only
- Implemented episode generation in `aceb.generator.builder` using only the Python standard library
- Used SHA-256 over `base_seed:episode_id` to derive deterministic episode-level seeds
- Implemented environment execution in `aceb.env.environment.RCSEnvironment` with explicit lifecycle state and bounded observation history
- Added a minimal `get_observation()` helper so the runner can fetch the next observation without changing the `step()` contract
- Introduced `AgentFeedback(correct, reward, done)` as the strict agent-facing feedback contract
- Refactored agent-facing observation history to exclude `expected_output`, preventing oracle leakage through history
- Implemented three baseline agent tiers under the same contract:
  - `RandomAgent` for uninformed behavior
  - `StaticShiftAgent` for single-hypothesis non-adaptive behavior
  - `AdaptiveShiftAgent` for commit → fail-detect → revise → recover behavior
- For the adaptive agent, revision search continues from the next candidate shift in order after a failed committed hypothesis, matching the selected user preference
- Implemented the first evaluator layer as small pure functions in `aceb.eval`, keeping metric logic easy to inspect and test
- Implemented the comparison layer as a thin orchestration wrapper around existing episode generation, runner, and evaluator logic, avoiding duplicated metric computation
- Implemented the validation layer as a lightweight wrapper around the comparison layer with a fixed episode set and boolean sanity diagnostics
- Implemented the metric validation suite as a compact evidence package built on controlled hand-constructed trajectories that reuse the evaluator rather than duplicating metric logic
- Implemented the reviewer-facing evidence summary as a packaging layer over the validation outputs, with structured claims and deterministic markdown rendering
- Implemented the narrative layer as lightweight documentation plus two explicit controlled scientific cases that reinforce the core measurement claim without adding new infrastructure

## What's been implemented
- `aceb/config.py`
- `aceb/generator/__init__.py`
- `aceb/generator/builder.py`
- `aceb/rules/base.py`
- `aceb/rules/shift.py`
- `aceb/rules/ruleset.py`
- `aceb/env/episode.py`
- `aceb/env/types.py`
- `aceb/env/environment.py`
- `aceb/agents/__init__.py`
- `aceb/agents/base.py`
- `aceb/agents/random_agent.py`
- `aceb/agents/static_shift_agent.py`
- `aceb/agents/adaptive_shift_agent.py`
- `aceb/agents/types.py`
- `aceb/runner/__init__.py`
- `aceb/runner/episode_runner.py`
- `aceb/eval/__init__.py`
- `aceb/eval/types.py`
- `aceb/eval/core_metrics.py`
- `aceb/eval/comparison.py`
- `aceb/eval/validation.py`
- `aceb/eval/evidence_summary.py`
- `aceb/validation/__init__.py`
- `aceb/validation/validation_set.py`
- `aceb/validation/run_validation.py`
- `aceb/narrative/kaggle_submission.md`
- `aceb/narrative/evidence_notes.md`
- `aceb/rules/__init__.py`
- `aceb/env/__init__.py`
- `tests/test_shift_rule.py`
- `tests/test_episode_spec.py`
- `tests/test_rule_set.py`
- `tests/test_episode_builder.py`
- `tests/test_environment.py`
- `tests/test_agents.py`
- `tests/test_episode_runner.py`
- `tests/test_static_shift_commit_rule_regression.py`
- `tests/test_adaptive_shift_agent.py`
- `tests/test_core_metrics.py`
- `tests/test_comparison_helper.py`
- `tests/test_validation_flow.py`
- `tests/test_metric_validation.py`
- `tests/test_evidence_summary.py`
- `tests/test_additional_validation_cases.py`
- `tests/conftest.py`

Implemented behavior:
- `ShiftRule` supports cyclic positive and negative shifts, wrap-around, and clear invalid-symbol errors
- `EpisodeSpec` stores all deterministic episode parameters with full type hints and lightweight validation
- `RuleSet` deterministically schedules between pre/post `ShiftRule` instances using the required boundary `step_id >= switch_step`
- `BenchmarkConfig` provides the minimal explicit generation contract: `alphabet_size`, `input_length`, `history_window`, `seed`, and optional ratio bounds
- `build_episode_spec` deterministically generates:
  - a unique alphabet of size at least 3
  - a non-constant input stream containing only alphabet symbols
  - non-zero distinct shifts that are also distinct modulo alphabet length
  - a switch step inside the middle ratio band and away from the first/last step
  - a valid `EpisodeSpec` carrying the derived episode seed
- `RCSEnvironment` provides:
  - explicit `reset() -> Observation`
  - explicit `step(action: str) -> StepResult`
  - `get_observation()` for the current active step
  - `get_trajectory()` returning a safe copy
  - reward mapping of `1.0` or `0.0`
  - bounded observation history based on `history_window`
  - clear runtime errors before reset and after completion
  - one `TrajectoryRecord` per executed step
- Agent contract hardening:
  - `BaseAgent.observe()` receives only `AgentFeedback(correct, reward, done)`
  - `run_episode()` does not pass `StepResult` into agents
  - agent-visible observation history does not include `expected_output`
- `RandomAgent` uses deterministic local randomness and resets cleanly per episode
- `StaticShiftAgent` tests candidate shifts, commits after 2 consistent confirmations, and never revises after commit
- `AdaptiveShiftAgent`:
  - searches non-zero shift candidates deterministically
  - commits after configurable consistent confirmations
  - uses the committed shift while feedback remains correct
  - tracks failure streak after commit
  - drops a failed hypothesis after the configured threshold
  - continues from the next candidate shift in order after revision
  - re-commits to a new hypothesis after renewed evidence
  - remains fully non-oracle and feedback-driven
- `run_episode()` supports all current agents end-to-end and returns full trajectory plus minimal summary statistics
- Core evaluator layer provides:
  - `compute_pcm()` for exact pre-switch mastery
  - `compute_cdl()` using strict post-switch sliding windows
  - `compute_pr()` by comparing post-switch wrong actions to the pre-change rule only
  - `evaluate_core_metrics()` returning compact `CoreMetricResult`
  - explicit validation for empty trajectories, length mismatch, incoherent step ordering, and invalid window parameters
- Comparison layer provides:
  - `compare_baseline_agents_on_episodes()` for fair same-episode baseline runs
  - `AgentEpisodeComparison` per agent per episode
  - `ComparisonResult` bundle across requested episodes
  - `summarize_by_agent()` with simple per-agent averages
  - CDL averaging over non-None values only, with `None` preserved when no valid CDL exists
  - deterministic RandomAgent seeding per episode via derived seed
  - reuse of `run_episode()` and `evaluate_core_metrics()` rather than duplicating logic
- Validation layer provides:
  - fixed deterministic `VALIDATION_EPISODE_IDS`
  - `get_validation_episode_ids()` defensive copy helper
  - `run_validation(config)` over the fixed validation set
  - `run_validation_with_summary(config)` returning comparison + summary
  - `validate_behavioral_separation(summary)` returning boolean sanity indicators only
  - handling of static `CDL=None` as a valid “no recovery” baseline case in the diagnostic helper
- Metric validation suite provides:
  - `MetricValidationCheck` and `MetricValidationSuiteResult`
  - `validate_pcm_construct()` showing PCM rises with better pre-switch mastery
  - `validate_cdl_window_behavior()` showing CDL does not trigger on a single lucky correct step and responds to real recovery windows
  - `validate_pr_perseveration_specificity()` showing PR is high for obsolete-policy errors and low for non-perseverative errors
  - `validate_metric_non_redundancy()` showing:
    - same accuracy can yield different PR
    - same PCM can yield different CDL
    - same post-switch error count can yield different PR
    - one lucky correct action does not falsely trigger CDL
  - structured details per check with case metrics, expected relations, and observed relations
  - reuse of existing evaluator logic via `evaluate_core_metrics()` rather than reimplementation
- Evidence summary layer provides:
  - `EvidenceClaim` and `EvidenceSummary`
  - `build_evidence_summary(config)` combining metric validation, baseline separation, and reviewer-facing claims
  - short factual claim explanations tied to explicit evidence keys
  - `render_evidence_summary_markdown(summary)` with compact sections for:
    - Metric Validity
    - Baseline Separation
    - Claims
  - deterministic, packaging-only output suitable for notebook/README/reviewer inspection
- Narrative layer provides:
  - `aceb/narrative/kaggle_submission.md` with concise sections for problem, contribution, key insight, evidence, practical meaning, and conclusion
  - `aceb/narrative/evidence_notes.md` mapping benchmark claims directly to existing evidence sources
  - two explicit additional scientific reinforcement cases in `tests/test_additional_validation_cases.py` showing:
    - same accuracy can still hide different CDL and PR
    - same post-switch error count can still produce sharply different PR
  - deterministic tests that reuse `evaluate_core_metrics()` only
- Full current test suite passes under both `pytest` and `unittest`; latest verified pytest total is 101 passing tests

## Prioritized backlog
### P0
- Review the Kaggle narrative and evidence notes as the first submission-facing package and decide whether wording needs tightening for the target audience
- Use the new controlled reinforcement cases only as long as they add clarity without bloating the benchmark story

### P1
- Expand evaluator evidence later with additional metrics (AHL/PCS/EFF) only after the current narrative and evidence package are accepted
- Add lightweight export/report helpers only after the reviewer-facing package is considered stable

### P2
- Implement broader batch evaluation, richer benchmark analysis, and CLI flow
- Broaden validation across larger seed/episode distributions for stronger benchmark evidence

## Next tasks
1. Review the Kaggle submission narrative and evidence notes for tone and clarity before external submission
2. Decide whether the current two reinforcement cases are sufficient or whether one more tightly targeted example is needed later
3. Extend later with additional metrics only after the current narrative and evidence layer are accepted
