# ACE-B / RCS-1 Kaggle Adapter

This directory provides a **thin Kaggle Benchmarks migration layer** over the existing ACE-B / RCS-1 core.

It does **not** rewrite the benchmark. Instead, it defines the smallest explicit boundary needed to map the current benchmark into Kaggle task and benchmark concepts.

## What the adapter does

- `task_adapter.py` wraps one deterministic `EpisodeSpec` as a Kaggle-facing episode task.
- `benchmark_adapter.py` builds a small deterministic benchmark grouping over a fixed episode set.
- Local verification and scoring always reuse the ACE-B core:
  - `build_episode_spec(...)`
  - `RCSEnvironment`
  - trajectory generation
  - `evaluate_core_metrics(...)`

## What remains in the benchmark core

The ACE-B core remains the source of truth for:

- episode generation
- hidden pre/post rule scheduling
- environment stepping
- feedback and trajectory recording
- PCM / CDL / PR evaluation

The Kaggle layer is only an integration wrapper.

## Task input / output boundary

### Task input

The adapter exposes an **episode-level multi-turn task contract**:

- the model sees one observation at a time
- each observation contains `step_id`, `input_symbol`, bounded `history`, and `last_feedback`
- the hidden rule change is not exposed directly

### Expected output

The intended Kaggle SDK path is **one predicted symbol per turn** in a multi-turn task notebook.

For local verification in this repository, the fallback response format is a structured sequence:

```python
{"actions": ["A", "B", ...]}
```

This keeps verification machine-checkable while preserving the episode contract.

## Verification / scoring path

The adapter does not duplicate rule logic manually.

- `score_kaggle_episode_actions(...)` replays a full action sequence through `RCSEnvironment`
- `run_kaggle_episode_task_with_agent(...)` runs an existing ACE-B agent through the same task
- both paths produce trajectories that are scored with `evaluate_core_metrics(...)`

## Benchmark grouping

`build_validation_benchmark(...)` creates a small deterministic benchmark group over the fixed validation episode IDs.

This is the recommended first migration target because it is:

- deterministic
- small enough for review
- already supported by the project’s validation evidence

## Real Kaggle SDK hookup points

The current environment does not instantiate the real Kaggle SDK objects.
When migrating into Kaggle Benchmarks, plug the adapter in as follows:

1. **Task notebook / task function**
   - Use the `KaggleEpisodeTask.task_input` contract to define the notebook task.
   - The real task should execute one turn at a time if Kaggle’s multi-turn task flow is available.

2. **Model interaction**
   - On each turn, the model returns a single symbol from the episode alphabet.
   - The notebook task feeds back correctness and the next observation.

3. **Task files / run files**
   - Let Kaggle Benchmarks generate task and run artifacts.
   - Keep ACE-B environment stepping and trajectory scoring inside the task logic.

4. **Benchmark grouping in Kaggle UI**
   - Add the resulting task notebooks to a Kaggle Benchmark collection.
   - Use the validation episode set first before expanding to larger review sets.

## Known limitations of this initial migration

- This repository does **not** create real `@kbench.task` notebooks yet.
- The local fallback scorer accepts a full action sequence, which is a practical stand-in for the intended multi-turn Kaggle interaction.
- If Kaggle task execution cannot preserve full turn-by-turn interaction, that limitation should be documented in the submission because it weakens the benchmark’s adaptive signal.

## Submission-facing repository boundary

Recommended submission-facing folders:

- **Benchmark core:** `aceb/rules`, `aceb/env`, `aceb/generator`, `aceb/runner`, `aceb/eval`, `aceb/validation`
- **Kaggle adapter:** `aceb/kaggle`
- **Narrative/docs:** `aceb/narrative`

Development-only artifacts that should not be part of submission packaging unless specifically needed:

- `.emergent/`
- `test_reports/`
- `tests/`
- `__pycache__/`
- `.pytest_cache/`

If `.emergent/` is only used for workspace tooling, exclude it from submission-facing packaging.
