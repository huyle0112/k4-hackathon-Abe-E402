import { useEffect, useRef } from "react"
import MindElixir, { type MindElixirData, type Theme } from "mind-elixir"
import "mind-elixir/style.css"

const VLEARN_MINDMAP_THEME: Theme = {
  name: "vlearn",
  type: "light",
  palette: ["#1c2b4a", "#8c2438", "#b08d3e", "#2f6f52", "#5b6270", "#3f5aa6"],
  cssVar: {
    "--main-color": "#171a1f",
    "--main-bgcolor": "#faf9f6",
    "--color": "#171a1f",
    "--bgcolor": "#ffffff",
    "--selected": "#1c2b4a",
    "--root-color": "#faf9f6",
    "--root-bgcolor": "#1c2b4a",
    "--root-radius": "16px",
    "--main-radius": "10px",
    "--panel-color": "#171a1f",
    "--panel-bgcolor": "#ffffff",
    "--panel-border-color": "#e4e1d9",
    "--map-padding": "60px",
  },
}

export function MindElixirCanvas({ data }: { data: MindElixirData }) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const mind = new MindElixir({
      el: container,
      direction: MindElixir.SIDE,
      editable: false,
      contextMenu: false,
      toolBar: true,
      keypress: false,
      theme: VLEARN_MINDMAP_THEME,
    })
    mind.init(data)

    return () => {
      container.replaceChildren()
    }
  }, [data])

  return <div ref={containerRef} className="size-full" />
}
