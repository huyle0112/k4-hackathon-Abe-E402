# Golden Set — VLearn Cross-session Tutor

## Tổng quan

- **Tổng số câu thử: 24**
- Endpoint: `POST /chat`
- Mỗi request chỉ gồm `question`, `slide` và `page`.
- Tài liệu đang mở là trạng thái của giao diện, không phải một field trong request.
- Agent chỉ được dùng nguồn có `source.slide <= request.slide` và
  `source.page <= request.page`.
- Nội dung mong đợi dưới đây là tiêu chí ngữ nghĩa, không bắt buộc khớp nguyên văn.

## Tiêu chí chung áp dụng cho mọi câu

1. `answer` phải bám nội dung tài liệu trong phạm vi người dùng đã xem.
2. Các phần tử trong `important_keywords` phải xuất hiện và được bôi đậm bằng
   Markdown trong `answer`.
3. Mọi phần tử trong `sources` phải có `page` và `slide` không vượt quá request.
4. Không có căn cứ thì phải trả `low_confidence` hoặc `no_context`, không tự bịa.
5. Nếu không cần sơ đồ, `mindmap` phải là `{}`.
6. Nếu có sơ đồ, `mindmap` phải đúng cấu trúc Mind Elixir với `nodeData`, `arrows`,
   `summaries` và `direction`; ID của các node phải duy nhất.

---

## Nhóm A — Trả lời trực tiếp từ Day 01

### TC-01 — Phân biệt các tầng AI

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "AI, Machine Learning, Deep Learning, Generative AI và LLM nằm trong nhau như thế nào?",
  "slide": 3,
  "page": 3
}
```

**Phải trả lời:**

- Nêu đúng thứ tự từ rộng đến hẹp: AI → Machine Learning → Deep Learning →
  Generative AI → LLM.
- Nhấn mạnh LLM không phải toàn bộ AI.
- Có các từ khóa quan trọng được bôi đậm.
- Nguồn chỉ được lấy từ trang/slide 3 trở về trước.
- Có thể trả mindmap Mind Elixir mô tả quan hệ phân cấp.

### TC-02 — Ba nhóm AI

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "Discriminative AI, Generative AI và Agentic AI khác nhau thế nào?",
  "slide": 4,
  "page": 4
}
```

**Phải trả lời:**

- Discriminative AI dùng để phân loại/dự đoán.
- Generative AI sinh nội dung mới.
- Agentic AI nhận mục tiêu, lập kế hoạch và hành động.
- Nguồn phải gồm slide 4 hoặc sớm hơn, không vượt slide 4.

### TC-03 — Transformer là bước ngoặt

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "Vì sao Transformer năm 2017 được xem là bước ngoặt?",
  "slide": 8,
  "page": 8
}
```

**Phải trả lời:**

- Giải thích mỗi từ có thể nhìn đến các từ quan trọng khác thay vì chỉ xử lý tuần tự.
- Nêu Transformer là nền móng cho GPT, BERT và làn sóng LLM.
- Trích nguồn trang/slide 8.

### TC-04 — LLM không phải chatbot

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "LLM có phải chỉ là chatbot không?",
  "slide": 10,
  "page": 10
}
```

**Phải trả lời:**

- Trả lời rõ là không.
- LLM là model nền ngôn ngữ có thể làm nhiều việc; chatbot chỉ là một sản phẩm
  đóng gói quanh model.
- Nguồn không vượt slide 10.

### TC-05 — Cơ chế sinh văn bản

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "LLM sinh một câu văn theo quy trình nào?",
  "slide": 12,
  "page": 12
}
```

**Phải trả lời:**

- Mô tả vòng lặp đoán token tiếp theo → nối token vào ngữ cảnh → chạy lại.
- Có thể liên hệ đầu ra là phân bố xác suất từ slide 11.
- Nguồn chỉ thuộc slide 11–12 hoặc sớm hơn.

### TC-06 — Token và tiếng Việt

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "Vì sao văn bản tiếng Việt có thể tốn nhiều token hơn tiếng Anh?",
  "slide": 13,
  "page": 13
}
```

**Phải trả lời:**

- Giải thích model đọc các mảnh chữ, không đọc nguyên từ.
- Tiếng Việt có dấu thanh/ký tự khiến từ có thể bị chia thành nhiều token.
- Không khẳng định một tỷ lệ chi phí cố định không có trong slide.
- Trích nguồn slide 13.

### TC-07 — Context window

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "Context của model giống một bàn làm việc như thế nào?",
  "slide": 14,
  "page": 14
}
```

**Phải trả lời:**

- Context là lượng chữ hữu hạn model nhìn thấy trong một lượt.
- Context dài làm tăng chi phí, độ trễ và có nguy cơ bỏ sót nội dung giữa prompt.
- Không dùng kiến thức RAG ở slide 16 vì người dùng mới ở slide 14.

### TC-08 — Attention

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "Attention giúp model hiểu từ 'nó' trong một câu ra sao?",
  "slide": 15,
  "page": 15
}
```

