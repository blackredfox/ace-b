from pathlib import Path

from aceb.agents.static_shift_agent import StaticShiftAgent
from aceb.config import BenchmarkConfig
from aceb.kaggle.benchmark_adapter import (
    DEFAULT_KAGGLE_EPISODE_IDS,
    KaggleBenchmarkGroup,
    build_task_prototype,
    build_validation_benchmark,
)
from aceb.kaggle.task_adapter import (
    KaggleEpisodeTask,
    build_kaggle_episode_task,
    run_kaggle_episode_task_with_agent,
    score_kaggle_episode_actions,
)
from aceb.rules.ruleset import RuleSet


def test_kaggle_episode_task_is_deterministic() -> None:
    config = BenchmarkConfig(alphabet_size=6, input_length=20, history_window=4, seed=24680)

    first = build_kaggle_episode_task(config, "episode_1")
    second = build_kaggle_episode_task(config, "episode_1")

    assert isinstance(first, KaggleEpisodeTask)
    assert first == second


def test_task_input_preserves_episode_level_interaction_contract() -> None:
    task = build_task_prototype()

    assert task.task_input["interaction_mode"] == "episode_level_multi_turn"
    assert task.task_input["turn_contract"]["hidden_rule_change"] is True
    assert task.task_input["turn_contract"]["model_input_fields"] == [
        "step_id",
        "input_symbol",
        "history",
        "last_feedback",
    ]
    assert task.expected_output["primary_kaggle_sdk_format"] == "one action per turn in a multi-turn task notebook"


def test_score_kaggle_episode_actions_routes_through_existing_core_correctly() -> None:
    task = build_task_prototype()
    rule_set = RuleSet(
        alphabet=task.episode.alphabet,
        shift_pre=task.episode.shift_pre,
        shift_post=task.episode.shift_post,
        switch_step=task.episode.switch_step,
    )
    perfect_actions = [
        rule_set.apply(input_symbol, step_id)
        for step_id, input_symbol in enumerate(task.episode.input_stream)
    ]

    result = score_kaggle_episode_actions(task, perfect_actions)

    assert result.accuracy == 1.0
    assert result.metrics.pcm == 1.0
    assert result.metrics.cdl == 0
    assert result.metrics.pr == 0.0
    assert len(result.trajectory) == len(task.episode.input_stream)


def test_working_task_prototype_runs_with_existing_agent_path() -> None:
    task = build_task_prototype()
    result = run_kaggle_episode_task_with_agent(task, StaticShiftAgent(alphabet=task.episode.alphabet))

    assert result.total_steps == len(task.episode.input_stream)
    assert 0.0 <= result.accuracy <= 1.0
    assert result.metrics.episode_id == task.episode_id


def test_validation_benchmark_group_is_reproducible() -> None:
    first = build_validation_benchmark()
    second = build_validation_benchmark()

    assert isinstance(first, KaggleBenchmarkGroup)
    assert first == second
    assert first.grouping_notes["deterministic"] is True


def test_validation_benchmark_uses_fixed_episode_ids() -> None:
    benchmark = build_validation_benchmark()

    assert benchmark.grouping_notes["episode_ids"] == DEFAULT_KAGGLE_EPISODE_IDS
    assert len(benchmark.tasks) == len(DEFAULT_KAGGLE_EPISODE_IDS)
    assert benchmark.task_ids == [task.task_id for task in benchmark.tasks]


def test_kaggle_readme_documents_hook_points_and_submission_boundaries() -> None:
    text = Path("/app/aceb/kaggle/README.md").read_text(encoding="utf-8")

    assert "Real Kaggle SDK hookup points" in text
    assert "Benchmark core" in text
    assert "Kaggle adapter" in text
    assert "Narrative/docs" in text
    assert ".emergent/" in text
    assert "test_reports/" in text