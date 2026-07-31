# VLearn AI API

## Phạm vi

Hệ thống có hai endpoint tương tác với AI:

| Endpoint | Chức năng |
|---|---|
| `POST /chat` | Hỏi đáp về nội dung người dùng đã xem. |
| `POST /mindmaps` | Tạo một mindmap từ các tài liệu được chọn và prompt của người dùng. |

Các endpoint `GET` chỉ đọc dữ liệu mindmap đã lưu trong SQLite và không gọi AI.

## Quy tắc chung

1. AI chỉ được sử dụng context mà request cho phép.
2. Nếu câu hỏi hoặc prompt chưa rõ, AI phải hỏi lại thay vì tự đoán ý người dùng.
3. Nếu yêu cầu nằm ngoài context, AI phải nói rõ giới hạn và gợi ý cách sửa yêu
   cầu; không tạo nội dung không có nguồn.
4. Mọi nguồn trả về phải là nguồn Agent thực sự sử dụng.
5. `/chat` không tạo hoặc trả mindmap.
6. Mindmap chỉ được tạo khi người dùng chủ động gọi `POST /mindmaps`.

---

# 1. Chat

## `POST /chat`

Trả lời câu hỏi dựa trên nội dung từ đầu tài liệu đến slide/trang người dùng đang
xem.

## Request

```http
POST /chat
Content-Type: application/json
```

```json
{
  "question": "Attention hoạt động như thế nào?",
  "slide": 15,
  "page": 15
}
```

| Field | Kiểu | Bắt buộc | Mô tả |
|---|---:|:---:|---|
| `question` | `string` | Có | Câu hỏi, từ 2 đến 2.000 ký tự. |
| `slide` | `integer` | Có | Slide hiện tại, bắt đầu từ 1. |
| `page` | `integer` | Có | Trang PDF hiện tại, bắt đầu từ 1. |

Context bắt buộc thỏa:

```text
source.slide <= request.slide
source.page <= request.page
```

## Response trả lời thành công

```json
{
  "status": "answered",
  "answer": "**Attention** cho phép mỗi **token** xác định những token khác có liên quan trong cùng ngữ cảnh.",
  "important_keywords": [
    "Attention",
    "token"
  ],
  "confidence": 0.87,
  "clarification_question": null,
  "sources": [
    {
      "source_id": "source-1",
      "document_id": "doc_day_01",
      "file_name": "day-01-ai-llm-foundation.pdf",
      "page": 15,
      "slide": 15,
      "excerpt": "Attention cho phép mỗi token nhìn lại và chấm mức độ liên quan của các token trước đó.",
      "relevance_score": 0.87
    }
  ]
}
```

## Response khi câu hỏi chưa rõ

Ví dụ người dùng chỉ hỏi: `"Cái này hoạt động ra sao?"`, nhưng không xác định được
“cái này” là nội dung nào.

```json
{
  "status": "clarification_required",
  "answer": "",
  "important_keywords": [],
  "confidence": 0,
  "clarification_question": "Bạn muốn hỏi về khái niệm nào trên slide hiện tại: Transformer, token hay attention?",
  "sources": []
}
```

Quy tắc:

- `clarification_question` phải là một câu hỏi ngắn, cụ thể và có thể trả lời được.
- Không đưa ra câu trả lời phỏng đoán trước khi người dùng làm rõ.
- Không bịa nguồn để diễn giải một yêu cầu mơ hồ.
- Frontend gửi câu trả lời làm rõ của người dùng thành một request `/chat` mới.

## Response khi ngoài context

```json
{
  "status": "no_context",
  "answer": "Nội dung về ba bước chi tiết của RLHF chưa xuất hiện trong phạm vi slide bạn đã xem. Bạn có thể tiếp tục đến slide tiếp theo hoặc hỏi về vai trò tổng quát của RLHF.",
  "important_keywords": [],
  "confidence": 0,
  "clarification_question": null,
  "sources": []
}
```

Response phải:

- Nói rõ phần nào không có trong context.
- Không trả lời bằng kiến thức bên ngoài.
- Có thể gợi ý một câu hỏi khác mà context hiện tại trả lời được.
- Không yêu cầu làm rõ nếu yêu cầu đã rõ nhưng đơn giản là ngoài context.

## Chat response fields

