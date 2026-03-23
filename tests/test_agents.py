import unittest

from aceb.agents.random_agent import RandomAgent
from aceb.agents.static_shift_agent import StaticShiftAgent
from aceb.env.types import Observation, StepResult


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
        first_result = StepResult(
            observation=first_observation,
            expected_output="B",
            correct=True,
            reward=1.0,
            done=False,
            post_switch=False,
        )
        second_observation = Observation(step_id=1, input_symbol="C", history=[], last_feedback={"correct": True, "reward": 1.0})
        second_result = StepResult(
            observation=second_observation,
            expected_output="D",
            correct=True,
            reward=1.0,
            done=False,
            post_switch=False,
        )

        agent.observe(first_observation, "B", first_result)
        agent.observe(second_observation, "D", second_result)

        self.assertEqual(agent.act(Observation(step_id=2, input_symbol="D", history=[], last_feedback=None)), "A")
        self.assertEqual(agent.act(Observation(step_id=3, input_symbol="A", history=[], last_feedback=None)), "B")

    def test_does_not_revise_policy_after_switch_once_committed(self) -> None:
        agent = StaticShiftAgent(alphabet=["A", "B", "C", "D"], required_consistent_inferences=2)
        agent.reset()

        pre_first = Observation(step_id=0, input_symbol="A", history=[], last_feedback=None)
        pre_second = Observation(step_id=1, input_symbol="B", history=[], last_feedback={"correct": True, "reward": 1.0})
        committed_result_one = StepResult(pre_first, "B", True, 1.0, False, False)
        committed_result_two = StepResult(pre_second, "C", True, 1.0, False, False)

        agent.observe(pre_first, "B", committed_result_one)
        agent.observe(pre_second, "C", committed_result_two)

        post_switch_observation = Observation(step_id=2, input_symbol="C", history=[], last_feedback={"correct": True, "reward": 1.0})
        post_switch_result = StepResult(post_switch_observation, "A", False, 0.0, False, True)
        agent.observe(post_switch_observation, "D", post_switch_result)

        self.assertEqual(agent.act(Observation(step_id=3, input_symbol="D", history=[], last_feedback=None)), "A")
