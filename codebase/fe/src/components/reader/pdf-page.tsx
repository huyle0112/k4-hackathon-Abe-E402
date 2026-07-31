import { useEffect, useRef, useState } from "react"

import { Util, type PDFDocumentProxy, type RenderTask } from "@/lib/pdf"

type PositionedTextItem = {
  key: number
  str: string
  left: number
  top: number
  fontSize: number
  scaleX: number
  angleDeg: number
}

const DEFAULT_ASCENT_RATIO = 0.8

function layoutTextItems(
  items: Array<{ str?: string; transform?: number[] }>,
  viewportTransform: number[]
): PositionedTextItem[] {
  const positioned: PositionedTextItem[] = []
  let key = 0
  for (const item of items) {
    if (!item.str || !item.transform) continue
    const tx = Util.transform(viewportTransform, item.transform)
    const angle = Math.atan2(tx[1], tx[0])
    const fontSize = Math.hypot(tx[2], tx[3])
    const scaleX = fontSize ? Math.hypot(tx[0], tx[1]) / fontSize : 1
    const ascent = fontSize * DEFAULT_ASCENT_RATIO
    const left = angle === 0 ? tx[4] : tx[4] + ascent * Math.sin(angle)
    const top = angle === 0 ? tx[5] - ascent : tx[5] - ascent * Math.cos(angle)
    positioned.push({ key: key++, str: item.str, left, top, fontSize, scaleX, angleDeg: (angle * 180) / Math.PI })
  }
  return positioned
}

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
  const [textItems, setTextItems] = useState<PositionedTextItem[]>([])

  useEffect(() => {
    if (!shouldRender || !canvasRef.current) {
      setTextItems([])
      return
    }

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

      page.getTextContent().then((textContent) => {
        if (cancelled) return
        setTextItems(layoutTextItems(textContent.items, cssViewport.transform))
      })
    })

    return () => {
      cancelled = true
      renderTask?.cancel()
      setTextItems([])
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
          <div className="relative block leading-none">
            <canvas ref={canvasRef} className="block" />
            <div className="pdf-text-layer absolute inset-0 overflow-hidden">
              {textItems.map((item) => (
                <span
                  key={item.key}
                  style={{
                    position: "absolute",
                    left: item.left,
                    top: item.top,
                    fontSize: item.fontSize,
                    transform: `rotate(${item.angleDeg}deg) scaleX(${item.scaleX})`,
                    transformOrigin: "0% 0%",
                    whiteSpace: "pre",
                    color: "transparent",
                    cursor: "text",
                    userSelect: "text",
                  }}
                >
                  {item.str}
                </span>
              ))}
            </div>
          </div>
        ) : (
          <span className="font-mono text-[11px] text-ink-soft/60">
            Đang tải…
          </span>
        )}
      </div>
    </div>
  )
}
