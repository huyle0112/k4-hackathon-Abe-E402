import { useState } from "react"
import { Link } from "react-router-dom"
import { AlertTriangle, ArrowUpRight, Info, Loader2, Sparkles } from "lucide-react"

import { cn } from "@/lib/utils"
import {
  createMindmap,
  DOCUMENTS,
  findDocumentBySlideFileId,
  type MindmapResponse,
} from "@/lib/mindmap-api"

export function MindmapQuickCreatePanel({
  courseCode,
  slideFileId,
}: {
  courseCode: string
  slideFileId: string
}) {
  const currentDoc = findDocumentBySlideFileId(slideFileId)
  const [selectedIds, setSelectedIds] = useState<string[]>(
    currentDoc ? [currentDoc.id] : []
  )
  const [prompt, setPrompt] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<MindmapResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const trimmedPrompt = prompt.trim()
  const canSubmit =
    selectedIds.length > 0 && trimmedPrompt.length <= 2000 && !loading

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

  const mindmapDetailHref =
    result?.status === "created" || result?.status === "cached"
      ? `/courses/${courseCode}/mindmap?slide=${slideFileId}${
          result.mindmap_id ? `&mindmap=${result.mindmap_id}` : ""
        }`
      : `/courses/${courseCode}/mindmap?slide=${slideFileId}`

  return (
    <div className="flex flex-1 flex-col gap-5 overflow-y-auto px-4 py-4">
      <div>
        <h3 className="mb-1 text-[13px] font-bold text-ink">
          1. Chọn tài liệu
        </h3>
        <p className="mb-3 text-[11.5px] text-ink-soft">
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
                <span className="block truncate text-[12.5px] font-semibold text-ink">
                  Day{String(doc.day).padStart(2, "0")} · {doc.title}
                </span>
                <span className="font-mono text-[10px] text-ink-soft">
                  {doc.fileName}
                </span>
              </span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <h3 className="mb-1 text-[13px] font-bold text-ink">
          2. Nhập prompt (tùy chọn)
        </h3>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Để trống để tạo mindmap tổng quan cho tài liệu đã chọn."
          rows={4}
          className="w-full resize-none rounded-[10px] border border-line px-3 py-2.5 text-[12.5px] text-ink outline-none focus:border-navy"
        />
      </div>

      <button
        type="button"
        onClick={handleSubmit}
        disabled={!canSubmit}
        className="flex items-center justify-center gap-2 rounded-[9px] bg-navy px-4 py-2.5 text-[13px] font-bold text-white transition-colors hover:bg-navy/90 disabled:cursor-not-allowed disabled:opacity-40"
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

      {(result?.status === "created" || result?.status === "cached") && (
        <div className="rounded-[10px] border border-ok/30 bg-ok/5 px-3.5 py-3">
          <p className="text-[12.5px] font-semibold text-ink">
            {result.title ?? "Mindmap đã sẵn sàng"}
          </p>
          <p className="mt-0.5 text-[11.5px] text-ink-soft">
            {result.status === "cached"
              ? "Đã tìm thấy mindmap phù hợp có sẵn."
              : "Mindmap mới đã được tạo thành công."}
          </p>
          <Link
            to={mindmapDetailHref}
            className="mt-2.5 inline-flex items-center gap-1.5 rounded-[8px] border border-navy bg-white px-3 py-1.5 text-[12px] font-semibold text-navy transition-colors hover:bg-[#EAF0F8]"
          >
            Xem mindmap chi tiết
            <ArrowUpRight className="size-3.5" />
          </Link>
        </div>
      )}

      {result?.status === "clarification_required" && (
        <div className="rounded-[10px] border border-line bg-white px-3.5 py-3">
          <div className="flex items-start gap-2">
            <Info className="mt-0.5 size-4 shrink-0 text-navy" />
            <div>
              <p className="text-[12.5px] font-semibold text-ink">
                {result.clarification_question}
              </p>
              <p className="mt-1 text-[11.5px] text-ink-soft">
                Hãy bổ sung prompt rồi bấm "Tạo mindmap" lại.
              </p>
            </div>
          </div>
        </div>
      )}

      {result?.status === "no_context" && (
        <div className="rounded-[10px] border border-maroon/25 bg-maroon/5 px-3.5 py-3">
          <div className="flex items-start gap-2">
            <AlertTriangle className="mt-0.5 size-4 shrink-0 text-maroon" />
            <p className="text-[12.5px] text-ink">{result.message}</p>
          </div>
        </div>
      )}
    </div>
  )
}
