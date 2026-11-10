"""
Diff and Consensus Engine.
Compares independent OCR extractions using Unicode NFC normalization,
token sequence matching, and mathematical equivalence checking.
"""

import unicodedata
from difflib import SequenceMatcher
from typing import List, Dict, Any, Tuple
from src.storage.models import ContentBlock
from src.utils.logger import get_logger

logger = get_logger("DiffEngine")

class DiffEngine:
    """Calculates textual and structural similarity between competing extraction passes."""

    @staticmethod
    def normalize_bengali_text(text: str) -> str:
        """Applies Unicode NFC normalization and strips superfluous whitespace."""
        if not text:
            return ""
        # Unicode NFC compose
        normalized = unicodedata.normalize("NFC", text)
        # Collapse multiple spaces
        normalized = " ".join(normalized.split())
        return normalized

    def compare_blocks(
        self,
        blocks_a: List[Dict[str, Any]],
        blocks_b: List[Dict[str, Any]]
    ) -> Tuple[float, List[str]]:
        """
        Compares two block streams and produces a similarity score [0..1] and flagged diffs.
        """
        if not blocks_a and not blocks_b:
            return 1.0, []
        if not blocks_a or not blocks_b:
            return 0.0, ["One extraction pass returned empty blocks"]

        discrepancies: List[str] = []

        # Join full texts for global character similarity
        text_a = self.normalize_bengali_text(" ".join(b.get("text", "") or "" for b in blocks_a))
        text_b = self.normalize_bengali_text(" ".join(b.get("text", "") or "" for b in blocks_b))

        matcher = SequenceMatcher(None, text_a, text_b)
        similarity = matcher.ratio()

        # Detailed block count and type comparison
        if len(blocks_a) != len(blocks_b):
            discrepancies.append(
                f"Block count discrepancy: Worker A produced {len(blocks_a)} blocks, "
                f"Worker B produced {len(blocks_b)} blocks"
            )

        # Inspect mathematical expressions across blocks
        maths_a = [b.get("latex") for b in blocks_a if b.get("latex")]
        maths_b = [b.get("latex") for b in blocks_b if b.get("latex")]

        if maths_a != maths_b:
            discrepancies.append(
                f"Mathematical formula disagreement: Worker A found {len(maths_a)} formulas, "
                f"Worker B found {len(maths_b)} formulas"
            )

        return round(similarity, 4), discrepancies

