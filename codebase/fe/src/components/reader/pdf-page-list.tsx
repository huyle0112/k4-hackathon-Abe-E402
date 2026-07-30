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
  const currentPageObserverRef = useRef<IntersectionObserver | null>(null)
  const visibleAreaRef = useRef<Map<number, number>>(new Map())
  const [visiblePages, setVisiblePages] = useState<Set<number>>(
    () => new Set([1])
  )

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
      className="min-h-0 flex-1 overflow-y-auto bg-[#F4F3EF] px-6 py-6"
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
