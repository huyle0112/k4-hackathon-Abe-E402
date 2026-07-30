import { useEffect, useRef, useState } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"

import { PdfPageList, type PdfPageListHandle } from "@/components/reader/pdf-page-list"
import { ReaderPager } from "@/components/reader/reader-pager"
import { ReaderSidebar } from "@/components/reader/reader-sidebar"
import { ReaderToolbar } from "@/components/reader/reader-toolbar"
import { ReaderTopbar } from "@/components/reader/reader-topbar"
import { SupportFab } from "@/components/dashboard/support-fab"
import { COURSES, findSlideFile, type SlideFile } from "@/data/comp2010-slides"
import { usePdfDocument } from "@/hooks/use-pdf-document"
import { loadPdfDocument, type PDFDocumentProxy } from "@/lib/pdf"

const ZOOM_STEP = 0.2
const ZOOM_MIN = 0.6
const ZOOM_MAX = 2.4

function ReaderContent({
  file,
  document,
  numPages,
}: {
  file: SlideFile
  document: PDFDocumentProxy | null
  numPages: number | null
}) {
  const [zoom, setZoom] = useState(1)
  const [currentPage, setCurrentPage] = useState(1)
  const pageListRef = useRef<PdfPageListHandle>(null)

  return (
    <div className="relative flex min-h-0 flex-1 flex-col">
      <ReaderToolbar
        currentPage={currentPage}
        numPages={numPages}
        zoom={zoom}
        onZoomOut={() => setZoom((z) => Math.max(ZOOM_MIN, z - ZOOM_STEP))}
        onZoomIn={() => setZoom((z) => Math.min(ZOOM_MAX, z + ZOOM_STEP))}
        onZoomReset={() => setZoom(1)}
      />

      <PdfPageList
        ref={pageListRef}
        document={document}
        numPages={numPages}
        zoom={zoom}
        fileName={file.fileName}
        onCurrentPageChange={setCurrentPage}
      />

      <ReaderPager
        currentPage={currentPage}
        numPages={numPages ?? 0}
        onNavigate={(page) => pageListRef.current?.goToPage(page)}
      />
    </div>
  )
}

export function CourseReaderPage() {
  const { courseCode = "" } = useParams()
  const [searchParams] = useSearchParams()
  const slideId = searchParams.get("slide") ?? ""

  const course = COURSES[courseCode.toLowerCase()]
  const file = course ? findSlideFile(course, slideId) : undefined

  const [pageCounts, setPageCounts] = useState<Record<string, number | undefined>>({})
  const { document, numPages } = usePdfDocument(file?.url)

  useEffect(() => {
    if (!course) return
    for (const day of course.days) {
      for (const f of day.files) {
        loadPdfDocument(f.url).then((doc) => {
          setPageCounts((prev) => ({ ...prev, [f.id]: doc.numPages }))
        })
      }
    }
  }, [course])

  if (!course || !file) {
    return (
      <div className="flex min-h-svh flex-col items-center justify-center gap-3 bg-paper text-center text-ink-soft">
        <p>Không tìm thấy tài liệu này.</p>
        <Link to={`/courses/${courseCode}`} className="font-semibold text-maroon">
          Quay lại khóa học
        </Link>
      </div>
    )
  }

  return (
    <div className="flex h-svh flex-col bg-paper font-sans text-ink antialiased">
      <ReaderTopbar
        courseCode={courseCode}
        fileTitle={file.fileName}
        subtitle={`${course.code} · Day${String(file.day).padStart(2, "0")}`}
      />

      <div className="flex min-h-0 flex-1">
        <ReaderSidebar
          course={course}
          courseCode={courseCode}
          activeFileId={file.id}
          activeDay={file.day}
          pageCounts={pageCounts}
        />

        <ReaderContent key={file.id} file={file} document={document} numPages={numPages} />
      </div>

      <SupportFab />
    </div>
  )
}

export default CourseReaderPage
