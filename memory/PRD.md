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
- Full current test suite passes under both `pytest` and `unittest`; latest verified pytest total is 72 passing tests

## Prioritized backlog
### P0
- Add stronger benchmark validation across more controlled episode sets to show clearer quantitative separation between random, static, and adaptive baselines
- Prepare the next evaluation layer only after the current comparison outputs are reviewed and accepted

### P1
- Add small multi-episode helper utilities for repeated comparison experiments without introducing CLI or exports yet
- Expand negative tests for comparison edge cases and metric validation branches

### P2
- Implement additional metrics (AHL/PCS/EFF), batch evaluation, aggregate reporting, and CLI flow
- Broaden benchmark validation across larger seed/episode distributions

## Next tasks
1. Add a small deterministic multi-episode validation set and inspect whether baseline separation stays consistent across more generated episodes
2. Extend the evaluator later with AHL, PCS, and EFF after the current comparison layer is reviewed
3. Add optional export/report helpers only after the core evaluation and comparison contracts are stable
