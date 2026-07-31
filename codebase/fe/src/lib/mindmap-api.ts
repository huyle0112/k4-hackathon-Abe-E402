import type { MindElixirData, NodeObj } from "mind-elixir"
import { SIDE } from "mind-elixir"

import { COURSES } from "@/data/comp2010-slides"
import { MINDMAPS, node } from "@/data/mindmap-data"

/**
 * Client-side mock of the `POST /mindmaps` contract documented in
 * codebase/backend/CHAT_API.md. The real endpoint doesn't exist yet (the
 * backend only has a CLI RAG pipeline), so this simulates status branches,
 * caching and history the same way `reader-chat-sidebar.tsx` mocks `/chat`.
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

export type MindmapStatus =
  | "created"
  | "cached"
  | "clarification_required"
  | "no_context"

export interface CreateMindmapRequest {
  document_ids: string[]
  prompt: string
}

export interface MindmapResponse {
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

export interface MindmapDocument {
  id: string
  title: string
  fileName: string
  slideFileId: string
  day: number
}

export const DOCUMENTS: MindmapDocument[] = COURSES.comp2010.days
  .filter((day) => day.files.length > 0)
  .map((day) => {
    const file = day.files[0]
    return {
      id: `doc_day_${String(day.day).padStart(2, "0")}`,
      title: file.label,
      fileName: file.fileName,
      slideFileId: file.id,
      day: day.day,
    }
  })

const VAGUE_PROMPTS = [
  "tạo mindmap",
  "tạo mindmap cho tôi",
  "làm mindmap",
  "vẽ mindmap",
  "mindmap cho tôi",
  "sơ đồ tư duy",
  "vẽ sơ đồ tư duy",
]

export const OUT_OF_CONTEXT_KEYWORDS = [
  "bệnh tim",
  "phác đồ điều trị",
  "y tế",
  "nấu ăn",
  "công thức nấu",
  "bóng đá",
  "thời tiết",
  "du lịch",
  "chứng khoán",
  "bất động sản",
]

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function normalizePrompt(prompt: string): string {
  return prompt.normalize("NFC").trim().replace(/\s+/g, " ").toLowerCase()
}

function isVague(normalized: string): boolean {
  return normalized.length < 10 || VAGUE_PROMPTS.includes(normalized)
}

function isOutOfContext(normalized: string): boolean {
  return OUT_OF_CONTEXT_KEYWORDS.some((keyword) => normalized.includes(keyword))
}

function buildTitle(prompt: string): string {
  const trimmed = prompt.trim()
  const short = trimmed.length > 48 ? `${trimmed.slice(0, 45)}…` : trimmed
  return short.charAt(0).toUpperCase() + short.slice(1)
}

function buildCreatedNodeData(documentIds: string[], prompt: string): NodeObj {
  const branches: NodeObj[] = []
  for (const docId of documentIds) {
    const doc = DOCUMENTS.find((d) => d.id === docId)
    const sourceData = doc ? MINDMAPS[doc.slideFileId] : undefined
    if (!doc || !sourceData) continue
    for (const branch of (sourceData.nodeData.children ?? []).slice(0, 2)) {
      branches.push(node(`${doc.title}: ${branch.topic}`, branch.children))
    }
  }
  return { ...node(buildTitle(prompt), branches), root: true } as NodeObj
}

function buildSources(documentIds: string[]): Source[] {
  return documentIds.map((docId, i) => {
    const doc = DOCUMENTS.find((d) => d.id === docId)
    const page = 4 + i * 5
    return {
      source_id: `source-${i + 1}`,
      document_id: docId,
      file_name: doc?.fileName ?? docId,
      page,
      slide: page,
      excerpt: `${doc?.title ?? docId} — trích đoạn minh hoạ liên quan đến prompt (mock).`,
      relevance_score: Math.round((0.75 + Math.random() * 0.2) * 100) / 100,
    }
  })
}

let mindmapCounter = 0
const cache = new Map<string, MindmapResponse>()
const history: MindmapResponse[] = []

function cacheKey(documentIds: string[], normalizedPrompt: string): string {
  return `${[...documentIds].sort().join(",")}::${normalizedPrompt}`
}

export async function createMindmapMock(
  request: CreateMindmapRequest
): Promise<MindmapResponse> {
  const normalized = normalizePrompt(request.prompt)
  const key = cacheKey(request.document_ids, normalized)

  const cached = cache.get(key)
  if (cached) {
    return { ...cached, status: "cached", message: "Đã tải mindmap đã lưu." }
  }

  await sleep(700 + Math.random() * 400)

  const selectedDocs = DOCUMENTS.filter((d) =>
    request.document_ids.includes(d.id)
  )

  if (isOutOfContext(normalized)) {
    return {
      status: "no_context",
      mindmap_id: null,
      title: null,
      prompt: request.prompt,
      document_ids: request.document_ids,
      clarification_question: null,
      message: `Các tài liệu đã chọn (${selectedDocs.map((d) => d.title).join(", ")}) không chứa nội dung phù hợp với yêu cầu này. Hãy chọn tài liệu khác hoặc đổi prompt sang chủ đề có trong tài liệu.`,
      mindmap: {},
      sources: [],
      created_at: null,
    }
  }

  if (isVague(normalized)) {
    const options = selectedDocs
      .flatMap((d) => MINDMAPS[d.slideFileId]?.nodeData.children ?? [])
      .slice(0, 3)
      .map((c) => c.topic)
    return {
      status: "clarification_required",
      mindmap_id: null,
      title: null,
      prompt: request.prompt,
      document_ids: request.document_ids,
      clarification_question:
        options.length > 0
          ? `Bạn muốn mindmap tập trung vào chủ đề nào: ${options.join(", ")}?`
          : "Bạn muốn mindmap tập trung vào chủ đề hoặc mục tiêu gì?",
      message: "Cần làm rõ yêu cầu trước khi tạo mindmap.",
      mindmap: {},
      sources: [],
      created_at: null,
    }
  }

  mindmapCounter += 1
  const nodeData = buildCreatedNodeData(request.document_ids, request.prompt)
  const response: MindmapResponse = {
    status: "created",
    mindmap_id: `mm_${Date.now().toString(36)}${mindmapCounter.toString(36)}`,
    title: nodeData.topic,
    prompt: request.prompt,
    document_ids: request.document_ids,
    clarification_question: null,
    message: `Đã tạo mindmap từ ${selectedDocs.length} tài liệu được chọn.`,
    mindmap: { nodeData, arrows: [], summaries: [], direction: SIDE },
    sources: buildSources(request.document_ids),
    created_at: new Date().toISOString(),
  }

  cache.set(key, response)
  history.unshift(response)
  return response
}

export function getMindmapHistory(): MindmapResponse[] {
  return [...history]
}

export function getMindmapById(mindmapId: string): MindmapResponse | undefined {
  return history.find((entry) => entry.mindmap_id === mindmapId)
}
