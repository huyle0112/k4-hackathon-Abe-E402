import type { ReactNode } from "react"

export function PageHead({
  title,
  description,
  pill,
}: {
  title: string
  description: string
  pill?: ReactNode
}) {
  return (
    <div className="mb-7 flex flex-wrap items-start justify-between gap-6">
      <div>
        <span className="mb-2 block font-mono text-[11.5px] font-semibold tracking-[0.1em] text-maroon uppercase">
          VLearn · VinUni AI Thực Chiến
        </span>
        <h1 className="mb-2 text-[29px] font-bold tracking-[-0.01em]">
          {title}
        </h1>
        <p className="max-w-[560px] text-[15px] text-ink-soft">
          {description}
        </p>
      </div>
      {pill && (
        <span className="rounded-full border border-line bg-white px-4 py-2.5 text-[13.5px] font-semibold whitespace-nowrap">
          {pill}
        </span>
      )}
    </div>
  )
}