| Field | Kiểu | Mô tả |
|---|---:|---|
| `status` | `string` | `answered`, `clarification_required`, `low_confidence` hoặc `no_context`. |
| `answer` | `string` | Câu trả lời Markdown; rỗng khi cần hỏi lại. |
| `important_keywords` | `string[]` | Từ khóa được bôi đậm trong `answer`. |
| `confidence` | `number` | Độ tin cậy từ `0.0` đến `1.0`. |
| `clarification_question` | `string \| null` | Câu hỏi làm rõ hoặc `null`. |
| `sources` | `Source[]` | Nguồn thực tế được sử dụng. |

---

# 2. Mindmap

## `POST /mindmaps`

Người dùng chọn một hoặc nhiều tài liệu, sau đó nhập prompt mô tả mindmap muốn
tạo. Agent chỉ được sử dụng nội dung của những tài liệu được chọn.

Ví dụ thao tác trên giao diện:

1. Chọn `AI & LLM Foundation`.
2. Chọn `Xác định bài toán cho AI`.
3. Nhập prompt: “So sánh LLM, workflow và agent; nêu trường hợp sử dụng”.
4. Bấm **Tạo mindmap**.

## Request

```http
POST /mindmaps
Content-Type: application/json
```

```json
{
  "document_ids": [
    "doc_day_01",
    "doc_day_02"
  ],
  "prompt": "So sánh LLM, workflow và agent; nêu trường hợp sử dụng."
}
```

| Field | Kiểu | Bắt buộc | Mô tả |
|---|---:|:---:|---|
| `document_ids` | `string[]` | Có | Từ 1 đến 20 ID tài liệu người dùng được quyền truy cập. Không được trùng ID. |
| `prompt` | `string` | Có | Yêu cầu tạo mindmap, từ 2 đến 2.000 ký tự. |

Request không truyền `title`. Agent tạo tiêu đề ngắn gọn từ prompt sau khi đã xác
định prompt đủ rõ.

Context của mindmap là hợp của nội dung trong `document_ids`:

```text
allowed_context = union(content(document_ids))
```

Agent không được:

- Dùng tài liệu không nằm trong `document_ids`.
- Bổ sung kiến thức ngoài tài liệu để làm mindmap có vẻ đầy đủ hơn.
- Tự chọn thêm tài liệu.
- Tự đoán chủ đề khi prompt mơ hồ.

## Response tạo thành công

```http
HTTP/1.1 201 Created
```

```json
{
  "status": "created",
  "mindmap_id": "mm_01JZ8D0M7CR6PVNQMT7A2H3B4C",
  "title": "LLM, Workflow và Agent",
  "prompt": "So sánh LLM, workflow và agent; nêu trường hợp sử dụng.",
  "document_ids": [
    "doc_day_01",
    "doc_day_02"
  ],
  "clarification_question": null,
  "message": "Đã tạo mindmap từ 2 tài liệu được chọn.",
  "mindmap": {
    "nodeData": {
      "id": "root",
      "topic": "LLM, Workflow và Agent",
      "root": true,
      "children": [
        {
          "id": "llm",
          "topic": "LLM",
          "direction": 0,
          "children": [
            {
              "id": "llm-role",
              "topic": "Bộ não suy luận"
            }
          ]
        },
        {
          "id": "workflow",
          "topic": "Workflow",
          "direction": 1,
          "children": [
            {
              "id": "workflow-role",
              "topic": "Chuỗi bước có kiểm soát"
            }
          ]
        },
        {
          "id": "agent",
          "topic": "Agent",
          "direction": 1,
          "children": [
            {
              "id": "agent-role",
              "topic": "Lập kế hoạch và dùng công cụ"
            }
          ]
        }
      ]
    },
    "arrows": [],
    "summaries": [],
    "direction": 2
  },
  "sources": [
    {
      "source_id": "source-1",
      "document_id": "doc_day_01",
      "file_name": "day-01-ai-llm-foundation.pdf",
      "page": 23,
      "slide": 23,
      "excerpt": "Agent không phải một loại model khác mà là LLM được đặt vào vòng làm việc."
    },
    {
      "source_id": "source-2",
      "document_id": "doc_day_02",
      "file_name": "day-02-xac-dinh-bai-toan-ai.pdf",
      "page": 18,
      "slide": 18,
      "excerpt": "Workflow phù hợp đầu vào đa dạng; Agent phù hợp tình huống nhiều bước và nhiều công cụ."
    }
  ],
  "created_at": "2026-07-31T10:30:00Z"
}
```

Backend phải lưu bản ghi và JSON Mind Elixir vào SQLite trước khi trả `201`.

## Response khi prompt chưa rõ

Ví dụ prompt: `"Tạo mindmap cho tôi"` không nói chủ đề, mục tiêu hoặc cách tổ chức
nội dung.

