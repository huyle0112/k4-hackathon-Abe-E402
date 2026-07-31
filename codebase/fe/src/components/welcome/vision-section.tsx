import { Section } from "@/components/welcome/section"
import { SectionHead } from "@/components/welcome/section-head"

export function VisionSection() {
  return (
    <Section id="vision">
      <SectionHead
        eyebrow="Tầm nhìn sản phẩm"
        title="Không chỉ trả lời. VLearn giúp bạn học."
        description="Một công cụ học tốt không làm thay phần suy nghĩ. Nó giúp người học thấy mình đang hiểu đến đâu, vì sao còn vướng và bước tiếp theo nên là gì."
      />
      <div className="max-w-[640px] rounded-[10px] border border-dashed border-line bg-[#FCFBF8] px-[18px] py-4 text-sm text-ink-soft">
        Placement Assessment đầu khóa là tùy chọn; quiz hằng ngày là bài đánh
        giá sau buổi học. Không có gate cứng ngăn sinh viên đi tiếp.
      </div>
    </Section>
  )
}
