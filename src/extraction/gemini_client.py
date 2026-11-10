"""
Gemini Vision Extraction Client.
Wraps the modern Google GenAI SDK to perform asynchronous vision extractions
with structured prompt enforcement and token usage reporting.
"""

import time
import json
import asyncio
from typing import Dict, Any, Tuple, Optional
import cv2
import numpy as np
from google import genai
from google.genai import types
from src.extraction.prompts import EXTRACTION_SYSTEM_PROMPT
from src.utils.logger import get_logger

logger = get_logger("GeminiClient")

class GeminiClient:
    """Async client for Gemini Vision extractions."""

    def __init__(self, model_name: str = "gemini-3.1-flash-lite"):
        self.model_name = model_name

    async def extract_page(
        self,
        image: np.ndarray,
        api_key: str,
        credential_alias: str,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submits preprocessed image to Gemini Vision API and returns parsed blocks and usage.
        """
        # Encode image to PNG bytes
        success, encoded_img = cv2.imencode(".png", image)
        if not success:
            raise ValueError("Failed to encode image to PNG for Gemini API")
        image_bytes = encoded_img.tobytes()

        client = genai.Client(api_key=api_key)
        prompt = custom_prompt or EXTRACTION_SYSTEM_PROMPT

        start_time = time.monotonic()

        # Modern google-genai async call
        response = await client.aio.models.generate_content(
            model=self.model_name,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                prompt
            ],
            config=types.GenerateContentConfig(
                temperature=0.1,  # Low temperature for deterministic factual extraction
                response_mime_type="application/json"
            )
        )

        latency = time.monotonic() - start_time
        raw_text = response.text.strip() if response.text else "{}"

        # Extract token usage if available in metadata
        input_tokens = 0
        output_tokens = 0
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
            output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

        # Parse JSON robustly with multi-stage LaTeX backslash recovery
        parsed_data = self._robust_json_decode(raw_text)

        if isinstance(parsed_data, list):
            parsed_blocks = parsed_data
        elif isinstance(parsed_data, dict):
            parsed_blocks = parsed_data.get("blocks", [])
        else:
            parsed_blocks = []

        return {
            "worker_alias": credential_alias,
            "raw_text": raw_text,
            "parsed_blocks": parsed_blocks,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_seconds": round(latency, 2)
        }

    def _robust_json_decode(self, text: str) -> Any:
        r"""
        Robustly decodes JSON from LLM outputs, automatically repairing:
        - \underline, \uparrow, \upsilon (where \u is followed by non-hex chars)
        - \frac, \times, \pm, \sqrt, \alpha, \beta, \sum (unescaped backslashes in math notation)
        - Raw control characters and markdown fences
        """
        import re
        cleaned = text.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Pass 1: Fix \u followed by non-hex characters (e.g. \underline)
        step1 = re.sub(r'\\u(?![0-9a-fA-F]{4})', r'\\\\u', cleaned)

        # Pass 2: In JSON strings, backslashes followed by letters ([a-zA-Z]) are LaTeX commands
        step2 = re.sub(r'(?<!\\)\\(?![\\"/])([a-zA-Z])', r'\\\\\1', step1)
        try:
            return json.loads(step2)
        except json.JSONDecodeError:
            pass

        # Pass 3: Double any remaining lone backslash
        step3 = re.sub(r'(?<!\\)\\(?!["\\])', r'\\\\', step1)
        try:
            return json.loads(step3)
        except json.JSONDecodeError:
            pass

        # Pass 4: Final fallback - replace all single backslashes
        step4 = re.sub(r'\\(?!["\\])', r'\\\\', cleaned)
        return json.loads(step4)
