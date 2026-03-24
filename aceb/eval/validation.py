from __future__ import annotations

from dataclasses import dataclass

from aceb.env.episode import EpisodeSpec
from aceb.env.types import TrajectoryRecord
from aceb.eval.core_metrics import evaluate_core_metrics
from aceb.rules.ruleset import RuleSet


@dataclass
class MetricValidationCheck:
    name: str
    passed: bool
    details: dict[str, object]


@dataclass
class MetricValidationSuiteResult:
    checks: list[MetricValidationCheck]


def validate_pcm_construct() -> MetricValidationCheck:
    episode = _base_validation_episode()
    strong_mastery = _build_trajectory(
        episode,
        actions=["B", "C", "D", "A", "B", "C", "D", "A"],
    )
    weak_mastery = _build_trajectory(
        episode,
        actions=["B", "C", "A", "B", "B", "C", "D", "A"],
    )

    strong_metrics = evaluate_core_metrics(episode, strong_mastery)
    weak_metrics = evaluate_core_metrics(episode, weak_mastery)
    observed_relation = strong_metrics.pcm > weak_metrics.pcm

    return MetricValidationCheck(
        name="pcm_construct_validity",
        passed=observed_relation,
        details={
            "case_1": _snapshot(strong_metrics, strong_mastery),
            "case_2": _snapshot(weak_metrics, weak_mastery),
            "expected_relation": "case_1_pcm > case_2_pcm",
            "observed_relation": observed_relation,
        },
    )


def validate_cdl_window_behavior() -> MetricValidationCheck:
    episode = _base_validation_episode()
    lucky_fluctuation = _build_trajectory(
        episode,
        actions=["B", "C", "D", "A", "B", "D", "B", "C"],
    )
    real_recovery = _build_trajectory(
        episode,
        actions=["B", "C", "D", "A", "B", "A", "A", "B"],
    )

    lucky_metrics = evaluate_core_metrics(episode, lucky_fluctuation)
    recovery_metrics = evaluate_core_metrics(episode, real_recovery)
    observed_relation = lucky_metrics.cdl is None and recovery_metrics.cdl == 1

    return MetricValidationCheck(
        name="cdl_window_behavior",
        passed=observed_relation,
        details={
            "case_1": _snapshot(lucky_metrics, lucky_fluctuation),
            "case_2": _snapshot(recovery_metrics, real_recovery),
            "expected_relation": "case_1_cdl is None and case_2_cdl == 1",
            "observed_relation": observed_relation,
        },
    )


def validate_pr_perseveration_specificity() -> MetricValidationCheck:
    episode = _base_validation_episode()
    perseverative_errors = _build_trajectory(
        episode,
        actions=["B", "C", "D", "A", "B", "C", "D", "A"],
    )
    non_perseverative_errors = _build_trajectory(
        episode,
        actions=["B", "C", "D", "A", "D", "A", "B", "C"],
    )

    perseverative_metrics = evaluate_core_metrics(episode, perseverative_errors)
    non_perseverative_metrics = evaluate_core_metrics(episode, non_perseverative_errors)
    observed_relation = perseverative_metrics.pr > non_perseverative_metrics.pr

    return MetricValidationCheck(
        name="pr_perseveration_specificity",
        passed=observed_relation,
        details={
            "case_1": _snapshot(perseverative_metrics, perseverative_errors),
            "case_2": _snapshot(non_perseverative_metrics, non_perseverative_errors),
            "expected_relation": "case_1_pr > case_2_pr",
            "observed_relation": observed_relation,
        },
    )


