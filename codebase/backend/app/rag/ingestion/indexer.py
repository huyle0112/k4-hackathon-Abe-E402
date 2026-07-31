from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.rag.embeddings import EmbeddingProvider
from app.rag.ingestion.chunker import SlideChunker
from app.rag.ingestion.pdf_loader import PDFLoader
from app.rag.models import (
    DocumentIngestionResult,
    IngestionReport,
)
from app.rag.vector_store import ChromaVectorStore


def load_manifest(path: str | Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    manifest_path = Path(path).resolve()
    with manifest_path.open("r", encoding="utf-8") as source:
        payload = json.load(source)
    documents = payload.get("documents", payload)
    if not isinstance(documents, dict):
        raise ValueError("Manifest must contain a documents object")
    return {
        str(filename): metadata
        for filename, metadata in documents.items()
        if isinstance(metadata, dict)
    }


class IndexingPipeline:
    def __init__(
        self,
        *,
        loader: PDFLoader,
        chunker: SlideChunker,
        embedding_provider: EmbeddingProvider,
        vector_store: ChromaVectorStore,
    ) -> None:
        self.loader = loader
        self.chunker = chunker
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def index_directory(
        self,
        source_directory: str | Path,
        *,
        manifest: dict[str, dict[str, Any]] | None = None,
        dry_run: bool = False,
    ) -> IngestionReport:
        source_path = Path(source_directory).resolve()
        if not source_path.is_dir():
            raise ValueError(f"Source directory does not exist: {source_path}")

        pdf_files = sorted(source_path.glob("*.pdf"))
        if not pdf_files:
            raise ValueError(f"No PDF files found in {source_path}")

        manifest = manifest or {}
        results: list[DocumentIngestionResult] = []
        for pdf_path in pdf_files:
            document_config = manifest.get(pdf_path.name, {})
            loaded = self.loader.load(
                pdf_path,
                document_id=document_config.get("document_id"),
                document_title=document_config.get("document_title"),
                session_number=document_config.get("session_number"),
            )
            chunks = self.chunker.chunk_document(loaded)
            warnings = [
                f"Slide {page.page_number}: {warning}"
                for page in loaded.pages
                for warning in page.warnings
            ]

            indexed_count = 0
            if not dry_run and chunks:
                embeddings = self.embedding_provider.embed_documents(
                    [chunk.text for chunk in chunks]
                )
                indexed_count = self.vector_store.upsert(chunks, embeddings)
                self.vector_store.delete_stale_chunks(
                    loaded.metadata.document_id,
                    {chunk.chunk_id for chunk in chunks},
                )

            results.append(
                DocumentIngestionResult(
                    document_id=loaded.metadata.document_id,
                    source_file=loaded.metadata.source_file,
                    total_pages=loaded.metadata.total_pages,
                    text_pages=sum(
                        page.extraction_method == "text"
                        for page in loaded.pages
                    ),
                    ocr_pages=sum(
                        page.extraction_method == "ocr"
                        for page in loaded.pages
                    ),
                    empty_pages=sum(
                        page.extraction_method == "none"
                        for page in loaded.pages
                    ),
                    chunk_count=len(chunks),
                    indexed_count=indexed_count,
                    warnings=warnings,
                )
            )

        return IngestionReport(
            source_directory=str(source_path),
            dry_run=dry_run,
            documents=results,
        )

from pathlib import Path

from app.rag.ingestion.chunker import chunk_page
from app.rag.ingestion.pdf_loader import load_pdf
from app.rag.vector_store import JsonVectorStore


def index_pdf(path: Path, session_id: str, store: JsonVectorStore) -> int:
    chunks = [
        chunk
        for page in load_pdf(path)
        for chunk in chunk_page(page.text, path.name, session_id, page.number)
    ]
    return store.replace_session(session_id, chunks)
