"""
Parallel Extraction Worker & Consensus Coordinator.
Executes dual-pass extraction across distinct Google AI Studio project credentials,
validates syntax, triggers AI Judge arbitration, and commits results to SQLite and JSON checkpoints.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np

from src.extraction.gemini_client import GeminiClient
from src.orchestration.key_manager import KeyManager
from src.orchestration.cost_tracker import CostTracker
from src.orchestration.retry_manager import RetryManager
from src.validation.latex_validator import LaTeXValidator
from src.validation.diff_engine import DiffEngine
from src.validation.ai_judge import AIJudge
from src.storage.models import PageExtractionRecord, ContentBlock, MathExpression, TableData
from src.storage.db import DatabaseManager
from src.extraction.prompts import EXTRACTION_SYSTEM_PROMPT
from src.utils.logger import get_logger

logger = get_logger("ParallelWorker")

class ParallelWorkerCoordinator:
    """Orchestrates dual-pass extractions and consensus verification per page."""

    def __init__(
        self,
        key_manager: KeyManager,
        db_manager: DatabaseManager,
        cost_tracker: CostTracker,
        checkpoint_dir: Path = Path("output/checkpoints")
    ):
        self.key_manager = key_manager
        self.db = db_manager
        self.cost_tracker = cost_tracker
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.client = GeminiClient(model_name="gemini-3.1-flash-lite")
        self.retry_manager = RetryManager(max_retries=7, base_delay=3.0, max_delay=60.0)
        self.latex_validator = LaTeXValidator()
        self.diff_engine = DiffEngine()
        self.ai_judge = AIJudge(self.client)

    async def process_page_extraction(
        self,
        image: np.ndarray,
        page_number: int,
        source_pdf_hash: str,
        selected_variant: str = "final_selected.png",
        render_dpi: int = 350,
        layout_hint: Optional[str] = None
    ) -> PageExtractionRecord:
        """
        Executes Dual-Pass extraction on the preprocessed page, arbitrates if needed,
        and commits the validated record.
        """
        logger.info(f"Initiating Dual-Pass OCR extraction for Page {page_number:03d}...")

        # 1. Acquire two distinct credentials from separate project scopes
        cred_a = await self.key_manager.acquire_key()
        cred_b = await self.key_manager.acquire_key(exclude_alias=cred_a.alias)

        logger.info(
            f"Page {page_number:03d}: Assigned Worker A -> [{cred_a.alias}], "
            f"Worker B -> [{cred_b.alias}]"
        )

        prompt_to_use = f"{EXTRACTION_SYSTEM_PROMPT}\n\n### SPATIAL LAYOUT INSTRUCTION:\n{layout_hint}" if layout_hint else None

        async def run_worker(cred):
            try:
                res = await self.client.extract_page(
                    image=image,
                    api_key=cred.key,
                    credential_alias=cred.alias,
                    custom_prompt=prompt_to_use
                )
                await self.key_manager.report_success(cred.alias, res["input_tokens"] + res["output_tokens"])
                self.cost_tracker.add_usage(res["input_tokens"], res["output_tokens"])
                self.db.record_quota_audit(
                    project_id=cred.project_name,
                    credential_alias=cred.alias,
                    endpoint="generate_content",
                    input_tokens=res["input_tokens"],
                    output_tokens=res["output_tokens"],
                    http_status=200,
                    latency_ms=res["latency_seconds"] * 1000.0
                )
                return res
            except Exception as e:
                err_str = str(e)
                if "429" in err_str:
                    await self.key_manager.report_rate_limit(cred.alias)
                elif "403" in err_str or "PERMISSION_DENIED" in err_str:
                    await self.key_manager.report_disabled(cred.alias, str(e))
                raise

        # 2. Run dual extractions concurrently
        task_a = self.retry_manager.execute_with_retry(lambda: run_worker(cred_a), f"Worker A ({cred_a.alias})")
        task_b = self.retry_manager.execute_with_retry(lambda: run_worker(cred_b), f"Worker B ({cred_b.alias})")

        res_a, res_b = await asyncio.gather(task_a, task_b)

        blocks_a = res_a.get("parsed_blocks", [])
        blocks_b = res_b.get("parsed_blocks", [])

        # 3. Compare extractions and calculate similarity
        similarity, discrepancies = self.diff_engine.compare_blocks(blocks_a, blocks_b)
        logger.info(f"Page {page_number:03d}: Worker A vs B Similarity = {similarity:.4f}")

        # 4. Check if AI Judge arbitration is required
        needs_judge = similarity < 0.98 or bool(discrepancies)
        final_raw_blocks: List[Dict[str, Any]] = []

        if needs_judge:
            reason = f"Similarity {similarity:.4f} < 0.98" if similarity < 0.98 else f"{len(discrepancies)} discrepancy item(s)"
            logger.warning(
                f"Page {page_number:03d}: Consensus threshold not met ({reason}). "
                f"Escalating to AI Judge..."
            )
            cred_judge = await self.key_manager.acquire_key()
            try:
                final_raw_blocks = await self.ai_judge.arbitrate(
                    image=image,
                    api_key=cred_judge.key,
                    credential_alias=cred_judge.alias,
                    extraction_a=res_a,
                    extraction_b=res_b,
                    discrepancies=discrepancies
                )
                await self.key_manager.report_success(cred_judge.alias)
            except Exception as e:
                logger.error(f"AI Judge arbitration failed: {e}. Falling back to Worker A.")
                final_raw_blocks = blocks_a
        else:
            final_raw_blocks = blocks_a

        # 5. Validate all LaTeX expressions and instantiate strongly typed ContentBlocks
        content_blocks: List[ContentBlock] = []
        for idx, raw_b in enumerate(final_raw_blocks, start=1):
            raw_type = str(raw_b.get("type", "paragraph")).lower().strip()
            if raw_type in ("header", "footer", "running_header", "page_number"):
                block_type = "footer_or_header"
            elif raw_type in ("heading", "title", "chapter_title"):
                block_type = "heading_1"
            elif raw_type in ("exercise", "question", "mcq"):
                block_type = "exercise_item"
            elif raw_type in ("solution", "answer"):
                block_type = "solution_block"
            elif raw_type in ("note", "callout", "box", "tip"):
                block_type = "callout_box"
            elif raw_type in ("math", "equation", "formula"):
                block_type = "math_block"
            elif raw_type in (
                "heading_1", "heading_2", "heading_3", "paragraph",
                "math_block", "table", "figure", "caption",
                "exercise_item", "solution_block", "callout_box",
                "footer_or_header"
            ):
                block_type = raw_type
            else:
                block_type = "paragraph"

            text_val = raw_b.get("text", "")
            latex_val = raw_b.get("latex")

            math_expressions: List[MathExpression] = []
            if latex_val:
                is_valid, err_msg = self.latex_validator.validate_expression(latex_val)
                math_expressions.append(
                    MathExpression(
                        latex=latex_val,
                        is_display=(block_type == "math_block"),
                        syntax_valid=is_valid,
                        validation_error=err_msg
                    )
                )

            raw_id = raw_b.get("block_id", f"b{idx:02d}")
            # Ensure globally unique block id prefixed with page number
            block_id = f"p{page_number}_{raw_id}" if not raw_id.startswith(f"p{page_number}_") else raw_id

            raw_lang = str(raw_b.get("language") or "bn").lower().strip()
            lang = raw_lang if raw_lang in ("bn", "en", "mixed") else "bn"

            table_dict = raw_b.get("table_data")
            table_obj = None
            if table_dict and isinstance(table_dict, dict):
                try:
                    table_obj = TableData(**table_dict)
                except Exception:
                    pass

            cb = ContentBlock(
                block_id=block_id,
                type=block_type,
                reading_order=raw_b.get("reading_order", idx),
                language=lang,
                text=text_val,
                latex=latex_val,
                math_expressions=math_expressions,
                table_data=table_obj,
                confidence=1.0 if not needs_judge else 0.95,
                review_required=raw_b.get("review_required", False)
            )
            content_blocks.append(cb)

        # 6. Build the master PageExtractionRecord
        total_tokens = (res_a["input_tokens"] + res_a["output_tokens"] +
                        res_b["input_tokens"] + res_b["output_tokens"])

        record = PageExtractionRecord(
            page_number=page_number,
            source_pdf_hash=source_pdf_hash,
            status="CONSENSUS_VERIFIED" if not needs_judge else "NEEDS_REVIEW",
            render_dpi=render_dpi,
            selected_variant=selected_variant,
            blocks=content_blocks,
            ocr_engine="gemini-3.1-flash-lite",
            tokens_used=total_tokens,
            estimated_cost_usd=self.cost_tracker.total_cost_usd,
            processed_at=datetime.utcnow().isoformat(),
            metadata={
                "similarity_score": similarity,
                "discrepancies": discrepancies,
                "judge_invoked": needs_judge,
                "worker_a": cred_a.alias,
                "worker_b": cred_b.alias
            }
        )

        # 7. Persist to SQLite
        self.db.upsert_page(record)

        # 8. Commit local checkpoint JSON
        checkpoint_path = self.checkpoint_dir / f"page_{page_number:03d}.json"
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            f.write(record.model_dump_json(indent=2))

        logger.info(
            f"Page {page_number:03d} complete! Committed {len(content_blocks)} blocks "
            f"to SQLite and checkpoint [{checkpoint_path.name}]"
        )

        return record
