import { Link } from "react-router-dom"
import { CheckCircle2, FileText } from "lucide-react"

import { cn } from "@/lib/utils"
import type { CourseDay } from "@/data/comp2010-slides"

export function ReaderSidebarDaySection({
  day,
  courseCode,
  activeFileId,
  pageCounts,
  defaultOpen,
}: {
  day: CourseDay
  courseCode: string
  activeFileId: string
  pageCounts: Record<string, number | undefined>
  defaultOpen: boolean
}) {
  const dayLabel = String(day.day).padStart(2, "0")

  return (
    <details className="group border-b border-line" open={defaultOpen}>
      <summary className="flex cursor-pointer list-none items-center justify-between px-4 py-3 [&::-webkit-details-marker]:hidden">
        <span className="text-[13.5px] font-bold text-ink">
          Day{dayLabel}
        </span>
        <span className="font-mono text-[10.5px] text-ink-soft">
          {day.files.length > 0
            ? `${day.files.length} tài liệu`
            : "Chưa có tài liệu"}
        </span>
      </summary>

      {day.files.length > 0 ? (
        <div className="flex flex-col gap-2 px-4 pb-3.5">
          {day.files.map((file) => {
            const active = file.id === activeFileId
            const pageCount = pageCounts[file.id]
            return (
              <Link
                key={file.id}
                to={`/courses/${courseCode}/reader?slide=${file.id}`}
                className={cn(
                  "flex items-center gap-2.5 rounded-[10px] border px-3 py-2.5 transition-colors",
                  active
                    ? "border-navy bg-[#EAF0F8]"
                    : "border-line bg-white hover:border-navy/40"
                )}
              >
                <FileText className="size-4 shrink-0 text-navy" />
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-[13px] font-semibold text-ink">
                    {file.fileName}
                  </span>
                  <span className="font-mono text-[11px] text-ink-soft">
                    {pageCount ? `${pageCount} trang` : "Đang tải…"}
                  </span>
                </span>
                {active && (
                  <CheckCircle2 className="size-4 shrink-0 text-navy" />
                )}
              </Link>
            )
          })}
        </div>
      ) : (
        <p className="px-4 pb-3.5 text-[12.5px] text-ink-soft/70">
          Chưa có tài liệu · sắp cập nhật
        </p>
      )}
    </details>
  )
}
