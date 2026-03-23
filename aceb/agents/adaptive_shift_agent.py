from __future__ import annotations

from aceb.agents.base import BaseAgent
from aceb.agents.types import AgentFeedback
from aceb.env.types import Observation


class AdaptiveShiftAgent(BaseAgent):
    def __init__(
        self,
        alphabet: list[str],
        required_consistent_inferences: int = 2,
        failure_streak_for_revision: int = 2,
    ) -> None:
        if required_consistent_inferences < 1:
            raise ValueError("required_consistent_inferences must be at least 1")
        if failure_streak_for_revision < 1:
            raise ValueError("failure_streak_for_revision must be at least 1")

        self.alphabet = alphabet.copy()
        self.required_consistent_inferences = required_consistent_inferences
        self.failure_streak_for_revision = failure_streak_for_revision
        self._index_by_symbol = {symbol: index for index, symbol in enumerate(self.alphabet)}
        self._candidate_shifts = list(range(1, len(self.alphabet)))
        self._committed_shift: int | None = None
        self._candidate_index = 0
        self._consecutive_success_count = 0
        self._failure_streak = 0
        self._has_reset = False

    def reset(self) -> None:
        self._committed_shift = None
        self._candidate_index = 0
        self._consecutive_success_count = 0
        self._failure_streak = 0
        self._has_reset = True

    def act(self, observation: Observation) -> str:
        self._ensure_ready()

        shift = self._committed_shift if self._committed_shift is not None else self._current_candidate_shift()
        return self._apply_shift(observation.input_symbol, shift)

    def observe(self, observation: Observation, action: str, feedback: AgentFeedback) -> None:
        self._ensure_ready()
        attempted_shift = self._infer_shift(observation.input_symbol, action)

        if self._committed_shift is None:
            self._update_search_state(attempted_shift, feedback.correct)
            return

        if feedback.correct:
            self._failure_streak = 0
            return

        self._failure_streak += 1
        if self._failure_streak >= self.failure_streak_for_revision:
            self._committed_shift = None
            self._candidate_index = self._next_candidate_index(self._committed_shift_index(attempted_shift))
            self._consecutive_success_count = 0
            self._failure_streak = 0

    def _update_search_state(self, attempted_shift: int, is_correct: bool) -> None:
        current_shift = self._current_candidate_shift()

        if is_correct:
            if attempted_shift != current_shift:
                self._candidate_index = self._candidate_shifts.index(attempted_shift)
                self._consecutive_success_count = 1
            else:
                self._consecutive_success_count += 1

            if self._consecutive_success_count >= self.required_consistent_inferences:
                self._committed_shift = self._current_candidate_shift()
                self._failure_streak = 0
            return

        self._candidate_index = self._next_candidate_index(self._candidate_shifts.index(attempted_shift))
        self._consecutive_success_count = 0

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

    def _committed_shift_index(self, attempted_shift: int) -> int:
        committed_shift = self._committed_shift if self._committed_shift is not None else attempted_shift
        return self._candidate_shifts.index(committed_shift)

    def _next_candidate_index(self, current_index: int) -> int:
        return (current_index + 1) % len(self._candidate_shifts)

    def _ensure_ready(self) -> None:
        if not self._has_reset:
            raise RuntimeError("reset() must be called before using the agent")