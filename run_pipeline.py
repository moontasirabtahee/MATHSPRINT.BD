"""
Bangla Book Digitizer V2 - Master Execution Pipeline.
Processes all 800+ pages of the textbook end-to-end with high-DPI rendering,
physical photographed page correction, multi-key parallel OCR consensus,
AI Judge arbitration, SQLite persistence, and real-time Word (.docx) compilation.
"""

import sys
import gc
import asyncio
import hashlib
import argparse
from pathlib import Path
from typing import List, Optional
import pymupdf

from src.preprocessing.image_renderer import ImageRenderer
from src.preprocessing.preprocessing_selector import PreprocessingSelector
from src.orchestration.key_manager import KeyManager
from src.orchestration.cost_tracker import CostTracker
from src.storage.db import DatabaseManager
from src.storage.models import PageExtractionRecord
from src.extraction.parallel_worker import ParallelWorkerCoordinator
from src.reconstruction.docx_builder import DocxBuilder
from src.reconstruction.chapter_detector import ChapterDetector
from src.reconstruction.json_assembler import JSONAssembler
from src.reconstruction.figure_extractor import FigureExtractor
from src.layout.column_detector import ColumnDetector
from src.quality.report_generator import ReportGenerator
from src.utils.logger import get_logger

logger = get_logger("MasterPipeline")

