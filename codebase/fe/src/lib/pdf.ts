import {
  GlobalWorkerOptions,
  getDocument,
  type PDFDocumentProxy,
} from "pdfjs-dist"

// pdfjs-dist internally calls the brand-new Map "upsert" methods (TC39 proposal),
// e.g. `this.#methodPromises.getOrInsertComputed(...)` in WorkerTransport. Browsers
// that haven't shipped these yet throw `getOrInsertComputed is not a function` and
// every document load fails silently. Polyfill per spec when missing.
//
// TS's lib.es2015.collection.d.ts doesn't declare these yet, so augment it here.
declare global {
  interface Map<K, V> {
    getOrInsertComputed(key: K, callback: (key: K) => V): V
    getOrInsert(key: K, defaultValue: V): V
  }
}

if (!Map.prototype.getOrInsertComputed) {
  Map.prototype.getOrInsertComputed = function <K, V>(
    this: Map<K, V>,
    key: K,
    callback: (key: K) => V,
  ): V {
    if (this.has(key)) return this.get(key) as V
    const value = callback(key)
    this.set(key, value)
    return value
  }
}
if (!Map.prototype.getOrInsert) {
  Map.prototype.getOrInsert = function <K, V>(this: Map<K, V>, key: K, defaultValue: V): V {
    if (this.has(key)) return this.get(key) as V
    this.set(key, defaultValue)
    return defaultValue
  }
}

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
