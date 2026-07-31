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
