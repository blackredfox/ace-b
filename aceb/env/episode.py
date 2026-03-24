from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EpisodeSpec:
    episode_id: str
    alphabet: list[str]
    input_stream: list[str]
    shift_pre: int
    shift_post: int
    switch_step: int
    history_window: int
    seed: int

    def __post_init__(self) -> None:
        if len(self.alphabet) <= 1:
            raise ValueError("alphabet must contain at least 2 symbols")
        if len(self.input_stream) == 0:
            raise ValueError("input_stream must not be empty")
        if not 0 <= self.switch_step < len(self.input_stream):
            raise ValueError("switch_step must be within the input_stream bounds")
        if self.shift_pre == self.shift_post:
            raise ValueError("shift_pre and shift_post must be different")
