import unittest

from aceb.config import BenchmarkConfig
from aceb.env.episode import EpisodeSpec
from aceb.generator.builder import build_episode_spec


class EpisodeBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = BenchmarkConfig(
            alphabet_size=5,
            input_length=20,
            history_window=4,
            seed=12345,
        )

    def test_builds_valid_episode_spec(self) -> None:
        spec = build_episode_spec(self.config, episode_id="episode-001")

        self.assertIsInstance(spec, EpisodeSpec)
        self.assertEqual(spec.episode_id, "episode-001")
        self.assertEqual(spec.history_window, self.config.history_window)

    def test_switch_step_is_within_required_bounds(self) -> None:
        spec = build_episode_spec(self.config, episode_id="episode-002")

        self.assertGreaterEqual(spec.switch_step, 6)
        self.assertLessEqual(spec.switch_step, 14)
        self.assertGreater(spec.switch_step, 0)
        self.assertLess(spec.switch_step, self.config.input_length - 1)

    def test_shifts_are_non_zero_distinct_and_not_modulo_equivalent(self) -> None:
        spec = build_episode_spec(self.config, episode_id="episode-003")

        self.assertNotEqual(spec.shift_pre, 0)
        self.assertNotEqual(spec.shift_post, 0)
        self.assertNotEqual(spec.shift_pre, spec.shift_post)
        self.assertNotEqual(spec.shift_pre % len(spec.alphabet), spec.shift_post % len(spec.alphabet))

    def test_input_stream_uses_only_alphabet_symbols(self) -> None:
        spec = build_episode_spec(self.config, episode_id="episode-004")

        self.assertTrue(all(symbol in spec.alphabet for symbol in spec.input_stream))

    def test_input_stream_is_not_constant(self) -> None:
        spec = build_episode_spec(self.config, episode_id="episode-005")

        self.assertGreaterEqual(len(set(spec.input_stream)), 2)

    def test_generation_is_deterministic_for_same_config_and_seed(self) -> None:
        first = build_episode_spec(self.config, episode_id="episode-006")
        second = build_episode_spec(self.config, episode_id="episode-006")

        self.assertEqual(first, second)

    def test_alphabet_is_unique_and_matches_requested_size(self) -> None:
        spec = build_episode_spec(self.config, episode_id="episode-007")

        self.assertEqual(len(spec.alphabet), self.config.alphabet_size)
        self.assertEqual(len(set(spec.alphabet)), self.config.alphabet_size)

    def test_episode_id_changes_episode_seed_deterministically(self) -> None:
        first = build_episode_spec(self.config, episode_id="episode-008a")
        second = build_episode_spec(self.config, episode_id="episode-008b")

        self.assertNotEqual(first.seed, second.seed)

    def test_switch_step_respects_custom_ratio_band(self) -> None:
        strict_config = BenchmarkConfig(
            alphabet_size=5,
            input_length=10,
            history_window=4,
            seed=12345,
            switch_ratio_min=0.4,
            switch_ratio_max=0.4,
        )

        spec = build_episode_spec(strict_config, episode_id="episode-009")

        self.assertEqual(spec.switch_step, 4)
        self.assertGreater(spec.switch_step, 0)
        self.assertLess(spec.switch_step, strict_config.input_length - 1)


if __name__ == "__main__":
    unittest.main()