def validate_metric_non_redundancy() -> MetricValidationCheck:
    episode = _base_validation_episode()

    same_accuracy_perseverative = _build_trajectory(
        episode,
        actions=["B", "C", "D", "A", "B", "C", "D", "A"],
    )
    same_accuracy_non_perseverative = _build_trajectory(
        episode,
        actions=["B", "C", "D", "A", "D", "A", "B", "C"],
    )
    same_pcm_slow_recovery = _build_trajectory(
        episode,
        actions=["B", "C", "D", "A", "B", "D", "B", "C"],
    )
    same_pcm_recovery = _build_trajectory(
        episode,
        actions=["B", "C", "D", "A", "B", "A", "A", "B"],
    )

    perseverative_metrics = evaluate_core_metrics(episode, same_accuracy_perseverative)
    non_perseverative_metrics = evaluate_core_metrics(episode, same_accuracy_non_perseverative)
    slow_recovery_metrics = evaluate_core_metrics(episode, same_pcm_slow_recovery)
    recovery_metrics = evaluate_core_metrics(episode, same_pcm_recovery)

    same_accuracy_different_pr = (
        _accuracy(same_accuracy_perseverative) == _accuracy(same_accuracy_non_perseverative)
        and perseverative_metrics.pr > non_perseverative_metrics.pr
    )
    same_pcm_different_cdl = (
        slow_recovery_metrics.pcm == recovery_metrics.pcm
        and slow_recovery_metrics.cdl != recovery_metrics.cdl
    )
    same_error_different_pr = (
        _post_switch_error_count(episode, same_accuracy_perseverative)
        == _post_switch_error_count(episode, same_accuracy_non_perseverative)
        and perseverative_metrics.pr > non_perseverative_metrics.pr
    )
    lucky_correct_does_not_trigger_cdl = slow_recovery_metrics.cdl is None

    passed = all(
        [
            same_accuracy_different_pr,
            same_pcm_different_cdl,
            same_error_different_pr,
            lucky_correct_does_not_trigger_cdl,
        ]
    )

    return MetricValidationCheck(
        name="metric_non_redundancy",
        passed=passed,
        details={
            "case_same_accuracy_perseverative": _snapshot(perseverative_metrics, same_accuracy_perseverative),
            "case_same_accuracy_non_perseverative": _snapshot(non_perseverative_metrics, same_accuracy_non_perseverative),
            "case_same_pcm_slow_recovery": _snapshot(slow_recovery_metrics, same_pcm_slow_recovery),
            "case_same_pcm_recovery": _snapshot(recovery_metrics, same_pcm_recovery),
            "expected_relation": {
                "same_accuracy_different_pr": True,
                "same_pcm_different_cdl": True,
                "same_error_different_pr": True,
                "lucky_correct_does_not_trigger_cdl": True,
            },
            "observed_relation": {
                "same_accuracy_different_pr": same_accuracy_different_pr,
                "same_pcm_different_cdl": same_pcm_different_cdl,
                "same_error_different_pr": same_error_different_pr,
                "lucky_correct_does_not_trigger_cdl": lucky_correct_does_not_trigger_cdl,
            },
        },
    )


def run_metric_validation_suite() -> MetricValidationSuiteResult:
    return MetricValidationSuiteResult(
        checks=[
            validate_pcm_construct(),
            validate_cdl_window_behavior(),
            validate_pr_perseveration_specificity(),
            validate_metric_non_redundancy(),
        ]
    )


def _base_validation_episode() -> EpisodeSpec:
    return EpisodeSpec(
        episode_id="metric-validation-episode",
        alphabet=["A", "B", "C", "D"],
        input_stream=["A", "B", "C", "D", "A", "B", "C", "D"],
        shift_pre=1,
        shift_post=2,
        switch_step=4,
        history_window=3,
        seed=999,
    )


def _build_trajectory(episode: EpisodeSpec, actions: list[str]) -> list[TrajectoryRecord]:
    if len(actions) != len(episode.input_stream):
        raise ValueError("actions length must match episode input_stream length")

    return [_make_record(episode, step_id, action) for step_id, action in enumerate(actions)]


def _make_record(episode: EpisodeSpec, step_id: int, action: str) -> TrajectoryRecord:
    rule_set = RuleSet(
        alphabet=episode.alphabet,
        shift_pre=episode.shift_pre,
        shift_post=episode.shift_post,
        switch_step=episode.switch_step,
    )
    input_symbol = episode.input_stream[step_id]
    expected_output = rule_set.apply(input_symbol, step_id)
    correct = action == expected_output

    return TrajectoryRecord(
        step_id=step_id,
        input_symbol=input_symbol,
        action=action,
        expected_output=expected_output,
        correct=correct,
        reward=1.0 if correct else 0.0,
        post_switch=rule_set.is_post_switch(step_id),
    )


def _snapshot(result: object, trajectory: list[TrajectoryRecord]) -> dict[str, float | int | None]:
    return {
        "pcm": result.pcm,
        "cdl": result.cdl,
        "pr": result.pr,
        "accuracy": _accuracy(trajectory),
    }


def _accuracy(trajectory: list[TrajectoryRecord]) -> float:
    return sum(1 for record in trajectory if record.correct) / len(trajectory)


def _post_switch_error_count(episode: EpisodeSpec, trajectory: list[TrajectoryRecord]) -> int:
    return sum(1 for record in trajectory if record.step_id >= episode.switch_step and not record.correct)
