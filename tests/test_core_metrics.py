import unittest

from aceb.env.episode import EpisodeSpec
from aceb.env.types import TrajectoryRecord
from aceb.eval.core_metrics import compute_cdl, compute_pcm, compute_pr, evaluate_core_metrics
from aceb.eval.types import CoreMetricResult


class CoreMetricTests(unittest.TestCase):
    def setUp(self) -> None:
        self.episode = EpisodeSpec(
            episode_id="metrics-episode-001",
            alphabet=["A", "B", "C", "D"],
            input_stream=["A", "B", "C", "D", "A", "B", "C", "D"],
            shift_pre=1,
            shift_post=2,
            switch_step=4,
            history_window=3,
            seed=101,
        )

    def test_pcm_is_computed_correctly_for_mixed_pre_switch_accuracy(self) -> None:
        trajectory = self._make_trajectory([True, True, False, False, False, False, False, False])

        self.assertEqual(compute_pcm(self.episode, trajectory), 0.5)

    def test_pcm_returns_one_for_perfect_pre_change_behavior(self) -> None:
        trajectory = self._make_trajectory([True, True, True, True, False, False, False, False])

        self.assertEqual(compute_pcm(self.episode, trajectory), 1.0)

    def test_pcm_returns_zero_for_total_pre_change_failure(self) -> None:
        trajectory = self._make_trajectory([False, False, False, False, True, True, True, True])

        self.assertEqual(compute_pcm(self.episode, trajectory), 0.0)

    def test_cdl_detects_first_valid_success_window(self) -> None:
        trajectory = self._make_trajectory([True, True, True, True, False, False, True, True])

        self.assertEqual(compute_cdl(self.episode, trajectory), 1)

    def test_cdl_does_not_trigger_on_single_lucky_correct_step(self) -> None:
        trajectory = self._make_trajectory([True, True, True, True, True, False, False, False])

        self.assertIsNone(compute_cdl(self.episode, trajectory))

    def test_cdl_returns_none_when_no_recovery_window_exists(self) -> None:
        trajectory = self._make_trajectory([True, True, True, True, False, False, False, False])

        self.assertIsNone(compute_cdl(self.episode, trajectory))

    def test_cdl_returns_none_when_post_switch_segment_is_shorter_than_window(self) -> None:
        short_episode = EpisodeSpec(
            episode_id="metrics-episode-short",
            alphabet=["A", "B", "C", "D"],
            input_stream=["A", "B", "C", "D", "A"],
            shift_pre=1,
            shift_post=2,
            switch_step=3,
            history_window=2,
            seed=102,
        )
        trajectory = [
            self._make_record(0, "A", "B", True),
            self._make_record(1, "B", "C", True),
            self._make_record(2, "C", "D", True),
            self._make_record(3, "D", "B", True),
            self._make_record(4, "A", "C", True),
        ]

        self.assertIsNone(compute_cdl(short_episode, trajectory, window_size=3, required_correct_in_window=2))

    def test_pr_counts_only_post_switch_errors_matching_pre_change_rule(self) -> None:
        trajectory = [
            self._make_record(0, "A", "B", True),
            self._make_record(1, "B", "C", True),
            self._make_record(2, "C", "D", True),
            self._make_record(3, "D", "A", True),
            self._make_record(4, "A", "B", False),
            self._make_record(5, "B", "C", False),
            self._make_record(6, "C", "A", False),
            self._make_record(7, "D", "B", True),
        ]

        self.assertEqual(compute_pr(self.episode, trajectory), 2 / 3)

    def test_pr_does_not_count_non_perseverative_post_switch_errors(self) -> None:
        trajectory = [
            self._make_record(0, "A", "B", True),
            self._make_record(1, "B", "C", True),
            self._make_record(2, "C", "D", True),
            self._make_record(3, "D", "A", True),
            self._make_record(4, "A", "D", False),
            self._make_record(5, "B", "A", False),
            self._make_record(6, "C", "B", True),
            self._make_record(7, "D", "B", True),
        ]

        self.assertEqual(compute_pr(self.episode, trajectory), 0.0)

    def test_pr_returns_zero_when_there_are_no_post_switch_errors(self) -> None:
        trajectory = [
            self._make_record(0, "A", "B", True),
            self._make_record(1, "B", "C", True),
            self._make_record(2, "C", "D", True),
            self._make_record(3, "D", "A", True),
            self._make_record(4, "A", "C", True),
            self._make_record(5, "B", "D", True),
            self._make_record(6, "C", "A", True),
            self._make_record(7, "D", "B", True),
        ]

        self.assertEqual(compute_pr(self.episode, trajectory), 0.0)

    def test_evaluate_core_metrics_returns_expected_combined_result(self) -> None:
        trajectory = [
            self._make_record(0, "A", "B", True),
            self._make_record(1, "B", "C", True),
            self._make_record(2, "C", "D", False),
            self._make_record(3, "D", "A", True),
            self._make_record(4, "A", "B", False),
            self._make_record(5, "B", "C", False),
            self._make_record(6, "C", "A", True),
            self._make_record(7, "D", "B", True),
        ]

        result = evaluate_core_metrics(self.episode, trajectory)

        self.assertEqual(
            result,
            CoreMetricResult(
                episode_id="metrics-episode-001",
                pcm=0.75,
                cdl=1,
                pr=1.0,
            ),
        )

    def test_pr_is_not_generic_post_switch_error_rate(self) -> None:
        trajectory = [
            self._make_record(0, "A", "B", True),
            self._make_record(1, "B", "C", True),
            self._make_record(2, "C", "D", True),
            self._make_record(3, "D", "A", True),
            self._make_record(4, "A", "D", False),
            self._make_record(5, "B", "A", False),
            self._make_record(6, "C", "B", False),
            self._make_record(7, "D", "C", False),
        ]

        self.assertEqual(compute_pr(self.episode, trajectory), 0.0)

    def _make_trajectory(self, correctness: list[bool]) -> list[TrajectoryRecord]:
        records: list[TrajectoryRecord] = []
        expected_outputs = ["B", "C", "D", "A", "C", "D", "A", "B"]
        wrong_outputs = ["C", "D", "A", "B", "B", "C", "B", "C"]

        for step_id, is_correct in enumerate(correctness):
            input_symbol = self.episode.input_stream[step_id]
            action = expected_outputs[step_id] if is_correct else wrong_outputs[step_id]
            records.append(self._make_record(step_id, input_symbol, action, is_correct))

        return records

    def _make_record(self, step_id: int, input_symbol: str, action: str, correct: bool) -> TrajectoryRecord:
        return TrajectoryRecord(
            step_id=step_id,
            input_symbol=input_symbol,
            action=action,
            expected_output=action if correct else "",
            correct=correct,
            reward=1.0 if correct else 0.0,
            post_switch=step_id >= self.episode.switch_step,
        )


if __name__ == "__main__":
    unittest.main()