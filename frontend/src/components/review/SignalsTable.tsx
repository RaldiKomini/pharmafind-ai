import { ArrowUpRight, BookOpen, ChevronRight, Radar } from "lucide-react";
import { Badge, evidenceTone } from "../common/Badge";
import type { SafetySignal } from "../../lib/types";
import { formatNumber, formatRatio, titleCase } from "../../lib/utils";

interface Props {
  signals: SafetySignal[];
  onSelect: (s: SafetySignal) => void;
}

export function SignalsTable({ signals, onSelect }: Props) {
  if (!signals || signals.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 bg-white/60 p-8 text-center">
        <Radar className="mx-auto h-6 w-6 text-slate-400" />
        <p className="mt-2 text-sm font-medium text-slate-700">No flagged signals</p>
        <p className="text-xs text-slate-500">
          The recent reporting pattern did not exceed baseline thresholds.
        </p>
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
              <th className="px-4 py-3 text-right font-semibold">Recent</th>
              <th className="px-4 py-3 text-right font-semibold">Baseline</th>
              <th className="px-4 py-3 text-right font-semibold">Ratio</th>
              <th className="px-4 py-3 text-right font-semibold">Signal</th>
              <th className="px-4 py-3 text-left font-semibold">Evidence</th>
              <th className="px-4 py-3 text-right font-semibold">Papers</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {signals.map((s, i) => {
              const grade = (s.evidence?.evidence_grade || "none").toLowerCase();
              const ratioHigh = s.ratio >= 3;
              return (
                <tr
                  key={`${s.reaction}-${i}`}
                  onClick={() => onSelect(s)}
                  className="group cursor-pointer hover:bg-brand-50/40 transition-colors"
                >
                  <td className="px-4 py-3 align-top">
                    <div className="font-medium text-slate-900">{titleCase(s.reaction)}</div>
                    <div className="text-[11px] text-slate-500 mt-0.5">
                      {(s.recent_rate * 100).toFixed(2)}% recent · {(s.baseline_rate * 100).toFixed(2)}% baseline
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-slate-800">
                    {formatNumber(s.recent_count)}
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-slate-500">
                    {formatNumber(s.baseline_count)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span
                      className={`inline-flex items-center gap-1 font-mono text-sm font-semibold ${
                        ratioHigh ? "text-amber-700" : "text-slate-700"
                      }`}
                    >
                      {ratioHigh && <ArrowUpRight className="h-3.5 w-3.5" />}
                      ×{formatRatio(s.ratio)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-slate-800">
                    {formatRatio(s.signal_score)}
                  </td>
                  <td className="px-4 py-3">
                    <Badge tone={evidenceTone(grade)} dot>
                      {grade}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="inline-flex items-center gap-1 text-xs text-slate-600">
                      <BookOpen className="h-3.5 w-3.5 text-slate-400" />
                      {s.evidence?.paper_count ?? 0}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <ChevronRight className="h-4 w-4 text-slate-300 group-hover:text-brand-600 transition-colors" />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
