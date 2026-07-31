import { useState } from "react"
import type { MindElixirData } from "mind-elixir"

import {
  createMindmapMock,
  getMindmapById,
  getMindmapHistory,
  type MindmapResponse,
} from "@/lib/mindmap-api"

export function useMindmapCreate(
  initialSelectedIds: string[] = [],
  initialMindmapId?: string
) {
  const initialEntry = initialMindmapId ? getMindmapById(initialMindmapId) ?? null : null

  const [selectedIds, setSelectedIds] = useState<string[]>(
    initialEntry?.document_ids ?? initialSelectedIds
  )
  const [prompt, setPrompt] = useState(initialEntry?.prompt ?? "")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<MindmapResponse | null>(initialEntry)
  const [history, setHistory] = useState<MindmapResponse[]>(() =>
    getMindmapHistory()
  )

  const trimmedPrompt = prompt.trim()
  const canSubmit =
    selectedIds.length > 0 &&
    trimmedPrompt.length >= 2 &&
    trimmedPrompt.length <= 2000 &&
    !loading

  function toggleDoc(id: string) {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    )
  }

  async function handleSubmit() {
    if (!canSubmit) return
    setLoading(true)
    try {
      const response = await createMindmapMock({
        document_ids: selectedIds,
        prompt: trimmedPrompt,
      })
      setResult(response)
      if (response.status === "created") {
        setHistory(getMindmapHistory())
      }
    } finally {
      setLoading(false)
    }
  }

  function loadFromHistory(entry: MindmapResponse) {
    setResult(entry)
    setSelectedIds(entry.document_ids)
    setPrompt(entry.prompt)
  }

  const mindmapView =
    result &&
    (result.status === "created" || result.status === "cached") &&
    "nodeData" in result.mindmap
      ? {
          id: result.mindmap_id,
          data: result.mindmap as MindElixirData,
          sources: result.sources,
        }
      : null

  return {
    selectedIds,
    toggleDoc,
    prompt,
    setPrompt,
    loading,
    result,
    history,
    canSubmit,
    handleSubmit,
    loadFromHistory,
    mindmapView,
  }
}
