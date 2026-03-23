import unittest

from aceb.env.episode import EpisodeSpec
from aceb.env.types import TrajectoryRecord
from aceb.eval.core_metrics import evaluate_core_metrics
from aceb.rules.ruleset import RuleSet


class AdditionalValidationCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.episode = EpisodeSpec(
            episode_id="additional-validation-episode",
            alphabet=["A", "B", "C", "D"],
            input_stream=["A", "B", "C", "D", "A", "B", "C", "D"],
            shift_pre=1,
            shift_post=2,
            switch_step=4,
            history_window=3,
            seed=1001,
        )

    def test_same_accuracy_can_hide_different_cdl_and_pr(self) -> None:
        recovery_trajectory = self._build_trajectory(["B", "C", "D", "A", "B", "C", "A", "B"])
        lucky_trajectory = self._build_trajectory(["B", "C", "D", "A", "C", "A", "B", "B"])

        recovery_metrics = evaluate_core_metrics(self.episode, recovery_trajectory)
        lucky_metrics = evaluate_core_metrics(self.episode, lucky_trajectory)
        recovery_accuracy = self._accuracy(recovery_trajectory)
        lucky_accuracy = self._accuracy(lucky_trajectory)

        self.assertEqual(recovery_accuracy, lucky_accuracy)
        self.assertNotEqual(recovery_metrics.cdl, lucky_metrics.cdl)
        self.assertNotEqual(recovery_metrics.pr, lucky_metrics.pr)

    def test_same_error_rate_can_produce_different_pr(self) -> None:
        perseverative_trajectory = self._build_trajectory(["B", "C", "D", "A", "B", "C", "A", "B"])
        non_perseverative_trajectory = self._build_trajectory(["B", "C", "D", "A", "D", "A", "A", "B"])

        perseverative_metrics = evaluate_core_metrics(self.episode, perseverative_trajectory)
        non_perseverative_metrics = evaluate_core_metrics(self.episode, non_perseverative_trajectory)

        self.assertEqual(self._post_switch_error_count(perseverative_trajectory), self._post_switch_error_count(non_perseverative_trajectory))
        self.assertGreater(perseverative_metrics.pr, non_perseverative_metrics.pr)

    def test_additional_cases_are_deterministic(self) -> None:
        actions = ["B", "C", "D", "A", "B", "C", "A", "B"]

        first = evaluate_core_metrics(self.episode, self._build_trajectory(actions))
        second = evaluate_core_metrics(self.episode, self._build_trajectory(actions))

        self.assertEqual(first, second)

    def _build_trajectory(self, actions: list[str]) -> list[TrajectoryRecord]:
        rule_set = RuleSet(
            alphabet=self.episode.alphabet,
            shift_pre=self.episode.shift_pre,
            shift_post=self.episode.shift_post,
            switch_step=self.episode.switch_step,
        )

        return [
            TrajectoryRecord(
                step_id=step_id,
                input_symbol=input_symbol,
                action=action,
                expected_output=rule_set.apply(input_symbol, step_id),
                correct=action == rule_set.apply(input_symbol, step_id),
                reward=1.0 if action == rule_set.apply(input_symbol, step_id) else 0.0,
                post_switch=rule_set.is_post_switch(step_id),
            )
            for step_id, (input_symbol, action) in enumerate(zip(self.episode.input_stream, actions))
        ]

    def _accuracy(self, trajectory: list[TrajectoryRecord]) -> float:
        return sum(1 for record in trajectory if record.correct) / len(trajectory)

    def _post_switch_error_count(self, trajectory: list[TrajectoryRecord]) -> int:
        return sum(1 for record in trajectory if record.post_switch and not record.correct)


if __name__ == "__main__":
    unittest.main()