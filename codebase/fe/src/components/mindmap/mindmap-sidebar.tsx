import { Workflow } from "lucide-react"

import { MindmapSidebarDaySection } from "@/components/mindmap/mindmap-sidebar-day-section"
import type { Course } from "@/data/comp2010-slides"

export function MindmapSidebar({
  course,
  courseCode,
  activeFileId,
  activeDay,
}: {
  course: Course
  courseCode: string
  activeFileId: string
  activeDay: number
}) {
  return (
    <aside className="flex w-[300px] shrink-0 flex-col overflow-y-auto border-r border-line bg-white">
      <div className="flex items-center gap-2.5 border-b border-line px-4 py-4">
        <div className="flex size-8 items-center justify-center rounded-[8px] bg-[#EAF0F8] text-navy">
          <Workflow className="size-4" />
        </div>
        <div>
          <h2 className="text-[13.5px] font-bold text-ink">Sơ đồ tư duy</h2>
          <p className="text-[11.5px] text-ink-soft">
            Tổng hợp nội dung theo từng buổi học
          </p>
        </div>
      </div>

      <div className="flex flex-1 flex-col">
        {course.days.map((day) => (
          <MindmapSidebarDaySection
            key={day.day}
            day={day}
            courseCode={courseCode}
            activeFileId={activeFileId}
            defaultOpen={day.day === activeDay}
          />
        ))}
      </div>
    </aside>
  )
}
