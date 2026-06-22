import { useEffect, useState } from "react";
import { Beaker, Bot, ShieldAlert } from "lucide-react";
import { AppShell } from "./components/layout/AppShell";
import { ReviewMode } from "./components/review/ReviewMode";
import { AgentMode } from "./components/agent/AgentMode";
import { getHealth } from "./lib/api";
import { cn } from "./lib/utils";
import { Badge } from "./components/common/Badge";

type Mode = "review" | "agent";
type BackendStatus = "checking" | "online" | "offline";

export default function App() {
  const [mode, setMode] = useState<Mode>("review");
  const [backendStatus, setBackendStatus] = useState<BackendStatus>("checking");

  useEffect(() => {
    let cancelled = false;
    const check = async () => {
      try {
        const res = await getHealth();
        if (!cancelled) setBackendStatus(res?.status === "ok" ? "online" : "offline");
      } catch {
        if (!cancelled) setBackendStatus("offline");
      }
    };
    check();
    const id = setInterval(check, 20000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  const backendOnline = backendStatus === "online";

  return (
    <AppShell backendStatus={backendStatus}>
      {/* Intro */}
      <section className="mb-6">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
          <div className="max-w-3xl">
            <div className="flex items-center gap-2 mb-2">
              <Badge tone="brand" dot>
                Pharmacovigilance · v0.1
              </Badge>
              <Badge tone="warning" icon={<ShieldAlert className="h-3 w-3" />}>
                Signals for human review · not medical advice
              </Badge>
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
              Detect reporting signals in{" "}
              <span className="bg-gradient-to-r from-brand-600 via-brand-500 to-teal-500 bg-clip-text text-transparent">
                FAERS + PubMed
              </span>
            </h2>
            <p className="mt-1.5 text-sm text-slate-600 max-w-2xl">
              PharmaFind AI aggregates adverse event reports, compares recent reporting patterns
              against a baseline, grades supporting literature, and produces a structured safety
              brief for qualified human reviewers.
            </p>
          </div>

          {/* Mode tabs */}
          <ModeTabs mode={mode} onChange={setMode} />
        </div>
      </section>

      {mode === "review" ? (
        <ReviewMode backendOnline={backendOnline} />
      ) : (
        <AgentMode backendOnline={backendOnline} />
      )}
    </AppShell>
  );
}

function ModeTabs({ mode, onChange }: { mode: Mode; onChange: (m: Mode) => void }) {
  const tabs: { id: Mode; label: string; icon: any }[] = [
    { id: "review", label: "Deterministic", icon: Beaker },
    { id: "agent", label: "Agent", icon: Bot },
  ];
  return (
    <div className="inline-flex items-center rounded-xl border border-slate-200 bg-white p-1 shadow-glass self-start sm:self-auto">
      {tabs.map((t) => {
        const Icon = t.icon;
        const active = mode === t.id;
        return (
          <button
            key={t.id}
            onClick={() => onChange(t.id)}
            className={cn(
              "inline-flex items-center gap-1.5 rounded-lg px-3.5 py-2 text-sm font-medium transition-all",
              active
                ? "bg-gradient-to-b from-brand-600 to-brand-700 text-white shadow-sm"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
            )}
          >
            <Icon className="h-4 w-4" />
            {t.label}
          </button>
        );
      })}
    </div>
  );
}
