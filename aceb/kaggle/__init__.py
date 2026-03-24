"""Thin Kaggle Benchmarks adapter layer for ACE-B / RCS-1."""

from .benchmark_adapter import (
    DEFAULT_KAGGLE_BENCHMARK_CONFIG,
    DEFAULT_KAGGLE_EPISODE_IDS,
    KaggleBenchmarkGroup,
    build_task_prototype,
    build_validation_benchmark,
)
from .task_adapter import (
    KaggleEpisodeTask,
    KaggleEpisodeTaskResult,
    build_kaggle_episode_task,
    run_kaggle_episode_task_with_agent,
    score_kaggle_episode_actions,
)

__all__ = [
    "DEFAULT_KAGGLE_BENCHMARK_CONFIG",
    "DEFAULT_KAGGLE_EPISODE_IDS",
    "KaggleBenchmarkGroup",
    "KaggleEpisodeTask",
    "KaggleEpisodeTaskResult",
    "build_kaggle_episode_task",
    "build_task_prototype",
    "build_validation_benchmark",
    "run_kaggle_episode_task_with_agent",
    "score_kaggle_episode_actions",
]
