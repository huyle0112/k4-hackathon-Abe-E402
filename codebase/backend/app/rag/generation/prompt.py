SYSTEM_RULES = """Bạn là trợ giảng VLearn.
Chỉ trả lời dựa trên ngữ cảnh bài giảng được cung cấp.
Không bịa dữ kiện; nếu ngữ cảnh thiếu, hãy nói rõ giới hạn.
Ưu tiên kết nối kiến thức giữa các buổi và giữ trích dẫn file/trang."""


def build_prompt(question: str, contexts: list[str]) -> str:
    joined = "\n\n".join(f"[Nguồn {index + 1}] {text}" for index, text in enumerate(contexts))
    return f"{SYSTEM_RULES}\n\n{joined}\n\nCâu hỏi: {question}"
