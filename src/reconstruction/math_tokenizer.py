"""
Lexical Tokenizer and AST Math Scanner.
Replaces brittle regular expression heuristics with a stateful lexer that
cleanly tokenizes mixed Bengali prose, LaTeX math expressions, and exam citations.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import re
from src.utils.logger import get_logger

logger = get_logger("MathTokenizer")

class TokenType(str, Enum):
    TEXT = "TEXT"
    MATH_INLINE = "MATH_INLINE"
    MATH_DISPLAY = "MATH_DISPLAY"
    CITATION = "CITATION"

@dataclass
class Token:
    kind: TokenType
    content: str

class MathTokenizer:
    """Stateful lexer for separating text, math expressions, and question citations."""

    CITATION_KEYWORDS = (
        "ব্যাংক", "বিসিএস", "মন্ত্রণালয়", "বোর্ড", "নিয়োগ", "পরীক্ষা",
        "Bank", "BCS", "Class", "বই", "সঞ্চয়", "অধিদপ্তর", "সহকারী", "প্রাথমিক"
    )

    def tokenize(self, text: str) -> List[Token]:
        """
        Tokenizes text into a clean sequence of TEXT, MATH_INLINE, MATH_DISPLAY,
        and CITATION tokens.
        """
        if not text:
            return []

        tokens: List[Token] = []
        i = 0
        n = len(text)
        current_text: List[str] = []

        def flush_text():
            if current_text:
                val = "".join(current_text)
                if val:
                    # Check if the text chunk is an exam citation
                    if self._is_citation(val):
                        tokens.append(Token(kind=TokenType.CITATION, content=val))
                    else:
                        tokens.append(Token(kind=TokenType.TEXT, content=val))
                current_text.clear()

        while i < n:
            # 1. Escaped dollar sign: \$ -> literal dollar
            if text[i] == "\\" and i + 1 < n and text[i + 1] == "$":
                current_text.append("$")
                i += 2
                continue

            # 2. Display Math: $$ ... $$
            if text[i:i+2] == "$$":
                flush_text()
                # Find matching closing $$
                end = text.find("$$", i + 2)
                if end != -1:
                    math_content = text[i+2:end].strip()
                    # Check if there is an accidental citation inside the math
                    math_pure, citation = self._extract_citation_from_math(math_content)
                    if math_pure:
                        tokens.append(Token(kind=TokenType.MATH_DISPLAY, content=math_pure))
                    if citation:
                        tokens.append(Token(kind=TokenType.CITATION, content=citation))
                    i = end + 2
                else:
                    # Unterminated $$, treat as single dollar
                    current_text.append("$")
                    i += 1
                continue

            # 3. Inline Math: $ ... $
            if text[i] == "$":
                flush_text()
                # Find matching closing $ (not preceded by \)
                end = i + 1
                found_close = False
                while end < n:
                    if text[end] == "$" and text[end - 1] != "\\":
                        found_close = True
                        break
                    end += 1

                if found_close:
                    math_content = text[i+1:end].strip()
                    math_pure, citation = self._extract_citation_from_math(math_content)
                    if math_pure:
                        tokens.append(Token(kind=TokenType.MATH_INLINE, content=math_pure))
                    if citation:
                        tokens.append(Token(kind=TokenType.CITATION, content=citation))
                    i = end + 1
                else:
                    current_text.append("$")
                    i += 1
                continue

            # 4. Bracketed text [ ... ] - check for standalone citations
            if text[i] == "[":
                close_bracket = text.find("]", i + 1)
                if close_bracket != -1:
                    bracket_content = text[i:close_bracket + 1]
                    if self._is_citation(bracket_content):
                        flush_text()
                        tokens.append(Token(kind=TokenType.CITATION, content=bracket_content))
                        i = close_bracket + 1
                        continue

            # 5. Regular character
            current_text.append(text[i])
            i += 1

        flush_text()
        return tokens

    def _is_citation(self, text: str) -> bool:
        """Determines if a string matches an exam or source citation."""
        stripped = text.strip()
        if (stripped.startswith("[") and stripped.endswith("]")) or (stripped.startswith("(") and stripped.endswith(")")):
            return any(k in stripped for k in self.CITATION_KEYWORDS)
        return False

    def _extract_citation_from_math(self, math_content: str) -> (str, Optional[str]):
        """Splits citations accidentally enclosed inside math delimiters."""
        for k in self.CITATION_KEYWORDS:
            if k in math_content:
                # Find matching bracket or parenthesis
                m = re.search(r'(\[[^\]]*\]|\([^\)]*\))', math_content)
                if m:
                    citation = m.group(0)
                    pure_math = math_content.replace(citation, "").strip()
                    return pure_math, citation
        return math_content, None

