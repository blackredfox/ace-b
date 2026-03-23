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

## Architecture decisions
- Created a minimal benchmark package structure under `aceb/` aligned with the implementation plan
- Kept primitive transformation logic in `aceb.rules.shift.ShiftRule`
- Kept deterministic episode metadata in `aceb.env.episode.EpisodeSpec`
- Added `aceb.rules.ruleset.RuleSet` as a small composition layer that schedules between two `ShiftRule` instances without environment behavior
- Added a minimal `aceb.config.BenchmarkConfig` contract for generation only
- Implemented episode generation in `aceb.generator.builder` using only the Python standard library
- Used SHA-256 over `base_seed:episode_id` to derive deterministic episode-level seeds
- Kept validation lightweight and focused on correctness of generation constraints rather than broad business rules

## What's been implemented
- `aceb/config.py`
- `aceb/generator/__init__.py`
- `aceb/generator/builder.py`
- `aceb/rules/base.py`
- `aceb/rules/shift.py`
- `aceb/rules/ruleset.py`
- `aceb/env/episode.py`
- `aceb/rules/__init__.py`
- `aceb/env/__init__.py`
- `tests/test_shift_rule.py`
- `tests/test_episode_spec.py`
- `tests/test_rule_set.py`
- `tests/test_episode_builder.py`
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
- Full current test suite passes under both `pytest` and `unittest`

## Prioritized backlog
### P0
- Add the remaining environment dataclasses (`HistoryItem`, `Feedback`, `Observation`, `Action`, `StepResult`)
- Implement the environment loop that consumes `EpisodeSpec` and `RuleSet`

### P1
- Expand generator coverage with negative-path tests for invalid ratio bands and impossible configs
- Add dedicated sampler/stream modules if the generator layer is split further

### P2
- Implement baseline agents, trajectory runner, benchmark metrics, and CLI pipeline
- Broaden property-style coverage across multiple seeds and episode ids

## Next tasks
1. Add the rest of the environment/data dataclasses used by the episode loop
2. Implement `RCSEnvironment.reset()` and `step()` around `EpisodeSpec` and `RuleSet`
3. Add environment tests for pre-switch, post-switch, and perseveration-ready behavior
