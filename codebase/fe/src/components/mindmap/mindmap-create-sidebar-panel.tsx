import { Link } from "react-router-dom"
import { AlertTriangle, ExternalLink, FileText, History, Info, Loader2, Sparkles } from "lucide-react"

import { MindElixirCanvas } from "@/components/mindmap/mind-elixir-canvas"
import { useMindmapCreate } from "@/hooks/use-mindmap-create"
import { cn } from "@/lib/utils"
import { DOCUMENTS } from "@/lib/mindmap-api"

export function MindmapCreateSidebarPanel({
  courseCode,
  slideFileId,
  initialSelectedIds = [],
}: {
  courseCode: string
  slideFileId: string
  initialSelectedIds?: string[]
}) {
  const {
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
  } = useMindmapCreate(initialSelectedIds)

  return (
    <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-4 py-4">
      <div>
        <h3 className="mb-1.5 text-[12.5px] font-bold text-ink">1. Chọn tài liệu</h3>
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
                <span className="font-mono text-[10px] text-ink-soft">
                  {doc.fileName}
                </span>
              </span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <h3 className="mb-1.5 text-[12.5px] font-bold text-ink">2. Nhập prompt</h3>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="VD: So sánh LLM, workflow và agent; nêu trường hợp sử dụng."
          rows={3}
          className="w-full resize-none rounded-[9px] border border-line px-2.5 py-2 text-[12.5px] text-ink outline-none focus:border-navy"
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

      {history.length > 0 && (
        <div>
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

      {result?.status === "clarification_required" && (
        <div className="rounded-[10px] border border-line bg-white px-3.5 py-3 text-center">
          <Info className="mx-auto mb-2 size-4 text-navy" />
          <p className="text-[12.5px] font-semibold text-ink">
            {result.clarification_question}
          </p>
          <p className="mt-1 text-[11px] text-ink-soft">
            Hãy bổ sung prompt rồi bấm "Tạo mindmap" lại.
          </p>
        </div>
      )}

      {result?.status === "no_context" && (
        <div className="rounded-[10px] border border-line bg-white px-3.5 py-3 text-center">
          <AlertTriangle className="mx-auto mb-2 size-4 text-maroon" />
          <p className="text-[12.5px] text-ink">{result.message}</p>
        </div>
      )}

      {mindmapView && (
        <div className="flex flex-col gap-2">
          <div className="h-[320px] shrink-0 overflow-hidden rounded-[10px] border border-line bg-[#F4F3EF]">
            <MindElixirCanvas key={mindmapView.id ?? "mindmap"} data={mindmapView.data} />
          </div>
          {mindmapView.sources.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {mindmapView.sources.map((source) => (
                <span
                  key={source.source_id}
                  title={source.excerpt}
                  className="flex items-center gap-1 rounded-full border border-line bg-paper px-2 py-1 text-[10.5px] text-ink-soft"
                >
                  <FileText className="size-3 text-navy" />
                  {source.file_name} · Trang {source.page}
                </span>
              ))}
            </div>
          )}
          {mindmapView.id && (
            <Link
              to={`/courses/${courseCode}/mindmap?slide=${slideFileId}&view=create&mindmapId=${mindmapView.id}`}
              className="flex items-center justify-center gap-1.5 rounded-[9px] border border-navy/30 px-3 py-2 text-[12px] font-semibold text-navy transition-colors hover:border-navy/60"
            >
              <ExternalLink className="size-3.5" />
              Xem trang chi tiết
            </Link>
          )}
        </div>
      )}
    </div>
  )
}
