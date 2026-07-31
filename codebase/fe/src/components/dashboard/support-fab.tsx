import { LifeBuoy } from "lucide-react"

export function SupportFab() {
  return (
    <button
      type="button"
      aria-label="Hỗ trợ nhanh"
      className="fixed right-6.5 bottom-6.5 flex size-12 items-center justify-center rounded-full border border-line bg-white text-navy shadow-[0_10px_26px_-8px_rgba(0,0,0,0.25)]"
    >
      <LifeBuoy className="size-5" />
    </button>
  )
}
