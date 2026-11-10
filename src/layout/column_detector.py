"""
Column Detector.
Detects column structures and vertical gutters in textbook page layouts
using horizontal projection profiles and whitespace valley analysis.
"""

from typing import List, Tuple
import cv2
import numpy as np
from src.utils.logger import get_logger

logger = get_logger("ColumnDetector")

class ColumnDetector:
    """Analyzes page whitespace to detect multi-column boundaries."""

    def __init__(self, min_gutter_width_px: int = 25):
        self.min_gutter_width_px = min_gutter_width_px

    def detect_columns(self, image: np.ndarray) -> List[Tuple[int, int]]:
        """
        Detects horizontal column spans [(x_start, x_end), ...].
        Returns:
            List of (x_start, x_end) pixel intervals for each detected column.
        """
        if image is None or image.size == 0:
            return [(0, 1000)]

        h, w = image.shape[:2]
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Binarize with Otsu
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Ignore top 10% (header) and bottom 10% (footer) when evaluating column structure
        content_zone = binary[int(h * 0.10) : int(h * 0.90), :]

        # Compute vertical projection (sum along columns)
        v_proj = np.sum(content_zone > 0, axis=0)

        # Smooth projection
        ksize = max(5, w // 100) | 1
        smoothed_proj = cv2.GaussianBlur(v_proj.astype(np.float32).reshape(1, -1), (ksize, 1), 0)[0]

        # Content margin detection (left and right outer margins)
        active_threshold = np.max(smoothed_proj) * 0.05
        active_indices = np.where(smoothed_proj > active_threshold)[0]

        if len(active_indices) == 0:
            return [(0, w)]

        left_margin = int(active_indices[0])
        right_margin = int(active_indices[-1])
        inner_width = right_margin - left_margin

        # Search for central gutter (whitespace valley) in the middle 60% of the active area
        mid_start = left_margin + int(inner_width * 0.30)
        mid_end = left_margin + int(inner_width * 0.70)

        valley_zone = smoothed_proj[mid_start:mid_end]
        if len(valley_zone) == 0:
            return [(left_margin, right_margin)]

        min_val = np.min(valley_zone)
        mean_val = np.mean(smoothed_proj[left_margin:right_margin])

        # A true 2-column gutter has near-zero density in the valley compared to column content
        is_two_column = min_val < (mean_val * 0.15) and (mid_end - mid_start) > self.min_gutter_width_px

        if is_two_column:
            valley_center = mid_start + int(np.argmin(valley_zone))
            col1 = (left_margin, valley_center - 10)
            col2 = (valley_center + 10, right_margin)
            logger.debug(f"Detected 2-column layout: {col1}, {col2}")
            return [col1, col2]
        else:
            return [(left_margin, right_margin)]

