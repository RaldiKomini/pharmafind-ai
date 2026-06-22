from dataclasses import dataclass
from datetime import date, timedelta

from app.clients.faers_client import FaersClient, FaersQueryConfig
from app.pipeline.reaction_extractor import extract_all_reaction_terms
from app.pipeline.reaction_aggregator import count_reactions
from app.pipeline.baseline_comparator import ReactionComparison, compare_reaction_counts
from app.pipeline.signal_detector import SignalDetectionConfig, detect_signals


@dataclass(frozen=True)
class FaersSignalReviewConfig:
    """Configuration for the FAERS-only signal detection step."""

    drug_name: str
    recent_days: int = 90
    baseline_days: int = 365
    max_reports_per_window: int = 1000
    min_recent_count: int = 10
    min_baseline_count: int = 3
    min_ratio: float = 2.0
    max_signals: int = 20


@dataclass(frozen=True)
class FaersSignalReviewResult:
    """FAERS-only result before PubMed evidence is attached."""

    drug_name: str
    recent_start: date
    recent_end: date
    baseline_start: date
    baseline_end: date
    recent_report_count: int
    baseline_report_count: int
    signals: list[ReactionComparison]


def run_faers_signal_review(
    config: FaersSignalReviewConfig,
    client: FaersClient | None = None,
    today: date | None = None,
) -> FaersSignalReviewResult:
    """
    Run the FAERS-only signal review pipeline.

    This function does not claim causality.
    It only detects reporting patterns for human review.
    """
    if today is None:
        today = date.today()

    if client is None:
        client = FaersClient()

    recent_end = today
    recent_start = recent_end - timedelta(days=config.recent_days)

    # Fetching the windows separately is important: one "latest reports" query
    # would mostly return recent reports and leave too little baseline data.
    baseline_end = recent_start - timedelta(days=1)
    baseline_start = baseline_end - timedelta(days=config.baseline_days)

    recent_reports = client.fetch_reports(
        FaersQueryConfig(
            drug_name=config.drug_name,
            start_date=recent_start,
            end_date=recent_end,
            limit=config.max_reports_per_window,
        )
    )

    baseline_reports = client.fetch_reports(
        FaersQueryConfig(
            drug_name=config.drug_name,
            start_date=baseline_start,
            end_date=baseline_end,
            limit=config.max_reports_per_window,
        )
    )

    recent_terms = extract_all_reaction_terms(recent_reports)
    baseline_terms = extract_all_reaction_terms(baseline_reports)

    recent_counts = count_reactions(recent_terms)
    baseline_counts = count_reactions(baseline_terms)

    comparisons = compare_reaction_counts(
        recent_counts=recent_counts,
        baseline_counts=baseline_counts,
        total_recent_reports=len(recent_reports),
        total_baseline_reports=len(baseline_reports),
    )

    signals = detect_signals(
        comparisons=comparisons,
        config=SignalDetectionConfig(
            min_recent_count=config.min_recent_count,
            min_baseline_count=config.min_baseline_count,
            min_ratio=config.min_ratio,
            max_signals=config.max_signals,
        ),
    )

    return FaersSignalReviewResult(
        drug_name=config.drug_name,
        recent_start=recent_start,
        recent_end=recent_end,
        baseline_start=baseline_start,
        baseline_end=baseline_end,
        recent_report_count=len(recent_reports),
        baseline_report_count=len(baseline_reports),
        signals=signals,
    )
