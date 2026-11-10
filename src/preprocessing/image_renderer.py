"""
Image Renderer.
Renders PDF pages to high-resolution (350-400 DPI) numpy RGB images using PyMuPDF.
"""

from pathlib import Path
from typing import Optional, Tuple
import pymupdf
import numpy as np
import cv2
from src.utils.logger import get_logger

logger = get_logger("ImageRenderer")

class ImageRenderer:
    """High-DPI PDF page rasterizer."""

    def __init__(self, target_dpi: int = 350):
        self.target_dpi = target_dpi
        # Standard PDF coordinate space is 72 points per inch
        self.zoom = target_dpi / 72.0

    def render_page(self, page: pymupdf.Page) -> np.ndarray:
        """
        Renders a PyMuPDF Page into a high-DPI BGR numpy array for OpenCV processing.
        """
        mat = pymupdf.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        # Convert raw pixmap samples to numpy array
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, 3))
        # PyMuPDF produces RGB; convert to BGR for OpenCV
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        return bgr

    def render_from_pdf(self, pdf_path: str, page_number: int) -> np.ndarray:
        """
        Opens PDF and renders 1-based page_number.
        """
        doc = pymupdf.open(pdf_path)
        if page_number < 1 or page_number > len(doc):
            raise IndexError(f"Page {page_number} out of range (1..{len(doc)})")
        page = doc[page_number - 1]
        img = self.render_page(page)
        doc.close()
        return img

