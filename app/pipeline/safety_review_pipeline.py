from dataclasses import dataclass

from app.clients.pubmed_client import PubMedClient, PubMedSearchConfig
from app.pipeline.evidence_grader import grade_pubmed_evidence
from app.pipeline.faers_signal_pipeline import (
    FaersSignalReviewConfig,
    run_faers_signal_review,
)
from app.pipeline.review_summary import ReviewSummary, build_review_summary
from app.pipeline.safety_signal import build_safety_signal


@dataclass(frozen=True)
class SafetyReviewConfig:
    """Top-level configuration for a full FAERS + PubMed safety review."""

    drug_name: str
    recent_days: int = 90
    baseline_days: int = 365
    max_reports_per_window: int = 1000
    max_pubmed_papers_per_signal: int = 5
    max_signals: int = 20


def run_safety_review(
    config: SafetyReviewConfig,
    pubmed_client: PubMedClient | None = None,
) -> ReviewSummary:
    """
    Run the full deterministic review pipeline.

    FAERS determines which reporting patterns are flagged. PubMed is searched
    afterward only to summarize literature support for those flagged patterns.
    """
    if pubmed_client is None:
        pubmed_client = PubMedClient()

    faers_result = run_faers_signal_review(
        FaersSignalReviewConfig(
            drug_name=config.drug_name,
            recent_days=config.recent_days,
            baseline_days=config.baseline_days,
            max_reports_per_window=config.max_reports_per_window,
            max_signals=config.max_signals,
        )
    )

    safety_signals = []

    for signal in faers_result.signals:
        # PubMed search is intentionally scoped to flagged signals so the review
        # stays focused and external API calls remain bounded.
        papers = pubmed_client.search_papers(
            PubMedSearchConfig(
                drug_name=config.drug_name,
                reaction=signal.reaction,
                max_results=config.max_pubmed_papers_per_signal,
            )
        )

        evidence = grade_pubmed_evidence(papers)
        safety_signals.append(build_safety_signal(signal, evidence))

    return build_review_summary(
        drug_name=faers_result.drug_name,
        recent_start=faers_result.recent_start,
        recent_end=faers_result.recent_end,
        baseline_start=faers_result.baseline_start,
        baseline_end=faers_result.baseline_end,
        recent_report_count=faers_result.recent_report_count,
        baseline_report_count=faers_result.baseline_report_count,
        signals=safety_signals,
    )