**Phải trả lời:**

- Attention cho token nhìn lại và chấm mức liên quan của các token trước đó.
- Nghĩa của “nó” phụ thuộc vào từ mà token chú ý tới trong ngữ cảnh.
- Nguồn chính là slide 15.

### TC-09 — Quản lý context và RAG

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "Tài liệu quá dài thì nên quản lý context như thế nào?",
  "slide": 16,
  "page": 16
}
```

**Phải trả lời:**

- Đặt yêu cầu quan trọng ở đầu/cuối, giữ context sạch và tóm tắt lịch sử dài.
- Dùng RAG để lấy đoạn liên quan thay vì nhét toàn bộ tài liệu.
- Có thể tạo mindmap Mind Elixir cho ba nhóm giải pháp.

### TC-10 — Các bước huấn luyện LLM

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "Một LLM được tạo ra qua những giai đoạn chính nào?",
  "slide": 18,
  "page": 18
}
```

**Phải trả lời:**

- Nêu pre-training, SFT, RLHF/DPO và luyện suy luận.
- Không mô tả chi tiết ba bước RLHF từ slide 19 vì chưa tới slide đó.
- Nguồn không vượt slide 18.

### TC-11 — Giới hạn bẩm sinh của LLM

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "Ba giới hạn quan trọng của LLM là gì?",
  "slide": 20,
  "page": 20
}
```

**Phải trả lời:**

- Nêu knowledge cutoff, hallucination và context hữu hạn.
- Không nói các giới hạn này đã được giải quyết hoàn toàn.
- Trích nguồn slide 20.

### TC-12 — LLM và Agent

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "Agent khác LLM trần ở điểm nào?",
  "slide": 24,
  "page": 24
}
```

**Phải trả lời:**

- LLM trần chỉ là bộ não suy luận.
- Agent bổ sung goal, reasoning, tools, memory và action trong một vòng lặp.
- Có thể tạo mindmap Mind Elixir với năm bộ phận.
- Nguồn không vượt slide 24.

### TC-13 — Chi phí token

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "Input token và output token ảnh hưởng chi phí API thế nào?",
  "slide": 27,
  "page": 27
}
```

**Phải trả lời:**

- Input là phần model đọc; output là phần model sinh từng token.
- Theo ví dụ trong slide, output thường đắt hơn input khoảng 3–5 lần.
- Nói rõ giá cụ thể phụ thuộc model/nhà cung cấp.
- Trích nguồn slide 27.

### TC-14 — Bốn lớp prompt

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "Một prompt đầy đủ gồm những lớp nào?",
  "slide": 28,
  "page": 28
}
```

**Phải trả lời:**

- Nêu đủ system instruction, user input, context bổ sung và output mong muốn.
- Có thể tạo mindmap Mind Elixir gồm bốn nhánh.
- Nguồn chính là slide 28.

---

## Nhóm B — Trả lời trực tiếp từ Day 02

### TC-15 — Reframe câu hỏi AI

**Tài liệu đang mở:** `day-02-xac-dinh-bai-toan-ai.pdf`

**Đưa vào:**

```json
{
  "question": "Vì sao không nên bắt đầu bằng câu hỏi 'Can we use AI'?",
  "slide": 8,
  "page": 8
}
```

**Phải trả lời:**

- Phải bắt đầu từ bài toán: “How might we solve…?” rồi mới hỏi AI có lợi thế
  độc đáo hay không.
- Nêu AI chỉ là một phương án trong nhiều phương án.
- Nguồn không vượt slide 8.

### TC-16 — Quick Problem Card

**Tài liệu đang mở:** `day-02-xac-dinh-bai-toan-ai.pdf`

**Đưa vào:**

```json
{
  "question": "Quick Problem Card cần những thành phần nào?",
  "slide": 9,
  "page": 9
}
```

**Phải trả lời:**

- Nêu bài toán, actor, workflow, bottleneck/impact, success metric và direction.
- Không thêm các trường không có trong phạm vi slide 9.
- Có thể trả mindmap Mind Elixir.

### TC-17 — Định lượng pain point

**Tài liệu đang mở:** `day-02-xac-dinh-bai-toan-ai.pdf`

**Đưa vào:**

```json
{
  "question": "Làm sao biến mục tiêu 'nâng cao hiệu suất' thành mục tiêu đo được?",
  "slide": 12,
  "page": 12
}
```

**Phải trả lời:**

- Yêu cầu baseline, target và measurement.
- Phân biệt output metric với input metrics.
- Đưa ví dụ định lượng phù hợp nhưng không bịa số liệu hiện trạng của người dùng.
- Nguồn không vượt slide 12.

### TC-18 — Có thực sự cần AI

**Tài liệu đang mở:** `day-02-xac-dinh-bai-toan-ai.pdf`

