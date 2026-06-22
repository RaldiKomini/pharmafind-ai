import { HTMLAttributes } from "react";
import { cn } from "../../lib/utils";

interface Props extends HTMLAttributes<HTMLDivElement> {
  glass?: boolean;
}

export function Card({ glass, className, ...rest }: Props) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-slate-200/70 shadow-glass",
        glass
          ? "bg-white/70 backdrop-blur-xl supports-[backdrop-filter]:bg-white/60"
          : "bg-white",
        className
      )}
      {...rest}
    />
  );
}

export function CardHeader({ className, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("px-5 pt-5 pb-3", className)} {...rest} />;
}

export function CardBody({ className, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("px-5 pb-5", className)} {...rest} />;
}

export function CardTitle({ className, ...rest }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={cn("text-sm font-semibold text-slate-900 tracking-tight", className)}
      {...rest}
    />
  );
}

export function CardSubtle({ className, ...rest }: HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("text-xs text-slate-500 mt-0.5", className)} {...rest} />;
}
