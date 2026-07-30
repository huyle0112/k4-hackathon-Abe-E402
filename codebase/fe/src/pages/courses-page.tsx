import { ArrowRight, NotebookPen } from "lucide-react"

import { CourseCard } from "@/components/courses/course-card"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { PageHead } from "@/components/dashboard/page-head"
import { SupportFab } from "@/components/dashboard/support-fab"

const DEMO_EMAIL = "demo@vinuni.edu.vn"

const COURSES = [
  {
    code: "COMP2010",
    name: "Khoá 3 + 4 Phase 1",
    description: "Khóa học Khoá 3 + 4 Phase 1",
    readPercent: 0,
    notebookHref: "#",
    openHref: "/courses/comp2010",
  },
]

export function CoursesPage() {
  return (
    <div className="min-h-svh bg-paper font-sans text-ink antialiased">
      <div className="h-1 bg-gradient-to-r from-navy to-maroon" />
      <DashboardHeader email={DEMO_EMAIL} />

      <main className="mx-auto max-w-[1320px] px-8 py-9 pb-24">
        <PageHead
          title="Khóa học của tôi"
          description="Mỗi khóa học lưu trữ tài liệu, giáo án và phần ghi chú tương tác của riêng bạn."
          pill={`${COURSES.length} khóa học đang theo học`}
        />

        {COURSES.map((course) => (
          <CourseCard key={course.code} {...course} />
        ))}

        <a
          href="#"
          className="group flex max-w-[900px] items-center gap-4.5 rounded-[14px] border border-line bg-white px-6 py-5.5 transition-[border-color,box-shadow,transform] hover:-translate-y-px hover:border-navy hover:shadow-[0_14px_30px_-18px_rgba(28,43,74,0.3)]"
        >
          <div className="flex size-[42px] shrink-0 items-center justify-center rounded-[10px] bg-[#EAF0F8] text-navy">
            <NotebookPen className="size-[19px]" />
          </div>
          <div className="flex-1">
            <h3 className="mb-0.5 text-[15.5px] font-bold">Sổ tay học tập</h3>
            <p className="text-[13.5px] text-ink-soft">
              Ghi chú, flashcard và phần kiến thức cần củng cố của bạn.
            </p>
          </div>
          <div className="flex size-[34px] shrink-0 items-center justify-center rounded-full border border-line text-ink-soft transition-colors group-hover:border-navy group-hover:bg-navy group-hover:text-white">
            <ArrowRight className="size-[15px]" />
          </div>
        </a>
      </main>

      <SupportFab />
    </div>
  )
}

export default CoursesPage
