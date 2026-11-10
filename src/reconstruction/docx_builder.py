"""
Reflowable Word Document Builder.
Assembles validated page extraction records into a professionally styled,
reflowable Microsoft Word (.docx) document with native editable OMML math equations,
native Word tables, callout boxes, and embedded figure crops.
"""

from pathlib import Path
from typing import List, Optional
import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from src.storage.models import PageExtractionRecord, ContentBlock, TableData
from src.reconstruction.docx_styler import DocxStyler
from src.reconstruction.docx_math_converter import DocxMathConverter
from src.reconstruction.document_beautifier import DocumentBeautifier
from src.reconstruction.math_tokenizer import MathTokenizer, TokenType
from src.utils.logger import get_logger

logger = get_logger("DocxBuilder")

class DocxBuilder:
    """Constructs reflowable Word documents from structured textbook records."""

    def __init__(self, primary_font: str = "Kalpurush", db: Optional[Any] = None):
        self.styler = DocxStyler(primary_font=primary_font)
        self.math_converter = DocxMathConverter()
        self.beautifier = DocumentBeautifier()
        self.tokenizer = MathTokenizer()
        self.db = db

    def build_document(
        self,
        pages: List[PageExtractionRecord],
        output_path: Path,
        title: str = "Khairul's Basic Math"
    ) -> Path:
        """
        Builds a complete, formatted .docx file from the supplied pages.
        Inserts page breaks between textbook pages to guarantee clear multi-page pagination.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc = Document()
        self.styler.apply_document_styles(doc)

        # Document Header
        title_p = doc.add_paragraph()
        title_run = title_p.add_run(title)
        self.styler.set_run_bengali_font(title_run, size_pt=22, bold=True, color=RGBColor(24, 43, 73))
        title_p.paragraph_format.space_after = Pt(16)

        sorted_pages = sorted(pages, key=lambda p: p.page_number)

        for idx, page in enumerate(sorted_pages):
            # Apply DocumentBeautifier polishing
            beautified_page = self.beautifier.beautify_page_record(page)

            # Insert page break between pages so each page starts on a new page in Word and Google Docs
            if idx > 0:
                doc.add_page_break()

            # Subtle page reference marker
            marker_p = doc.add_paragraph()
            marker_run = marker_p.add_run(f"─── [পৃষ্ঠা {beautified_page.page_number}] ───")
            self.styler.set_run_bengali_font(marker_run, size_pt=8.5, color=RGBColor(140, 140, 140))
            marker_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            marker_p.paragraph_format.space_before = Pt(8)
            marker_p.paragraph_format.space_after = Pt(2)

            sorted_blocks = sorted(beautified_page.blocks, key=lambda b: b.reading_order)

            for block in sorted_blocks:
                self._render_block(doc, block, page_number=beautified_page.page_number)

        doc.save(str(output_path))
        logger.info(f"Successfully generated Word document at [{output_path}]")
        return output_path

    def _render_block(self, doc: Document, block: ContentBlock, page_number: Optional[int] = None) -> None:
        """Renders an individual content block based on its classified type."""
        btype = block.type

        if btype.startswith("heading"):
            p = doc.add_paragraph()
            size = 16 if btype == "heading_1" else (14 if btype == "heading_2" else 12)
            color = RGBColor(18, 52, 102) if btype == "heading_1" else RGBColor(30, 41, 59)
            run = p.add_run(block.text or "")
            self.styler.set_run_bengali_font(run, size_pt=size, bold=True, color=color)
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)

        elif btype == "callout_box":
            # Detect callout flavor for styled background shading
            text = block.text or ""
            fill_hex = "F0F4F8"  # Default soft slate
            if any(k in text for k in ("জেনে রাখুন", "নোট", "Note", "মনে রাখুন")):
                fill_hex = "EBF3FA"  # Soft Blue
            elif any(k in text for k in ("শর্টকাট", "ম্যাজিক", "টেকনিক", "Shortcut")):
                fill_hex = "FFFBEA"  # Soft Gold/Amber
            elif any(k in text for k in ("ভুল হতে পারে", "সতর্কতা", "Warning", "Caution")):
                fill_hex = "FEF2F2"  # Soft Rose

            table = doc.add_table(rows=1, cols=1)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            cell = table.cell(0, 0)
            self.styler.set_cell_background(cell, fill_hex=fill_hex)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            self._render_text_with_inline_math(p, text, size_pt=10.5, is_italic=False, page_number=page_number, block_id=block.block_id)
            doc.add_paragraph()  # spacing

        elif btype == "table" or (block.text and "|" in block.text and len(block.text.strip().splitlines()) >= 2):
            t_data = block.table_data or self._parse_markdown_table(block.text or "")
            if t_data and (t_data.headers or t_data.rows):
                self._render_table(doc, t_data, page_number=page_number)
            else:
                p = doc.add_paragraph()
                self._render_text_with_inline_math(p, block.text or "", size_pt=11, page_number=page_number, block_id=block.block_id)

        elif btype == "math_block":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            latex_expr = block.latex or block.text or ""
            omml_el, success, err = self.math_converter.convert_latex_to_omml(latex_expr)
            if omml_el is not None:
                p._p.append(omml_el)
            else:
                run = p.add_run(latex_expr)
                self.styler.set_run_bengali_font(run, size_pt=11, bold=True)

            if not success and self.db is not None and page_number is not None:
                self.db.flag_page_needs_review(
                    page_number=page_number,
                    reason=f"Math block fallback: {err}",
                    block_id=block.block_id
                )

        elif btype == "exercise_item":
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.15)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(3)
            self._render_text_with_inline_math(p, block.text or "", size_pt=11, is_bold_start=True, page_number=page_number, block_id=block.block_id)

        elif btype == "solution_block":
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            self._render_text_with_inline_math(p, block.text or "", size_pt=10.5, is_bold_start=True, page_number=page_number, block_id=block.block_id)

        elif btype == "figure":
            crop_path = None
            if block.figure_data and block.figure_data.crop_path:
                crop_path = Path(block.figure_data.crop_path)

            if crop_path and crop_path.exists():
                doc.add_picture(str(crop_path), width=Inches(4.5))
            elif page_number:
                # Fallback: check output/figures for existing page figure
                matching = list(Path("output/figures").glob(f"page_{page_number:03d}_*.png"))
                if matching:
                    doc.add_picture(str(matching[0]), width=Inches(4.5))

            caption = (block.figure_data.caption if block.figure_data else None) or block.text
            if caption:
                cap_p = doc.add_paragraph()
                cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cap_run = cap_p.add_run(f"চিত্র: {caption}")
                self.styler.set_run_bengali_font(cap_run, size_pt=9.5, color=RGBColor(100, 100, 100), italic=True)

        elif btype != "footer_or_header":
            # Normal paragraph
            p = doc.add_paragraph()
            self._render_text_with_inline_math(p, block.text or "", size_pt=11, page_number=page_number, block_id=block.block_id)

    def _parse_markdown_table(self, text: str) -> Optional[TableData]:
        """Parses markdown table text into structured TableData."""
        if not text or "|" not in text:
            return None

        lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
        pipe_lines = [l for l in lines if "|" in l]
        if len(pipe_lines) < 1:
            return None

        def split_row(row_str: str) -> List[str]:
            s = row_str.strip()
            if s.startswith("|"):
                s = s[1:]
            if s.endswith("|"):
                s = s[:-1]
            return [c.strip() for c in s.split("|")]

        first_row = split_row(pipe_lines[0])
        if len(first_row) < 2:
            return None

        headers = []
        rows = []
        start_idx = 0

        # Check if row 2 is a markdown divider (---)
        if len(pipe_lines) > 1 and all(c.strip().replace("-", "").replace(":", "") == "" for c in split_row(pipe_lines[1])):
            headers = first_row
            start_idx = 2
        else:
            headers = first_row
            start_idx = 1

        num_cols = len(headers)
        for l in pipe_lines[start_idx:]:
            cols = split_row(l)
            if all(c.strip().replace("-", "").replace(":", "") == "" for c in cols):
                continue
            if len(cols) < num_cols:
                cols.extend([""] * (num_cols - len(cols)))
            elif len(cols) > num_cols:
                cols = cols[:num_cols]
            rows.append(cols)

        if not rows and not headers:
            return None

        return TableData(headers=headers, rows=rows)

    def _render_text_with_inline_math(
        self,
        paragraph,
        text: str,
        size_pt: float = 11,
        is_italic: bool = False,
        is_bold_start: bool = False,
        page_number: Optional[int] = None,
        block_id: Optional[str] = None
    ) -> None:
        """
        Tokenizes text into math, text, and citations using MathTokenizer.
        Renders native OMML equations, styled citations, and Bengali text runs.
        """
        if not text:
            return

        tokens = self.tokenizer.tokenize(text)

        for idx, tok in enumerate(tokens):
            if tok.kind in (TokenType.MATH_INLINE, TokenType.MATH_DISPLAY):
                omml_el, success, err = self.math_converter.convert_latex_to_omml(tok.content)
                if omml_el is not None:
                    paragraph._p.append(omml_el)
                else:
                    run = paragraph.add_run(tok.content)
                    self.styler.set_run_bengali_font(run, size_pt=size_pt)

                # Actionable QA flag: If fallback occurred, record it in SQLite
                if not success and self.db is not None and page_number is not None:
                    self.db.flag_page_needs_review(
                        page_number=page_number,
                        reason=f"Math conversion fallback: {err}",
                        block_id=block_id
                    )

            elif tok.kind == TokenType.CITATION:
                # Elegant italicized slate blue font for question sources
                run = paragraph.add_run(f" {tok.content} ")
                self.styler.set_run_bengali_font(
                    run, size_pt=size_pt * 0.95, italic=True, color=RGBColor(65, 85, 115)
                )

            else:
                # Regular text run
                run = paragraph.add_run(tok.content)
                bold = is_bold_start and idx == 0
                self.styler.set_run_bengali_font(run, size_pt=size_pt, bold=bold)

    def _render_table(self, doc: Document, table_data: TableData, page_number: Optional[int] = None) -> None:
        """Constructs a native Word table with styled borders, header shading, and cell padding."""
        num_rows = len(table_data.rows) + (1 if table_data.headers else 0)
        num_cols = len(table_data.headers) if table_data.headers else (len(table_data.rows[0]) if table_data.rows else 1)

        if num_rows == 0 or num_cols == 0:
            return

        table = doc.add_table(rows=num_rows, cols=num_cols)
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        current_row = 0
        if table_data.headers:
            for col_idx, header_text in enumerate(table_data.headers):
                cell = table.cell(0, col_idx)
                self.styler.set_cell_background(cell, fill_hex="E8EDF2")
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(3)
                run = p.add_run(header_text)
                self.styler.set_run_bengali_font(run, size_pt=10, bold=True, color=RGBColor(24, 43, 73))
            current_row += 1

        for r in table_data.rows:
            for col_idx, val in enumerate(r):
                if col_idx < num_cols:
                    cell = table.cell(current_row, col_idx)
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    self._render_text_with_inline_math(p, val, size_pt=9.5, page_number=page_number)
            current_row += 1

        doc.add_paragraph()  # spacing after table

