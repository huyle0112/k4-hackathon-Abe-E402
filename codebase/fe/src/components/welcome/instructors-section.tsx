import { Eyebrow } from "@/components/welcome/eyebrow"
import { Section } from "@/components/welcome/section"

export function InstructorsSection() {
  return (
    <Section id="for-instructors">
      <div className="grid items-center gap-14 lg:grid-cols-2">
        <div>
          <Eyebrow>Dành cho giảng viên</Eyebrow>
          <h2 className="mt-3.5 font-display text-[clamp(26px,3.4vw,38px)] leading-[1.22] font-medium tracking-[-0.005em]">
            Một màn hình để biết lớp đang cần gì hôm nay.
          </h2>
          <p className="mt-3.5 mb-7 text-base text-ink-soft">
            Theo dõi ai đã vào học, knowledge component nào đang là điểm
            nghẽn, câu hỏi nào cần trả lời và sinh viên nào cần được hỗ trợ
            thêm — với diễn giải thay vì nhãn kết luận.
          </p>
          <a
            href="#"
            className="inline-block rounded-[9px] bg-maroon px-[18px] py-2.5 text-[14.5px] font-semibold text-white transition-[transform,box-shadow] hover:-translate-y-px hover:shadow-[0_6px_16px_rgba(140,36,56,0.28)]"
          >
            Vào cổng giảng viên
          </a>
        </div>

        <div className="rounded-[14px] bg-navy p-6 text-white shadow-[0_24px_50px_-22px_rgba(28,43,74,0.5)]">
          <div className="mb-4.5 flex items-center justify-between font-mono text-xs text-[#C9D0DE]">
            <span>Hôm nay · Day 10</span>
            <span className="rounded-full bg-white/10 px-2.5 py-[3px]">
              Dữ liệu minh họa
            </span>
          </div>
          <div className="mb-2.5 flex items-end justify-between">
            <span className="font-display text-xl">Gradient descent</span>
            <span className="font-mono text-[11px] text-[#E4B7BF]">
              KC cần giảng lại
            </span>
          </div>
          <div className="mt-1.5 mb-3 font-display text-[44px] leading-none font-semibold">
            68%
          </div>
          <div className="mb-5 h-2 overflow-hidden rounded-full bg-white/14">
            <span
              className="block h-full w-[68%] rounded-full"
              style={{
                background: "linear-gradient(90deg, #C9A25B, #B08D3E)",
              }}
            />
          </div>
          <div className="flex flex-wrap gap-4.5 border-t border-white/12 pt-4 text-xs text-[#C9D0DE]">
            <div>
              <b className="block font-display text-base font-medium text-white">
                12
              </b>
              sinh viên cần chú ý
            </div>
            <div>
              <b className="block font-display text-base font-medium text-white">
                8
              </b>
              câu hỏi đang chờ
            </div>
            <div>
              <b className="block font-display text-base font-medium text-white">
                3
              </b>
              KC dưới ngưỡng
            </div>
          </div>
        </div>
      </div>
    </Section>
  )
}
