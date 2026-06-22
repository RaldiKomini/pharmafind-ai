export interface SafetyReviewRequest {
  drug_name: string;
  recent_days: number;
  baseline_days: number;
  max_reports_per_window: number;
  max_signals: number;
  max_pubmed_papers_per_signal: number;
  use_llm: boolean;
}

export interface PubMedPaper {
  pmid?: string;
  title?: string;
  source?: string;
  pub_date?: string;
  date?: string;
  journal?: string;
  url?: string;
  [k: string]: unknown;
}

export type EvidenceGrade = "none" | "weak" | "moderate" | "strong";

export interface EvidenceSummary {
  paper_count: number;
  evidence_grade: EvidenceGrade | string;
  papers: PubMedPaper[];
}

export interface SafetySignal {
  reaction: string;
  recent_count: number;
  baseline_count: number;
  recent_rate: number;
  baseline_rate: number;
  ratio: number;
  signal_score: number;
  evidence: EvidenceSummary;
}

export interface ReviewSummary {
  drug_name: string;
  recent_start: string;
  recent_end: string;
  baseline_start: string;
  baseline_end: string;
  recent_report_count: number;
  baseline_report_count: number;
  signals: SafetySignal[];
  limitations: string[];
}

export interface SafetyReviewResponse {
  summary: ReviewSummary;
  markdown_report: string;
}

export interface AgentChatRequest {
  message: string;
}

export interface AgentChatResponse {
  answer: string;
  last_drug_name?: string | null;
  last_pdf_path?: string | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "agent" | "system";
  content: string;
  meta?: {
    last_drug_name?: string | null;
    last_pdf_path?: string | null;
  };
  timestamp: number;
}
