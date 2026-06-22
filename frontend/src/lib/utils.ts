export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

export function formatNumber(n: number | undefined | null): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return n.toLocaleString();
}

export function formatRatio(n: number | undefined | null, digits = 2): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return n.toFixed(digits);
}

export function formatRange(start?: string, end?: string): string {
  if (!start || !end) return "—";
  return `${start} → ${end}`;
}

export function isLlmCreditError(message: string): boolean {
  const m = message.toLowerCase();
  return (
    m.includes("openai") ||
    m.includes("api key") ||
    m.includes("api_key") ||
    m.includes("credit") ||
    m.includes("quota") ||
    m.includes("rate limit") ||
    m.includes("insufficient")
  );
}

export function uid(): string {
  return Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
}

export function titleCase(s: string): string {
  return s
    .toLowerCase()
    .split(/\s+/)
    .map((w) => (w ? w[0].toUpperCase() + w.slice(1) : w))
    .join(" ");
}
