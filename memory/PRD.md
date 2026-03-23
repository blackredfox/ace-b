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

## Architecture decisions
- Created a minimal benchmark package structure under `aceb/` aligned with the implementation plan
- Kept primitive transformation logic in `aceb.rules.shift.ShiftRule`
- Kept deterministic episode metadata in `aceb.env.episode.EpisodeSpec`
- Added `aceb.rules.ruleset.RuleSet` as a small composition layer that schedules between two `ShiftRule` instances without environment behavior
- Added a minimal `aceb.config.BenchmarkConfig` contract for generation only
- Implemented episode generation in `aceb.generator.builder` using only the Python standard library
- Used SHA-256 over `base_seed:episode_id` to derive deterministic episode-level seeds
- Implemented environment execution in `aceb.env.environment.RCSEnvironment` with explicit lifecycle state and bounded observation history
- Kept validation lightweight and focused on correctness of generation and execution contracts rather than broader business rules

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
- `aceb/rules/__init__.py`
- `aceb/env/__init__.py`
- `tests/test_shift_rule.py`
- `tests/test_episode_spec.py`
- `tests/test_rule_set.py`
- `tests/test_episode_builder.py`
- `tests/test_environment.py`
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
- `RCSEnvironment` now provides:
  - explicit `reset() -> Observation`
  - explicit `step(action: str) -> StepResult`
  - `get_trajectory()` returning a safe copy
  - reward mapping of `1.0` or `0.0`
  - bounded observation history based on `history_window`
  - clear runtime errors before reset and after completion
  - one `TrajectoryRecord` per executed step
- Full current test suite passes under both `pytest` and `unittest`; latest verified pytest total is 31 passing tests

## Prioritized backlog
### P0
- Add the remaining richer environment dataclasses if needed later (e.g. separate feedback/history item types only if truly necessary)
- Implement agent interfaces and a single-episode runner around `RCSEnvironment`

### P1
- Add perseveration-related helper logic and evaluation-ready annotations outside the environment core loop
- Expand environment hardening tests around deeper copy semantics and additional invalid state edge cases

### P2
- Implement baseline agents, trajectory runner, benchmark metrics, and CLI pipeline
- Broaden property-style coverage across multiple seeds and episode ids

## Next tasks
1. Add baseline agent interfaces and a simple runner that can interact with `RCSEnvironment`
2. Implement the evaluator-side trajectory and metric layer outside the environment
3. Add end-to-end tests that generate an episode, execute it in the environment, and validate recorded behavior
