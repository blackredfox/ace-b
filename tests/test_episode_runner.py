import unittest

from aceb.agents.random_agent import RandomAgent
from aceb.agents.static_shift_agent import StaticShiftAgent
from aceb.config import BenchmarkConfig
from aceb.env.environment import RCSEnvironment
from aceb.generator.builder import build_episode_spec
from aceb.runner.episode_runner import run_episode


class EpisodeRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = BenchmarkConfig(
            alphabet_size=5,
            input_length=12,
            history_window=3,
            seed=54321,
        )
        self.episode = build_episode_spec(self.config, episode_id="episode-runner-001")

    def test_runner_completes_episode_end_to_end(self) -> None:
        environment = RCSEnvironment(self.episode)
        agent = RandomAgent(alphabet=self.episode.alphabet, seed=99)

        result = run_episode(environment, agent)

        self.assertEqual(result.episode_id, self.episode.episode_id)
        self.assertEqual(result.total_steps, len(self.episode.input_stream))

    def test_returned_trajectory_length_matches_episode_length(self) -> None:
        environment = RCSEnvironment(self.episode)
        agent = RandomAgent(alphabet=self.episode.alphabet, seed=99)

        result = run_episode(environment, agent)

        self.assertEqual(len(result.trajectory), len(self.episode.input_stream))

    def test_summary_statistics_are_computed_correctly(self) -> None:
        environment = RCSEnvironment(self.episode)
        agent = RandomAgent(alphabet=self.episode.alphabet, seed=99)

        result = run_episode(environment, agent)

        expected_correct = sum(1 for record in result.trajectory if record.correct)
        expected_accuracy = expected_correct / len(result.trajectory)
        self.assertEqual(result.total_correct, expected_correct)
        self.assertEqual(result.accuracy, expected_accuracy)

    def test_runner_works_with_random_and_static_agents(self) -> None:
        random_result = run_episode(
            RCSEnvironment(self.episode),
            RandomAgent(alphabet=self.episode.alphabet, seed=99),
        )
        static_result = run_episode(
            RCSEnvironment(self.episode),
            StaticShiftAgent(alphabet=self.episode.alphabet, required_consistent_inferences=2),
        )

        self.assertEqual(random_result.total_steps, len(self.episode.input_stream))
        self.assertEqual(static_result.total_steps, len(self.episode.input_stream))

    def test_repeated_runs_with_same_seeds_are_deterministic(self) -> None:
        first = run_episode(
            RCSEnvironment(self.episode),
            RandomAgent(alphabet=self.episode.alphabet, seed=99),
        )
        second = run_episode(
            RCSEnvironment(self.episode),
            RandomAgent(alphabet=self.episode.alphabet, seed=99),
        )

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()