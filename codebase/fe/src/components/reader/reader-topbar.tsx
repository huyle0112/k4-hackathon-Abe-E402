import { Link } from "react-router-dom"
import { ChevronLeft, FileText } from "lucide-react"

import { LocaleThemeControls } from "@/components/dashboard/locale-theme-controls"
import { BrandMark } from "@/components/welcome/brand-mark"

export function ReaderTopbar({
  courseCode,
  fileTitle,
  subtitle,
}: {
  courseCode: string
  fileTitle: string
  subtitle: string
}) {
  return (
    <header className="flex h-16 shrink-0 items-center gap-4 border-b border-line bg-white px-5">
      <Link
        to={`/courses/${courseCode}`}
        aria-label="Quay lại khóa học"
        className="flex size-9 shrink-0 items-center justify-center rounded-[9px] border border-line text-ink-soft transition-colors hover:text-ink"
      >
        <ChevronLeft className="size-4" />
      </Link>

      <Link to="/dashboard" className="flex shrink-0 items-center gap-2">
        <BrandMark />
        <span className="text-[15px] font-semibold text-ink">
          V<span className="text-maroon">Learn</span>
        </span>
      </Link>

      <div className="ml-1 flex min-w-0 items-center gap-2.5 border-l border-line pl-4">
        <FileText className="size-4 shrink-0 text-navy" />
        <div className="min-w-0">
          <h1 className="truncate text-[14.5px] font-bold text-ink">
            {fileTitle}
          </h1>
          <p className="truncate font-mono text-[11px] text-ink-soft">
            {subtitle}
          </p>
        </div>
      </div>

      <div className="ml-auto flex shrink-0 items-center gap-2.5">
        <LocaleThemeControls />
      </div>
    </header>
  )
}
