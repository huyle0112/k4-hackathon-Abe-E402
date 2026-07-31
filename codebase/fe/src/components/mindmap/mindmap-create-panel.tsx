import { useState } from "react"
import type { MindElixirData } from "mind-elixir"
import { AlertTriangle, FileText, History, Info, Loader2, Sparkles } from "lucide-react"

import { MindElixirCanvas } from "@/components/mindmap/mind-elixir-canvas"
import { cn } from "@/lib/utils"
import {
  createMindmap,
  DOCUMENTS,
  getMindmapById,
  getMindmapHistory,
  type MindmapResponse,
} from "@/lib/mindmap-api"

export function MindmapCreatePanel({
  initialMindmapId,
}: {
  initialMindmapId?: string
} = {}) {
  const initialEntry = initialMindmapId
    ? getMindmapById(initialMindmapId)
    : undefined
  const [selectedIds, setSelectedIds] = useState<string[]>(
    initialEntry?.document_ids ?? []
  )
  const [prompt, setPrompt] = useState(initialEntry?.prompt ?? "")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<MindmapResponse | null>(
    initialEntry ?? null
  )
  const [error, setError] = useState<string | null>(null)
  const [history, setHistory] = useState<MindmapResponse[]>(() =>
    getMindmapHistory()
  )

  const trimmedPrompt = prompt.trim()
  const canSubmit =
    selectedIds.length > 0 &&
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
    setError(null)
    try {
      const response = await createMindmap({
        document_ids: selectedIds,
        prompt: trimmedPrompt,
      })
      setResult(response)
      if (response.status === "created" || response.status === "cached") {
        setHistory(getMindmapHistory())
      }
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Không thể tạo mindmap từ máy chủ."
      )
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

  return (
    <div className="flex h-full min-h-0">
      <div className="flex w-[360px] shrink-0 flex-col gap-5 overflow-y-auto border-r border-line bg-white px-5 py-5">
        <div>
          <h3 className="mb-1 text-[13.5px] font-bold text-ink">
            1. Chọn tài liệu
          </h3>
          <p className="mb-3 text-[12px] text-ink-soft">
            Chọn một hoặc nhiều buổi học làm ngữ cảnh cho mindmap.
          </p>
          <div className="flex flex-col gap-2">
            {DOCUMENTS.map((doc) => (
              <label
                key={doc.id}
                className={cn(
                  "flex cursor-pointer items-start gap-2.5 rounded-[10px] border px-3 py-2.5 transition-colors",
                  selectedIds.includes(doc.id)
                    ? "border-navy bg-[#EAF0F8]"
                    : "border-line hover:border-navy/40"
                )}
              >
                <input
                  type="checkbox"
                  className="mt-0.5"
                  checked={selectedIds.includes(doc.id)}
                  onChange={() => toggleDoc(doc.id)}
                />
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-[13px] font-semibold text-ink">
                    Day{String(doc.day).padStart(2, "0")} · {doc.title}
                  </span>
                  <span className="font-mono text-[10.5px] text-ink-soft">
                    {doc.fileName}
                  </span>
                </span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <h3 className="mb-1 text-[13.5px] font-bold text-ink">
            2. Nhập prompt (tùy chọn)
          </h3>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Để trống để tạo mindmap tổng quan cho toàn bộ tài liệu đã chọn."
            rows={4}
            className="w-full resize-none rounded-[10px] border border-line px-3 py-2.5 text-[13px] text-ink outline-none focus:border-navy"
          />
        </div>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={!canSubmit}
          className="flex items-center justify-center gap-2 rounded-[9px] bg-navy px-4 py-2.5 text-[13.5px] font-bold text-white transition-colors hover:bg-navy/90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? (
            <Loader2 className="size-4 animate-spin" />
          ) : (
            <Sparkles className="size-4" />
          )}
          {loading ? "Đang tạo mindmap…" : "Tạo mindmap"}
        </button>

        {error && (
          <p className="rounded-[9px] border border-maroon/25 bg-maroon/5 px-3 py-2.5 text-[12px] text-maroon">
            {error}
          </p>
        )}

        {history.length > 0 && (
          <div>
            <h3 className="mb-2 flex items-center gap-1.5 text-[12.5px] font-bold text-ink-soft">
              <History className="size-3.5" />
              Mindmap gần đây
            </h3>
            <div className="flex flex-col gap-1.5">
              {history.map((entry) => (
                <button
                  key={entry.mindmap_id}
                  type="button"
                  onClick={() => loadFromHistory(entry)}
                  className="truncate rounded-[8px] border border-line px-3 py-2 text-left text-[12px] text-ink-soft transition-colors hover:border-navy/40 hover:text-ink"
                >
                  {entry.title}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="relative min-h-0 min-w-0 flex-1 bg-[#F4F3EF]">
        {!result && (
          <div className="flex h-full items-center justify-center px-8 text-center text-[13.5px] text-ink-soft">
            Chọn tài liệu và nhập prompt để tạo mindmap.
          </div>
        )}

        {result?.status === "clarification_required" && (
          <div className="flex h-full items-center justify-center px-8">
            <div className="max-w-md rounded-2xl border border-line bg-white px-5 py-4 text-center shadow-[0_10px_24px_-20px_rgba(28,43,74,0.3)]">
              <Info className="mx-auto mb-2.5 size-5 text-navy" />
              <p className="text-[13.5px] font-semibold text-ink">
                {result.clarification_question}
              </p>
              <p className="mt-1.5 text-[12px] text-ink-soft">
                Hãy bổ sung prompt rồi bấm "Tạo mindmap" lại.
              </p>
            </div>
          </div>
        )}

        {result?.status === "no_context" && (
          <div className="flex h-full items-center justify-center px-8">
            <div className="max-w-md rounded-2xl border border-line bg-white px-5 py-4 text-center shadow-[0_10px_24px_-20px_rgba(28,43,74,0.3)]">
              <AlertTriangle className="mx-auto mb-2.5 size-5 text-maroon" />
              <p className="text-[13.5px] text-ink">{result.message}</p>
            </div>
          </div>
        )}

        {mindmapView && (
          <>
            <MindElixirCanvas
              key={mindmapView.id ?? "mindmap"}
              data={mindmapView.data}
            />
            {mindmapView.sources.length > 0 && (
              <div className="pointer-events-none absolute inset-x-0 bottom-0 z-10 flex justify-center pb-5">
                <div className="pointer-events-auto flex max-w-2xl flex-wrap items-center gap-2 rounded-2xl border border-line bg-white/95 px-4 py-3 shadow-[0_10px_26px_-10px_rgba(0,0,0,0.3)] backdrop-blur">
                  <span className="font-mono text-[10.5px] font-semibold tracking-[0.08em] text-ink-soft uppercase">
                    Nguồn
                  </span>
                  {mindmapView.sources.map((source) => (
                    <span
                      key={source.source_id}
                      title={source.excerpt}
                      className="flex items-center gap-1.5 rounded-full border border-line bg-paper px-2.5 py-1 text-[11px] text-ink-soft"
                    >
                      <FileText className="size-3 text-navy" />
                      {source.file_name} · Trang {source.page}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
