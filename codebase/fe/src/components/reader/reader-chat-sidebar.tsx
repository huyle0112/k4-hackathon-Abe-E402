import { useEffect, useRef, useState } from "react"
import { Bot, ChevronRight, History, Plus, Send } from "lucide-react"

import { cn } from "@/lib/utils"

type ChatMessage = {
  id: string
  role: "assistant" | "user"
  page: number
  text: string
}

let messageSeq = 0
function nextId() {
  messageSeq += 1
  return `msg-${messageSeq}`
}

function seedMessages(): ChatMessage[] {
  return [
    {
      id: nextId(),
      role: "assistant",
      page: 1,
      text: "Xin chào! Mình là VLearn Tutor. Bạn có thể bôi đen một đoạn trên slide để hỏi, hoặc gửi câu hỏi tự do bên dưới nhé!",
    },
    {
      id: nextId(),
      role: "user",
      page: 1,
      text: "Slide này nói môn học sẽ làm gì vậy ạ?",
    },
    {
      id: nextId(),
      role: "assistant",
      page: 1,
      text: "Đây là buổi giới thiệu hackathon COMP2010 — slide nêu mục tiêu môn học, cách chia nhóm và các mốc nộp bài trong Phase 1. Bạn muốn mình liệt kê chi tiết từng mốc không?",
    },
    {
      id: nextId(),
      role: "user",
      page: 1,
      text: "\"Healthcare Product Value\" trong slide nghĩa là gì?",
    },
    {
      id: nextId(),
      role: "assistant",
      page: 1,
      text: "Đó là phần đề bài yêu cầu nhóm xây dựng sản phẩm tạo ra giá trị thực sự cho lĩnh vực y tế — ví dụ cải thiện trải nghiệm bệnh nhân, hỗ trợ bác sĩ chẩn đoán, hoặc tối ưu vận hành bệnh viện.",
    },
  ]
}

const MOCK_REPLIES: Array<{ keywords: string[]; reply: string }> = [
  {
    keywords: ["healthcare", "y tế", "bệnh nhân"],
    reply:
      "Sản phẩm y tế tốt cần giải quyết một vấn đề thật của người dùng (bệnh nhân, bác sĩ, bệnh viện) và đo lường được giá trị mang lại, không chỉ dừng ở công nghệ.",
  },
  {
    keywords: ["nhóm", "team", "hackathon"],
    reply:
      "Mỗi nhóm hackathon nên phân vai rõ ràng (research, dev, thuyết trình) và bám sát checklist nộp bài theo từng ngày để không bị dồn việc vào cuối kỳ.",
  },
  {
    keywords: ["deadline", "nộp bài", "mốc"],
    reply:
      "Các mốc nộp bài thường nằm ở cuối mỗi ngày học — bạn nên xem lại phần lịch trình ở đầu slide Day tương ứng để nắm chính xác thời hạn.",
  },
]

function mockReply(input: string): string {
  const lower = input.toLowerCase()
  const found = MOCK_REPLIES.find((entry) => entry.keywords.some((k) => lower.includes(k)))
  if (found) return found.reply
  return "AI hiện không thể trả lời câu hỏi này. Vui lòng thử diễn đạt khác hoặc thử lại sau ít phút."
}

