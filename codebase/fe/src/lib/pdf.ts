import {
  GlobalWorkerOptions,
  getDocument,
  type PDFDocumentProxy,
} from "pdfjs-dist"

// Served from public/ (copied from node_modules/pdfjs-dist/build/pdf.worker.min.mjs)
// rather than resolved via `new URL(..., import.meta.url)`: in dev, Vite pipes any
// in-project .mjs request through its HMR transform, which injects a `/@vite/client`
// import the worker's global scope can't satisfy, silently crashing the worker so
// getDocument() never resolves. A public/ asset is served byte-for-byte, unaffected.
GlobalWorkerOptions.workerSrc = "/pdf.worker.min.mjs"

const documentCache = new Map<string, Promise<PDFDocumentProxy>>()

export function loadPdfDocument(url: string): Promise<PDFDocumentProxy> {
  if (!url) {
    return Promise.reject(new Error("PDF URL is required"))
  }

  let pending = documentCache.get(url)
  if (!pending) {
    pending = getDocument({ url }).promise
    documentCache.set(url, pending)
  }
  return pending
}

export type { PDFDocumentProxy, PDFPageProxy, RenderTask } from "pdfjs-dist"
