import { Moon } from "lucide-react"

export function LocaleThemeControls() {
  return (
    <>
      <span className="flex size-9 items-center justify-center rounded-[9px] border border-line font-mono text-[11.5px] font-semibold text-ink-soft">
        VI
      </span>
      <button
        type="button"
        aria-label="Chuyển giao diện tối"
        className="flex size-9 items-center justify-center rounded-[9px] border border-line text-ink-soft"
      >
        <Moon className="size-[15px]" />
      </button>
    </>
  )
}
