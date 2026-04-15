import { buildUrl } from "../../core/client"
import { ChatQueryRequest, ChatMessage } from "./chat.types"

export const chatApi = {
  streamQuery: (
    body: ChatQueryRequest,
    onMessage: (chunk: string) => void,
    onDone?: () => void,
    onError?: (err: any) => void
  ) => {
    const url = buildUrl("/chat/query") // ✅ FIXED

    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("jwt")}`,
      },
      body: JSON.stringify(body),
    }).then(async (res) => {
      const reader = res.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) return

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split("\n")

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = JSON.parse(line.replace("data: ", ""))

            if (data.content) onMessage(data.content)
            if (data.done && onDone) onDone()
            if (data.error && onError) onError(data.error)
          }
        }
      }
    })
  },

  getHistory: async (sessionId: string) => {
    const res = await fetch(
      buildUrl(`/chat/history?session_id=${sessionId}`),
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("jwt")}`,
        },
      }
    )
    return res.json()
  },

  clearHistory: async (sessionId: string) => {
    await fetch(
      buildUrl(`/chat/history?session_id=${sessionId}`),
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("jwt")}`,
        },
      }
    )
  },
}