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
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between px-4 py-3 text-left"
      >
        <div className="flex items-center gap-2">
          <Settings2 className="h-4 w-4 text-slate-500" />
          <span className="text-sm font-medium text-slate-800">Advanced settings</span>
        </div>
        <ChevronDown
          className={`h-4 w-4 text-slate-400 transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {open && (
        <div className="border-t border-slate-200/70 p-4 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <NumberField
              label="Recent window (days)"
              value={value.recent_days}
              min={1}
              onChange={(v) => update("recent_days", v)}
              disabled={disabled}
            />
            <NumberField
              label="Baseline window (days)"
              value={value.baseline_days}
              min={1}
              onChange={(v) => update("baseline_days", v)}
              disabled={disabled}
            />
            <NumberField
              label="Max reports / window"
              value={value.max_reports_per_window}
              min={1}
              onChange={(v) => update("max_reports_per_window", v)}
              disabled={disabled}
            />
            <NumberField
              label="Max signals"
              value={value.max_signals}
              min={1}
              onChange={(v) => update("max_signals", v)}
              disabled={disabled}
            />
            <NumberField
              label="Max PubMed papers / signal"
              value={value.max_pubmed_papers_per_signal}
              min={0}
              onChange={(v) => update("max_pubmed_papers_per_signal", v)}
              disabled={disabled}
            />
          </div>

          <label className="flex items-start gap-3 rounded-lg border border-dashed border-violet-200 bg-violet-50/40 p-3">
            <input
              type="checkbox"
              className="mt-0.5 h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
              checked={value.use_llm}
              onChange={(e) => update("use_llm", e.target.checked)}
              disabled={disabled}
            />
            <div className="text-xs text-slate-700">
              <div className="flex items-center gap-1.5 font-medium text-violet-800">
                <Sparkles className="h-3.5 w-3.5" />
                Use LLM-enhanced narrative (optional)
              </div>
              <p className="mt-0.5 text-slate-500">
                Requires backend OpenAI API key + credits. Deterministic results are always computed
                first.
              </p>
            </div>
          </label>
        </div>
      )}
    </div>
  );
}

function NumberField({
  label,
  value,
  onChange,
  min,
  disabled,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min?: number;
  disabled?: boolean;
}) {
  return (
    <label className="block">
      <span className="text-[11px] font-medium uppercase tracking-wider text-slate-500">
        {label}
      </span>
      <input
        type="number"
        min={min}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(Number(e.target.value))}
        className="mt-1 block w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/30 disabled:bg-slate-100"
      />
    </label>
  );
}
