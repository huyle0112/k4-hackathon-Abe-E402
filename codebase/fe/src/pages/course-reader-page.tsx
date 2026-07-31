import { Loader2 } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"

import { PdfPageList, type PdfPageListHandle } from "@/components/reader/pdf-page-list"
import { ReaderChatSidebar } from "@/components/reader/reader-chat-sidebar"
import { ReaderPager } from "@/components/reader/reader-pager"
import { ReaderSidebar } from "@/components/reader/reader-sidebar"
import { ReaderToolbar } from "@/components/reader/reader-toolbar"
import { ReaderTopbar } from "@/components/reader/reader-topbar"
import { SupportFab } from "@/components/dashboard/support-fab"
import { fetchCourse, findSlideFile, type Course, type SlideFile } from "@/lib/courses-api"
import { usePdfDocument } from "@/hooks/use-pdf-document"
import { loadPdfDocument, type PDFDocumentProxy } from "@/lib/pdf"

const ZOOM_STEP = 0.2
const ZOOM_MIN = 0.6
const ZOOM_MAX = 2.4
const ZOOM_DEFAULT = 0.8

function ReaderContent({
  file,
  courseCode,
  document,
  numPages,
  onCurrentPageChange,
}: {
  file: SlideFile
  courseCode: string
  document: PDFDocumentProxy | null
  numPages: number | null
  onCurrentPageChange?: (page: number) => void
}) {
  const [zoom, setZoom] = useState(ZOOM_DEFAULT)
  const [currentPage, setCurrentPageState] = useState(1)
  const pageListRef = useRef<PdfPageListHandle>(null)

  const setCurrentPage = (page: number) => {
    setCurrentPageState(page)
    onCurrentPageChange?.(page)
  }

  return (
    <div className="relative flex min-h-0 min-w-0 flex-1 flex-col">
      <ReaderToolbar
        currentPage={currentPage}
        numPages={numPages}
        zoom={zoom}
        onZoomOut={() => setZoom((z) => Math.max(ZOOM_MIN, z - ZOOM_STEP))}
        onZoomIn={() => setZoom((z) => Math.min(ZOOM_MAX, z + ZOOM_STEP))}
        onZoomReset={() => setZoom(ZOOM_DEFAULT)}
        mindmapHref={`/courses/${courseCode}/mindmap?slide=${file.id}`}
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

  const [course, setCourse] = useState<Course | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCourse(courseCode)
      .then(setCourse)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [courseCode])

  const file = course ? findSlideFile(course, slideId) : undefined

  const [pageCounts, setPageCounts] = useState<Record<string, number | undefined>>({})
  const { document, numPages } = usePdfDocument(file?.url)
  const [chatPage, setChatPage] = useState(1)
  const [chatPageFileId, setChatPageFileId] = useState(file?.id)

  if (file?.id !== chatPageFileId) {
    setChatPageFileId(file?.id)
    setChatPage(1)
  }

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

  if (loading) {
    return (
      <div className="flex h-svh flex-col bg-paper text-ink antialiased">
        <div className="flex flex-1 items-center justify-center">
          <Loader2 className="size-8 animate-spin text-navy" />
        </div>
      </div>
    )
  }

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

        <ReaderContent
          key={file.id}
          file={file}
          courseCode={courseCode}
          document={document}
          numPages={numPages}
          onCurrentPageChange={setChatPage}
        />

        <ReaderChatSidebar currentPage={chatPage} slideFileId={file.id} />
      </div>

      
    </div>
  )
}

export default CourseReaderPage
