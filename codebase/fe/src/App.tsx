import { lazy, Suspense } from "react"
import { Route, Routes } from "react-router-dom"

import { CourseDetailPage } from "@/pages/course-detail-page"
import { CoursesPage } from "@/pages/courses-page"
import { DashboardPage } from "@/pages/dashboard-page"
import { LoginPage } from "@/pages/login-page"
import { WelcomePage } from "@/pages/welcome-page"

const CourseReaderPage = lazy(() => import("@/pages/course-reader-page"))

export function App() {
  return (
    <Routes>
      <Route path="/" element={<WelcomePage />} />
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
    </Routes>
  )
}

export default App
