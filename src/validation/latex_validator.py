"""
LaTeX and Mathematical Syntax Validator.
Validates structural integrity, delimiter balance, and MathML parseability
for all mathematical expressions extracted from the textbook.
"""

from typing import Tuple, Optional
import re
import latex2mathml.commands
import latex2mathml.tokenizer
from latex2mathml.converter import convert as latex_to_mathml
from src.utils.logger import get_logger

logger = get_logger("LaTeXValidator")

class LaTeXValidator:
    """Validates mathematical LaTeX strings for structural and syntactic correctness."""

    def validate_expression(self, latex: str) -> Tuple[bool, Optional[str]]:
        """
        Validates a LaTeX math string.
        Returns:
            Tuple[is_valid: bool, error_message: Optional[str]]
        """
        if not latex or not latex.strip():
            return True, None

        cleaned = latex.strip().strip("$")

        # 1. Delimiter Balance Check
        balanced, err = self._check_delimiter_balance(cleaned)
        if not balanced:
            return False, err

        # 2. Convert to MathML using latex2mathml to verify complete syntax validity
        try:
            _ = latex_to_mathml(cleaned)
            return True, None
        except Exception as e:
            return False, f"MathML conversion syntax error: {str(e)}"

    @staticmethod
    def _check_delimiter_balance(text: str) -> Tuple[bool, Optional[str]]:
        """Verifies matched braces, brackets, and parentheses."""
        pairs = {"{": "}", "[": "]", "(": ")"}
        stack = []

        for idx, char in enumerate(text):
            if char in pairs.keys():
                stack.append((char, idx))
            elif char in pairs.values():
                if not stack:
                    return False, f"Unmatched closing delimiter '{char}' at index {idx}"
                open_char, _ = stack.pop()
                if pairs[open_char] != char:
                    return False, f"Mismatched delimiter: expected '{pairs[open_char]}' but found '{char}' at index {idx}"

        if stack:
            open_char, idx = stack[-1]
            return False, f"Unclosed delimiter '{open_char}' at index {idx}"

        return True, None

