from pydantic import BaseModel, Field


class SafetyReviewRequest(BaseModel):
    """Request body for the deterministic review and PDF export endpoints."""

    drug_name: str = Field(..., min_length=1)
    recent_days: int = 90
    baseline_days: int = 365
    max_reports_per_window: int = 1000
    max_signals: int = 20
    max_pubmed_papers_per_signal: int = 5
    use_llm: bool = False


class SafetyReviewResponse(BaseModel):
    """Response returned by POST /reviews."""

    summary: dict
    markdown_report: str


class AgentChatRequest(BaseModel):
    """Single user message sent to the agent endpoint."""

    message: str


class AgentChatResponse(BaseModel):
    """Agent answer plus lightweight state metadata for the UI."""

    answer: str
    last_drug_name: str | None = None
    last_pdf_path: str | None = None
