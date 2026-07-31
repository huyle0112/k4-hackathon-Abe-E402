import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { CheckCircle2, Loader2 } from "lucide-react"

import { DayCard } from "@/components/courses/day-card"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { SupportFab } from "@/components/dashboard/support-fab"
import { fetchCourse, type Course } from "@/lib/courses-api"

const DEMO_EMAIL = "demo@vinuni.edu.vn"

export function CourseDetailPage() {
  const { courseCode = "" } = useParams()
  const [course, setCourse] = useState<Course | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCourse(courseCode)
      .then(setCourse)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [courseCode])

  if (loading) {
    return (
      <div className="min-h-svh bg-paper font-sans text-ink antialiased">
        <div className="h-1 bg-gradient-to-r from-navy to-maroon" />
        <DashboardHeader email={DEMO_EMAIL} />
        <main className="flex h-64 items-center justify-center">
          <Loader2 className="size-8 animate-spin text-navy" />
        </main>
      </div>
    )
  }

  if (!course) {
    return (
      <div className="min-h-svh bg-paper font-sans text-ink antialiased">
        <div className="h-1 bg-gradient-to-r from-navy to-maroon" />
        <DashboardHeader email={DEMO_EMAIL} />
        <main className="mx-auto max-w-[1320px] px-8 py-16 text-center text-ink-soft">
          Không tìm thấy khóa học này.{" "}
          <Link to="/courses" className="font-semibold text-maroon">
            Quay lại danh sách khóa học
          </Link>
        </main>
      </div>
    )
  }

  const readDays = 0
  const readPercent = Math.round((readDays / course.days.length) * 100) || 0
  const firstFile = course.days.find((d) => d.files.length > 0)?.files[0]

  return (
    <div className="min-h-svh bg-paper font-sans text-ink antialiased">
      <div className="h-1 bg-gradient-to-r from-navy to-maroon" />
      <DashboardHeader email={DEMO_EMAIL} />

      <main className="mx-auto max-w-[1320px] px-8 py-8 pb-24">
        <div className="mb-3.5 flex items-center gap-2 text-[13.5px] text-ink-soft">
          <Link to="/courses" className="hover:text-navy hover:underline">
            Khóa học của tôi
          </Link>
          <span>/</span>
          <span>{course.code}</span>
        </div>

        <div className="mb-7.5 flex flex-wrap items-start justify-between gap-6">
          <div>
            <span className="mb-2 block font-mono text-[11.5px] font-semibold tracking-[0.1em] text-maroon uppercase">
              VLearn · VinUni AI Thực Chiến
            </span>
            <h1 className="mb-2 text-[27px] font-extrabold tracking-[-0.01em]">
              {course.name}
            </h1>
            <p className="text-[14.5px] text-ink-soft">{course.classmates}</p>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-3 rounded-xl border border-line bg-white px-4 py-2.5">
              <CheckCircle2 className="size-[17px] text-ok" />
              <span className="text-[13.5px] font-bold whitespace-nowrap text-ok">
                Đã đọc {readDays}/{course.days.length} ngày
              </span>
              <span className="h-[5px] w-20 overflow-hidden rounded-full bg-[#EEEBE3]">
                <span
                  className="block h-full bg-ok"
                  style={{ width: `${readPercent}%` }}
                />
              </span>
              <span className="text-[12.5px] font-semibold text-ink-soft">
                {readPercent}%
              </span>
            </div>
            {firstFile ? (
              <Link
                to={`/courses/${course.code.toLowerCase()}/reader?slide=${firstFile.id}`}
                className="rounded-[9px] bg-navy px-5 py-3 text-[14px] font-bold whitespace-nowrap text-white transition-[background,transform] hover:-translate-y-px hover:bg-navy/90"
              >
                Bắt đầu đọc
              </Link>
            ) : null}
          </div>
        </div>

        <div className="flex flex-col gap-3.5">
          {course.days.map((d) => (
            <DayCard
              key={d.day}
              day={d.day}
              files={d.files}
              courseCode={course.code.toLowerCase()}
            />
          ))}
        </div>
      </main>

      <SupportFab />
    </div>
  )
}

export default CourseDetailPage
