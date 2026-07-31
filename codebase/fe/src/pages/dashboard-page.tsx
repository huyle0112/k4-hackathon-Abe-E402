import { Link } from "react-router-dom"
import { ArrowRight, BookOpen, MessageCircleQuestion } from "lucide-react"

import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { PageHead } from "@/components/dashboard/page-head"
import { SupportFab } from "@/components/dashboard/support-fab"

const DEMO_EMAIL = "demo@vinuni.edu.vn"
const DEMO_NAME = "KIỀU PHÚC HUY"

const STATS = [
  { icon: BookOpen, label: "Khóa học", value: "1" },
  { icon: MessageCircleQuestion, label: "Câu hỏi với tutor", value: "4" },
] as const

export function DashboardPage() {
  return (
    <div className="min-h-svh bg-paper font-sans text-ink antialiased">
      <div className="h-1 bg-gradient-to-r from-navy to-maroon" />
      <DashboardHeader email={DEMO_EMAIL} />

      <main className="mx-auto max-w-[1320px] px-8 py-9 pb-24">
        <PageHead
          title="Không gian học tập VLearn"
          description="Theo dõi tiến độ, học liệu và phần kiến thức cần củng cố tại VinUni AI Thực Chiến."
          pill="1 khóa học đang theo học"
        />

        <section className="relative mb-6 overflow-hidden rounded-2xl bg-navy px-11 py-9 shadow-[0_20px_44px_-22px_rgba(28,43,74,0.45)]">
          <div
            className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-maroon from-[78%] to-transparent to-[78%]"
            aria-hidden="true"
          />
          <div className="relative z-10 max-w-[680px] text-white">
            <span className="mb-3.5 block font-mono text-[11.5px] font-semibold tracking-[0.1em] text-[#F2A8B1] uppercase">
              VLearn · VinUni AI Thực Chiến
            </span>
            <h2 className="mb-3.5 text-[26px] font-bold tracking-[-0.01em]">
              Chào mừng trở lại, {DEMO_NAME}!
            </h2>
            <p className="mb-5 max-w-[600px] text-[15px] leading-[1.65] text-white/85">
              VLearn đang tổng hợp tiến độ đọc và các tín hiệu học tập. Mở
              Khóa học của tôi để tiếp tục ngày học hoặc trao đổi cùng VLearn
              Tutor.
            </p>
            <div className="flex flex-wrap gap-2.5">
              <span className="flex items-center gap-1.5 rounded-full bg-white/12 px-3.5 py-2 text-[13px] font-semibold text-white">
                <span className="size-[7px] rounded-full bg-ok" />
                Tín hiệu học tập đang hoạt động
              </span>
              <span className="rounded-full bg-white px-3.5 py-2 text-[13px] font-semibold text-maroon">
                Đã đọc 0/6 ngày học
              </span>
            </div>
          </div>
        </section>

        <div className="mb-4.5 grid gap-4.5 sm:grid-cols-2">
          {STATS.map((stat) => (
            <div
              key={stat.label}
              className="flex items-center gap-4 rounded-[14px] border border-line bg-white px-6 py-5.5"
            >
              <div className="flex size-[42px] shrink-0 items-center justify-center rounded-[10px] bg-[#EAF0F8] text-navy">
                <stat.icon className="size-[19px]" />
              </div>
              <div>
                <div className="mb-1 font-mono text-[11px] tracking-[0.06em] text-ink-soft uppercase">
                  {stat.label}
                </div>
                <div className="text-[26px] font-bold">{stat.value}</div>
              </div>
            </div>
          ))}
        </div>

        <Link
          to="/courses"
          className="group flex items-center gap-4.5 rounded-[14px] border border-line bg-white px-6 py-5.5 transition-[border-color,box-shadow,transform] hover:-translate-y-px hover:border-navy hover:shadow-[0_14px_30px_-18px_rgba(28,43,74,0.3)]"
        >
          <div className="flex size-[42px] shrink-0 items-center justify-center rounded-[10px] bg-[#EAF0F8] text-navy">
            <BookOpen className="size-[19px]" />
          </div>
          <div className="flex-1">
            <h3 className="mb-0.5 text-[15.5px] font-bold">
              Xem khóa học của tôi
            </h3>
            <p className="text-[13.5px] text-ink-soft">
              Mở danh sách đầy đủ các lớp bạn đang theo học.
            </p>
          </div>
          <div className="flex size-[34px] shrink-0 items-center justify-center rounded-full border border-line text-ink-soft transition-colors group-hover:border-navy group-hover:bg-navy group-hover:text-white">
            <ArrowRight className="size-[15px]" />
          </div>
        </Link>
      </main>

      <SupportFab />
    </div>
  )
}

export default DashboardPage
