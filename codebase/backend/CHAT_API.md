# Chat API

## `POST /chat`

Nhận câu hỏi cùng slide và trang người dùng đang xem. Agent chỉ được sử dụng nội
dung từ đầu tài liệu đến slide/trang hiện tại, không được truy xuất nội dung ở các
slide phía sau.

## Request

```http
POST /chat
Content-Type: application/json
```

```json
{
  "question": "Attention hoạt động như thế nào?",
  "slide": 12,
  "page": 12
}
```

### Request fields

| Field | Kiểu | Bắt buộc | Mô tả |
|---|---:|:---:|---|
| `question` | `string` | Có | Câu hỏi của người dùng, từ 2 đến 2.000 ký tự. |
| `slide` | `integer` | Có | Slide người dùng đang xem, bắt đầu từ 1. |
| `page` | `integer` | Có | Trang PDF người dùng đang dừng, bắt đầu từ 1. |

### Quy tắc giới hạn context

Backend bắt buộc áp dụng đồng thời:

```text
source.slide <= request.slide
source.page <= request.page
```

Agent không được:

- Truy xuất nội dung từ slide lớn hơn `request.slide`.
- Truy xuất nội dung từ trang lớn hơn `request.page`.
- Dùng kiến thức từ các slide phía sau để bổ sung câu trả lời.
- Trích dẫn nguồn vượt quá vị trí hiện tại của người dùng.
- Tiết lộ trước nội dung người dùng chưa học tới.

Ví dụ, nếu request có `slide: 12` và `page: 12`, Agent chỉ được sử dụng nội dung
từ slide/trang 1–12. Slide hoặc trang 13 trở đi phải bị loại khỏi retrieval trước
khi tạo câu trả lời.

