from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, Field


ChatIntent = Literal["summary", "rag", "current_slide", "greeting"]
SummaryScope = Literal[
    "current_lesson", "previous_lessons", "through_current"
]


@dataclass(frozen=True)
class ChatRoute:
    intent: ChatIntent
    summary_scope: SummaryScope | None = None
    referenced_sessions: tuple[int, ...] = ()


TASK_ROUTER_SYSTEM_PROMPT = """Bạn là bộ định tuyến task cho trợ lý học tập.
Chỉ phân loại cách backend phải lấy context; không trả lời câu hỏi của người dùng.

Chọn đúng một task:
- greeting: lời chào, hỏi trợ lý là ai, có chức năng gì hoặc có thể giúp gì.
- current_slide: câu hỏi yêu cầu đọc, liệt kê, giải thích, tìm thuật ngữ hoặc
  điểm cần chú ý trên "slide này", "trang này", "phần này".
- current_lesson: yêu cầu tổng quan, tóm tắt, nội dung chính hoặc phần cần chú ý
  của toàn bộ bài/buổi hiện tại.
- previous_lessons: yêu cầu nội dung/tổng kết các bài hoặc buổi trước.
- through_current: yêu cầu tổng hợp từ đầu đến bài hiện tại.
- linked_lessons: yêu cầu liên hệ/so sánh nội dung hiện tại với bài, buổi hoặc
  day được nêu bằng số. Trích các số đó vào referenced_sessions.
- rag_search: câu hỏi kiến thức cụ thể cần tìm đoạn evidence liên quan.

Quy tắc:
- "slide này có những thuật ngữ nào cần chú ý" là current_slide.
- "bài học này cần chú ý vào phần nào" là current_lesson.
- Không chọn rag_search cho yêu cầu cần đọc toàn bộ slide hoặc toàn bộ bài.
- referenced_sessions để [] nếu prompt không nêu số bài/buổi/day."""


class TaskRouteOutput(BaseModel):
    task: Literal[
        "greeting",
        "current_slide",
        "current_lesson",
        "previous_lessons",
        "through_current",
        "linked_lessons",
        "rag_search",
    ]
    referenced_sessions: list[int]


class LLMTaskRouter:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 2,
        client: Any | None = None,
    ) -> None:
        if client is None:
            from openai import OpenAI

            options: dict[str, Any] = {
                "api_key": api_key,
                "timeout": timeout,
                "max_retries": max_retries,
            }
            if base_url:
                options["base_url"] = base_url
            client = OpenAI(**options)
        self.client = client
        self.model = model

    def route(self, prompt: str) -> ChatRoute:
        try:
            response = self.client.responses.parse(
                model=self.model,
                instructions=TASK_ROUTER_SYSTEM_PROMPT,
                input=prompt,
                text_format=TaskRouteOutput,
                store=False,
                tools=[],
                max_output_tokens=120,
            )
            output = TaskRouteOutput.model_validate(
                response.output_parsed
            )
        except Exception:
            return route_chat_prompt(prompt)
        sessions = tuple(sorted(set(output.referenced_sessions)))
        if output.task == "greeting":
            return ChatRoute(intent="greeting")
        if output.task == "current_slide":
            return ChatRoute(intent="current_slide")
        if output.task == "current_lesson":
            return ChatRoute(intent="summary", summary_scope="current_lesson")
        if output.task == "previous_lessons":
            return ChatRoute(
                intent="summary", summary_scope="previous_lessons"
            )
        if output.task == "through_current":
            return ChatRoute(
                intent="summary", summary_scope="through_current"
            )
        if output.task == "linked_lessons":
            return ChatRoute(
                intent="rag", referenced_sessions=sessions
            )
        return ChatRoute(intent="rag")


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", value.replace("đ", "d")).strip()


def route_chat_prompt(prompt: str) -> ChatRoute:
    normalized = _normalize(prompt)
    greeting_text = normalized.strip(" ?!.")
    greeting_markers = {
        "xin chao",
        "chao",
        "hello",
        "hi",
        "hey",
        "ban la ai",
        "ban lam duoc gi",
        "ban co chuc nang gi",
        "ban co the giup gi",
        "tutor la gi",
    }
    if (
        greeting_text in greeting_markers
        or greeting_text.startswith("xin chao ")
        or greeting_text.startswith("chao tutor")
    ):
        return ChatRoute(intent="greeting")
    referenced_sessions = tuple(
        sorted(
            {
                int(match)
                for match in re.findall(
                    r"\b(?:bai(?: hoc)?|buoi|day)\s*0*(\d+)\b",
                    normalized,
                )
            }
        )
    )
    previous_lesson_markers = (
        "noi dung cua bai truoc",
        "noi dung bai truoc",
        "bai truoc hoc gi",
        "bai truoc noi gi",
        "bai truoc noi ve gi",
        "buoi truoc hoc gi",
        "buoi truoc noi gi",
        "buoi truoc noi ve gi",
    )
    if any(marker in normalized for marker in previous_lesson_markers):
        return ChatRoute(intent="summary", summary_scope="previous_lessons")

    current_lesson_markers = (
        "noi dung cua bai nay",
        "noi dung bai nay",
        "bai nay hoc gi",
        "bai nay noi gi",
        "bai nay noi ve gi",
        "buoi nay hoc gi",
        "buoi nay noi ve gi",
        "bai hoc nay can chu y",
        "bai nay can chu y",
    )
    if any(marker in normalized for marker in current_lesson_markers):
        return ChatRoute(intent="summary", summary_scope="current_lesson")

    current_slide_markers = (
        "slide nay",
        "trang nay",
        "phan nay",
        "doan nay",
    )
    if any(marker in normalized for marker in current_slide_markers):
        return ChatRoute(intent="current_slide")

    summary_markers = (
        "tom tat",
        "tong ket",
        "tong quan",
        "overview",
        "summary",
        "cac y chinh",
        "noi dung chinh",
    )
    if not any(marker in normalized for marker in summary_markers):
        return ChatRoute(
            intent="rag", referenced_sessions=referenced_sessions
        )

    through_current = (
        "tu dau den bai hien tai",
        "tu bai dau den bai nay",
        "tat ca bai den hien tai",
    )
    if any(marker in normalized for marker in through_current):
        return ChatRoute(intent="summary", summary_scope="through_current")

    previous = (
        "cac bai truoc",
        "tat ca bai truoc",
        "nhung buoi truoc",
        "cac buoi truoc",
    )
    if any(marker in normalized for marker in previous):
        return ChatRoute(intent="summary", summary_scope="previous_lessons")

    return ChatRoute(intent="summary", summary_scope="current_lesson")
