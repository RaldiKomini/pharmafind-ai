import { HTMLAttributes } from "react";
import { cn } from "../../lib/utils";

type Tone =
  | "neutral"
  | "info"
  | "success"
  | "warning"
  | "danger"
  | "brand"
  | "teal"
  | "violet";

interface Props extends HTMLAttributes<HTMLSpanElement> {
  tone?: Tone;
  icon?: React.ReactNode;
  dot?: boolean;
}

const toneClasses: Record<Tone, string> = {
  neutral: "bg-slate-100 text-slate-700 border-slate-200",
  info: "bg-sky-50 text-sky-700 border-sky-200",
  success: "bg-emerald-50 text-emerald-700 border-emerald-200",
  warning: "bg-amber-50 text-amber-800 border-amber-200",
  danger: "bg-rose-50 text-rose-700 border-rose-200",
  brand: "bg-brand-50 text-brand-700 border-brand-200",
  teal: "bg-teal-50 text-teal-700 border-teal-200",
  violet: "bg-violet-50 text-violet-700 border-violet-200",
};

const dotColors: Record<Tone, string> = {
  neutral: "bg-slate-400",
  info: "bg-sky-500",
  success: "bg-emerald-500",
  warning: "bg-amber-500",
  danger: "bg-rose-500",
  brand: "bg-brand-500",
  teal: "bg-teal-500",
  violet: "bg-violet-500",
};

export function Badge({ tone = "neutral", className, icon, dot, children, ...rest }: Props) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-medium tracking-wide",
        toneClasses[tone],
        className
      )}
      {...rest}
    >
      {dot && <span className={cn("h-1.5 w-1.5 rounded-full", dotColors[tone])} />}
      {icon}
      {children}
    </span>
  );
}

export function evidenceTone(grade: string): Tone {
  switch ((grade || "").toLowerCase()) {
    case "strong":
      return "success";
    case "moderate":
      return "teal";
    case "weak":
      return "warning";
    case "none":
    default:
      return "neutral";
  }
}
