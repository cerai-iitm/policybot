import api from "@/lib/axios";
import { ChatPayload } from "@/lib/types/chat";
import { API_URL } from "@/lib/config/env";
import { getToken } from "@/lib/utils/token";

export const sendQueryStream = async (
  data: ChatPayload,
  onMessage: (msg: string) => void
) => {
  const token = getToken();

  const response = await fetch(`${API_URL}/chat/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      Accept: "text/event-stream",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Query failed");
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) throw new Error("No reader");

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // 🔥 Split by double newline (SSE event boundary)
    const events = buffer.split("\n\n");

    for (let i = 0; i < events.length - 1; i++) {
      const event = events[i].trim();

      if (!event.startsWith("data:")) continue;

      const jsonStr = event.replace(/^data:\s*/, "");

      try {
        const parsed = JSON.parse(jsonStr);

        // ✅ HANDLE CONTENT STREAM
        if (parsed.content) {
          onMessage(parsed.content);
        }

        // ✅ HANDLE END
        if (parsed.done) {
          return;
        }

        // (optional later)
        // if (parsed.context_chunks) { ... }

      } catch (err) {
        console.error("Stream parse error:", err, jsonStr);
      }
    }

    buffer = events[events.length - 1];
  }
};

export const getChatHistory = async (sessionId: string) => {
  const res = await api.get(`/chat/history?session_id=${sessionId}`);
  return res.data;
};

export const deleteChatHistory = async (sessionId: string) => {
  const res = await api.delete(`/chat/history?session_id=${sessionId}`);
  return res.data;
};
