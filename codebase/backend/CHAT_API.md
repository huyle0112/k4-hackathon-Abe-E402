# VLearn API

## Nguyên tắc chung

- Chat và mindmap là hai chức năng độc lập.
- `POST /chat` không tự tạo hoặc trả về mindmap.
- Mindmap chỉ được tạo khi người dùng chủ động gọi `POST /mindmaps`.
- Mindmap được lưu trong SQLite sau khi tạo thành công.
- Khi người dùng mở lại mindmap cũ, backend đọc từ SQLite và không gọi lại LLM.
- Agent chỉ được dùng nội dung đến slide/trang hiện tại:

```text
source.slide <= request.slide
source.page <= request.page
```

---

# Chat

## `POST /chat`

Gửi câu hỏi về nội dung người dùng đã xem.

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

### Request fields

| Field | Kiểu | Bắt buộc | Mô tả |
|---|---:|:---:|---|
| `question` | `string` | Có | Câu hỏi, từ 2 đến 2.000 ký tự. |
| `slide` | `integer` | Có | Slide hiện tại, bắt đầu từ 1. |
| `page` | `integer` | Có | Trang PDF hiện tại, bắt đầu từ 1. |

## Response

```json
{
  "answer": "**Attention** cho phép mỗi **token** xác định những token khác có liên quan trong cùng ngữ cảnh.",
  "important_keywords": [
    "Attention",
    "token"
  ],
  "confidence": 0.87,
  "status": "answered",
  "sources": [
    {
      "source_id": "source-1",
      "file_name": "day-01-ai-llm-foundation.pdf",
      "page": 15,
      "slide": 15,
      "excerpt": "Attention cho phép mỗi token nhìn lại và chấm mức độ liên quan của các token trước đó.",
      "relevance_score": 0.87
    }
  ]
}
```

### Response fields

| Field | Kiểu | Mô tả |
|---|---:|---|
| `answer` | `string` | Câu trả lời Markdown. Từ khóa quan trọng được bọc bằng `**`. |
| `important_keywords` | `string[]` | Từ hoặc cụm từ quan trọng xuất hiện trong câu trả lời. |
| `confidence` | `number` | Độ tin cậy từ `0.0` đến `1.0`. |
| `status` | `string` | `answered`, `low_confidence` hoặc `no_context`. |
| `sources` | `Source[]` | Nguồn Agent thực sự sử dụng. |

`/chat` không có field `mindmap`.

## Không tìm thấy context

```json
{
  "answer": "Không tìm thấy nội dung phù hợp trong phạm vi các slide bạn đã xem.",
  "important_keywords": [],
  "confidence": 0,
  "status": "no_context",
  "sources": []
}
```

---

# Mindmap

## Luồng hoạt động

```text
Người dùng bấm “Tạo mindmap”
    ↓
POST /mindmaps
    ↓
Backend kiểm tra mindmap trùng trong SQLite
    ├── Đã tồn tại → trả bản ghi cũ, không gọi LLM
    └── Chưa tồn tại → gọi LLM → lưu SQLite → trả bản ghi mới

Người dùng mở lại mindmap
    ↓
GET /mindmaps/{mindmap_id}
    ↓
Đọc SQLite → trả dữ liệu Mind Elixir, không gọi LLM
```

## `POST /mindmaps`

Tạo mindmap theo phạm vi tài liệu người dùng đã xem.

Endpoint này có tính idempotent theo tổ hợp:

```text
user_id + document_id + slide + page + normalized(title)
```

Nếu mindmap tương ứng đã tồn tại, backend trả lại bản ghi cũ với
`generation_status: "cached"` và không gọi LLM.

## Request

```http
POST /mindmaps
Content-Type: application/json
```

```json
{
  "title": "Tổng quan Attention",
  "slide": 16,
  "page": 16
}
```

### Request fields

| Field | Kiểu | Bắt buộc | Mô tả |
|---|---:|:---:|---|
| `title` | `string` | Có | Chủ đề hoặc tên mindmap, từ 2 đến 200 ký tự. |
| `slide` | `integer` | Có | Slide cuối cùng được phép dùng. |
| `page` | `integer` | Có | Trang cuối cùng được phép dùng. |

`user_id` được lấy từ phiên đăng nhập. `document_id` được lấy từ tài liệu đang mở;
hai giá trị này không được client tự truyền trong body.

## Response khi tạo mới

```http
HTTP/1.1 201 Created
```

```json
{
  "mindmap_id": "mm_01JZ8D0M7CR6PVNQMT7A2H3B4C",
  "title": "Tổng quan Attention",
  "document_id": "doc_day_01",
  "file_name": "day-01-ai-llm-foundation.pdf",
  "context_boundary": {
    "slide": 16,
    "page": 16
  },
  "generation_status": "generated",
  "mindmap": {
    "nodeData": {
      "id": "attention-root",
      "topic": "Attention",
      "root": true,
      "children": [
        {
          "id": "attention-mechanism",
          "topic": "Cơ chế",
          "direction": 0,
          "children": [
            {
              "id": "token-relevance",
              "topic": "Mức độ liên quan giữa token"
            }
          ]
        },
        {
          "id": "attention-context",
          "topic": "Quản lý context",
          "direction": 1,
          "children": [
            {
              "id": "clean-context",
              "topic": "Giữ context sạch"
            },
            {
              "id": "rag-context",
              "topic": "Lấy đúng đoạn bằng RAG"
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
      "file_name": "day-01-ai-llm-foundation.pdf",
      "page": 15,
      "slide": 15,
      "excerpt": "Attention cho phép mỗi token nhìn lại các token quan trọng khác."
    },
    {
      "source_id": "source-2",
      "file_name": "day-01-ai-llm-foundation.pdf",
      "page": 16,
      "slide": 16,
      "excerpt": "Cách bày context quyết định model chú ý vào đâu."
    }
  ],
  "created_at": "2026-07-31T10:30:00Z",
  "updated_at": "2026-07-31T10:30:00Z"
}
```

## Response khi mindmap đã tồn tại

```http
HTTP/1.1 200 OK
```

```json
{
  "mindmap_id": "mm_01JZ8D0M7CR6PVNQMT7A2H3B4C",
  "title": "Tổng quan Attention",
  "document_id": "doc_day_01",
  "file_name": "day-01-ai-llm-foundation.pdf",
  "context_boundary": {
    "slide": 16,
    "page": 16
  },
  "generation_status": "cached",
  "mindmap": {
    "nodeData": {
      "id": "attention-root",
      "topic": "Attention",
      "root": true,
      "children": []
    },
    "arrows": [],
    "summaries": [],
    "direction": 2
  },
  "sources": [],
  "created_at": "2026-07-31T10:30:00Z",
  "updated_at": "2026-07-31T10:30:00Z"
}
```

`generation_status: "cached"` bảo đảm response được lấy từ SQLite. Backend không
được gọi LLM trong nhánh này.

---

## `GET /mindmaps`

Lấy danh sách mindmap đã lưu của người dùng hiện tại. Endpoint chỉ đọc SQLite.

### Request

```http
GET /mindmaps?document_id=doc_day_01&limit=20&cursor=mm_01JZ8D0M
```

### Query parameters

| Field | Kiểu | Bắt buộc | Mô tả |
|---|---:|:---:|---|
| `document_id` | `string` | Không | Chỉ lấy mindmap của một tài liệu. |
| `limit` | `integer` | Không | Số bản ghi, từ 1 đến 100; mặc định 20. |
| `cursor` | `string` | Không | Cursor phân trang từ response trước. |

### Response

```json
{
  "items": [
    {
      "mindmap_id": "mm_01JZ8D0M7CR6PVNQMT7A2H3B4C",
      "title": "Tổng quan Attention",
      "document_id": "doc_day_01",
      "file_name": "day-01-ai-llm-foundation.pdf",
      "context_boundary": {
        "slide": 16,
        "page": 16
      },
      "created_at": "2026-07-31T10:30:00Z",
      "updated_at": "2026-07-31T10:30:00Z"
    }
  ],
  "next_cursor": null
}
```

Danh sách không cần trả toàn bộ cây mindmap để giảm kích thước response.

---

## `GET /mindmaps/{mindmap_id}`

Mở lại một mindmap đã lưu. Endpoint đọc dữ liệu trực tiếp từ SQLite và tuyệt đối
không gọi LLM.

### Request

```http
GET /mindmaps/mm_01JZ8D0M7CR6PVNQMT7A2H3B4C
```

### Response

```http
HTTP/1.1 200 OK
```

```json
{
  "mindmap_id": "mm_01JZ8D0M7CR6PVNQMT7A2H3B4C",
  "title": "Tổng quan Attention",
  "document_id": "doc_day_01",
  "file_name": "day-01-ai-llm-foundation.pdf",
  "context_boundary": {
    "slide": 16,
    "page": 16
  },
  "generation_status": "cached",
  "mindmap": {
    "nodeData": {
      "id": "attention-root",
      "topic": "Attention",
      "root": true,
      "children": []
    },
    "arrows": [],
    "summaries": [],
    "direction": 2
  },
  "sources": [],
  "created_at": "2026-07-31T10:30:00Z",
  "updated_at": "2026-07-31T10:30:00Z"
}
```

