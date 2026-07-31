# PDF RAG backend

Backend này cung cấp pipeline RAG local cho slide PDF:

```text
PDF -> text/OCR -> normalize -> chunk -> embedding -> Chroma
    -> retrieval -> reranking -> generation -> citation
```

Baseline mặc định không cần API key:

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

Tạo `.env` local nếu cần thay đổi cấu hình. Không commit file này:

```powershell
Copy-Item .env.example .env
```

Các giá trị rỗng trong `.env` sử dụng default an toàn từ `app/config.py`.

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
`retrieval_hits`.

## Chạy test

```powershell
python -m pytest -q
```

Tests tạo PDF và Chroma database trong temporary directory. Dữ liệu test không
được ghi vào repository.

## Chạy evaluation

Với golden set hợp lệ tối thiểu 20 case:

```powershell
python scripts/evaluate.py ../../eval/golden-set.json
```

Trong lúc phát triển có thể dùng bộ nhỏ hơn:

```powershell
python scripts/evaluate.py path/to/private-golden-set.json --allow-incomplete
```

Evaluator báo pass rate, abstention accuracy, retrieval hit rate và citation
hit rate mà không ghi câu trả lời hoặc text nguồn vào repository.

## Chuyển sang model local hoặc API sau này

`EmbeddingProvider` và `TextGenerationProvider` là interface thay thế được.
Baseline hash/extractive có thể được đổi mà không sửa ingestion, vector-store
schema, retrieval hay citation.

Để dùng sentence-transformers local, cài package tương ứng, đặt:

```dotenv
EMBEDDING_PROVIDER=sentence-transformers
LOCAL_EMBEDDING_MODEL=<multilingual-model-name>
```

Để dùng OpenAI API, cập nhật `.env`:

```dotenv
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSION=3072
EMBEDDING_API_KEY=sk-...
```

**Lưu ý quan trọng**: Khi thay đổi Provider, Model hoặc Dimension (ví dụ từ Hash sang OpenAI), bạn **bắt buộc phải xóa index cũ và tạo lại** vì các vector khác dimension/model không thể lưu chung. Hãy chạy lệnh sau:

```powershell
python scripts/ingest.py --rebuild
```

Không đưa model cache, API key hoặc `.env` vào Git.

## Hạn chế hiện tại

- Chưa có LLM provider thật.
- Hash embedding chủ yếu phản ánh lexical overlap.
- OCR cần cài Tesseract ngoài Python và language data `vie+eng`.
- Diagram hoặc text nằm trong hình có thể cần vision extraction sau này.
- Confidence hiện là heuristic, phải hiệu chỉnh bằng golden set.
