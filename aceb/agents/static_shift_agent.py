from __future__ import annotations

from aceb.agents.base import BaseAgent
from aceb.agents.types import AgentFeedback
from aceb.env.types import Observation


class StaticShiftAgent(BaseAgent):
    def __init__(self, alphabet: list[str], required_consistent_inferences: int = 2) -> None:
        if required_consistent_inferences < 1:
            raise ValueError("required_consistent_inferences must be at least 1")

        self.alphabet = alphabet.copy()
        self.required_consistent_inferences = required_consistent_inferences
        self._index_by_symbol = {symbol: index for index, symbol in enumerate(self.alphabet)}
        self._candidate_shifts = list(range(1, len(self.alphabet)))
        self._committed_shift: int | None = None
        self._candidate_index = 0
        self._consecutive_success_count = 0
        self._has_reset = False

    def reset(self) -> None:
        self._committed_shift = None
        self._candidate_index = 0
        self._consecutive_success_count = 0
        self._has_reset = True

    def act(self, observation: Observation) -> str:
        self._ensure_ready()

        shift = self._committed_shift if self._committed_shift is not None else self._current_candidate_shift()
        return self._apply_shift(observation.input_symbol, shift)

    def observe(self, observation: Observation, action: str, feedback: AgentFeedback) -> None:
        self._ensure_ready()

        if self._committed_shift is not None:
            return

        attempted_shift = self._infer_shift(observation.input_symbol, action)

        if feedback.correct:
            if attempted_shift != self._current_candidate_shift():
                self._candidate_index = self._candidate_shifts.index(attempted_shift)
                self._consecutive_success_count = 1
            else:
                self._consecutive_success_count += 1
        else:
            self._candidate_index = (self._candidate_shifts.index(attempted_shift) + 1) % len(self._candidate_shifts)
            self._consecutive_success_count = 0

        if self._consecutive_success_count >= self.required_consistent_inferences:
            self._committed_shift = self._current_candidate_shift()

    def _apply_shift(self, input_symbol: str, shift: int) -> str:
        if input_symbol not in self._index_by_symbol:
            raise ValueError(f"symbol {input_symbol!r} is not in the alphabet")

        current_index = self._index_by_symbol[input_symbol]
        shifted_index = (current_index + shift) % len(self.alphabet)
        return self.alphabet[shifted_index]

    def _infer_shift(self, input_symbol: str, output_symbol: str) -> int:
        if input_symbol not in self._index_by_symbol:
            raise ValueError(f"symbol {input_symbol!r} is not in the alphabet")
        if output_symbol not in self._index_by_symbol:
            raise ValueError(f"symbol {output_symbol!r} is not in the alphabet")

        input_index = self._index_by_symbol[input_symbol]
        output_index = self._index_by_symbol[output_symbol]
        return (output_index - input_index) % len(self.alphabet)

    def _current_candidate_shift(self) -> int:
        return self._candidate_shifts[self._candidate_index]

    def _ensure_ready(self) -> None:
        if not self._has_reset:
            raise RuntimeError("reset() must be called before using the agent")