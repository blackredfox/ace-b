from __future__ import annotations

from dataclasses import replace

from aceb.env.episode import EpisodeSpec
from aceb.env.types import Observation, StepResult, TrajectoryRecord
from aceb.rules.ruleset import RuleSet


class RCSEnvironment:
    def __init__(self, episode: EpisodeSpec) -> None:
        self.episode = episode
        self.rule_set = RuleSet(
            alphabet=episode.alphabet,
            shift_pre=episode.shift_pre,
            shift_post=episode.shift_post,
            switch_step=episode.switch_step,
        )
        self._current_step = 0
        self._done = False
        self._last_feedback: dict[str, object] | None = None
        self._trajectory: list[TrajectoryRecord] = []
        self._has_reset = False

    def reset(self) -> Observation:
        self._current_step = 0
        self._done = False
        self._last_feedback = None
        self._trajectory = []
        self._has_reset = True
        return self._build_observation(self._current_step)

    def get_observation(self) -> Observation:
        if not self._has_reset:
            raise RuntimeError("reset() must be called before get_observation()")
        if self._done:
            raise RuntimeError("no current observation is available after the episode is done")

        return self._build_observation(self._current_step)

    def step(self, action: str) -> StepResult:
        if not self._has_reset:
            raise RuntimeError("reset() must be called before step()")
        if self._done:
            raise RuntimeError("step() cannot be called after the episode is done")
        if not 0 <= self._current_step < len(self.episode.input_stream):
            raise RuntimeError("environment is in an invalid step state")

        observation = self._build_observation(self._current_step)
        input_symbol = observation.input_symbol
        expected_output = self.rule_set.apply(input_symbol, observation.step_id)
        correct = action == expected_output
        reward = 1.0 if correct else 0.0
        post_switch = self.rule_set.is_post_switch(observation.step_id)

        record = TrajectoryRecord(
            step_id=observation.step_id,
            input_symbol=input_symbol,
            action=action,
            expected_output=expected_output,
            correct=correct,
            reward=reward,
            post_switch=post_switch,
        )
        self._trajectory.append(record)
        self._last_feedback = {"correct": correct, "reward": reward}

        self._current_step += 1
        self._done = self._current_step >= len(self.episode.input_stream)

        return StepResult(
            observation=observation,
            expected_output=expected_output,
            correct=correct,
            reward=reward,
            done=self._done,
            post_switch=post_switch,
        )

    def get_trajectory(self) -> list[TrajectoryRecord]:
        return [replace(record) for record in self._trajectory]

    def _build_observation(self, step_id: int) -> Observation:
        if not 0 <= step_id < len(self.episode.input_stream):
            raise RuntimeError("environment is in an invalid step state")

        history_window = self.episode.history_window
        history_records = self._trajectory[-history_window:] if history_window > 0 else []
        history = [
            {
                "step_id": record.step_id,
                "input_symbol": record.input_symbol,
                "action": record.action,
                "expected_output": record.expected_output,
                "correct": record.correct,
            }
            for record in history_records
        ]

        last_feedback = None if self._last_feedback is None else dict(self._last_feedback)

        return Observation(
            step_id=step_id,
            input_symbol=self.episode.input_stream[step_id],
            history=history,
            last_feedback=last_feedback,
        )

