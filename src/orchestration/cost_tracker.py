"""
Cost and Token Accounting Tracker.
Tracks cumulative input/output token usage and calculates estimated USD costs.
"""

from typing import Dict, Any
from pydantic import BaseModel

class CostTracker:
    """Tracks token consumption and computes costs based on Google AI Studio pricing."""

    # Gemini 3.5 Flash pricing (approx $0.075 per 1M input tokens, $0.30 per 1M output tokens)
    INPUT_COST_PER_M = 0.075
    OUTPUT_COST_PER_M = 0.30

    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0

    def add_usage(self, input_tokens: int, output_tokens: int) -> float:
        """Records token usage and returns cost for this request in USD."""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_requests += 1

        cost = (
            (input_tokens / 1_000_000.0) * self.INPUT_COST_PER_M +
            (output_tokens / 1_000_000.0) * self.OUTPUT_COST_PER_M
        )
        return round(cost, 6)

    @property
    def total_cost_usd(self) -> float:
        cost = (
            (self.total_input_tokens / 1_000_000.0) * self.INPUT_COST_PER_M +
            (self.total_output_tokens / 1_000_000.0) * self.OUTPUT_COST_PER_M
        )
        return round(cost, 4)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "estimated_cost_usd": self.total_cost_usd
        }

