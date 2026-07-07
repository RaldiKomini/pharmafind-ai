import { CalendarRange, Database, FileBarChart2, Pill, Radar } from "lucide-react";
import type { ReviewSummary } from "../../lib/types";
import { formatNumber, formatRange, titleCase } from "../../lib/utils";

export function SummaryCards({ summary }: { summary: ReviewSummary }) {
  const cards = [
    { label: "Drug", value: titleCase(summary.drug_name), icon: Pill, tint: "from-brand-500/10 to-brand-500/0 text-brand-700" },
    { label: "Analysis window", value: formatRange(summary.analysis_start, summary.analysis_end), icon: CalendarRange, tint: "from-teal-500/10 to-teal-500/0 text-teal-700", mono: true },
    { label: "All FAERS reports", value: formatNumber(summary.total_report_count), icon: Database, tint: "from-sky-500/10 to-sky-500/0 text-sky-700" },
    { label: "Drug reports", value: formatNumber(summary.drug_report_count), icon: FileBarChart2, tint: "from-violet-500/10 to-violet-500/0 text-violet-700" },
    { label: "Flagged signals", value: formatNumber(summary.signals?.length ?? 0), icon: Radar, tint: "from-amber-500/10 to-amber-500/0 text-amber-700", emphasis: true },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div key={card.label} className="relative overflow-hidden rounded-xl border border-slate-200 bg-white p-4 shadow-glass">
            <div className={`pointer-events-none absolute -right-6 -top-6 h-20 w-20 rounded-full bg-gradient-to-br ${card.tint} blur-xl opacity-70`} />
            <div className="relative flex items-start justify-between gap-2">
              <div className="min-w-0">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">{card.label}</p>
                <p className={`mt-1.5 text-slate-900 truncate ${card.emphasis ? "text-2xl font-bold" : "text-base font-semibold"} ${card.mono ? "font-mono text-xs" : ""}`} title={card.value}>{card.value}</p>
              </div>
              <div className="rounded-lg bg-slate-50 p-1.5 ring-1 ring-slate-200/70"><Icon className="h-4 w-4 text-slate-500" /></div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
