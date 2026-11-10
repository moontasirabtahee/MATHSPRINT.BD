"""
Illumination Corrector.
Normalizes non-uniform page lighting across the scanned page using background
division modeling while strictly protecting mathematical signs and Bengali matras.
"""

from typing import Optional
import cv2
import numpy as np
from src.utils.logger import get_logger

logger = get_logger("IlluminationCorrector")

class IlluminationCorrector:
    """Normalizes uneven ambient illumination across photographed textbook pages."""

    def __init__(self, filter_size: int = 41):
        self.filter_size = filter_size

    def correct_illumination(self, image: np.ndarray) -> np.ndarray:
        """
        Applies background division illumination leveling.
        """
        if image is None or image.size == 0:
            return image

        is_color = len(image.shape) == 3
        if is_color:
            planes = cv2.split(image)
            normalized_planes = []
            for plane in planes:
                normalized_planes.append(self._normalize_plane(plane))
            return cv2.merge(normalized_planes)
        else:
            return self._normalize_plane(image)

    def _normalize_plane(self, plane: np.ndarray) -> np.ndarray:
        """Normalizes a single 8-bit channel using morphological background division."""
        # Estimate background illumination with large Gaussian blur
        ksize = self.filter_size | 1
        background = cv2.GaussianBlur(plane, (ksize, ksize), 0)

        # Avoid zero-division: clip background to minimum 1
        bg_float = np.maximum(background.astype(np.float32), 1.0)
        plane_float = plane.astype(np.float32)

        # Division: (plane / bg) * 255
        divided = (plane_float / bg_float) * 255.0
        clipped = np.clip(divided, 0, 255).astype(np.uint8)

        # Gentle blend with original to avoid washing out thin symbols
        result = cv2.addWeighted(clipped, 0.85, plane, 0.15, 0)
        return result

