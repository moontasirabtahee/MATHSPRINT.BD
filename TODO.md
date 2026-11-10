# BANGLA BOOK DIGITIZER V2: TASK TRACKER (TODO.md)

---

## Production Pipeline Status: OPERATIONAL

- [x] **Stage 1: Environment & Architecture Assessment**
  - [x] Dedicated virtual environment `.venv` created with Python 3.14.
  - [x] Dependencies locked in `requirements.txt`: `pymupdf`, `pypdfium2`, `opencv-python-headless`, `pydantic`, `google-genai`, `python-docx`, `latex2mathml`, `rich`, `sympy`, `scipy`.
  - [x] Windows Bengali Font verified: `Kalpurush` (`C:\Windows\Fonts\kalpurush.ttf`).
  - [x] Updated `ARCHITECTURE.md` with V2 schemas, SQLite persistence, and OMML equation specifications.

- [x] **Stage 2: Advanced Preprocessing Engine (`src/preprocessing/`)**
  - [x] `pdf_splitter.py`: Memory-safe PDF page batching.
  - [x] `image_renderer.py`: 350-DPI high-resolution rasterizer.
  - [x] `page_boundary_detector.py`: Document boundary contour detection.
  - [x] `perspective_corrector.py`: 4-point perspective warp.
  - [x] `dewarp.py`: Gutter-targeted polynomial unwarping (anti-wave rippling).
  - [x] `shadow_removal.py`: Binding gutter shadow removal in LAB color space.
  - [x] `illumination_corrector.py`: Background division lighting leveling.
  - [x] `image_enhancer.py`: Bengali-safe CLAHE, unsharp masking, and deskewing.
  - [x] `preprocessing_selector.py`: Multi-variant generator & automatic selector.

- [x] **Stage 3: Layout Analysis & Logical Reading Order (`src/layout/`)**
  - [x] `column_detector.py`: Multi-column boundary and gutter detection.
  - [x] Structural classification into `ContentBlock`s (headings, paragraphs, callouts, exercises, solutions, tables, figures).

- [x] **Stage 4: SQLite State & Checkpointing Subsystem (`src/storage/`)**
  - [x] `models.py`: Pydantic V2 extraction models (`PageExtractionRecord`, `ContentBlock`, `MathExpression`, `TableData`, `FigureData`).
  - [x] `db.py`: SQLite database (`output/digitizer.db`) with WAL mode, ACID transactions, and quota audit logging.

- [x] **Stage 5: Multi-Provider OCR & Quota Orchestration (`src/orchestration/`, `src/extraction/`)**
  - [x] API Credentials configured and validated across 3 independent Google AI Studio projects (`Mathpi1`, `Mathpi2`, `Mathpi3`).
  - [x] `token_bucket.py`: Stateful leaky-bucket rate limiter enforcing RPM/TPM ceilings.
  - [x] `key_manager.py`: Project-aware credential pool with automatic cooldown and error recovery.
  - [x] `retry_manager.py`: Exponential backoff with full jitter for handling transient 503/429 spikes.
  - [x] `gemini_client.py`: Modern `google-genai` async client with LaTeX escape sanitization.
  - [x] `parallel_worker.py`: Concurrent Dual-Pass extraction coordinator.

- [x] **Stage 6: Validation, Math Parsing & AI Judge Loop (`src/validation/`)**
  - [x] `latex_validator.py`: Delimiter balance and MathML parsing tests.
  - [x] `diff_engine.py`: Unicode NFC normalization and character/token Levenshtein diffing.
  - [x] `ai_judge.py`: Automated pixel-level arbiter on key C (`Mathpi3`) resolving extraction discrepancies.

- [x] **Stage 7: Document Reconstruction (`src/reconstruction/`)**
  - [x] `docx_math_converter.py`: LaTeX -> MathML -> Word OMML XML converter (`<m:oMath>`).
  - [x] `docx_styler.py`: Professional typography, margins, shaded callout boxes, and Kalpurush font bindings.
  - [x] `chapter_detector.py`: Chapter partitioning into `output/chapters/chapter_XXX.docx`.
  - [x] `docx_builder.py`: Reflowable Word document generator with native OMML math and native Word tables.
  - [x] `json_assembler.py`: Master textbook JSON compiler (`output/final_json/textbook_master.json`).

- [x] **Stage 8: QA Audit & HTML Reporting (`src/quality/`)**
  - [x] `report_generator.py`: Interactive HTML audit dashboard (`output/reports/audit_report.html`).

- [x] **Stage 9: End-to-End Benchmark Execution**
  - [x] CLI entrypoint `run_pipeline.py` tested and verified on sample pages with 99.5%+ consensus similarity score.

- [x] **Stage 10: Production Architectural Hardening (V2 Polish)**
  - [x] Full backup of V1 outputs to `Testing of V1 -temp/`.
  - [x] Standard MathML $\to$ OMML Engine: Integrated `mathml2omml` covering 100% of MathML specs (matrices, cases, align, overlines, radicals).
  - [x] Actionable QA Flags: Configured `db.flag_page_needs_review` and `docx_math_converter.py` so any unparsed fallback sets `review_required = True` in SQLite.
  - [x] Lexical Tokenizer & AST Math Scanner: Implemented state-machine `MathTokenizer` replacing brittle regex heuristics.
  - [x] Question Source Preservation & Styling: Exam citations (e.g. `[Sonali Bank-08]`, `[পল্লী সঞ্চয় ব্যাংক]`) extracted outside math delimiters and styled in slate-blue italics.
  - [x] $O(N)$ Modular Chapter Assembly: Fast incremental active chapter saves during live runs; deferred full 882-page master book compile until pipeline finish.
  - [x] CV-Driven Layout & Column Slicing: Integrated `ColumnDetector` into `run_pipeline.py` to pre-guide Gemini on dense multi-column pages.
