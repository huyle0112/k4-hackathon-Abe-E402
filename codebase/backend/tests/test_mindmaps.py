from __future__ import annotations

import hashlib
from pathlib import Path

from app.mindmaps import (
    CreateMindmapRequest,
    GeneratedMindmap,
    MindmapData,
    MindmapNode,
    MindmapRepository,
    MindmapService,
)
from app.rag.models import Chunk, SearchHit


class FakeEmbedding:
    def __init__(self) -> None:
        self.calls = 0

    def embed_query(self, text: str) -> list[float]:
        del text
        self.calls += 1
        return [1.0, 0.0]


class FakeStore:
    def __init__(self, hits: list[SearchHit]) -> None:
        self.hits = hits
        self.last_where = None

    def get_chunks(self, *, where=None):
        self.last_where = where
        return [hit.chunk for hit in self.hits]


class FakeContextProvider:
    def __init__(self, hits: list[SearchHit]) -> None:
        self.hits = hits
        self.document_ids = None

    def load(self, document_ids: list[str]) -> list[SearchHit]:
        self.document_ids = document_ids
        return self.hits


class FakeReranker:
    def rerank(self, query, candidates, **kwargs):
        del query, kwargs
        return candidates


class FakeGenerator:
    def __init__(self, chunk_id: str) -> None:
        self.chunk_id = chunk_id
        self.calls = 0

    def generate(self, prompt: str, evidence_context: str):
        del prompt
        assert self.chunk_id in evidence_context
        self.calls += 1
        return GeneratedMindmap(
            title="Attention",
            mindmap=MindmapData(
                nodeData=MindmapNode(
                    id="root",
                    topic="Attention",
                    root=True,
                    children=[
                        MindmapNode(id="child", topic="Token")
                    ],
                )
            ),
            cited_chunk_ids=[self.chunk_id],
        )


class FailingGenerator:
    def generate(self, prompt: str, evidence_context: str):
        del prompt, evidence_context
        raise RuntimeError("provider failed")


def _hit() -> SearchHit:
    text = "Attention giúp mỗi token xác định phần ngữ cảnh liên quan."
    chunk = Chunk(
        chunk_id="day-01-slide-15-chunk-01",
        document_id="doc_day_01",
        document_title="AI Foundation",
        session_number=1,
        source_file="day-01.pdf",
        slide_number=15,
        chunk_index=1,
        text=text,
        extraction_method="text",
        content_hash=hashlib.sha256(text.encode()).hexdigest(),
        token_count=9,
    )
    return SearchHit(
        chunk=chunk,
        score=0.9,
        vector_score=0.9,
        lexical_score=0.9,
        rank=1,
    )


def _service(
    tmp_path: Path,
    *,
    hits: list[SearchHit],
    generator=None,
) -> MindmapService:
    return MindmapService(
        repository=MindmapRepository(tmp_path / "mindmaps.sqlite3"),
        context_provider=FakeContextProvider(hits),
        generation_provider=generator,
    )


def test_create_mindmap_persists_and_reuses_cache(tmp_path: Path) -> None:
    hit = _hit()
    generator = FakeGenerator(hit.chunk.chunk_id)
    service = _service(tmp_path, hits=[hit], generator=generator)
    request = CreateMindmapRequest(
        document_ids=["doc_day_01"],
        prompt="Tạo mindmap giải thích Attention",
    )

    created = service.create(request, user_id="u1")
    cached = service.create(request, user_id="u1")

    assert created.status == "created"
    assert created.mindmap_id
    assert created.sources == []
    assert cached.status == "cached"
    assert cached.mindmap_id == created.mindmap_id
    assert generator.calls == 1


def test_vague_prompt_requests_clarification_without_generation(
    tmp_path: Path,
) -> None:
    hit = _hit()
    generator = FakeGenerator(hit.chunk.chunk_id)
    service = _service(tmp_path, hits=[hit], generator=generator)

    response = service.create(
        CreateMindmapRequest(
            document_ids=["doc_day_01"],
            prompt="tạo mindmap cho tôi",
        )
    )

    assert response.status == "clarification_required"
    assert response.clarification_question
    assert response.mindmap == {}
    assert response.mindmap_id is None
    assert generator.calls == 0


def test_no_relevant_context_does_not_create_mindmap(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path, hits=[], generator=None)

    response = service.create(
        CreateMindmapRequest(
            document_ids=["doc_day_01"],
            prompt="Tạo mindmap phác đồ điều trị đau ngực",
        )
    )

    assert response.status == "no_context"
    assert response.mindmap == {}
    assert response.sources == []
    assert response.mindmap_id is None


def test_document_filter_contains_only_selected_documents(
    tmp_path: Path,
) -> None:
    hit = _hit()
    context_provider = FakeContextProvider([hit])
    service = MindmapService(
        repository=MindmapRepository(tmp_path / "mindmaps.sqlite3"),
        context_provider=context_provider,
        generation_provider=FakeGenerator(hit.chunk.chunk_id),
    )

    service.create(
        CreateMindmapRequest(
            document_ids=["doc_day_01", "doc_day_02"],
            prompt="So sánh LLM và Agent",
        )
    )

    assert context_provider.document_ids == ["doc_day_01", "doc_day_02"]


def test_blank_prompt_uses_all_selected_document_context(
    tmp_path: Path,
) -> None:
    hit = _hit()
    context_provider = FakeContextProvider([hit])
    generator = FakeGenerator(hit.chunk.chunk_id)
    service = MindmapService(
        repository=MindmapRepository(tmp_path / "mindmaps.sqlite3"),
        context_provider=context_provider,
        generation_provider=generator,
    )

    response = service.create(
        CreateMindmapRequest(document_ids=["doc_day_01"], prompt="")
    )

    assert response.status == "created"
    assert response.prompt.startswith("Tạo mindmap tổng quan")
    assert context_provider.document_ids == ["doc_day_01"]


def test_provider_failure_returns_structured_response(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path,
        hits=[_hit()],
        generator=FailingGenerator(),
    )

    response = service.create(
        CreateMindmapRequest(
            document_ids=["doc_day_01"],
            prompt="Tạo mindmap về Attention",
        )
    )

    assert response.status == "no_context"
    assert response.mindmap == {}
    assert response.mindmap_id is None
    assert response.sources == []
