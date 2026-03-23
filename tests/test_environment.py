import unittest

from aceb.env.environment import RCSEnvironment
from aceb.env.episode import EpisodeSpec
from aceb.rules.ruleset import RuleSet


class RCSEnvironmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.episode = EpisodeSpec(
            episode_id="episode-env-001",
            alphabet=["A", "B", "C"],
            input_stream=["A", "B", "C", "A"],
            shift_pre=1,
            shift_post=2,
            switch_step=2,
            history_window=2,
            seed=99,
        )
        self.environment = RCSEnvironment(self.episode)

    def test_reset_returns_initial_observation(self) -> None:
        observation = self.environment.reset()

        self.assertEqual(observation.step_id, 0)
        self.assertEqual(observation.input_symbol, "A")
        self.assertEqual(observation.history, [])
        self.assertIsNone(observation.last_feedback)

    def test_step_before_reset_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(RuntimeError, r"reset\(\) must be called before step\(\)"):
            self.environment.step("B")

    def test_step_evaluates_correctly_before_switch(self) -> None:
        self.environment.reset()

        result = self.environment.step("B")

        self.assertEqual(result.observation.step_id, 0)
        self.assertEqual(result.expected_output, "B")
        self.assertTrue(result.correct)
        self.assertFalse(result.post_switch)
        self.assertFalse(result.done)

    def test_step_evaluates_correctly_after_switch(self) -> None:
        self.environment.reset()
        self.environment.step("B")
        self.environment.step("C")

        result = self.environment.step("B")

        self.assertEqual(result.observation.step_id, 2)
        self.assertEqual(result.expected_output, "B")
        self.assertTrue(result.correct)
        self.assertTrue(result.post_switch)

    def test_reward_is_one_for_correct_and_zero_for_incorrect(self) -> None:
        self.environment.reset()

        correct_result = self.environment.step("B")
        incorrect_result = self.environment.step("A")

        self.assertEqual(correct_result.reward, 1.0)
        self.assertEqual(incorrect_result.reward, 0.0)
        self.assertFalse(incorrect_result.correct)

    def test_trajectory_records_are_appended_correctly(self) -> None:
        self.environment.reset()
        self.environment.step("B")
        self.environment.step("A")

        trajectory = self.environment.get_trajectory()

        self.assertEqual(len(trajectory), 2)
        self.assertEqual(trajectory[0].step_id, 0)
        self.assertEqual(trajectory[0].action, "B")
        self.assertEqual(trajectory[1].step_id, 1)
        self.assertEqual(trajectory[1].action, "A")

    def test_history_is_bounded_by_history_window(self) -> None:
        self.environment.reset()
        self.environment.step("B")
        self.environment.step("C")
        self.environment.step("B")

        final_result = self.environment.step("C")
        history = final_result.observation.history

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["step_id"], 1)
        self.assertEqual(history[1]["step_id"], 2)

    def test_done_becomes_true_after_last_step(self) -> None:
        self.environment.reset()

        self.environment.step("B")
        self.environment.step("C")
        self.environment.step("B")
        final_result = self.environment.step("C")

        self.assertTrue(final_result.done)

    def test_step_after_done_raises_clear_error(self) -> None:
        self.environment.reset()
        self.environment.step("B")
        self.environment.step("C")
        self.environment.step("B")
        self.environment.step("C")

        with self.assertRaisesRegex(RuntimeError, "cannot be called after the episode is done"):
            self.environment.step("A")

    def test_get_trajectory_returns_copy_without_exposing_internal_list(self) -> None:
        self.environment.reset()
        self.environment.step("B")

        external_trajectory = self.environment.get_trajectory()
        external_trajectory.append(external_trajectory[0])

        self.assertEqual(len(self.environment.get_trajectory()), 1)

    def test_switch_behavior_matches_ruleset_exactly(self) -> None:
        ruleset = RuleSet(
            alphabet=self.episode.alphabet,
            shift_pre=self.episode.shift_pre,
            shift_post=self.episode.shift_post,
            switch_step=self.episode.switch_step,
        )
        self.environment.reset()

        for step_id, input_symbol in enumerate(self.episode.input_stream):
            expected_output = ruleset.apply(input_symbol, step_id)
            result = self.environment.step(expected_output)

            self.assertEqual(result.expected_output, expected_output)
            self.assertEqual(result.post_switch, ruleset.is_post_switch(step_id))


if __name__ == "__main__":
    unittest.main()