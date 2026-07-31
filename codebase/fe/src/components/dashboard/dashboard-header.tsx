import { Link, useLocation } from "react-router-dom"
import { BookOpen, ChevronDown, ExternalLink, Home, NotebookPen } from "lucide-react"

import { LocaleThemeControls } from "@/components/dashboard/locale-theme-controls"
import { BrandMark } from "@/components/welcome/brand-mark"
import { cn } from "@/lib/utils"

const NAV_LINKS = [
  { href: "/dashboard", label: "Trang chủ", icon: Home },
  { href: "/courses", label: "Khóa học của tôi", icon: BookOpen },
  { href: "#", label: "Sổ tay học tập", icon: NotebookPen },
]

export function DashboardHeader({ email }: { email: string }) {
  const { pathname } = useLocation()

  return (
    <header className="sticky top-0 z-20 border-b border-line bg-white">
      <div className="mx-auto flex h-16 max-w-[1320px] items-center justify-between px-8">
        <div className="flex flex-1 items-center">
          <Link
            to="/dashboard"
            className="flex items-center gap-[9px] text-[15px] font-semibold text-ink"
          >
            <BrandMark />
            <span>
              V<span className="text-maroon">Learn</span>
            </span>
          </Link>

          <nav className="ml-5 flex items-center gap-1.5">
            {NAV_LINKS.map((link) => {
              const active = pathname.startsWith(link.href)
              return (
                <Link
                  key={link.href}
                  to={link.href}
                  className={cn(
                    "flex items-center gap-1.5 rounded-[9px] px-3.5 py-2.5 text-[14.5px] font-semibold text-ink-soft transition-colors",
                    active && "text-maroon shadow-[inset_0_-2px_0_#8c2438]"
                  )}
                >
                  <link.icon className="size-4" />
                  {link.label}
                </Link>
              )
            })}
          </nav>
        </div>

        <div className="flex items-center gap-2.5">
          <a
            href="#"
            className="flex items-center gap-1.5 rounded-[9px] border border-line bg-white px-3.5 py-2 text-[13.5px] font-semibold text-ink"
          >
            <ExternalLink className="size-3.5" />
            Mở Codelabs
          </a>
          <LocaleThemeControls />
          <div className="flex items-center gap-2 rounded-[9px] border border-line py-1.5 pr-2.5 pl-2 text-[13.5px]">
            <span className="flex size-5 items-center justify-center rounded-full bg-navy font-mono text-[11px] font-bold text-white">
              2
            </span>
            <span className="max-w-[140px] truncate font-semibold text-ink">
              {email}
            </span>
            <ChevronDown className="size-3.5 text-ink-soft" />
          </div>
        </div>
      </div>
    </header>
  )
}