```http
HTTP/1.1 200 OK
```

```json
{
  "status": "clarification_required",
  "mindmap_id": null,
  "title": null,
  "prompt": "Tạo mindmap cho tôi",
  "document_ids": [
    "doc_day_01",
    "doc_day_02"
  ],
  "clarification_question": "Bạn muốn mindmap tập trung vào chủ đề nào trong hai tài liệu: nền tảng LLM, Agent hay cách xác định bài toán AI?",
  "message": "Cần làm rõ yêu cầu trước khi tạo mindmap.",
  "mindmap": {},
  "sources": [],
  "created_at": null
}
```

Quy tắc:

- Không tạo mindmap rỗng hoặc mindmap chung chung.
- Không ghi bản ghi vào SQLite.
- Không sinh `mindmap_id`.
- `mindmap` bắt buộc là `{}`.
- Câu hỏi làm rõ nên đưa ra lựa chọn phù hợp với nội dung tài liệu đã chọn.
- Sau khi người dùng trả lời, frontend gửi một request `POST /mindmaps` mới với
  prompt đã được làm rõ.

## Response khi prompt ngoài context

Ví dụ chọn hai bài học về AI nhưng prompt yêu cầu mindmap về điều trị bệnh tim:

```http
HTTP/1.1 200 OK
```

```json
{
  "status": "no_context",
  "mindmap_id": null,
  "title": null,
  "prompt": "Tạo mindmap phác đồ điều trị bệnh tim.",
  "document_ids": [
    "doc_day_01",
    "doc_day_02"
  ],
  "clarification_question": null,
  "message": "Các tài liệu đã chọn không chứa nội dung về phác đồ điều trị bệnh tim. Hãy chọn tài liệu y khoa phù hợp hoặc đổi prompt sang chủ đề có trong tài liệu.",
  "mindmap": {},
  "sources": [],
  "created_at": null
}
```

Quy tắc:

- Không tạo mindmap bằng kiến thức nền của LLM.
- Không lưu SQLite.
- Không gọi đây là prompt mơ hồ: prompt đã rõ nhưng ngoài context.
- Nói rõ tài liệu được chọn không có nội dung phù hợp.
- Gợi ý chọn tài liệu khác hoặc đổi prompt.
- `mindmap` là `{}` và `sources` là `[]`.

## Response khi chỉ một phần prompt có trong context

Ví dụ prompt yêu cầu so sánh “Attention và cơ chế lượng tử”, nhưng tài liệu chỉ có
Attention:

```json
{
  "status": "clarification_required",
  "mindmap_id": null,
  "title": null,
  "prompt": "So sánh Attention và cơ chế lượng tử.",
  "document_ids": [
    "doc_day_01"
  ],
  "clarification_question": "Tài liệu có nội dung về Attention nhưng không có cơ chế lượng tử. Bạn có muốn tạo mindmap chỉ về Attention không?",
  "message": "Một phần yêu cầu nằm ngoài nội dung tài liệu đã chọn.",
  "mindmap": {},
  "sources": [],
  "created_at": null
}
```

Không được tự bỏ phần ngoài context rồi tạo mindmap nếu chưa được người dùng xác
nhận.

## Mindmap response fields

| Field | Kiểu | Mô tả |
|---|---:|---|
| `status` | `string` | `created`, `cached`, `clarification_required` hoặc `no_context`. |
| `mindmap_id` | `string \| null` | ID bản ghi; `null` nếu chưa tạo. |
| `title` | `string \| null` | Tiêu đề do Agent tạo; `null` nếu chưa tạo. |
| `prompt` | `string` | Prompt gốc của người dùng. |
| `document_ids` | `string[]` | Tài liệu được dùng làm context. |
| `clarification_question` | `string \| null` | Câu hỏi làm rõ hoặc `null`. |
| `message` | `string` | Thông báo ngắn cho giao diện. |
| `mindmap` | `MindElixirData \| {}` | Dữ liệu Mind Elixir hoặc object rỗng. |
| `sources` | `Source[]` | Các nguồn thực tế dùng để tạo mindmap. |
| `created_at` | `string \| null` | Thời điểm lưu SQLite. |

---

# Mindmap cache và SQLite

## Nhận diện yêu cầu đã tạo

Cache key:

```text
user_id
+ sorted(unique(document_ids))
+ normalized(prompt)
```

`normalized(prompt)` phải ít nhất:

- Chuẩn hóa Unicode.
- Loại khoảng trắng thừa.
- Chuyển về chữ thường để so khớp.

