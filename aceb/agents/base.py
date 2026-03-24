from __future__ import annotations

from abc import ABC, abstractmethod

from aceb.agents.types import AgentFeedback
from aceb.env.types import Observation


class BaseAgent(ABC):
    @abstractmethod
    def reset(self) -> None:
        """Prepare the agent for a new episode."""

    @abstractmethod
    def act(self, observation: Observation) -> str:
        """Choose an action for the current observation."""

    @abstractmethod
    def observe(self, observation: Observation, action: str, feedback: AgentFeedback) -> None:
        """Update internal state after a step result."""
