"""
Preprocessing Selector.
Orchestrates the multi-stage visual enhancement pipeline, generates versioned variants,
evaluates image fidelity metrics, and selects the optimal version for OCR extraction.
"""

from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import cv2
import numpy as np
from src.preprocessing.page_boundary_detector import PageBoundaryDetector
from src.preprocessing.perspective_corrector import PerspectiveCorrector
from src.preprocessing.dewarp import DewarpEngine
from src.preprocessing.shadow_removal import ShadowRemovalEngine
from src.preprocessing.illumination_corrector import IlluminationCorrector
from src.preprocessing.image_enhancer import ImageEnhancer
from src.utils.logger import get_logger

logger = get_logger("PreprocessingSelector")

class PreprocessingSelector:
    """Orchestrates image corrections, saves intermediate variants, and selects the final render."""

    def __init__(self, output_dir: Path = Path("output/debug_variants")):
        self.output_dir = output_dir
        self.boundary_detector = PageBoundaryDetector()
        self.perspective_corrector = PerspectiveCorrector()
        self.dewarp_engine = DewarpEngine()
        self.shadow_engine = ShadowRemovalEngine()
        self.illumination_corrector = IlluminationCorrector()
        self.enhancer = ImageEnhancer()

    def process_page(
        self,
        original_image: np.ndarray,
        page_num: int,
        save_variants: bool = True
    ) -> Tuple[np.ndarray, str, Dict[str, Any]]:
        """
        Executes multi-stage physical photo correction pipeline.
        Returns:
            Tuple[selected_image, selected_variant_name, metadata]
        """
        page_dir = self.output_dir / f"page_{page_num:03d}"
        if save_variants:
            page_dir.mkdir(parents=True, exist_ok=True)

        variants: Dict[str, np.ndarray] = {}
        metadata: Dict[str, Any] = {"page_number": page_num, "stages_applied": []}

        # 1. Original
        variants["original.png"] = original_image
        if save_variants:
            cv2.imwrite(str(page_dir / "original.png"), original_image)

        # 2. Page Boundary & Perspective Correction
        boundary = self.boundary_detector.detect_boundary(original_image)
        if boundary is not None:
            rectified = self.perspective_corrector.correct_perspective(original_image, boundary)
            variants["perspective_corrected.png"] = rectified
            metadata["stages_applied"].append("perspective_corrected")
            current = rectified
            if save_variants:
                cv2.imwrite(str(page_dir / "perspective_corrected.png"), rectified)
        else:
            current = original_image

        # 3. Text-Line Curvature Dewarping
        dewarped, was_dewarped = self.dewarp_engine.dewarp(current)
        if was_dewarped:
            variants["dewarped.png"] = dewarped
            metadata["stages_applied"].append("dewarped")
            current = dewarped
            if save_variants:
                cv2.imwrite(str(page_dir / "dewarped.png"), dewarped)

        # 4. Gutter Shadow & Illumination Correction
        shadow_removed = self.shadow_engine.remove_gutter_shadow(current)
        illum_corrected = self.illumination_corrector.correct_illumination(shadow_removed)
        variants["illumination_corrected.png"] = illum_corrected
        metadata["stages_applied"].append("illumination_corrected")
        current = illum_corrected
        if save_variants:
            cv2.imwrite(str(page_dir / "illumination_corrected.png"), illum_corrected)

        # 5. Bengali-safe CLAHE & Unsharp Masking
        clahe_img = self.enhancer.apply_clahe(current)
        sharp_img = self.enhancer.apply_unsharp_mask(clahe_img, amount=0.35, radius=1)
        deskewed_img, angle = self.enhancer.deskew_text(sharp_img)
        variants["clahe.png"] = deskewed_img
        metadata["stages_applied"].append("clahe_enhanced")
        metadata["deskew_angle"] = angle
        if save_variants:
            cv2.imwrite(str(page_dir / "clahe.png"), deskewed_img)

        # 6. Automatic Variant Evaluation
        selected_name, selected_img = self._select_optimal_variant(variants)
        variants["final_selected.png"] = selected_img
        metadata["selected_variant"] = selected_name

        if save_variants:
            cv2.imwrite(str(page_dir / "final_selected.png"), selected_img)

        logger.info(
            f"Page {page_num:03d} preprocessed successfully. "
            f"Selected variant: [bold green]{selected_name}[/bold green]"
        )

        return selected_img, selected_name, metadata

    def _select_optimal_variant(self, variants: Dict[str, np.ndarray]) -> Tuple[str, np.ndarray]:
        """
        Calculates sharpness (Laplacian variance) and contrast entropy to choose
        between illumination-corrected, CLAHE-enhanced, or original image.
        """
        scores: Dict[str, float] = {}

        for name, img in variants.items():
            if name.startswith("final"):
                continue
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img

            # Edge sharpness metric: Laplacian variance
            lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()

            # Dynamic range / contrast: standard deviation of intensities
            std_dev = float(np.std(gray))

            # Composite score: balance sharpness with reasonable contrast
            # Penalize over-saturation / extreme variance that indicates noisy grain
            normalized_lap = min(lap_var / 500.0, 2.0)
            normalized_std = min(std_dev / 50.0, 2.0)
            composite_score = (0.6 * normalized_lap) + (0.4 * normalized_std)

            scores[name] = composite_score

        # Pick variant with highest balanced score, preferring enhanced versions
        best_name = max(scores, key=lambda k: scores[k])
        return best_name, variants[best_name]

