import { FormEvent } from "react";
import { Pill, Play } from "lucide-react";
import { Button } from "../common/Button";
import { AdvancedSettings } from "./AdvancedSettings";
import type { SafetyReviewRequest } from "../../lib/types";

interface Props {
  value: SafetyReviewRequest;
  onChange: (next: SafetyReviewRequest) => void;
  onSubmit: () => void;
  loading: boolean;
  disabled?: boolean;
}

export function ReviewForm({ value, onChange, onSubmit, loading, disabled }: Props) {
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!value.drug_name.trim() || loading || disabled) return;
    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-[11px] font-medium uppercase tracking-wider text-slate-500 mb-1.5">
          Drug name
        </label>
        <div className="relative">
          <Pill className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="e.g. Ozempic"
            value={value.drug_name}
            onChange={(e) => onChange({ ...value, drug_name: e.target.value })}
            disabled={disabled || loading}
            className="block w-full rounded-xl border border-slate-200 bg-white pl-9 pr-3 py-3 text-sm font-medium text-slate-900 shadow-sm placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/30 disabled:bg-slate-100"
          />
        </div>
        <p className="mt-1.5 text-[11px] text-slate-500">
          Enter a brand or generic drug name. Analysis uses all FAERS reports mentioning that name.
        </p>
      </div>

      <AdvancedSettings value={value} onChange={onChange} disabled={loading} />

      <Button
        type="submit"
        size="lg"
        className="w-full"
        loading={loading}
        disabled={disabled || !value.drug_name.trim()}
        icon={!loading ? <Play className="h-4 w-4" /> : undefined}
      >
        {loading ? "Running review…" : "Run Review"}
      </Button>

      {disabled && (
        <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
          Backend is offline. Start the backend at <code className="font-mono">127.0.0.1:8000</code>{" "}
          to run a review.
        </p>
      )}
    </form>
  );
}
