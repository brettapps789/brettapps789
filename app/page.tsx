"use client";

import { useState, useRef, useEffect, useMemo } from "react";
import { Send, Bot, User, Loader2, LayoutTemplate, Code, Crown } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ProjectStatus {
  project: string;
  phase: string;
  agent: string;
  status: string;
}

const PHASE_LABELS: Record<string, string> = {
  "0": "Idle",
  "1": "Intelligence & Strategy",
  "2": "Content Creation",
  "3": "Design & Production",
  "4": "Web & Conversion",
  "5": "Deployment & Optimisation",
};

const STATUS_COLORS: Record<string, string> = {
  "processing": "bg-amber-100 text-amber-800 border-amber-300",
  "waiting for approval": "bg-blue-100 text-blue-800 border-blue-300",
  "complete": "bg-emerald-100 text-emerald-800 border-emerald-300",
};

function parseProjectStatus(content: string): ProjectStatus | null {
  const match = content.match(
    /Project:\s*([^|\n]+?)\s*\|\s*Phase:\s*([^|\n]+?)\s*\|\s*Current Agent:\s*([^|\n]+?)\s*\|\s*Status:\s*([^\n]+)/i
  );
  if (!match) return null;
  return {
    project: match[1].trim(),
    phase: match[2].trim(),
    agent: match[3].trim(),
    status: match[4].trim(),
  };
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Project: No Active Project | Phase: 0 | Current Agent: Sovereign Orchestrator | Status: Waiting for Approval\n\nG'day! I'm the **AAW Sovereign Orchestrator** — your Project Manager and COO for **Fair Dinkum Publishing**. 🇦🇺\n\nI lead a workforce of **14 specialised AI agents** that will take your raw ebook idea and turn it into a live, revenue-generating digital asset — no worries!\n\n**The Sovereign Workflow covers 5 phases:**\n1. 🔍 Intelligence & Strategy (Research → Market Analysis)\n2. ✍️ Content Creation (Writing → Editing → Fact-Checking)\n3. 🎨 Design & Production (Design → Formatting / EPUB)\n4. 🌐 Web & Conversion (Web Dev → SEO → Integrations)\n5. 🚀 Deployment & Optimisation (Deploy → CI/CD → Testing → Analytics)\n\n**To kick off the Sovereign Workflow**, just tell me your ebook idea — e.g., *I want to write an ebook about sustainable gardening in the Australian Outback.*",
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

  const projectStatus = useMemo<ProjectStatus | null>(() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      const msg = messages[i];
      if (msg.role === "assistant") {
        const status = parseProjectStatus(msg.content);
        if (status) return status;
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
        headers: { "Content-Type": "application/json" },
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

  const statusKey = projectStatus?.status.toLowerCase() ?? "";
  const statusColor =
    STATUS_COLORS[statusKey] ?? "bg-gray-100 text-gray-700 border-gray-300";
  const phaseLabel = projectStatus
    ? PHASE_LABELS[projectStatus.phase] ?? `Phase ${projectStatus.phase}`
    : null;

  return (
    <div className="flex h-screen bg-gray-50 font-sans">
      {/* Left Pane: Chat */}
      <div className="flex flex-col w-full lg:w-1/2 border-r border-gray-200 bg-white">
        {/* Header */}
        <header className="bg-gradient-to-r from-green-800 to-yellow-700 px-6 py-4 flex items-center justify-between sticky top-0 z-10 shadow-md">
          <div className="flex items-center gap-3">
            <div className="bg-yellow-400 p-2 rounded-lg">
              <Crown className="w-5 h-5 text-green-900" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">
                AAW Sovereign Orchestrator
              </h1>
              <p className="text-sm text-yellow-200">
                Fair Dinkum Publishing · 14-Agent Workflow
              </p>
            </div>
          </div>
        </header>

        {/* Project Status Dashboard */}
        {projectStatus && (
          <div className="bg-white border-b border-gray-200 px-6 py-3">
            <div className="flex flex-wrap items-center gap-3 text-sm">
              <span className="font-semibold text-gray-800 truncate max-w-[180px]">
                📚 {projectStatus.project}
              </span>
              <span className="text-gray-400">|</span>
              {phaseLabel && (
                <span className="text-gray-600">
                  <span className="font-medium">Phase {projectStatus.phase}:</span>{" "}
                  {phaseLabel}
                </span>
              )}
              <span className="text-gray-400">|</span>
              <span className="text-gray-600">
                🤖 <span className="font-medium">{projectStatus.agent}</span>
              </span>
              <span className="text-gray-400">|</span>
              <span
                className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${statusColor}`}
              >
                {projectStatus.status}
              </span>
            </div>
            {/* Phase Progress Bar */}
            {projectStatus.phase !== "0" && (
              <div className="mt-2 flex gap-1">
                {[1, 2, 3, 4, 5].map((p) => {
                  const phaseNum = parseInt(projectStatus.phase, 10);
                  const isActive = p === phaseNum;
                  const isDone = p < phaseNum;
                  return (
                    <div
                      key={p}
                      className={`h-1.5 flex-1 rounded-full transition-all ${
                        isDone
                          ? "bg-emerald-500"
                          : isActive
                          ? "bg-yellow-500"
                          : "bg-gray-200"
                      }`}
                      title={PHASE_LABELS[String(p)]}
                    />
                  );
                })}
              </div>
            )}
          </div>
        )}

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
                      : "bg-yellow-100 text-yellow-700"
                  }`}
                >
                  {message.role === "user" ? (
                    <User className="w-5 h-5" />
                  ) : (
                    <Crown className="w-5 h-5" />
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
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-yellow-100 text-yellow-700 flex items-center justify-center">
                  <Crown className="w-5 h-5" />
                </div>
                <div className="bg-white border border-gray-200 px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm flex items-center gap-2 text-gray-500">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Orchestrating the workforce...</span>
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
              className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-full px-2 py-2 focus-within:ring-2 focus-within:ring-yellow-500 focus-within:border-transparent transition-all"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Tell me your ebook idea or type APPROVE / REVISE / PIVOT..."
                className="flex-1 bg-transparent border-none focus:ring-0 px-4 py-2 text-gray-900 placeholder-gray-500 outline-none"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="bg-green-800 hover:bg-green-700 text-white p-2.5 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0"
              >
                <Send className="w-5 h-5" />
              </button>
            </form>
            <div className="text-center mt-3">
              <p className="text-xs text-gray-400">
                Sovereign Workflow · 14 agents ·{" "}
                <code className="bg-gray-100 px-1 py-0.5 rounded">
                  compile_epub
                </code>{" "}
                ·{" "}
                <code className="bg-gray-100 px-1 py-0.5 rounded">
                  GitHub Pages
                </code>{" "}
                ·{" "}
                <code className="bg-gray-100 px-1 py-0.5 rounded">
                  project_state.json
                </code>
              </p>
            </div>
          </div>
        </footer>
      </div>

      {/* Right Pane: Live Preview */}
      <div className="hidden lg:flex flex-col w-1/2 bg-white">
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-2 sticky top-0 z-10">
          <LayoutTemplate className="w-5 h-5 text-gray-500" />
          <h2 className="text-lg font-semibold text-gray-900 tracking-tight">
            Live Preview
          </h2>
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
              <p className="text-lg font-medium text-gray-500">
                No preview available
              </p>
              <p className="text-sm mt-2">
                When the Web Dev Agent builds the landing page, it will appear
                here.
              </p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
