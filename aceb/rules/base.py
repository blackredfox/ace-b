from abc import ABC, abstractmethod


class BaseRule(ABC):
    @abstractmethod
    def apply(self, input_symbol: str) -> str:
        """Transform a single input symbol into an output symbol."""