Nếu đã có bản ghi cùng cache key, `POST /mindmaps` trả mindmap cũ:

```json
{
  "status": "cached",
  "mindmap_id": "mm_01JZ8D0M7CR6PVNQMT7A2H3B4C",
  "title": "LLM, Workflow và Agent",
  "prompt": "So sánh LLM, workflow và agent; nêu trường hợp sử dụng.",
  "document_ids": [
    "doc_day_01",
    "doc_day_02"
  ],
  "clarification_question": null,
  "message": "Đã tải mindmap đã lưu.",
  "mindmap": {
    "nodeData": {
      "id": "root",
      "topic": "LLM, Workflow và Agent",
      "root": true,
      "children": []
    },
    "arrows": [],
    "summaries": [],
    "direction": 2
  },
  "sources": [],
  "created_at": "2026-07-31T10:30:00Z"
}
```

Trong nhánh `"cached"`:

- Không gọi lại LLM.
- Không tạo bản ghi mới.
- Trả đúng JSON đã lưu trong SQLite.

## Bảng `mindmaps`

| Cột | Kiểu SQLite | Ràng buộc |
|---|---|---|
| `id` | `TEXT` | Primary key |
| `user_id` | `TEXT` | Not null |
| `title` | `TEXT` | Not null |
| `prompt` | `TEXT` | Not null |
| `normalized_prompt` | `TEXT` | Not null |
| `document_set_hash` | `TEXT` | Not null |
| `mindmap_json` | `TEXT` | Not null |
| `sources_json` | `TEXT` | Not null |
| `created_at` | `TEXT` | Not null |
| `updated_at` | `TEXT` | Not null |

Unique index:

```sql
UNIQUE(user_id, document_set_hash, normalized_prompt)
```

## Bảng `mindmap_documents`

| Cột | Kiểu SQLite | Ràng buộc |
|---|---|---|
| `mindmap_id` | `TEXT` | Foreign key → `mindmaps.id` |
| `document_id` | `TEXT` | Not null |

Primary key:

```sql
PRIMARY KEY(mindmap_id, document_id)
```

---

# Đọc mindmap đã lưu

Hai endpoint sau không tương tác với AI:

## `GET /mindmaps`

Liệt kê mindmap của người dùng từ SQLite.

```http
GET /mindmaps?limit=20&cursor=mm_01JZ8D0M
```

```json
{
  "items": [
    {
      "mindmap_id": "mm_01JZ8D0M7CR6PVNQMT7A2H3B4C",
      "title": "LLM, Workflow và Agent",
      "prompt": "So sánh LLM, workflow và agent; nêu trường hợp sử dụng.",
      "document_ids": [
        "doc_day_01",
        "doc_day_02"
      ],
      "created_at": "2026-07-31T10:30:00Z"
    }
  ],
  "next_cursor": null
}
```

## `GET /mindmaps/{mindmap_id}`

Đọc mindmap từ SQLite, không gọi LLM.

```http
GET /mindmaps/mm_01JZ8D0M7CR6PVNQMT7A2H3B4C
```

Response có `status: "cached"` và trả toàn bộ `mindmap`. Backend chỉ trả bản ghi
thuộc người dùng hiện tại.

---

# TypeScript types

```typescript
type ChatStatus =
  | "answered"
  | "clarification_required"
  | "low_confidence"
  | "no_context"

interface ChatRequest {
  question: string
  slide: number
  page: number
}

interface Source {
  source_id: string
  document_id: string
  file_name: string
  page: number
  slide: number
  excerpt: string
  relevance_score?: number
}

interface ChatResponse {
  status: ChatStatus
  answer: string
  important_keywords: string[]
  confidence: number
  clarification_question: string | null
  sources: Source[]
}

interface MindElixirNode {
  id: string
  topic: string
  root?: boolean
  direction?: 0 | 1
  children?: MindElixirNode[]
}

interface MindElixirData {
  nodeData: MindElixirNode
  arrows: unknown[]
  summaries: unknown[]
  direction: number
}

interface CreateMindmapRequest {
  document_ids: string[]
  prompt: string
}

type MindmapStatus =
  | "created"
  | "cached"
  | "clarification_required"
  | "no_context"

interface MindmapResponse {
  status: MindmapStatus
  mindmap_id: string | null
  title: string | null
  prompt: string
  document_ids: string[]
  clarification_question: string | null
  message: string
  mindmap: MindElixirData | Record<string, never>
  sources: Source[]
  created_at: string | null
}
```
