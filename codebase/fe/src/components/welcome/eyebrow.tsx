import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

export function Eyebrow({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <span
      className={cn(
        "font-mono text-[11.5px] font-medium tracking-[0.11em] text-maroon uppercase",
        className
      )}
    >
      {children}
    </span>
  )
}
