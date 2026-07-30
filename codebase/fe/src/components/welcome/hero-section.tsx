import { Link } from "react-router-dom"

import { Eyebrow } from "@/components/welcome/eyebrow"
import { TutorChatCard } from "@/components/welcome/tutor-chat-card"

export function HeroSection() {
  return (
    <section className="relative overflow-hidden pt-19 pb-24">
      <div
        className="pointer-events-none absolute -top-35 -right-40 size-[520px] rounded-full"
        style={{
          background:
            "radial-gradient(circle, rgba(140,36,56,0.10), transparent 70%)",
        }}
        aria-hidden="true"
      />

      <div className="relative mx-auto grid max-w-[1140px] items-center gap-14 px-7 lg:grid-cols-[1.05fr_0.95fr]">
        <div>
          <Eyebrow>Nền tảng học thích ứng · VinUni AI Thực Chiến</Eyebrow>
          <h1 className="mt-4.5 mb-5.5 font-display text-[clamp(34px,4.6vw,54px)] leading-[1.12] font-medium tracking-[-0.01em]">
            Chỗ nào em yếu,{" "}
            <span className="font-semibold text-maroon italic">
              VLearn biết đúng chỗ đó.
            </span>
          </h1>
          <p className="mb-7.5 max-w-[520px] text-[17.5px] leading-[1.65] text-ink-soft">
            Học theo từng ngày, hỏi tutor ngay trên tài liệu và luyện đúng
            knowledge component còn thiếu — thay vì nhận một đáp án nhanh rồi
            bỏ qua cách suy luận.
          </p>
          <div className="mb-4 flex flex-wrap gap-3">
            <Link
              to="/login"
              className="rounded-[9px] bg-maroon px-[18px] py-2.5 text-[14.5px] font-semibold text-white transition-[transform,box-shadow] hover:-translate-y-px hover:shadow-[0_6px_16px_rgba(140,36,56,0.28)]"
            >
              Bắt đầu học
            </Link>
            <a
              href="#daily-loop"
              className="rounded-[9px] border border-line px-[18px] py-2.5 text-[14.5px] font-semibold text-ink transition-colors hover:border-ink-soft"
            >
              Xem cách hoạt động
            </a>
          </div>
          <p className="text-[13px] text-ink-soft">
            Đăng nhập bằng tài khoản VinUni AI Thực Chiến được cấp
          </p>
        </div>

        <TutorChatCard />
      </div>
    </section>
  )
}
