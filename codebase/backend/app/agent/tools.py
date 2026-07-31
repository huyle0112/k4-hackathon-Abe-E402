from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from app.mindmaps import CreateMindmapRequest, MindmapService
from app.rag.embeddings import EmbeddingProvider
from app.rag.retrieval.reranker import BaselineReranker
from app.rag.vector_store import ChromaVectorStore


class StrictToolArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SearchSlideEvidenceArgs(StrictToolArgs):
    query: str = Field(min_length=2, max_length=2000)
    document_id: str = Field(min_length=1)
    current_slide: int = Field(ge=1)
    current_page: int = Field(ge=1)
    top_k: int = Field(default=5, ge=1, le=10)


class GetSavedMindmapArgs(StrictToolArgs):
    mindmap_id: str = Field(pattern=r"^mm_[a-f0-9]+$")


class CreateMindmapArgs(StrictToolArgs):
    document_ids: list[str] = Field(min_length=1, max_length=20)
    prompt: str = Field(min_length=2, max_length=2000)


TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "search_slide_evidence",
        "description": (
            "Tìm nội dung trong đúng tài liệu đang mở. Tool chỉ dùng slide "
            "hiện tại hoặc các slide trước đó; page không giới hạn context."
        ),
        "strict": True,
        "parameters": SearchSlideEvidenceArgs.model_json_schema(),
    },
    {
        "type": "function",
        "name": "get_saved_mindmap",
        "description": (
            "Đọc mindmap cũ của chính người dùng từ SQLite bằng mindmap_id; "
            "không gọi LLM."
        ),
        "strict": True,
        "parameters": GetSavedMindmapArgs.model_json_schema(),
    },
    {
        "type": "function",
        "name": "create_mindmap",
        "description": (
            "Tạo mindmap từ các tài liệu người dùng chọn và prompt rõ ràng. "
            "Service tự trả bản cache trong SQLite nếu yêu cầu đã tồn tại."
        ),
        "strict": True,
        "parameters": CreateMindmapArgs.model_json_schema(),
    },
]


class AgentTools:
    """Server-side implementations for model-requested tool calls."""

    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider,
        vector_store: ChromaVectorStore,
        reranker: BaselineReranker,
        mindmap_service: MindmapService,
        candidate_k: int = 20,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.reranker = reranker
        self.mindmap_service = mindmap_service
        self.candidate_k = candidate_k

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        user_id: str,
    ) -> dict[str, Any]:
        if name == "search_slide_evidence":
            args = TypeAdapter(SearchSlideEvidenceArgs).validate_python(
                arguments
            )
            return self.search_slide_evidence(args)
        if name == "get_saved_mindmap":
            args = TypeAdapter(GetSavedMindmapArgs).validate_python(arguments)
            return self.get_saved_mindmap(args, user_id=user_id)
        if name == "create_mindmap":
            args = TypeAdapter(CreateMindmapArgs).validate_python(arguments)
            return self.create_mindmap(args, user_id=user_id)
        raise ValueError(f"Unknown agent tool: {name}")

    def search_slide_evidence(
        self, args: SearchSlideEvidenceArgs
    ) -> dict[str, Any]:
        # Page is UI/PDF state only; retrieval is bounded solely by slide.
        context_boundary = args.current_slide
        embedding = self.embedding_provider.embed_query(args.query)
        candidates = self.vector_store.query(
            embedding,
            n_results=max(self.candidate_k, args.top_k * 3),
            where={
                "$and": [
                    {"document_id": args.document_id},
                    {"slide_number": {"$lte": context_boundary}},
                ]
            },
        )
        hits = self.reranker.rerank(
            args.query,
            candidates,
            top_k=args.top_k,
            score_threshold=0.12,
        )
        return {
            "query": args.query,
            "document_id": args.document_id,
            "context_boundary": context_boundary,
            "evidence": [
                {
                    "chunk_id": hit.chunk.chunk_id,
                    "document_id": hit.chunk.document_id,
                    "source_file": hit.chunk.source_file,
                    "slide": hit.chunk.slide_number,
                    "page": hit.chunk.slide_number,
                    "text": hit.chunk.text,
                    "score": hit.score,
                }
                for hit in hits
            ],
        }

    def get_saved_mindmap(
        self, args: GetSavedMindmapArgs, *, user_id: str
    ) -> dict[str, Any]:
        row = self.mindmap_service.repository.find_by_id(
            user_id, args.mindmap_id
        )
        if row is None:
            return {"status": "not_found", "mindmap_id": args.mindmap_id}
        response = self.mindmap_service._from_row(row, status="cached")
        return response.model_dump(mode="json")

    def create_mindmap(
        self, args: CreateMindmapArgs, *, user_id: str
    ) -> dict[str, Any]:
        response = self.mindmap_service.create(
            CreateMindmapRequest(
                document_ids=args.document_ids,
                prompt=args.prompt,
            ),
            user_id=user_id,
        )
        return response.model_dump(mode="json")
