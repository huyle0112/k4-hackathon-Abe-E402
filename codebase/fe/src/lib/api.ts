/**
 * API client cho VLearn Backend (FastAPI).
 * Tất cả các gọi API tập trung ở đây để dễ bảo trì.
 */

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/+$/, "")

// ──────────────────────────────────────────────
//  Types (khớp với Pydantic models bên backend)
// ──────────────────────────────────────────────

export type SlideFile = {
  id: string
  day: number
  file_name: string
  url: string
  label: string
}

export type CourseDay = {
  day: number
  files: SlideFile[]
}

export type Course = {
  code: string
  name: string
  classmates: string
  days: CourseDay[]
}

export type CourseSummary = {
  code: string
  name: string
  description: string
  read_percent: number
  total_days: number
}

export type Source = {
  slide_id: string
  day: number
  page: number
  file_name: string
  relevance_score: number
}

export type HistoryMessage = {
  role: "user" | "assistant"
  text: string
}

export type ChatRequest = {
  question: string
  course_code: string
  slide_id?: string | null
  page?: number | null
  history?: HistoryMessage[]
}

export type ChatResponse = {
  answer: string
  sources: Source[]
  confidence: number
  status: "ok" | "low_confidence" | "out_of_scope" | "error"
}

export type HealthResponse = {
  status: string
  version: string
  vector_store_ready: boolean
  indexed_chunks: number
}

// ──────────────────────────────────────────────
//  HTTP helper
// ──────────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })

  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const body = await response.json()
      detail = body.detail ?? detail
    } catch {
      // Ignore JSON parse errors
    }
    throw new Error(detail)
  }

  return response.json() as Promise<T>
}

// ──────────────────────────────────────────────
//  API functions
// ──────────────────────────────────────────────

/** GET /health */
export function fetchHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/health")
}

/** GET /courses — danh sách khóa học */
export function fetchCourses(): Promise<CourseSummary[]> {
  return apiFetch<CourseSummary[]>("/courses")
}

/** GET /courses/:courseCode — chi tiết khóa học */
export function fetchCourse(courseCode: string): Promise<Course> {
  return apiFetch<Course>(`/courses/${encodeURIComponent(courseCode)}`)
}

/** POST /chat — chatbot hỏi đáp */
export function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  return apiFetch<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(request),
  })
}
