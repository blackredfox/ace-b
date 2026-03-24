import unittest

from aceb.rules.shift import ShiftRule


class ShiftRuleTests(unittest.TestCase):
    def test_basic_shift(self) -> None:
        rule = ShiftRule(alphabet=["A", "B", "C", "D"], shift=1)

        self.assertEqual(rule.apply("A"), "B")
        self.assertEqual(rule.apply("B"), "C")

    def test_wrap_around(self) -> None:
        rule = ShiftRule(alphabet=["A", "B", "C", "D"], shift=1)

        self.assertEqual(rule.apply("D"), "A")

    def test_invalid_symbol_raises_clear_error(self) -> None:
        rule = ShiftRule(alphabet=["A", "B", "C", "D"], shift=1)

        with self.assertRaisesRegex(ValueError, "is not in the alphabet"):
            rule.apply("Z")

    def test_negative_shift(self) -> None:
        rule = ShiftRule(alphabet=["A", "B", "C", "D"], shift=-1)

        self.assertEqual(rule.apply("A"), "D")
        self.assertEqual(rule.apply("C"), "B")


if __name__ == "__main__":
    unittest.main()