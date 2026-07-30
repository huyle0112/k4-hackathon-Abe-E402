## Thành viên nhóm

| Tên thành viên | Mã sinh viên | Vai trò |
|---|---|---|
| Lê Hồ Quang Huy | 2A202602026 | Nhóm trưởng |
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
