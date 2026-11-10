"""
HTML Audit Report Generator.
Generates an interactive, side-by-side visual audit report comparing original
page crops, enhanced variants, extracted Bengali text, LaTeX formulas, and review flags.
"""

from pathlib import Path
from typing import List
import json
from src.storage.models import PageExtractionRecord
from src.utils.logger import get_logger

logger = get_logger("ReportGenerator")

class ReportGenerator:
    """Produces interactive HTML reports for visual quality assurance."""

    def __init__(self, output_dir: Path = Path("output/reports")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_audit_report(
        self,
        pages: List[PageExtractionRecord],
        output_file: str = "audit_report.html"
    ) -> Path:
        """Generates comprehensive HTML report."""
        report_path = self.output_dir / output_file

        rows_html = []
        for p in sorted(pages, key=lambda x: x.page_number):
            status_color = "#10B981" if p.status == "CONSENSUS_VERIFIED" else "#F59E0B"
            judge_badge = '<span class="badge badge-judge">Judge Invoked</span>' if p.metadata.get("judge_invoked") else ''

            blocks_html = []
            for b in p.blocks:
                math_badge = f'<span class="badge badge-math">${b.latex}$</span>' if b.latex else ''
                blocks_html.append(f"""
                <div class="block-item">
                    <span class="block-tag">{b.type} (Order: {b.reading_order})</span>
                    <p class="block-text">{b.text or ''}</p>
                    {math_badge}
                </div>
                """)

            rows_html.append(f"""
            <div class="page-card">
                <div class="card-header">
                    <h3>Page {p.page_number:03d} <span class="badge" style="background-color: {status_color}">{p.status}</span> {judge_badge}</h3>
                    <span>Tokens: {p.tokens_used} | Model: {p.ocr_engine}</span>
                </div>
                <div class="card-body">
                    <div class="image-panel">
                        <img src="../debug_variants/page_{p.page_number:03d}/final_selected.png" alt="Preprocessed Page" loading="lazy" />
                    </div>
                    <div class="content-panel">
                        {''.join(blocks_html)}
                    </div>
                </div>
            </div>
            """)

        html_content = f"""<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <title>Bangla Book Digitizer V2 - Quality Audit Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #F8FAFC; color: #1E293B; margin: 0; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ margin: 0; color: #0F172A; }}
        .page-card {{ background: white; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 24px; overflow: hidden; }}
        .card-header {{ background: #F1F5F9; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; }}
        .card-body {{ display: flex; flex-direction: row; gap: 20px; padding: 20px; }}
        .image-panel {{ flex: 1; max-width: 45%; }}
        .image-panel img {{ width: 100%; border-radius: 4px; border: 1px solid #CBD5E1; }}
        .content-panel {{ flex: 1; max-height: 800px; overflow-y: auto; padding-right: 10px; }}
        .block-item {{ margin-bottom: 12px; padding: 10px; background: #F8FAFC; border-left: 3px solid #3B82F6; border-radius: 4px; }}
        .block-tag {{ font-size: 11px; text-transform: uppercase; font-weight: bold; color: #64748B; }}
        .block-text {{ margin: 4px 0; font-size: 14px; line-height: 1.5; }}
        .badge {{ padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; color: white; }}
        .badge-judge {{ background: #8B5CF6; }}
        .badge-math {{ background: #E0E7FF; color: #3730A3; font-family: 'Cambria Math', monospace; display: inline-block; padding: 2px 6px; border-radius: 4px; margin-top: 4px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Bangla Book Digitizer V2 — QA Audit Report</h1>
        <p>Total Pages Audited: {len(pages)} | Source: Khairul.pdf</p>
    </div>
    {''.join(rows_html)}
</body>
</html>
"""
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Audit report generated at [{report_path}]")
        return report_path

