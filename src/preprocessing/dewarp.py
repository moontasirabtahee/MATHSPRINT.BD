"""
Dewarping Engine.
Conservative geometric dewarping module that rectifies binding curvature near the
gutter margin using smooth polynomial modeling while preventing artificial wave ripples.
"""

from typing import Tuple
import cv2
import numpy as np
from src.utils.logger import get_logger

logger = get_logger("DewarpEngine")

class DewarpEngine:
    """Estimates and rectifies gutter curvature near the book spine."""

    def __init__(self, gutter_width_ratio: float = 0.20, max_displacement_px: int = 35):
        self.gutter_width_ratio = gutter_width_ratio
        self.max_displacement_px = max_displacement_px

    def dewarp(self, image: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Rectifies curvature strictly near the spine/gutter using a smooth polynomial curve.
        Returns:
            Tuple[np.ndarray, bool]: (dewarped_image, was_dewarped)
        """
        if image is None or image.size == 0:
            return image, False

        h, w = image.shape[:2]
        if w < 300 or h < 300:
            return image, False

        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Detect the spine side (left gutter is typical for scanned single pages with binding shadow)
        # Compare left 10% vs right 10% mean darkness
        left_mean = float(np.mean(gray[:, : int(w * 0.10)]))
        right_mean = float(np.mean(gray[:, int(w * 0.90) :]))

        # The darker edge with shadow is the gutter
        gutter_on_left = left_mean < right_mean

        # Find header rule line or text-line boundary at top margin
        # Search in top 15%
        top_strip = gray[: int(h * 0.15), :]
        edges = cv2.Canny(top_strip, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=int(w * 0.3), maxLineGap=20)

        if lines is None or len(lines) == 0:
            # No reference horizontal rule found to reliably gauge curvature
            logger.debug("No reference line found in header margin; skipping dewarp")
            return image, False

        # Extract line points
        line_pts = []
        for line in lines:
            pts = line.reshape(-1)[:4]
            x1, y1, x2, y2 = pts
            if abs(y2 - y1) < 40:  # near-horizontal line
                line_pts.append((x1, y1))
                line_pts.append((x2, y2))

        if len(line_pts) < 4:
            return image, False

        line_pts = sorted(line_pts, key=lambda p: p[0])
        xs = np.array([p[0] for p in line_pts], dtype=np.float32)
        ys = np.array([p[1] for p in line_pts], dtype=np.float32)

        # Fit a 2nd-degree polynomial: y = ax^2 + bx + c
        try:
            poly = np.polyfit(xs, ys, deg=2)
        except Exception:
            return image, False

        # Evaluate curvature derivative: |2a|
        a = poly[0]
        if abs(a) < 1e-6:
            # Negligible curvature
            return image, False

        # Compute vertical displacement profile across page width
        x_all = np.arange(w, dtype=np.float32)
        curve_y = poly[0] * (x_all ** 2) + poly[1] * x_all + poly[2]
        # Reference baseline is the flat section away from the gutter
        if gutter_on_left:
            baseline_y = curve_y[int(w * 0.70)]
        else:
            baseline_y = curve_y[int(w * 0.30)]

        disp_y = curve_y - baseline_y

        # Restrict displacement to the gutter region using a smooth taper
        gutter_w = int(w * self.gutter_width_ratio)
        taper = np.ones(w, dtype=np.float32)
        if gutter_on_left:
            taper[gutter_w:] = 0.0
            taper[:gutter_w] = 0.5 * (1.0 + np.cos(np.pi * np.arange(gutter_w) / gutter_w))
        else:
            taper[: w - gutter_w] = 0.0
            taper[w - gutter_w :] = 0.5 * (1.0 - np.cos(np.pi * np.arange(gutter_w) / gutter_w))

        smooth_disp_y = disp_y * taper
        smooth_disp_y = np.clip(smooth_disp_y, -self.max_displacement_px, self.max_displacement_px)

        if np.max(np.abs(smooth_disp_y)) < 3.0:
            return image, False

        # Construct smooth displacement map
        grid_x, grid_y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        map_y = grid_y - smooth_disp_y.reshape(1, w)
        map_x = grid_x

        dewarped = cv2.remap(
            image,
            map_x.astype(np.float32),
            map_y.astype(np.float32),
            interpolation=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )

        return dewarped, True
