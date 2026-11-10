"""
Page Boundary Detector.
Detects physical page boundaries in photographed textbook pages using OpenCV
contour analysis, convex hull, and geometric filtering.
"""

from typing import Optional, Tuple
import cv2
import numpy as np
from src.utils.logger import get_logger

logger = get_logger("PageBoundaryDetector")

class PageBoundaryDetector:
    """Detects document boundary coordinates in photographed page images."""

    def __init__(self, min_area_ratio: float = 0.50, max_area_ratio: float = 0.99):
        self.min_area_ratio = min_area_ratio
        self.max_area_ratio = max_area_ratio

    def detect_boundary(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detects 4-corner polygon bounding the physical book page.
        Returns:
            np.ndarray of shape (4, 2) with points [top-left, top-right, bottom-right, bottom-left],
            or None if no confident boundary is detected.
        """
        if image is None or image.size == 0:
            logger.warning("Empty image passed to detect_boundary")
            return None

        h, w = image.shape[:2]
        total_area = float(h * w)

        # Scale down for robust contour search
        max_dim = 1200
        scale = 1.0
        if max(h, w) > max_dim:
            scale = max_dim / float(max(h, w))
            resized = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        else:
            resized = image.copy()

        # Convert to grayscale
        if len(resized.shape) == 3:
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        else:
            gray = resized

        # Bilateral filter to smooth background texture while keeping edges sharp
        blurred = cv2.bilateralFilter(gray, 9, 75, 75)

        # Edge detection with Otsu threshold guidance
        otsu_val, _ = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        canny_low = 0.5 * otsu_val
        canny_high = otsu_val
        edges = cv2.Canny(blurred, int(canny_low), int(canny_high))

        # Morphological close to bridge edge gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, _ = cv2.findContours(closed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        # Sort contours by area descending
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        for cnt in contours[:5]:
            area = cv2.contourArea(cnt)
            area_ratio = area / (resized.shape[0] * resized.shape[1])
            if area_ratio < self.min_area_ratio or area_ratio > self.max_area_ratio:
                continue

            perimeter = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)

            if len(approx) == 4:
                pts = approx.reshape(4, 2).astype(np.float32)
                # Rescale back to original image coordinates
                pts /= scale
                return self._order_points(pts)

            # Fallback to convex hull if approximate polygon has 5-8 vertices
            hull = cv2.convexHull(cnt)
            hull_peri = cv2.arcLength(hull, True)
            hull_approx = cv2.approxPolyDP(hull, 0.03 * hull_peri, True)
            if len(hull_approx) == 4:
                pts = hull_approx.reshape(4, 2).astype(np.float32)
                pts /= scale
                return self._order_points(pts)

        return None

    @staticmethod
    def _order_points(pts: np.ndarray) -> np.ndarray:
        """
        Orders coordinates: [top-left, top-right, bottom-right, bottom-left].
        """
        rect = np.zeros((4, 2), dtype=np.float32)
        # Sum: top-left has smallest sum, bottom-right has largest sum
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # Diff: top-right has smallest diff (x - y), bottom-left has largest diff
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect

