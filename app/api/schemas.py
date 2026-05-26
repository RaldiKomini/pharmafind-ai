from pydantic import BaseModel, Field


class SafetyReviewRequest(BaseModel):
    drug_name: str = Field(..., min_length=1)
    recent_days: int = 90
    baseline_days: int = 365
    max_reports_per_window: int = 1000
    max_signals: int = 20
    max_pubmed_papers_per_signal: int = 5


class SafetyReviewResponse(BaseModel):
    summary: dict
    markdown_report: str