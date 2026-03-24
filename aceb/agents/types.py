from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AgentFeedback:
    correct: bool
    reward: float
    done: bool
