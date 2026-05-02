import { Message } from "./types/chat.types";

export const mapHistoryToMessages = (apiMessages: any[]): Message[] => {
  return apiMessages.map((msg) => ({
    id: String(msg.id), // backend id → string
    type: msg.role === "user" ? "user" : "ai",
    content: msg.content,
  }));
};