def calculate_file_hash(filepath: Path) -> str:
    """Computes SHA-256 hash of the input document."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()[:16]

async def run_pipeline(
    pdf_path: str,
    start_page: Optional[int] = None,
    end_page: Optional[int] = None,
    batch_compile_interval: int = 10,
    resume: bool = True
) -> None:
    """
    Executes the book digitization pipeline across all pages in the PDF.
    """
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        logger.error(f"Source PDF not found at {pdf_file}")
        return

    # Inspect total page count of PDF
    doc = pymupdf.open(str(pdf_file))
    total_doc_pages = len(doc)
    doc.close()

    # Default to processing the entire document (1 .. total_doc_pages)
    start_p = 1 if start_page is None or start_page < 1 else start_page
    end_p = total_doc_pages if end_page is None or end_page > total_doc_pages else end_page

    logger.info(
        f"\n{'='*35} BANGLA BOOK DIGITIZER V2 {'='*35}\n"
        f"Target PDF: [{pdf_file.name}] (Total Pages in Book: {total_doc_pages})\n"
        f"Execution Scope: Page {start_p} to Page {end_p} ({end_p - start_p + 1} pages)\n"
        f"Resume Mode: {'ENABLED (Skipping verified pages)' if resume else 'DISABLED (Re-processing all)'}\n"
        f"{'='*96}"
    )

    pdf_hash = calculate_file_hash(pdf_file)

    # Initialize subsystems
    db = DatabaseManager(Path("output/digitizer.db"))
    key_manager = KeyManager(Path("config/keys.json"))
    cost_tracker = CostTracker()
    renderer = ImageRenderer(target_dpi=350)
    preprocessor = PreprocessingSelector(output_dir=Path("output/debug_variants"))
    coordinator = ParallelWorkerCoordinator(key_manager, db, cost_tracker)
    docx_builder = DocxBuilder(primary_font="Kalpurush", db=db)
    figure_extractor = FigureExtractor()
    column_detector = ColumnDetector()
    chapter_detector = ChapterDetector()
    json_assembler = JSONAssembler()
    report_gen = ReportGenerator()

    completed_page_numbers = set(db.get_completed_page_numbers()) if resume else set()
    logger.info(f"Database sync: {len(completed_page_numbers)} verified page(s) found in cache.")

    processed_records: List[PageExtractionRecord] = []

    # First load any existing completed records in the target range
    for p_num in range(start_p, end_p + 1):
        if resume and p_num in completed_page_numbers:
            cached_rec = db.get_page(p_num)
            if cached_rec:
                processed_records.append(cached_rec)

    newly_processed_since_save = 0

    def compile_active_chapter(current_records: List[PageExtractionRecord]) -> None:
        """Incrementally compiles only the active chapter in progress (O(1) time complexity)."""
        if not current_records:
            return
        sorted_records = sorted(current_records, key=lambda x: x.page_number)
        chapters = chapter_detector.partition_into_chapters(sorted_records)
        if chapters:
            active_idx = len(chapters)
            ch_title, ch_pages = chapters[-1]
            ch_path = Path("output/chapters") / f"chapter_{active_idx:03d}.docx"
            docx_builder.build_document(ch_pages, ch_path, title=f"Chapter {active_idx}: {ch_title}")
            logger.info(f"Incremental chapter compile: Chapter {active_idx} ({len(ch_pages)} pages) -> [{ch_path.name}]")

    def compile_master_deliverables(current_records: List[PageExtractionRecord]) -> None:
        """Compiles the complete master Word document, all chapters, master JSON, and HTML QA report."""
        # Query all completed pages from SQLite to ensure master deliverables always cover the entire book
        all_page_nums = sorted(list(db.get_completed_page_numbers()))
        all_records: List[PageExtractionRecord] = []
        if all_page_nums:
            for p in all_page_nums:
                rec = db.get_page(p)
                if rec:
                    all_records.append(rec)
        if not all_records:
            all_records = current_records

        if not all_records:
            return
        sorted_records = sorted(all_records, key=lambda x: x.page_number)
        logger.info(f"\nCompiling complete master deliverables ({len(sorted_records)} pages)...")

        # 1. Master JSON
        json_assembler.assemble_master_json(sorted_records)

        # 2. All Chapters
        chapters = chapter_detector.partition_into_chapters(sorted_records)
        for idx, (ch_title, ch_pages) in enumerate(chapters, start=1):
            ch_path = Path("output/chapters") / f"chapter_{idx:03d}.docx"
            docx_builder.build_document(ch_pages, ch_path, title=f"Chapter {idx}: {ch_title}")

        # 3. Master Full Book DOCX
        final_docx_path = Path("output/final_docx/Khairul_Basic_Math_Reconstructed.docx")
        docx_builder.build_document(sorted_records, final_docx_path, title="Khairul's Basic Math")

        # 4. QA HTML Report
        report_gen.generate_audit_report(sorted_records)

    # Main page processing loop
    for page_num in range(start_p, end_p + 1):
        if resume and page_num in completed_page_numbers:
            logger.info(f"Page {page_num:03d}/{end_p:03d} already completed in SQLite. Skipping OCR.")
            continue

        logger.info(f"\n--- [Page {page_num:03d} of {end_p:03d}] Processing ---")

        # 1. Render High-DPI Page Image
        raw_bgr = renderer.render_from_pdf(str(pdf_file), page_number=page_num)

        # 2. Advanced Physical Photographed-Page Preprocessing
        selected_img, selected_name, meta = preprocessor.process_page(
            original_image=raw_bgr,
            page_num=page_num,
            save_variants=True
        )

        # 3. CV-Driven Layout & Column Structure Analysis
        column_spans = column_detector.detect_columns(selected_img)
        layout_hint = None
        if len(column_spans) > 1:
            logger.info(f"Page {page_num:03d}: Multi-column layout detected ({len(column_spans)} columns: {column_spans})")
            layout_hint = (
                f"LAYOUT DIRECTIVE: Physical CV analysis detected {len(column_spans)} distinct columns on this page. "
                f"You MUST transcribe the entire left column (x-span: {column_spans[0]}) first in logical top-to-bottom reading order, "
                f"before transcribing the right column (x-span: {column_spans[1]}). Never interleave blocks between columns."
            )

        # 4. Dual-Pass Multi-Key OCR & Consensus Arbitration
        record = await coordinator.process_page_extraction(
            image=selected_img,
            page_number=page_num,
            source_pdf_hash=pdf_hash,
            selected_variant=selected_name,
            render_dpi=350,
            layout_hint=layout_hint
        )

        # 5. Extract & Enhance Diagrams / Figures
        record = figure_extractor.extract_figures_for_page(record, selected_img)

        processed_records.append(record)
        completed_page_numbers.add(page_num)
        newly_processed_since_save += 1

        # Periodic incremental active chapter save (O(1) time complexity)
        if newly_processed_since_save >= batch_compile_interval:
            compile_active_chapter(processed_records)
            newly_processed_since_save = 0

        # Memory cleanup
        del raw_bgr
        del selected_img
        gc.collect()

    # Final compilation of all pages
    if processed_records:
        compile_master_deliverables(processed_records)

        summary = cost_tracker.get_summary()
        logger.info(
            f"\n{'='*35} ALL PAGES COMPLETED {'='*35}\n"
            f"- Total Pages In Master Document: {len(processed_records)}\n"
            f"- Output Document: [cyan]output/final_docx/Khairul_Basic_Math_Reconstructed.docx[/cyan]\n"
            f"- Chapters: [cyan]output/chapters/[/cyan]\n"
            f"- Master Dataset: [cyan]output/final_json/textbook_master.json[/cyan]\n"
            f"- QA Audit Report: [cyan]output/reports/audit_report.html[/cyan]\n"
            f"- Cumulative Token Usage: {summary['total_tokens']:,} (Cost: ${summary['estimated_cost_usd']:.4f})\n"
            f"{'='*96}"
        )

def main():
    parser = argparse.ArgumentParser(description="Bangla Book Digitizer V2 Pipeline")
    parser.add_argument("--pdf", default="input/raw_pdf/Khairul.pdf", help="Source PDF textbook path")
    parser.add_argument("--start-page", type=int, default=1, help="Start page number (1-based, default: 1)")
    parser.add_argument("--end-page", type=int, default=None, help="End page number (1-based, default: all pages)")
    parser.add_argument("--batch-compile", type=int, default=10, help="Pages interval to re-compile deliverables")
    parser.add_argument("--no-resume", action="store_true", help="Do not skip completed pages")

    args = parser.parse_args()
    asyncio.run(run_pipeline(
        pdf_path=args.pdf,
        start_page=args.start_page,
        end_page=args.end_page,
        batch_compile_interval=args.batch_compile,
        resume=not args.no_resume
    ))

if __name__ == "__main__":
    main()
