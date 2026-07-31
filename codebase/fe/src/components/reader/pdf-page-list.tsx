import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react"
import { Sparkles } from "lucide-react"

import { PdfPage } from "@/components/reader/pdf-page"
import type { PDFDocumentProxy } from "@/lib/pdf"

export type PdfPageListHandle = {
  goToPage: (page: number) => void
}

type SelectionPopover = {
  text: string
  page: number
  x: number
  y: number
}

export const PdfPageList = forwardRef<
  PdfPageListHandle,
  {
    document: PDFDocumentProxy | null
    numPages: number | null
    zoom: number
    fileName: string
    onCurrentPageChange: (page: number) => void
    onAskAboutSelection?: (text: string, page: number) => void
  }
>(function PdfPageList(
  { document, numPages, zoom, fileName, onCurrentPageChange, onAskAboutSelection },
  ref
) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const pageElsRef = useRef<Map<number, HTMLDivElement>>(new Map())
  const observerRef = useRef<IntersectionObserver | null>(null)
  const currentPageObserverRef = useRef<IntersectionObserver | null>(null)
  const visibleAreaRef = useRef<Map<number, number>>(new Map())
  const [visiblePages, setVisiblePages] = useState<Set<number>>(
    () => new Set([1])
  )
  const [selectionPopover, setSelectionPopover] = useState<SelectionPopover | null>(null)

  useImperativeHandle(ref, () => ({
    goToPage: (page: number) => {
      const container = scrollRef.current
      const pageElement = pageElsRef.current.get(page)
      if (!container || !pageElement) return

      const containerRect = container.getBoundingClientRect()
      const pageRect = pageElement.getBoundingClientRect()
      const top = container.scrollTop + pageRect.top - containerRect.top

      container.scrollTo({ top, behavior: "smooth" })
    },
  }))

  useEffect(() => {
    setVisiblePages(new Set([1]))
    pageElsRef.current.clear()
    visibleAreaRef.current.clear()
  }, [document])

  useEffect(() => {
    if (!scrollRef.current) return

    observerRef.current = new IntersectionObserver(
      (entries) => {
        setVisiblePages((prev) => {
          let changed = false
          const next = new Set(prev)
          for (const entry of entries) {
            if (!entry.isIntersecting) continue
            const n = Number(
              (entry.target as HTMLElement).dataset.pageNumber
            )
            if (!next.has(n)) {
              next.add(n)
              changed = true
            }
            observerRef.current?.unobserve(entry.target)
          }
          return changed ? next : prev
        })
      },
      { root: scrollRef.current, rootMargin: "800px 0px", threshold: 0 }
    )

    for (const el of pageElsRef.current.values()) {
      observerRef.current.observe(el)
    }

    return () => observerRef.current?.disconnect()
  }, [document])

  useEffect(() => {
    const root = scrollRef.current
    if (!root) return

    currentPageObserverRef.current = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          const page = Number((entry.target as HTMLElement).dataset.pageNumber)
          visibleAreaRef.current.set(
            page,
            entry.isIntersecting ? entry.intersectionRect.height : 0
          )
        }

        let currentPage = 1
        let largestVisibleArea = 0
        for (const [page, visibleArea] of visibleAreaRef.current) {
          if (
            visibleArea > largestVisibleArea ||
            (visibleArea === largestVisibleArea && page < currentPage)
          ) {
            currentPage = page
            largestVisibleArea = visibleArea
          }
        }
        onCurrentPageChange(currentPage)
      },
      {
        root,
        threshold: [0, 0.1, 0.25, 0.5, 0.75, 1],
      }
    )

    for (const el of pageElsRef.current.values()) {
      currentPageObserverRef.current.observe(el)
    }

    return () => {
      currentPageObserverRef.current?.disconnect()
      currentPageObserverRef.current = null
      visibleAreaRef.current.clear()
    }
  }, [document, onCurrentPageChange])

  const registerEl = useCallback(
    (n: number) => (el: HTMLDivElement | null) => {
      if (el) {
        pageElsRef.current.set(n, el)
        observerRef.current?.observe(el)
        currentPageObserverRef.current?.observe(el)
      } else {
        pageElsRef.current.delete(n)
        visibleAreaRef.current.delete(n)
      }
    },
    []
  )

  useEffect(() => {
    const container = scrollRef.current
    if (!container) return

    const handleSelectionChange = () => {
      const selection = window.getSelection()
      if (!selection || selection.isCollapsed || selection.rangeCount === 0) {
        setSelectionPopover(null)
        return
      }

      const range = selection.getRangeAt(0)
      if (!container.contains(range.commonAncestorContainer)) {
        setSelectionPopover(null)
        return
      }

      const text = selection.toString().trim()
      if (!text) {
        setSelectionPopover(null)
        return
      }

      const anchorEl =
        range.commonAncestorContainer instanceof Element
          ? range.commonAncestorContainer
          : range.commonAncestorContainer.parentElement
      const pageEl = anchorEl?.closest<HTMLElement>("[data-page-number]")
      const page = pageEl ? Number(pageEl.dataset.pageNumber) : 1
      const rect = range.getBoundingClientRect()

      setSelectionPopover({ text, page, x: rect.right, y: rect.bottom })
    }

    const handleScroll = () => setSelectionPopover(null)

    window.document.addEventListener("selectionchange", handleSelectionChange)
    container.addEventListener("scroll", handleScroll)
    return () => {
      window.document.removeEventListener("selectionchange", handleSelectionChange)
      container.removeEventListener("scroll", handleScroll)
    }
  }, [])

  if (!document || !numPages) {
    return (
      <div className="flex flex-1 items-center justify-center text-[13.5px] text-ink-soft">
        Đang tải tài liệu…
      </div>
    )
  }

  return (
    <div
      ref={scrollRef}
      className="min-h-0 min-w-0 flex-1 overflow-x-auto overflow-y-auto bg-[#F4F3EF] px-6 py-6"
    >
      {Array.from({ length: numPages }, (_, i) => i + 1).map((n) => (
        <PdfPage
          key={n}
          document={document}
          pageNumber={n}
          totalPages={numPages}
          zoom={zoom}
          fileName={fileName}
          shouldRender={visiblePages.has(n)}
          registerEl={registerEl(n)}
        />
      ))}

      {selectionPopover && onAskAboutSelection && (
        <button
          type="button"
          style={{ position: "fixed", left: selectionPopover.x + 8, top: selectionPopover.y + 8 }}
          className="z-50 flex items-center gap-1.5 rounded-full border border-navy/30 bg-navy px-3 py-1.5 text-[12px] font-semibold text-white shadow-[0_10px_24px_-10px_rgba(0,0,0,0.5)] transition-opacity hover:opacity-90"
          onMouseDown={(e) => e.preventDefault()}
          onClick={() => {
            onAskAboutSelection(selectionPopover.text, selectionPopover.page)
            window.getSelection()?.removeAllRanges()
            setSelectionPopover(null)
          }}
        >
          <Sparkles className="size-3.5" />
          Hỏi chatbot
        </button>
      )}
    </div>
  )
})
