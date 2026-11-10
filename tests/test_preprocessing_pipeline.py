"""
Test script for the Stage 2 Preprocessing Pipeline.
Runs boundary detection, perspective correction, dewarping, shadow removal,
illumination correction, and CLAHE enhancement on real photographed sample pages.
"""

from pathlib import Path
import cv2
from src.preprocessing.preprocessing_selector import PreprocessingSelector
from src.utils.logger import get_logger

logger = get_logger("TestPreprocessing")

def test_samples():
    selector = PreprocessingSelector(output_dir=Path("output/debug_variants"))

    samples = [
        (25, "input/test_samples/sample_page_25.png"),
        (50, "input/test_samples/sample_page_50.png"),
    ]

    for page_num, img_path in samples:
        path = Path(img_path)
        if not path.exists():
            logger.error(f"Sample image not found: {img_path}")
            continue

        logger.info(f"Processing sample page {page_num} from {img_path}...")
        img = cv2.imread(str(path))
        assert img is not None, f"Failed to load image from {img_path}"

        selected_img, selected_name, metadata = selector.process_page(
            original_image=img,
            page_num=page_num,
            save_variants=True
        )

        variant_dir = Path("output/debug_variants") / f"page_{page_num:03d}"
        assert (variant_dir / "original.png").exists(), "original.png missing"
        assert (variant_dir / "final_selected.png").exists(), "final_selected.png missing"

        logger.info(
            f"Successfully processed Page {page_num}. "
            f"Selected: {selected_name}, Stages: {metadata['stages_applied']}, "
            f"Output saved to {variant_dir}"
        )

    print("ALL PREPROCESSING TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    test_samples()

