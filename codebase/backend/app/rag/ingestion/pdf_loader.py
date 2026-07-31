from __future__ import annotations

import hashlib
import re
from pathlib import Path

from app.rag.ingestion.normalizer import is_text_usable, normalize_text
from app.rag.ingestion.ocr import OCRUnavailableError, TesseractOCR
from app.rag.models import (
    DocumentMetadata,
    LoadedDocument,
    PageContent,
)


class PDFLoadError(RuntimeError):
    """Raised when a PDF cannot be validated or read."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "document"


def _infer_session_number(stem: str) -> int:
    match = re.search(
        r"(?:day|lesson|session)[\s_-]*0*(\d+)",
        stem,
        flags=re.IGNORECASE,
    )
    return int(match.group(1)) if match else 1


def _humanize_stem(stem: str) -> str:
    return re.sub(r"[-_]+", " ", stem).strip().title()


class PDFLoader:
    def __init__(
        self,
        *,
        ocr_enabled: bool = True,
        ocr_provider: TesseractOCR | None = None,
    ) -> None:
        self.ocr_enabled = ocr_enabled
        self.ocr_provider = ocr_provider or TesseractOCR()

    def load(
        self,
        path: str | Path,
        *,
        document_id: str | None = None,
        document_title: str | None = None,
        session_number: int | None = None,
    ) -> LoadedDocument:
        pdf_path = Path(path).resolve()
        if not pdf_path.is_file():
            raise PDFLoadError(f"PDF does not exist: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise PDFLoadError(f"Expected a .pdf file: {pdf_path}")
        with pdf_path.open("rb") as source:
            if source.read(5) != b"%PDF-":
                raise PDFLoadError(f"Invalid PDF header: {pdf_path}")

        try:
            import pymupdf
        except ImportError as error:
            raise PDFLoadError(
                "PyMuPDF is required. Install backend requirements first."
            ) from error

        try:
            document = pymupdf.open(pdf_path)
        except Exception as error:
            raise PDFLoadError(f"Cannot open PDF {pdf_path}: {error}") from error

        if document.page_count < 1:
            document.close()
            raise PDFLoadError(f"PDF has no pages: {pdf_path}")

        resolved_document_id = document_id or _slugify(pdf_path.stem)
        metadata = DocumentMetadata(
            document_id=resolved_document_id,
            document_title=document_title or _humanize_stem(pdf_path.stem),
            session_number=session_number
            if session_number is not None
            else _infer_session_number(pdf_path.stem),
            source_file=pdf_path.name,
            total_pages=document.page_count,
            file_sha256=_sha256_file(pdf_path),
        )

        pages: list[PageContent] = []
        try:
            for page_index, page in enumerate(document, start=1):
                warnings: list[str] = []
                raw_text = self._extract_text_blocks(page)
                normalized = normalize_text(raw_text)
                extraction_method = "text" if normalized else "none"

                if not is_text_usable(normalized):
                    if self.ocr_enabled and self.ocr_provider.is_available():
                        try:
                            ocr_text = normalize_text(
                                self.ocr_provider.extract(page)
                            )
                            if len(ocr_text) > len(normalized):
                                normalized = ocr_text
                                extraction_method = "ocr"
                            else:
                                warnings.append(
                                    "OCR did not improve extracted text"
                                )
                        except OCRUnavailableError as error:
                            warnings.append(str(error))
                    elif self.ocr_enabled:
                        warnings.append(
                            "Text quality is low and Tesseract is unavailable"
                        )

                if not normalized:
                    extraction_method = "none"
                    warnings.append("Page contains no extractable text")

                pages.append(
                    PageContent(
                        document_id=metadata.document_id,
                        page_number=page_index,
                        text=normalized,
                        extraction_method=extraction_method,
                        char_count=len(normalized),
                        warnings=warnings,
                    )
                )
        finally:
            document.close()

        return LoadedDocument(metadata=metadata, pages=pages)

    @staticmethod
    def _extract_text_blocks(page: object) -> str:
        blocks = page.get_text("blocks", sort=True)
        text_blocks: list[str] = []
        for block in blocks:
            if len(block) < 5:
                continue
            block_type = block[6] if len(block) > 6 else 0
            if block_type != 0:
                continue
            block_text = str(block[4]).strip()
            if block_text:
                text_blocks.append(block_text)
        return "\n\n".join(text_blocks)