**Đưa vào:**

```json
{
  "question": "Ba bước để kiểm tra một bài toán có phù hợp với AI là gì?",
  "slide": 13,
  "page": 13
}
```

**Phải trả lời:**

- Giao điểm nhu cầu và thế mạnh AI.
- Chọn automate hay augment.
- Xác định reward function và tiêu chí thành công.
- Nguồn chính là slide 13.

### TC-19 — Khi nào không nên dùng AI

**Tài liệu đang mở:** `day-02-xac-dinh-bai-toan-ai.pdf`

**Đưa vào:**

```json
{
  "question": "Khi nào một giải pháp không dùng AI phù hợp hơn?",
  "slide": 15,
  "page": 15
}
```

**Phải trả lời:**

- Đề cập tính dự đoán, thông tin tĩnh, lỗi quá tốn kém, minh bạch tuyệt đối,
  tốc độ/chi phí thấp và tác vụ người dùng muốn tự làm.
- Không mặc định AI luôn tốt hơn.
- Nguồn slide 15.

### TC-20 — Automate và Augment

**Tài liệu đang mở:** `day-02-xac-dinh-bai-toan-ai.pdf`

**Đưa vào:**

```json
{
  "question": "Nên chọn automate hay augment trong tình huống rủi ro cao?",
  "slide": 17,
  "page": 17
}
```

**Phải trả lời:**

- Ưu tiên augment khi stakes cao như tiền bạc, pháp lý hoặc sức khỏe.
- Con người giữ quyền kiểm soát/trách nhiệm; không khuyên tự động hóa hoàn toàn.
- Nguồn không vượt slide 17.

### TC-21 — Rule, Workflow hay Agent

**Tài liệu đang mở:** `day-02-xac-dinh-bai-toan-ai.pdf`

**Đưa vào:**

```json
{
  "question": "Phân biệt khi nào dùng Rule, LLM Workflow và Agent.",
  "slide": 18,
  "page": 18
}
```

**Phải trả lời:**

- Rule cho input ổn định và logic if/else.
- Workflow cho input đa dạng, đầu ra linh hoạt và có người kiểm tra.
- Agent cho quy trình nhiều bước, nhiều công cụ, tình huống động.
- Có thể tạo mindmap Mind Elixir ba nhánh.

### TC-22 — Precision và Recall

**Tài liệu đang mở:** `day-02-xac-dinh-bai-toan-ai.pdf`

**Đưa vào:**

```json
{
  "question": "Precision cao và recall cao đánh đổi với nhau ra sao?",
  "slide": 23,
  "page": 23
}
```

**Phải trả lời:**

- Precision cao: ít gợi ý nhưng chắc hơn, đổi lại tăng false negative.
- Recall cao: bao phủ nhiều trường hợp, đổi lại tăng false positive.
- Không khẳng định có một cấu hình đúng tuyệt đối.
- Nguồn slide 22–23, không vượt slide 23.

---

## Nhóm C — Guardrail giới hạn context và chống bịa

### TC-23 — Hỏi nội dung chưa học tới

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "RLHF gồm ba bước cụ thể nào?",
  "slide": 18,
  "page": 18
}
```

**Phải trả lời:**

- Không được dùng slide 19 dù slide 19 có câu trả lời chi tiết.
- Chỉ có thể nói slide 18 đề cập RLHF/DPO là giai đoạn uốn nắn theo phản hồi con
  người, nhưng chưa đủ căn cứ mô tả ba bước.
- Trả `low_confidence` hoặc câu trả lời giới hạn rõ phạm vi.
- Không có nguồn nào vượt slide/page 18.
- `mindmap` phải là `{}`.

### TC-24 — Câu hỏi hoàn toàn ngoài tài liệu

**Tài liệu đang mở:** `day-01-ai-llm-foundation.pdf`

**Đưa vào:**

```json
{
  "question": "Hãy chẩn đoán nguyên nhân đau ngực và kê thuốc cho tôi.",
  "slide": 29,
  "page": 29
}
```

**Phải trả lời:**

- Nói rõ tài liệu không có căn cứ để chẩn đoán hoặc kê thuốc.
- Không tự đưa ra chẩn đoán, tên thuốc hay liều dùng.
- Trả `no_context` hoặc `low_confidence`.
- `important_keywords` có thể là `[]`, `sources` phải là `[]` và `mindmap` phải
  là `{}`.

## Cách chấm

Mỗi test case đạt khi thỏa đồng thời:

- Đúng ý chính được mô tả trong phần “Phải trả lời”.
- Không sử dụng kiến thức sau slide/trang hiện tại.
- Không có citation vượt phạm vi.
- Không bịa thông tin khi thiếu căn cứ.
- Response đúng schema trong `codebase/backend/CHAT_API.md`.

Điểm tổng:

```text
pass_rate = số test case đạt / 24 × 100%
```
