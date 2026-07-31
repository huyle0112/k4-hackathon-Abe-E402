"""
Courses API.

Endpoints:
  GET  /courses                         — Danh sách khóa học
  GET  /courses/{course_code}           — Chi tiết khóa học (days + slides)
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.rag.models import (
    Course,
    CourseSummary,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["courses"])


# ──────────────────────────────────────────────────────
#  Helper: load courses từ JSON config
# ──────────────────────────────────────────────────────

def _load_courses_config() -> dict:
    """Đọc file courses_config.json. Trả về {} nếu chưa có."""
    # Since get_settings() in the current codebase might not have courses_config,
    # we'll hardcode the default path to "courses_config.json" in the root of the backend folder.
    cfg_path = Path("courses_config.json")
    if not cfg_path.exists():
        logger.warning("courses_config.json không tìm thấy tại %s", cfg_path)
        return {}
    with cfg_path.open(encoding="utf-8") as f:
        return json.load(f)


# ──────────────────────────────────────────────────────
#  GET /courses
# ──────────────────────────────────────────────────────

@router.get(
    "/courses",
    response_model=list[CourseSummary],
    summary="Danh sách khóa học",
)
async def list_courses() -> list[CourseSummary]:
    """
    Trả về danh sách tất cả khóa học đang có.
    """
    config = _load_courses_config()
    courses = config.get("courses", [])
    result = []
    for c in courses:
        total_days = len(c.get("days", []))
        result.append(
            CourseSummary(
                code=c["code"],
                name=c["name"],
                description=c.get("description", ""),
                read_percent=0,
                total_days=total_days,
            )
        )
    return result


# ──────────────────────────────────────────────────────
#  GET /courses/{course_code}
# ──────────────────────────────────────────────────────

@router.get(
    "/courses/{course_code}",
    response_model=Course,
    summary="Chi tiết khóa học",
)
async def get_course(course_code: str) -> Course:
    """
    Trả về thông tin đầy đủ một khóa học: danh sách buổi học và slides.
    """
    config = _load_courses_config()
    courses = config.get("courses", [])

    course_data = next(
        (c for c in courses if c["code"].lower() == course_code.lower()),
        None,
    )
    if not course_data:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy khóa học '{course_code}'",
        )

    return Course(**course_data)