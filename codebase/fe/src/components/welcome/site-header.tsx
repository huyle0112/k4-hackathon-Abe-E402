import { Link } from "react-router-dom"

import { BrandMark } from "@/components/welcome/brand-mark"

const NAV_LINKS = [
  { href: "#vision", label: "Tầm nhìn" },
  { href: "#daily-loop", label: "Cách học" },
  { href: "#features", label: "Tính năng" },
  { href: "#for-instructors", label: "Giảng viên" },
]

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-line bg-paper/88 backdrop-blur-md">
      <div className="mx-auto flex max-w-[1140px] items-center justify-between px-7 py-4">
        <a href="#" className="flex items-center gap-[9px] text-[15px] font-semibold">
          <BrandMark />
          <span>
            VinUni AI Thực Chiến
            <span className="mx-0.5 font-normal text-ink-soft">·</span>
          </span>
          <small className="text-[12.5px] font-medium text-ink-soft">VLearn</small>
        </a>

        <nav className="hidden gap-7.5 text-[14.5px] text-ink-soft min-[860px]:flex">
          {NAV_LINKS.map((link) => (
            <a key={link.href} href={link.href} className="transition-colors hover:text-ink">
              {link.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-3.5">
          <span className="rounded-[6px] border border-line px-2 py-1 font-mono text-xs text-ink-soft">
            VI
          </span>
          <Link
            to="/login"
            className="rounded-[9px] border border-line px-[18px] py-2.5 text-[14.5px] font-semibold text-ink transition-colors hover:border-ink-soft"
          >
            Đăng nhập
          </Link>
          <a
            href="#daily-loop"
            className="rounded-[9px] bg-maroon px-[18px] py-2.5 text-[14.5px] font-semibold text-white transition-[transform,box-shadow] hover:-translate-y-px hover:shadow-[0_6px_16px_rgba(140,36,56,0.28)]"
          >
            Khám phá VLearn
          </a>
        </div>
      </div>
    </header>
  )
}
