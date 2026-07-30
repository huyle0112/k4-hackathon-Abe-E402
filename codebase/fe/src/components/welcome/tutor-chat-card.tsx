import { cn } from "@/lib/utils"

const MESSAGES = [
  {
    from: "student",
    text: "Em chưa hiểu vì sao learning rate quá lớn lại làm mô hình khó hội tụ.",
  },
  {
    from: "tutor",
    text: "Nếu mỗi bước cập nhật vượt qua điểm tối ưu, em nghĩ loss sẽ thay đổi như thế nào?",
  },
  {
    from: "student",
    text: "Loss có thể dao động thay vì giảm dần?",
  },
  {
    from: "tutor",
    text: "Đúng rồi. Hãy thử liên hệ điều đó với độ dài của vector gradient nhé.",
  },
] as const

function Avatar({ from }: { from: "student" | "tutor" }) {
  return (
    <div
      className={cn(
        "flex size-[26px] shrink-0 items-center justify-center rounded-full font-display text-[13px] font-semibold",
        from === "tutor" ? "bg-navy text-white" : "bg-[#EDEAE2] text-ink-soft"
      )}
    >
      {from === "tutor" ? "V" : "SV"}
    </div>
  )
}

export function TutorChatCard() {
  return (
    <div className="overflow-hidden rounded-[14px] border border-line bg-white shadow-[0_20px_44px_-20px_rgba(23,26,31,0.18)]">
      <div className="flex items-center justify-between border-b border-line bg-[#FCFBF8] px-[18px] py-3.5">
        <span className="flex items-center gap-[9px] font-mono text-xs tracking-[0.06em] text-ink-soft uppercase">
          <span className="size-[7px] rounded-full bg-ok shadow-[0_0_0_3px_rgba(47,111,82,0.18)]" />
          VLearn Tutor
        </span>
        <span className="rounded-full bg-maroon-soft px-2 py-[3px] font-mono text-[11px] tracking-[0.04em] text-maroon">
          Thích ứng
        </span>
      </div>

      <div className="flex flex-col gap-3.5 px-[18px] pt-5 pb-4">
        {MESSAGES.map((msg, i) => (
          <div
            key={i}
            className={cn(
              "flex max-w-[92%] gap-2.5",
              msg.from === "student" && "max-w-[80%] flex-row-reverse self-end"
            )}
          >
            <Avatar from={msg.from} />
            <div
              className={cn(
                "rounded-xl px-3.5 py-[11px] text-[14.5px] leading-normal",
                msg.from === "tutor"
                  ? "rounded-tl-[4px] bg-[#F1F0EC]"
                  : "rounded-tr-[4px] bg-navy text-white"
              )}
            >
              {msg.text}
            </div>
          </div>
        ))}

        <div
          className="flex w-fit gap-1 rounded-xl rounded-tl-[4px] bg-[#F1F0EC] px-3.5 py-3"
          aria-hidden="true"
        >
          {[0, 0.2, 0.4].map((delay) => (
            <span
              key={delay}
              className="size-1.5 animate-blink rounded-full bg-ink-soft opacity-50 motion-reduce:animate-none motion-reduce:opacity-60"
              style={{ animationDelay: `${delay}s` }}
            />
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2 border-t border-line px-[18px] py-3 text-[13.5px] text-ink-soft before:content-['↳'] before:text-line">
        Tiếp tục hỏi…
      </div>
    </div>
  )
}
