import unittest

from aceb.agents.adaptive_shift_agent import AdaptiveShiftAgent
from aceb.agents.random_agent import RandomAgent
from aceb.agents.static_shift_agent import StaticShiftAgent
from aceb.config import BenchmarkConfig
from aceb.env.environment import RCSEnvironment
from aceb.eval.comparison import compare_baseline_agents_on_episodes, summarize_by_agent
from aceb.eval.core_metrics import evaluate_core_metrics
from aceb.generator.builder import build_episode_spec
from aceb.runner.episode_runner import run_episode


class ComparisonHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = BenchmarkConfig(
            alphabet_size=6,
            input_length=20,
            history_window=4,
            seed=24680,
        )
        self.episode_ids = ["comparison-001", "comparison-002", "comparison-003"]

    def test_returns_results_for_all_three_baseline_agents(self) -> None:
        comparison = compare_baseline_agents_on_episodes(self.config, [self.episode_ids[0]])

        self.assertEqual({result.agent_name for result in comparison.results}, {"RandomAgent", "StaticShiftAgent", "AdaptiveShiftAgent"})

    def test_every_agent_is_evaluated_on_every_requested_episode(self) -> None:
        comparison = compare_baseline_agents_on_episodes(self.config, self.episode_ids)

        self.assertEqual(len(comparison.results), len(self.episode_ids) * 3)
        for episode_id in self.episode_ids:
            episode_results = [result for result in comparison.results if result.episode_id == episode_id]
            self.assertEqual(len(episode_results), 3)

    def test_results_are_deterministic_across_repeated_identical_runs(self) -> None:
        first = compare_baseline_agents_on_episodes(self.config, self.episode_ids)
        second = compare_baseline_agents_on_episodes(self.config, self.episode_ids)

        self.assertEqual(first, second)

    def test_helper_uses_same_episode_configuration_as_manual_metric_runs(self) -> None:
        comparison = compare_baseline_agents_on_episodes(self.config, [self.episode_ids[0]])
        episode = build_episode_spec(self.config, self.episode_ids[0])

        manual_results = {}
        for agent_name, agent in [
            ("RandomAgent", RandomAgent(alphabet=episode.alphabet, seed=self._random_seed_for_episode(episode.seed))),
            ("StaticShiftAgent", StaticShiftAgent(alphabet=episode.alphabet)),
            ("AdaptiveShiftAgent", AdaptiveShiftAgent(alphabet=episode.alphabet)),
        ]:
            run_result = run_episode(RCSEnvironment(episode), agent)
            metrics = evaluate_core_metrics(episode, run_result.trajectory)
            manual_results[agent_name] = (metrics.pcm, metrics.cdl, metrics.pr, run_result.accuracy)

        for result in comparison.results:
            self.assertEqual(
                (result.pcm, result.cdl, result.pr, result.accuracy),
                manual_results[result.agent_name],
            )

    def test_random_agent_performs_worse_than_static_agent_pre_change_or_accuracy(self) -> None:
        summary = summarize_by_agent(compare_baseline_agents_on_episodes(self.config, self.episode_ids))

        self.assertTrue(
            summary["StaticShiftAgent"]["pcm"] > summary["RandomAgent"]["pcm"]
            or summary["StaticShiftAgent"]["accuracy"] > summary["RandomAgent"]["accuracy"]
        )

    def test_adaptive_agent_shows_better_recovery_than_static_agent(self) -> None:
        summary = summarize_by_agent(compare_baseline_agents_on_episodes(self.config, self.episode_ids))

        static_cdl = summary["StaticShiftAgent"]["cdl"]
        adaptive_cdl = summary["AdaptiveShiftAgent"]["cdl"]
        static_pr = summary["StaticShiftAgent"]["pr"]
        adaptive_pr = summary["AdaptiveShiftAgent"]["pr"]

        self.assertTrue(
            (static_cdl is None or (adaptive_cdl is not None and adaptive_cdl < static_cdl))
            or adaptive_pr < static_pr
        )

    def test_static_agent_can_have_high_pcm_but_worse_post_switch_metrics_than_adaptive(self) -> None:
        summary = summarize_by_agent(compare_baseline_agents_on_episodes(self.config, self.episode_ids))

        self.assertGreater(summary["StaticShiftAgent"]["pcm"], summary["RandomAgent"]["pcm"])
        self.assertTrue(
            (summary["AdaptiveShiftAgent"]["cdl"] is not None and summary["StaticShiftAgent"]["cdl"] is not None and summary["AdaptiveShiftAgent"]["cdl"] < summary["StaticShiftAgent"]["cdl"])
            or summary["AdaptiveShiftAgent"]["pr"] < summary["StaticShiftAgent"]["pr"]
        )

    def test_none_cdl_values_are_preserved_in_results_and_summary(self) -> None:
        short_config = BenchmarkConfig(
            alphabet_size=5,
            input_length=4,
            history_window=2,
            seed=13579,
        )
        comparison = compare_baseline_agents_on_episodes(short_config, ["short-episode"])
        summary = summarize_by_agent(comparison)

        self.assertTrue(all(result.cdl is None for result in comparison.results))
        self.assertTrue(all(agent_summary["cdl"] is None for agent_summary in summary.values()))

    def _random_seed_for_episode(self, episode_seed: int) -> int:
        from aceb.eval.comparison import _derive_agent_seed

        return _derive_agent_seed(episode_seed, "random")


if __name__ == "__main__":
    unittest.main()