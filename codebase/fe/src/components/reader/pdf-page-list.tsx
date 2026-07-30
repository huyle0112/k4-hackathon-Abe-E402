import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react"

import { PdfPage } from "@/components/reader/pdf-page"
import type { PDFDocumentProxy } from "@/lib/pdf"

export type PdfPageListHandle = {
  goToPage: (page: number) => void
}

export const PdfPageList = forwardRef<
  PdfPageListHandle,
  {
    document: PDFDocumentProxy | null
    numPages: number | null
    zoom: number
    fileName: string
    onCurrentPageChange: (page: number) => void
  }
>(function PdfPageList(
  { document, numPages, zoom, fileName, onCurrentPageChange },
  ref
) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const pageElsRef = useRef<Map<number, HTMLDivElement>>(new Map())
  const observerRef = useRef<IntersectionObserver | null>(null)
  const rafRef = useRef<number | null>(null)
  const [visiblePages, setVisiblePages] = useState<Set<number>>(
    () => new Set([1])
  )

  useImperativeHandle(ref, () => ({
    goToPage: (page: number) => {
      pageElsRef.current
        .get(page)
        ?.scrollIntoView({ behavior: "smooth", block: "start" })
    },
  }))

  useEffect(() => {
    setVisiblePages(new Set([1]))
    pageElsRef.current.clear()
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

  const registerEl = useCallback(
    (n: number) => (el: HTMLDivElement | null) => {
      if (el) {
        pageElsRef.current.set(n, el)
        observerRef.current?.observe(el)
      } else {
        pageElsRef.current.delete(n)
      }
    },
    []
  )

  const handleScroll = useCallback(() => {
    if (rafRef.current !== null) return
    rafRef.current = requestAnimationFrame(() => {
      rafRef.current = null
      const container = scrollRef.current
      if (!container) return
      const containerRect = container.getBoundingClientRect()
      const thresholdY = containerRect.top + containerRect.height * 0.35
      let current = 1
      let bestTop = -Infinity
      for (const [n, el] of pageElsRef.current) {
        const top = el.getBoundingClientRect().top
        if (top <= thresholdY && top > bestTop) {
          bestTop = top
          current = n
        }
      }
      onCurrentPageChange(current)
    })
  }, [onCurrentPageChange])

  useEffect(() => {
    const el = scrollRef.current
    el?.addEventListener("scroll", handleScroll, { passive: true })
    handleScroll()
    return () => {
      el?.removeEventListener("scroll", handleScroll)
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current)
    }
  }, [handleScroll, document])

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
      className="flex-1 overflow-y-auto bg-[#F4F3EF] px-6 py-6"
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
    </div>
  )
})
