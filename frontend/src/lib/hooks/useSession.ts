import { useEffect, useState } from "react";
import {
  createSession,
  deleteSession,
  getActiveSession,
} from "@/lib/api/session.api";

export const useSession = (notebookId: string) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  /**
   * Load or create session
   */
  const initSession = async () => {
    try {
      setLoading(true);

      const session = await getActiveSession(notebookId);
      setSessionId(session.session_id);
    } catch (err) {
      // fallback: create if not exists
      const session = await createSession(notebookId);
      setSessionId(session.session_id);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Reset session (delete + recreate)
   */
  const resetSession = async () => {
    if (!sessionId) return;

    await deleteSession(sessionId);

    const newSession = await createSession(notebookId);
    setSessionId(newSession.session_id);
  };

  useEffect(() => {
    if (!notebookId) return;
    initSession();
  }, [notebookId]);

  return {
    sessionId,
    loading,
    resetSession,
    refresh: initSession,
  };
};