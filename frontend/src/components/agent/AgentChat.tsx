import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";
import { Bot, Send, Sparkles } from "lucide-react";
import { Button } from "../common/Button";
import { ChatMessageBubble } from "./ChatMessage";
import type { ChatMessage } from "../../lib/types";

interface Props {
  messages: ChatMessage[];
  onSend: (text: string) => void;
  loading: boolean;
  disabled?: boolean;
  onDownloadPdf: () => void;
  pdfLoading?: boolean;
}

const SUGGESTIONS = [
  "Review Ozempic safety signals",
  "Why was suicidal ideation flagged?",
  "Compare Ozempic and Wegovy",
  "Generate a PDF",
];

export function AgentChat({ messages, onSend, loading, disabled, onDownloadPdf, pdfLoading }: Props) {
  const [text, setText] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const submit = (val?: string) => {
    const v = (val ?? text).trim();
    if (!v || loading || disabled) return;
    onSend(v);
    setText("");
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    submit();
  };

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="flex flex-col rounded-2xl border border-slate-200 bg-white shadow-glass overflow-hidden h-[72vh] min-h-[520px]">
      {/* Chat area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 sm:px-6 py-5 space-y-4 bg-gradient-to-b from-slate-50/40 to-white">
        {messages.length === 0 && <EmptyAgentState onPick={(s) => submit(s)} />}

        {messages.map((m) => (
          <ChatMessageBubble
            key={m.id}
            message={m}
            onDownloadPdf={onDownloadPdf}
            pdfLoading={pdfLoading}
          />
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-teal-500 text-white">
              <Bot className="h-4 w-4" />
            </div>
            <div className="rounded-2xl rounded-tl-sm border border-slate-200 bg-white px-4 py-3 shadow-sm">
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-brand-400 pulse-dot" />
                <span className="h-2 w-2 rounded-full bg-brand-400 pulse-dot" style={{ animationDelay: "0.2s" }} />
                <span className="h-2 w-2 rounded-full bg-brand-400 pulse-dot" style={{ animationDelay: "0.4s" }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Composer */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-slate-200 bg-white px-3 sm:px-4 py-3"
      >
        {messages.length > 0 && (
          <div className="hidden sm:flex flex-wrap gap-1.5 mb-2">
            {SUGGESTIONS.slice(0, 3).map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => submit(s)}
                disabled={loading || disabled}
                className="text-[11px] rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-slate-600 hover:bg-white hover:border-brand-300 hover:text-brand-700 disabled:opacity-50"
              >
                {s}
              </button>
            ))}
          </div>
        )}
        <div className="flex items-end gap-2">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKey}
            placeholder={disabled ? "Backend offline — agent unavailable" : "Ask the agent…"}
            rows={1}
            disabled={disabled || loading}
            className="flex-1 resize-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/30 disabled:bg-slate-100 max-h-40"
          />
          <Button
            type="submit"
            loading={loading}
            disabled={disabled || !text.trim()}
            icon={!loading ? <Send className="h-4 w-4" /> : undefined}
          >
            Send
          </Button>
        </div>
        <p className="mt-2 text-[10px] text-slate-400 flex items-center gap-1">
          <Sparkles className="h-3 w-3" />
          The agent uses deterministic FAERS + PubMed tools and does not provide medical advice.
        </p>
      </form>
    </div>
  );
}

function EmptyAgentState({ onPick }: { onPick: (s: string) => void }) {
  return (
    <div className="text-center py-8">
      <div className="mx-auto h-12 w-12 rounded-2xl bg-gradient-to-br from-brand-500 to-teal-500 flex items-center justify-center shadow-glow">
        <Bot className="h-6 w-6 text-white" />
      </div>
      <h3 className="mt-3 text-sm font-semibold text-slate-900">PharmaFind Agent</h3>
      <p className="mx-auto mt-1 max-w-md text-xs text-slate-500 leading-relaxed">
        Ask the agent to run reviews, explain flagged signals, compare drugs, or generate PDFs. The
        agent calls deterministic backend tools — it is not a medical advisor.
      </p>
      <div className="mt-4 mx-auto max-w-md grid grid-cols-1 sm:grid-cols-2 gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => onPick(s)}
            className="text-left text-xs rounded-xl border border-slate-200 bg-white px-3 py-2 hover:border-brand-300 hover:bg-brand-50/40 transition-colors text-slate-700"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
