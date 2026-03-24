from __future__ import annotations

from dataclasses import dataclass

from aceb.agents.base import BaseAgent
from aceb.agents.types import AgentFeedback
from aceb.env.environment import RCSEnvironment
from aceb.env.types import TrajectoryRecord


@dataclass
class EpisodeRunResult:
    episode_id: str
    trajectory: list[TrajectoryRecord]
    total_steps: int
    total_correct: int
    accuracy: float


def run_episode(environment: RCSEnvironment, agent: BaseAgent) -> EpisodeRunResult:
    agent.reset()
    observation = environment.reset()

    while True:
        action = agent.act(observation)
        if not isinstance(action, str) or action == "":
            raise ValueError("agent returned an invalid empty action")

        result = environment.step(action)
        agent.observe(
            observation,
            action,
            AgentFeedback(correct=result.correct, reward=result.reward, done=result.done),
        )

        if result.done:
            break

        observation = environment.get_observation()

    trajectory = environment.get_trajectory()
    total_steps = len(trajectory)
    total_correct = sum(1 for record in trajectory if record.correct)
    accuracy = total_correct / total_steps if total_steps else 0.0

    return EpisodeRunResult(
        episode_id=environment.episode.episode_id,
        trajectory=trajectory,
        total_steps=total_steps,
        total_correct=total_correct,
        accuracy=accuracy,
    )
