from __future__ import annotations

from app.rag.generation.generator import AnswerGenerator
from app.agent.router import LLMTaskRouter, route_chat_prompt
from app.rag.models import ChatResponse, RetrievalRequest, SearchHit
from app.rag.retrieval.retriever import Retriever


class RAGService:
    def __init__(
        self,
        *,
        retriever: Retriever,
        generator: AnswerGenerator,
        task_router: LLMTaskRouter | None = None,
    ) -> None:
        self.retriever = retriever
        self.generator = generator
        self.task_router = task_router

    def ask(
        self,
        query: str,
        *,
        document_id: str | None = None,
        session_numbers: list[int] | None = None,
        max_slide: int | None = None,
        top_k: int = 5,
    ) -> ChatResponse:
        route = (
            self.task_router.route(query)
            if self.task_router is not None
            else route_chat_prompt(query)
        )
        if route.intent == "greeting":
            return ChatResponse(
                answer=(
                    "Xin chào! Mình là VLearn Tutor, một trợ lý AI hỗ trợ "
                    "học tập từ tài liệu của khóa học. Mình có thể giải thích "
                    "nội dung slide hiện tại, trả lời câu hỏi có dẫn nguồn, "
                    "tóm tắt một hoặc nhiều bài học, liên hệ kiến thức giữa "
                    "các buổi và hỗ trợ tạo mindmap từ tài liệu bạn chọn."
                ),
                confidence=1.0,
                abstained=False,
                status="answered",
                important_keywords=["VLearn Tutor", "AI"],
                citations=[],
                retrieval_hits=[],
            )
        if route.intent == "current_slide" and document_id and max_slide:
            return self._answer_current_slide(
                query,
                document_id=document_id,
                current_slide=max_slide,
            )
        if route.intent == "summary" and document_id:
            return self._summarize(
                query,
                document_id=document_id,
                scope=route.summary_scope or "current_lesson",
            )
        if route.referenced_sessions and document_id and max_slide:
            return self._answer_linked_lessons(
                query,
                document_id=document_id,
                current_slide=max_slide,
                referenced_sessions=list(route.referenced_sessions),
                top_k=top_k,
            )
        request = RetrievalRequest(
            query=query,
            document_id=document_id,
            session_numbers=session_numbers,
            max_slide=max_slide,
            top_k=top_k,
        )
        hits = self.retriever.retrieve(request)
        required_sessions = (
            request.session_numbers
            if request.session_numbers
            and len(request.session_numbers) >= 2
            else None
        )
        generated = self.generator.generate(
            request.query,
            hits,
            required_session_numbers=required_sessions,
        )
        return ChatResponse(
            **generated.model_dump(),
            status="no_context" if generated.abstained else "answered",
            retrieval_hits=hits,
        )

    def _answer_current_slide(
        self,
        query: str,
        *,
        document_id: str,
        current_slide: int,
    ) -> ChatResponse:
        chunks = self.retriever.vector_store.get_chunks(
            where={
                "$and": [
                    {"document_id": document_id},
                    {"slide_number": current_slide},
                ]
            }
        )
        hits = [
            SearchHit(
                chunk=chunk,
                score=1.0,
                vector_score=1.0,
                lexical_score=1.0,
                rank=index,
            )
            for index, chunk in enumerate(chunks, start=1)
        ]
        generated = self.generator.generate(
            query, hits, trusted_context=True
        )
        return ChatResponse(
            **generated.model_dump(),
            status="no_context" if generated.abstained else "answered",
            retrieval_hits=hits,
        )

    def _answer_linked_lessons(
        self,
        query: str,
        *,
        document_id: str,
        current_slide: int,
        referenced_sessions: list[int],
        top_k: int,
    ) -> ChatResponse:
        current_document = self.retriever.vector_store.get_chunks(
            where={"document_id": document_id}
        )
        current_session = (
            current_document[0].session_number if current_document else None
        )
        referenced_sessions = sorted(
            {
                session
                for session in referenced_sessions
                if session != current_session
            }
        )
        if not referenced_sessions:
            request = RetrievalRequest(
                query=query,
                document_id=document_id,
                max_slide=current_slide,
                top_k=top_k,
            )
            hits = self.retriever.retrieve(request)
            generated = self.generator.generate(query, hits)
            return ChatResponse(
                **generated.model_dump(),
                status=(
                    "no_context" if generated.abstained else "answered"
                ),
                retrieval_hits=hits,
            )

        current_chunks = self.retriever.vector_store.get_chunks(
            where={
                "$and": [
                    {"document_id": document_id},
                    {"slide_number": current_slide},
                ]
            }
        )
        current_hits = [
            SearchHit(
                chunk=chunk,
                score=1.0,
                vector_score=1.0,
                lexical_score=1.0,
                rank=index,
            )
            for index, chunk in enumerate(current_chunks, start=1)
        ]
        reference_query = "\n".join(
            [
                query,
                "Nội dung slide hiện tại cần liên kết:",
                *[chunk.text for chunk in current_chunks],
            ]
        )
        reference_hits = self.retriever.retrieve(
            RetrievalRequest(
                query=reference_query,
                session_numbers=referenced_sessions,
                top_k=top_k,
            )
        )
        overview_chunks = self.retriever.vector_store.get_chunks(
            where={
                "$and": [
                    {
                        "session_number": {
                            "$in": referenced_sessions
                        }
                    },
                    {"slide_number": {"$lte": 3}},
                ]
            }
        )
        overview_hits = [
            SearchHit(
                chunk=chunk,
                score=1.0,
                vector_score=1.0,
                lexical_score=1.0,
                rank=index,
            )
            for index, chunk in enumerate(overview_chunks, start=1)
        ]
        hits_by_id = {
            hit.chunk.chunk_id: hit
            for hit in current_hits + overview_hits + reference_hits
        }
        hits = list(hits_by_id.values())
        hits = [
            hit.model_copy(update={"rank": rank})
            for rank, hit in enumerate(hits, start=1)
        ]
        required_sessions = sorted(
            {
                *referenced_sessions,
                *(
                    [current_session]
                    if current_session is not None
                    else []
                ),
            }
        )
        generation_query = (
            f"{query}\n\n"
            "QUY ƯỚC NGỮ CẢNH: Các cụm như “các từ khóa này”, “nội dung "
            "này” hoặc “phần này” chỉ nội dung của slide hiện tại được cung "
            "cấp trong evidence. Hãy dùng slide hiện tại làm vế thứ nhất và "
            "bài học được nhắc rõ làm vế thứ hai để giải thích mối liên hệ."
        )
        generated = self.generator.generate(
            generation_query,
            hits,
            required_session_numbers=required_sessions,
            trusted_context=True,
        )
        return ChatResponse(
            **generated.model_dump(),
            status="no_context" if generated.abstained else "answered",
            retrieval_hits=hits,
        )

    def _summarize(
        self, query: str, *, document_id: str, scope: str
    ) -> ChatResponse:
        current_chunks = self.retriever.vector_store.get_chunks(
            where={"document_id": document_id}
        )        
        if not current_chunks:
            generated = self.generator.generate(
                query, [], trusted_context=True
            )
            return ChatResponse(
                **generated.model_dump(),
                status="no_context",
                retrieval_hits=[],
            )

        current_session = current_chunks[0].session_number
        if scope == "previous_lessons":
            where = {"session_number": {"$lt": current_session}}
        elif scope == "through_current":
            where = {"session_number": {"$lte": current_session}}
        else:
            where = {"document_id": document_id}
        chunks = self.retriever.vector_store.get_chunks(where=where)
        hits = [
            SearchHit(
                chunk=chunk,
                score=1.0,
                vector_score=1.0,
                lexical_score=1.0,
                rank=index,
            )
            for index, chunk in enumerate(chunks, start=1)
        ]
        required_sessions = (
            sorted({chunk.session_number for chunk in chunks})
            if scope in {"previous_lessons", "through_current"}
            else None
        )
        generated = self.generator.generate(
            query,
            hits,
            required_session_numbers=required_sessions,
            trusted_context=True,
        )
        # Summary context is an internal input, not a retrieval result. The
        # client receives the synthesized summary without RAG-style sources.
        generated = generated.model_copy(update={"citations": []})
        return ChatResponse(
            **generated.model_dump(),
            status="no_context" if generated.abstained else "answered",
            retrieval_hits=[],
        )
