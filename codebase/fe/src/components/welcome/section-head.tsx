import type { ReactNode } from "react"

import { Eyebrow } from "@/components/welcome/eyebrow"

export function SectionHead({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string
  title: ReactNode
  description?: ReactNode
}) {
  return (
    <div className="mb-11 max-w-[640px]">
      <Eyebrow>{eyebrow}</Eyebrow>
      <h2 className="mt-3.5 font-display text-[clamp(26px,3.4vw,38px)] leading-[1.22] font-medium tracking-[-0.005em]">
        {title}
      </h2>
      {description ? (
        <p className="mt-3.5 max-w-[560px] text-base text-ink-soft">
          {description}
        </p>
      ) : null}
    </div>
  )
}
