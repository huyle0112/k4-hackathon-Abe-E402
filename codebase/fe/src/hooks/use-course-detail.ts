import { useEffect, useState } from "react"
import { type Course, fetchCourse } from "@/lib/api"

export function useCourseDetail(courseCode: string) {
  const [course, setCourse] = useState<Course | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    if (!courseCode) return

    let mounted = true
    setLoading(true)
    fetchCourse(courseCode)
      .then((data) => {
        if (mounted) {
          setCourse(data)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err)
          setLoading(false)
        }
      })
    return () => {
      mounted = false
    }
  }, [courseCode])

  return { course, loading, error }
}
