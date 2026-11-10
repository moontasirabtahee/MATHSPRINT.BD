"""
Image Enhancer.
Applies conservative CLAHE (Contrast Limited Adaptive Histogram Equalization)
and unsharp masking to enhance thin strokes, subscripts, superscripts, and
Bengali vowel marks (মাত্রাহীন ও অর্ধমাত্রা বর্ণ/কার) without introducing noise artifacts.
"""

from typing import Optional, Tuple
import cv2
import numpy as np
from src.utils.logger import get_logger

logger = get_logger("ImageEnhancer")

class ImageEnhancer:
    """Enhances text contrast and edge sharpness while preserving faint diacritics."""

    def __init__(self, clahe_clip_limit: float = 1.5, tile_grid_size: int = 8):
        self.clahe_clip_limit = clahe_clip_limit
        self.tile_grid_size = tile_grid_size
        self._clahe = cv2.createCLAHE(
            clipLimit=self.clahe_clip_limit,
            tileGridSize=(self.tile_grid_size, self.tile_grid_size)
        )

    def apply_clahe(self, image: np.ndarray) -> np.ndarray:
        """
        Applies CLAHE on luminance channel only to preserve color fidelity.
        """
        if image is None or image.size == 0:
            return image

        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l_enhanced = self._clahe.apply(l)
            merged = cv2.merge([l_enhanced, a, b])
            return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
        else:
            return self._clahe.apply(image)

    def apply_unsharp_mask(self, image: np.ndarray, amount: float = 0.5, radius: int = 1) -> np.ndarray:
        """
        Gentle unsharp masking to clarify thin math dots and vowel marks.
        """
        if image is None or image.size == 0:
            return image

        ksize = (2 * radius + 1) | 1
        blurred = cv2.GaussianBlur(image, (ksize, ksize), 0)
        # unsharp = original + amount * (original - blurred)
        enhanced = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)
        return np.clip(enhanced, 0, 255).astype(np.uint8)

    def deskew_text(self, image: np.ndarray, max_angle: float = 10.0) -> Tuple[np.ndarray, float]:
        """
        Calculates and corrects subtle rotational skew using Hough line transform.
        """
        if image is None or image.size == 0:
            return image, 0.0

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

        if lines is None or len(lines) == 0:
            return image, 0.0

        angles = []
        for line in lines:
            pts = line.reshape(-1)
            if len(pts) < 4:
                continue
            x1, y1, x2, y2 = pts[:4]
            if x2 == x1:
                continue
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            if abs(angle) < max_angle:
                angles.append(angle)

        if not angles:
            return image, 0.0

        median_angle = float(np.median(angles))
        if abs(median_angle) < 0.2:
            return image, 0.0

        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        rot_mat = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(
            image,
            rot_mat,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )

        return rotated, median_angle
