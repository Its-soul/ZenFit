import React, { useState } from 'react';
import { 
  X, 
  Sparkles, 
  Send, 
  Bot, 
  User, 
  Loader2, 
  HelpCircle,
  Flame,
  Zap
} from 'lucide-react';

interface AICoachDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AICoachDrawer: React.FC<AICoachDrawerProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<{ sender: 'ai' | 'user'; text: string }[]>([
    {
      sender: 'ai',
      text: "Namaste & Welcome! I am ZenFit AI, your bio-performance coach. Ask me about muscle recovery, workout tweaks, or macro targets!",
    },
  ]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);

  if (!isOpen) return null;

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSending) return;

    const userText = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { sender: 'user', text: userText }]);
    setIsSending(true);

    try {
      const res = await fetch('/api/ai/ask-coach', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userQuery: userText }),
      });

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { sender: 'ai', text: data.reply || 'Stay dedicated to your daily habits!' },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: 'ai', text: 'Error connecting to ZenFit AI. Ensure your network or GEMINI_API_KEY is configured.' },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const sampleQuestions = [
    'How do I accelerate muscle recovery after heavy leg day?',
    'What should my pre-workout macro ratio be?',
    'How does HRV impact my strength output today?',
  ];

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-96 bg-slate-900/95 border-l border-slate-800/80 backdrop-blur-2xl z-50 flex flex-col shadow-2xl animate-fade-in">
      {/* Header */}
      <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-400 to-teal-500 flex items-center justify-center text-slate-950 font-black shadow-md shadow-emerald-500/20">
            <Sparkles className="w-5 h-5 fill-slate-950" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-1.5">
              <span>ZenFit AI Coach</span>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            </h3>
            <p className="text-[10px] text-slate-400">Sports Science Neural Advisor</p>
          </div>
        </div>

        <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-slate-200">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-2.5 ${m.sender === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div
              className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                m.sender === 'user'
                  ? 'bg-emerald-400 text-slate-950'
                  : 'bg-slate-800 text-emerald-400 border border-emerald-500/30'
              }`}
            >
              {m.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div
              className={`p-3 rounded-2xl text-xs leading-relaxed max-w-[80%] ${
                m.sender === 'user'
                  ? 'bg-emerald-500/20 text-emerald-100 border border-emerald-500/30'
                  : 'bg-slate-950/80 text-slate-200 border border-slate-800'
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}

        {isSending && (
          <div className="flex items-center gap-2 text-xs text-emerald-400 p-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>AI Coach is analyzing...</span>
          </div>
        )}
      </div>

      {/* Sample Quick Questions */}
      <div className="p-3 border-t border-slate-800/60 bg-slate-950/40 space-y-1">
        <span className="text-[10px] font-bold uppercase text-slate-500 block px-1">Suggested Prompts</span>
        <div className="space-y-1">
          {sampleQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => setInput(q)}
              className="w-full text-left p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-[11px] text-slate-300 truncate border border-slate-800"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSend} className="p-3 border-t border-slate-800/80 flex items-center gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask AI Coach..."
          className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
        />
        <button
          type="submit"
          disabled={isSending}
          className="p-2 rounded-xl bg-emerald-400 hover:bg-emerald-300 text-slate-950 font-bold transition-all disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