## Response thành công

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "answer": "**Attention** là cơ chế giúp mô hình xác định những phần thông tin quan trọng trong dữ liệu đầu vào. Cơ chế này giúp mô hình biểu diễn mối quan hệ giữa các **token** và hiểu **ngữ cảnh** tốt hơn.",
  "important_keywords": [
    "Attention",
    "token",
    "ngữ cảnh"
  ],
  "confidence": 0.87,
  "status": "answered",
  "sources": [
    {
      "source_id": "source-1",
      "file_name": "day-01-ai-llm-foundation.pdf",
      "page": 10,
      "slide": 10,
      "excerpt": "Attention cho phép mô hình xác định mức độ liên quan giữa các token trong cùng một chuỗi.",
      "relevance_score": 0.87
    },
    {
      "source_id": "source-2",
      "file_name": "day-01-ai-llm-foundation.pdf",
      "page": 12,
      "slide": 12,
      "excerpt": "Cơ chế attention hỗ trợ mô hình biểu diễn thông tin theo ngữ cảnh.",
      "relevance_score": 0.81
    }
  ],
  "mindmap": {
    "nodeData": {
      "id": "attention-root",
      "topic": "Attention",
      "root": true,
      "children": [
        {
          "id": "input",
          "topic": "Dữ liệu đầu vào",
          "direction": 0,
          "children": [
            {
              "id": "token",
              "topic": "Token"
            }
          ]
        },
        {
          "id": "weight",
          "topic": "Trọng số",
          "direction": 1,
          "children": [
            {
              "id": "relevance",
              "topic": "Mức độ liên quan"
            }
          ]
        },
        {
          "id": "result",
          "topic": "Kết quả",
          "direction": 1,
          "children": [
            {
              "id": "context",
              "topic": "Biểu diễn ngữ cảnh"
            }
          ]
        }
      ]
    },
    "arrows": [],
    "summaries": [],
    "direction": 2
  }
}
```

### Response fields

| Field | Kiểu | Mô tả |
|---|---:|---|
| `answer` | `string` | Câu trả lời ở định dạng Markdown. Các từ khóa quan trọng được bọc bằng `**`. |
| `important_keywords` | `string[]` | Các từ hoặc cụm từ quan trọng trong câu trả lời. |
| `confidence` | `number` | Độ tin cậy từ `0.0` đến `1.0`. |
| `status` | `string` | `answered`, `low_confidence` hoặc `no_context`. |
| `sources` | `Source[]` | Nguồn Agent thực sự sử dụng. Mọi nguồn phải nằm trong phạm vi hiện tại. |
| `mindmap` | `object` | Dữ liệu Mind Elixir hoặc object rỗng `{}`. |

### Source object

| Field | Kiểu | Mô tả |
|---|---:|---|
| `source_id` | `string` | ID duy nhất của nguồn trong response. |
| `file_name` | `string` | Tên file PDF chứa nguồn. |
| `page` | `integer` | Trang chứa nguồn, phải nhỏ hơn hoặc bằng `request.page`. |
| `slide` | `integer` | Slide chứa nguồn, phải nhỏ hơn hoặc bằng `request.slide`. |
| `excerpt` | `string` | Đoạn nội dung Agent đã sử dụng. |
| `relevance_score` | `number` | Mức độ liên quan từ `0.0` đến `1.0`. |

### Mind Elixir object

Khi có mindmap:

```json
{
  "mindmap": {
    "nodeData": {
      "id": "root",
      "topic": "Chủ đề",
      "root": true,
      "children": [
        {
          "id": "branch-1",
          "topic": "Nhánh 1",
          "direction": 0,
          "children": []
        },
        {
          "id": "branch-2",
          "topic": "Nhánh 2",
          "direction": 1,
          "children": []
        }
      ]
    },
    "arrows": [],
    "summaries": [],
    "direction": 2
  }
}
```

Object trong `mindmap` phải có thể truyền trực tiếp vào Mind Elixir:

```typescript
mind.init(response.mindmap)
```

Quy tắc dữ liệu:

- `nodeData` là node gốc và bắt buộc có `id`, `topic`, `root: true`.
- Mỗi node con bắt buộc có `id` duy nhất và `topic`.
- `children` chứa các node con; có thể là mảng rỗng.
- `direction` của nhánh chính sử dụng `0` hoặc `1`.
- `arrows` chứa các liên kết bổ sung giữa node; trả `[]` nếu không sử dụng.
- `summaries` chứa dữ liệu tổng hợp nhiều node; trả `[]` nếu không sử dụng.
- `direction` cấp mindmap xác định hướng bố cục; mặc định dùng `2`.
- Backend chỉ trả dữ liệu, frontend chịu trách nhiệm render bằng Mind Elixir.

Khi không có mindmap:

```json
{
  "mindmap": {}
}
```

`mindmap` luôn phải xuất hiện. Không trả về `null`, chuỗi rỗng hoặc bỏ field.

## Quy tắc từ khóa quan trọng

1. `important_keywords` chỉ chứa từ hoặc cụm từ liên quan trực tiếp đến câu trả lời.
2. Mỗi từ khóa phải xuất hiện trong `answer`.
3. Từ khóa trong `answer` phải được bôi đậm bằng Markdown: `**từ khóa**`.
4. Không bôi đậm cả câu hoặc đoạn văn dài.
5. Không lặp từ khóa trong `important_keywords`.
6. Nếu không có từ khóa quan trọng, trả về `important_keywords: []`.

## Không đủ độ tin cậy

```json
{
  "answer": "Mình chưa tìm thấy căn cứ đủ chắc chắn trong phạm vi các slide bạn đã xem.",
  "important_keywords": [],
  "confidence": 0.08,
  "status": "low_confidence",
  "sources": [
    {
      "source_id": "source-1",
      "file_name": "day-01-ai-llm-foundation.pdf",
      "page": 4,
      "slide": 4,
      "excerpt": "Đoạn gần nhất được tìm thấy nhưng chưa đủ để trả lời chính xác câu hỏi.",
      "relevance_score": 0.08
    }
  ],
  "mindmap": {}
}
```

## Không tìm thấy context phù hợp

```json
{
  "answer": "Không tìm thấy nội dung phù hợp trong phạm vi các slide bạn đã xem.",
  "important_keywords": [],
  "confidence": 0,
  "status": "no_context",
  "sources": [],
  "mindmap": {}
}
```

Nếu câu hỏi chỉ có thể được trả lời bằng nội dung sau vị trí hiện tại:

```json
{
  "answer": "Nội dung cần thiết để trả lời câu hỏi này chưa xuất hiện trong phạm vi slide bạn đang xem.",
  "important_keywords": [],
  "confidence": 0,
  "status": "no_context",
  "sources": [],
  "mindmap": {}
}
```

Backend không được tự động mở rộng phạm vi sang slide tiếp theo.

## Lỗi dữ liệu đầu vào

```http
HTTP/1.1 422 Unprocessable Entity
```

```json
{
  "detail": [
    {
      "loc": ["body", "question"],
      "msg": "String should have at least 2 characters",
      "type": "string_too_short"
    }
  ]
}
```

## TypeScript types

```typescript
interface ChatRequest {
  question: string
  slide: number
  page: number
}

type ChatStatus = "answered" | "low_confidence" | "no_context"

interface ChatSource {
  source_id: string
  file_name: string
  page: number
  slide: number
  excerpt: string
  relevance_score: number
}

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
  delta1?: {
    x: number
    y: number
  }
  delta2?: {
    x: number
    y: number
  }
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

interface ChatResponse {
  answer: string
  important_keywords: string[]
  confidence: number
  status: ChatStatus
  sources: ChatSource[]
  mindmap: MindElixirData | Record<string, never>
}
```
