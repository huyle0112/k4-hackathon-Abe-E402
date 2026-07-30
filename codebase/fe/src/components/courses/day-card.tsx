import { Link } from "react-router-dom"
import { ChevronDown, FileText } from "lucide-react"

import type { SlideFile } from "@/data/comp2010-slides"

export function DayCard({
  day,
  files,
  courseCode,
}: {
  day: number
  files: SlideFile[]
  courseCode: string
}) {
  const dayLabel = String(day).padStart(2, "0")
  const completed = false
  const hasFiles = files.length > 0

  return (
    <details className="group overflow-hidden rounded-2xl border border-line bg-white shadow-[0_10px_24px_-22px_rgba(28,43,74,0.3)]">
      <summary className="flex list-none items-center gap-4.5 px-5.5 py-4.5 [&::-webkit-details-marker]:hidden">
        <div className="flex size-13 shrink-0 flex-col items-center justify-center rounded-full bg-[#F0EFEA] font-mono">
          <span className="text-[8.5px] leading-none tracking-[0.06em] text-ink-soft">
            DAY
          </span>
          <span className="text-[15px] leading-[1.3] font-extrabold">
            {dayLabel}
          </span>
        </div>
        <div className="flex-1 cursor-pointer">
          <h3 className="mb-0.5 text-[15.5px] font-bold">
            Day{dayLabel}
          </h3>
          <p className="text-[13px] text-ink-soft">
            {hasFiles
              ? `${completed ? "Đã hoàn thành ngày học" : "Chưa hoàn thành ngày học"} · ${files.length} slide`
              : "Chưa có tài liệu · sắp cập nhật"}
          </p>
        </div>
        <div className="flex size-7.5 shrink-0 items-center justify-center rounded-full text-ink-soft transition-transform duration-200 group-open:rotate-180">
          <ChevronDown className="size-4" />
        </div>
      </summary>

      <div className="mx-5.5 border-t border-line pt-3.5 pb-5 pl-[70px] text-[13.5px] text-ink-soft">
        {hasFiles ? (
          <ul className="flex flex-col gap-2">
            {files.map((file, i) => (
              <li key={file.id}>
                <Link
                  to={`/courses/${courseCode}/reader?slide=${file.id}`}
                  className="flex items-center gap-2.5 transition-colors hover:text-ink"
                >
                  <FileText className="size-3.5 shrink-0 text-navy" />
                  Slide {i + 1} · {file.label}
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-ink-soft/70">Chưa có tài liệu · sắp cập nhật</p>
        )}
      </div>
    </details>
  )
}
