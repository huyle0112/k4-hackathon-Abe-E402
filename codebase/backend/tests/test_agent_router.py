from app.agent.router import route_chat_prompt


def test_normal_question_uses_rag() -> None:
    assert route_chat_prompt("Double Diamond là gì?").intent == "rag"


def test_greeting_does_not_use_rag() -> None:
    assert route_chat_prompt("Xin chào").intent == "greeting"
    assert route_chat_prompt("Bạn là ai?").intent == "greeting"
    assert route_chat_prompt("Bạn làm được gì?").intent == "greeting"


def test_explicit_lesson_reference_is_preserved_for_linking() -> None:
    route = route_chat_prompt(
        "Các từ khóa này liên quan gì đến bài học 1?"
    )
    assert route.intent == "rag"
    assert route.referenced_sessions == (1,)


def test_summary_defaults_to_current_lesson() -> None:
    route = route_chat_prompt("Tóm tắt nội dung chính của bài này")
    assert route.intent == "summary"
    assert route.summary_scope == "current_lesson"


def test_summary_can_load_previous_lessons() -> None:
    route = route_chat_prompt("Tóm tắt tất cả bài trước đó")
    assert route.intent == "summary"
    assert route.summary_scope == "previous_lessons"


def test_implicit_previous_lesson_question_is_a_summary() -> None:
    route = route_chat_prompt("Nội dung của bài trước là gì?")
    assert route.intent == "summary"
    assert route.summary_scope == "previous_lessons"


def test_slide_terms_question_uses_exact_slide_context() -> None:
    route = route_chat_prompt(
        "Slide này có những thuật ngữ nào cần chú ý?"
    )
    assert route.intent == "current_slide"


def test_lesson_focus_question_uses_full_lesson_context() -> None:
    route = route_chat_prompt("Bài học này cần chú ý vào phần nào?")
    assert route.intent == "summary"
    assert route.summary_scope == "current_lesson"


def test_summary_can_load_through_current_lesson() -> None:
    route = route_chat_prompt("Tóm tắt từ đầu đến bài hiện tại")
    assert route.intent == "summary"
    assert route.summary_scope == "through_current"
