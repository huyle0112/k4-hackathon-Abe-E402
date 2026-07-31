from __future__ import annotations

import hashlib
import re

from app.rag.ingestion.normalizer import approximate_token_count
from app.rag.models import Chunk, LoadedDocument, PageContent


_PARAGRAPH_BREAK = re.compile(r"\n\s*\n")


class SlideChunker:
    """Split each PDF page independently while preserving slide citations."""

    def __init__(self, max_tokens: int = 700, overlap_tokens: int = 80) -> None:
        if max_tokens < 50:
            raise ValueError("max_tokens must be at least 50")
        if overlap_tokens < 0 or overlap_tokens >= max_tokens:
            raise ValueError("overlap_tokens must be between 0 and max_tokens")
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def chunk_document(self, document: LoadedDocument) -> list[Chunk]:
        chunks: list[Chunk] = []
        for page in document.pages:
            fragments = self._split_page(page)
            for chunk_index, fragment in enumerate(fragments, start=1):
                content_hash = hashlib.sha256(
                    fragment.encode("utf-8")
                ).hexdigest()
                chunks.append(
                    Chunk(
                        chunk_id=(
                            f"{document.metadata.document_id}"
                            f"-slide-{page.page_number:02d}"
                            f"-chunk-{chunk_index:02d}"
                        ),
                        document_id=document.metadata.document_id,
                        document_title=document.metadata.document_title,
                        session_number=document.metadata.session_number,
                        source_file=document.metadata.source_file,
                        slide_number=page.page_number,
                        chunk_index=chunk_index,
                        text=fragment,
                        extraction_method=page.extraction_method,
                        content_hash=content_hash,
                        token_count=approximate_token_count(fragment),
                    )
                )
        return chunks

    def _split_page(self, page: PageContent) -> list[str]:
        if not page.text.strip():
            return []
        if approximate_token_count(page.text) <= self.max_tokens:
            return [page.text.strip()]

        paragraphs = [
            paragraph.strip()
            for paragraph in _PARAGRAPH_BREAK.split(page.text)
            if paragraph.strip()
        ]
        if len(paragraphs) == 1:
            paragraphs = [
                line.strip() for line in page.text.splitlines() if line.strip()
            ]

        fragments: list[str] = []
        current: list[str] = []
        current_tokens = 0

        for paragraph in paragraphs:
            paragraph_tokens = approximate_token_count(paragraph)
            if paragraph_tokens > self.max_tokens:
                if current:
                    fragments.append("\n\n".join(current).strip())
                    current = []
                    current_tokens = 0
                fragments.extend(self._split_long_paragraph(paragraph))
                continue

            if current and current_tokens + paragraph_tokens > self.max_tokens:
                completed = "\n\n".join(current).strip()
                fragments.append(completed)
                overlap = self._tail_words(completed, self.overlap_tokens)
                current = [overlap, paragraph] if overlap else [paragraph]
                current_tokens = approximate_token_count("\n\n".join(current))
            else:
                current.append(paragraph)
                current_tokens += paragraph_tokens

        if current:
            fragments.append("\n\n".join(current).strip())

        return [fragment for fragment in fragments if fragment]

    def _split_long_paragraph(self, paragraph: str) -> list[str]:
        words = paragraph.split()
        step = self.max_tokens - self.overlap_tokens
        fragments: list[str] = []
        start = 0
        while start < len(words):
            end = min(len(words), start + self.max_tokens)
            fragments.append(" ".join(words[start:end]))
            if end == len(words):
                break
            start += step
        return fragments

    @staticmethod
    def _tail_words(text: str, count: int) -> str:
        if count <= 0:
            return ""
        words = text.split()
        return " ".join(words[-count:])

import hashlib

from app.rag.embeddings import embed
from app.rag.ingestion.normalizer import normalize_text
from app.rag.models import Chunk


def chunk_page(
    text: str,
    file_name: str,
    session_id: str,
    page: int,
    max_chars: int = 1200,
    overlap: int = 160,
) -> list[Chunk]:
    clean = normalize_text(text)
    if not clean:
        return []
    chunks: list[Chunk] = []
    start = 0
    while start < len(clean):
        end = min(len(clean), start + max_chars)
        if end < len(clean):
            boundary = clean.rfind(" ", start, end)
            if boundary > start + max_chars // 2:
                end = boundary
        content = clean[start:end].strip()
        digest = hashlib.sha1(f"{session_id}:{file_name}:{page}:{start}".encode()).hexdigest()[:16]
        chunks.append(Chunk(
            id=digest,
            text=content,
            file_name=file_name,
            session_id=session_id,
            page=page,
            slide=page,
            embedding=embed(content),
        ))
        if end >= len(clean):
            break
        start = max(start + 1, end - overlap)
    return chunks
