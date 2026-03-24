import unittest

from aceb.rules.ruleset import RuleSet


class RuleSetTests(unittest.TestCase):
    def test_uses_pre_change_rule_before_switch(self) -> None:
        ruleset = RuleSet(alphabet=["A", "B", "C", "D"], shift_pre=1, shift_post=2, switch_step=3)

        self.assertEqual(ruleset.apply("A", step_id=0), "B")
        self.assertFalse(ruleset.is_post_switch(2))

    def test_uses_post_change_rule_after_switch(self) -> None:
        ruleset = RuleSet(alphabet=["A", "B", "C", "D"], shift_pre=1, shift_post=2, switch_step=3)

        self.assertEqual(ruleset.apply("A", step_id=4), "C")
        self.assertTrue(ruleset.is_post_switch(4))

    def test_boundary_step_uses_post_change_rule(self) -> None:
        ruleset = RuleSet(alphabet=["A", "B", "C", "D"], shift_pre=1, shift_post=2, switch_step=3)

        self.assertTrue(ruleset.is_post_switch(3))
        self.assertEqual(ruleset.apply("D", step_id=3), "B")

    def test_multiple_calls_are_consistent(self) -> None:
        ruleset = RuleSet(alphabet=["A", "B", "C", "D"], shift_pre=1, shift_post=2, switch_step=2)

        first = ruleset.apply("B", step_id=1)
        second = ruleset.apply("B", step_id=1)
        third = ruleset.apply("B", step_id=3)
        fourth = ruleset.apply("B", step_id=3)

        self.assertEqual(first, second)
        self.assertEqual(third, fourth)
        self.assertEqual(first, "C")
        self.assertEqual(third, "D")

    def test_negative_step_id_raises_error(self) -> None:
        ruleset = RuleSet(alphabet=["A", "B", "C", "D"], shift_pre=1, shift_post=2, switch_step=3)

        with self.assertRaisesRegex(ValueError, "step_id must be non-negative"):
            ruleset.is_post_switch(-1)

        with self.assertRaisesRegex(ValueError, "step_id must be non-negative"):
            ruleset.apply("A", step_id=-1)


if __name__ == "__main__":
    unittest.main()