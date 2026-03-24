from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Observation:
    step_id: int
    input_symbol: str
    history: list[dict[str, object]]
    last_feedback: dict[str, object] | None


@dataclass
class StepResult:
    observation: Observation
    expected_output: str
    correct: bool
    reward: float
    done: bool
    post_switch: bool


@dataclass
class TrajectoryRecord:
    step_id: int
    input_symbol: str
    action: str
    expected_output: str
    correct: bool
    reward: float
    post_switch: bool
