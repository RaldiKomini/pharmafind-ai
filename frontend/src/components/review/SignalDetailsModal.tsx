import { useEffect } from "react";
import { BookOpen, ExternalLink, Info, ShieldAlert, X } from "lucide-react";
import { Badge, evidenceTone } from "../common/Badge";
import type { SafetySignal } from "../../lib/types";
import { formatNumber, formatRatio, titleCase } from "../../lib/utils";

interface Props {
  signal: SafetySignal | null;
  onClose: () => void;
}

export function SignalDetailsModal({ signal, onClose }: Props) {
  useEffect(() => {
    if (!signal) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [signal, onClose]);

  if (!signal) return null;
  const grade = (signal.evidence?.evidence_grade || "none").toLowerCase();
  const papers = signal.evidence?.papers ?? [];

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-slate-900/40 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative w-full sm:max-w-2xl max-h-[92vh] overflow-hidden rounded-t-2xl sm:rounded-2xl bg-white shadow-2xl border border-slate-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="relative border-b border-slate-200 bg-gradient-to-r from-brand-50 via-white to-teal-50 px-6 py-5">
          <button
            onClick={onClose}
            className="absolute right-4 top-4 rounded-lg p-1.5 text-slate-500 hover:bg-white hover:text-slate-700"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
          <p className="text-[11px] font-semibold uppercase tracking-wider text-brand-700">
            Flagged reporting signal
          </p>
          <h2 className="mt-1 text-xl font-bold text-slate-900 pr-10">
            {titleCase(signal.reaction)}
          </h2>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <Badge tone={evidenceTone(grade)} dot>
              Evidence: {grade}
            </Badge>
            <Badge tone="brand">×{formatRatio(signal.ratio)} vs baseline</Badge>
            <Badge tone="neutral">Score {formatRatio(signal.signal_score)}</Badge>
          </div>
        </div>

        <div className="overflow-y-auto max-h-[calc(92vh-9rem)] px-6 py-5 space-y-5">
          {/* Stat grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <Stat label="Recent count" value={formatNumber(signal.recent_count)} />
            <Stat label="Baseline count" value={formatNumber(signal.baseline_count)} />
            <Stat label="Recent rate" value={`${(signal.recent_rate * 100).toFixed(2)}%`} />
            <Stat label="Baseline rate" value={`${(signal.baseline_rate * 100).toFixed(2)}%`} />
          </div>

          {/* Safe explanation */}
          <div className="flex gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
            <ShieldAlert className="h-5 w-5 shrink-0 text-amber-600 mt-0.5" />
            <div className="text-xs text-amber-900 leading-relaxed">
              This is a <strong>reporting pattern</strong> derived from FAERS spontaneous reports —
              not evidence of causality. The ratio compares the recent reporting frequency to the
              baseline window. Patterns require further investigation by qualified reviewers.
            </div>
          </div>

          {/* PubMed evidence */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <BookOpen className="h-4 w-4 text-slate-500" /> PubMed literature support
              </h3>
              <span className="text-xs text-slate-500">{papers.length} paper(s)</span>
            </div>

            {papers.length === 0 ? (
              <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50/50 p-4 text-center">
                <Info className="mx-auto h-4 w-4 text-slate-400" />
                <p className="mt-1 text-xs text-slate-500">
                  No supporting PubMed literature was returned for this signal.
                </p>
              </div>
            ) : (
              <ul className="space-y-2">
                {papers.map((p, i) => {
                  const pmid = (p.pmid || (p as any).id || "") as string;
                  const journal = p.journal || p.source;
                  const date = p.date || p.pub_date;
                  const url =
                    (p.url as string) ||
                    (pmid ? `https://pubmed.ncbi.nlm.nih.gov/${pmid}/` : undefined);
                  return (
                    <li
                      key={`${pmid || i}`}
                      className="rounded-xl border border-slate-200 bg-white p-3 hover:border-brand-300 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-slate-900 leading-snug">
                            {p.title || "Untitled paper"}
                          </p>
                          <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-slate-500">
                            {journal && <span>{String(journal)}</span>}
                            {date && <span>· {String(date)}</span>}
                            {pmid && (
                              <span className="font-mono">· PMID {pmid}</span>
                            )}
                          </div>
                        </div>
                        {url && (
                          <a
                            href={url}
                            target="_blank"
                            rel="noreferrer noopener"
                            className="shrink-0 inline-flex items-center gap-1 text-xs font-medium text-brand-700 hover:text-brand-800"
                          >
                            Open
                            <ExternalLink className="h-3.5 w-3.5" />
                          </a>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-3">
      <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
        {label}
      </div>
      <div className="mt-1 font-mono text-sm font-semibold text-slate-900">{value}</div>
    </div>
  );
}
