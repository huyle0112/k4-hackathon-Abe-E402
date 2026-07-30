# AI SPEC — [Tên lát cắt] · Nhóm [XX] · Zone [X]

Hướng: [x] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [x] Tối ưu tính năng có sẵn  [ ] Tính năng mới

## §1. User & Job

- Job executor + workflow: Học viên đang trong quá trình học tập, ôn thi, hoặc làm bài tập, cần truy xuất và tổng hợp kiến thức từ nhiều buổi học khác nhau trong cùng một môn học.
- Core JTBD: "Khi tôi ôn tập hoặc học bài mới, tôi muốn tìm hiểu và kết nối kiến thức từ nhiều bài giảng khác nhau để có cái nhìn toàn diện, thay vì chỉ nhận được câu trả lời bó hẹp trong nội dung của một buổi học duy nhất."
- Problem statement: Chatbot hiện tại thường chỉ phản hồi dựa trên nội dung cục bộ của slide/buổi học hiện tại, dẫn đến việc trả lời thiếu hoặc không chính xác đối với các câu hỏi mang tính tổng hợp, làm đứt gãy mạch suy nghĩ và ảnh hưởng xấu đến trải nghiệm học tập của người dùng.
- Evidence (chuẩn A và/hoặc B — log đầy đủ trong repo):

  - Số liệu mining / kết quả khảo sát (n = 25, % xác nhận):
    - Vấn đề (Pain point): 47.8% người được hỏi gặp trường hợp chatbot trả lời thiếu chính xác do thiếu kiến thức bài cũ ở mức "Thường xuyên" và "Rất thường xuyên" (nếu tính cả "Thỉnh thoảng" là 82.6%).
    - Mức độ ảnh hưởng: 47.8% cho rằng việc chatbot không liên kết được bài học ảnh hưởng "Nhiều" đến "Rất nhiều" tới trải nghiệm học.
    - Sự mong muốn: 60.8% đánh giá tính năng sử dụng nội dung nhiều buổi học là "Cần thiết" và "Rất cần thiết".
    - Trường hợp sử dụng (Use case): Top nhu cầu cao nhất là Giải thích mối liên hệ giữa các bài (43.5%), Tóm tắt một chương (39.1%), Ôn tập trước bài kiểm tra (39.1%), và Xác định kiến thức nền (39.1%).
    - Hành vi: Có tới 40.9% người dùng muốn "Được tự lựa chọn phạm vi nội dung" để chatbot trả lời, thay vì AI tự động giới hạn ở bài hiện tại hay toàn bộ môn học.
  - ≥5 quote/ví dụ nguyên văn + nguồn: (Cần bổ sung thêm từ khảo sát)

## §2. Impact & quyết định chọn

- Bảng impact ≥3 ứng viên (bao nhiêu người · tần suất · tốn gì mỗi lần · khả thi):

  - Ứng viên 1 (Giải thích liên kết bài học): Hỗ trợ giải thích mối liên hệ giữa bài mới và cũ. Tác động 43.5% (10 người). Tần suất: Thường xuyên (mỗi khi học bài mới). Tốn: Vài phút để user tự mở lại slide cũ đối chiếu. Khả thi: Cao.
  - Ứng viên 2 (Tóm tắt tổng hợp theo chương): Gom nhóm kiến thức và tóm tắt ôn thi. Tác động 39.1% (9 người). Tần suất: Trung bình (cuối chương hoặc lúc thi). Tốn: Cần đọc lại rất nhiều tài liệu để nhặt ý chính. Khả thi: Trung bình.
  - Ứng viên 3 (Trợ lý tìm kiếm slide cũ): Chỉ đơn thuần định vị lại 1 nội dung đã học ở slide nào. Tác động: 13% (3 người). Tần suất: Ít. Tốn: Vài chục giây lướt lại các file PDF. Khả thi: Rất cao.
- Ứng viên ĐÃ LOẠI + vì sao:

  - Trợ lý tìm kiếm slide cũ (Ứng viên 3). Vì sao: Mức độ tác động quá thấp (chỉ 13% sinh viên chọn đây là trường hợp cần nhất). Sinh viên có thể dùng chức năng search text (Ctrl+F) đơn giản thay vì cần đến AI phức tạp.
- Ứng viên CHỌN + vì sao (bằng số):

  - Chọn hướng: Xây dựng tính năng cho phép "Người dùng tùy chọn phạm vi bài học" kết hợp khả năng "Giải thích mối liên hệ giữa bài cũ và bài mới".
  - Vì sao:
    - Khảo sát chỉ ra đây là Use case được mong đợi nhất (43.5% người lựa chọn).
    - Giải quyết dứt điểm pain point lớn nhất: 47.8% user bị ảnh hưởng rất nhiều vì chatbot hiện tại hay trả lời thiếu do không nhớ kiến thức cũ.
    - Đáp ứng chính xác nhu cầu UX: 40.9% user mong muốn tự nắm quyền kiểm soát, tự chọn lượng file/phạm vi context đẩy vào cho Chatbot, thay vì Chatbot mặc định đọc toàn bộ môn học.

## §3. Giải pháp tương tự đã nghiên cứu

- [Sản phẩm 1]: flow / đáng học / đáng né / mình khác gì
- 

## §4. Thiết kế

- Lát cắt MỘT CÂU (1 user · 1 việc · 1 quyết định AI · 1 kết quả):
- Non-goals (≥3 thứ KHÔNG build):
- Mức prototype nhắm tới: [ ] Sketch [ ] Mock [ ] Working — phần nào mock, phần nào thật:
- Automation: [ ] augment [ ] conditional [ ] automate — lý do theo cost-of-error:
- §4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR, xem guide):| Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  | ------------ | --------------------------------------- |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8) [bảng theo guide §2.5]

## §6. Bốn đường đi của trải nghiệm

- Happy path: · Low-confidence (②): · Failure/không căn cứ (①): · Correction (user sửa):
- Khi bị đòi ngoài phạm vi (③): · Case đặc thù domain (④):

## §7. Kiểm thử

- Chiều chất lượng + định nghĩa kiểm chứng được:
- Golden set (≥20 case theo cơ cấu trong guide §2.6, file trong eval/):
- Quality bar (chốt từ 23:59, giữ nguyên sau đó): "Đạt khi ≥ ___% qua bộ, và ___"
- Kết quả các lượt chạy (bảng % — cập nhật đến trước CP6):

## §8. Phân công & kế hoạch

- Phân công có tên: spec / evidence / prompt / code / demo
- Willing users (≥3 tên) + kế hoạch vòng validation CP5 (3 câu hỏi, ai log):
- Multi-prototype (nếu làm): trục khác biệt của ≥2 phương án + lý do chọn:

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |

[Sản phẩm 2]: ...
