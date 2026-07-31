import { useEffect, useRef } from "react"

import type { PDFDocumentProxy, RenderTask } from "@/lib/pdf"

export function PdfPage({
  document,
  pageNumber,
  totalPages,
  zoom,
  fileName,
  shouldRender,
  registerEl,
}: {
  document: PDFDocumentProxy
  pageNumber: number
  totalPages: number
  zoom: number
  fileName: string
  shouldRender: boolean
  registerEl: (el: HTMLDivElement | null) => void
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    if (!shouldRender || !canvasRef.current) return

    let cancelled = false
    let renderTask: RenderTask | null = null

    document.getPage(pageNumber).then((page) => {
      if (cancelled) return
      const canvas = canvasRef.current
      if (!canvas) return

      const outputScale = zoom * (window.devicePixelRatio || 1)
      const pixelViewport = page.getViewport({ scale: outputScale })
      const cssViewport = page.getViewport({ scale: zoom })

      canvas.width = Math.floor(pixelViewport.width)
      canvas.height = Math.floor(pixelViewport.height)
      canvas.style.width = `${Math.floor(cssViewport.width)}px`
      canvas.style.height = `${Math.floor(cssViewport.height)}px`

      const ctx = canvas.getContext("2d")
      if (!ctx) return

      renderTask = page.render({
        canvas,
        canvasContext: ctx,
        viewport: pixelViewport,
      })
      renderTask.promise.catch((err: unknown) => {
        if (!(err instanceof Error && err.name === "RenderingCancelledException")) {
          throw err
        }
      })
    })

    return () => {
      cancelled = true
      renderTask?.cancel()
    }
  }, [shouldRender, zoom, document, pageNumber])

  return (
    <div
      ref={registerEl}
      data-page-number={pageNumber}
      className="mx-auto mb-6 w-fit overflow-hidden rounded-xl border border-line bg-[#FCFBF8] shadow-[0_10px_24px_-20px_rgba(28,43,74,0.3)]"
    >
      <div className="flex items-center justify-between border-b border-line px-4 py-2 font-mono text-[11px] text-ink-soft">
        <span>
          Trang {pageNumber} / {totalPages}
        </span>
        <span className="truncate">{fileName}</span>
      </div>
      <div className="flex min-h-[300px] min-w-[220px] items-center justify-center">
        {shouldRender ? (
          <canvas ref={canvasRef} />
        ) : (
          <span className="font-mono text-[11px] text-ink-soft/60">
            Đang tải…
          </span>
        )}
      </div>
    </div>
  )
}
