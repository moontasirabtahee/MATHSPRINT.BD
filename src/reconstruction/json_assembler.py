"""
Master JSON Assembler.
Aggregates validated page extraction records into a consolidated textbook dataset.
"""

import json
from pathlib import Path
from typing import List
from src.storage.models import PageExtractionRecord
from src.utils.logger import get_logger

logger = get_logger("JSONAssembler")

class JSONAssembler:
    """Consolidates page extraction records into a validated master JSON file."""

    def assemble_master_json(
        self,
        pages: List[PageExtractionRecord],
        output_path: Path = Path("output/final_json/textbook_master.json")
    ) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sorted_pages = sorted(pages, key=lambda p: p.page_number)

        master_data = {
            "title": "Khairul's Basic Math",
            "total_pages": len(sorted_pages),
            "pages": [p.model_dump() for p in sorted_pages]
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Master textbook JSON assembled successfully at [{output_path}]")
        return output_path

