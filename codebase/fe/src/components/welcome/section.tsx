import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

export function Section({
  id,
  children,
  className,
}: {
  id?: string
  children: ReactNode
  className?: string
}) {
  return (
    <section id={id} className={cn("border-t border-line py-22", className)}>
      <div className="mx-auto max-w-[1140px] px-7">{children}</div>
    </section>
  )
}
