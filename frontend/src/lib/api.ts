import type {
  AgentChatRequest,
  AgentChatResponse,
  SafetyReviewPdfRequest,
  SafetyReviewRequest,
  SafetyReviewResponse,
} from "./types";

// In local development, Vite proxies /api to the FastAPI backend.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export class ApiError extends Error {
  status?: number;
  raw?: unknown;
  constructor(message: string, status?: number, raw?: unknown) {
    super(message);
    this.status = status;
    this.raw = raw;
  }
}

function formatErrorPayload(payload: unknown): string {
  if (!payload) return "Request failed.";
  if (typeof payload === "string") return payload;
  if (typeof payload === "object") {
    const obj = payload as Record<string, unknown>;
    // FastAPI: { detail: "..." } or { detail: [{loc, msg, type}, ...] }
    if ("detail" in obj) {
      const detail = obj.detail;
      if (typeof detail === "string") return detail;
      if (Array.isArray(detail)) {
        return detail
          .map((d: any) => {
            const loc = Array.isArray(d?.loc) ? d.loc.join(".") : "";
            return loc ? `${loc}: ${d?.msg ?? "invalid"}` : d?.msg ?? "invalid";
          })
          .join("; ");
      }
      try {
        return JSON.stringify(detail);
      } catch {
        return "Request failed.";
      }
    }
    if ("message" in obj && typeof obj.message === "string") return obj.message as string;
    try {
      return JSON.stringify(obj);
    } catch {
      return "Request failed.";
    }
  }
  return "Request failed.";
}

async function parseError(res: Response): Promise<ApiError> {
  let payload: unknown = null;
  try {
    const ct = res.headers.get("content-type") || "";
    payload = ct.includes("application/json") ? await res.json() : await res.text();
  } catch {
    /* ignore */
  }
  return new ApiError(formatErrorPayload(payload) || `HTTP ${res.status}`, res.status, payload);
}

export async function getHealth(signal?: AbortSignal): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE_URL}/health`, { signal });
  if (!res.ok) throw await parseError(res);
  return res.json();
}

export async function runReview(
  body: SafetyReviewRequest,
  signal?: AbortSignal
): Promise<SafetyReviewResponse> {
  const res = await fetch(`${API_BASE_URL}/reviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok) throw await parseError(res);
  return res.json();
}

export async function downloadReviewPdf(
  body: SafetyReviewPdfRequest,
  signal?: AbortSignal
): Promise<Blob> {
  const res = await fetch(`${API_BASE_URL}/reviews/pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok) throw await parseError(res);
  return res.blob();
}

export async function agentChat(
  body: AgentChatRequest,
  signal?: AbortSignal
): Promise<AgentChatResponse> {
  const res = await fetch(`${API_BASE_URL}/agent/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok) throw await parseError(res);
  return res.json();
}

export async function downloadAgentPdf(signal?: AbortSignal): Promise<Blob> {
  const res = await fetch(`${API_BASE_URL}/agent/pdf`, { signal });
  if (!res.ok) throw await parseError(res);
  return res.blob();
}

export function triggerBlobDownload(blob: Blob, filename: string) {
  // Use an object URL so PDF downloads work without navigating away from the app.
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}
