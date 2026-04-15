import api from "@/lib/axios";
import { ChatPayload } from "@/lib/types/chat";

export const sendQuery = async (data: ChatPayload) => {
  const res = await api.post("/chat/query", data);
  return res.data;
};

export const getChatHistory = async (sessionId: string) => {
  const res = await api.get(`/chat/history?session_id=${sessionId}`);
  return res.data;
};

export const deleteChatHistory = async (sessionId: string) => {
  const res = await api.delete(`/chat/history?session_id=${sessionId}`);
  return res.data;
};
