import { cn } from "@/lib/utils"

export function BrandMark({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "flex size-[26px] shrink-0 items-center justify-center rounded-[7px] bg-navy font-display text-sm font-semibold text-white",
        className
      )}
    >
      V
    </span>
  )
}
