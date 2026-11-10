# BANGLA BOOK DIGITIZER V2: ARCHITECTURAL BLUEPRINT
## Production-Grade 800-Page Bengali, English & Mathematics Book Digitization System

---

## 1. Executive Summary & Design Tenets

The **Bangla Book Digitizer V2** is an industrial-grade document intelligence and document reconstruction system designed to ingest photographed textbook volumes (such as *Khairul's Basic Math*, ~882 photographed pages) and generate:
1. A reflowable, professionally styled Microsoft Word (`.docx`) document with native editable Office Math Markup Language (OMML) equations, native formatted tables, and embedded figure crops.
2. Chapter-wise modular Word documents (`output/chapters/chapter_XXX.docx`).
3. Strongly-typed, validated JSON datasets for every page validated by Pydantic.
4. An interactive HTML visual quality audit report highlighting discrepancies, OCR confidence, and AI Judge consensus decisions.

### Core Non-Negotiable Axioms
- **Fidelity Over Speed**: Mathematical notation (subscripts, superscripts, fractions, $\therefore$, $\pm$, matrices) and Bengali phonetic diacritics (হসন্ত, মাত্রা, কার, ফলা, যুক্তবর্ণ) must never be truncated, approximated, or silently altered.
- **Artifact-Aware Preprocessing**: Physical book photographs exhibit gutter binding shadows, curvature, perspective distortion, and ink annotations. Multi-stage enhancement produces versioned variants while preserving the unmodified original.
- **Provider-Aware Quota Orchestration**: API credentials from Google AI Studio / Gemini are tracked at the project and token bucket level, avoiding naive key rotation that causes project-wide 429 throttling.
- **Dual-Pass Extraction & AI Judge Consensus**: Critical content is verified through multi-pass comparison, with an automated AI Judge inspecting discrepancies against the source image.
- **Idempotent SQLite Persistence**: State and page extraction records are recorded in an ACID-compliant SQLite store (`output/digitizer.db`) enabling seamless resumption after network failures, crashes, or quota pauses.

---

## 2. System Architecture & Directory Layout

```text
MATHEMATICS/
├── ARCHITECTURE.md                  # Comprehensive V2 system blueprint & schemas
├── TODO.md                          # Phase-by-phase implementation tracker
├── requirements.txt                 # Pinned dependencies
├── config/
│   ├── settings.yaml                # Global preprocessing, model, and font configs
│   └── keys.json.example            # Project-aware API credential configuration
├── input/
│   ├── raw_pdf/                     # Source PDF (Khairul.pdf - 882 pages)
│   └── test_samples/                # Isolated benchmark sample pages
├── output/
│   ├── digitizer.db                 # SQLite database tracking page statuses & quotas
│   ├── checkpoints/                 # Validated per-page JSON artifacts
│   ├── chapters/                    # Chapter-wise compiled DOCX outputs
│   ├── final_book.docx              # Master compiled reflowable textbook
│   ├── final_json/                  # Master consolidated textbook dataset
│   ├── rendered_images/             # Preprocessed high-DPI page renders
│   ├── debug_variants/              # Multi-variant image outputs for visual audit
│   └── reports/                     # HTML audit logs with side-by-side diffs
├── src/
│   ├── preprocessing/               # Computer vision & photographed page correction
│   │   ├── __init__.py
│   │   ├── page_boundary_detector.py # Contour and document boundary extraction
│   │   ├── perspective_corrector.py # Four-point perspective transformation
│   │   ├── dewarp.py                # Text-line curvature and cylindrical unwarping
│   │   ├── shadow_removal.py        # Illumination flattening & binding shadow reduction
│   │   ├── illumination_corrector.py# Contrast and uneven lighting normalization
│   │   ├── image_enhancer.py        # Fine-stroke CLAHE & diacritic preservation
│   │   └── preprocessing_selector.py# Variant generation & quality score selection
│   ├── layout/                      # Layout analysis & reading order
│   │   └── column_detector.py       # CV-driven Otsu & projection gutter detection
│   ├── orchestration/               # API key rotation, token buckets & rate limiters
│   ├── extraction/                  # Dual-pass OCR, Gemini integration & prompts
│   ├── validation/                  # Diff engine, LaTeX validator & AI Judge
│   ├── reconstruction/              # Word reconstruction & mathematical typesetting
│   │   ├── docx_builder.py          # Reflowable Word document generator
│   │   ├── docx_math_converter.py   # Standard MathML2OMML engine with <m:nor/> injection
│   │   ├── math_tokenizer.py        # Lexical tokenizer & AST math/citation parser
│   │   ├── document_beautifier.py   # Question citations, typography & MCQ option polish
│   │   ├── figure_extractor.py      # Automated diagram cropping & contrast enhancement
│   │   ├── chapter_detector.py      # Intelligent chapter boundary detection
│   │   ├── docx_styler.py           # Kalpurush complex-script font bindings
│   │   └── json_assembler.py        # Master dataset compiler
│   └── quality/                     # Audit reporting & SQLite persistence
│   │   ├── shadow_removal.py        # Morphological binding/gutter shadow compensation
│   │   ├── illumination_corrector.py# Division-based background normalization
│   │   ├── image_enhancer.py        # Bengali-safe CLAHE & unsharp masking
│   │   └── preprocessing_selector.py# Variant orchestrator (original, dewarped, enhanced)
│   ├── layout/                      # Document layout & logical reading order
│   │   ├── __init__.py
│   │   ├── layout_detector.py       # Region segmentation (text, math, table, figure)
│   │   ├── column_detector.py       # Multi-column boundary detection
│   │   ├── reading_order.py         # Topo-sort reading order & block relationships
│   │   └── layout_reconstructor.py  # Structured layout assembler
│   ├── orchestration/               # API keys, token buckets, and quota protection
│   │   ├── __init__.py
│   │   ├── provider_manager.py      # Multi-provider interfaces (Gemini, Mathpix, Local)
│   │   ├── key_manager.py           # Project-scoped credential state tracker
│   │   ├── token_bucket.py          # Leaky/Token bucket rate limiter (RPM/TPM/RPD)
│   │   ├── retry_manager.py         # Exponential backoff with jitter
│   │   └── cost_tracker.py          # Token and cost accounting
│   ├── extraction/                  # Vision-Language OCR execution
│   │   ├── __init__.py
│   │   ├── gemini_client.py         # Async Google GenAI SDK wrapper
│   │   ├── prompts.py               # Bengali + LaTeX extraction system prompts
│   │   └── parallel_worker.py       # Concurrent extraction coordinator
│   ├── validation/                  # Multi-tier verification & consensus
│   │   ├── __init__.py
│   │   ├── diff_engine.py           # Character/token Levenshtein & AST diffing
│   │   ├── latex_validator.py       # Syntax parsing (latex2mathml & sympy)
│   │   └── ai_judge.py              # Visual re-inspection and discrepancy arbitration
│   ├── reconstruction/              # Word (.docx) & JSON generation
│   │   ├── __init__.py
│   │   ├── json_assembler.py        # Pydantic schema validation & serialization
│   │   ├── docx_styler.py           # Typography, styles, Kalpurush Bengali font bindings
│   │   ├── docx_math_converter.py   # LaTeX -> MathML -> OMML XML converter
│   │   ├── docx_builder.py          # Reflowable document builder (tables, math, figures)
│   │   └── chapter_detector.py      # Chapter boundaries and modular chapter builder
│   ├── storage/                     # SQLite persistence and checkpointing
│   │   ├── __init__.py
│   │   ├── db.py                    # SQLite schema initialization and connection pool
│   │   └── models.py                # Database entity mappings
│   ├── quality/                     # QA and visual audit
│   │   ├── __init__.py
│   │   ├── table_comparator.py      # Row/column & numerical verification
│   │   ├── figure_comparator.py     # Crop dimension and integrity checks
│   │   └── report_generator.py      # Interactive side-by-side HTML audit dashboard
│   └── utils/                       # Shared utilities
│       ├── __init__.py
│       ├── logger.py                # Rich structured logger
│       └── exceptions.py            # Custom exception hierarchy
└── tests/                           # Unit and integration test suites
```

---

## 3. Pydantic Page Extraction Schema

The system enforces strict typing through Pydantic v2 models:

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

class BoundingBox(BaseModel):
    ymin: int
    xmin: int
    ymax: int
    xmax: int

class MathExpression(BaseModel):
    latex: str
    is_display: bool = False
    syntax_valid: bool = True
    validation_error: Optional[str] = None

class TableData(BaseModel):
    headers: List[str] = []
    rows: List[List[str]] = []
    has_merged_cells: bool = False

class FigureData(BaseModel):
    figure_id: str
    caption: Optional[str] = None
    crop_path: Optional[str] = None

class ContentBlock(BaseModel):
    block_id: str
    type: Literal[
        "heading_1", "heading_2", "heading_3",
        "paragraph", "math_block", "table",
        "figure", "caption", "exercise_item",
        "solution_block", "callout_box", "footer_or_header"
    ]
    reading_order: int
    language: Literal["bn", "en", "mixed"] = "bn"
    text: Optional[str] = None
    latex: Optional[str] = None
    bbox: Optional[BoundingBox] = None
    parent_block_id: Optional[str] = None
    related_block_ids: List[str] = []
    table_data: Optional[TableData] = None
    figure_data: Optional[FigureData] = None
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    review_required: bool = False
    validation_errors: List[str] = []

class PageExtractionRecord(BaseModel):
    page_number: int
    source_pdf_hash: str
    status: Literal["PENDING", "PREPROCESSED", "EXTRACTED", "CONSENSUS_VERIFIED", "NEEDS_REVIEW", "COMPLETED", "FAILED"]
    render_dpi: int = 350
    selected_variant: str = "final_selected.png"
    blocks: List[ContentBlock] = []
    ocr_engine: str = "gemini-2.5-flash"
    tokens_used: int = 0
    estimated_cost_usd: float = 0.0
    processed_at: str
```

---

## 4. SQLite Persistence Schema

Database file: `output/digitizer.db`

```sql
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS page_blocks (
    block_id TEXT PRIMARY KEY,
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
```

---

## 5. Mathematical & Word Equation Generation

- **LaTeX to OMML Pipeline**:
  $$\text{LaTeX} \xrightarrow{\text{latex2mathml}} \text{MathML XML} \xrightarrow{\text{XSLT or MML2OMML DOM}} \text{Word OMML XML} (\texttt{m:oMath})$$
- The converted OMML structure is injected into python-docx paragraphs via `ctypes` or `oxml` parsing (`parse_xml`), allowing native, editable equation rendering in Microsoft Word with the Cambria Math typeface, while Bengali surrounding text is styled with Kalpurush.
