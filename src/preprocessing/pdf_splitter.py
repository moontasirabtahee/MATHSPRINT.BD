"""
PDF Splitter.
Manages batch splitting, page extraction, and memory-safe iteration across
large volumes (e.g. 800+ pages) without memory leakage.
"""

from pathlib import Path
from typing import Generator, List, Tuple
import pymupdf
from src.utils.logger import get_logger

logger = get_logger("PDFSplitter")

class PDFSplitter:
    """Chunks large PDF textbooks into manageable batches."""

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"Source PDF not found at {pdf_path}")

        doc = pymupdf.open(str(self.pdf_path))
        self.total_pages = len(doc)
        doc.close()

    def get_batches(self, batch_size: int = 25) -> List[Tuple[int, int]]:
        """
        Returns list of (start_page, end_page) 1-based inclusive tuples.
        """
        batches = []
        for start in range(1, self.total_pages + 1, batch_size):
            end = min(start + batch_size - 1, self.total_pages)
            batches.append((start, end))
        return batches

    def extract_page_range(self, start_page: int, end_page: int, output_pdf: str) -> None:
        """
        Extracts a subset of pages into a separate sub-PDF for isolated processing.
        """
        doc = pymupdf.open(str(self.pdf_path))
        sub_doc = pymupdf.open()
        # PyMuPDF uses 0-based indices
        sub_doc.insert_pdf(doc, from_page=start_page - 1, to_page=end_page - 1)
        sub_doc.save(output_pdf)
        sub_doc.close()
        doc.close()
        logger.info(f"Extracted pages {start_page}-{end_page} to {output_pdf}")

