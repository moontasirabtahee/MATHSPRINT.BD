"""
AI Judge and Self-Correction Arbitration Engine.
Resolves discordant OCR extractions by directly inspecting original image pixels
and adjudicating token-level differences.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from src.extraction.gemini_client import GeminiClient
from src.extraction.prompts import AI_JUDGE_ARBITRATION_PROMPT
from src.utils.logger import get_logger

logger = get_logger("AIJudge")

class AIJudge:
    """Arbiter that resolves discrepancies between parallel extraction workers."""

    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client

    async def arbitrate(
        self,
        image: np.ndarray,
        api_key: str,
        credential_alias: str,
        extraction_a: Dict[str, Any],
        extraction_b: Dict[str, Any],
        discrepancies: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Supplies original image crop along with both extractions to the Judge for pixel-level resolution.
        """
        logger.info(
            f"AI Judge invoked using [{credential_alias}]. "
            f"Resolving {len(discrepancies)} discrepancy item(s)..."
        )

        arbitration_context = (
            f"{AI_JUDGE_ARBITRATION_PROMPT}\n\n"
            f"### DISCREPANCIES DETECTED:\n"
            f"{chr(10).join(f'- {d}' for d in discrepancies)}\n\n"
            f"### EXTRACTION A (Worker: {extraction_a.get('worker_alias')}):\n"
            f"{extraction_a.get('raw_text', '')}\n\n"
            f"### EXTRACTION B (Worker: {extraction_b.get('worker_alias')}):\n"
            f"{extraction_b.get('raw_text', '')}\n"
        )

        result = await self.client.extract_page(
            image=image,
            api_key=api_key,
            credential_alias=credential_alias,
            custom_prompt=arbitration_context
        )

        logger.info(
            f"AI Judge resolved consensus: {len(result['parsed_blocks'])} verified blocks produced."
        )

        return result["parsed_blocks"]

