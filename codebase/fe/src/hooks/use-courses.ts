import { useEffect, useState } from "react"
import { type CourseSummary, fetchCourses } from "@/lib/api"

export function useCourses() {
  const [courses, setCourses] = useState<CourseSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let mounted = true
    fetchCourses()
      .then((data) => {
        if (mounted) {
          setCourses(data)
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
  }, [])

  return { courses, loading, error }
}
