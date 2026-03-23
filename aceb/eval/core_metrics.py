from __future__ import annotations

from aceb.env.episode import EpisodeSpec
from aceb.env.types import TrajectoryRecord
from aceb.eval.types import CoreMetricResult
from aceb.rules.shift import ShiftRule


def compute_pcm(episode: EpisodeSpec, trajectory: list[TrajectoryRecord]) -> float:
    _validate_trajectory(episode, trajectory)

    pre_change_records = [record for record in trajectory if record.step_id < episode.switch_step]
    if not pre_change_records:
        raise ValueError("trajectory contains no pre-change steps")

    correct_count = sum(1 for record in pre_change_records if record.correct)
    return correct_count / len(pre_change_records)


def compute_cdl(
    episode: EpisodeSpec,
    trajectory: list[TrajectoryRecord],
    window_size: int = 3,
    required_correct_in_window: int = 2,
) -> int | None:
    _validate_trajectory(episode, trajectory)
    _validate_window_params(window_size, required_correct_in_window)

    post_switch_records = [record for record in trajectory if record.step_id >= episode.switch_step]
    if len(post_switch_records) < window_size:
        return None

    for start_index in range(len(post_switch_records) - window_size + 1):
        window = post_switch_records[start_index : start_index + window_size]
        correct_count = sum(1 for record in window if record.correct)
        if correct_count >= required_correct_in_window:
            return start_index

    return None


def compute_pr(episode: EpisodeSpec, trajectory: list[TrajectoryRecord]) -> float:
    _validate_trajectory(episode, trajectory)

    pre_rule = ShiftRule(alphabet=episode.alphabet, shift=episode.shift_pre)
    post_switch_errors = [
        record
        for record in trajectory
        if record.step_id >= episode.switch_step and not record.correct
    ]
    if not post_switch_errors:
        return 0.0

    perseverative_errors = sum(
        1
        for record in post_switch_errors
        if record.action == pre_rule.apply(record.input_symbol)
    )
    return perseverative_errors / len(post_switch_errors)


def evaluate_core_metrics(
    episode: EpisodeSpec,
    trajectory: list[TrajectoryRecord],
    window_size: int = 3,
    required_correct_in_window: int = 2,
) -> CoreMetricResult:
    _validate_trajectory(episode, trajectory)
    _validate_window_params(window_size, required_correct_in_window)

    return CoreMetricResult(
        episode_id=episode.episode_id,
        pcm=compute_pcm(episode, trajectory),
        cdl=compute_cdl(
            episode,
            trajectory,
            window_size=window_size,
            required_correct_in_window=required_correct_in_window,
        ),
        pr=compute_pr(episode, trajectory),
    )


def _validate_trajectory(episode: EpisodeSpec, trajectory: list[TrajectoryRecord]) -> None:
    if not trajectory:
        raise ValueError("trajectory must not be empty")
    if len(trajectory) != len(episode.input_stream):
        raise ValueError("trajectory length must match episode input_stream length")

    expected_step_ids = list(range(len(trajectory)))
    actual_step_ids = [record.step_id for record in trajectory]
    if actual_step_ids != expected_step_ids:
        raise ValueError("trajectory step ordering must be coherent")


def _validate_window_params(window_size: int, required_correct_in_window: int) -> None:
    if window_size < 1:
        raise ValueError("window_size must be at least 1")
    if required_correct_in_window < 1:
        raise ValueError("required_correct_in_window must be at least 1")
    if required_correct_in_window > window_size:
        raise ValueError("required_correct_in_window must be less than or equal to window_size")
