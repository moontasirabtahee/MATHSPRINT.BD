"""
Token Bucket Rate Limiter.
Provides stateful request pacing for requests-per-minute (RPM) and tokens-per-minute (TPM).
"""

import time
import asyncio
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger("TokenBucket")

class TokenBucket:
    """Implements a thread-safe / asyncio leaky-token-bucket rate limiter."""

    def __init__(self, capacity: int, refill_rate_per_sec: float):
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.refill_rate = refill_rate_per_sec
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens_needed: float = 1.0) -> None:
        """Asynchronously waits until sufficient tokens are available."""
        while True:
            async with self._lock:
                now = time.monotonic()
                elapsed = now - self.last_update
                self.last_update = now

                # Refill tokens up to maximum capacity
                self.tokens = min(self.capacity, self.tokens + (elapsed * self.refill_rate))

                if self.tokens >= tokens_needed:
                    self.tokens -= tokens_needed
                    return

                # Calculate sleep duration needed to accumulate tokens
                deficit = tokens_needed - self.tokens
                wait_time = deficit / self.refill_rate

            await asyncio.sleep(min(wait_time, 2.0))

