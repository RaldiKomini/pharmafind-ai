import { useEffect } from "react";
import { BookOpen, ExternalLink, Info, ShieldAlert, X } from "lucide-react";
import { Badge, evidenceTone } from "../common/Badge";
import type { SafetySignal } from "../../lib/types";
import { formatNumber, formatRatio, titleCase } from "../../lib/utils";

export function SignalDetailsModal({ signal, onClose }: { signal: SafetySignal | null; onClose: () => void }) {
  useEffect(() => {
    if (!signal) return;
    const onKey = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [signal, onClose]);

  if (!signal) return null;
  const evidence = signal.evidence;
  const stance = evidence.synthesis?.overall_stance || "retrieved";
  const table = signal.contingency_table;

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-slate-900/40 backdrop-blur-sm" onClick={onClose}>
      <div className="relative w-full sm:max-w-3xl max-h-[94vh] overflow-hidden rounded-t-2xl sm:rounded-2xl bg-white shadow-2xl border border-slate-200" onClick={(event) => event.stopPropagation()}>
        <div className="relative border-b border-slate-200 bg-gradient-to-r from-brand-50 via-white to-teal-50 px-6 py-5">
          <button onClick={onClose} className="absolute right-4 top-4 rounded-lg p-1.5 text-slate-500 hover:bg-white hover:text-slate-700" aria-label="Close"><X className="h-4 w-4" /></button>
          <p className="text-[11px] font-semibold uppercase tracking-wider text-brand-700">Disproportionality signal</p>
          <h2 className="mt-1 text-xl font-bold text-slate-900 pr-10">{titleCase(signal.reaction)}</h2>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <Badge tone="brand">PRR {formatRatio(signal.prr)}</Badge>
            <Badge tone="teal">ROR {formatRatio(signal.ror)}</Badge>
            <Badge tone={evidenceTone(stance)} dot>Literature: {stance}</Badge>
          </div>
        </div>

        <div className="overflow-y-auto max-h-[calc(94vh-9rem)] px-6 py-5 space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <Stat label="Drug + event" value={formatNumber(table.drug_with_event)} />
            <Stat label="Drug + other events" value={formatNumber(table.drug_without_event)} />
            <Stat label="Other drugs + event" value={formatNumber(table.other_drugs_with_event)} />
            <Stat label="Other drugs + other events" value={formatNumber(table.other_drugs_without_event)} />
            <Stat label="PRR (95% CI)" value={`${formatRatio(signal.prr)} (${formatRatio(signal.prr_ci_low)}–${formatRatio(signal.prr_ci_high)})`} />
            <Stat label="ROR (95% CI)" value={`${formatRatio(signal.ror)} (${formatRatio(signal.ror_ci_low)}–${formatRatio(signal.ror_ci_high)})`} />
          </div>

          <div className="flex gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
            <ShieldAlert className="h-5 w-5 shrink-0 text-amber-600 mt-0.5" />
            <div className="text-xs text-amber-900 leading-relaxed">PRR and ROR measure <strong>reporting disproportionality</strong>, not incidence, individual risk, or causality. This analysis includes every report mentioning the drug.</div>
          </div>

          <section>
            <h3 className="text-sm font-semibold text-slate-900 mb-2">Threshold evaluation</h3>
            <ul className="space-y-1.5 text-xs text-slate-600">
              {signal.threshold_reasons.map((reason) => <li key={reason} className="rounded-lg bg-emerald-50 border border-emerald-100 px-3 py-2">✓ {reason}</li>)}
              {signal.continuity_corrected && <li className="rounded-lg bg-slate-50 border border-slate-200 px-3 py-2">A 0.5 zero-cell continuity correction was applied.</li>}
            </ul>
          </section>

          <section>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2"><BookOpen className="h-4 w-4 text-slate-500" />Retrieved PubMed evidence</h3>
              <span className="text-xs text-slate-500">{evidence.retrieved_paper_count} shown · {evidence.total_result_count} matches</span>
            </div>

            {evidence.synthesis && (
              <div className="rounded-xl border border-violet-200 bg-violet-50/50 p-4 mb-3 space-y-3">
                <div className="flex items-center gap-2"><Badge tone={evidenceTone(evidence.synthesis.overall_stance)} dot>{evidence.synthesis.overall_stance}</Badge><span className="text-[11px] text-slate-500">PMID-validated abstract synthesis</span></div>
                <p className="text-sm text-slate-800 leading-relaxed">
                  {evidence.synthesis.summary}{" "}
                  {Array.from(new Set(evidence.synthesis.claims.flatMap((claim) => claim.pmids))).map((pmid) => (
                    <a key={pmid} href={`https://pubmed.ncbi.nlm.nih.gov/${pmid}/`} target="_blank" rel="noreferrer noopener" className="font-mono text-xs text-brand-700 hover:underline">PMID {pmid} </a>
                  ))}
                </p>
                {evidence.synthesis.claims.length > 0 && (
                  <ul className="space-y-2 text-xs text-slate-700">
                    {evidence.synthesis.claims.map((claim, index) => (
                      <li key={`${claim.text}-${index}`} className="border-t border-violet-100 pt-2">
                        <span className="font-medium">{claim.stance}: </span>{claim.text}{" "}
                        {claim.pmids.map((pmid) => <a key={pmid} href={`https://pubmed.ncbi.nlm.nih.gov/${pmid}/`} target="_blank" rel="noreferrer noopener" className="font-mono text-brand-700 hover:underline">PMID {pmid}</a>)}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {evidence.papers.length === 0 ? (
              <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50/50 p-4 text-center"><Info className="mx-auto h-4 w-4 text-slate-400" /><p className="mt-1 text-xs text-slate-500">No PubMed abstracts were returned.</p></div>
            ) : (
              <ul className="space-y-3">
                {evidence.papers.map((paper) => (
                  <li key={paper.pmid} className="rounded-xl border border-slate-200 bg-white p-4 hover:border-brand-300 transition-colors">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-slate-900 leading-snug">{paper.title || "Untitled paper"}</p>
                        <p className="mt-1 text-[11px] text-slate-500">{[paper.source, paper.pub_date, `PMID ${paper.pmid}`].filter(Boolean).join(" · ")}</p>
                      </div>
                      <a href={`https://pubmed.ncbi.nlm.nih.gov/${paper.pmid}/`} target="_blank" rel="noreferrer noopener" className="shrink-0 inline-flex items-center gap-1 text-xs font-medium text-brand-700 hover:text-brand-800">Open <ExternalLink className="h-3.5 w-3.5" /></a>
                    </div>
                    {paper.abstract && <p className="mt-3 text-xs text-slate-600 leading-relaxed whitespace-pre-line">{paper.abstract}</p>}
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-3"><div className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">{label}</div><div className="mt-1 font-mono text-xs font-semibold text-slate-900">{value}</div></div>;
}
