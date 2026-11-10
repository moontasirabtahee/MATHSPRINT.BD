"""
Human-in-the-Loop QA & Review Dashboard (Streamlit).
Allows reviewers to view scanned page images, inspect and edit extracted Bengali text,
modify LaTeX mathematical formulas with live KaTeX preview, inspect tables/figures,
and save persistent corrections to SQLite and JSON checkpoints without reprocessing.
"""

import sys
from pathlib import Path
import json
import streamlit as st
from PIL import Image

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.storage.db import DatabaseManager
from src.storage.models import PageExtractionRecord, ContentBlock
from src.reconstruction.docx_builder import DocxBuilder

st.set_page_config(
    page_title="Bangla Book Digitizer V2 - Review Studio",
    page_icon="📖",
    layout="wide"
)

db = DatabaseManager(Path("output/digitizer.db"))

st.title("📖 Bangla Book Digitizer V2 — Human Review & Correction Studio")

# Sidebar: Page selection & filtering
st.sidebar.header("Navigation & Status")

with db._get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT page_number, status, review_required, tokens_used FROM pages ORDER BY page_number ASC")
    page_rows = cursor.fetchall()

if not page_rows:
    st.warning("No pages found in database. Please run `run_pipeline.py` first to process pages.")
    st.stop()

filter_option = st.sidebar.radio("Filter Pages", ["All Pages", "Needs Review Only", "Completed Only"])

filtered_pages = []
for r in page_rows:
    p_num = r["page_number"]
    status = r["status"]
    is_rev = bool(r["review_required"])
    if filter_option == "Needs Review Only" and not (is_rev or status == "NEEDS_REVIEW"):
        continue
    if filter_option == "Completed Only" and status not in ("COMPLETED", "CONSENSUS_VERIFIED"):
        continue
    filtered_pages.append(r)

if not filtered_pages:
    st.info("No pages match the selected filter.")
    st.stop()

page_options = [f"Page {r['page_number']:03d} [{r['status']}]" for r in filtered_pages]
selected_page_str = st.sidebar.selectbox("Select Page to Inspect", page_options)
selected_page_num = int(selected_page_str.split()[1])

# Fetch page data
record = db.get_page(selected_page_num)
if not record:
    st.error(f"Failed to load record for Page {selected_page_num}")
    st.stop()

# Layout: 2 Columns (Left: Image Viewer, Right: Content Editor)
col_left, col_right = st.columns([1, 1], gap="medium")

with col_left:
    st.subheader(f"🖼️ Page {record.page_number:03d} Visual Reference")

    # Variant selector
    variants_dir = Path("output/debug_variants") / f"page_{record.page_number:03d}"
    available_variants = []
    if variants_dir.exists():
        available_variants = [f.name for f in variants_dir.glob("*.png")]

    selected_variant_name = "final_selected.png"
    if available_variants:
        selected_variant_name = st.selectbox("Image Preprocessing Variant", available_variants, index=available_variants.index("final_selected.png") if "final_selected.png" in available_variants else 0)

    image_path = variants_dir / selected_variant_name
    if not image_path.exists():
        # Fallback to test sample if present
        image_path = Path("input/test_samples") / f"sample_page_{record.page_number}.png"

    if image_path.exists():
        zoom_width = st.slider("Image Display Width (px)", min_value=400, max_value=1200, value=650, step=50)
        img = Image.open(image_path)
        st.image(img, width=zoom_width, caption=f"{selected_variant_name} ({img.width}x{img.height})")
    else:
        st.warning(f"Image not found at {image_path}")

    # Metadata & Statistics
    st.markdown("---")
    st.markdown(f"**Status:** `{record.status}` | **OCR Engine:** `{record.ocr_engine}`")
    st.markdown(f"**Tokens Used:** `{record.tokens_used:,}` | **Estimated Cost:** `${record.estimated_cost_usd:.4f}`")
    if record.metadata:
        st.json(record.metadata, expanded=False)

with col_right:
    st.subheader(f"✏️ Content Blocks ({len(record.blocks)} total)")

    updated_blocks = []
    has_changes = False

    for idx, block in enumerate(record.blocks):
        with st.expander(f"Block #{block.reading_order:02d} [{block.type}] - {block.block_id}", expanded=(block.review_required or idx < 3)):
            col_b1, col_b2 = st.columns([3, 1])
            with col_b1:
                block_type = st.selectbox(
                    "Block Classification",
                    [
                        "heading_1", "heading_2", "heading_3", "paragraph",
                        "math_block", "table", "exercise_item", "solution_block",
                        "callout_box", "figure", "footer_or_header"
                    ],
                    index=[
                        "heading_1", "heading_2", "heading_3", "paragraph",
                        "math_block", "table", "exercise_item", "solution_block",
                        "callout_box", "figure", "footer_or_header"
                    ].index(block.type) if block.type in [
                        "heading_1", "heading_2", "heading_3", "paragraph",
                        "math_block", "table", "exercise_item", "solution_block",
                        "callout_box", "figure", "footer_or_header"
                    ] else 3,
                    key=f"type_{block.block_id}"
                )
            with col_b2:
                review_flag = st.checkbox("Needs Review", value=block.review_required, key=f"rev_{block.block_id}")

            new_text = st.text_area(
                "Bengali / Mixed Text (supports inline $...$)",
                value=block.text or "",
                height=100,
                key=f"text_{block.block_id}"
            )

            new_latex = None
            if block.latex or block.type == "math_block":
                new_latex = st.text_input(
                    "Mathematical LaTeX Formula",
                    value=block.latex or "",
                    key=f"latex_{block.block_id}"
                )
                if new_latex:
                    st.markdown("**Live KaTeX Equation Preview:**")
                    st.latex(new_latex)

            if new_text != (block.text or "") or block_type != block.type or review_flag != block.review_required or (new_latex and new_latex != (block.latex or "")):
                has_changes = True

            # Clone block with updated values
            updated_block = block.model_copy(update={
                "type": block_type,
                "text": new_text,
                "latex": new_latex,
                "review_required": review_flag
            })
            updated_blocks.append(updated_block)

    st.markdown("---")
    col_act1, col_act2, col_act3 = st.columns([1, 1, 1])

    with col_act1:
        if st.button("💾 Save All Block Changes", type="primary", use_container_width=True):
            record.blocks = updated_blocks
            if not any(b.review_required for b in updated_blocks):
                record.status = "CONSENSUS_VERIFIED"
            db.upsert_page(record)

            # Update checkpoint JSON
            checkpoint_file = Path("output/checkpoints") / f"page_{record.page_number:03d}.json"
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                f.write(record.model_dump_json(indent=2))

            st.success(f"Page {record.page_number:03d} successfully saved to SQLite and checkpoint!")
            st.rerun()

    with col_act2:
        if st.button("✅ Mark Page VERIFIED", use_container_width=True):
            record.status = "COMPLETED"
            for b in record.blocks:
                b.review_required = False
            db.upsert_page(record)
            st.success(f"Page {record.page_number:03d} marked COMPLETED!")
            st.rerun()

    with col_act3:
        if st.button("📄 Recompile Word Document", use_container_width=True):
            builder = DocxBuilder(primary_font="Kalpurush")
            final_docx_path = Path("output/final_docx/Khairul_Basic_Math_Reconstructed.docx")
            all_pages = [db.get_page(r["page_number"]) for r in page_rows]
            valid_pages = [p for p in all_pages if p is not None]
            builder.build_document(valid_pages, final_docx_path)
            st.success(f"Recompiled Word document at [{final_docx_path.name}]!")

