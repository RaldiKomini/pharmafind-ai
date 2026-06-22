import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Check, Copy, Download, FileText } from "lucide-react";
import { Button } from "../common/Button";

interface Props {
  markdown: string;
  onDownloadPdf: () => void;
  pdfLoading?: boolean;
  pdfDisabled?: boolean;
}

export function MarkdownReportViewer({ markdown, onDownloadPdf, pdfLoading, pdfDisabled }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(markdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      /* noop */
    }
  };

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-glass">
      <div className="flex items-center justify-between gap-3 border-b border-slate-200 bg-slate-50/60 px-4 py-3">
        <div className="flex items-center gap-2 min-w-0">
          <div className="rounded-lg bg-white p-1.5 ring-1 ring-slate-200">
            <FileText className="h-4 w-4 text-brand-600" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-slate-900">Safety review brief</p>
            <p className="text-[11px] text-slate-500">Auto-generated · for human review</p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Button
            size="sm"
            variant="secondary"
            onClick={handleCopy}
            icon={copied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
          >
            {copied ? "Copied" : "Copy Markdown"}
          </Button>
          <Button
            size="sm"
            variant="primary"
            onClick={onDownloadPdf}
            loading={pdfLoading}
            disabled={pdfDisabled}
            icon={!pdfLoading ? <Download className="h-3.5 w-3.5" /> : undefined}
          >
            Download PDF
          </Button>
        </div>
      </div>
      <div className="markdown-body max-h-[60vh] overflow-y-auto px-6 py-5">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown || "_No report content._"}</ReactMarkdown>
      </div>
    </div>
  );
}
