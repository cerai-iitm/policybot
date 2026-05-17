import { Message } from "./types/chat.types";

export const mapHistoryToMessages = (
  apiMessages: any[]
): Message[] => {
  return apiMessages.map((msg) => ({
    id: String(msg.id),

    type: msg.role === "user" ? "user" : "ai",

    content: msg.content || "",

    /**
     * Historical messages are ALWAYS completed.
     */
    isStreaming: false,

    loading: false,
  }));
};