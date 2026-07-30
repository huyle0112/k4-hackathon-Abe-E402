import { Compass, ShieldCheck, Target } from "lucide-react"

import { Section } from "@/components/welcome/section"
import { SectionHead } from "@/components/welcome/section-head"

const FEATURES = [
  {
    icon: Target,
    title: "Biết đúng chỗ còn yếu",
    description:
      "VLearn neo câu hỏi, bài luyện và tiến độ vào knowledge component thay vì đưa ra một điểm số chung chung.",
  },
  {
    icon: Compass,
    title: "Hướng dẫn vừa đủ",
    description:
      "Người mới được giải thích rõ; người đang tiến bộ được gợi mở; khi bế tắc, tutor chuyển sang hỗ trợ trực tiếp.",
  },
  {
    icon: ShieldCheck,
    title: "Dữ liệu học tập có trách nhiệm",
    description:
      "Tín hiệu học tập được dùng có giới hạn, có consent và không biến một hành vi đơn lẻ thành kết luận về sinh viên.",
  },
]

export function FeaturesSection() {
  return (
    <Section id="features">
      <SectionHead
        eyebrow="Tính năng cốt lõi"
        title="Thiết kế cho tiến bộ thật, không phô diễn AI."
      />
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {FEATURES.map((feature) => (
          <div key={feature.title}>
            <div className="mb-4 flex size-[38px] items-center justify-center rounded-[9px] bg-navy text-white">
              <feature.icon size={18} strokeWidth={2} />
            </div>
            <h3 className="mb-2 font-display text-[19px] font-medium">
              {feature.title}
            </h3>
            <p className="text-[14.5px] leading-[1.6] text-ink-soft">
              {feature.description}
            </p>
          </div>
        ))}
      </div>
    </Section>
  )
}
