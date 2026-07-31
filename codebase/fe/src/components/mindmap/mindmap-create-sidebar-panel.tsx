import { useState } from "react"
import { Link } from "react-router-dom"
import type { MindElixirData } from "mind-elixir"
import { AlertTriangle, ExternalLink, History, Info, Loader2, Sparkles } from "lucide-react"

import { MindElixirCanvas } from "@/components/mindmap/mind-elixir-canvas"
import { cn } from "@/lib/utils"
import {
  createMindmap,
  DOCUMENTS,
  getMindmapHistory,
  type MindmapResponse,
} from "@/lib/mindmap-api"

export function MindmapCreateSidebarPanel({
  courseCode,
  slideFileId,
}: {
  courseCode: string
  slideFileId: string
}) {
  const currentDocId = DOCUMENTS.find((d) => d.slideFileId === slideFileId)?.id
  const [selectedIds, setSelectedIds] = useState<string[]>(
    currentDocId ? [currentDocId] : []
  )
  const [prompt, setPrompt] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<MindmapResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [history, setHistory] = useState<MindmapResponse[]>(() =>
    getMindmapHistory()
  )

  const trimmedPrompt = prompt.trim()
  const canSubmit = selectedIds.length > 0 && trimmedPrompt.length <= 2000 && !loading

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
        cause instanceof Error ? cause.message : "Không thể tạo mindmap từ máy chủ."
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
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto px-4 py-4">
      <div>
        <h3 className="mb-1 text-[12.5px] font-bold text-ink">1. Chọn tài liệu</h3>
        <p className="mb-2.5 text-[11.5px] text-ink-soft">
          Chọn một hoặc nhiều buổi học làm ngữ cảnh cho mindmap.
        </p>
        <div className="flex flex-col gap-1.5">
          {DOCUMENTS.map((doc) => (
            <label
              key={doc.id}
              className={cn(
                "flex cursor-pointer items-start gap-2 rounded-[9px] border px-2.5 py-2 transition-colors",
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
                <span className="block truncate text-[12.5px] font-semibold text-ink">
                  Day{String(doc.day).padStart(2, "0")} · {doc.title}
                </span>
                <span className="font-mono text-[10px] text-ink-soft">{doc.fileName}</span>
              </span>
            </label>
          ))}
        </div>
      </div>

      <div className="mt-4">
        <h3 className="mb-1 text-[12.5px] font-bold text-ink">2. Nhập prompt (tùy chọn)</h3>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Để trống để tạo mindmap tổng quan cho tài liệu đã chọn."
          rows={3}
          className="w-full resize-none rounded-[9px] border border-line px-2.5 py-2 text-[12.5px] text-ink outline-none focus:border-navy"
        />
      </div>

      <button
        type="button"
        onClick={handleSubmit}
        disabled={!canSubmit}
        className="mt-3 flex items-center justify-center gap-2 rounded-[9px] bg-navy px-4 py-2.5 text-[13px] font-bold text-white transition-colors hover:bg-navy/90 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {loading ? <Loader2 className="size-4 animate-spin" /> : <Sparkles className="size-4" />}
        {loading ? "Đang tạo mindmap…" : "Tạo mindmap"}
      </button>

      {error && (
        <p className="mt-3 rounded-[9px] border border-maroon/25 bg-maroon/5 px-2.5 py-2 text-[11.5px] text-maroon">
          {error}
        </p>
      )}

      {result?.status === "clarification_required" && (
        <div className="mt-3 rounded-[9px] border border-line bg-white px-2.5 py-2.5 text-center">
          <Info className="mx-auto mb-1.5 size-4 text-navy" />
          <p className="text-[12.5px] font-semibold text-ink">
            {result.clarification_question}
          </p>
          <p className="mt-1 text-[11px] text-ink-soft">
            Hãy bổ sung prompt rồi bấm "Tạo mindmap" lại.
          </p>
        </div>
      )}

      {result?.status === "no_context" && (
        <div className="mt-3 rounded-[9px] border border-line bg-white px-2.5 py-2.5 text-center">
          <AlertTriangle className="mx-auto mb-1.5 size-4 text-maroon" />
          <p className="text-[12.5px] text-ink">{result.message}</p>
        </div>
      )}

      {mindmapView && (
        <div className="mt-3 flex flex-col gap-2">
          <div className="h-72 overflow-hidden rounded-[10px] border border-line bg-[#F4F3EF]">
            <MindElixirCanvas key={mindmapView.id ?? "mindmap"} data={mindmapView.data} />
          </div>

          <Link
            to={`/courses/${courseCode}/mindmap?slide=${slideFileId}`}
            className="flex items-center justify-center gap-1.5 rounded-[9px] border border-line px-3 py-2 text-[12px] font-semibold text-ink-soft transition-colors hover:text-ink"
          >
            <ExternalLink className="size-3.5" />
            Mở toàn màn hình
          </Link>

          {mindmapView.sources.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {mindmapView.sources.map((source) => (
                <span
                  key={source.source_id}
                  title={source.excerpt}
                  className="rounded-full border border-line bg-white px-2 py-1 text-[10.5px] text-ink-soft"
                >
                  {source.file_name} · Trang {source.page}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {history.length > 0 && (
        <div className="mt-4">
          <h3 className="mb-1.5 flex items-center gap-1.5 text-[11.5px] font-bold text-ink-soft">
            <History className="size-3.5" />
            Mindmap gần đây
          </h3>
          <div className="flex flex-col gap-1.5">
            {history.map((entry) => (
              <button
                key={entry.mindmap_id}
                type="button"
                onClick={() => loadFromHistory(entry)}
                className="truncate rounded-[8px] border border-line px-2.5 py-1.5 text-left text-[11.5px] text-ink-soft transition-colors hover:border-navy/40 hover:text-ink"
              >
                {entry.title}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
