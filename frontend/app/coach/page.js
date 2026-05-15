"use client";

import { Bot, Send } from "lucide-react";
import { useState } from "react";

import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { streamCoachMessage } from "@/services/aiCoachService";
import { searchMemory } from "@/services/memoryService";

export default function CoachPage() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "I am online. Ask about training, meals, sleep, recovery, or what to do next today."
    }
  ]);
  const [input, setInput] = useState("");
  const [memoryQuery, setMemoryQuery] = useState("missed workout sleep protein consistency");
  const [memoryResults, setMemoryResults] = useState([]);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setMessages((current) => [...current, { role: "user", content: userMessage }]);
    setInput("");
    setLoading(true);

    try {
      const assistantIndex = Date.now();
      setMessages((current) => [...current, { id: assistantIndex, role: "assistant", content: "", streaming: true }]);
      let streamed = "";
      await streamCoachMessage(userMessage, {
        onToken: (token) => {
          streamed += token;
          setMessages((current) =>
            current.map((message) =>
              message.id === assistantIndex ? { ...message, content: streamed, streaming: true } : message
            )
          );
        },
        onMetadata: (metadata) => {
          setMessages((current) =>
            current.map((message) =>
              message.id === assistantIndex
                ? {
                    ...message,
                    content: metadata.message || streamed,
                    recommendations: metadata.recommendations,
                    memoriesUsed: metadata.memories_used,
                    confidence: metadata.confidence,
                    streaming: false
                  }
                : message
            )
          );
        }
      });
    } catch (error) {
      setMessages((current) => [...current, { role: "assistant", content: "I could not reach the coach service. Check the backend and try again." }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <ProtectedFeaturePage
      title="AI Coach"
      description="Memory-aware local coaching powered by agents, Qdrant retrieval, and structured dashboard context."
    >
      <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
        <section className="panel rounded-xl p-4">
          <div className="mb-4 flex items-center gap-2 text-sm text-muted">
            <Bot className="h-4 w-4 text-cyanGlow" />
            Coach agent {loading ? <span className="text-slate-400">is typing...</span> : null}
          </div>

          <div className="h-[420px] space-y-3 overflow-auto pr-2">
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`max-w-[86%] rounded-2xl p-3 text-sm ${
                  message.role === "user" ? "ml-auto bg-white text-slate-950" : "soft-panel text-slate-100"
                }`}
              >
                <p className="whitespace-pre-wrap leading-6">{message.content || (message.streaming ? "Thinking..." : "")}</p>
                {message.confidence ? <p className="mt-2 text-xs text-muted">Confidence {Math.round(message.confidence * 100)}%</p> : null}
                {message.recommendations?.length ? (
                  <div className="mt-3 space-y-2">
                    {message.recommendations.map((item) => (
                      <div key={item.title} className="rounded-xl border border-white/10 bg-[#0b0f17] p-2">
                        <p className="font-semibold">{item.title}</p>
                        <p className="text-xs opacity-80">{item.body}</p>
                      </div>
                    ))}
                  </div>
                ) : null}
              </div>
            ))}
          </div>

          <form className="mt-4 flex gap-3" onSubmit={handleSubmit}>
            <Input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Ask what to do next..." />
            <Button disabled={loading}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </section>

        <aside className="panel rounded-xl p-4">
          <h2 className="font-semibold">Memory search</h2>
          <p className="mt-2 text-sm text-muted">Inspect the same Qdrant memory layer the coach uses.</p>
          <div className="mt-4 flex gap-2">
            <Input value={memoryQuery} onChange={(event) => setMemoryQuery(event.target.value)} />
            <Button
              variant="secondary"
              onClick={async () => {
                setMemoryResults(await searchMemory(memoryQuery));
              }}
              type="button"
            >
              Search
            </Button>
          </div>

          <div className="mt-4 max-h-[420px] space-y-3 overflow-auto">
            {memoryResults.map((memory) => (
              <div key={memory.id} className="soft-panel rounded-xl p-3">
                <p className="text-sm">{memory.text}</p>
                <p className="mt-2 text-xs text-muted">
                  {memory.metadata?.event_type || memory.metadata?.source} - score {memory.score.toFixed(3)}
                </p>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </ProtectedFeaturePage>
  );
}
