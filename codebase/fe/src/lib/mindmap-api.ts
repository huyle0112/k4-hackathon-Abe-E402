import type { MindElixirData } from "mind-elixir"

import { COURSES } from "@/data/comp2010-slides"
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

const INDEXED_DOCUMENT_IDS: Record<number, string> = {
  1: "day-01-ai-llm-foundation",
  2: "day-02-xac-dinh-bai-toan-ai",
}

export const DOCUMENTS: MindmapDocument[] = COURSES.comp2010.days
  .filter((day) => day.files.length > 0 && INDEXED_DOCUMENT_IDS[day.day])
  .map((day) => {
    const file = day.files[0]
    return {
      id: INDEXED_DOCUMENT_IDS[day.day],
      title: file.label,
      fileName: file.fileName,
      slideFileId: file.id,
      day: day.day,
    }
  })

const history: MindmapResponse[] = []

export async function createMindmap(
  request: CreateMindmapRequest
): Promise<MindmapResponse> {
  const response = await postJson<MindmapResponse>("/mindmaps", request, {
    "X-User-Id": "vlearn-web",
  })
  if (
    (response.status === "created" || response.status === "cached") &&
    response.mindmap_id
  ) {
    const existing = history.findIndex(
      (entry) => entry.mindmap_id === response.mindmap_id
    )
    if (existing >= 0) history.splice(existing, 1)
    history.unshift(response)
  }
  return response
}

export function getMindmapHistory(): MindmapResponse[] {
  return [...history]
}

export function getMindmapById(mindmapId: string): MindmapResponse | undefined {
  return history.find((entry) => entry.mindmap_id === mindmapId)
}

export function findDocumentBySlideFileId(
  slideFileId: string
): MindmapDocument | undefined {
  return DOCUMENTS.find((doc) => doc.slideFileId === slideFileId)
}
