from dataclasses import dataclass
from pathlib import Path

import fitz


@dataclass(frozen=True)
class PdfPage:
    number: int
    text: str


def load_pdf(path: Path) -> list[PdfPage]:
    if not path.is_file() or path.suffix.lower() != ".pdf":
        raise ValueError(f"Không phải file PDF hợp lệ: {path}")
    with fitz.open(path) as document:
        return [PdfPage(number=index + 1, text=page.get_text("text")) for index, page in enumerate(document)]