Frontend truyền trực tiếp `mindmap` vào Mind Elixir:

```typescript
mind.init(response.mindmap)
```

### Không tìm thấy

```http
HTTP/1.1 404 Not Found
```

```json
{
  "error": {
    "code": "MINDMAP_NOT_FOUND",
    "message": "Không tìm thấy mindmap."
  }
}
```

Backend phải kiểm tra mindmap thuộc người dùng hiện tại; không được trả mindmap của
người dùng khác.

---

# Cấu trúc Mind Elixir

```typescript
interface MindElixirNode {
  id: string
  topic: string
  root?: boolean
  direction?: 0 | 1
  children?: MindElixirNode[]
  expanded?: boolean
  tags?: string[]
  style?: {
    fontSize?: string
    color?: string
    background?: string
    fontWeight?: string
  }
}

interface MindElixirArrow {
  id: string
  label: string
  from: string
  to: string
  delta1?: { x: number; y: number }
  delta2?: { x: number; y: number }
}

interface MindElixirSummary {
  id: string
  parent: string
  start: number
  end: number
  text: string
}

interface MindElixirData {
  nodeData: MindElixirNode
  arrows: MindElixirArrow[]
  summaries: MindElixirSummary[]
  direction: number
}
```

## Quy tắc dữ liệu

- `nodeData` là node gốc, bắt buộc có `id`, `topic` và `root: true`.
- Mỗi node phải có `id` duy nhất trong mindmap.
- `children` chứa node con và có thể là mảng rỗng.
- `arrows` và `summaries` phải là mảng, kể cả khi không có dữ liệu.
- Không lưu HTML không tin cậy trong `dangerouslySetInnerHTML`.
- JSON Mind Elixir phải được kiểm tra schema trước khi ghi SQLite.

---

# Dữ liệu SQLite

## Bảng `mindmaps`

| Cột | Kiểu SQLite | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | `TEXT` | Primary key | ID mindmap. |
| `user_id` | `TEXT` | Not null | Chủ sở hữu. |
| `document_id` | `TEXT` | Not null | Tài liệu nguồn. |
| `file_name` | `TEXT` | Not null | Tên file tại thời điểm tạo. |
| `title` | `TEXT` | Not null | Tiêu đề mindmap. |
| `normalized_title` | `TEXT` | Not null | Tiêu đề chuẩn hóa để chống tạo trùng. |
| `slide` | `INTEGER` | Not null | Slide tối đa đã dùng. |
| `page` | `INTEGER` | Not null | Trang tối đa đã dùng. |
| `mindmap_json` | `TEXT` | Not null | JSON Mind Elixir. |
| `sources_json` | `TEXT` | Not null | JSON danh sách nguồn. |
| `created_at` | `TEXT` | Not null | Thời điểm tạo theo ISO 8601 UTC. |
| `updated_at` | `TEXT` | Not null | Thời điểm cập nhật theo ISO 8601 UTC. |

Unique index:

```sql
UNIQUE(user_id, document_id, slide, page, normalized_title)
```

Quy tắc gọi LLM:

| Endpoint | Được gọi LLM? |
|---|:---:|
| `POST /chat` | Có |
| `POST /mindmaps` khi chưa có bản ghi | Có |
| `POST /mindmaps` khi đã có bản ghi | Không |
| `GET /mindmaps` | Không |
| `GET /mindmaps/{mindmap_id}` | Không |

---

# TypeScript API types

```typescript
interface ChatRequest {
  question: string
  slide: number
  page: number
}

type ChatStatus = "answered" | "low_confidence" | "no_context"

interface Source {
  source_id: string
  file_name: string
  page: number
  slide: number
  excerpt: string
  relevance_score?: number
}

interface ChatResponse {
  answer: string
  important_keywords: string[]
  confidence: number
  status: ChatStatus
  sources: Source[]
}

interface CreateMindmapRequest {
  title: string
  slide: number
  page: number
}

interface MindmapResponse {
  mindmap_id: string
  title: string
  document_id: string
  file_name: string
  context_boundary: {
    slide: number
    page: number
  }
  generation_status: "generated" | "cached"
  mindmap: MindElixirData
  sources: Source[]
  created_at: string
  updated_at: string
}

interface MindmapListItem {
  mindmap_id: string
  title: string
  document_id: string
  file_name: string
  context_boundary: {
    slide: number
    page: number
  }
  created_at: string
  updated_at: string
}

interface MindmapListResponse {
  items: MindmapListItem[]
  next_cursor: string | null
}
```
