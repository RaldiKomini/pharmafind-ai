import { ShieldAlert } from "lucide-react";

export function FooterDisclaimer() {
  return (
    <footer className="mt-12 border-t border-slate-200/70 bg-white/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-start gap-2 text-xs text-slate-500 max-w-3xl">
            <ShieldAlert className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
            <p>
              FAERS reports are spontaneous adverse event reports and do not establish causality.
              Report counts are not incidence rates. PharmaFind AI is a research and human-review
              support tool — not a diagnostic or medical recommendation system.
            </p>
          </div>
          <div className="text-[11px] text-slate-400">
            © {new Date().getFullYear()} PharmaFind AI · FAERS + PubMed
          </div>
        </div>
      </div>
    </footer>
  );
}
