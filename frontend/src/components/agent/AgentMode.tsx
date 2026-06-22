import { useState } from "react";
import { Bot, ShieldAlert } from "lucide-react";
import { Card, CardBody, CardHeader, CardSubtle, CardTitle } from "../common/Card";
import { ErrorAlert } from "../common/ErrorAlert";
import { Badge } from "../common/Badge";
import { AgentChat } from "./AgentChat";
import {
  ApiError,
  agentChat,
  downloadAgentPdf,
  triggerBlobDownload,
} from "../../lib/api";
import type { ChatMessage } from "../../lib/types";
import { isLlmCreditError, uid } from "../../lib/utils";

interface Props {
  backendOnline: boolean;
}

export function AgentMode({ backendOnline }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentUnavailable, setAgentUnavailable] = useState(false);

  const handleSend = async (text: string) => {
    const userMsg: ChatMessage = {
      id: uid(),
      role: "user",
      content: text,
      timestamp: Date.now(),
    };
    setMessages((m) => [...m, userMsg]);
    setLoading(true);
    setError(null);

    try {
      const res = await agentChat({ message: text });
      const agentMsg: ChatMessage = {
        id: uid(),
        role: "agent",
        content: res.answer || "_(no response)_",
        meta: {
          last_drug_name: res.last_drug_name ?? null,
          last_pdf_path: res.last_pdf_path ?? null,
        },
        timestamp: Date.now(),
      };
      setMessages((m) => [...m, agentMsg]);
      setAgentUnavailable(false);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : (e as Error).message;
      if (isLlmCreditError(msg) || (e instanceof ApiError && e.status && e.status >= 500)) {
        setAgentUnavailable(true);
        setError(
          "Agent mode requires the backend LLM configuration. You can still use deterministic review mode."
        );
      } else {
        setError(msg);
      }
      setMessages((m) => [
        ...m,
        {
          id: uid(),
          role: "system",
          content: "The agent could not respond to that message.",
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadAgentPdf = async () => {
    setPdfLoading(true);
    try {
      const blob = await downloadAgentPdf();
      triggerBlobDownload(blob, "pharmafind_agent_report.pdf");
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : (e as Error).message;
      setError(`Agent PDF download failed: ${msg}`);
    } finally {
      setPdfLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
      <div className="lg:col-span-8 min-w-0 space-y-4">
        {error && (
          <ErrorAlert
            tone={agentUnavailable ? "warning" : "danger"}
            title={agentUnavailable ? "Agent mode unavailable" : "Agent error"}
            message={error}
            onClose={() => setError(null)}
          />
        )}
        <AgentChat
          messages={messages}
          onSend={handleSend}
          loading={loading}
          disabled={!backendOnline}
          onDownloadPdf={handleDownloadAgentPdf}
          pdfLoading={pdfLoading}
        />
      </div>

      <div className="lg:col-span-4 space-y-4">
        <Card glass>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-4 w-4 text-brand-600" />
              About the agent
            </CardTitle>
            <CardSubtle>How this AI agent behaves</CardSubtle>
          </CardHeader>
          <CardBody className="space-y-3 text-xs text-slate-600 leading-relaxed">
            <p>
              The agent orchestrates the same deterministic FAERS + PubMed tools used by the review
              mode. It can run reviews, explain signals, and generate PDFs on request.
            </p>
            <div className="flex gap-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2.5">
              <ShieldAlert className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
              <p className="text-[11px] text-amber-900">
                The agent does <strong>not</strong> provide medical advice. Outputs describe
                reporting signals for human review only.
              </p>
            </div>
            <div className="flex flex-wrap gap-1.5 pt-1">
              <Badge tone="brand">FAERS aggregation</Badge>
              <Badge tone="teal">PubMed search</Badge>
              <Badge tone="violet">PDF export</Badge>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="pt-5">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
              Try asking
            </h4>
            <ul className="text-xs text-slate-600 space-y-1.5">
              <li>• “Review Ozempic safety signals”</li>
              <li>• “Why was suicidal ideation flagged?”</li>
              <li>• “Compare Ozempic and Wegovy”</li>
              <li>• “Generate a PDF”</li>
            </ul>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
