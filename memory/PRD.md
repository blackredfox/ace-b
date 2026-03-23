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

## Architecture decisions
- Created a minimal benchmark package structure under `aceb/` that follows the implementation plan from the docs
- Added `BaseRule` and `ShiftRule` in the `aceb.rules` package
- Added `EpisodeSpec` in `aceb.env.episode` as a standalone data contract, uncoupled from rule logic
- Limited validation to lightweight `__post_init__` checks that protect the data contract without adding operational behavior
- Kept tests dependency-light with standard-library `unittest`, while also ensuring plain `pytest` works via `tests/conftest.py`

## What's been implemented
- `aceb/rules/base.py`
- `aceb/rules/shift.py`
- `aceb/env/episode.py`
- `aceb/rules/__init__.py`
- `aceb/env/__init__.py`
- `tests/test_shift_rule.py`
- `tests/test_episode_spec.py`
- `tests/conftest.py`

Implemented behavior:
- `ShiftRule` supports cyclic positive and negative shifts, wrap-around, and clear invalid-symbol errors
- `EpisodeSpec` stores all deterministic episode parameters with full type hints
- Lightweight `EpisodeSpec` validation checks:
  - alphabet has at least 2 symbols
  - input stream is not empty
  - switch step stays within input stream bounds
  - pre/post shifts are different
- Test suite passes under both `pytest` and `unittest`

## Prioritized backlog
### P0
- Add the remaining foundation types for the environment layer (history items, feedback, observation, action)
- Implement config and episode generation scaffolding for the shift-family MVP

### P1
- Build generator modules: alphabet sampling, shift-pair sampling, input stream generation, and episode builder
- Add tests for generator validity and reproducibility

### P2
- Implement environment stepping, baseline agents, metrics, and CLI pipeline
- Expand validation and test coverage for additional invalid data cases if needed

## Next tasks
1. Add the remaining environment dataclasses used by the episode loop
2. Implement reproducible episode generation for the shift-family benchmark
3. Add unit tests for generator constraints and deterministic episode specs
