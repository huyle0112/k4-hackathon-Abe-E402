# Dữ liệu PDF mẫu cho pipeline RAG

Thư mục này chỉ dành cho PDF giả, PDF nhỏ được phép chia sẻ hoặc tài liệu mẫu
có giấy phép phù hợp để kiểm thử pipeline. Không đặt slide khóa học đầy đủ, dữ
liệu nhạy cảm, embedding hoặc vector database tại đây.

PDF thật của các buổi học phải được đặt trên máy local trong:

```text
private-data/lessons/
```

Các file trong `private-data/lessons/` không được commit, ngoại trừ
`.gitkeep`.

## Quy ước đầu vào PDF

- Mỗi PDF biểu diễn một buổi học.
- Tên file phải ổn định, dễ nhận biết và không chứa thông tin nhạy cảm.
- Mỗi trang PDF được xem là một slide; số trang là `slide_number`.
- PDF có text sẽ được trích xuất trực tiếp.
- Trang không có text hoặc chỉ chứa ảnh sẽ dùng OCR làm phương án dự phòng.
- Hình, bảng và sơ đồ quan trọng cần được trích xuất hoặc mô tả để không làm
  mất ngữ nghĩa.

Không tạo PDF rỗng để làm dữ liệu mẫu vì đó không phải file PDF hợp lệ. Nếu
chưa có PDF giả an toàn, chỉ cần giữ README này và `.gitkeep`.

## Metadata cần tạo khi ingestion

Pipeline phải tạo và giữ metadata cho từng chunk:

| Trường | Cách tạo |
|---|---|
| `chunk_id` | `{document_id}-slide-{NN}-chunk-{MM}` |
| `document_id` | Sinh ổn định từ tên file hoặc manifest |
| `document_title` | Lấy từ metadata PDF hoặc tên file đã chuẩn hóa |
| `source_file` | Tên PDF nguồn |
| `slide_number` | Số trang PDF, bắt đầu từ 1 |
| `session_number` | Lấy từ manifest hoặc quy ước tên file nếu có |
| `language` | Phát hiện hoặc cấu hình khi ingestion |
| `extraction_method` | `text`, `ocr` hoặc `vision` |

Citation hiển thị cho người dùng nên có dạng:
`{document_title}, slide {slide_number} — {source_file}`.

## Kiểm tra tối thiểu trước khi index

- File có header PDF hợp lệ và đọc được.
- `document_id` không trùng giữa các tài liệu.
- Không bỏ sót trang và không tạo chunk rỗng.
- Thứ tự đọc của text, bảng và cột không bị đảo.
- OCR tiếng Việt giữ đúng dấu ở mức chấp nhận được.
- Mọi chunk đều giữ `source_file` và `slide_number`.
- Không ghi PDF thật, text trích xuất, embedding hoặc vector store vào Git.
