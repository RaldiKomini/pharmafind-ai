from pydantic import BaseModel, Field


class SafetyReviewRequest(BaseModel):
    """Configuration for the count-based PRR/ROR and PubMed review."""

    drug_name: str = Field(..., min_length=1, max_length=200)
    analysis_days: int = Field(365, ge=1, le=3650)
    min_case_count: int = Field(5, ge=1, le=10000)
    min_prr: float = Field(2.0, ge=0.0, le=1000.0)
    min_ror_ci_lower: float = Field(1.0, ge=0.0, le=1000.0)
    max_signals: int = Field(10, ge=1, le=50)
    pubmed_candidate_count: int = Field(25, ge=1, le=100)
    max_pubmed_papers_per_signal: int = Field(5, ge=0, le=10)
    use_embeddings: bool = True
    use_llm: bool = False


class ContingencyTableResponse(BaseModel):
    drug_with_event: int
    drug_without_event: int
    other_drugs_with_event: int
    other_drugs_without_event: int


class PubMedPaperResponse(BaseModel):
    pmid: str
    title: str
    source: str
    pub_date: str
    abstract: str
    doi: str | None = None
    publication_types: list[str] | tuple[str, ...]
    relevance_score: float | None = None


class EvidenceClaimResponse(BaseModel):
    text: str
    stance: str
    pmids: list[str]


class EvidenceSynthesisResponse(BaseModel):
    summary: str
    overall_stance: str
    claims: list[EvidenceClaimResponse]
    limitations: list[str]


class EvidenceSummaryResponse(BaseModel):
    total_result_count: int
    retrieved_paper_count: int
    ranking_method: str
    papers: list[PubMedPaperResponse]
    synthesis: EvidenceSynthesisResponse | None = None
    synthesis_status: str


class SafetySignalResponse(BaseModel):
    reaction: str
    case_count: int
    contingency_table: ContingencyTableResponse
    prr: float
    prr_ci_low: float
    prr_ci_high: float
    ror: float
    ror_ci_low: float
    ror_ci_high: float
    continuity_corrected: bool
    passes_threshold: bool
    threshold_reasons: list[str]
    evidence: EvidenceSummaryResponse


class ReviewSummaryResponse(BaseModel):
    drug_name: str
    analysis_start: str
    analysis_end: str
    total_report_count: int
    drug_report_count: int
    pubmed_search_terms: list[str]
    signals: list[SafetySignalResponse]
    limitations: list[str]


class SafetyReviewResponse(BaseModel):
    summary: ReviewSummaryResponse
    markdown_report: str


class SafetyReviewPdfRequest(BaseModel):
    """Already-generated report content to render as a PDF."""

    drug_name: str = Field(..., min_length=1, max_length=200)
    markdown_report: str = Field(..., min_length=1)


class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class AgentChatResponse(BaseModel):
    answer: str
    last_drug_name: str | None = None
    last_pdf_path: str | None = None
