export interface SafetyReviewRequest {
  drug_name: string;
  analysis_days: number;
  min_case_count: number;
  min_prr: number;
  min_ror_ci_lower: number;
  max_signals: number;
  pubmed_candidate_count: number;
  max_pubmed_papers_per_signal: number;
  use_embeddings: boolean;
  use_llm: boolean;
}

export interface ContingencyTable {
  drug_with_event: number;
  drug_without_event: number;
  other_drugs_with_event: number;
  other_drugs_without_event: number;
}

export interface PubMedPaper {
  pmid: string;
  title: string;
  source: string;
  pub_date: string;
  abstract: string;
  doi?: string | null;
  publication_types: string[];
  relevance_score?: number | null;
}

export type EvidenceStance = "supports" | "refutes" | "mixed" | "unclear";

export interface EvidenceClaim {
  text: string;
  stance: EvidenceStance | string;
  pmids: string[];
}

export interface EvidenceSynthesis {
  summary: string;
  overall_stance: EvidenceStance | string;
  claims: EvidenceClaim[];
  limitations: string[];
}

export interface EvidenceSummary {
  total_result_count: number;
  retrieved_paper_count: number;
  ranking_method: string;
  papers: PubMedPaper[];
  synthesis?: EvidenceSynthesis | null;
  synthesis_status: string;
}

export interface SafetySignal {
  reaction: string;
  case_count: number;
  contingency_table: ContingencyTable;
  prr: number;
  prr_ci_low: number;
  prr_ci_high: number;
  ror: number;
  ror_ci_low: number;
  ror_ci_high: number;
  continuity_corrected: boolean;
  passes_threshold: boolean;
  threshold_reasons: string[];
  evidence: EvidenceSummary;
}

export interface ReviewSummary {
  drug_name: string;
  analysis_start: string;
  analysis_end: string;
  total_report_count: number;
  drug_report_count: number;
  pubmed_search_terms: string[];
  signals: SafetySignal[];
  limitations: string[];
}

export interface SafetyReviewResponse {
  summary: ReviewSummary;
  markdown_report: string;
}

export interface SafetyReviewPdfRequest {
  drug_name: string;
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
