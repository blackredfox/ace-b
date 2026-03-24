from __future__ import annotations

from dataclasses import dataclass

from aceb.config import BenchmarkConfig
from aceb.kaggle.task_adapter import KaggleEpisodeTask, build_kaggle_episode_task
from aceb.validation.validation_set import get_validation_episode_ids


DEFAULT_KAGGLE_BENCHMARK_CONFIG = BenchmarkConfig(
    alphabet_size=6,
    input_length=20,
    history_window=4,
    seed=24680,
)
DEFAULT_KAGGLE_EPISODE_IDS = get_validation_episode_ids()


@dataclass
class KaggleBenchmarkGroup:
    benchmark_name: str
    benchmark_description: str
    task_ids: list[str]
    tasks: list[KaggleEpisodeTask]
    grouping_notes: dict[str, object]
    sdk_hook_points: dict[str, str]


def build_task_prototype(
    config: BenchmarkConfig = DEFAULT_KAGGLE_BENCHMARK_CONFIG,
    episode_id: str = "episode_1",
) -> KaggleEpisodeTask:
    return build_kaggle_episode_task(config, episode_id)


def build_validation_benchmark(
    config: BenchmarkConfig = DEFAULT_KAGGLE_BENCHMARK_CONFIG,
    episode_ids: list[str] | None = None,
) -> KaggleBenchmarkGroup:
    selected_episode_ids = DEFAULT_KAGGLE_EPISODE_IDS if episode_ids is None else episode_ids.copy()
    tasks = [build_kaggle_episode_task(config, episode_id) for episode_id in selected_episode_ids]

    return KaggleBenchmarkGroup(
        benchmark_name="ace-b-rcs1-validation-benchmark",
        benchmark_description=(
            "Deterministic ACE-B / RCS-1 review set for thin Kaggle Benchmarks migration. "
            "Each task wraps one episode-level hidden-rule-change interaction."
        ),
        task_ids=[task.task_id for task in tasks],
        tasks=tasks,
        grouping_notes={
            "episode_ids": selected_episode_ids,
            "deterministic": True,
            "core_source_of_truth": "ACE-B generator, environment, and evaluator remain unchanged.",
        },
        sdk_hook_points={
            "task_creation": "Create one Kaggle task notebook per task in this group.",
            "benchmark_creation": "Create a Kaggle Benchmark in the UI and attach these task notebooks.",
            "model_routing": "Let Kaggle Benchmarks manage model execution; keep ACE-B scoring in the task logic.",
        },
    )
