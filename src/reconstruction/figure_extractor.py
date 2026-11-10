"""
Automated Figure and Diagram Extraction Module.
Detects, crops, cleans, and optimizes diagram and illustration assets from
high-resolution textbook page scans for embedding into Word documents.
"""

from pathlib import Path
from typing import Optional, Tuple, List
import cv2
import numpy as np
from src.storage.models import PageExtractionRecord, ContentBlock, FigureData
from src.utils.logger import get_logger

logger = get_logger("FigureExtractor")

class FigureExtractor:
    """Extracts, cleans, and preserves diagram crops from scanned pages."""

    def __init__(self, output_dir: Path = Path("output/figures")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_figures_for_page(
        self,
        record: PageExtractionRecord,
        page_image: np.ndarray
    ) -> PageExtractionRecord:
        """
        Inspects blocks for diagram/figure regions, crops them from the high-DPI image,
        enhances line contrast, and stores the resulting image files.
        """
        if page_image is None or len(page_image.shape) < 2:
            return record

        h, w = page_image.shape[:2]
        fig_idx = 1

        for block in record.blocks:
            if block.type == "figure" or block.figure_data is not None:
                crop_path = self.output_dir / f"page_{record.page_number:03d}_fig_{fig_idx:02d}.png"

                # Check if bounding box coordinates exist [ymin, xmin, ymax, xmax] (0-1000 scale)
                bbox = block.bbox
                if bbox and len(bbox) == 4:
                    ymin, xmin, ymax, xmax = bbox
                    py_min = max(0, int(ymin * h / 1000.0) - 10)
                    px_min = max(0, int(xmin * w / 1000.0) - 10)
                    py_max = min(h, int(ymax * h / 1000.0) + 10)
                    px_max = min(w, int(xmax * w / 1000.0) + 10)
                else:
                    # Auto-detect diagram contour on the page
                    detected_boxes = self._find_drawing_contours(page_image)
                    if detected_boxes:
                        py_min, px_min, py_max, px_max = detected_boxes[0]
                    else:
                        py_min, px_min, py_max, px_max = 0, 0, 0, 0

                if py_max > py_min and px_max > px_min:
                    crop = page_image[py_min:py_max, px_min:px_max]
                    enhanced_crop = self._enhance_diagram_crop(crop)
                    cv2.imwrite(str(crop_path), enhanced_crop)
                    logger.info(f"Page {record.page_number}: Saved enhanced figure crop -> [{crop_path}]")

                    fig_id = f"p{record.page_number}_fig{fig_idx:02d}"
                    if not block.figure_data:
                        block.figure_data = FigureData(
                            figure_id=fig_id,
                            crop_path=str(crop_path),
                            caption=block.text or f"চিত্র {fig_idx}"
                        )
                    else:
                        block.figure_data.crop_path = str(crop_path)
                        if not getattr(block.figure_data, "figure_id", None):
                            block.figure_data.figure_id = fig_id

                    fig_idx += 1

        return record

    def _find_drawing_contours(self, page_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Finds prominent non-text drawing/diagram contour regions on the page."""
        gray = cv2.cvtColor(page_image, cv2.COLOR_BGR2GRAY) if len(page_image.shape) == 3 else page_image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        gradient = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
        _, thresh = cv2.threshold(gradient, 40, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        h, w = gray.shape[:2]
        min_area = (h * w) * 0.01  # At least 1% of page area
        for c in contours:
            x, y, bw, bh = cv2.boundingRect(c)
            if bw * bh > min_area and bh > 60 and bw > 60:
                boxes.append((max(0, y - 5), max(0, x - 5), min(h, y + bh + 5), min(w, x + bw + 5)))
        return boxes

    def _enhance_diagram_crop(self, crop: np.ndarray) -> np.ndarray:
        """
        Polishes a diagram crop by whitening paper background texture
        and sharpening line drawings / geometric shapes.
        """
        if crop is None or crop.size == 0:
            return crop

        # Convert to grayscale to evaluate illumination
        if len(crop.shape) == 3:
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        else:
            gray = crop.copy()

        # Smooth paper texture while preserving hard edges (bilateral filter)
        filtered = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)

        # Background normalization: divide by morphological background
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        background = cv2.morphologyEx(filtered, cv2.MORPH_DILATE, kernel)
        diff = cv2.absdiff(filtered, background)
        normalized = cv2.normalize(255 - diff, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

        # Convert back to BGR for Word compatibility
        if len(crop.shape) == 3:
            return cv2.cvtColor(normalized, cv2.COLOR_GRAY2BGR)
        return normalized
