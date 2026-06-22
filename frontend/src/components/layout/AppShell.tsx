import { ReactNode } from "react";
import { AppHeader } from "./AppHeader";
import { FooterDisclaimer } from "./FooterDisclaimer";

interface Props {
  children: ReactNode;
  backendStatus: "checking" | "online" | "offline";
}

export function AppShell({ children, backendStatus }: Props) {
  return (
    <div className="relative min-h-screen">
      {/* Background gradient + grid */}
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-white via-slate-50 to-brand-50/40" />
        <div className="absolute inset-0 bg-grid-faint [background-size:32px_32px] opacity-50 [mask-image:radial-gradient(ellipse_at_top,black_30%,transparent_75%)]" />
        <div className="absolute -top-32 left-1/3 h-72 w-72 rounded-full bg-brand-300/30 blur-3xl" />
        <div className="absolute top-40 right-10 h-72 w-72 rounded-full bg-teal-300/20 blur-3xl" />
      </div>

      <AppHeader backendStatus={backendStatus} />

      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
        {children}
      </main>

      <FooterDisclaimer />
    </div>
  );
}
