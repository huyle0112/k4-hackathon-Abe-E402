import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react"
import { Bot, ChevronRight, MessageCircle, Plus, Send, Sparkles, X } from "lucide-react"

import { MindmapCreateSidebarPanel } from "@/components/mindmap/mindmap-create-sidebar-panel"
import {
  findChatDocumentContext,
  sendChatMessage,
  type Source,
} from "@/lib/chat-api"
import { DOCUMENTS } from "@/lib/mindmap-api"
import { cn } from "@/lib/utils"

type ChatMessage = {
  id: string
  role: "assistant" | "user"
  page?: number
  text: string
  sources?: Source[]
  quote?: string
}

type QuotedSelection = {
  text: string
  page: number
}

export type ReaderChatSidebarHandle = {
  askAboutSelection: (text: string, page: number) => void
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
      text: "Xin chào, mình là VLearn Tutor!",
    },
  ]
}

export const ReaderChatSidebar = forwardRef<
  ReaderChatSidebarHandle,
  {
    currentPage: number
    slideFileId: string
    courseCode: string
  }
>(function ReaderChatSidebar({ currentPage, slideFileId, courseCode }, ref) {
  const [open, setOpen] = useState(true)
  const [tab, setTab] = useState<"chat" | "mindmap">("chat")
  const [messages, setMessages] = useState<ChatMessage[]>(() => seedMessages())
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [quotedSelection, setQuotedSelection] = useState<QuotedSelection | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const currentDocId = DOCUMENTS.find((d) => d.slideFileId === slideFileId)?.id

  useImperativeHandle(ref, () => ({
    askAboutSelection: (text, page) => {
      setOpen(true)
      setTab("chat")
      setQuotedSelection({ text, page })
      requestAnimationFrame(() => inputRef.current?.focus())
    },
  }))

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" })
  }, [messages, isTyping])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text) return

    const quote = quotedSelection
    const questionForApi = quote
      ? `Trích dẫn: "${quote.text}"\n\nCâu hỏi: ${text}`
      : text

    setMessages((prev) => [
      ...prev,
      { id: nextId(), role: "user", page: quote?.page ?? currentPage, text, quote: quote?.text },
    ])
    setInput("")
    setQuotedSelection(null)
    setIsTyping(true)

    const context = findChatDocumentContext(slideFileId)
    const response = await sendChatMessageMock(
      { question: questionForApi, slide: currentPage, page: currentPage },
      context ?? { document_id: slideFileId, file_name: slideFileId }
    )

    setMessages((prev) => [
      ...prev,
      {
        id: nextId(),
        role: "assistant",
        page: currentPage,
        text: response.clarification_question ?? response.answer,
        sources: response.sources,
      },
    ])
    setIsTyping(false)
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

      <div className="flex items-center gap-1.5 border-b border-line px-3 py-2">
        <button
          type="button"
          onClick={() => setTab("chat")}
          className={cn(
            "flex items-center gap-1.5 rounded-[7px] px-2.5 py-1.5 text-[12px] font-semibold transition-colors",
            tab === "chat" ? "bg-[#EAF0F8] text-navy" : "text-ink-soft hover:text-ink"
          )}
        >
          <MessageCircle className="size-3.5" />
          Trò chuyện
        </button>
        <button
          type="button"
          onClick={() => setTab("mindmap")}
          className={cn(
            "flex items-center gap-1.5 rounded-[7px] px-2.5 py-1.5 text-[12px] font-semibold transition-colors",
            tab === "mindmap" ? "bg-[#EAF0F8] text-navy" : "text-ink-soft hover:text-ink"
          )}
        >
          <Sparkles className="size-3.5" />
          Tạo mindmap
        </button>
      </div>

      {tab === "mindmap" ? (
        <MindmapCreateSidebarPanel
          key={slideFileId}
          courseCode={courseCode}
          slideFileId={slideFileId}
          initialSelectedIds={currentDocId ? [currentDocId] : []}
        />
      ) : (
        <>
          <div ref={scrollRef} className="flex flex-1 flex-col gap-4 overflow-y-auto px-4 py-4">
            {messages.map((msg) => (
              <div key={msg.id} className={cn("flex flex-col gap-1", msg.role === "user" && "items-end")}>
                <span className="font-mono text-[10.5px] tracking-[0.02em] text-ink-soft/70 uppercase">
                  Ngữ cảnh: Slide trang {msg.page}
                </span>
                {msg.role === "assistant" ? (
                  <div className="max-w-[92%]">
                    <p className="text-[13.5px] leading-relaxed text-ink">{msg.text}</p>
                    {msg.sources && msg.sources.length > 0 && (
                      <ul className="mt-1.5 flex flex-col gap-0.5">
                        {msg.sources.map((source) => (
                          <li
                            key={source.source_id}
                            className="text-[11px] text-ink-soft/80"
                          >
                            Nguồn: {source.file_name} · trang {source.page}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ) : (
                  <div className="flex max-w-[85%] flex-col items-end gap-1">
                    {msg.quote && (
                      <p className="max-w-full truncate rounded-lg border border-navy/20 bg-[#EAF0F8] px-2.5 py-1 text-[11.5px] text-navy/80">
                        &ldquo;{msg.quote}&rdquo;
                      </p>
                    )}
                    <p className="rounded-xl rounded-tr-[4px] bg-navy px-3.5 py-2.5 text-[13.5px] leading-relaxed text-white">
                      {msg.text}
                    </p>
                  </div>
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

          {quotedSelection && (
            <div className="flex items-start gap-2 border-t border-line bg-[#F7F6F2] px-3.5 py-2.5">
              <div className="min-w-0 flex-1">
                <p className="font-mono text-[10.5px] tracking-[0.02em] text-ink-soft/70 uppercase">
                  Trích dẫn · trang {quotedSelection.page}
                </p>
                <p className="mt-0.5 line-clamp-2 text-[12.5px] text-ink-soft">
                  &ldquo;{quotedSelection.text}&rdquo;
                </p>
              </div>
              <button
                type="button"
                onClick={() => setQuotedSelection(null)}
                aria-label="Bỏ trích dẫn"
                className="shrink-0 text-ink-soft transition-colors hover:text-ink"
              >
                <X className="size-3.5" />
              </button>
            </div>
          )}

          <form
            onSubmit={(e) => {
              e.preventDefault()
              sendMessage()
            }}
            className="flex items-center gap-2 border-t border-line px-3.5 py-3"
          >
            <input
              ref={inputRef}
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
        </>
      )}
    </aside>
  )
})
