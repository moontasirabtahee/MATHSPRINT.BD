"""
Perspective Corrector.
Warps detected 4-point page boundaries into an upright, rectangular planar view.
"""

from typing import Optional
import cv2
import numpy as np
from src.utils.logger import get_logger

logger = get_logger("PerspectiveCorrector")

class PerspectiveCorrector:
    """Applies four-point perspective transformation to correct camera angle distortion."""

    def correct_perspective(self, image: np.ndarray, pts: np.ndarray) -> np.ndarray:
        """
        Warps image quadrilateral defined by pts into a planar rectangle.
        pts: np.ndarray of shape (4, 2) ordered [tl, tr, br, bl].
        """
        if pts is None or len(pts) != 4:
            logger.warning("Invalid points passed to correct_perspective, returning original image")
            return image

        tl, tr, br, bl = pts

        # Compute width of new image
        width_a = np.linalg.norm(br - bl)
        width_b = np.linalg.norm(tr - tl)
        max_width = max(int(width_a), int(width_b))

        # Compute height of new image
        height_a = np.linalg.norm(tr - br)
        height_b = np.linalg.norm(tl - bl)
        max_height = max(int(height_a), int(height_b))

        if max_width <= 0 or max_height <= 0:
            logger.warning("Computed invalid dimensions in perspective correction")
            return image

        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]
        ], dtype=np.float32)

        transform_matrix = cv2.getPerspectiveTransform(pts.astype(np.float32), dst)
        warped = cv2.warpPerspective(
            image,
            transform_matrix,
            (max_width, max_height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )

        return warped

