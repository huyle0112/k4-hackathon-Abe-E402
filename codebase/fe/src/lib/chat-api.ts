import { DOCUMENTS, OUT_OF_CONTEXT_KEYWORDS } from "@/lib/mindmap-api"

/**
 * Client-side mock of the `POST /chat` contract documented in
 * codebase/backend/CHAT_API.md. The real endpoint doesn't exist yet, so this
 * simulates the status branches (answered / clarification_required /
 * low_confidence / no_context) the same way `mindmap-api.ts` mocks
 * `POST /mindmaps`.
 */

export interface Source {
  source_id: string
  document_id: string
  file_name: string
  page: number
  slide: number
  excerpt: string
  relevance_score?: number
}

export type ChatStatus =
  | "answered"
  | "clarification_required"
  | "low_confidence"
  | "no_context"

export interface ChatRequest {
  question: string
  slide: number
  page: number
}

export interface ChatResponse {
  status: ChatStatus
  answer: string
  important_keywords: string[]
  confidence: number
  clarification_question: string | null
  sources: Source[]
}

export interface ChatDocumentContext {
  document_id: string
  file_name: string
}

const VAGUE_PRONOUNS = ["cái này", "cái đó", "chỗ này", "phần này", "nó"]

const TOPIC_ANSWERS: Array<{
  keywords: string[]
  answer: string
  important_keywords: string[]
  excerpt: string
}> = [
  {
    keywords: ["healthcare", "y tế", "bệnh nhân"],
    answer:
      "Sản phẩm **y tế** tốt cần giải quyết một vấn đề thật của người dùng (bệnh nhân, bác sĩ, bệnh viện) và đo lường được giá trị mang lại, không chỉ dừng ở công nghệ.",
    important_keywords: ["y tế"],
    excerpt:
      "Đề bài yêu cầu nhóm xây dựng sản phẩm tạo ra giá trị thực sự cho lĩnh vực y tế — ví dụ cải thiện trải nghiệm bệnh nhân, hỗ trợ bác sĩ chẩn đoán, hoặc tối ưu vận hành bệnh viện.",
  },
  {
    keywords: ["nhóm", "team", "hackathon"],
    answer:
      "Mỗi **nhóm** hackathon nên phân vai rõ ràng (research, dev, thuyết trình) và bám sát checklist nộp bài theo từng ngày để không bị dồn việc vào cuối kỳ.",
    important_keywords: ["nhóm"],
    excerpt:
      "Slide nêu mục tiêu môn học, cách chia nhóm và các mốc nộp bài trong Phase 1.",
  },
  {
    keywords: ["deadline", "nộp bài", "mốc"],
    answer:
      "Các **mốc nộp bài** thường nằm ở cuối mỗi ngày học — bạn nên xem lại phần lịch trình ở đầu slide Day tương ứng để nắm chính xác thời hạn.",
    important_keywords: ["mốc nộp bài"],
    excerpt: "Lịch trình nộp bài được liệt kê theo từng ngày học (Day 1 → Day N).",
  },
]

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function normalizeQuestion(question: string): string {
  return question.normalize("NFC").trim().toLowerCase()
}

function isVague(normalized: string): boolean {
  const hasPronoun = VAGUE_PRONOUNS.some((p) => normalized.includes(p))
  const hasTopic = TOPIC_ANSWERS.some((entry) =>
    entry.keywords.some((k) => normalized.includes(k))
  )
  return (hasPronoun || normalized.length < 8) && !hasTopic
}

function isOutOfContext(normalized: string): boolean {
  return OUT_OF_CONTEXT_KEYWORDS.some((keyword) => normalized.includes(keyword))
}

export async function sendChatMessageMock(
  request: ChatRequest,
  context: ChatDocumentContext
): Promise<ChatResponse> {
  await sleep(700 + Math.random() * 400)

  const normalized = normalizeQuestion(request.question)

  if (isOutOfContext(normalized)) {
    return {
      status: "no_context",
      answer: `Nội dung này chưa xuất hiện trong phạm vi bạn đã xem của "${context.file_name}" (đến trang ${request.page}). Bạn có thể tiếp tục đọc thêm hoặc hỏi về nội dung khác đã có trong tài liệu.`,
      important_keywords: [],
      confidence: 0,
      clarification_question: null,
      sources: [],
    }
  }

  if (isVague(normalized)) {
    return {
      status: "clarification_required",
      answer: "",
      important_keywords: [],
      confidence: 0,
      clarification_question:
        "Bạn muốn hỏi cụ thể về nội dung nào trên slide hiện tại?",
      sources: [],
    }
  }

  const found = TOPIC_ANSWERS.find((entry) =>
    entry.keywords.some((k) => normalized.includes(k))
  )

  const source: Source = {
    source_id: "source-1",
    document_id: context.document_id,
    file_name: context.file_name,
    page: request.page,
    slide: request.slide,
    excerpt: found?.excerpt ?? `${context.file_name} — trích đoạn liên quan đến câu hỏi (mock).`,
    relevance_score: found
      ? Math.round((0.8 + Math.random() * 0.15) * 100) / 100
      : Math.round((0.35 + Math.random() * 0.15) * 100) / 100,
  }

  if (!found) {
    return {
      status: "low_confidence",
      answer:
        "Mình chưa chắc câu trả lời chính xác cho câu hỏi này dựa trên nội dung bạn đã xem. Bạn có thể hỏi cụ thể hơn hoặc thử diễn đạt khác.",
      important_keywords: [],
      confidence: source.relevance_score ?? 0.4,
      clarification_question: null,
      sources: [source],
    }
  }

  return {
    status: "answered",
    answer: found.answer,
    important_keywords: found.important_keywords,
    confidence: source.relevance_score ?? 0.85,
    clarification_question: null,
    sources: [source],
  }
}

export function findChatDocumentContext(slideFileId: string): ChatDocumentContext | undefined {
  const doc = DOCUMENTS.find((d) => d.slideFileId === slideFileId)
  if (!doc) return undefined
  return { document_id: doc.id, file_name: doc.fileName }
}
