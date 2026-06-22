import { Activity, FlaskConical, ShieldAlert } from "lucide-react";
import { Badge } from "../common/Badge";

interface Props {
  backendStatus: "checking" | "online" | "offline";
}

export function AppHeader({ backendStatus }: Props) {
  const statusTone =
    backendStatus === "online" ? "success" : backendStatus === "offline" ? "danger" : "neutral";
  const statusLabel =
    backendStatus === "online"
      ? "Backend online"
      : backendStatus === "offline"
        ? "Backend offline"
        : "Checking backend…";

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/70 backdrop-blur-xl supports-[backdrop-filter]:bg-white/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <div className="relative">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 via-brand-600 to-teal-500 shadow-glow">
                <FlaskConical className="h-5 w-5 text-white" />
              </div>
              <span className="absolute -bottom-0.5 -right-0.5 flex h-3 w-3">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-teal-400 opacity-60" />
                <span className="relative inline-flex h-3 w-3 rounded-full bg-teal-500 border-2 border-white" />
              </span>
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold tracking-tight text-slate-900">
                  PharmaFind <span className="text-brand-600">AI</span>
                </h1>
                <Badge tone="violet" className="hidden sm:inline-flex">
                  Beta
                </Badge>
              </div>
              <p className="hidden sm:block text-xs text-slate-500 truncate">
                AI-assisted pharmacovigilance signal review
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Badge tone="warning" icon={<ShieldAlert className="h-3.5 w-3.5" />} className="hidden md:inline-flex">
              Signals for human review · not medical advice
            </Badge>
            <Badge tone={statusTone as any} dot icon={<Activity className="h-3.5 w-3.5" />}>
              {statusLabel}
            </Badge>
          </div>
        </div>
      </div>
    </header>
  );
}
