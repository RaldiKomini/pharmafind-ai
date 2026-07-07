from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

from app.pipeline.safety_signal import SafetySignal


@dataclass(frozen=True)
class ReviewSummary:
    """Final deterministic statistics and bounded literature evidence."""

    drug_name: str
    analysis_start: date
    analysis_end: date
    total_report_count: int
    drug_report_count: int
    pubmed_search_terms: list[str]
    signals: list[SafetySignal]
    limitations: list[str]


def build_review_summary(
    drug_name: str,
    analysis_start: date,
    analysis_end: date,
    total_report_count: int,
    drug_report_count: int,
    pubmed_search_terms: list[str],
    signals: list[SafetySignal],
) -> ReviewSummary:
    """Assemble a review with limitations specific to this data method."""
    return ReviewSummary(
        drug_name=drug_name,
        analysis_start=analysis_start,
        analysis_end=analysis_end,
        total_report_count=total_report_count,
        drug_report_count=drug_report_count,
        pubmed_search_terms=pubmed_search_terms,
        signals=signals,
        limitations=[
            "FAERS reports are spontaneous adverse event reports and do not establish causality.",
            "PRR and ROR describe reporting disproportionality, not incidence or patient risk.",
            "This openFDA analysis includes all reports mentioning the selected drug; it is not restricted to primary-suspect drugs.",
            "openFDA returns the latest report version, but separate consumer and sponsor submissions describing the same event may remain.",
            "Drug names are matched against reported and harmonized exact-name fields; incomplete normalization can omit relevant reports.",
            "PubMed synthesis, when requested, is restricted to the displayed retrieved abstracts and requires human review.",
        ],
    )


def review_summary_to_dict(summary: ReviewSummary) -> dict[str, Any]:
    data = asdict(summary)
    data["analysis_start"] = summary.analysis_start.isoformat()
    data["analysis_end"] = summary.analysis_end.isoformat()
    return data
