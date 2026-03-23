from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BenchmarkConfig:
    alphabet_size: int
    input_length: int
    history_window: int
    seed: int
    switch_ratio_min: float = 0.3
    switch_ratio_max: float = 0.7

    def __post_init__(self) -> None:
        if self.alphabet_size < 3:
            raise ValueError("alphabet_size must be at least 3")
        if self.input_length < 3:
            raise ValueError("input_length must be at least 3")
        if not 0 < self.switch_ratio_min <= self.switch_ratio_max < 1:
            raise ValueError("switch ratios must satisfy 0 < min <= max < 1")
