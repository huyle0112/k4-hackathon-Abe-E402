import { BookOpen } from "lucide-react"

import { ReaderSidebarDaySection } from "@/components/reader/reader-sidebar-day-section"
import type { Course } from "@/data/comp2010-slides"

export function ReaderSidebar({
  course,
  courseCode,
  activeFileId,
  activeDay,
  pageCounts,
}: {
  course: Course
  courseCode: string
  activeFileId: string
  activeDay: number
  pageCounts: Record<string, number | undefined>
}) {
  return (
    <aside className="flex w-[300px] shrink-0 flex-col overflow-y-auto border-r border-line bg-white">
      <div className="flex items-center gap-2.5 border-b border-line px-4 py-4">
        <div className="flex size-8 items-center justify-center rounded-[8px] bg-[#EAF0F8] text-navy">
          <BookOpen className="size-4" />
        </div>
        <div>
          <h2 className="text-[13.5px] font-bold text-ink">
            Học liệu môn học
          </h2>
          <p className="text-[11.5px] text-ink-soft">
            Chương, slide và tài liệu đã upload
          </p>
        </div>
      </div>

      <div className="flex flex-1 flex-col">
        {course.days.map((day) => (
          <ReaderSidebarDaySection
            key={day.day}
            day={day}
            courseCode={courseCode}
            activeFileId={activeFileId}
            pageCounts={pageCounts}
            defaultOpen={day.day === activeDay}
          />
        ))}
      </div>
    </aside>
  )
}
