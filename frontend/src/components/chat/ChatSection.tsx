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
import logo from "@/assets/logo.png";
import Iconone from "@/assets/cerai.png";
import Icontwo from "@/assets/iiit.png";
import Iconthree from "@/assets/wsai.png";
import SuggestedQuestions from "./SuggestedQuestions";


import { FiMenu } from "react-icons/fi";
import { useIsMobile } from "@/hooks/useIsMobile";
import { getPdfSummary, queryChat, getSuggestedQueries } from "@/lib/router";
import { useNotebookId } from "@/hooks/useNotebookId";


interface SourceChunk {
  text: string;
  source: string;
  page_number: number | null;
}

interface Message {
  type: "user" | "ai";
  content: string;
  sourceChunks?: SourceChunk[];
  loadingType?: "thinking" | "summary";
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
  onOpenSidebar?: () => void;
  onAttach?: () => void;
}

const ChatSection: React.FC<ChatSectionProps> = ({ checkedPdfs, sources, onOpenSidebar, onAttach }) => {
  console.log("Sources in ChatSection:", sources);

  const notebookId = useNotebookId();

  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState("");
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
  const hasConversationStarted = messages.length > 0;
 

  const isMobile = useIsMobile();



  const inputPlaceholder =
  checkedPdfs.length > 0
    ? "Ask a question from the source doc"
    : "Select a source to continue";

const isSummaryMode =
  messages.length === 1 &&
  messages[0].type === "ai" &&
  !messages.some((m) => m.type === "user");



useEffect(() => {
  setSuggestedQuestions([]);

  if (checkedPdfs.length === 1) {
    generateSummary(checkedPdfs[0]);
   
  }
}, [checkedPdfs]);



const generateSummary = async (filename: string) => {
  setMessages([
    {
      type: "ai",
      content: "",
      sourceChunks: [],
      loadingType: "summary",
    },
  ]);

  setLoading(true);

  try {
    const res = await getPdfSummary(notebookId, filename);

    setMessages([
      {
        type: "ai",
        content: res.summary,
        sourceChunks: [],
      },
    ]);

    // ✅ Fetch suggestions AFTER summary is set
    await fetchSuggestedQuestions(filename);

  } catch (error) {
    console.error("Failed to fetch PDF summary:", error);

    setMessages([
      {
        type: "ai",
        content: "❌ Failed to generate summary for this document.",
        sourceChunks: [],
      },
    ]);
  } finally {
    setLoading(false);
  }
};


  
  function getOrCreateSessionId() {
    const newSessionId = uuidv4();
    // localStorage.setItem("sessionId", newSessionId);
    return newSessionId;
  }



const streamAIResponse = async (fullText: string) => {
  const words = fullText.split(" ");
  let currentText = "";

  const chunkSize = 6; // smoother chunk streaming

  for (let i = 0; i < words.length; i += chunkSize) {
    currentText += words.slice(i, i + chunkSize).join(" ") + " ";

    setMessages((prev) => {
      const newMessages = [...prev];
      const lastIdx = newMessages.length - 1;

      if (newMessages[lastIdx].type === "ai") {
        newMessages[lastIdx] = {
          ...newMessages[lastIdx],
          content: currentText,
          loadingType: "thinking",
        };
      }

      return newMessages;
    });

    await new Promise((resolve) => setTimeout(resolve, 120));
  }

  // Remove blinking cursor when done
  setMessages((prev) => {
    const newMessages = [...prev];
    const lastIdx = newMessages.length - 1;

    if (newMessages[lastIdx].type === "ai") {
      newMessages[lastIdx] = {
        ...newMessages[lastIdx],
        loadingType: undefined,
      };
    }

    return newMessages;
  });

  setTimeout(() => {
  if (chatHistoryRef.current) {
    chatHistoryRef.current.scrollTo({
      top: chatHistoryRef.current.scrollHeight,
      behavior: "smooth",
    });
  }
}, 100);

};

 const handleSend = async (overrideQuery?: string) => {

    console.log("handleSend called with input:", userInput.trim());
    if (loading) {
      // Optionally show a message: "Please wait for the current response."
      return;
    }
   if (checkedPdfs.length === 0) {
  if (!userInput.trim()) return;

  const humanMessage = { type: "user" as const, content: userInput.trim() };

  if (!overrideQuery) {
  setUserInput("");
}


  setMessages((prev) => [
    ...prev,
    humanMessage,
    {
      type: "ai",
      content:
        "⚠️ No sources selected.\n\nPlease select at least one document from the left sidebar to generate a response.",
      sourceChunks: [],
    },
  ]);

  return;
}

    
const query = overrideQuery ?? userInput.trim();

if (query) {

        const humanMessage = { 
    type: "user" as const, 
    content: query 
  };
    if (!overrideQuery) {
    setUserInput("");
  }
      // Add user message and placeholder AI message with loader
      setMessages((prev) => [
        ...prev,
        humanMessage,
        { type: "ai", content: "", sourceChunks: [] }, // Loader placeholder
      ]);
    try {
  setLoading(true);


const res = await queryChat({
  query,
  session_id: sessionId,
  notebook_id: notebookId,
  pdfs: checkedPdfs, // ✅ REQUIRED
});

if ("error" in res) {
  // Backend returned an error response
  setMessages((prev) => {
    const newMessages = [...prev];
    const lastIdx = newMessages.length - 1;

    if (newMessages[lastIdx].type === "ai") {
      newMessages[lastIdx] = {
        ...newMessages[lastIdx],
        content: res.error,
        sourceChunks: res.context_chunks || [],
      };
    }

    return newMessages;
  });

  setLoading(false);
  return;
}

await streamAIResponse(res.response);

setMessages((prev) => {
  const newMessages = [...prev];
  const lastIdx = newMessages.length - 1;

  if (newMessages[lastIdx].type === "ai") {
    newMessages[lastIdx] = {
      ...newMessages[lastIdx],
      sourceChunks: res.context_chunks,
    };
  }

  return newMessages;
});



  setLoading(false);
}
 catch (error) {
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

const fetchSuggestedQuestions = async (filename: string) => {
  try {
    const res = await getSuggestedQueries(notebookId, [filename]);

    if ("error" in res) {
      console.error("Failed to fetch suggested questions:", res.error);
      setSuggestedQuestions([]);
      return;
    }

    setSuggestedQuestions(res.suggested_queries || []);
  } catch (err) {
    console.error("Error fetching suggestions:", err);
    setSuggestedQuestions([]);
  }
};



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
     chatHistoryRef.current.scrollTo({
  top: chatHistoryRef.current.scrollHeight,
  behavior: "smooth",
});

    }
  }, [messages]);



  return (
    <div
      id="chat-section"
      className="relative flex flex-col h-full min-h-0 overflow-hidden bg-[#FFFFFF]"
    >
      {/* ChatSection Topbar - icons/navbar (placed above messages so messages render below) */}

      {/* MOBILE TOPBAR */}
{isMobile && (
  <div className="h-14 px-4 pt-2 flex items-center justify-between  bg-white">
    <div className="flex items-center gap-3">
     <button
  aria-label="menu"
  onClick={onOpenSidebar}
  className="p-1"
>
  <FiMenu size={22} className="text-slate-800" />
</button>


      <img
        src={logo.src}
        alt="PolicyBot"
        className="h-5 w-auto"
      />
    </div>

    <div className="flex items-center gap-3 border border-black/20 rounded-md px-3 py-2">
    <a
    href="https://cerai.iitm.ac.in/"
    target="_blank"
    rel="noopener noreferrer"
  >
    <img
      alt="CeRAI"
      src={Iconone.src}
      className="h-4 w-auto cursor-pointer transition duration-300 hover:scale-110"
    />
  </a>

  <a
    href="https://www.iitm.ac.in/"
    target="_blank"
    rel="noopener noreferrer"
  >
    <img
      alt="IITM"
      src={Icontwo.src}
      className="h-4 w-4 cursor-pointer transition duration-300 hover:scale-110"
    />
  </a>

  <a
    href="https://wsai.iitm.ac.in/"
    target="_blank"
    rel="noopener noreferrer"
  >
    <img
      alt="WSAI"
      src={Iconthree.src}
      className="h-4 w-4 cursor-pointer transition duration-300 hover:scale-110"
    />
  </a>

    </div>
    
  </div>
)}


{!isMobile && (
<div
  id="chat-topbar"
  className="flex items-center justify-end px-4 py-2 bg-[#FFFFFF] z-10"
>
  {/* Model selector dropdown */}
  {isAdmin && availableModels.length > 0 && (
    <ModelSelector
      models={availableModels}
      selected={selectedModel}
      onChange={handleModelChange}
    />
  )}

  {/* === New Figma Design Container === */}
  <div className="ml-2">
 
  <div className="flex items-center justify-between w-[208px] h-[64px] px-4 rounded-[10px] border border-black/20">
    
    {/* Logo */}
  <a
    href="https://cerai.iitm.ac.in/"
    target="_blank"
    rel="noopener noreferrer"
  >
    <img
      src={Iconone.src}
      alt="CeRAI"
      className="h-7 w-auto object-contain cursor-pointer transition duration-300 hover:scale-110"
    />
  </a>

    {/* Right Icons */}
    <div className="flex items-center gap-3">
      
    

        <a
      href="https://www.iitm.ac.in/"
      target="_blank"
      rel="noopener noreferrer"
    >
      <img
        src={Icontwo.src}
        alt="IITM"
        className="h-7 w-7 object-contain cursor-pointer transition duration-300 hover:scale-110"
      />
    </a>
          <a
      href="https://wsai.iitm.ac.in/"
      target="_blank"
      rel="noopener noreferrer"
    >
      <img
        src={Iconthree.src}
        alt="WSAI"
        className="h-7 w-7 object-contain cursor-pointer transition duration-300 hover:scale-110"
      />
    </a>

    </div>

  </div>
 


  </div>

  {/* ================= COMMENTED OLD BUTTONS ================= */}

  {/*
  <a
    href="https://github.com/cerai-iitm/policybot"
    target="_blank"
    rel="noopener noreferrer"
    aria-label="Open PolicyBot on GitHub"
    className="flex items-center rounded-md p-1 hover:bg-bg-dark"
  >
    <FaGithubSquare className="w-6 h-6 text-[var(--color-text)]" />
  </a>
  */}

  {/*
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
  */}

</div>
)}


   
{/* Chat history */}
<div
  ref={chatHistoryRef}
className={`flex-1 min-h-0 transition-all duration-500 ${
  hasConversationStarted
    ? `overflow-y-auto custom-scrollbar ${
        isMobile ? "px-4 pt-4 pb-36" : "pt-4"
      }`
    : "flex items-center justify-center px-4"
}`}


>


  {/* ⭐ Centered Chat Column */}
 <div
  className={`w-full max-w-[760px] mx-auto flex flex-col ${
    !hasConversationStarted ? "flex-1 justify-center" : ""
  }`}
>


    {!hasConversationStarted && (
      <div className="flex flex-col items-center gap-6 w-full transition-all duration-700 ease-in-out">

      <div className="max-w-[547px] w-full text-center px-4">
  <div className="text-slate-900 font-semibold font-dm leading-tight
                  text-2xl sm:text-3xl">
    Welcome to PolicyBot
  </div>

  <div className="text-slate-600 font-normal font-inter tracking-tight mt-2
                  text-sm sm:text-base leading-6 sm:leading-8">
    Making government policy and legal documents easier to understand
  </div>
</div>


        {/* CENTER INPUT */}
        <ChatInput
        placeholder={inputPlaceholder}
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onSend={handleSend}
          
          disabled={loading || checkedPdfs.length === 0}
          selectedCount={checkedPdfs.length}  
          onOpenSidebar={onOpenSidebar}   // ✅ ADD
          onAttach={onAttach}
        />

      </div>
    )}

   {hasConversationStarted && (
  <>
    {messages.map((message, index) => (
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
            loadingType={message.loadingType}
          />
        )}
      </div>
    ))}

    {/* ✅ Suggested Questions appear ONLY after summary */}
    {isSummaryMode && suggestedQuestions.length > 0 && (
      <SuggestedQuestions
        questions={suggestedQuestions}
onSelect={(question) => {
  handleSend(question);
}}
      />
    )}
  </>
)}


  </div>
</div>


      {/* Chat input */}
{hasConversationStarted && (
  <div
    className={`
      w-full
      ${isMobile
        ? "fixed bottom-0 left-0 z-30 bg-white pb-[env(safe-area-inset-bottom)]"
        : "relative max-w-3xl mx-auto"}
    `}
  >
    <ChatInput
      placeholder={inputPlaceholder}
      value={userInput}
      onChange={(e) => setUserInput(e.target.value)}
      onSend={handleSend}
     
      disabled={loading || checkedPdfs.length === 0}
      selectedCount={checkedPdfs.length}
      onOpenSidebar={onOpenSidebar}   // ✅ ADD
      onAttach={onAttach}
    />
  </div>
)}



{/* Footer */}
{(!isMobile || (isMobile && !hasConversationStarted)) && (
  <div className="text-center px-4">
    <div className="text-slate-950 text-[10px] sm:text-[12px] font-normal font-inter leading-4 pb-4">
      Developed by: N Gautam, S Raji, Omir Kumar, and Dr. Sudarsun Santhiappan
    </div>
  </div>
)}


    </div>
  );
};

export default ChatSection;
