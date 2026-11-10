"""
Word Document Styler.
Configures typography, styles, colors, line spacing, margins, and complex script
font bindings (Kalpurush) for professional textbook publishing.
"""

from typing import Optional
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from src.utils.logger import get_logger

logger = get_logger("DocxStyler")

class DocxStyler:
    """Manages document styles and Bengali font bindings for python-docx."""

    def __init__(self, primary_font: str = "Kalpurush"):
        self.primary_font = primary_font

    def apply_document_styles(self, doc: Document) -> None:
        """Configures page margins and default styles."""
        # Page Margins (0.75 in / 54pt)
        for section in doc.sections:
            section.top_margin = Inches(0.75)
            section.bottom_margin = Inches(0.75)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)

        # Configure Normal Style
        normal_style = doc.styles["Normal"]
        normal_style.font.name = self.primary_font
        normal_style.font.size = Pt(11)
        normal_style.font.color.rgb = RGBColor(30, 30, 30)
        normal_style.paragraph_format.line_spacing = 1.15
        normal_style.paragraph_format.space_after = Pt(4)

    def set_run_bengali_font(
        self,
        run,
        size_pt: float = 11,
        bold: bool = False,
        italic: bool = False,
        color: Optional[RGBColor] = None
    ) -> None:
        """
        Sets font name, size, bold, italic, and explicit Complex Script (w:cs) XML attributes
        so Microsoft Word correctly renders Bengali characters with the Kalpurush font.
        """
        run.font.name = self.primary_font
        run.font.size = Pt(size_pt)
        run.bold = bold
        run.italic = italic
        if color:
            run.font.color.rgb = color

        # Set complex script font in underlying XML (w:rFonts)
        rPr = run._r.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)

        rFonts.set(qn("w:ascii"), self.primary_font)
        rFonts.set(qn("w:hAnsi"), self.primary_font)
        rFonts.set(qn("w:cs"), self.primary_font)

    @staticmethod
    def set_cell_background(cell, fill_hex: str = "F2F4F7") -> None:
        """Sets shading background color for table cells or callout boxes."""
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), fill_hex)
        tcPr.append(shd)
