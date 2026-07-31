export type SlideFile = {
  id: string
  day: number
  fileName: string
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

function slideFile(day: number, fileName: string, label: string): SlideFile {
  return {
    id: `D${String(day).padStart(2, "0")}-S01`,
    day,
    fileName,
    url: `/slides/${fileName}`,
    label,
  }
}

export const COURSES: Record<string, Course> = {
  comp2010: {
    code: "COMP2010",
    name: "COMP2010 – Khoá 3 + 4 Phase 1",
    classmates: "1074 học viên cùng lớp",
    days: [
      {
        day: 1,
        files: [slideFile(1, "d1-slide-hackathon.pdf", "Giới thiệu môn học")],
      },
      {
        day: 2,
        files: [slideFile(2, "d2-slide-hackathon.pdf", "Nội dung buổi học")],
      },
    ],
  },
}

export function findSlideFile(
  course: Course,
  slideId: string
): SlideFile | undefined {
  for (const day of course.days) {
    const file = day.files.find((f) => f.id === slideId)
    if (file) return file
  }
  return undefined
}
