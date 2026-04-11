"use client";

import { useState, useRef, useEffect, useMemo } from "react";
import { Send, FileText, Bot, User, Loader2, FolderOpen, LayoutTemplate, Code } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I am the Ebook Building AI Agent Workforce. I can help you write, compile, and publish EPUB ebooks. I can also create GitHub repositories, generate landing pages linked to brettapps.com, and host them on GitHub Pages. Need help with marketing or monetization? I can hand off to my Market Research, Advertising, and Stripe Agents! What would you like to do today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Extract the latest HTML code block from the assistant's messages
  const latestHtml = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      const msg = messages[i];
      if (msg.role === "assistant") {
        const match = msg.content.match(/```html\s*\n([\s\S]*?)(?:```|$)/);
        if (match) return match[1];
      }
    }
    return null;
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: userMessage }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || "Failed to fetch response");
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastIndex = newMessages.length - 1;
          newMessages[lastIndex] = {
            ...newMessages[lastIndex],
            content: newMessages[lastIndex].content + chunk,
          };
          return newMessages;
        });
      }
    } catch (error: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `**Error:** ${error.message}\n\n*(Make sure you have set the \`OPENAI_API_KEY\` environment variable in the Settings panel)*`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 font-sans">
      {/* Left Pane: Chat */}
      <div className="flex flex-col w-full lg:w-1/2 border-r border-gray-200 bg-white">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <div className="bg-blue-100 p-2 rounded-lg">
              <FolderOpen className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900 tracking-tight">
                Ebook Building AI Agent Workforce
              </h1>
              <p className="text-sm text-gray-500">
                Powered by OpenAI Agents SDK, MCP, and Multi-Agent Handoffs
              </p>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 bg-gray-50">
          <div className="max-w-3xl mx-auto space-y-6">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-4 ${
                message.role === "user" ? "flex-row-reverse" : ""
              }`}
            >
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-emerald-100 text-emerald-600"
                }`}
              >
                {message.role === "user" ? (
                  <User className="w-5 h-5" />
                ) : (
                  <Bot className="w-5 h-5" />
                )}
              </div>
              <div
                className={`flex flex-col max-w-[80%] ${
                  message.role === "user" ? "items-end" : "items-start"
                }`}
              >
                <div
                  className={`px-4 py-3 rounded-2xl ${
                    message.role === "user"
                      ? "bg-blue-600 text-white rounded-tr-sm"
                      : "bg-white border border-gray-200 text-gray-800 rounded-tl-sm shadow-sm"
                  }`}
                >
                  {message.role === "user" ? (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  ) : (
                    <div className="prose prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-gray-50 prose-pre:text-gray-800 prose-pre:border prose-pre:border-gray-200">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center">
                <Bot className="w-5 h-5" />
              </div>
              <div className="bg-white border border-gray-200 px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm flex items-center gap-2 text-gray-500">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Agent is thinking and reading files...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

        {/* Input Area */}
        <footer className="bg-white border-t border-gray-200 p-4">
          <div className="max-w-3xl mx-auto">
            <form
              onSubmit={handleSubmit}
              className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-full px-2 py-2 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent transition-all"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask me to build an EPUB, research the market, or add a Stripe Buy button..."
                className="flex-1 bg-transparent border-none focus:ring-0 px-4 py-2 text-gray-900 placeholder-gray-500 outline-none"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="bg-blue-600 hover:bg-blue-700 text-white p-2.5 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0"
              >
                <Send className="w-5 h-5" />
              </button>
            </form>
            <div className="text-center mt-3">
              <p className="text-xs text-gray-400">
                The agent uses <code className="bg-gray-100 px-1 py-0.5 rounded">server-filesystem</code>, <code className="bg-gray-100 px-1 py-0.5 rounded">server-github</code>, and <code className="bg-gray-100 px-1 py-0.5 rounded">compile_epub</code>.
              </p>
            </div>
          </div>
        </footer>
      </div>

      {/* Right Pane: Live Preview */}
      <div className="hidden lg:flex flex-col w-1/2 bg-white">
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-2 sticky top-0 z-10">
          <LayoutTemplate className="w-5 h-5 text-gray-500" />
          <h2 className="text-lg font-semibold text-gray-900 tracking-tight">Live Preview</h2>
        </header>
        <main className="flex-1 bg-gray-100 relative">
          {latestHtml ? (
            <iframe
              srcDoc={latestHtml}
              className="w-full h-full border-none bg-white"
              title="Live Preview"
              sandbox="allow-scripts allow-same-origin"
            />
          ) : (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400 p-8 text-center">
              <Code className="w-12 h-12 mb-4 text-gray-300" />
              <p className="text-lg font-medium text-gray-500">No preview available</p>
              <p className="text-sm mt-2">Ask the agent to code an HTML page to see it rendered here.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
