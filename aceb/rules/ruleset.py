from __future__ import annotations

from .shift import ShiftRule


class RuleSet:
    def __init__(
        self,
        alphabet: list[str],
        shift_pre: int,
        shift_post: int,
        switch_step: int,
    ) -> None:
        if shift_pre == shift_post:
            raise ValueError("shift_pre and shift_post must be different")

        self.switch_step = switch_step
        self.pre_rule = ShiftRule(alphabet=alphabet, shift=shift_pre)
        self.post_rule = ShiftRule(alphabet=alphabet, shift=shift_post)

    def apply(self, input_symbol: str, step_id: int) -> str:
        rule = self.post_rule if self.is_post_switch(step_id) else self.pre_rule
        return rule.apply(input_symbol)

    def is_post_switch(self, step_id: int) -> bool:
        if step_id < 0:
            raise ValueError("step_id must be non-negative")

        return step_id >= self.switch_step
