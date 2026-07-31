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

# PDF RAG backend

Backend này cung cấp pipeline RAG local cho slide PDF:

```text
PDF -> text/OCR -> normalize -> chunk -> embedding -> Chroma
    -> retrieval -> reranking -> generation -> citation
```

Khi không có `.env`, baseline mặc định không cần API key:

- Embedding: deterministic hash n-gram chạy local.
- Vector store: Chroma persistent local.
- Generation: extractive fallback dựa trên các chunk được truy xuất.
- OCR: Tesseract `vie+eng`, chỉ dùng khi đã cài và text layer không đủ tốt.

Hash embedding giúp phát triển và kiểm thử offline nhưng không thay thế một
multilingual semantic embedding model trong bản đánh giá chất lượng cuối.

## Thiết lập

Từ `codebase/backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Tạo `.env` local nếu cần thay đổi cấu hình. Không commit file này. Trước khi
chạy, phải điền các secret bắt buộc của provider đã chọn:

```powershell
Copy-Item .env.example .env
```

Các giá trị rỗng không ghi đè default an toàn từ `app/config.py`. Riêng khi
đã chọn `EMBEDDING_PROVIDER=openai`, thiếu model hoặc API key là lỗi cấu hình;
pipeline không âm thầm quay về hash embedding.

## Audit PDF không ghi index

```powershell
python scripts/ingest.py --dry-run --no-ocr
```

Kết quả JSON chỉ chứa metadata, số trang, số chunk và cảnh báo; không in toàn
bộ nội dung slide.

## Ingestion

```powershell
python scripts/ingest.py
```

Chỉ định folder hoặc manifest:

```powershell
python scripts/ingest.py --source ../../private-data/lessons
python scripts/ingest.py --manifest ../data-sample/lessons.example.json
```

Rebuild collection local:

```powershell
python scripts/ingest.py --rebuild
```

Vector database được lưu tại `vector-store/chroma/` và không được commit.
Ingestion dùng stable chunk ID và `upsert`, nên chạy lại không tạo duplicate.
Collection lưu embedding provider, model và dimension. Nếu một trong ba giá
trị thay đổi, lệnh thường sẽ dừng trước khi ghi để không trộn các loại vector.

## OpenAI semantic embedding

Cấu hình local trong `.env`:

```dotenv
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_API_KEY=
EMBEDDING_BASE_URL=
EMBEDDING_DIMENSION=3072
EMBEDDING_BATCH_SIZE=64
EMBEDDING_TIMEOUT_SECONDS=60
EMBEDDING_MAX_RETRIES=3
```

Để `EMBEDDING_BASE_URL` trống khi dùng endpoint OpenAI mặc định. API key chỉ
được đặt trong `.env` local, không đặt trong `.env.example`, source code, log
hoặc frontend.

Collection local hiện tại đã được tạo bằng
`openai:text-embedding-3-large:3072`. Chỉ khi chuyển từ một
provider/model/dimension khác sang cấu hình này mới phải chủ động rebuild:

```powershell
python scripts/ingest.py --rebuild
```

`--rebuild` xóa collection local đang chọn rồi index lại từ PDF. Không dùng
cờ này nếu chưa chủ động chấp nhận rebuild. Những lần ingestion tiếp theo với
cùng provider/model/dimension dùng `upsert` và không tạo duplicate.

OpenAI SDK quản lý timeout và số lần retry hữu hạn theo cấu hình. Unit tests
dùng mock client và không gọi API thật.

## OpenAI LLM generation

LLM là tùy chọn. Nếu `LLM_PROVIDER` và `LLM_MODEL` đều để trống, pipeline giữ
extractive fallback. Nếu đã chọn `LLM_PROVIDER=openai`, cả model và API key là
bắt buộc; cấu hình thiếu sẽ fail fast thay vì gửi request hoặc âm thầm đổi
provider.

```dotenv
LLM_PROVIDER=openai
LLM_MODEL=<model-hỗ-trợ-Structured-Outputs>
LLM_API_KEY=
LLM_BASE_URL=
LLM_REASONING_EFFORT=
LLM_MAX_OUTPUT_TOKENS=1200
LLM_TIMEOUT_SECONDS=60
LLM_MAX_RETRIES=2
```

Để `LLM_BASE_URL` trống khi dùng endpoint OpenAI mặc định. Chỉ điền
`LLM_REASONING_EFFORT` nếu model được chọn hỗ trợ tham số này. Không đặt API
key trong `.env.example`, source code, log hoặc frontend.

Generation dùng OpenAI Responses API với Pydantic Structured Outputs và
`store=False`. Pipeline không cấp tool cho model. System instruction, câu hỏi
và evidence được truyền tách biệt; slide được đánh dấu là dữ liệu không đáng
tin cậy. LLM chỉ đề xuất `cited_chunk_ids`; backend lọc ID không hợp lệ rồi tự
dựng lại tên PDF, số slide và excerpt từ các chunk thực sự đã gửi.

Nếu request LLM gặp timeout, rate limit, refusal, authentication/validation
error hoặc response không hoàn chỉnh, backend trả abstention có lý do rõ ràng.
Nó không âm thầm thay bằng extractive answer như thể LLM đã thành công.

Giới hạn context và coverage nhiều buổi:

```dotenv
RETRIEVAL_MIN_SESSION_EVIDENCE=1
GENERATION_MAX_CONTEXT_CHUNKS=8
GENERATION_MAX_CONTEXT_TOKENS=3500
```

Khi chỉ rõ ít nhất hai session, retriever lấy candidates riêng cho từng
session, merge, deduplicate và rerank, sau đó giữ quota nguồn tối thiểu của mỗi
session. Nếu thiếu nguồn hoặc citation ở một session, generator abstain. Query
không có filter vẫn dùng global retrieval và không bị ép lấy nguồn từ mọi PDF.

## Query local

Tất cả buổi học:

```powershell
python scripts/query.py "Context của LLM là gì?"
```

Chỉ một hoặc nhiều buổi:

```powershell
python scripts/query.py "Context của LLM là gì?" --sessions 1
python scripts/query.py "Liên hệ kiến thức giữa hai buổi" --sessions 1 2
```

Response JSON gồm `answer`, `confidence`, `abstained`, `citations` và
`retrieval_hits`. Khi có LLM, response còn có metadata generation đã lược bỏ
nội dung nhạy cảm, gồm mode, provider/model, latency, status, request ID và
token usage nếu API cung cấp.

Sau khi tự điền `.env`, người dùng có thể chủ động chạy một live smoke test:

```powershell
.\.venv\Scripts\python.exe scripts\query.py `
  "Context của LLM là gì?" --sessions 1
```

