import { Link, useParams, useSearchParams } from "react-router-dom"
import { FileText } from "lucide-react"

import { MindElixirCanvas } from "@/components/mindmap/mind-elixir-canvas"
import { MindmapSidebar } from "@/components/mindmap/mindmap-sidebar"
import { ReaderTopbar } from "@/components/reader/reader-topbar"
import { COURSES, findSlideFile } from "@/data/comp2010-slides"
import { MINDMAPS } from "@/data/mindmap-data"

export function CourseMindmapPage() {
  const { courseCode = "" } = useParams()
  const [searchParams] = useSearchParams()
  const slideId = searchParams.get("slide") ?? ""

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

        <div className="relative min-h-0 min-w-0 flex-1 bg-[#F4F3EF]">
          {mindmapData ? (
            <MindElixirCanvas key={file.id} data={mindmapData} />
          ) : (
            <div className="flex h-full items-center justify-center text-[13.5px] text-ink-soft">
              Chưa có sơ đồ tư duy cho tài liệu này.
            </div>
          )}

          <Link
            to={`/courses/${courseCode}/reader?slide=${file.id}`}
            className="absolute top-4 right-4 z-10 flex items-center gap-2 rounded-full border border-line bg-white/95 px-4 py-2 text-[12.5px] font-semibold text-ink-soft shadow-[0_10px_26px_-10px_rgba(0,0,0,0.3)] backdrop-blur transition-colors hover:text-ink"
          >
            <FileText className="size-3.5" />
            Xem tài liệu PDF
          </Link>
        </div>
      </div>
    </div>
  )
}

export default CourseMindmapPage
