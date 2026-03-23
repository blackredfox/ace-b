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
- `AdaptiveShiftAgent` now:
  - searches non-zero shift candidates deterministically
  - commits after configurable consistent confirmations
  - uses the committed shift while feedback remains correct
  - tracks failure streak after commit
  - drops a failed hypothesis after the configured threshold
  - continues from the next candidate shift in order after revision
  - re-commits to a new hypothesis after renewed evidence
  - remains fully non-oracle and feedback-driven
- `run_episode()` supports all current agents end-to-end and returns full trajectory plus minimal summary statistics
- Full current test suite passes under both `pytest` and `unittest`; latest verified pytest total is 52 passing tests

## Prioritized backlog
### P0
- Implement evaluator-side metric functions for adaptation behavior (PCM, CDL, PR, later AHL/PCS/EFF)
- Add comparative end-to-end tests showing clear separation across random, static, and adaptive agents over generated episode sets

### P1
- Add richer runner helpers for multiple episodes without introducing full CLI or aggregation yet
- Strengthen constructor validation and more long-horizon adaptive behavior tests where useful

### P2
- Implement batch evaluation, aggregate summaries, and CLI flow
- Expand benchmark validation across broader seeds and episode distributions

## Next tasks
1. Implement evaluator metrics on top of recorded trajectories and switch-step metadata
2. Add comparative tests that measure separation between Random, Static, and Adaptive behaviors
3. Build a small multi-episode runner once the metric layer is in place
