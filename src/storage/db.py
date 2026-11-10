"""
SQLite Database and Persistence Manager.
Provides ACID transactions, crash recovery, and idempotent state persistence
for 800+ page textbook processing runs.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from src.storage.models import PageExtractionRecord, ContentBlock
from src.utils.logger import get_logger

logger = get_logger("StorageDB")

class DatabaseManager:
    """Manages SQLite state storage for pages, blocks, and quota tracking."""

    def __init__(self, db_path: Path = Path("output/digitizer.db")):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns SQLite connection with WAL mode enabled for concurrent reads."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_schema(self) -> None:
        """Initializes tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pages (
                page_number INTEGER PRIMARY KEY,
                source_pdf_hash TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                render_dpi INTEGER DEFAULT 350,
                selected_variant TEXT,
                ocr_engine TEXT,
                tokens_used INTEGER DEFAULT 0,
                estimated_cost_usd REAL DEFAULT 0.0,
                review_required BOOLEAN DEFAULT 0,
                processed_at TEXT,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS page_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_id TEXT NOT NULL,
                page_number INTEGER NOT NULL,
                type TEXT NOT NULL,
                reading_order INTEGER NOT NULL,
                text TEXT,
                latex TEXT,
                confidence REAL DEFAULT 1.0,
                review_required BOOLEAN DEFAULT 0,
                raw_json TEXT NOT NULL,
                FOREIGN KEY(page_number) REFERENCES pages(page_number) ON DELETE CASCADE
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS quota_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                credential_alias TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                input_tokens INTEGER,
                output_tokens INTEGER,
                http_status INTEGER,
                latency_ms REAL
            );
            """)
            conn.commit()

    def upsert_page(self, record: PageExtractionRecord) -> None:
        """Atomically inserts or updates a page record and its constituent blocks."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Upsert into pages table
            cursor.execute("""
            INSERT INTO pages (
                page_number, source_pdf_hash, status, render_dpi,
                selected_variant, ocr_engine, tokens_used, estimated_cost_usd,
                review_required, processed_at, metadata_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(page_number) DO UPDATE SET
                source_pdf_hash = excluded.source_pdf_hash,
                status = excluded.status,
                render_dpi = excluded.render_dpi,
                selected_variant = excluded.selected_variant,
                ocr_engine = excluded.ocr_engine,
                tokens_used = excluded.tokens_used,
                estimated_cost_usd = excluded.estimated_cost_usd,
                review_required = excluded.review_required,
                processed_at = excluded.processed_at,
                metadata_json = excluded.metadata_json,
                updated_at = CURRENT_TIMESTAMP;
            """, (
                record.page_number,
                record.source_pdf_hash,
                record.status,
                record.render_dpi,
                record.selected_variant,
                record.ocr_engine,
                record.tokens_used,
                record.estimated_cost_usd,
                1 if any(b.review_required for b in record.blocks) else 0,
                record.processed_at,
                json.dumps(record.metadata, ensure_ascii=False)
            ))

            # Delete existing blocks for this page to replace cleanly
            cursor.execute("DELETE FROM page_blocks WHERE page_number = ?", (record.page_number,))

            # Insert current blocks
            for block in record.blocks:
                cursor.execute("""
                INSERT INTO page_blocks (
                    block_id, page_number, type, reading_order, text,
                    latex, confidence, review_required, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    block.block_id,
                    record.page_number,
                    block.type,
                    block.reading_order,
                    block.text,
                    block.latex,
                    block.confidence,
                    1 if block.review_required else 0,
                    block.model_dump_json()
                ))

            conn.commit()

    def get_page(self, page_number: int) -> Optional[PageExtractionRecord]:
        """Retrieves and rehydrates a page record with its blocks from SQLite."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pages WHERE page_number = ?", (page_number,))
            row = cursor.fetchone()
            if not row:
                return None

            cursor.execute(
                "SELECT raw_json FROM page_blocks WHERE page_number = ? ORDER BY reading_order ASC",
                (page_number,)
            )
            block_rows = cursor.fetchall()
            blocks = [ContentBlock.model_validate_json(b["raw_json"]) for b in block_rows]

            metadata = json.loads(row["metadata_json"]) if row["metadata_json"] else {}

            return PageExtractionRecord(
                page_number=row["page_number"],
                source_pdf_hash=row["source_pdf_hash"],
                status=row["status"],
                render_dpi=row["render_dpi"],
                selected_variant=row["selected_variant"],
                blocks=blocks,
                ocr_engine=row["ocr_engine"],
                tokens_used=row["tokens_used"],
                estimated_cost_usd=row["estimated_cost_usd"],
                processed_at=row["processed_at"] or "",
                metadata=metadata
            )

    def get_completed_page_numbers(self) -> List[int]:
        """Returns set of page numbers already processed and saved in database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT page_number FROM pages WHERE status IN ('COMPLETED', 'CONSENSUS_VERIFIED', 'NEEDS_REVIEW')")
            return [row["page_number"] for row in cursor.fetchall()]

    def get_all_pages(self) -> List[PageExtractionRecord]:
        """Returns all completed pages sorted by page number."""
        page_nums = sorted(self.get_completed_page_numbers())
        pages = []
        for p in page_nums:
            rec = self.get_page(p)
            if rec:
                pages.append(rec)
        return pages

    def flag_page_needs_review(self, page_number: int, reason: str, block_id: Optional[str] = None) -> None:
        """Flags a page and block as requiring human review in SQLite when a fallback occurs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pages SET review_required = 1, status = 'NEEDS_REVIEW' WHERE page_number = ?",
                (page_number,)
            )
            if block_id:
                cursor.execute(
                    "UPDATE page_blocks SET review_required = 1 WHERE block_id = ?",
                    (block_id,)
                )
            conn.commit()
            logger.info(f"Page {page_number:03d}: Flagged review_required=True in SQLite (Reason: {reason})")

    def record_quota_audit(
        self,
        project_id: str,
        credential_alias: str,
        endpoint: str,
        input_tokens: int,
        output_tokens: int,
        http_status: int,
        latency_ms: float
    ) -> None:
        """Logs each API transaction for quota and cost monitoring."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO quota_audit (
                project_id, credential_alias, endpoint, input_tokens,
                output_tokens, http_status, latency_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id, credential_alias, endpoint, input_tokens,
                output_tokens, http_status, latency_ms
            ))
            conn.commit()
