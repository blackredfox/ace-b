import unittest

from aceb.agents.adaptive_shift_agent import AdaptiveShiftAgent
from aceb.agents.static_shift_agent import StaticShiftAgent
from aceb.agents.types import AgentFeedback
from aceb.env.environment import RCSEnvironment
from aceb.env.episode import EpisodeSpec
from aceb.env.types import Observation
from aceb.runner.episode_runner import run_episode


class AdaptiveShiftAgentTests(unittest.TestCase):
    def test_requires_reset_before_use(self) -> None:
        agent = AdaptiveShiftAgent(alphabet=["A", "B", "C", "D"])

        with self.assertRaisesRegex(RuntimeError, r"reset\(\) must be called before using the agent"):
            agent.act(Observation(step_id=0, input_symbol="A", history=[], last_feedback=None))

    def test_commits_after_configured_confirmations(self) -> None:
        agent = AdaptiveShiftAgent(alphabet=["A", "B", "C", "D"], required_consistent_inferences=2)
        agent.reset()

        agent.observe(
            Observation(step_id=0, input_symbol="A", history=[], last_feedback=None),
            "B",
            AgentFeedback(correct=True, reward=1.0, done=False),
        )
        self.assertIsNone(agent._committed_shift)

        agent.observe(
            Observation(step_id=1, input_symbol="C", history=[], last_feedback={"correct": True, "reward": 1.0}),
            "D",
            AgentFeedback(correct=True, reward=1.0, done=False),
        )
        self.assertEqual(agent._committed_shift, 1)

    def test_uses_committed_shift_while_feedback_remains_correct(self) -> None:
        agent = AdaptiveShiftAgent(alphabet=["A", "B", "C", "D"], required_consistent_inferences=2)
        agent.reset()

        agent.observe(Observation(step_id=0, input_symbol="A", history=[], last_feedback=None), "B", AgentFeedback(True, 1.0, False))
        agent.observe(Observation(step_id=1, input_symbol="B", history=[], last_feedback=None), "C", AgentFeedback(True, 1.0, False))
        agent.observe(Observation(step_id=2, input_symbol="C", history=[], last_feedback=None), "D", AgentFeedback(True, 1.0, False))

        self.assertEqual(agent._committed_shift, 1)
        self.assertEqual(agent.act(Observation(step_id=3, input_symbol="D", history=[], last_feedback=None)), "A")

    def test_abandons_committed_shift_after_failure_streak(self) -> None:
        agent = AdaptiveShiftAgent(
            alphabet=["A", "B", "C", "D"],
            required_consistent_inferences=2,
            failure_streak_for_revision=2,
        )
        agent.reset()

        agent.observe(Observation(step_id=0, input_symbol="A", history=[], last_feedback=None), "B", AgentFeedback(True, 1.0, False))
        agent.observe(Observation(step_id=1, input_symbol="B", history=[], last_feedback=None), "C", AgentFeedback(True, 1.0, False))
        self.assertEqual(agent._committed_shift, 1)

        agent.observe(Observation(step_id=2, input_symbol="C", history=[], last_feedback=None), "D", AgentFeedback(False, 0.0, False))
        self.assertEqual(agent._committed_shift, 1)

        agent.observe(Observation(step_id=3, input_symbol="D", history=[], last_feedback=None), "A", AgentFeedback(False, 0.0, False))
        self.assertIsNone(agent._committed_shift)
        self.assertEqual(agent._current_candidate_shift(), 2)

    def test_can_recommit_to_new_shift_after_revision(self) -> None:
        agent = AdaptiveShiftAgent(
            alphabet=["A", "B", "C", "D"],
            required_consistent_inferences=2,
            failure_streak_for_revision=2,
        )
        agent.reset()

        agent.observe(Observation(step_id=0, input_symbol="A", history=[], last_feedback=None), "B", AgentFeedback(True, 1.0, False))
        agent.observe(Observation(step_id=1, input_symbol="B", history=[], last_feedback=None), "C", AgentFeedback(True, 1.0, False))
        agent.observe(Observation(step_id=2, input_symbol="C", history=[], last_feedback=None), "D", AgentFeedback(False, 0.0, False))
        agent.observe(Observation(step_id=3, input_symbol="D", history=[], last_feedback=None), "A", AgentFeedback(False, 0.0, False))

        agent.observe(Observation(step_id=4, input_symbol="A", history=[], last_feedback=None), "C", AgentFeedback(True, 1.0, False))
        self.assertIsNone(agent._committed_shift)
        agent.observe(Observation(step_id=5, input_symbol="B", history=[], last_feedback=None), "D", AgentFeedback(True, 1.0, False))

        self.assertEqual(agent._committed_shift, 2)

    def test_is_deterministic_across_identical_runs(self) -> None:
        first = AdaptiveShiftAgent(alphabet=["A", "B", "C", "D"])
        second = AdaptiveShiftAgent(alphabet=["A", "B", "C", "D"])
        observation = Observation(step_id=0, input_symbol="A", history=[], last_feedback=None)

        first.reset()
        second.reset()
        first_actions = [first.act(observation)]
        second_actions = [second.act(observation)]
        first.observe(observation, first_actions[0], AgentFeedback(True, 1.0, False))
        second.observe(observation, second_actions[0], AgentFeedback(True, 1.0, False))
        first_actions.append(first.act(Observation(step_id=1, input_symbol="B", history=[], last_feedback=None)))
        second_actions.append(second.act(Observation(step_id=1, input_symbol="B", history=[], last_feedback=None)))

        self.assertEqual(first_actions, second_actions)

    def test_revises_and_recovers_better_than_static_agent_after_switch(self) -> None:
        episode = EpisodeSpec(
            episode_id="adaptive-vs-static",
            alphabet=["A", "B", "C", "D"],
            input_stream=["A", "B", "C", "D", "A", "B", "C", "D", "A", "B"],
            shift_pre=1,
            shift_post=2,
            switch_step=4,
            history_window=3,
            seed=11,
        )

        adaptive_result = run_episode(RCSEnvironment(episode), AdaptiveShiftAgent(episode.alphabet, 2, 2))
        static_result = run_episode(RCSEnvironment(episode), StaticShiftAgent(episode.alphabet, 2))

        adaptive_post_switch_correct = sum(1 for record in adaptive_result.trajectory if record.post_switch and record.correct)
        static_post_switch_correct = sum(1 for record in static_result.trajectory if record.post_switch and record.correct)

        self.assertGreater(adaptive_post_switch_correct, static_post_switch_correct)

    def test_works_with_agent_feedback_only(self) -> None:
        agent = AdaptiveShiftAgent(alphabet=["A", "B", "C", "D"])
        agent.reset()

        agent.observe(
            Observation(step_id=0, input_symbol="A", history=[], last_feedback=None),
            "B",
            AgentFeedback(correct=True, reward=1.0, done=False),
        )
        self.assertEqual(agent.act(Observation(step_id=1, input_symbol="B", history=[], last_feedback=None)), "C")


if __name__ == "__main__":
    unittest.main()
