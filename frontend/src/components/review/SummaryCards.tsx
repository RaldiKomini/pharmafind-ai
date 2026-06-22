import { CalendarRange, Database, FileBarChart2, Pill, Radar } from "lucide-react";
import type { ReviewSummary } from "../../lib/types";
import { formatNumber, formatRange, titleCase } from "../../lib/utils";

interface Props {
  summary: ReviewSummary;
}

export function SummaryCards({ summary }: Props) {
  const cards = [
    {
      label: "Drug",
      value: titleCase(summary.drug_name),
      icon: Pill,
      tint: "from-brand-500/10 to-brand-500/0 text-brand-700",
    },
    {
      label: "Recent window",
      value: formatRange(summary.recent_start, summary.recent_end),
      icon: CalendarRange,
      tint: "from-teal-500/10 to-teal-500/0 text-teal-700",
      mono: true,
    },
    {
      label: "Baseline window",
      value: formatRange(summary.baseline_start, summary.baseline_end),
      icon: CalendarRange,
      tint: "from-slate-500/10 to-slate-500/0 text-slate-700",
      mono: true,
    },
    {
      label: "Recent reports",
      value: formatNumber(summary.recent_report_count),
      icon: Database,
      tint: "from-sky-500/10 to-sky-500/0 text-sky-700",
    },
    {
      label: "Baseline reports",
      value: formatNumber(summary.baseline_report_count),
      icon: FileBarChart2,
      tint: "from-violet-500/10 to-violet-500/0 text-violet-700",
    },
    {
      label: "Flagged signals",
      value: formatNumber(summary.signals?.length ?? 0),
      icon: Radar,
      tint: "from-amber-500/10 to-amber-500/0 text-amber-700",
      emphasis: true,
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {cards.map((c) => {
        const Icon = c.icon;
        return (
          <div
            key={c.label}
            className="relative overflow-hidden rounded-xl border border-slate-200 bg-white p-4 shadow-glass"
          >
            <div
              className={`pointer-events-none absolute -right-6 -top-6 h-20 w-20 rounded-full bg-gradient-to-br ${c.tint} blur-xl opacity-70`}
            />
            <div className="relative flex items-start justify-between gap-2">
              <div className="min-w-0">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                  {c.label}
                </p>
                <p
                  className={`mt-1.5 text-slate-900 truncate ${
                    c.emphasis ? "text-2xl font-bold" : "text-base font-semibold"
                  } ${c.mono ? "font-mono text-sm" : ""}`}
                  title={c.value}
                >
                  {c.value}
                </p>
              </div>
              <div className="rounded-lg bg-slate-50 p-1.5 ring-1 ring-slate-200/70">
                <Icon className="h-4 w-4 text-slate-500" />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
