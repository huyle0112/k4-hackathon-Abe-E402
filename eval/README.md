# Evaluation contract

Folder này chứa schema, golden set được phép commit và kết quả đánh giá không
nhạy cảm.

Golden set chính thức cần tối thiểu 20 case:

- 7 câu hỏi trong một buổi.
- 6 câu liên kết nhiều buổi.
- 3 câu low-confidence hoặc mơ hồ.
- 3 câu ngoài phạm vi.
- 1 câu correction.

Quality bar đề xuất:

- Retrieval Hit@5 tối thiểu 90%.
- Citation đúng file và slide tối thiểu 95%.
- Out-of-scope abstention tối thiểu 90%.
- Không citation nào trỏ tới chunk ngoài context.
- Ingestion không bỏ sót trang PDF.

Không commit toàn văn slide hoặc answer chứa đoạn trích dài từ dữ liệu riêng
tư. Nếu golden set sử dụng nội dung thật chưa được phép chia sẻ, lưu bản đó
trong vùng private và chỉ commit schema hoặc số liệu tổng hợp.

`golden-set.schema.json` định nghĩa data contract cho từng test case.

Chạy evaluator từ `codebase/backend/`:

```powershell
python scripts/evaluate.py ../../eval/golden-set.json
```
