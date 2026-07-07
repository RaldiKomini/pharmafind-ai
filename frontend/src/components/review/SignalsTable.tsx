import { BookOpen, ChevronRight, Radar } from "lucide-react";
import { Badge, evidenceTone } from "../common/Badge";
import type { SafetySignal } from "../../lib/types";
import { formatNumber, formatRatio, titleCase } from "../../lib/utils";

export function SignalsTable({ signals, onSelect }: { signals: SafetySignal[]; onSelect: (signal: SafetySignal) => void }) {
  if (!signals?.length) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 bg-white/60 p-8 text-center">
        <Radar className="mx-auto h-6 w-6 text-slate-400" />
        <p className="mt-2 text-sm font-medium text-slate-700">No flagged signals</p>
        <p className="text-xs text-slate-500">No reaction passed the configured count, PRR, and ROR confidence-bound thresholds.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-glass">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50/80 text-[11px] uppercase tracking-wider text-slate-500">
            <tr>
              <th className="px-4 py-3 text-left font-semibold">Reaction</th>
              <th className="px-4 py-3 text-right font-semibold">Cases</th>
              <th className="px-4 py-3 text-right font-semibold">PRR (95% CI)</th>
              <th className="px-4 py-3 text-right font-semibold">ROR (95% CI)</th>
              <th className="px-4 py-3 text-left font-semibold">Literature</th>
              <th className="px-4 py-3 text-right font-semibold">Papers</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {signals.map((signal) => {
              const stance = signal.evidence.synthesis?.overall_stance || "retrieved";
              return (
                <tr key={signal.reaction} onClick={() => onSelect(signal)} className="group cursor-pointer hover:bg-brand-50/40 transition-colors">
                  <td className="px-4 py-3 align-top">
                    <div className="font-medium text-slate-900">{titleCase(signal.reaction)}</div>
                    <div className="text-[11px] text-slate-500 mt-0.5">Passed all configured thresholds</div>
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-slate-800">{formatNumber(signal.case_count)}</td>
                  <MetricCell value={signal.prr} low={signal.prr_ci_low} high={signal.prr_ci_high} />
                  <MetricCell value={signal.ror} low={signal.ror_ci_low} high={signal.ror_ci_high} />
                  <td className="px-4 py-3"><Badge tone={evidenceTone(stance)} dot>{stance}</Badge></td>
                  <td className="px-4 py-3 text-right">
                    <span className="inline-flex items-center gap-1 text-xs text-slate-600"><BookOpen className="h-3.5 w-3.5 text-slate-400" />{signal.evidence.retrieved_paper_count}/{signal.evidence.total_result_count}</span>
                  </td>
                  <td className="px-4 py-3 text-right"><ChevronRight className="h-4 w-4 text-slate-300 group-hover:text-brand-600 transition-colors" /></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function MetricCell({ value, low, high }: { value: number; low: number; high: number }) {
  return (
    <td className="px-4 py-3 text-right font-mono text-slate-800 whitespace-nowrap">
      <div className="font-semibold">{formatRatio(value)}</div>
      <div className="text-[10px] text-slate-500">{formatRatio(low)}–{formatRatio(high)}</div>
    </td>
  );
}
