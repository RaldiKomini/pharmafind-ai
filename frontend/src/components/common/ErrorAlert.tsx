import { AlertTriangle, X } from "lucide-react";

interface Props {
  title?: string;
  message: string;
  onClose?: () => void;
  tone?: "danger" | "warning";
}

export function ErrorAlert({ title, message, onClose, tone = "danger" }: Props) {
  const colors =
    tone === "warning"
      ? "border-amber-200 bg-amber-50 text-amber-900"
      : "border-rose-200 bg-rose-50 text-rose-900";
  const iconColor = tone === "warning" ? "text-amber-600" : "text-rose-600";

  return (
    <div className={`flex gap-3 rounded-xl border ${colors} px-4 py-3`}>
      <AlertTriangle className={`h-5 w-5 shrink-0 ${iconColor}`} />
      <div className="flex-1 min-w-0">
        {title && <p className="text-sm font-semibold">{title}</p>}
        <p className="text-sm leading-relaxed break-words">{message}</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-current/60 hover:text-current"
          aria-label="Dismiss"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
