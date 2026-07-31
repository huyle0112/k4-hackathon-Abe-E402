from app.rag.generation.generator import generate_answer
from app.rag.models import Chunk, SearchHit


def test_generation_abstains_when_confidence_is_low():
    chunk = Chunk(id="x", text="Một đoạn nội dung bài giảng đủ dài để làm nguồn.", file_name="a.pdf", session_id="d1", page=3)
    response = generate_answer("câu hỏi", [SearchHit(chunk=chunk, score=0.01)], 0.12)
    assert response.status == "low_confidence"
    assert response.citations[0].page == 3
