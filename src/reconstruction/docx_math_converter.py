"""
LaTeX to Office Math Markup Language (OMML) Converter.
Transforms LaTeX expressions to MathML XML, and converts MathML into genuine,
native editable Word equations (<m:oMath>) using the standard MathML2OMML engine.
Automatically unwraps <m:box> tags and purges empty runs so equations are 100% compatible
with both Microsoft Word and Google Docs.
Automatically injects <m:nor/> for Bengali numerals so Word renders them with Kalpurush.
Provides actionable QA error reporting so failed expressions are flagged in SQLite.
"""

from typing import Optional, Any, Tuple
import re
from xml.sax.saxutils import escape as xml_escape
import lxml.etree as ET
from latex2mathml.converter import convert as latex_to_mathml
import mathml2omml
from docx.oxml import parse_xml
from src.utils.logger import get_logger

logger = get_logger("DocxMathConverter")

MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"

class DocxMathConverter:
    """Converts LaTeX mathematical formulas into native Word OMML XML elements."""

    def convert_latex_to_omml(self, latex: str) -> Tuple[Optional[Any], bool, Optional[str]]:
        """
        Converts LaTeX string to a python-docx OxmlElement representing <m:oMath>.
        Returns:
            Tuple of (oxml_element, success_bool, error_message_or_None)
        """
        if not latex or not latex.strip():
            return None, True, None

        clean_latex = latex.strip().strip("$")

        try:
            # 1. Convert LaTeX to MathML
            mathml_str = latex_to_mathml(clean_latex)

            # 2. Convert MathML to genuine OMML
            omml_str = mathml2omml.convert(mathml_str)

            # 3. Clean OMML for strict Word & Google Docs compatibility:
            #    - Unwraps <m:box><m:e> wrappers that crash Google Docs
            #    - Purges empty runs <m:r><m:t/></m:r>
            #    - Injects and deduplicates <m:nor/> for Bengali text/digits
            omml_cleaned = self._clean_omml_for_word_and_gdocs(omml_str)

            # 4. Parse into Word OXML element
            oxml_element = parse_xml(omml_cleaned)
            return oxml_element, True, None

        except Exception as e:
            err_msg = str(e)
            logger.warning(f"Failed to convert LaTeX '{clean_latex}' to OMML: {err_msg}")
            try:
                # Fallback: create raw text run equation with properly escaped XML
                safe_text = xml_escape(clean_latex)
                fallback_xml = (
                    f'<m:oMath xmlns:m="{MATH_NS}">'
                    f'<m:r><m:rPr><m:nor/></m:rPr><m:t>{safe_text}</m:t></m:r>'
                    f'</m:oMath>'
                )
                return parse_xml(fallback_xml), False, f"LaTeX-to-OMML fallback: {err_msg}"
            except Exception as fe:
                logger.warning(f"Fallback OMML generation failed for '{clean_latex}': {fe}")
                return None, False, f"OMML generation failure: {fe}"

    def _clean_omml_for_word_and_gdocs(self, omml_xml: str) -> str:
        """
        Cleans and normalizes OMML XML for full cross-platform compatibility:
        - Ensures root has xmlns:m
        - Recursively strips <m:box><m:e> containers (which crash Google Docs converter)
        - Injects <m:nor/> for non-ASCII characters (Kalpurush font fallback)
        - Removes redundant duplicate <m:nor/> elements
        - Removes empty <m:r> runs containing no text
        """
        if "xmlns:m=" not in omml_xml:
            omml_xml = omml_xml.replace("<m:oMath>", f'<m:oMath xmlns:m="{MATH_NS}">')

        root = ET.fromstring(omml_xml.encode("utf-8"))
        ns = {"m": MATH_NS}

        # 1. Recursively unwrap all <m:box> elements (from innermost to outermost)
        while True:
            boxes = root.xpath(".//m:box", namespaces=ns)
            if not boxes:
                break
            for box in boxes:
                parent = box.getparent()
                if parent is None:
                    continue
                e_elem = box.find(f"{{{MATH_NS}}}e")
                if e_elem is not None:
                    box_idx = list(parent).index(box)
                    for child in list(e_elem):
                        parent.insert(box_idx, child)
                        box_idx += 1
                parent.remove(box)

        # 2. Injects <m:nor/> for non-ASCII characters & deduplicate
        for r in root.xpath(".//m:r", namespaces=ns):
            t = r.find(f"{{{MATH_NS}}}t")
            if t is not None and t.text:
                if any(ord(c) > 127 for c in t.text):
                    rpr = r.find(f"{{{MATH_NS}}}rPr")
                    if rpr is None:
                        rpr = ET.Element(f"{{{MATH_NS}}}rPr")
                        r.insert(0, rpr)
                    if rpr.find(f"{{{MATH_NS}}}nor") is None:
                        rpr.append(ET.Element(f"{{{MATH_NS}}}nor"))

        # Deduplicate <m:nor/> inside any <m:rPr>
        for rpr in root.xpath(".//m:rPr", namespaces=ns):
            nors = rpr.findall(f"{{{MATH_NS}}}nor")
            if len(nors) > 1:
                for extra in nors[1:]:
                    rpr.remove(extra)

        # 3. Remove empty runs <m:r>
        for r in root.xpath(".//m:r", namespaces=ns):
            t = r.find(f"{{{MATH_NS}}}t")
            if t is None or not t.text or not t.text.strip():
                parent = r.getparent()
                if parent is not None:
                    parent.remove(r)

        return ET.tostring(root, encoding="utf-8").decode("utf-8")
