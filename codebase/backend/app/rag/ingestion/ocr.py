from __future__ import annotations

import os
import shutil
from typing import Any


class OCRUnavailableError(RuntimeError):
    """Raised when OCR is requested but Tesseract is unavailable."""


class TesseractOCR:
    def __init__(self, languages: str = "vie+eng", dpi: int = 240) -> None:
        self.languages = languages
        self.dpi = dpi

    @staticmethod
    def is_available() -> bool:
        configured = os.getenv("TESSERACT_CMD")
        if configured:
            return os.path.isfile(configured)
        return shutil.which("tesseract") is not None

    def extract(self, page: Any) -> str:
        if not self.is_available():
            raise OCRUnavailableError(
                "Tesseract is not available. Install it with Vietnamese and "
                "English language data or disable OCR."
            )

        try:
            text_page = page.get_textpage_ocr(
                language=self.languages,
                dpi=self.dpi,
                full=True,
            )
            return page.get_text("text", textpage=text_page, sort=True)
        except Exception as error:  # PyMuPDF exposes runtime-specific errors.
            raise OCRUnavailableError(f"OCR failed: {error}") from error
