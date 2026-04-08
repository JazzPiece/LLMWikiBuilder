"""
llm/base.py — Abstract LLM backend interface.

All backends return LLMResponse and implement the same two methods.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    cached: bool = False


class LLMBackend(ABC):
    @abstractmethod
    def complete(self, system: str, user: str, max_tokens: int = 2048) -> LLMResponse:
        """Send a completion request. Returns LLMResponse."""
        ...

    @abstractmethod
    def estimate_cost_usd(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD for a call with the given token counts."""
        ...


class CostGuardError(RuntimeError):
    """Raised when the per-run cost budget is exceeded."""
