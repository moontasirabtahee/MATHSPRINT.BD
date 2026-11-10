"""
Credential and Quota Key Manager.
Manages Google AI Studio credentials across independent project scopes,
tracking rate limits, in-flight calls, cooldowns, and quota exhaustion.
"""

import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from src.orchestration.token_bucket import TokenBucket
from src.utils.logger import get_logger

logger = get_logger("KeyManager")

class CredentialState(BaseModel):
    alias: str
    key: str
    project_name: str
    project_number: str
    rpm_limit: int = 15
    tpm_limit: int = 1000000
    rpd_limit: int = 1500
    status: str = "IDLE"  # IDLE, ACTIVE, COOLDOWN, EXHAUSTED, DISABLED
    cooldown_until: float = 0.0
    consecutive_errors: int = 0
    total_calls: int = 0
    total_tokens: int = 0

class KeyManager:
    """Orchestrates independent API credentials with project-aware rate-limiting."""

    def __init__(self, config_path: Path = Path("config/keys.json")):
        self.config_path = config_path
        self.credentials: Dict[str, CredentialState] = {}
        self.buckets: Dict[str, TokenBucket] = {}
        self._lock = asyncio.Lock()
        self._load_keys()

    def _load_keys(self) -> None:
        """Loads API credentials from config/keys.json."""
        if not self.config_path.exists():
            logger.warning(f"Key config not found at {self.config_path}")
            return

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data.get("api_keys", []):
            alias = item["alias"]
            cred = CredentialState(
                alias=alias,
                key=item["key"],
                project_name=item.get("project_name", "unknown"),
                project_number=item.get("project_number", "unknown"),
                rpm_limit=item.get("rpm_limit", 15),
                tpm_limit=item.get("tpm_limit", 1000000),
                rpd_limit=item.get("rpd_limit", 1500),
            )
            self.credentials[alias] = cred
            # Refill rate per second: rpm / 60.0
            refill_rate = cred.rpm_limit / 60.0
            self.buckets[alias] = TokenBucket(capacity=cred.rpm_limit, refill_rate_per_sec=refill_rate)

        logger.info(f"Loaded {len(self.credentials)} API credential(s) into KeyManager")

    async def acquire_key(self, exclude_alias: Optional[str] = None) -> CredentialState:
        """
        Retrieves the next available healthy credential, respecting rate limits and cooldowns.
        If exclude_alias is provided, selects a distinct credential (for dual-pass extraction).
        """
        while True:
            now = time.monotonic()
            async with self._lock:
                candidates = []
                for alias, cred in self.credentials.items():
                    if alias == exclude_alias:
                        continue
                    if cred.status == "DISABLED" or cred.status == "EXHAUSTED":
                        continue
                    if cred.status == "COOLDOWN":
                        if now >= cred.cooldown_until:
                            cred.status = "IDLE"
                            cred.consecutive_errors = 0
                            logger.info(f"Key [{alias}] exited cooldown and returned to IDLE")
                        else:
                            continue
                    candidates.append(cred)

                if candidates:
                    # Pick candidate with lowest in-flight / total calls
                    selected = min(candidates, key=lambda c: c.total_calls)
                    bucket = self.buckets[selected.alias]

            if not candidates:
                # All keys are in cooldown or disabled; sleep briefly and retry
                logger.warning("All credentials currently cooling down. Awaiting capacity...")
                await asyncio.sleep(2.0)
                continue

            # Wait for rate limit token
            await bucket.acquire(1.0)
            return selected

    async def report_success(self, alias: str, tokens_used: int = 0) -> None:
        """Records successful API execution."""
        async with self._lock:
            cred = self.credentials.get(alias)
            if cred:
                cred.status = "IDLE"
                cred.consecutive_errors = 0
                cred.total_calls += 1
                cred.total_tokens += tokens_used

    async def report_rate_limit(self, alias: str, retry_after_sec: float = 20.0) -> None:
        """Flags key with cooldown due to HTTP 429."""
        async with self._lock:
            cred = self.credentials.get(alias)
            if cred:
                cred.consecutive_errors += 1
                backoff = min(60.0, retry_after_sec * (1.5 ** (cred.consecutive_errors - 1)))
                cred.status = "COOLDOWN"
                cred.cooldown_until = time.monotonic() + backoff
                logger.warning(
                    f"Key [{alias}] hit rate limit. Cooling down for {backoff:.1f}s "
                    f"(Errors: {cred.consecutive_errors})"
                )

    async def report_disabled(self, alias: str, reason: str) -> None:
        """Permanently disables credential (e.g. 403 Permission Denied / Billing required)."""
        async with self._lock:
            cred = self.credentials.get(alias)
            if cred:
                cred.status = "DISABLED"
                logger.error(f"Permanently disabling key [{alias}] ({cred.project_name}): {reason}")

