"use client";

import { Bot, Send, Sparkles } from "lucide-react";
import { useState } from "react";

import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { streamCoachMessage } from "@/services/aiCoachService";

const QUICK_ACTIONS = ["I'm tired today", "What should I eat?", "Adjust my workout", "How am I doing?", "Motivate me"];

export default function CoachPage() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "How are you feeling today? I can help you adjust your workout, choose your next meal, or find one small win."
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage(text) {
    const userMessage = text.trim();
    if (!userMessage) return;

    setMessages((current) => [...current, { role: "user", content: userMessage }]);
    setInput("");
    setLoading(true);

    const assistantId = Date.now();
    setMessages((current) => [...current, { id: assistantId, role: "assistant", content: "", streaming: true }]);

    let streamed = "";
    try {
      await streamCoachMessage(userMessage, {
        onToken: (token) => {
          streamed += token;
          setMessages((current) => current.map((message) => (message.id === assistantId ? { ...message, content: streamed } : message)));
        },
        onMetadata: (metadata) => {
          setMessages((current) =>
            current.map((message) =>
              message.id === assistantId
                ? { ...message, content: metadata.message || streamed, recommendations: metadata.recommendations, streaming: false }
                : message
            )
          );
        }
      });
    } catch {
      setMessages((current) =>
        current.map((message) =>
          message.id === assistantId
            ? { ...message, content: "I’m having trouble replying, but you can still win today with a short walk, water, and one protein-forward meal.", streaming: false }
            : message
        )
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <ProtectedFeaturePage
      title="Coach"
      description="Warm, practical guidance when you need help choosing the next right step."
    >
      <div className="grid gap-5 lg:grid-cols-[1fr_300px]">
        <section className="panel rounded-[1.5rem] p-4">
          <div className="mb-4 flex items-center gap-2 text-sm text-muted">
            <Bot className="h-4 w-4 text-zenSage" />
            {loading ? "Coach is thinking..." : "Ready for today’s session?"}
          </div>

          <div className="h-[460px] space-y-3 overflow-auto pr-2">
            {messages.map((message, index) => (
              <div
                key={message.id || `${message.role}-${index}`}
                className={`max-w-[88%] rounded-3xl p-4 text-sm ${
                  message.role === "user" ? "ml-auto bg-zenCream text-[#121711]" : "soft-panel text-slate-100"
                }`}
              >
                <p className="whitespace-pre-wrap leading-6">{message.content || "Thinking about your best next step..."}</p>
                {message.recommendations?.length ? (
                  <div className="mt-3 space-y-2">
                    {message.recommendations.slice(0, 2).map((item) => (
                      <div key={item.title} className="rounded-2xl border border-white/10 bg-[#0d120e] p-3">
                        <p className="font-semibold">{item.title}</p>
                        <p className="mt-1 text-xs leading-5 text-muted">{item.body}</p>
                      </div>
                    ))}
                  </div>
                ) : null}
              </div>
            ))}
          </div>

          <form
            className="mt-4 flex gap-3"
            onSubmit={(event) => {
              event.preventDefault();
              sendMessage(input);
            }}
          >
            <Input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Need help adjusting today?" />
            <Button disabled={loading}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </section>

        <aside className="panel rounded-[1.5rem] p-4">
          <div className="rounded-3xl bg-zenCream p-4 text-[#121711]">
            <Sparkles className="h-5 w-5" />
            <p className="mt-3 font-semibold">Ask for the kind of help you need.</p>
            <p className="mt-2 text-sm leading-6 text-slate-700">ZenFit keeps answers short, supportive, and focused on today.</p>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {QUICK_ACTIONS.map((prompt) => (
              <button
                key={prompt}
                onClick={() => sendMessage(prompt)}
                className="rounded-full border border-white/10 px-3 py-2 text-xs text-slate-200 transition hover:border-zenSage hover:text-white"
              >
                {prompt}
              </button>
            ))}
          </div>
        </aside>
      </div>
    </ProtectedFeaturePage>
  );
}
