## Thành viên nhóm

| Tên thành viên | Mã sinh viên | Vai trò |
|---|---|---|
| Lê Hồ Quang Huy | 2A202602026 | Nhóm trưởng / Backend Developer + AI tools |
| Lã Phan Hoài An | 2A202601846 | Agent |
| Nguyễn Tiến Đạt | 2A202601678 | Agent |
| Kiều Phúc Huy | 2A202601056 | Front-end Developer |
| Nguyễn Nam Phong | 2A202601320 | Backend Developer |

## Phân công vai trò

| Thành viên | Vai trò | Phụ trách chính | Artifact/Module |
|---|---|---|---|
| Lê Hồ Quang Huy | Product/Tech Lead, Backend & AI Integration | Chốt lát cắt sản phẩm, kiến trúc tổng thể, quản lý checkpoint, tích hợp pipeline xử lý PDF, backend và RAG, đồng thời bảo đảm bản build khớp AI Spec | `spec.md`, tích hợp trong `codebase/backend/`, `README.md`, changelog |
| Lã Phan Hoài An | Data & RAG Ingestion Engineer | Xây pipeline trích xuất nội dung từ PDF, xử lý OCR khi cần, chuẩn hóa văn bản, chia chunk theo trang/slide, gắn metadata buổi học và xây index dữ liệu | Pipeline ingestion/indexing trong `codebase/backend/` |
| Nguyễn Tiến Đạt | Retrieval & LLM Engineer | Xây retrieval một buổi và nhiều buổi trên dữ liệu trích xuất từ PDF, reranking, prompt, citation theo file/trang/slide, confidence, abstention và xử lý câu hỏi ngoài phạm vi | Retrieval/generation trong `codebase/backend/`, prompt và AI traces |
| Kiều Phúc Huy | Front-end & UX Engineer | Xây giao diện chatbot, hiển thị và mở nguồn trích dẫn theo file PDF/trang/slide, lựa chọn buổi học và bốn flow happy path/low-confidence/failure/correction | `codebase/frontend/`, hỗ trợ demo flow |
| Nguyễn Nam Phong | Backend API & Evaluation Engineer | Xây API giữa frontend và RAG, quản lý ingestion/indexing PDF và cấu hình runtime, tự động hóa golden set, chạy đánh giá và tổng hợp kết quả | Backend API trong `codebase/backend/`, `eval/` |

## Cấu trúc repository

```text
.
├── README.md                         # Tổng quan dự án, thành viên và phân công
├── spec.md                           # AI Spec, thiết kế, kiểm thử và kế hoạch
├── .gitignore                        # Quy tắc loại trừ file local và dữ liệu sinh ra
├── codebase/
│   ├── backend/                      # Backend API và pipeline RAG
│   │   ├── README.md                 # Tài liệu backend
│   │   ├── requirements.txt          # Dependency Python
│   │   ├── app/
│   │   │   ├── main.py               # Điểm khởi chạy ứng dụng backend
│   │   │   ├── config.py             # Cấu hình runtime
│   │   │   ├── api/
│   │   │   │   ├── chat.py           # API hỏi đáp chatbot
│   │   │   │   └── health.py         # API kiểm tra trạng thái dịch vụ
│   │   │   └── rag/
│   │   │       ├── models.py         # Schema dữ liệu, chunk, nguồn và response
│   │   │       ├── embeddings.py     # Tạo embedding cho nội dung đã trích xuất
│   │   │       ├── vector_store.py   # Giao tiếp với vector store
│   │   │       ├── ingestion/
│   │   │       │   ├── pdf_loader.py # Đọc nội dung theo trang PDF
│   │   │       │   ├── ocr.py        # OCR dự phòng cho slide dạng ảnh
│   │   │       │   ├── normalizer.py # Làm sạch và chuẩn hóa văn bản
│   │   │       │   ├── chunker.py    # Chia chunk theo trang/slide
│   │   │       │   └── indexer.py    # Tạo và cập nhật index
│   │   │       ├── retrieval/
│   │   │       │   ├── retriever.py  # Truy xuất một hoặc nhiều buổi học
│   │   │       │   ├── reranker.py   # Xếp hạng lại kết quả truy xuất
│   │   │       │   └── filters.py    # Lọc theo tài liệu, buổi và slide
│   │   │       └── generation/
│   │   │           ├── prompt.py      # Prompt và quy tắc tạo câu trả lời
│   │   │           ├── generator.py   # Gọi LLM và sinh câu trả lời
│   │   │           └── citations.py   # Tạo citation theo PDF/trang/slide
│   │   ├── scripts/
│   │   │   └── ingest.py              # Lệnh chạy ingestion/indexing
│   │   └── tests/
│   │       ├── test_api.py            # Kiểm thử API
│   │       ├── test_ingestion.py      # Kiểm thử xử lý PDF và indexing
│   │       ├── test_retrieval.py      # Kiểm thử retrieval
│   │       └── test_generation.py     # Kiểm thử generation và citation
│   ├── data-sample/
│   │   └── README.md                  # Quy ước PDF mẫu an toàn để commit
│   └── fe/                            # Frontend React, TypeScript và Vite
│       ├── README.md                  # Hướng dẫn frontend
│       ├── package.json               # Dependency và npm scripts
│       ├── package-lock.json          # Khóa phiên bản dependency
│       ├── vite.config.ts             # Cấu hình Vite
│       ├── tsconfig*.json             # Cấu hình TypeScript
│       ├── eslint.config.js           # Cấu hình ESLint
│       ├── components.json            # Cấu hình shadcn/ui
│       ├── index.html                 # HTML entrypoint
│       ├── public/                    # PDF worker, slide và static assets
│       └── src/
│           ├── main.tsx               # Entry point React
│           ├── App.tsx                # Router và application shell
│           ├── index.css              # Style toàn cục
│           ├── pages/                 # Các màn hình của ứng dụng
│           ├── components/            # UI, dashboard, reader và welcome
│           ├── hooks/                 # Hook đọc và quản lý tài liệu PDF
│           ├── lib/                   # Tiện ích chung và xử lý PDF
│           ├── data/                  # Metadata slide dùng bởi frontend
│           ├── slides/                # Bản PDF dùng trong source frontend
│           └── assets/                # Tài nguyên giao diện
├── private-data/
│   └── lessons/
│       ├── day-01-ai-llm-foundation.pdf
│       └── day-02-xac-dinh-bai-toan-ai.pdf
│                                      # PDF bài học
├── eval/                              # Golden set và kết quả đánh giá
├── validation/                        # Evidence kiểm chứng và demo
└── reflection/                        # Reflection cá nhân của thành viên
```

Các file `__init__.py` đánh dấu Python package. Các file `.gitkeep` chỉ dùng để
giữ thư mục rỗng trên Git và không chứa dữ liệu nghiệp vụ. `vector-store/`,
embedding, API key, file `.env` và PDF bài học thật không được commit.
