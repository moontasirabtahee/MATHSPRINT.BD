"""
Chapter Detector.
Identifies chapter boundaries from heading blocks and page metadata to enable
modular chapter-by-chapter document compilation.
"""

from typing import List, Dict, Tuple
from src.storage.models import PageExtractionRecord
from src.utils.logger import get_logger

logger = get_logger("ChapterDetector")

class ChapterDetector:
    """Partitions textbook pages into logical chapters."""

    CHAPTER_KEYWORDS = ["অধ্যায়", "chapter", "পার্ট", "খণ্ড", "পরিমাপ", "সংখ্যা", "পাটিগণিত", "বীজগণিত", "জ্যামিতি"]

    def partition_into_chapters(
        self,
        pages: List[PageExtractionRecord]
    ) -> List[Tuple[str, List[PageExtractionRecord]]]:
        """
        Groups pages into chapter buckets [(chapter_title, [page_records...]), ...].
        """
        if not pages:
            return []

        sorted_pages = sorted(pages, key=lambda p: p.page_number)
        chapters: List[Tuple[str, List[PageExtractionRecord]]] = []

        current_title = "Chapter_01"
        current_pages: List[PageExtractionRecord] = []

        for page in sorted_pages:
            # Check if this page contains a primary chapter heading
            found_new_chapter = False
            for block in page.blocks:
                if block.type == "heading_1" and block.text:
                    cleaned_heading = block.text.strip()
                    if any(kw in cleaned_heading.lower() for kw in self.CHAPTER_KEYWORDS) or len(current_pages) >= 50:
                        if current_pages:
                            chapters.append((current_title, current_pages))
                            current_pages = []
                        current_title = cleaned_heading
                        found_new_chapter = True
                        break

            current_pages.append(page)

        if current_pages:
            chapters.append((current_title, current_pages))

        logger.info(f"Partitioned {len(sorted_pages)} page(s) into {len(chapters)} chapter(s)")
        return chapters

