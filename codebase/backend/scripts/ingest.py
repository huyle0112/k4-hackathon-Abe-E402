from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

from app.config import Settings
from app.rag.embeddings import create_embedding_provider
from app.rag.ingestion.chunker import SlideChunker
from app.rag.ingestion.indexer import IndexingPipeline, load_manifest
from app.rag.ingestion.ocr import TesseractOCR
from app.rag.ingestion.pdf_loader import PDFLoader
from app.rag.runtime import create_vector_store


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest local lesson PDFs into the local vector store."
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="Directory containing lesson PDFs.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Optional JSON metadata manifest.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Extract and chunk without writing embeddings.",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Reset the selected local collection before indexing.",
    )
    parser.add_argument(
        "--no-ocr",
        action="store_true",
        help="Disable OCR fallback.",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv(BACKEND_ROOT / ".env")
    args = parse_args()
    settings = Settings.from_env()
    source = (args.source or settings.lessons_dir).resolve()

    embedding_provider = create_embedding_provider(settings)
    vector_store = create_vector_store(settings, embedding_provider)
    if args.rebuild:
        if args.dry_run:
            raise ValueError("--rebuild cannot be combined with --dry-run")
        vector_store.reset()

    ocr_provider = TesseractOCR(
        languages=settings.ocr_languages,
        dpi=settings.ocr_dpi,
    )
    pipeline = IndexingPipeline(
        loader=PDFLoader(
            ocr_enabled=settings.ocr_enabled and not args.no_ocr,
            ocr_provider=ocr_provider,
        ),
        chunker=SlideChunker(
            max_tokens=settings.chunk_max_tokens,
            overlap_tokens=settings.chunk_overlap_tokens,
        ),
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )
    report = pipeline.index_directory(
        source,
        manifest=load_manifest(args.manifest),
        dry_run=args.dry_run,
    )
    payload = report.model_dump()
    payload["summary"] = {
        "document_count": len(report.documents),
        "total_pages": report.total_pages,
        "total_chunks": report.total_chunks,
        "vector_store_count": vector_store.count(),
        "embedding_provider": embedding_provider.name,
        "ocr_available": ocr_provider.is_available(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
