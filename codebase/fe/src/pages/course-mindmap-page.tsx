import { useState } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import { FileText, LayoutGrid, Sparkles } from "lucide-react"

import { MindElixirCanvas } from "@/components/mindmap/mind-elixir-canvas"
import { MindmapCreatePanel } from "@/components/mindmap/mindmap-create-panel"
import { MindmapSidebar } from "@/components/mindmap/mindmap-sidebar"
import { ReaderTopbar } from "@/components/reader/reader-topbar"
import { cn } from "@/lib/utils"
import { COURSES, findSlideFile } from "@/data/comp2010-slides"
import { MINDMAPS } from "@/data/mindmap-data"

export function CourseMindmapPage() {
  const { courseCode = "" } = useParams()
  const [searchParams] = useSearchParams()
  const slideId = searchParams.get("slide") ?? ""
  const [view, setView] = useState<"slide" | "create">("slide")
  const [lastSlideId, setLastSlideId] = useState(slideId)
  if (slideId !== lastSlideId) {
    setLastSlideId(slideId)
    setView("slide")
  }

  const course = COURSES[courseCode.toLowerCase()]
  const file = course ? findSlideFile(course, slideId) : undefined

  if (!course || !file) {
    return (
      <div className="flex min-h-svh flex-col items-center justify-center gap-3 bg-paper text-center text-ink-soft">
        <p>Không tìm thấy tài liệu này.</p>
        <Link to={`/courses/${courseCode}`} className="font-semibold text-maroon">
          Quay lại khóa học
        </Link>
      </div>
    )
  }

  const mindmapData = MINDMAPS[file.id]

  return (
    <div className="flex h-svh flex-col bg-paper font-sans text-ink antialiased">
      <ReaderTopbar
        courseCode={courseCode}
        fileTitle={`Sơ đồ tư duy · ${file.fileName}`}
        subtitle={`${course.code} · Day${String(file.day).padStart(2, "0")}`}
      />

      <div className="flex min-h-0 flex-1">
        <MindmapSidebar
          course={course}
          courseCode={courseCode}
          activeFileId={file.id}
          activeDay={file.day}
        />

        <div className="flex min-h-0 min-w-0 flex-1 flex-col">
          <div className="flex items-center gap-2 border-b border-line bg-white px-6 py-3">
            <button
              type="button"
              onClick={() => setView("slide")}
              className={cn(
                "flex items-center gap-1.5 rounded-[8px] border px-3 py-1.5 text-[12.5px] font-semibold transition-colors",
                view === "slide"
                  ? "border-navy bg-[#EAF0F8] text-navy"
                  : "border-line text-ink-soft hover:text-ink"
              )}
            >
              <LayoutGrid className="size-3.5" />
              Xem theo slide
            </button>
            <button
              type="button"
              onClick={() => setView("create")}
              className={cn(
                "flex items-center gap-1.5 rounded-[8px] border px-3 py-1.5 text-[12.5px] font-semibold transition-colors",
                view === "create"
                  ? "border-navy bg-[#EAF0F8] text-navy"
                  : "border-line text-ink-soft hover:text-ink"
              )}
            >
              <Sparkles className="size-3.5" />
              Tạo mindmap tuỳ chỉnh
            </button>

            {view === "slide" && (
              <Link
                to={`/courses/${courseCode}/reader?slide=${file.id}`}
                className="ml-auto flex items-center gap-1.5 rounded-[8px] border border-line px-3 py-1.5 text-[12.5px] font-semibold text-ink-soft transition-colors hover:text-ink"
              >
                <FileText className="size-3.5" />
                Xem tài liệu PDF
              </Link>
            )}
          </div>

          <div className="relative min-h-0 flex-1 bg-[#F4F3EF]">
            {view === "slide" ? (
              mindmapData ? (
                <MindElixirCanvas key={file.id} data={mindmapData} />
              ) : (
                <div className="flex h-full items-center justify-center text-[13.5px] text-ink-soft">
                  Chưa có sơ đồ tư duy cho tài liệu này.
                </div>
              )
            ) : (
              <MindmapCreatePanel />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CourseMindmapPage
