# VLearn Cross-session Tutor Backend

Backend FastAPI và pipeline RAG theo cấu trúc được mô tả trong README gốc. Hệ thống
đọc PDF theo trang/slide, lập chỉ mục cục bộ, tìm kiếm trong một hoặc nhiều buổi học,
trả lời có nguồn và từ chối khi độ tin cậy thấp.

## Cài đặt và chạy

Yêu cầu Python 3.11+.

```powershell
cd codebase\backend
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

API chính:

- `GET /health`: trạng thái và số chunk đã index.
- `POST /api/chat`: hỏi trong phạm vi `session_ids` hoặc `file_names`.
- `GET /docs`: Swagger UI.

Ví dụ request:

```json
{
  "question": "Attention liên quan thế nào đến LLM?",
  "session_ids": ["day-01", "day-02"],
  "top_k": 5
}
```

## Lập chỉ mục PDF

Chạy từ `codebase/backend`:

```powershell
python scripts\ingest.py ..\..\private-data\lessons\day-01-ai-llm-foundation.pdf --session day-01
python scripts\ingest.py ..\..\private-data\lessons\day-02-xac-dinh-bai-toan-ai.pdf --session day-02
```

Dữ liệu sinh ra nằm tại `vector-store/chunks.json` và không nên commit. Có thể đổi
đường dẫn bằng biến `VECTOR_STORE_PATH`. Các cấu hình khác gồm `CORS_ORIGINS`,
`TOP_K` và `CONFIDENCE_THRESHOLD`.

## Kiểm thử

```powershell
python -m pytest
```

MVP dùng embedding từ vựng cục bộ, không cần API key và không bịa câu trả lời ngoài
nguồn. `ocr.py` là điểm mở rộng rõ ràng cho PDF dạng ảnh; hiện hệ thống sẽ bỏ qua
trang không trích được text thay vì đoán nội dung.
