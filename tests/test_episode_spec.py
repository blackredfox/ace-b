import unittest

from aceb.env.episode import EpisodeSpec


class EpisodeSpecTests(unittest.TestCase):
    def test_valid_creation(self) -> None:
        spec = EpisodeSpec(
            episode_id="episode-001",
            alphabet=["A", "B", "C"],
            input_stream=["A", "B", "C", "A"],
            shift_pre=1,
            shift_post=2,
            switch_step=2,
            history_window=3,
            seed=42,
        )

        self.assertEqual(spec.episode_id, "episode-001")
        self.assertEqual(spec.alphabet, ["A", "B", "C"])
        self.assertEqual(spec.input_stream, ["A", "B", "C", "A"])
        self.assertEqual(spec.shift_pre, 1)
        self.assertEqual(spec.shift_post, 2)
        self.assertEqual(spec.switch_step, 2)
        self.assertEqual(spec.history_window, 3)
        self.assertEqual(spec.seed, 42)

    def test_invalid_switch_step_raises_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "switch_step must be within the input_stream bounds"):
            EpisodeSpec(
                episode_id="episode-002",
                alphabet=["A", "B", "C"],
                input_stream=["A", "B", "C"],
                shift_pre=1,
                shift_post=2,
                switch_step=3,
                history_window=2,
                seed=7,
            )


if __name__ == "__main__":
    unittest.main()