"""
Shadow Removal & Gutter Shadow Compensation.
Mitigates book-spine gutter shadows and non-uniform illumination bands
in photographed book spreads while preserving faint Bengali diacritics.
"""

from typing import Tuple
import cv2
import numpy as np
from src.utils.logger import get_logger

logger = get_logger("ShadowRemoval")

class ShadowRemovalEngine:
    """Removes binding gutter shadows and localized lighting gradient anomalies."""

    def __init__(self, kernel_size: int = 51):
        self.kernel_size = kernel_size

    def remove_gutter_shadow(self, image: np.ndarray) -> np.ndarray:
        """
        Estimates and attenuates vertical shadow bands near book binding.
        """
        if image is None or image.size == 0:
            return image

        is_color = len(image.shape) == 3
        if is_color:
            # Work in LAB color space to modify L (luminance) channel only
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            target = l_channel
        else:
            target = image.copy()

        h, w = target.shape[:2]

        # Use large morphological dilation to estimate page background
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.kernel_size, self.kernel_size))
        dilated = cv2.dilate(target, kernel)
        # Apply median blur to smooth out residual text ghosting
        bg_estimate = cv2.medianBlur(dilated, 21)

        # Calculate difference (shadow intensity)
        diff = 255 - cv2.absdiff(target, bg_estimate)

        # Normalize difference to full range [0, 255]
        norm = cv2.normalize(diff, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        if is_color:
            # Merge back into LAB and convert to BGR
            # Blend normalized L with original L to preserve natural contrast
            blended_l = cv2.addWeighted(norm, 0.75, target, 0.25, 0)
            merged_lab = cv2.merge([blended_l, a_channel, b_channel])
            corrected = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)
            return corrected
        else:
            return cv2.addWeighted(norm, 0.75, target, 0.25, 0)