Lệnh này gọi embedding API cho query và gọi LLM API nếu LLM đã được cấu hình.
Không chạy lệnh live này trong automated tests.

## Chạy test

```powershell
python -m pytest -q
```

Tests tạo PDF và Chroma database trong temporary directory, dùng mock Responses
API và không gọi mạng. Dữ liệu test không được ghi vào repository.

## Chạy evaluation

Với golden set hợp lệ tối thiểu 20 case:

```powershell
python scripts/evaluate.py ../../eval/golden-set.json
```

Trong lúc phát triển có thể dùng bộ nhỏ hơn:

```powershell
python scripts/evaluate.py path/to/private-golden-set.json --allow-incomplete
```

Evaluator báo pass rate, abstention accuracy, retrieval/citation hit rate,
cross-session source coverage, citation precision và citation completeness mà
không ghi câu trả lời hoặc text nguồn vào repository.

## Chuyển sang model local

`EmbeddingProvider` và `TextGenerationProvider` là interface thay thế được.
Baseline hash/extractive có thể được đổi mà không sửa ingestion, vector-store
schema, retrieval hay citation.

Để dùng sentence-transformers local, cài package tương ứng, đặt:

```dotenv
EMBEDDING_PROVIDER=sentence-transformers
LOCAL_EMBEDDING_MODEL=<multilingual-model-name>
```

Không đưa model cache, API key hoặc `.env` vào Git.

## Hạn chế hiện tại

- Chưa chạy live LLM smoke test tự động; người dùng chủ động chạy sau khi kiểm
  tra cấu hình và chi phí.
- Chất lượng OpenAI semantic embedding cần được đo bằng golden set thật.
- Hash fallback chủ yếu phản ánh lexical overlap.
- OCR cần cài Tesseract ngoài Python và language data `vie+eng`.
- Diagram hoặc text nằm trong hình có thể cần vision extraction sau này.
- Confidence hiện là heuristic, phải hiệu chỉnh bằng golden set.
- Citation completeness hiện dựa trên chunk ID và expected source; đánh giá
  semantic support cho từng mệnh đề vẫn cần golden set/review thủ công.
