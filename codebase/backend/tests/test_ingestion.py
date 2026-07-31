from __future__ import annotations

import hashlib
from pathlib import Path

import pymupdf

from app.rag.embeddings import HashEmbeddingProvider
from app.rag.ingestion.chunker import SlideChunker
from app.rag.ingestion.indexer import IndexingPipeline
from app.rag.ingestion.normalizer import (
    is_text_usable,
    normalize_text,
)
from app.rag.ingestion.pdf_loader import PDFLoader
from app.rag.models import (
    DocumentMetadata,
    LoadedDocument,
    PageContent,
)
from app.rag.vector_store import ChromaVectorStore


def _create_test_pdf(path: Path) -> None:
    document = pymupdf.open()
    page_one = document.new_page()
    page_one.insert_text(
        (72, 72),
        "Buoi 1: Cam bien do am dat va chu ky do.",
    )
    page_two = document.new_page()
    page_two.insert_text(
        (72, 72),
        "Buoi 2: Quy tac tuoi dua tren du lieu cam bien.",
    )
    document.save(path)
    document.close()


def test_normalizer_preserves_vietnamese() -> None:
    raw = "  Trí tuệ\u00a0nhân tạo  \r\n\r\n\r\n  có ích.  "
    assert normalize_text(raw) == "Trí tuệ nhân tạo\n\ncó ích."
    assert is_text_usable("Trí tuệ nhân tạo hỗ trợ người học.")


def test_pdf_loader_extracts_pages_and_metadata(tmp_path: Path) -> None:
    pdf_path = tmp_path / "day-03-synthetic.pdf"
    _create_test_pdf(pdf_path)

    loaded = PDFLoader(ocr_enabled=False).load(pdf_path)

    assert loaded.metadata.session_number == 3
    assert loaded.metadata.total_pages == 2
    assert len(loaded.pages) == 2
    assert all(page.extraction_method == "text" for page in loaded.pages)
    assert "Cam bien" in loaded.pages[0].text


def test_chunker_never_crosses_slide_boundary() -> None:
    document = LoadedDocument(
        metadata=DocumentMetadata(
            document_id="synthetic",
            document_title="Synthetic",
            session_number=1,
            source_file="synthetic.pdf",
            total_pages=2,
            file_sha256="0" * 64,
        ),
        pages=[
            PageContent(
                document_id="synthetic",
                page_number=1,
                text="Nội dung slide một. " * 40,
                extraction_method="text",
                char_count=800,
            ),
            PageContent(
                document_id="synthetic",
                page_number=2,
                text="Nội dung slide hai. " * 40,
                extraction_method="text",
                char_count=800,
            ),
        ],
    )
    chunks = SlideChunker(max_tokens=50, overlap_tokens=10).chunk_document(
        document
    )

    assert {chunk.slide_number for chunk in chunks} == {1, 2}
    assert all(
        not (
            "slide một" in chunk.text.lower()
            and "slide hai" in chunk.text.lower()
        )
        for chunk in chunks
    )
    assert len({chunk.chunk_id for chunk in chunks}) == len(chunks)


def test_indexing_is_idempotent(tmp_path: Path) -> None:
    source = tmp_path / "lessons"
    source.mkdir()
    _create_test_pdf(source / "day-01-synthetic.pdf")

    embedding = HashEmbeddingProvider(128)
    store = ChromaVectorStore(
        path=tmp_path / "chroma",
        collection_name="test_ingestion",
        embedding_provider_name=embedding.name,
        embedding_dimension=embedding.dimension,
    )
    pipeline = IndexingPipeline(
        loader=PDFLoader(ocr_enabled=False),
        chunker=SlideChunker(max_tokens=200, overlap_tokens=20),
        embedding_provider=embedding,
        vector_store=store,
    )

    first = pipeline.index_directory(source)
    second = pipeline.index_directory(source)

    assert first.total_pages == 2
    assert first.total_chunks == 2
    assert second.total_chunks == 2
    assert store.count() == 2


def test_private_pdfs_have_expected_page_count() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    lesson_dir = repo_root / "private-data" / "lessons"
    pdfs = sorted(lesson_dir.glob("*.pdf"))
    if not pdfs:
        return

    assert len(pdfs) == 2
    for pdf_path in pdfs:
        loaded = PDFLoader(ocr_enabled=False).load(pdf_path)
        assert loaded.metadata.total_pages == 29
        assert len(loaded.pages) == 29
        assert hashlib.sha256(pdf_path.read_bytes()).hexdigest() == (
            loaded.metadata.file_sha256
        )
