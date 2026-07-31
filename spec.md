# AI SPEC — VLearn Cross-session Tutor · Nhóm Abe-E402 · Zone [2]

Hướng: [x] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [x] Tối ưu tính năng có sẵn  [ ] Tính năng mới
Trạng thái tài liệu: **Bản nộp chính thức — cập nhật theo ngày 31/07/2026**

## §1. User & Job

- **Job executor + workflow:** Học viên đang học bài mới, ôn thi hoặc làm bài
  tập; trong lúc đọc slide, họ cần truy xuất và kết nối kiến thức từ một hoặc
  nhiều buổi học của cùng môn.
- **Core JTBD:** “Khi tôi ôn tập hoặc học bài mới, tôi muốn chọn những buổi học
  liên quan và hỏi trên toàn bộ phạm vi đó để hiểu mối liên hệ giữa các khái
  niệm, thay vì chỉ nhận câu trả lời bó hẹp trong slide đang mở.”
- **Problem statement:** Chatbot hiện tại chủ yếu bám vào slide/buổi đang mở.
  Với câu hỏi tổng hợp hoặc liên kết bài cũ và bài mới, câu trả lời dễ thiếu
  căn cứ, khiến học viên phải tự mở nhiều PDF để tìm và đối chiếu.
- **Evidence định lượng từ khảo sát:** khảo sát ghi nhận `n = 25` người tham gia.
  Nguồn: [Google Forms — Responses](https://docs.google.com/forms/d/1gNubNiLzgH7uuS2kvr3-0hiQJCLNShvV9yPWNh-L7Gw/edit#responses).
  Do một số câu bị bỏ qua, mẫu số hợp lệ thay đổi theo từng câu hỏi:

  - 47,8% gặp câu trả lời thiếu chính xác do thiếu kiến thức bài cũ ở mức
    “Thường xuyên” hoặc “Rất thường xuyên”; tính cả “Thỉnh thoảng” là 82,6%.
  - 47,8% cho rằng việc chatbot không liên kết được bài học ảnh hưởng “Nhiều”
    hoặc “Rất nhiều” đến trải nghiệm.
  - 60,8% đánh giá khả năng dùng nội dung nhiều buổi là “Cần thiết” hoặc
    “Rất cần thiết”.
  - Nhu cầu nổi bật: giải thích mối liên hệ giữa các bài 43,5%; tóm tắt chương
    39,1%; ôn tập trước kiểm tra 39,1%; xác định kiến thức nền 39,1%.
  - 40,9% muốn tự chọn phạm vi nội dung cho chatbot.
  - **Mẫu số hợp lệ:** các tỷ lệ 47,8%, 82,6%, 60,8%, 43,5% và 39,1% được tính
    trên khoảng 23 câu trả lời hợp lệ; tỷ lệ 40,9% được tính trên khoảng 22 câu
    trả lời hợp lệ. `n = 25` là tổng số người tham gia khảo sát.

- **Evidence hành vi từ log ẩn danh:** nguồn
  `data/chat_history_anonymized_for_hackathon.csv`.

  1. “tôi cần tổng hợp kiến thức ngày 1 và ngày 2” — U0197, C0143, M0127,
     24/07/2026.
  2. “giải thích một cách dễ hiểu các khải niệm keyword chính trong bài này,
     tạo liên kết giữa các phần một cách dễ hiểu” — U0345, C0292, M1756,
     27/07/2026.
  3. “Tổng hợp toàn bộ những kiên thức chính trong bài này” — U0212, C0065,
     M1189, 29/07/2026.
  4. “tổng hợp chi tiết các nguyên tắc cần tuần theo khi viết prompt” — U0138,
     C0221, M0692, 29/07/2026.
  5. “tổng hợp lại các ý chính của bài 2 này” — U0153, C0467, M1010,
     27/07/2026.

  Các lỗi chính tả được giữ nguyên vì đây là trích dẫn nguyên văn.

## §2. Impact & quyết định chọn

| Ứng viên | Bao nhiêu người | Tần suất | Tốn gì mỗi lần | Khả thi |
|---|---:|---|---|---|
| Giải thích liên kết bài cũ–mới | 43,5% (khoảng 10/23 câu trả lời hợp lệ) | Mỗi khi bài mới phụ thuộc kiến thức nền | Vài phút mở lại nhiều PDF và tự đối chiếu | Cao: RAG đã có metadata buổi, slide và citation |
| Tóm tắt tổng hợp theo chương | 39,1% (khoảng 9/23) | Cuối chương/trước kiểm tra | Đọc lại nhiều tài liệu và tự gom ý | Trung bình: cần kiểm soát coverage và context dài |
| Tìm lại slide cũ | 13% (khoảng 3/23) | Ít | Vài chục giây tìm thủ công | Rất cao nhưng giá trị AI thấp |

- **Ứng viên đã loại:** trợ lý chỉ tìm slide cũ. Tác động thấp nhất (13%) và
  phần lớn có thể giải bằng tìm kiếm văn bản/metadata, chưa cần generation.
- **Ứng viên đã chọn:** người dùng tự chọn một hoặc nhiều buổi học, sau đó hỏi
  để AI giải thích mối liên hệ và trả nguồn theo file/trang/slide.
- **Lý do chọn bằng số:** đây là use case đứng đầu (43,5%), giải quyết pain
  point có tần suất cao (47,8%) và khớp nhu cầu kiểm soát phạm vi (40,9%).
- **Giả thuyết giá trị:** nếu học viên chủ động chọn đúng phạm vi và nhận được
  nguồn có thể mở để kiểm tra, họ sẽ tổng hợp kiến thức nhanh hơn và ít gặp câu
  trả lời thiếu do chỉ dùng bài hiện tại.

## §3. Giải pháp tương tự đã nghiên cứu

| Sản phẩm | Flow đáng học | Điều đáng né | VLearn khác gì |
|---|---|---|---|
| [Google NotebookLM](https://support.google.com/notebooklm/answer/16179559?hl=en) | Chọn/bỏ chọn từng nguồn; citation mở đúng vị trí để kiểm tra | Notebook tổng quát, không bám tiến độ slide trong khóa học | Phạm vi theo buổi và chặn nguồn sau slide hiện tại |
| [ChatGPT Study Mode](https://help.openai.com/en/articles/11780217-study-mode) | Giải thích theo lớp, hỏi gợi mở và kiểm tra hiểu biết | Vẫn có thể trả lời trực tiếp hoặc sai; người dùng tự quản lý context | Chỉ dùng học liệu đã index và abstain khi thiếu evidence |
| [Khanmigo](https://support.khanacademy.org/hc/en-us/articles/13860282793869-What-are-the-Community-Guidelines-for-Khanmigo) | Dùng gợi ý/câu hỏi thay vì làm hộ, hướng tới tư duy độc lập | Không nên được xem là nguồn duy nhất | Từ chối làm hộ bài đang chấm và gắn câu trả lời với PDF/trang/slide |

**Quyết định thiết kế:** học cách cho user kiểm soát nguồn như NotebookLM và
hỗ trợ học thay vì làm hộ như Study Mode/Khanmigo. Điểm khác biệt của VLearn là
phạm vi theo buổi học, theo tiến độ đọc và citation do backend dựng từ chunk
thật.

## §4. Thiết kế

- **Lát cắt mục tiêu — một câu:** Một học viên chọn các buổi liên quan và đặt một câu hỏi
  tổng hợp; AI quyết định evidence có đủ và phủ đủ các buổi không; hệ thống trả
  lời có citation, hoặc hỏi lại/abstain kèm bước tiếp theo.
- **Non-goals:**

  1. Không dùng web hoặc kiến thức nền để lấp phần slide không có.
  2. Không tự thêm buổi/tài liệu ngoài phạm vi user chọn.
  3. Không chẩn đoán, kê thuốc hoặc trả dữ liệu thời gian thực.
  4. Không làm hộ bài kiểm tra đang chấm điểm.
  5. Không xây LMS, chấm điểm hay cá nhân hóa dài hạn trong lát cắt này.

- **Mức prototype:** code frontend/backend đã được nối qua API thật; trạng thái
  hiện tại [x] Code-integrated [ ] Đã tái lập working end-to-end; đích demo
  [x] Working end-to-end.
- **Phần đã có code:** ingestion PDF, metadata buổi/slide, retrieval đa buổi,
  rerank, coverage guard, generation/citation, API contract và evaluator.
- **Phần được latest evaluator kiểm chứng:** happy path trong phạm vi hiện tại,
  clarification, no-context và policy safety trên 22 golden case.
- **Phần đã nối:** frontend chat và mindmap gọi API backend thật; request chat
  gửi `document_id` và slide hiện tại; router chỉ liên kết bài khác khi câu hỏi
  nhắc rõ buổi cần liên hệ. Mindmap gửi tập tài liệu đã chọn và prompt tùy chọn.
- **Phần chưa xác nhận end-to-end:** build/test của trạng thái code hiện tại
  chưa được tái lập; citation chat chưa mở trực tiếp tới slide.
- **Automation:** [x] augment [ ] conditional [ ] automate. User giữ quyền chọn
  phạm vi và kiểm tra nguồn; AI chỉ truy xuất, giải thích và gợi ý bước tiếp theo.
  Cost-of-error của câu trả lời sai cao hơn chi phí kiểm tra citation.

### §4b. Nguyên tắc HAX/PAIR

| Nguyên tắc | Áp dụng trong prototype | Trạng thái thực tế |
|---|---|---|
| Làm rõ AI có thể làm gì | Nhãn “Trợ lý học theo ngữ cảnh”, hiển thị trang đang đọc | **Một phần:** UI có nhãn/trang; chat chưa hiển thị phạm vi nhiều buổi |
| Làm rõ AI dùng dữ liệu nào | Response backend có file, page, slide và excerpt | **Một phần:** UI thật hiển thị nguồn; chưa mở citation tới slide |
| Giới hạn khi không chắc | Confidence threshold, clarification và abstention | **Đã kiểm chứng:** latest run có 5 `clarification_required` và 7 `no_context` |
| Giải thích kết quả | Backend chỉ dựng citation từ chunk ID hợp lệ | **Có code/test module:** chưa kiểm chứng thao tác mở nguồn end-to-end |
| Hỗ trợ sửa sai | Sửa câu hỏi, thêm/bớt buổi và chạy lại | **Mục tiêu:** chưa có action “Sửa phạm vi” và golden case correction nhiều lượt |
| Giữ quyền kiểm soát | User chọn nguồn thay vì AI tự mở toàn môn | **Một phần:** mindmap thật có checkbox; chat liên kết buổi qua yêu cầu rõ thay vì selector |
| Graceful failure | Provider lỗi không được giả vờ thành công | **Một phần:** frontend đã hiển thị lỗi API; chưa có nút retry riêng |

## §5. Kiểu lỗi — 4 lớp chỗ khó và kịch bản

| ID | Lớp | Kịch bản | Hành vi thiết kế | Evidence | Trạng thái |
|---|---|---|---|---|---|
| E1 | Input & intent | Chỉ nhập “Tool” hoặc “là gì” | Hỏi một câu làm rõ, không citation | CHAT-06, CHAT-07 | **Đã kiểm chứng** |
| E2 | Input & intent | Hỏi nội dung ngoài phần slide được phép | Không dùng phần chưa xem; nêu thiếu context | CHAT-08, CHAT-09 | **Đã kiểm chứng:** latest trả `no_context` |
| E3 | Input & intent | User chọn nhầm hoặc thiếu buổi | Nêu phạm vi hiện tại và cho sửa lựa chọn | Chưa có golden case correction nhiều lượt | **Mục tiêu** |
| E4 | Retrieval & context | Một buổi được chọn không có evidence | Abstain vì thiếu coverage đa buổi | `test_missing_cross_session_evidence_forces_abstention` | **Có test module; chưa E2E** |
| E5 | Retrieval & context | Có hit nhưng lexical/vector coverage thấp | Không khẳng định khi thiếu căn cứ | CHAT-08, CHAT-09; generation tests | **Một phần:** latest dùng `no_context`, chưa có output `low_confidence` |
| E6 | Generation & citation | LLM đề xuất chunk ID không tồn tại | Loại citation sai; hết citation thì abstain | `test_invalid_and_duplicate_citations_are_filtered` | **Có test module; chưa E2E** |
| E7 | Generation & citation | Câu đa buổi chỉ cite một buổi | Yêu cầu citation phủ mọi buổi hoặc abstain | `test_cross_session_answer_requires_citations_from_each_session` | **Có test module; chưa E2E** |
| E8 | Operations & policy | Timeout, rate limit, refusal, response incomplete | Báo lỗi kiểm soát; không âm thầm bịa/fallback | Generation provider tests | **Có test module; UI retry chưa có** |
| E9 | Operations & policy | Xin đáp án bài đang chấm hoặc yêu cầu bịa nguồn | Từ chối và đề nghị hỗ trợ học | CHAT-10, CHAT-11 | **Đã kiểm chứng** |
| E10 | Operations & policy | Hỏi deadline, giá hiện tại, chẩn đoán/kê thuốc | `no_context`/từ chối; hướng tới nguồn phù hợp | CHAT-12–14, MAP-06 | **Đã kiểm chứng** |

Hai khoảng trống phát hiện khi đối chiếu code và golden set:

1. API `/chat` đã nhận `document_id` và router có thể nhận diện buổi được nhắc
   rõ; tuy nhiên chat chưa có selector để user chọn danh sách buổi trực tiếp.
2. Chưa có golden case correction nhiều lượt và backend/frontend chưa thống
   nhất khi nào dùng `low_confidence` thay vì `no_context`.

## §6. Bốn đường đi của trải nghiệm

| Đường đi | Trigger | Response/UI | Evidence hiện có | Trạng thái |
|---|---|---|---|---|
| Happy path | Câu rõ, đủ evidence và citation hợp lệ | Trả lời + confidence + nguồn file/trang/slide | CHAT-01–05, MAP-01–03 | **Đã kiểm chứng trong phạm vi golden set** |
| Low-confidence (②) | Có hit nhưng coverage yếu | Không khẳng định; đề xuất câu hỏi/phạm vi cụ thể hơn | CHAT-08, CHAT-09 | **Một phần:** latest thực tế trả `no_context`, chưa trả `low_confidence` |
| Failure/không căn cứ (①) | Không hit, thiếu evidence hoặc policy chặn | `no_context`, không citation và nêu lý do | CHAT-11–13, MAP-06, MAP-08 | **Đã kiểm chứng** |
| Correction | User sửa câu hỏi hoặc phạm vi | Gửi request mới và thay kết quả/citation cũ | Chưa có case nhiều lượt | **Mục tiêu** |
| Ngoài phạm vi (③) | Yêu cầu rõ nhưng tài liệu không chứa | Từ chối phần ngoài phạm vi, không dùng kiến thức nền | CHAT-12, CHAT-13, MAP-06 | **Đã kiểm chứng** |
| Đặc thù domain (④) | Bài đang chấm, bịa nguồn, y khoa | Policy an toàn và hướng dẫn thay thế | CHAT-10, CHAT-11, CHAT-14, MAP-08 | **Đã kiểm chứng** |

**Target happy path đa buổi — chưa được latest result kiểm chứng end-to-end:**
user chọn Day 1 + Day 2 và hỏi “LLM, Workflow và Agent
liên hệ với nhau thế nào?” → retrieval giữ nguồn từ cả hai buổi → AI giải thích
vai trò của LLM và tiêu chí chọn Workflow/Agent → trả ít nhất một citation cho
mỗi buổi.

**Target correction flow — chưa có golden case nhiều lượt:** câu đầu chỉ chọn
Day 1 nên thiếu tiêu chí Workflow;
user bấm “Sửa phạm vi”, thêm Day 2 và gửi lại → câu trả lời mới thay thế phần
thiếu và hiển thị nguồn của cả hai ngày.

## §7. Kiểm thử

### Chiều chất lượng và định nghĩa kiểm chứng được

| Chiều | Định nghĩa đạt |
|---|---|
| Retrieval | Expected source nằm trong top 5; câu đa buổi có evidence từ mọi buổi |
| Groundedness | Không có ý chính nằm ngoài evidence |
| Citation precision | 100% citation thuộc context hits và đúng file/slide |
| Citation completeness | Mọi ý chính cần nguồn đều có citation hỗ trợ |
| Abstention | Câu ngoài phạm vi/thiếu evidence không được trả như fact |
| Clarification | Câu mơ hồ phải hỏi lại, không đoán và không tạo nguồn |
| Context boundary | Không dùng slide sau trang hiện tại hoặc tài liệu chưa chọn |
| Correction | Sau khi sửa phạm vi, response mới dùng đúng phạm vi mới |

### Golden set hiện có

- `eval/golden-set.json` gồm **22 case**: 14 chat và 8 mindmap.
- 15 case lấy từ chatlog quan sát được; 7 case được biên soạn để phủ rủi ro.
- Risk coverage: K1 — thiếu thông tin trong tài liệu; K2 — câu mơ hồ; K3 — yêu
  cầu việc sản phẩm không được phép làm; K4 — câu trả lời sai có hậu quả thật.
- Golden set đã phủ happy path, clarification, no-context và safety. Khoảng
  trống còn lại là correction nhiều lượt và chat chọn nhiều buổi end-to-end.

### Quality bar

“Đạt khi **≥80%** case pass, **0 fabricated_content** và
**0 fabricated_citation**.”

Engineering bar sau tích hợp: Retrieval Hit@5 ≥90%, citation đúng file/slide
≥95%, out-of-scope abstention ≥90% và không citation nào ngoài context.

### Kết quả các lượt chạy

Kết quả đánh giá gần nhất được lưu tại `eval/latest-results.json`:

| Endpoint/flow | Pass/Total | Tỷ lệ |
|---|---:|---:|
| `POST /chat` | 14/14 | 100% |
| `POST /mindmaps` | 8/8 | 100% |
| **Toàn bộ** | **22/22** | **100%** |

Phân bố status của 22 kết quả:

| Status | Số case |
|---|---:|
| `answered` | 7 |
| `clarification_required` | 5 |
| `no_context` | 7 |
| `created` | 3 |

- Thời điểm artifact: 31/07/2026 05:16:48 UTC, tương đương khoảng 12:16 giờ
  Việt Nam.
- Kết quả **đạt quality bar ≥80%** và không ghi nhận case thất bại theo các
  constraint của golden set.
- `eval/first-run-results.json` là baseline giả lập (`is_simulated: true`) nên
  không được dùng làm kết quả chính thức.
- Latest result là artifact evaluator thực tế đã lưu, nhưng vẫn cần chạy lại
  trên commit demo cuối để xác nhận khả năng tái lập.

## §8. Phân công & kế hoạch

| Thành viên | Phụ trách | Artifact |
|---|---|---|
| Lê Hồ Quang Huy | Spec, chốt lát cắt, tích hợp và demo | `spec.md`, changelog |
| Lã Phan Hoài An | PDF ingestion, OCR, chunk, embedding/index | `app/rag/ingestion/`, `embeddings.py` |
| Nguyễn Tiến Đạt | Retrieval đa buổi, rerank, generation, citation | `app/rag/retrieval/`, `app/rag/generation/` |
| Kiều Phúc Huy | Chat/mindmap UX, chọn phạm vi, mở citation | `codebase/fe/` |
| Nguyễn Nam Phong | API, runtime, evaluator và kết quả | `app/api/`, `eval/` |

### Validation CP5

Ba tác vụ dùng cho mỗi phiên:

1. Chọn Day 1 + Day 2 và yêu cầu giải thích mối liên hệ giữa LLM, Workflow và
   Agent.
2. Mở ít nhất hai citation và kiểm tra file/trang/slide.
3. Thử một câu mơ hồ hoặc ngoài phạm vi, sau đó sửa câu hỏi/phạm vi để tiếp tục.

Ba câu hỏi phỏng vấn:

1. Khi chọn nhiều buổi, câu trả lời có giúp thấy mối liên hệ mà chat một bài
   không làm được không? Cho ví dụ.
2. Bạn có mở và kiểm tra được ý chính qua citation trong 30 giây không?
3. Khi hệ thống hỏi lại/từ chối, bạn có biết phải sửa câu hỏi hoặc phạm vi thế
   nào không?

Tiêu chí đạt: 3/3 người hoàn thành luồng chính; điểm hữu ích trung bình ≥4/5;
3/3 người kiểm tra citation trong 30 giây; 3/3 người hiểu bước tiếp theo
khi hệ thống hỏi lại hoặc abstain.

**Willing users và phản hồi nguyên văn:**

1. **Nguyễn Thùy Trang:** “Khi mình đang xem một bài học, trợ lý đôi lúc lấy
   nguồn từ bài khác nên câu trả lời khá khó hiểu. Mình muốn AI chỉ sử dụng đúng
   bài và slide hiện tại, trừ khi mình yêu cầu liên hệ với các bài trước.”
2. **Trần Kiều Hạnh:** “Chức năng mindmap nên dùng toàn bộ nội dung của những
   tài liệu mình chọn, thay vì chỉ tìm vài đoạn liên quan. Nếu không nhập prompt
   thì hệ thống vẫn nên tự tạo một sơ đồ tổng quan.”
3. **Nguyễn Đức Anh:** “Khi đặt câu hỏi tổng hợp, mình muốn chatbot có thể liên kết nội dung từ nhiều buổi học đã chọn và ghi rõ thông tin được lấy từ bài hoặc slide nào. Nếu không tìm thấy nguồn phù hợp, hệ thống nên thông báo thay vì tự đưa ra câu trả lời.”

**Nhóm đã sửa từ phản hồi:** Nhóm đã giới hạn truy xuất theo đúng tài liệu và
slide đang mở, đồng thời chỉ liên kết bài khác khi người dùng yêu cầu rõ ràng.
Chức năng mindmap được tách khỏi RAG, đọc toàn bộ tài liệu đã chọn, hỗ trợ prompt
tùy chọn và lưu kết quả vào SQLite để tái sử dụng.

**Người log:** Lê Hồ Quang Huy tổng hợp; Kiều Phúc Huy ghi quan sát UX; Nguyễn
Nam Phong lưu kết quả case và metric.

### Multi-prototype

- **A — Auto scope:** AI tự dùng toàn bộ môn; ít thao tác nhưng context lớn và
  khó biết bài nào thực sự được dùng.
- **B — User-controlled scope:** user chọn buổi/tài liệu; thêm một thao tác
  nhưng minh bạch và giảm nguy cơ lấy nhầm context.
- **Chọn B** vì khớp 40,9% người khảo sát muốn tự chọn phạm vi. Quyết định này
  vẫn cần xác nhận lại trong validation người dùng.

### Việc cần xong trước tích hợp/demo

1. Nối selector buổi học vào contract `/chat`.
2. Chạy lại frontend API integration trên môi trường demo và bổ sung nút retry.
3. Bảo toàn ít nhất một citation cho mỗi buổi trước khi cắt context.
4. Viết next action cụ thể cho `low_confidence`.
5. Cho citation mở đúng PDF/trang/slide.
6. Chạy backend test, frontend build và evaluator trên cùng commit demo.
7. Chạy lại golden set trên commit demo và hoàn tất validation với hai willing
   users đã ghi nhận.

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao/evidence |
|---|---|---|
| 30/07/2026 | Chốt vấn đề và lát cắt đa buổi | Survey và log nhu cầu tổng hợp |
| 30–31/07/2026 | Thêm PDF RAG, retrieval, generation và citation | Cần nguồn kiểm chứng được |
| 31/07/2026 | Thêm chat/mindmap UI và golden set 22 case | Bao phủ happy/error/safety flow |
| 31/07/2026 | Ghi nhận latest evaluator result 22/22 | `eval/latest-results.json`: 14/14 chat, 8/8 mindmap |
| 31/07/2026 | Chọn user-controlled scope | 40,9% người khảo sát muốn tự chọn phạm vi |

## Phụ lục — Sản phẩm 2: Mindmap theo tài liệu đã chọn

Mindmap hỗ trợ cùng JTBD tổng hợp kiến thức nhưng không thay thế lát cắt chat đa
buổi:

- User chọn 1–20 tài liệu và nhập prompt.
- Backend chỉ retrieval trong tài liệu đã chọn, tạo Mind Elixir JSON, citation
  và lưu SQLite/cache.
- Flow gồm `created`, `cached`, `clarification_required`, `no_context`.
- Có 8 golden case; frontend đã gọi API thật nhưng vẫn cần chạy lại build/test
  end-to-end trên commit demo.
