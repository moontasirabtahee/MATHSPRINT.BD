"""
Structured logger for the Mathematics OCR & Reconstruction pipeline.
Uses Rich for clean terminal formatting and supports persistent file logging.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler

_LOGGER: Optional[logging.Logger] = None

def get_logger(name: str = "DigitizerV2") -> logging.Logger:
    """Return a configured logger with Rich console output and file rotation."""
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # Rich console handler
    console = Console(file=sys.stdout)
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
        markup=True
    )
    rich_handler.setLevel(logging.INFO)
    logger.addHandler(rich_handler)

    # File handler for persistent logging
    log_dir = Path("output/reports")
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "pipeline.log", encoding="utf-8")
    file_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s] %(filename)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_format)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    _LOGGER = logger
    return logger

