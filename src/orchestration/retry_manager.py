"""
Retry Manager.
Implements exponential backoff with full jitter for robust handling of transient
network anomalies, HTTP 429 rate limits, and 503 server errors.
"""

import random
import asyncio
from typing import Callable, Any, TypeVar, Coroutine
from src.utils.logger import get_logger

logger = get_logger("RetryManager")

T = TypeVar("T")

class RetryManager:
    """Provides retry execution wrapper with full jitter backoff."""

    def __init__(self, max_retries: int = 7, base_delay: float = 4.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def execute_with_retry(
        self,
        func: Callable[[], Coroutine[Any, Any, T]],
        operation_name: str = "API Request"
    ) -> T:
        """Executes async func with exponential backoff and jitter."""
        for attempt in range(1, self.max_retries + 1):
            try:
                return await func()
            except Exception as e:
                err_str = str(e)
                # If error is a permanent 403 or 401, re-raise immediately without retry
                if "403" in err_str or "PERMISSION_DENIED" in err_str or "401" in err_str:
                    logger.error(f"{operation_name} permanent auth error: {e}")
                    raise

                if attempt == self.max_retries:
                    logger.error(f"{operation_name} failed after {attempt} attempts: {e}")
                    raise

                # Full jitter calculation
                backoff_limit = min(self.max_delay, self.base_delay * (2 ** (attempt - 1)))
                jittered_delay = random.uniform(self.base_delay, backoff_limit)

                logger.warning(
                    f"{operation_name} encountered error ({e}). "
                    f"Retrying attempt {attempt + 1}/{self.max_retries} in {jittered_delay:.2f}s..."
                )
                await asyncio.sleep(jittered_delay)

        raise RuntimeError(f"{operation_name} exceeded max retries")

