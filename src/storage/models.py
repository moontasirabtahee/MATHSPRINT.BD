"""
Data models for the Mathematics Textbook OCR and Reconstruction system.
Uses Pydantic v2 for strict runtime schema validation and serialization.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    """Normalized or pixel bounding box coordinates [ymin, xmin, ymax, xmax]."""
    ymin: int = Field(ge=0, description="Top coordinate")
    xmin: int = Field(ge=0, description="Left coordinate")
    ymax: int = Field(ge=0, description="Bottom coordinate")
    xmax: int = Field(ge=0, description="Right coordinate")

    @property
    def width(self) -> int:
        return max(0, self.xmax - self.xmin)

    @property
    def height(self) -> int:
        return max(0, self.ymax - self.ymin)

    @property
    def area(self) -> int:
        return self.width * self.height

class MathExpression(BaseModel):
    """Encapsulates a mathematical expression extracted from the textbook."""
    latex: str
    is_display: bool = False
    syntax_valid: bool = True
    validation_error: Optional[str] = None

class TableData(BaseModel):
    """Tabular data representation supporting numerical textbook tables."""
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    has_merged_cells: bool = False

class FigureData(BaseModel):
    """Metadata for embedded illustrations, geometry diagrams, and graphs."""
    figure_id: str = "fig_01"
    caption: Optional[str] = None
    crop_path: Optional[str] = None
    diagram_type: Optional[str] = None

class ContentBlock(BaseModel):
    """A discrete, classified logical block within a page."""
    block_id: str
    type: Literal[
        "heading_1",
        "heading_2",
        "heading_3",
        "paragraph",
        "math_block",
        "table",
        "figure",
        "caption",
        "exercise_item",
        "solution_block",
        "callout_box",
        "footer_or_header",
        "header",
        "footer"
    ]
    reading_order: int = Field(ge=1, description="1-based logical reading order")
    language: Literal["bn", "en", "mixed", "none", "other"] = "bn"
    text: Optional[str] = None
    latex: Optional[str] = None
    bbox: Optional[BoundingBox] = None
    column_id: int = 1
    parent_block_id: Optional[str] = None
    related_block_ids: List[str] = Field(default_factory=list)
    math_expressions: List[MathExpression] = Field(default_factory=list)
    table_data: Optional[TableData] = None
    figure_data: Optional[FigureData] = None
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    review_required: bool = False
    validation_errors: List[str] = Field(default_factory=list)

class PageExtractionRecord(BaseModel):
    """Complete, self-contained record for an individual page."""
    page_number: int = Field(ge=1)
    source_pdf_hash: str
    status: Literal[
        "PENDING",
        "PREPROCESSED",
        "EXTRACTED",
        "CONSENSUS_VERIFIED",
        "NEEDS_REVIEW",
        "COMPLETED",
        "FAILED"
    ] = "PENDING"
    render_dpi: int = 350
    selected_variant: str = "final_selected.png"
    blocks: List[ContentBlock] = Field(default_factory=list)
    ocr_engine: str = "gemini-2.5-flash"
    tokens_used: int = 0
    estimated_cost_usd: float = 0.0
    processed_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

