"use_client";
import React, { useState, useRef, useEffect, useCallback } from "react";
import { FaGithubSquare } from "react-icons/fa";
import { MdDarkMode, MdLightMode } from "react-icons/md";
import HumanMessage from "./HumanMessage";
import AIMessage from "./AIMessage";
import ChatInput from "./ChatInput";
import { SidebarItem } from "../leftSidebar/LeftSidebar";
import { useTheme } from "next-themes";
import { v4 as uuidv4 } from "uuid";
import { withBase } from "@/lib/url";
import ModelSelector from "./ModelSelector";
import { useAdmin } from "@/app/components/AdminContext";

interface SourceChunk {
  text: string;
  source: string;
  page_number: number | null;
}

interface Message {
  type: "user" | "ai";
  content: string;
  sourceChunks?: SourceChunk[];
}

interface QueryRequestBody {
  query: string;
  pdfs: string[];
  session_id: string;
  model_name?: string;
}

interface ChatSectionProps {
  checkedPdfs: string[];
  sources: SidebarItem[];
}

const ChatSection: React.FC<ChatSectionProps> = ({ checkedPdfs, sources }) => {
  console.log("Sources in ChatSection:", sources);
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState("");
  const [warning, setWarning] = useState("");
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [sessionId] = useState(() => getOrCreateSessionId());
  const chatHistoryRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(false);
  const { theme, setTheme, systemTheme } = useTheme();
  
  // Model selection state (admin only)
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [availableModels, setAvailableModels] = useState<Array<{id: string, name: string}>>([]);

  const resolvedTheme = theme === "system" ? systemTheme : theme;
  const { isAdmin } = useAdmin();
  
  function getOrCreateSessionId() {
    const newSessionId = uuidv4();
    // localStorage.setItem("sessionId", newSessionId);
    return newSessionId;
  }
  const handleSend = async () => {
    console.log("handleSend called with input:", userInput.trim());
    if (loading) {
      // Optionally show a message: "Please wait for the current response."
      return;
    }
    if (checkedPdfs.length === 0) {
      setWarning("Please select at least one PDF before sending a query.");
      return;
    }
    setWarning("");
    if (userInput.trim()) {
      const humanMessage = { type: "user" as const, content: userInput.trim() };
      setUserInput("");
      // Add user message and placeholder AI message with loader
      setMessages((prev) => [
        ...prev,
        humanMessage,
        { type: "ai", content: "", sourceChunks: [] }, // Loader placeholder
      ]);
      try {
        console.log("Sending request with PDFs:", checkedPdfs);
        setLoading(true);
        
        // Build request body
        const requestBody: QueryRequestBody = {
          query: userInput.trim(),
          pdfs: checkedPdfs,
          session_id: sessionId,
        };
        
        // Only include model_name if admin AND model is selected
        if (isAdmin && selectedModel) {
          requestBody.model_name = selectedModel;
        }
        
        console.log("Query request:", {
          isAdmin,
          model: isAdmin ? selectedModel : "default",
          pdfsCount: checkedPdfs.length
        });
        
        const response = await fetch(withBase("/api/query"), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Update the last AI message with the actual response and source chunks
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastIdx = newMessages.length - 1;
          if (newMessages[lastIdx].type === "ai") {
            if (data.error) {
              newMessages[lastIdx] = {
                ...newMessages[lastIdx],
                content: "Error: Failed to get response.",
                sourceChunks: data.context_chunks || [],
              };
            } else {
              newMessages[lastIdx] = {
                ...newMessages[lastIdx],
                content: data.response,
                sourceChunks: data.context_chunks || [],
              };
            }
          }
          return newMessages;
        });
        setLoading(false);
        await fetchSuggestedQuestions();
      } catch (error) {
        setLoading(false);
        console.error("Fetch error:", error);
        // Update the last AI message with error
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastIdx = newMessages.length - 1;
          if (newMessages[lastIdx].type === "ai") {
            newMessages[lastIdx] = {
              ...newMessages[lastIdx],
              content: "Error: Failed to get response.",
              sourceChunks: [],
            };
          }
          return newMessages;
        });
      }
    }
  };
  const handleSuggestionClick = (question: string) => {
    setUserInput(question);
  };

  const fetchSuggestedQuestions = useCallback(async () => {
    try {
      const res = await fetch(withBase("/api/suggested-queries"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
      await res.json(); // Consume response (feature currently disabled)
      // setSuggestedQuestions(data.suggested_queries || []); // TODO: Re-enable when ready
      setSuggestedQuestions([]);
    } catch {
      setSuggestedQuestions([]);
    }
  }, [sessionId]);

  // Handle model selection change (admin only)
  const handleModelChange = (modelId: string) => {
    console.log("Model changed to:", modelId);
    setSelectedModel(modelId);
  };

  // Fetch default model on mount (admin only)
  useEffect(() => {
    if (!isAdmin) return;

    let mounted = true;
    (async () => {
      try {
        const response = await fetch(withBase("/api/default-model"));
        if (!response.ok) {
          console.error("Failed to fetch default model:", response.statusText);
          return;
        }
        
        const data = await response.json();
        // data: { model_name: "gemma3n:e4b", provider: "ollama", supported_models: [...] }
        
        if (!mounted) return;
        
        setSelectedModel(data.model_name);
        setAvailableModels(data.supported_models || []);
        
        console.log("Initialized model selection:", {
          default: data.model_name,
          available: data.supported_models?.length || 0
        });
      } catch (error) {
        console.error("Error fetching default model:", error);
      }
    })();
    
    return () => { mounted = false; };
  }, [isAdmin]);

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [messages]);
  useEffect(() => {
    fetchSuggestedQuestions();
  }, [fetchSuggestedQuestions]); // on mount

  useEffect(() => {
    if (warning) {
      window.alert(warning);
      setWarning("");
    }
  }, [warning]);

  return (
    <div
      id="chat-section"
      className="relative flex flex-col h-full min-h-0 bg-bg-light"
    >
      {/* ChatSection Topbar - icons/navbar (placed above messages so messages render below) */}
      <div
        id="chat-topbar"
        className="flex items-center justify-end px-4 py-2 bg-bg-light z-10"
      >
        {/* Model selector dropdown */}
        {isAdmin && availableModels.length > 0 && (
          <ModelSelector
            models={availableModels}
            selected={selectedModel}
            onChange={handleModelChange}
          />
        )}

        {/* GitHub link - opens repo in new tab */}
        <a
          href="https://github.com/cerai-iitm/policybot"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Open PolicyBot on GitHub"
          className="flex items-center rounded-md p-1 hover:bg-bg-dark"
        >
          <FaGithubSquare className="w-6 h-6 text-[var(--color-text)]" />
        </a>
        {/* Theme toggle */}
        <button
          aria-label="Toggle theme"
          title="Toggle dark / light"
          onClick={() =>
            setTheme(
              (resolvedTheme === "dark" ? "light" : "dark") as "light" | "dark"
            )
          }
          className="ml-2 p-1 rounded-md hover:bg-bg-dark flex items-center justify-center"
        >
          {resolvedTheme === "dark" ? (
            <MdLightMode className="w-5 h-5 text-[var(--color-text)]" />
          ) : (
            <MdDarkMode className="w-5 h-5 text-[var(--color-text)]" />
          )}
        </button>
      </div>

      {/* Chat history */}
      <div
        ref={chatHistoryRef}
        className="flex-1 min-h-0 p-4 overflow-y-auto flex flex-col"
      >
        {messages.length === 0 ? (
          <div className="relative flex h-full w-full items-center justify-center p-4 overflow-hidden">
            <div className="relative z-10 flex flex-col items-start gap-4">
              <div className="text-6xl font-extrabold text-black dark:text-slate-300">
                PolicyBot
              </div>

              <div className="text-lg text-slate-600 dark:text-slate-400">
                Your AI assistant for policy documents.
              </div>

              <div className="text-base text-slate-600 dark:text-slate-400">
                Select PDFs from the list and enter a question to get started.
              </div>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.type === "user" ? "justify-end" : "justify-start"
              } mb-2`}
            >
              {message.type === "user" ? (
                <HumanMessage content={message.content} />
              ) : (
                <AIMessage
                  content={message.content}
                  sourceChunks={message.sourceChunks}
                />
              )}
            </div>
          ))
        )}
      </div>
      {/* Chat input */}
      <ChatInput
        value={userInput}
        onChange={(e) => setUserInput(e.target.value)}
        onSend={handleSend}
        suggestedQuestions={suggestedQuestions}
        onSuggestionClick={handleSuggestionClick}
        disabled={loading || checkedPdfs.length === 0}
      />
      <div className="text-center px-4 text-[10px]">
        <p>
          PolicyBot responses can be inaccurate. Please double-check its
          responses.
        </p>
        <p>Developed By: N Gautam, Omir Kumar, and Dr. Sudarsun Santhiappan</p>
        <p> Policybot v2.0.0 </p>
      </div>
    </div>
  );
};

export default ChatSection;
