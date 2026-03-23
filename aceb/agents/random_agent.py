from __future__ import annotations

import random

from aceb.agents.base import BaseAgent
from aceb.env.types import Observation, StepResult


class RandomAgent(BaseAgent):
    def __init__(self, alphabet: list[str], seed: int) -> None:
        self.alphabet = alphabet.copy()
        self.seed = seed
        self._rng: random.Random | None = None

    def reset(self) -> None:
        self._rng = random.Random(self.seed)

    def act(self, observation: Observation) -> str:
        del observation

        if self._rng is None:
            raise RuntimeError("reset() must be called before act()")

        return self._rng.choice(self.alphabet)

    def observe(self, observation: Observation, action: str, result: StepResult) -> None:
        del observation, action, result
