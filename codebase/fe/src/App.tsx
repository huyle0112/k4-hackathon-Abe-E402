import { lazy, Suspense } from "react"
import { Navigate, Route, Routes } from "react-router-dom"

import { CourseDetailPage } from "@/pages/course-detail-page"
import { CoursesPage } from "@/pages/courses-page"
import { DashboardPage } from "@/pages/dashboard-page"
import { LoginPage } from "@/pages/login-page"
import { WelcomePage } from "@/pages/welcome-page"

const CourseReaderPage = lazy(() => import("@/pages/course-reader-page"))
const CourseMindmapPage = lazy(() => import("@/pages/course-mindmap-page"))

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/welcome" element={<WelcomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/courses" element={<CoursesPage />} />
      <Route path="/courses/:courseCode" element={<CourseDetailPage />} />
      <Route
        path="/courses/:courseCode/reader"
        element={
          <Suspense fallback={null}>
            <CourseReaderPage />
          </Suspense>
        }
      />
      <Route
        path="/courses/:courseCode/mindmap"
        element={
          <Suspense fallback={null}>
            <CourseMindmapPage />
          </Suspense>
        }
      />
    </Routes>
  )
}

export default App
