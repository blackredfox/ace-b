from __future__ import annotations

from aceb.agents.base import BaseAgent
from aceb.env.types import Observation, StepResult


class StaticShiftAgent(BaseAgent):
    def __init__(self, alphabet: list[str], required_consistent_inferences: int = 2) -> None:
        if required_consistent_inferences < 1:
            raise ValueError("required_consistent_inferences must be at least 1")

        self.alphabet = alphabet.copy()
        self.required_consistent_inferences = required_consistent_inferences
        self._index_by_symbol = {symbol: index for index, symbol in enumerate(self.alphabet)}
        self._committed_shift: int | None = None
        self._shift_counts: dict[int, int] = {}
        self._has_reset = False

    def reset(self) -> None:
        self._committed_shift = None
        self._shift_counts = {}
        self._has_reset = True

    def act(self, observation: Observation) -> str:
        self._ensure_ready()

        shift = self._committed_shift if self._committed_shift is not None else 1
        return self._apply_shift(observation.input_symbol, shift)

    def observe(self, observation: Observation, action: str, result: StepResult) -> None:
        del action
        self._ensure_ready()

        if self._committed_shift is not None:
            return

        inferred_shift = self._infer_shift(observation.input_symbol, result.expected_output)
        new_count = self._shift_counts.get(inferred_shift, 0) + 1
        self._shift_counts[inferred_shift] = new_count

        if new_count >= self.required_consistent_inferences:
            self._committed_shift = inferred_shift

    def _apply_shift(self, input_symbol: str, shift: int) -> str:
        if input_symbol not in self._index_by_symbol:
            raise ValueError(f"symbol {input_symbol!r} is not in the alphabet")

        current_index = self._index_by_symbol[input_symbol]
        shifted_index = (current_index + shift) % len(self.alphabet)
        return self.alphabet[shifted_index]

    def _infer_shift(self, input_symbol: str, expected_output: str) -> int:
        if input_symbol not in self._index_by_symbol:
            raise ValueError(f"symbol {input_symbol!r} is not in the alphabet")
        if expected_output not in self._index_by_symbol:
            raise ValueError(f"symbol {expected_output!r} is not in the alphabet")

        input_index = self._index_by_symbol[input_symbol]
        output_index = self._index_by_symbol[expected_output]
        return (output_index - input_index) % len(self.alphabet)

    def _ensure_ready(self) -> None:
        if not self._has_reset:
            raise RuntimeError("reset() must be called before using the agent")