# PRD

## Original problem statement
Task 1 — ShiftRule Implementation

Goal: Implement the core transformation rule for the benchmark.

Requirements:
- Create a Python class `ShiftRule`
- Inputs: `alphabet: list[str]`, `shift: int`
- Applies cyclic shift over alphabet
- Handles wrap-around correctly
- Validates input symbol
- Raises a clear error if symbol is not in alphabet
- Includes tests for basic shift, wrap-around, invalid symbol exception, and preferred negative shift support
- No external dependencies
- Clean, readable code with type hints

## Architecture decisions
- Created a minimal Python package layout under `aceb/` aligned with the benchmark docs
- Added a small abstract `BaseRule` interface in `aceb/rules/base.py`
- Implemented `ShiftRule` in `aceb/rules/shift.py` with explicit validation for empty alphabets, duplicate symbols, and invalid input symbols
- Used standard-library `unittest` tests to avoid external dependencies
- Added `tests/conftest.py` so plain `pytest` works without manual PYTHONPATH setup

## What's been implemented
- `aceb/__init__.py`
- `aceb/rules/__init__.py`
- `aceb/rules/base.py`
- `aceb/rules/shift.py`
- `tests/test_shift_rule.py`
- `tests/conftest.py`

Implemented behavior:
- Positive cyclic shifting
- Correct wrap-around behavior
- Clear `ValueError` for unknown symbols
- Negative shift support
- Passing tests under both `unittest` and `pytest`

## Prioritized backlog
### P0
- Add the next vertical-slice foundation files from the implementation plan (`config.py`, env data types, episode spec)
- Add more `ShiftRule` validation tests if the benchmark will accept arbitrary alphabets from generated configs

### P1
- Implement episode generation (`sampler.py`, `stream.py`, `builder.py`)
- Add tests for valid shift pair sampling and episode construction

### P2
- Implement environment loop, baseline agents, and benchmark metrics
- Add CLI and serialization utilities for end-to-end runs

## Next tasks
1. Build the episode/config data model for the shift-family MVP
2. Implement episode generation with reproducible seeds
3. Add environment stepping and post-switch behavior handling
