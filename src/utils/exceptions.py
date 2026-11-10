"""
Custom exceptions for the Mathematics OCR & Reconstruction pipeline.
"""

class PipelineError(Exception):
    """Base exception for all pipeline errors."""
    pass

class PreprocessingError(PipelineError):
    """Raised when PDF rendering, splitting, or image enhancement fails."""
    pass

class KeyRotationError(PipelineError):
    """Raised when all API keys in the rotation pool are exhausted or in cooldown."""
    pass

class ExtractionError(PipelineError):
    """Raised when LLM/VLM extraction fails or returns unparseable content."""
    pass

class LaTeXValidationError(PipelineError):
    """Raised when LaTeX math syntax is invalid or delimiters are unbalanced."""
    pass

class ConsensusError(PipelineError):
    """Raised when consensus cannot be reached and AI Judge fails to arbitrate."""
    pass

class ReconstructionError(PipelineError):
    """Raised when JSON assembly or DOCX generation fails."""
    pass

