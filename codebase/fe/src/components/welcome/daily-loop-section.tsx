import { Section } from "@/components/welcome/section"
import { SectionHead } from "@/components/welcome/section-head"

const LOOP_STEPS = [
  {
    num: "01",
    title: "Học theo ngày",
    description:
      "Slide, ghi chú giảng viên và tài liệu bổ sung nằm trong cùng một không gian học tập.",
  },
  {
    num: "02",
    title: "Tutor thích ứng",
    description:
      "Giải thích, gợi mở hoặc kiểm tra lại tùy mức độ hiểu và trạng thái của người học.",
  },
  {
    num: "03",
    title: "Đánh giá sau buổi",
    description:
      "Một bài quiz ngắn giúp xác định knowledge component nào đã vững hoặc cần luyện thêm.",
  },
  {
    num: "04",
    title: "Mastery rõ ràng",
    description:
      "Tiến độ được cập nhật theo từng đơn vị kiến thức, có lý do và có đường luyện tiếp theo.",
  },
]

export function DailyLoopSection() {
  return (
    <Section id="daily-loop">
      <SectionHead
        eyebrow="Một vòng học có định hướng"
        title="Đo vừa đủ. Dạy đúng lúc. Luyện đúng chỗ."
        description="VLearn bám theo nhịp học thật của sinh viên: trong buổi học, sau buổi học và khi cần ôn lại."
      />
      <div className="grid grid-cols-1 gap-px overflow-hidden rounded-[14px] border border-line bg-line sm:grid-cols-2 lg:grid-cols-4">
        {LOOP_STEPS.map((step) => (
          <div key={step.num} className="bg-white px-6 py-7">
            <span className="font-mono text-xs font-semibold text-maroon">
              {step.num}
            </span>
            <h3 className="mt-3.5 mb-2 font-display text-[19px] font-medium">
              {step.title}
            </h3>
            <p className="text-[14.5px] leading-[1.55] text-ink-soft">
              {step.description}
            </p>
          </div>
        ))}
      </div>
    </Section>
  )
}
