from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

from app.pipeline.safety_signal import SafetySignal


@dataclass(frozen=True)
class ReviewSummary:
    """Final deterministic review object returned to API/report layers."""

    drug_name: str

    recent_start: date
    recent_end: date
    baseline_start: date
    baseline_end: date

    recent_report_count: int
    baseline_report_count: int

    signals: list[SafetySignal]

    limitations: list[str]


def build_review_summary(
    drug_name: str,
    recent_start: date,
    recent_end: date,
    baseline_start: date,
    baseline_end: date,
    recent_report_count: int,
    baseline_report_count: int,
    signals: list[SafetySignal],
) -> ReviewSummary:
    """Assemble the final review summary with standard safety limitations."""
    return ReviewSummary(
        drug_name=drug_name,
        recent_start=recent_start,
        recent_end=recent_end,
        baseline_start=baseline_start,
        baseline_end=baseline_end,
        recent_report_count=recent_report_count,
        baseline_report_count=baseline_report_count,
        signals=signals,
        limitations=[
            "FAERS reports are spontaneous adverse event reports and do not establish causality.",
            "Report counts are not incidence rates and cannot estimate patient risk.",
            "Reporting patterns may be affected by duplicate reports, media attention, stimulated reporting, missing data, and reporting bias.",
            "Flagged patterns should be treated as signals for human pharmacovigilance review.",
        ],
    )


def review_summary_to_dict(summary: ReviewSummary) -> dict[str, Any]:
    """
    Convert summary to a JSON-friendly dictionary.
    """
    data = asdict(summary)

    data["recent_start"] = summary.recent_start.isoformat()
    data["recent_end"] = summary.recent_end.isoformat()
    data["baseline_start"] = summary.baseline_start.isoformat()
    data["baseline_end"] = summary.baseline_end.isoformat()

    return data
