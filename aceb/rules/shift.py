from __future__ import annotations

from .base import BaseRule


class ShiftRule(BaseRule):
    def __init__(self, alphabet: list[str], shift: int) -> None:
        if not alphabet:
            raise ValueError("alphabet must not be empty")
        if len(set(alphabet)) != len(alphabet):
            raise ValueError("alphabet must contain unique symbols")

        self.alphabet = alphabet.copy()
        self.shift = shift
        self._index_by_symbol = {symbol: index for index, symbol in enumerate(self.alphabet)}

    def apply(self, input_symbol: str) -> str:
        if input_symbol not in self._index_by_symbol:
            raise ValueError(f"symbol {input_symbol!r} is not in the alphabet")

        current_index = self._index_by_symbol[input_symbol]
        shifted_index = (current_index + self.shift) % len(self.alphabet)
        return self.alphabet[shifted_index]