import { DOCUMENTS } from "@/lib/mindmap-api"
import { postJson } from "@/lib/api-client"

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
  document_id: string
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

interface ApiCitation {
  source_file: string
  document_id: string
  document_title: string
  slide_number: number
  chunk_id: string
  excerpt: string
}

interface ApiChatResponse {
  status: ChatStatus | null
  answer: string
  important_keywords: string[]
  confidence: number
  abstained: boolean
  clarification_question: string | null
  citations: ApiCitation[]
}

export async function sendChatMessage(
  request: ChatRequest,
  context: ChatDocumentContext
): Promise<ChatResponse> {
  const response = await postJson<ApiChatResponse>("/chat", {
    ...request,
    document_id: context.document_id,
  })
  return {
    status:
      response.status ??
      (response.abstained ? "low_confidence" : "answered"),
    answer: response.answer,
    important_keywords: response.important_keywords ?? [],
    confidence: response.confidence,
    clarification_question: response.clarification_question,
    sources: (response.citations ?? []).map((citation) => ({
      source_id: citation.chunk_id,
      document_id: citation.document_id,
      file_name: citation.source_file || context.file_name,
      page: citation.slide_number,
      slide: citation.slide_number,
      excerpt: citation.excerpt,
    })),
  }
}

export function findChatDocumentContext(
  slideFileId: string
): ChatDocumentContext | undefined {
  const doc = DOCUMENTS.find((item) => item.slideFileId === slideFileId)
  if (!doc) return undefined
  return { document_id: doc.id, file_name: doc.fileName }
}
