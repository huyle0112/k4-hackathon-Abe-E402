from __future__ import annotations

from app.agent.tools import (
    AgentTools,
    GetSavedMindmapArgs,
    LoadLessonContextArgs,
    SearchSlideEvidenceArgs,
    TOOL_DEFINITIONS,
)


class FakeEmbedding:
    def embed_query(self, query):
        self.query = query
        return [1.0, 0.0]


class FakeStore:
    def __init__(self):
        self.chunks = []

    def query(self, embedding, *, n_results, where):
        self.embedding = embedding
        self.n_results = n_results
        self.where = where
        return []

    def get_chunks(self, *, where=None):
        self.where = where
        return self.chunks


class FakeReranker:
    def rerank(self, query, candidates, **kwargs):
        return candidates


class FakeRepository:
    def __init__(self):
        self.request = None

    def find_by_id(self, user_id, mindmap_id):
        self.request = (user_id, mindmap_id)
        return None


class FakeMindmapService:
    def __init__(self):
        self.repository = FakeRepository()


def _tools():
    return AgentTools(
        embedding_provider=FakeEmbedding(),
        vector_store=FakeStore(),
        reranker=FakeReranker(),
        mindmap_service=FakeMindmapService(),
    )


def test_tool_definitions_are_strict_openai_functions() -> None:
    assert {item["name"] for item in TOOL_DEFINITIONS} == {
        "load_lesson_context",
        "search_slide_evidence",
        "get_saved_mindmap",
        "create_mindmap",
    }
    assert all(item["strict"] for item in TOOL_DEFINITIONS)


def test_empty_summary_context_does_not_call_embedding() -> None:
    tools = _tools()
    result = tools.load_lesson_context(
        LoadLessonContextArgs(
            document_id="doc-1", scope="current_lesson"
        )
    )

    assert result["chunks"] == []
    assert not hasattr(tools.embedding_provider, "query")


def test_search_never_uses_slides_after_current_context() -> None:
    tools = _tools()
    result = tools.search_slide_evidence(
        SearchSlideEvidenceArgs(
            query="Attention là gì?",
            document_id="doc-1",
            current_slide=15,
            current_page=13,
        )
    )

    assert result["context_boundary"] == 15
    assert tools.vector_store.where == {
        "$and": [
            {"document_id": "doc-1"},
            {"slide_number": {"$lte": 15}},
        ]
    }


def test_get_saved_mindmap_is_scoped_to_user() -> None:
    tools = _tools()
    result = tools.get_saved_mindmap(
        GetSavedMindmapArgs(mindmap_id="mm_a1"), user_id="user-1"
    )

    assert result["status"] == "not_found"
    assert tools.mindmap_service.repository.request == ("user-1", "mm_a1")
