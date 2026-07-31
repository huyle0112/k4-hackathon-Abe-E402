from app.rag.models import Chunk


def in_scope(chunk: Chunk, session_ids: list[str], file_names: list[str]) -> bool:
    return (
        (not session_ids or chunk.session_id in session_ids)
        and (not file_names or chunk.file_name in file_names)
    )
