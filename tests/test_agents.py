import unittest

from aceb.agents.random_agent import RandomAgent
from aceb.agents.static_shift_agent import StaticShiftAgent
from aceb.agents.types import AgentFeedback
from aceb.env.types import Observation


class RandomAgentTests(unittest.TestCase):
    def test_returns_only_symbols_from_alphabet(self) -> None:
        agent = RandomAgent(alphabet=["A", "B", "C"], seed=7)
        observation = Observation(step_id=0, input_symbol="A", history=[], last_feedback=None)

        agent.reset()
        actions = [agent.act(observation) for _ in range(10)]

        self.assertTrue(all(action in ["A", "B", "C"] for action in actions))

    def test_is_deterministic_with_seed(self) -> None:
        first = RandomAgent(alphabet=["A", "B", "C"], seed=7)
        second = RandomAgent(alphabet=["A", "B", "C"], seed=7)
        observation = Observation(step_id=0, input_symbol="A", history=[], last_feedback=None)

        first.reset()
        second.reset()
        first_actions = [first.act(observation) for _ in range(5)]
        second_actions = [second.act(observation) for _ in range(5)]

        self.assertEqual(first_actions, second_actions)


class StaticShiftAgentTests(unittest.TestCase):
    def test_produces_stable_behavior_after_committing(self) -> None:
        agent = StaticShiftAgent(alphabet=["A", "B", "C", "D"], required_consistent_inferences=2)
        agent.reset()

        first_observation = Observation(step_id=0, input_symbol="A", history=[], last_feedback=None)
        second_observation = Observation(step_id=1, input_symbol="C", history=[], last_feedback={"correct": True, "reward": 1.0})

        agent.observe(first_observation, "B", AgentFeedback(correct=True, reward=1.0, done=False))
        agent.observe(second_observation, "D", AgentFeedback(correct=True, reward=1.0, done=False))

        self.assertEqual(agent.act(Observation(step_id=2, input_symbol="D", history=[], last_feedback=None)), "A")
        self.assertEqual(agent.act(Observation(step_id=3, input_symbol="A", history=[], last_feedback=None)), "B")

    def test_does_not_revise_policy_after_switch_once_committed(self) -> None:
        agent = StaticShiftAgent(alphabet=["A", "B", "C", "D"], required_consistent_inferences=2)
        agent.reset()

        pre_first = Observation(step_id=0, input_symbol="A", history=[], last_feedback=None)
        pre_second = Observation(step_id=1, input_symbol="B", history=[], last_feedback={"correct": True, "reward": 1.0})

        agent.observe(pre_first, "B", AgentFeedback(correct=True, reward=1.0, done=False))
        agent.observe(pre_second, "C", AgentFeedback(correct=True, reward=1.0, done=False))

        post_switch_observation = Observation(step_id=2, input_symbol="C", history=[], last_feedback={"correct": True, "reward": 1.0})
        agent.observe(post_switch_observation, "D", AgentFeedback(correct=False, reward=0.0, done=False))

        self.assertEqual(agent.act(Observation(step_id=3, input_symbol="D", history=[], last_feedback=None)), "A")

    def test_uses_only_action_and_correct_feedback_to_commit(self) -> None:
        agent = StaticShiftAgent(alphabet=["A", "B", "C", "D"], required_consistent_inferences=2)
        agent.reset()

        agent.observe(
            Observation(step_id=0, input_symbol="A", history=[], last_feedback=None),
            "B",
            AgentFeedback(correct=True, reward=1.0, done=False),
        )
        agent.observe(
            Observation(step_id=1, input_symbol="C", history=[], last_feedback={"correct": True, "reward": 1.0}),
            "D",
            AgentFeedback(correct=True, reward=1.0, done=False),
        )

        self.assertEqual(agent.act(Observation(step_id=2, input_symbol="A", history=[], last_feedback=None)), "B")
