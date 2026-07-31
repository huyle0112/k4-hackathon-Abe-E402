import { useState } from "react"
import { type ChatRequest, type ChatResponse, sendChatMessage } from "@/lib/api"

export function useChat() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const sendMessage = async (request: ChatRequest): Promise<ChatResponse> => {
    setLoading(true)
    setError(null)
    try {
      const res = await sendChatMessage(request)
      setLoading(false)
      return res
    } catch (err) {
      const finalErr = err instanceof Error ? err : new Error(String(err))
      setError(finalErr)
      setLoading(false)
      throw finalErr
    }
  }

  return { sendMessage, loading, error }
}
