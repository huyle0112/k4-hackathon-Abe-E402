from app.rag.ingestion.chunker import chunk_page


def test_chunk_page_preserves_source_metadata():
    chunks = chunk_page("Nội dung về mô hình ngôn ngữ. " * 100, "lesson.pdf", "day-01", 2, 200, 20)
    assert len(chunks) > 1
    assert all(item.page == 2 and item.session_id == "day-01" for item in chunks)
    assert all(item.embedding for item in chunks)
