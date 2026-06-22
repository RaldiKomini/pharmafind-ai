import { Bot, Download, FileText, Pill, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Badge } from "../common/Badge";
import { Button } from "../common/Button";
import type { ChatMessage } from "../../lib/types";

interface Props {
  message: ChatMessage;
  onDownloadPdf?: () => void;
  pdfLoading?: boolean;
}

export function ChatMessageBubble({ message, onDownloadPdf, pdfLoading }: Props) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  if (isSystem) {
    return (
      <div className="flex justify-center">
        <div className="text-[11px] text-slate-500 bg-slate-100 border border-slate-200 rounded-full px-3 py-1">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      <div className="shrink-0">
        {isUser ? (
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-slate-800 text-white">
            <User className="h-4 w-4" />
          </div>
        ) : (
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-teal-500 text-white shadow-glow">
            <Bot className="h-4 w-4" />
          </div>
        )}
      </div>
      <div className={`max-w-[85%] min-w-0 ${isUser ? "items-end" : "items-start"} flex flex-col gap-1.5`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
            isUser
              ? "bg-slate-900 text-white rounded-tr-sm"
              : "bg-white border border-slate-200 text-slate-800 rounded-tl-sm"
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="markdown-body">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {!isUser && message.meta && (message.meta.last_drug_name || message.meta.last_pdf_path) && (
          <div className="flex flex-wrap items-center gap-2">
            {message.meta.last_drug_name && (
              <Badge tone="brand" icon={<Pill className="h-3 w-3" />}>
                {message.meta.last_drug_name}
              </Badge>
            )}
            {message.meta.last_pdf_path && (
              <>
                <Badge tone="teal" icon={<FileText className="h-3 w-3" />}>
                  PDF ready
                </Badge>
                {onDownloadPdf && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={onDownloadPdf}
                    loading={pdfLoading}
                    icon={!pdfLoading ? <Download className="h-3.5 w-3.5" /> : undefined}
                  >
                    Download Agent PDF
                  </Button>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
