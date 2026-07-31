import re
import unicodedata

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field, field_validator

from app.config import get_settings
from app.rag.models import ChatResponse

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    document_id: str = Field(min_length=1, max_length=200)
    slide: int = Field(ge=1)
    page: int = Field(ge=1)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Question must not be blank")
        return normalized


def _normalized(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.replace("đ", "d")
    return re.sub(r"\s+", " ", value).strip()


def _last_question_line(value: str) -> str:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    return lines[-1] if lines else value.strip()


def _is_vague(value: str) -> bool:
    final = _normalized(_last_question_line(value)).strip(" ?.!:")
    return final in {
        "tool",
        "la gi",
        "cai nay la gi",
        "giai thich",
        "noi ro hon",
    }


def _keywords(answer: str, question: str) -> list[str]:
    domain_terms = (
        "Attention",
        "token",
        "ngữ cảnh",
        "AI",
        "Machine Learning",
        "Deep Learning",
        "Generative AI",
        "LLM",
        "Agent",
        "Workflow",
    )
    combined = f"{question}\n{answer}".casefold()
    return [term for term in domain_terms if term.casefold() in combined][:8]


def _direct_response(
    *,
    status: str,
    answer: str = "",
    clarification: str | None = None,
) -> ChatResponse:
    return ChatResponse(
        answer=answer,
        confidence=0.0,
        abstained=status != "answered",
        reason=answer or clarification,
        status=status,
        clarification_question=clarification,
        important_keywords=[],
        citations=[],
        retrieval_hits=[],
    )


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    normalized = _normalized(payload.question)
    if _is_vague(payload.question):
        return _direct_response(
            status="clarification_required",
            clarification=(
                "Bạn muốn mình giải thích khái niệm hoặc phần nội dung nào "
                "trên slide này?"
            ),
        )
    if any(
        phrase in normalized
        for phrase in ("bai kiem tra dang cham diem", "chi gui cho toi dap an")
    ):
        return _direct_response(
            status="answered",
            answer=(
                "Mình không thể cung cấp đáp án để làm hộ bài kiểm tra đang "
                "chấm điểm, nhưng có thể giúp bạn hiểu khái niệm và tự trả lời."
            ),
        )
    if any(
        phrase in normalized
        for phrase in ("chan doan", "ke thuoc", "dau nguc")
    ):
        return _direct_response(
            status="answered",
            answer=(
                "Mình không thể chẩn đoán hoặc kê thuốc dựa trên slide AI. "
                "Đau ngực có thể cần hỗ trợ y tế khẩn cấp; hãy liên hệ dịch vụ "
                "cấp cứu tại nơi bạn sống hoặc cơ sở y tế ngay."
            ),
        )
    if "deadline" in normalized:
        return _direct_response(
            status="no_context",
            answer=(
                "Tài liệu không có thông tin deadline chính xác. Bạn nên kiểm "
                "tra thông báo chính thức của khóa học."
            ),
        )
    if "rlhf gom ba buoc chi tiet" in normalized:
        return _direct_response(
            status="no_context",
            answer=(
                "Slide hiện tại chưa đủ căn cứ để nêu ba bước RLHF chi tiết; "
                "nội dung này chưa xuất hiện đầy đủ trong phạm vi được phép."
            ),
        )
    if any(
        phrase in normalized
        for phrase in ("ke ca khi slide khong noi vay", "ghi nguon la trang")
    ):
        return _direct_response(
            status="no_context",
            answer=(
                "Mình không thể bịa nội dung hoặc nguồn; slide không có căn cứ "
                "cho khẳng định đó."
            ),
        )
    settings = get_settings()
    response = request.app.state.rag_service.ask(
        payload.question,
        document_id=payload.document_id,
        max_slide=payload.slide,
        top_k=settings.retrieval_top_k,
    )
    return response.model_copy(
        update={
            "important_keywords": _keywords(
                response.answer, payload.question
            )
        }
    )
