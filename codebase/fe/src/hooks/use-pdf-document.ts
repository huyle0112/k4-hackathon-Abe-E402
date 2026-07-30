import { useEffect, useState } from "react"

import { loadPdfDocument, type PDFDocumentProxy } from "@/lib/pdf"

type Status = "idle" | "loading" | "ready" | "error"

type Result = {
  url: string | undefined
  document: PDFDocumentProxy | null
  numPages: number | null
  status: Status
}

export function usePdfDocument(url: string | undefined) {
  const [result, setResult] = useState<Result>({
    url: undefined,
    document: null,
    numPages: null,
    status: "idle",
  })

  useEffect(() => {
    if (!url) return

    let cancelled = false

    loadPdfDocument(url).then(
      (doc) => {
        if (cancelled) return
        setResult({ url, document: doc, numPages: doc.numPages, status: "ready" })
      },
      () => {
        if (cancelled) return
        setResult({ url, document: null, numPages: null, status: "error" })
      }
    )

    return () => {
      cancelled = true
    }
  }, [url])

  if (!url) {
    return { document: null, numPages: null, status: "idle" as const }
  }
  if (result.url !== url) {
    return { document: null, numPages: null, status: "loading" as const }
  }
  return { document: result.document, numPages: result.numPages, status: result.status }
}
