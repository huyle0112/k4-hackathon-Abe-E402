export interface SlideFile {
  id: string;
  day: number;
  fileName: string;
  url: string;
  label: string;
}

export interface CourseDay {
  day: number;
  files: SlideFile[];
}

export interface Course {
  code: string;
  name: string;
  classmates: string;
  description: string;
  days: CourseDay[];
}

export interface CourseSummary {
  code: string;
  name: string;
  description: string;
  read_percent: number;
  total_days: number;
}

const API_BASE = "http://localhost:8000/api";

export async function fetchCourses(): Promise<CourseSummary[]> {
  const response = await fetch(`${API_BASE}/courses`);
  if (!response.ok) {
    throw new Error("Failed to fetch courses");
  }
  return response.json();
}

export async function fetchCourse(courseCode: string): Promise<Course> {
  const response = await fetch(`${API_BASE}/courses/${courseCode}`);
  if (!response.ok) {
    throw new Error("Failed to fetch course details");
  }
  return response.json();
}

export function findSlideFile(
  course: Course,
  slideId: string
): SlideFile | undefined {
  for (const day of course.days) {
    const file = day.files.find((f) => f.id === slideId);
    if (file) return file;
  }
  return undefined;
}
