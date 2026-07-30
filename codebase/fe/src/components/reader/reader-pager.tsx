import { ChevronLeft, ChevronRight } from "lucide-react"

export function ReaderPager({
  currentPage,
  numPages,
  onNavigate,
}: {
  currentPage: number
  numPages: number
  onNavigate: (page: number) => void
}) {
  if (numPages <= 0) return null

  return (
    <div className="pointer-events-none absolute inset-x-0 bottom-5 flex justify-center">
      <div className="pointer-events-auto flex items-center gap-3 rounded-full border border-line bg-white/95 px-2 py-1.5 shadow-[0_10px_26px_-10px_rgba(0,0,0,0.3)] backdrop-blur">
        <button
          type="button"
          disabled={currentPage <= 1}
          onClick={() => onNavigate(Math.max(1, currentPage - 1))}
          aria-label="Trang trước"
          className="flex size-8 items-center justify-center rounded-full text-ink-soft transition-colors hover:text-ink disabled:opacity-30"
        >
          <ChevronLeft className="size-4" />
        </button>
        <span className="font-mono text-[12.5px] font-semibold text-ink">
          Trang {currentPage} / {numPages}
        </span>
        <button
          type="button"
          disabled={currentPage >= numPages}
          onClick={() => onNavigate(Math.min(numPages, currentPage + 1))}
          aria-label="Trang sau"
          className="flex size-8 items-center justify-center rounded-full text-ink-soft transition-colors hover:text-ink disabled:opacity-30"
        >
          <ChevronRight className="size-4" />
        </button>
      </div>
    </div>
  )
}
