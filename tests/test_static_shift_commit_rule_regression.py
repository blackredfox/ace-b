import unittest

from aceb.agents.static_shift_agent import StaticShiftAgent
from aceb.env.types import Observation, StepResult


class StaticShiftCommitRuleRegressionTests(unittest.TestCase):
    def test_does_not_commit_on_non_consecutive_same_shift_inferences(self) -> None:
        """Commit requires two consistent inferences, so mixed inferences should not commit."""
        agent = StaticShiftAgent(alphabet=["A", "B", "C", "D"], required_consistent_inferences=2)
        agent.reset()

        # infer shift=2
        obs0 = Observation(step_id=0, input_symbol="A", history=[], last_feedback=None)
        res0 = StepResult(obs0, "C", True, 1.0, False, False)
        agent.observe(obs0, "C", res0)

        # infer shift=1 (breaks consistency)
        obs1 = Observation(step_id=1, input_symbol="A", history=[], last_feedback={"correct": True, "reward": 1.0})
        res1 = StepResult(obs1, "B", False, 0.0, False, False)
        agent.observe(obs1, "B", res1)

        # infer shift=2 again (same as first, but not consecutive)
        obs2 = Observation(step_id=2, input_symbol="B", history=[], last_feedback={"correct": False, "reward": 0.0})
        res2 = StepResult(obs2, "D", True, 1.0, False, False)
        agent.observe(obs2, "D", res2)

        # If no commit happened yet, default policy is shift=1: D -> A.
        # If agent committed too early to shift=2, output would be D -> B.
        action = agent.act(Observation(step_id=3, input_symbol="D", history=[], last_feedback=None))
        self.assertEqual(action, "A")


if __name__ == "__main__":
    unittest.main()
