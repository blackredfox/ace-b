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

## Architecture decisions
- Created a minimal benchmark package structure under `aceb/` aligned with the implementation plan
- Kept primitive transformation logic in `aceb.rules.shift.ShiftRule`
- Kept deterministic episode metadata in `aceb.env.episode.EpisodeSpec`
- Added `aceb.rules.ruleset.RuleSet` as a small composition layer that schedules between two `ShiftRule` instances without introducing environment behavior or history
- Limited validation to lightweight guardrails that protect the data contract and boundary semantics without adding broader business logic
- Kept tests dependency-light with standard-library `unittest`, while also ensuring plain `pytest` works via `tests/conftest.py`

## What's been implemented
- `aceb/rules/base.py`
- `aceb/rules/shift.py`
- `aceb/rules/ruleset.py`
- `aceb/env/episode.py`
- `aceb/rules/__init__.py`
- `aceb/env/__init__.py`
- `tests/test_shift_rule.py`
- `tests/test_episode_spec.py`
- `tests/test_rule_set.py`
- `tests/conftest.py`

Implemented behavior:
- `ShiftRule` supports cyclic positive and negative shifts, wrap-around, and clear invalid-symbol errors
- `EpisodeSpec` stores all deterministic episode parameters with full type hints and lightweight validation
- `RuleSet` deterministically schedules between pre/post `ShiftRule` instances using the required boundary `step_id >= switch_step`
- `RuleSet` rejects negative `step_id` with a clear error and rejects identical pre/post shifts
- Entire current test suite passes under both `pytest` and `unittest`

## Prioritized backlog
### P0
- Add the remaining environment dataclasses (`HistoryItem`, `Feedback`, `Observation`, `Action`, `StepResult`)
- Implement reproducible episode generation for the shift-family MVP

### P1
- Build generator modules: alphabet sampling, shift-pair sampling, input stream generation, and episode builder
- Add tests for generator validity, switch bounds, and reproducibility

### P2
- Implement environment stepping, baseline agents, metrics, and CLI pipeline
- Expand coverage for constructor edge cases and additional invalid data cases where useful

## Next tasks
1. Add the rest of the environment/data dataclasses used by the episode loop
2. Implement the shift-family episode generator with deterministic seeds
3. Add unit tests for generator constraints and RuleSet/EpisodeSpec integration points
