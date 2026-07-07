import { ChevronDown, Settings2, Sparkles } from "lucide-react";
import { useState } from "react";
import type { SafetyReviewRequest } from "../../lib/types";

interface Props {
  value: SafetyReviewRequest;
  onChange: (next: SafetyReviewRequest) => void;
  disabled?: boolean;
}

export function AdvancedSettings({ value, onChange, disabled }: Props) {
  const [open, setOpen] = useState(false);
  const update = <K extends keyof SafetyReviewRequest>(key: K, v: SafetyReviewRequest[K]) =>
    onChange({ ...value, [key]: v });

  return (
    <div className="rounded-xl border border-slate-200 bg-white/60">
      <button
        type="button"
        onClick={() => setOpen((current) => !current)}
        className="flex w-full items-center justify-between px-4 py-3 text-left"
      >
        <div className="flex items-center gap-2">
          <Settings2 className="h-4 w-4 text-slate-500" />
          <span className="text-sm font-medium text-slate-800">Analysis settings</span>
        </div>
        <ChevronDown
          className={`h-4 w-4 text-slate-400 transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {open && (
        <div className="border-t border-slate-200/70 p-4 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <NumberField label="Analysis window (days)" value={value.analysis_days} min={1} onChange={(v) => update("analysis_days", v)} disabled={disabled} />
            <NumberField label="Minimum cases" value={value.min_case_count} min={1} onChange={(v) => update("min_case_count", v)} disabled={disabled} />
            <NumberField label="Minimum PRR" value={value.min_prr} min={0} step={0.1} onChange={(v) => update("min_prr", v)} disabled={disabled} />
            <NumberField label="Minimum ROR CI lower" value={value.min_ror_ci_lower} min={0} step={0.1} onChange={(v) => update("min_ror_ci_lower", v)} disabled={disabled} />
            <NumberField label="Maximum signals" value={value.max_signals} min={1} onChange={(v) => update("max_signals", v)} disabled={disabled} />
            <NumberField label="PubMed candidates" value={value.pubmed_candidate_count} min={1} onChange={(v) => update("pubmed_candidate_count", v)} disabled={disabled} />
            <NumberField label="Abstracts per signal" value={value.max_pubmed_papers_per_signal} min={0} onChange={(v) => update("max_pubmed_papers_per_signal", v)} disabled={disabled} />
          </div>

          <Toggle
            checked={value.use_embeddings}
            onChange={(checked) => update("use_embeddings", checked)}
            disabled={disabled}
            title="Semantic abstract reranking"
            description="Uses embeddings when an OpenAI key is available; otherwise PubMed relevance is used."
          />
          <Toggle
            checked={value.use_llm}
            onChange={(checked) => update("use_llm", checked)}
            disabled={disabled}
            title="Grounded literature synthesis"
            description="Summarizes only retrieved abstracts and validates every cited PMID. Requires an OpenAI API key."
          />
        </div>
      )}
    </div>
  );
}

function Toggle({ checked, onChange, disabled, title, description }: { checked: boolean; onChange: (checked: boolean) => void; disabled?: boolean; title: string; description: string }) {
  return (
    <label className="flex items-start gap-3 rounded-lg border border-dashed border-violet-200 bg-violet-50/40 p-3">
      <input type="checkbox" className="mt-0.5 h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500" checked={checked} onChange={(event) => onChange(event.target.checked)} disabled={disabled} />
      <div className="text-xs text-slate-700">
        <div className="flex items-center gap-1.5 font-medium text-violet-800"><Sparkles className="h-3.5 w-3.5" />{title}</div>
        <p className="mt-0.5 text-slate-500">{description}</p>
      </div>
    </label>
  );
}

function NumberField({ label, value, onChange, min, step, disabled }: { label: string; value: number; onChange: (value: number) => void; min?: number; step?: number; disabled?: boolean }) {
  return (
    <label className="block">
      <span className="text-[11px] font-medium uppercase tracking-wider text-slate-500">{label}</span>
      <input type="number" min={min} step={step} value={value} disabled={disabled} onChange={(event) => onChange(Number(event.target.value))} className="mt-1 block w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/30 disabled:bg-slate-100" />
    </label>
  );
}
