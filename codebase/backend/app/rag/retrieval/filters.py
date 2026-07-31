from __future__ import annotations

from typing import Any


def build_session_filter(
    session_numbers: list[int] | None,
) -> dict[str, Any] | None:
    if not session_numbers:
        return None
    unique_sessions = sorted(set(session_numbers))
    if any(session < 1 for session in unique_sessions):
        raise ValueError("Session numbers must be positive")
    if len(unique_sessions) == 1:
        return {"session_number": unique_sessions[0]}
    return {"session_number": {"$in": unique_sessions}}

from app.rag.models import Chunk


def in_scope(chunk: Chunk, session_ids: list[str], file_names: list[str]) -> bool:
    return (
        (not session_ids or chunk.session_id in session_ids)
        and (not file_names or chunk.file_name in file_names)
    )
