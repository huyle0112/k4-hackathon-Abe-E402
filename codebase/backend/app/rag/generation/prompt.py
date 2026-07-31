from __future__ import annotations

from app.rag.models import SearchHit


SYSTEM_INSTRUCTION = """Bạn là trợ lý học tập chỉ trả lời dựa trên nguồn được
cung cấp. Không sử dụng kiến thức ngoài nguồn. Nếu nguồn không đủ, hãy nói rõ
không đủ căn cứ. Mọi ý chính phải có citation theo đúng chunk_id, file PDF và
số slide. Trả lời bằng tiếng Việt, ngắn gọn và trực tiếp."""


def build_generation_prompt(query: str, hits: list[SearchHit]) -> str:
    contexts: list[str] = []
    for hit in hits:
        contexts.append(
            "\n".join(
                [
                    f"[chunk_id={hit.chunk.chunk_id}]",
                    f"[source={hit.chunk.source_file}]",
                    f"[slide={hit.chunk.slide_number}]",
                    hit.chunk.text,
                ]
            )
        )
    joined_context = "\n\n---\n\n".join(contexts)
    return (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"CÂU HỎI:\n{query}\n\n"
        f"NGUỒN:\n{joined_context}\n\n"
        "YÊU CẦU: Trả lời chỉ từ NGUỒN. Nếu không đủ nguồn, hãy từ chối."
    )
