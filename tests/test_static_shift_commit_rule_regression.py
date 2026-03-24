import unittest

from aceb.agents.static_shift_agent import StaticShiftAgent
from aceb.agents.types import AgentFeedback
from aceb.env.types import Observation


class StaticShiftCommitRuleRegressionTests(unittest.TestCase):
    def test_does_not_commit_on_non_consecutive_same_shift_inferences(self) -> None:
        """Commit requires two consistent inferences, so mixed inferences should not commit."""
        agent = StaticShiftAgent(alphabet=["A", "B", "C", "D"], required_consistent_inferences=2)
        agent.reset()

        agent.observe(
            Observation(step_id=0, input_symbol="A", history=[], last_feedback=None),
            "C",
            AgentFeedback(correct=True, reward=1.0, done=False),
        )

        agent.observe(
            Observation(step_id=1, input_symbol="A", history=[], last_feedback={"correct": True, "reward": 1.0}),
            "B",
            AgentFeedback(correct=False, reward=0.0, done=False),
        )

        agent.observe(
            Observation(step_id=2, input_symbol="B", history=[], last_feedback={"correct": False, "reward": 0.0}),
            "D",
            AgentFeedback(correct=True, reward=1.0, done=False),
        )

        self.assertIsNone(agent._committed_shift)


if __name__ == "__main__":
    unittest.main()
