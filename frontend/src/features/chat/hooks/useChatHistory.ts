"use client";

import { useEffect, useState } from "react";
import { getChatHistory } from "@/lib/api/chat.api";
import { mapHistoryToMessages } from "../chat.mapper";

export const useChatHistory = (
  sessionId: string,
  setChatMessages: any,
  clearChat: any
) => {
  const [isLoading, setIsLoading] = useState(true);

useEffect(() => {
  const fetchHistory = async () => {
    try {
      setIsLoading(true);
      const res = await getChatHistory(sessionId);
      const mapped = mapHistoryToMessages(res.messages || []);
      setChatMessages(mapped);
    } catch {
      clearChat();
    } finally {
      setIsLoading(false);
    }
  };

  fetchHistory();
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, [sessionId]); // ✅ ONLY sessionId

  return { isLoading };
};