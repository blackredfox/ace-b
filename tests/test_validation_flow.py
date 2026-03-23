import unittest

from aceb.config import BenchmarkConfig
from aceb.validation.run_validation import run_validation, run_validation_with_summary, validate_behavioral_separation
from aceb.validation.validation_set import VALIDATION_EPISODE_IDS, get_validation_episode_ids


class ValidationFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = BenchmarkConfig(
            alphabet_size=6,
            input_length=20,
            history_window=4,
            seed=24680,
        )

    def test_validation_runs_without_errors(self) -> None:
        comparison = run_validation(self.config)

        self.assertEqual(comparison.episodes, VALIDATION_EPISODE_IDS)
        self.assertEqual(len(comparison.results), len(VALIDATION_EPISODE_IDS) * 3)

    def test_validation_with_summary_returns_comparison_and_summary(self) -> None:
        result = run_validation_with_summary(self.config)

        self.assertIn("comparison", result)
        self.assertIn("summary", result)
        self.assertEqual(set(result["summary"].keys()), {"RandomAgent", "StaticShiftAgent", "AdaptiveShiftAgent"})

    def test_repeated_validation_runs_are_identical(self) -> None:
        first = run_validation_with_summary(self.config)
        second = run_validation_with_summary(self.config)

        self.assertEqual(first, second)

    def test_random_agent_pcm_is_lower_than_static_agent_pcm(self) -> None:
        summary = run_validation_with_summary(self.config)["summary"]

        self.assertLess(summary["RandomAgent"]["pcm"], summary["StaticShiftAgent"]["pcm"])

    def test_adaptive_cdl_is_less_than_or_equal_to_static_cdl_when_present(self) -> None:
        summary = run_validation_with_summary(self.config)["summary"]

        self.assertIsNotNone(summary["AdaptiveShiftAgent"]["cdl"])
        static_cdl = summary["StaticShiftAgent"]["cdl"]
        adaptive_cdl = summary["AdaptiveShiftAgent"]["cdl"]

        self.assertTrue(static_cdl is None or adaptive_cdl <= static_cdl)

    def test_adaptive_pr_is_less_than_or_equal_to_static_pr(self) -> None:
        summary = run_validation_with_summary(self.config)["summary"]

        self.assertLessEqual(summary["AdaptiveShiftAgent"]["pr"], summary["StaticShiftAgent"]["pr"])

    def test_behavioral_separation_helper_returns_expected_boolean_flags(self) -> None:
        summary = run_validation_with_summary(self.config)["summary"]
        diagnostics = validate_behavioral_separation(summary)

        self.assertEqual(
            diagnostics,
            {
                "random_vs_static_pcm": True,
                "adaptive_vs_static_cdl": True,
                "adaptive_vs_static_pr": True,
            },
        )

    def test_validation_episode_ids_helper_returns_copy(self) -> None:
        episode_ids = get_validation_episode_ids()
        episode_ids.append("extra")

        self.assertEqual(VALIDATION_EPISODE_IDS, ["episode_1", "episode_2", "episode_3", "episode_4", "episode_5"])


if __name__ == "__main__":
    unittest.main()