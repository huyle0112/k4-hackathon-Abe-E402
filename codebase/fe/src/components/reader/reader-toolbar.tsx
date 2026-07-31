import { Link } from "react-router-dom"
import { Minus, Plus, Workflow } from "lucide-react"

export function ReaderToolbar({
  currentPage,
  numPages,
  zoom,
  onZoomIn,
  onZoomOut,
  onZoomReset,
  mindmapHref,
}: {
  currentPage: number
  numPages: number | null
  zoom: number
  onZoomIn: () => void
  onZoomOut: () => void
  onZoomReset: () => void
  mindmapHref: string
}) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-line bg-white px-6 py-3">
      <span className="rounded-full border border-line bg-paper px-3.5 py-1.5 font-mono text-[12.5px] font-semibold text-ink">
        Trang {currentPage} / {numPages ?? "…"}
      </span>

      <div className="flex items-center gap-2">
        <Link
          to={mindmapHref}
          className="flex items-center gap-1.5 rounded-[8px] border border-line px-3 py-1.5 text-[12.5px] font-semibold text-ink-soft transition-colors hover:text-ink"
        >
          <Workflow className="size-3.5" />
          Sơ đồ tư duy
        </Link>

        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={onZoomOut}
            aria-label="Thu nhỏ"
            className="flex size-8 items-center justify-center rounded-[8px] border border-line text-ink-soft transition-colors hover:text-ink"
          >
            <Minus className="size-3.5" />
          </button>
          <button
            type="button"
            onClick={onZoomReset}
            className="w-14 rounded-[8px] border border-line py-1.5 text-center text-[12.5px] font-semibold text-ink-soft transition-colors hover:text-ink"
          >
            {Math.round(zoom * 100)}%
          </button>
          <button
            type="button"
            onClick={onZoomIn}
            aria-label="Phóng to"
            className="flex size-8 items-center justify-center rounded-[8px] border border-line text-ink-soft transition-colors hover:text-ink"
          >
            <Plus className="size-3.5" />
          </button>
        </div>
      </div>
    </div>
  )
}