export function ReaderChatSidebar({ currentPage }: { currentPage: number }) {
  const [open, setOpen] = useState(true)
  const [messages, setMessages] = useState<ChatMessage[]>(() => seedMessages())
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" })
  }, [messages, isTyping])

  const sendMessage = () => {
    const text = input.trim()
    if (!text) return

    setMessages((prev) => [...prev, { id: nextId(), role: "user", page: currentPage, text }])
    setInput("")
    setIsTyping(true)

    window.setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { id: nextId(), role: "assistant", page: currentPage, text: mockReply(text) },
      ])
      setIsTyping(false)
    }, 900)
  }

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label="Mở VLearn Tutor"
        className="fixed right-6 top-1/2 z-20 flex size-11 -translate-y-1/2 items-center justify-center rounded-full border border-line bg-navy text-white shadow-[0_10px_26px_-8px_rgba(0,0,0,0.35)] transition-transform hover:scale-105"
      >
        <Bot className="size-5" />
      </button>
    )
  }

  return (
    <aside className="relative flex w-[380px] shrink-0 flex-col border-l border-line bg-white">
      <button
        type="button"
        onClick={() => setOpen(false)}
        aria-label="Thu gọn VLearn Tutor"
        className="absolute top-1/2 -left-3.5 z-20 flex size-7 -translate-y-1/2 items-center justify-center rounded-full border border-line bg-white text-ink-soft shadow-[0_6px_16px_-6px_rgba(0,0,0,0.3)] transition-colors hover:text-ink"
      >
        <ChevronRight className="size-3.5" />
      </button>

      <div className="flex items-center gap-2 border-b border-line px-4 py-3.5">
        <div className="flex size-8 shrink-0 items-center justify-center rounded-[8px] bg-navy text-white">
          <Bot className="size-4" />
        </div>
        <div className="min-w-0 flex-1">
          <h2 className="text-[13.5px] font-bold text-ink">VLearn Tutor</h2>
          <p className="flex items-center gap-1.5 text-[11px] text-ink-soft">
            <span className="size-[6px] shrink-0 rounded-full bg-ok" />
            Trợ lý học theo ngữ cảnh
          </p>
        </div>
        <button
          type="button"
          aria-label="Lịch sử hội thoại"
          className="flex size-7 shrink-0 items-center justify-center rounded-[7px] text-ink-soft transition-colors hover:text-ink"
        >
          <History className="size-3.5" />
        </button>
        <button
          type="button"
          onClick={() => setMessages([])}
          aria-label="Cuộc trò chuyện mới"
          className="flex size-7 shrink-0 items-center justify-center rounded-[7px] text-ink-soft transition-colors hover:text-ink"
        >
          <Plus className="size-3.5" />
        </button>
        <span className="shrink-0 rounded-full border border-line bg-paper px-2.5 py-1 font-mono text-[11px] font-semibold text-ink">
          Trang slide: {currentPage}
        </span>
      </div>

      <div ref={scrollRef} className="flex flex-1 flex-col gap-4 overflow-y-auto px-4 py-4">
        {messages.map((msg) => (
          <div key={msg.id} className={cn("flex flex-col gap-1", msg.role === "user" && "items-end")}>
            <span className="font-mono text-[10.5px] tracking-[0.02em] text-ink-soft/70 uppercase">
              Ngữ cảnh: Slide trang {msg.page}
            </span>
            {msg.role === "assistant" ? (
              <p className="max-w-[92%] text-[13.5px] leading-relaxed text-ink">{msg.text}</p>
            ) : (
              <p className="max-w-[85%] rounded-xl rounded-tr-[4px] bg-navy px-3.5 py-2.5 text-[13.5px] leading-relaxed text-white">
                {msg.text}
              </p>
            )}
          </div>
        ))}

        {isTyping && (
          <div className="flex flex-col gap-1">
            <span className="font-mono text-[10.5px] tracking-[0.02em] text-ink-soft/70 uppercase">
              Ngữ cảnh: Slide trang {currentPage}
            </span>
            <div className="flex w-fit gap-1 rounded-xl rounded-tl-[4px] bg-[#F1F0EC] px-3.5 py-3" aria-hidden="true">
              {[0, 0.2, 0.4].map((delay) => (
                <span
                  key={delay}
                  className="size-1.5 animate-blink rounded-full bg-ink-soft opacity-50 motion-reduce:animate-none motion-reduce:opacity-60"
                  style={{ animationDelay: `${delay}s` }}
                />
              ))}
            </div>
          </div>
        )}

        {messages.length === 0 && !isTyping && (
          <p className="mt-6 text-center text-[13px] text-ink-soft">
            Bắt đầu cuộc trò chuyện mới — hãy đặt câu hỏi về slide hiện tại.
          </p>
        )}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault()
          sendMessage()
        }}
        className="flex items-center gap-2 border-t border-line px-3.5 py-3"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Nhập câu hỏi hoặc bôi đen tài liệu..."
          className="flex-1 rounded-full border border-line bg-paper px-4 py-2.5 text-[13.5px] text-ink outline-none placeholder:text-ink-soft focus:border-navy"
        />
        <button
          type="submit"
          disabled={!input.trim()}
          aria-label="Gửi"
          className="flex size-9 shrink-0 items-center justify-center rounded-full bg-navy text-white transition-opacity hover:opacity-90 disabled:opacity-40"
        >
          <Send className="size-4" />
        </button>
      </form>
    </aside>
  )
}
