"use_client";
import React, { useState, useRef, useEffect } from "react";
import HumanMessage from "./HumanMessage";
import AIMessage from "./AIMessage";
import ChatInput from "./ChatInput";

interface Message {
  type: "user" | "ai";
  content: string;
}

interface ChatSectionProps {
  checkedPdfs: string[];
}

const ChatSection: React.FC<ChatSectionProps> = ({ checkedPdfs }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState("");
  const [warning, setWarning] = useState("");

  const [sourceSummary, setSourceSummary] = useState<string>("");
  const [loadingSummary, setLoadingSummary] = useState<boolean>(false);
  const chatHistoryRef = useRef<HTMLDivElement>(null);

  const handleSend = async () => {
    console.log("handleSend called with input:", userInput.trim()); // Add here
    if (checkedPdfs.length === 0) {
      setWarning("Please select at least one PDF before sending a query.");
      return;
    }
    setWarning("");
    if (userInput.trim()) {
      const humanMessage = { type: "user" as const, content: userInput.trim() };
      const aiMessage = { type: "ai" as const, content: "" };
      const query = userInput.trim();

      setUserInput("");
      setMessages((prev) => [...prev, humanMessage, aiMessage]);
      try {
        console.log("Sending request with PDFs:", checkedPdfs); // Add here
        const response = await fetch("http://localhost:8000/api/query", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: query, pdfs: checkedPdfs }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error("No response body");
        }

        const decoder = new TextDecoder();
        let buffer = "";
        let fullResponse = "";
        let isDone = false;

        while (!isDone) {
          try {
            const { done, value } = await reader.read();
            if (done) break; // Natural end of stream

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n\n");
            buffer = lines.pop() || "";

            for (const line of lines) {
              if (line.startsWith("data: ")) {
                const data = JSON.parse(line.slice(6));
                fullResponse += data.partial;
                setMessages((prev) => {
                  const newMessages = [...prev];
                  const lastMessage = newMessages[newMessages.length - 1];
                  if (lastMessage.type === "ai") {
                    lastMessage.content = fullResponse;
                  }
                  return newMessages;
                });

                if (data.done) {
                  isDone = true;
                  break;
                }
              }
            }
          } catch (readError) {
            // Handle read errors gracefully, but don't treat as fatal if done
            console.warn("Read error:", readError);
            break;
          }
        }

        // Only set error if no response was received
        if (!fullResponse.trim()) {
          throw new Error("No response received");
        }
      } catch (error) {
        console.error("Stream error:", error);
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage.type === "ai") {
            lastMessage.content = "Error: Failed to get response.";
          }
          return newMessages;
        });
      }
    }
  };

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    if (messages.length === 0) {
      setLoadingSummary(true);
      fetch("/api/sources-summary")
        .then((res) => res.json())
        .then((data) => {
          setSourceSummary(data.explanation);
          setLoadingSummary(false);
        })
        .catch(() => setLoadingSummary(false));
    }
  }, [messages.length]);

  return (
    <div className="flex flex-col h-full bg-white">
      {warning && <div className="text-red-500">{warning}</div>}
      {/* Chat history */}
      <div
        ref={chatHistoryRef}
        className="flex-1 p-4 overflow-y-auto flex flex-col"
      >
        {messages.length === 0 ? (
          <div className="text-gray-500 p-4">
            {loadingSummary
              ? "Loading summary..."
              : sourceSummary || "No summary available."}
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
                <AIMessage content={message.content} />
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
      />
      <div className="text-center px-4 text-[10px]">
        <p>
          PolicyBot responses can be inaccurate. Please double-check its
          responses.
        </p>
        <p>Done By: N Gautam, Sudarsun Santhiappan, Omir Kumar</p>
      </div>
    </div>
  );
};

export default ChatSection;
