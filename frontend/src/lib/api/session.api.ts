import api from "@/lib/axios";
import { Session } from "@/lib/types/session";

/**
 * Create session (triggered after notebook creation OR reset)
 */
export const createSession = async (notebookId: string): Promise<Session> => {
  const res = await api.post("/chat/sessions", {
    notebook_id: notebookId,
    title: "default", // always default
  });

  return res.data;
};

/**
 * Get active session for a notebook
 */
export const getActiveSession = async (
  notebookId: string
): Promise<Session> => {
  const res = await api.get(`/chat/sessions/active/${notebookId}`);
  return res.data;
};

/**
 * Delete session
 */
export const deleteSession = async (sessionId: string): Promise<void> => {
  await api.delete(`/chat/sessions/${sessionId}`);
};