from __future__ import annotations

from dataclasses import dataclass

from aceb.agents.base import BaseAgent
from aceb.config import BenchmarkConfig
from aceb.env.environment import RCSEnvironment
from aceb.env.episode import EpisodeSpec
from aceb.env.types import Observation, TrajectoryRecord
from aceb.eval.core_metrics import evaluate_core_metrics
from aceb.eval.types import CoreMetricResult
from aceb.generator.builder import build_episode_spec
from aceb.runner.episode_runner import run_episode


@dataclass
class KaggleEpisodeTask:
    task_id: str
    benchmark_name: str
    episode_id: str
    episode: EpisodeSpec
    task_input: dict[str, object]
    expected_output: dict[str, object]
    verification_path: dict[str, str]
    sdk_hook_points: dict[str, str]


@dataclass
class KaggleEpisodeTaskResult:
    task_id: str
    episode_id: str
    total_steps: int
    total_correct: int
    accuracy: float
    metrics: CoreMetricResult
    trajectory: list[TrajectoryRecord]


def build_kaggle_episode_task(config: BenchmarkConfig, episode_id: str) -> KaggleEpisodeTask:
    episode = build_episode_spec(config, episode_id)
    environment = RCSEnvironment(episode)
    initial_observation = environment.reset()

    return KaggleEpisodeTask(
        task_id=f"rcs1-{episode_id}",
        benchmark_name="ACE-B / RCS-1",
        episode_id=episode_id,
        episode=episode,
        task_input={
            "interaction_mode": "episode_level_multi_turn",
            "instruction": (
                "Infer the hidden symbol transformation rule from turn-by-turn feedback. "
                "At each turn, return exactly one symbol from the provided alphabet."
            ),
            "initial_observation": _serialize_observation(initial_observation),
            "turn_contract": {
                "model_input_fields": ["step_id", "input_symbol", "history", "last_feedback"],
                "model_output_format": {"action": "single symbol from the episode alphabet"},
                "feedback_fields": ["correct", "reward", "done"],
                "history_window": episode.history_window,
                "hidden_rule_change": True,
            },
        },
        expected_output={
            "primary_kaggle_sdk_format": "one action per turn in a multi-turn task notebook",
            "local_fallback_format": {
                "actions": ["single symbol per episode step"],
            },
        },
        verification_path={
            "core_source_of_truth": "EpisodeSpec -> RCSEnvironment -> trajectory -> evaluate_core_metrics",
            "local_scoring_entrypoint": "score_kaggle_episode_actions",
            "agent_prototype_entrypoint": "run_kaggle_episode_task_with_agent",
        },
        sdk_hook_points={
            "task_definition": "Wrap the episode interaction in a Kaggle Benchmarks task function or notebook task.",
            "model_interaction": "Feed one observation per turn and record one returned symbol per turn.",
            "benchmark_grouping": "Add the produced task notebooks to a Kaggle Benchmark collection in the UI.",
        },
    )


def score_kaggle_episode_actions(
    task: KaggleEpisodeTask,
    actions: list[str],
) -> KaggleEpisodeTaskResult:
    _validate_actions(task.episode, actions)

    environment = RCSEnvironment(task.episode)
    environment.reset()
    for action in actions:
        environment.step(action)

    trajectory = environment.get_trajectory()
    metrics = evaluate_core_metrics(task.episode, trajectory)
    total_steps = len(trajectory)
    total_correct = sum(1 for record in trajectory if record.correct)

    return KaggleEpisodeTaskResult(
        task_id=task.task_id,
        episode_id=task.episode_id,
        total_steps=total_steps,
        total_correct=total_correct,
        accuracy=total_correct / total_steps if total_steps else 0.0,
        metrics=metrics,
        trajectory=trajectory,
    )


def run_kaggle_episode_task_with_agent(
    task: KaggleEpisodeTask,
    agent: BaseAgent,
) -> KaggleEpisodeTaskResult:
    run_result = run_episode(RCSEnvironment(task.episode), agent)
    metrics = evaluate_core_metrics(task.episode, run_result.trajectory)

    return KaggleEpisodeTaskResult(
        task_id=task.task_id,
        episode_id=task.episode_id,
        total_steps=run_result.total_steps,
        total_correct=run_result.total_correct,
        accuracy=run_result.accuracy,
        metrics=metrics,
        trajectory=run_result.trajectory,
    )


def _serialize_observation(observation: Observation) -> dict[str, object]:
    return {
        "step_id": observation.step_id,
        "input_symbol": observation.input_symbol,
        "history": observation.history,
        "last_feedback": observation.last_feedback,
    }


def _validate_actions(episode: EpisodeSpec, actions: list[str]) -> None:
    if len(actions) != len(episode.input_stream):
        raise ValueError("actions length must match episode input_stream length")
    invalid_actions = [action for action in actions if action not in episode.alphabet]
    if invalid_actions:
        raise ValueError("all actions must be symbols from the episode alphabet")
