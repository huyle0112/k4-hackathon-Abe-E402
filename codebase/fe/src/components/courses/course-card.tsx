import { Link } from "react-router-dom"
import { Activity, ArrowRight, BookOpen, NotebookPen } from "lucide-react"

export function CourseCard({
  code,
  name,
  description,
  readPercent,
  notebookHref,
  openHref,
}: {
  code: string
  name: string
  description: string
  readPercent: number
  notebookHref: string
  openHref: string
}) {
  return (
    <div className="group mb-5 max-w-[600px] rounded-2xl border border-line bg-white p-7 shadow-[0_14px_30px_-24px_rgba(28,43,74,0.25)] transition-[border-color,box-shadow] hover:border-navy/40 hover:shadow-[0_18px_36px_-22px_rgba(28,43,74,0.35)]">
      <Link to={openHref} className="block">
        <div className="mb-4.5 flex items-start justify-between">
          <div className="flex size-11 items-center justify-center rounded-[11px] bg-[#EAF0F8] text-navy">
            <BookOpen className="size-[19px]" />
          </div>
          <span className="rounded-full bg-ok/10 px-3.5 py-1.5 text-[12.5px] font-bold text-ok">
            {readPercent}% đọc
          </span>
        </div>

        <div className="mb-1.5 font-mono text-[11.5px] tracking-[0.06em] text-ink-soft uppercase">
          {code}
        </div>
        <h3 className="mb-1.5 text-[21px] font-extrabold tracking-[-0.01em]">
          {name}
        </h3>
        <p className="mb-4.5 text-[14px] text-ink-soft">{description}</p>

        <div className="mb-4 h-[7px] overflow-hidden rounded-full bg-[#EEEBE3]">
          <div
            className="h-full rounded-full bg-gradient-to-r from-maroon to-[#E88A97]"
            style={{ width: `${readPercent}%` }}
          />
        </div>

        <div className="mb-5 flex items-center gap-1.5 text-[13.5px] font-semibold text-ok">
          <Activity className="size-[15px]" />
          Sẵn sàng học
        </div>
      </Link>

      <div className="flex items-center gap-4.5">
        <a
          href={notebookHref}
          onClick={(event) => event.stopPropagation()}
          className="flex items-center gap-2 rounded-[9px] border border-line bg-white px-3.5 py-2.5 text-[13.5px] font-semibold text-ink"
        >
          <NotebookPen className="size-[15px] text-navy" />
          Sổ tay học tập
        </a>
        <Link
          to={openHref}
          className="flex items-center gap-1.5 text-[13.5px] font-bold text-maroon"
        >
          Mở khóa học
          <ArrowRight className="size-3.5" />
        </Link>
      </div>
    </div>
  )
}
