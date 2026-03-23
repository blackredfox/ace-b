from __future__ import annotations

from abc import ABC, abstractmethod

from aceb.env.types import Observation, StepResult


class BaseAgent(ABC):
    @abstractmethod
    def reset(self) -> None:
        """Prepare the agent for a new episode."""

    @abstractmethod
    def act(self, observation: Observation) -> str:
        """Choose an action for the current observation."""

    @abstractmethod
    def observe(self, observation: Observation, action: str, result: StepResult) -> None:
        """Update internal state after a step result."""
