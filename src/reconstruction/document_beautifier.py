"""
Document Beautifier and Typography Polish Engine.
Normalizes mathematical notation, cleans question citations, repairs Bengali fraction
rendering in Office Math (OMML), and applies publishing-grade formatting.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from src.storage.models import PageExtractionRecord, ContentBlock
from src.utils.logger import get_logger

logger = get_logger("DocumentBeautifier")

class DocumentBeautifier:
    """Pre-processes and polishes content blocks before Word document construction."""

    # Regex for detecting common competitive exam sources in Bengali textbooks
    SOURCE_PATTERN = re.compile(
        r'(\[[^\]]*(?:ব্যাংক|বিসিএস|মন্ত্রণালয়|বোর্ড|নিয়োগ|পরীক্ষা|Bank|BCS|Class|বই|সঞ্চয়|অধিদপ্তর|সহকারী|প্রাথমিক)[^\]]*\]|'
        r'\((?:[^\)]*(?:ব্যাংক|বিসিএস|মন্ত্রণালয়|বোর্ড|নিয়োগ|পরীক্ষা|Bank|BCS|Class|বই|সঞ্চয়|অধিদপ্তর|সহকারী|প্রাথমিক)[^\)]*)\))',
        re.IGNORECASE
    )

    # Regex for loose Unicode math (square roots, powers, multiplication signs)
    LOOSE_SQRT_PATTERN = re.compile(r'(?<!\$)(√[০-৯a-zA-Zক-হ]+)(?!\$)')
    LOOSE_EXPONENT_PATTERN = re.compile(r'(?<!\$)([০-৯a-zA-Zক-হ]+)\^([০-৯a-zA-Z\d]+)(?!\$)')
    LOOSE_MULT_PATTERN = re.compile(r'(?<!\$)([০-৯a-zA-Z\d]+)\s*([×*])\s*([০-৯a-zA-Z\d]+)(?!\$)')

    def beautify_page_record(self, record: PageExtractionRecord) -> PageExtractionRecord:
        """Applies typography polishing and math normalization across all blocks of a page."""
        beautified_blocks: List[ContentBlock] = []

        for block in record.blocks:
            b = block.model_copy(deep=True)
            self._beautify_block(b)
            beautified_blocks.append(b)

        record.blocks = beautified_blocks
        return record

    def _beautify_block(self, block: ContentBlock) -> None:
        """In-place beautification of an individual ContentBlock."""
        if not block.text:
            return

        text = block.text

        # 1. Sanitize Display Math ($$ ... $$) into clean inline or display tokens
        text = self._sanitize_dollar_math(text)

        # 2. Extract and sanitize mixed citations inside math delimiters
        text = self._separate_citations_from_math(text)

        # 3. Upgrade loose Unicode math outside $...$ to proper LaTeX math
        text = self._upgrade_loose_unicode_math(text)

        # 4. Polish Bengali numbers & typography
        text = self._polish_bangla_typography(text)

        # 5. Format MCQ options and answer markers nicely
        text = self._format_mcq_options(text)

        block.text = text

    def _format_mcq_options(self, text: str) -> str:
        """Formats MCQ option labels (ক, খ, গ, ঘ or a, b, c, d) with consistent bold markers."""
        # Normalize (ক), (খ), (গ), (ঘ)
        text = re.sub(r'[\(（]([ক-ঘa-dA-D])[\)）]', r' (\1) ', text)
        # Separate উত্তর / Answer tag onto its own clear visual anchor
        text = re.sub(r'(উত্তর\s*:\s*[ক-ঘa-dA-D]|Ans\s*:\s*[ক-ঘa-dA-D])', r' \n\1 ', text)
        return text

    def _sanitize_dollar_math(self, text: str) -> str:
        """
        Replaces double dollar delimiters ($$ ... $$) with standard single dollars
        or clean newlines so the tokenizer does not leave orphan '$' characters.
        """
        # Replace $$...$$ with $...$
        text = re.sub(r'\$\$\s*(.*?)\s*\$\$', r' $\1$ ', text)
        return text

    def _separate_citations_from_math(self, text: str) -> str:
        """
        Finds occurrences where question sources (e.g. [Sonali Bank-08]) or Bengali notes
        were accidentally enclosed inside math delimiters ($...$) and moves them outside.
        """
        def clean_math_match(match: re.Match) -> str:
            inner = match.group(1).strip()
            # Check if inner contains an exam citation
            citation_match = self.SOURCE_PATTERN.search(inner)
            if citation_match:
                citation = citation_match.group(0)
                # Remove citation from inside math
                pure_math = inner.replace(citation, "").strip()
                if pure_math:
                    return f"${pure_math}$ {citation}"
                else:
                    return citation
            return f"${inner}$"

        return re.sub(r'\$([^\$]+)\$', clean_math_match, text)

    def _upgrade_loose_unicode_math(self, text: str) -> str:
        r"""
        Upgrades un-typeset math like √ক into $\sqrt{ক}$ and x^২ into $x^{২}$
        when they occur outside of existing math delimiters.
        """
        # Split text into math and non-math segments to only transform prose
        parts = re.split(r'(\$[^\$]+\$)', text)
        for i in range(len(parts)):
            if not parts[i].startswith("$"):
                # Upgrade square roots: √ক -> $\sqrt{ক}$
                parts[i] = self.LOOSE_SQRT_PATTERN.sub(r'$\\sqrt{\1}$', parts[i])
                parts[i] = parts[i].replace("$\\sqrt{√", "$\\sqrt{")
                # Upgrade powers: x^2 or ক^৩ -> $x^{2}$
                parts[i] = self.LOOSE_EXPONENT_PATTERN.sub(r'$\1^{\2}$', parts[i])

        return "".join(parts)

    def _polish_bangla_typography(self, text: str) -> str:
        """Polishes dashes, quotation marks, and Bengali spacing."""
        # Convert multiple raw carets >>>> to a clean right arrow
        text = re.sub(r'>{3,}', ' ➔ ', text)
        # Convert ASCII quotes to typographic quotes around Bengali
        text = re.sub(r'"([^"]+)"', r'“\1”', text)
        # Normalize double spaces
        text = re.sub(r'[ \t]{2,}', ' ', text)
        return text.strip()
