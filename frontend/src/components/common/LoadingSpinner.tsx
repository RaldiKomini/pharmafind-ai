import { Loader2 } from "lucide-react";
import { cn } from "../../lib/utils";

export function LoadingSpinner({ className, label }: { className?: string; label?: string }) {
  return (
    <div className={cn("inline-flex items-center gap-2 text-slate-600", className)}>
      <Loader2 className="h-4 w-4 animate-spin text-brand-600" />
      {label && <span className="text-sm">{label}</span>}
    </div>
  );
}
