# PDF RAG validation — 2026-07-30

## Environment

- Branch: `feat/pdf-rag-pipeline`
- Python: 3.13.2
- Embedding provider: `hash-ngram-384` local, không cần API key
- Vector store: ChromaDB local
- OCR engine: chưa cài; không cần cho hai PDF hiện tại

## PDF ingestion

| Chỉ số | Kết quả |
|---|---:|
| Số PDF | 2 |
| Tổng số trang | 58 |
| Trang đọc bằng text layer | 58 |
| Trang cần OCR | 0 |
| Trang rỗng | 0 |
| Tổng số chunk | 58 |
| Vector sau indexing | 58 |
| Vector sau re-index | 58 |

Re-index giữ nguyên 58 vector, xác nhận stable chunk ID và upsert không tạo
duplicate.

## Automated tests

- Kết quả: 14 tests passed.
- Dependency check: không có broken requirement.
- Bao phủ: normalization, PDF loading, page-aware chunking, idempotent
  indexing, retrieval, session filter, stale chunk cleanup, citation,
  abstention, RAG service và evaluation metrics.

## Smoke flows

| Flow | Kết quả |
|---|---|
| Câu hỏi trong một buổi | Trả lời extractive, có citation |
| Câu hỏi liên kết nhiều buổi | Trả lời extractive, có citation |
| Câu hỏi ngoài phạm vi | Abstain |

## Data safety

- `.gitignore` đã chặn nội dung mới trong `private-data/lessons/` và vẫn cho
  phép theo dõi `.gitkeep`.
- Hai PDF hiện tại đã được Git theo dõi từ trước, nên `.gitignore` không thể
  tự bỏ theo dõi chúng. Trong lần triển khai này không untrack hoặc xóa PDF để
  tuân thủ yêu cầu không xóa nếu chưa có sự đồng thuận.
- `.env`, môi trường Python local và vector store không được đưa vào Git.

## Known limitations

- Hash embedding là baseline offline, chủ yếu phản ánh lexical overlap.
- Chưa tích hợp semantic embedding model hoặc LLM provider thật.
- Confidence là heuristic và cần hiệu chỉnh bằng golden set tối thiểu 20 case.
- Chưa đánh giá answer correctness vì chưa có golden set thật được phép dùng.
- Diagram hoặc text nằm trong hình có thể cần OCR/vision với tài liệu khác.

Báo cáo này chỉ chứa số liệu tổng hợp, không chứa text slide, embedding, API
key hoặc vector database.
